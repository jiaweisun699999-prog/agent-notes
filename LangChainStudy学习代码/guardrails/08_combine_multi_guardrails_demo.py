"""
综合案例：金融客服系统 —— 四层安全护栏实战

业务背景：
    某银行智能客服系统，支持用户查询账户余额、交易记录，以及执行转账、冻结账户等敏感操作。
    系统需要多层安全防护以确保合规和资金安全。

四层防护架构：
    第1层（before_agent）：输入关键词过滤  —— 拦截明显违规的请求（如洗钱、诈骗关键词）
    第2层（PIIMiddleware）：   敏感信息脱敏    —— 自动脱敏身份证号、银行卡号、手机号
    第3层（HITL）：             高危操作人工审批 —— 转账 > 5000元、冻结账户等操作须主管审批
    第4层（after_agent）：      输出内容安全审核 —— 用模型对最终回复做合规性兜底检查

执行流程：
    用户输入 → [第1层: 关键词拦截] → [第2层: PII脱敏] → Agent执行(模型+工具)
    → 工具调用中如触发高危操作则 [第3层: 人工审批] → [第4层: 输出审核] → 返回用户
"""
from typing import Any
from langchain.agents import create_agent
from langchain.agents.middleware import (
    PIIMiddleware,
    HumanInTheLoopMiddleware,
    before_agent,
    after_agent,
    AgentState,
)
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime
from langgraph.types import Command

from init_llm import deepseek_llm


# =============================================================================
# 0. 模拟银行数据库
# =============================================================================

ACCOUNT_DATABASE = {
    "622021234567890": {
        "name": "张三",
        "balance": 158000.00, # 余额
        "phone": "13812345678",
        "id_card": "110101199001011234",
        "status": "正常",
    },
    "622029876543210": {
        "name": "李四",
        "balance": 3200.50, # 余额
        "phone": "13987654321",
        "id_card": "320102198505052345",
        "status": "正常",
    },
}

# =============================================================================
# 1. 定义业务工具
# =============================================================================

@tool
def query_balance(account_no: str) -> str:
    """
    查询账户余额
    Args:
        account_no: 银行卡号
    """
    account = ACCOUNT_DATABASE.get(account_no)
    if not account:
        return f"卡号 {account_no} 不存在，请核实后重新查询。"
    return (f"账户 {account_no}（户名：{account['name']}，手机号：{account['phone']}，身份证号：{account['id_card']}）"
            f"当前余额：¥{account['balance']:,.2f}，状态：{account['status']}。")


@tool
def query_transactions(account_no: str, count: int = 5) -> str:
    """
    查询最近 N 笔交易记录
    Args:
        account_no: 银行卡号
        count: 查询最近几笔交易，默认5笔
    """
    account = ACCOUNT_DATABASE.get(account_no)
    if not account:
        return f"卡号 {account_no} 不存在。"
    # 模拟交易记录
    sample = [
        ("2026-06-09", "超市消费", -156.80),
        ("2026-06-08", "工资入账", 15000.00),
        ("2026-06-07", "美团外卖", -45.00),
        ("2026-06-06", "京东购物", -899.00),
        ("2026-06-05", "滴滴出行", -32.50),
    ]
    lines = [f"账户 {account_no} 最近 {min(count, len(sample))} 笔交易："]
    for date, desc, amount in sample[:count]:
        direction = "收入" if amount > 0 else "支出"
        lines.append(f"  {date}  {desc}  {direction} {abs(amount)}元")
    return "\n".join(lines)


@tool
def transfer_funds(from_account: str, to_account: str, amount: float, note: str = "") -> str:
    """
    账户转账
    Args:
        from_account: 转出卡号
        to_account: 转入卡号
        amount: 转账金额
        note: 转账备注
    """
    # payer 转出方，payee 转入方
    payer = ACCOUNT_DATABASE.get(from_account)
    payee = ACCOUNT_DATABASE.get(to_account)
    if not payer:
        return f"转出卡号 {from_account} 不存在。"
    if not payee:
        return f"转入卡号 {to_account} 不存在。"
    if payer["balance"] < amount:
        return f"余额不足！当前余额 {payer['balance']}元，无法转出 {amount}元。"
    # 执行转账
    payer["balance"] -= amount
    payee["balance"] += amount
    return (
        f"转账成功！从 {from_account}（{payer['name']}）向 {to_account}（{payee['name']}）"
        f"转入 {amount}元。备注：{note or '无'}。"
        f"转出方余额：{payer['balance']}元，转入方余额：{payee['balance']}元。"
    )


@tool
def freeze_account(account_no: str, reason: str) -> str:
    """
    冻结指定账户
    Args:
        account_no: 要冻结的银行卡号
        reason: 冻结原因
    """
    account = ACCOUNT_DATABASE.get(account_no)
    if not account:
        return f"卡号 {account_no} 不存在。"
    if account["status"] == "已冻结":
        return f"账户 {account_no} 已经是冻结状态，无需重复操作。"
    account["status"] = "已冻结"
    return f"账户 {account_no}（户名：{account['name']}，手机号：{account['phone']}，身份证号：{account['id_card']}）已冻结，原因：{reason}。"


@tool
def get_investment_advice() -> str:
    """
    获取用户的投资建议
    """
    return f"基于你的账户信息，建议您投资于股票高风险的金融产品。"



# =============================================================================
# 2. 第1层：Before Agent —— 违禁词输入过滤（确定性守卫）
# =============================================================================

BANNED_KEYWORDS = ["洗钱", "诈骗", "套现", "盗刷"]


@before_agent(can_jump_to=["end"])
def input_content_filter(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """
    输入内容过滤器 —— 第1层防护
    在模型处理之前快速拦截包含金融违规关键词的请求。
    命中后直接终止流程，连模型调用都不触发。
    """

    # 取本轮用户输入（多轮对话时取最后一条 human 消息）
    last_message = state["messages"][-1]
    if last_message.type != "human":
        return None

    # 检查用户输入是否包含违禁关键词
    content = last_message.content

    for keyword in BANNED_KEYWORDS:
        if keyword in content:
            print(f"\n{'=' * 60}")
            print(f"[第1层·输入过滤] 检测到违规关键词[{keyword}]，已拦截")
            print(f"{'=' * 60}")
            return {
                "messages": [{
                    "role": "assistant",
                    "content": (
                        f"您的请求包含违规内容，涉及[{keyword}]相关操作。"
                        f"根据监管要求，本系统无法处理此类请求。如有疑问请联系客服。"
                    ),
                }],
                "jump_to": "end",
            }

    print(f"[第1层·输入过滤] 通过，未检测到违禁关键词")
    return None


# =============================================================================
# 3. 第2层：PIIMiddleware —— 敏感信息脱敏（内置守卫）
# =============================================================================

# PIIMiddleware 在模型调用前、工具返回结果后、最终输出后 三个节点自动脱敏
# 这里配置两种敏感信息类型：身份证号、手机号

# =============================================================================
# 4. 第3层：HumanInTheLoop —— 高危操作人工审批
# =============================================================================

# HITL 配置：转账和冻结需要审批，查询操作自动放行
# 转账金额 > 5000 时需要额外确认（在描述中提示）

# =============================================================================
# 5. 第4层：After Agent —— 输出内容安全审核（模型驱动守卫）
# =============================================================================

@after_agent(can_jump_to=["end"])
def output_compliance_review(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """
    输出合规审核器 —— 第4层防护
    用模型对 Agent 的最终回复做合规性检查，确保：
    - 不包含投资建议或收益承诺
    - 措辞符合金融监管要求
    """

    last_message = state["messages"][-1]


    # 只审核 AI 生成的回复
    if last_message.type != "ai":
        return None

    review_prompt = f"""你是一名金融合规审查员。请判断以下客服回复是否合规，只回复[合规]或[不合规]。

                    审查标准：
                    1. 回复中不得包含任何投资建议、收益承诺或理财产品推荐
                    2. 回复不得引导客户进行任何高风险操作
                    3. 回复语气应专业、客观，不得夸大或误导
                    
                    客服回复内容：
                    {last_message.content}
                    
                    审查结果（合规/不合规）："""

    review_result = deepseek_llm.invoke([
        {"role": "user", "content": review_prompt}
    ])

    if "不合规" in review_result.content:
        print(f"\n{'=' * 60}")
        print(f"[第4层·输出审核] 模型回复未通过合规审查，已替换为安全兜底回复")
        print(f"  审核模型判定：{review_result.content}")
        print(f"{'=' * 60}")
        last_message.content = (
            "抱歉，当前回复内容未能通过合规审核。"
            "请您换个方式描述问题，或拨打我行客服热线咨询。"
        )
    else:
        print(f"[第4层·输出审核] 通过合规审查")

    return None


# =============================================================================
# 6. 创建 Agent —— 四层防护叠加
# =============================================================================

agent = create_agent(
    model=deepseek_llm,
    tools=[query_balance, query_transactions, transfer_funds, freeze_account, get_investment_advice],
    middleware=[
        # 第1层：确定性输入过滤（最快，最早执行）
        input_content_filter,

        # 第2层：PII 自动脱敏（三个节点：before_model / after_tool / after_model）
        PIIMiddleware(
            pii_type="phone_number",           # 自定义 PII 类型名，检测手机号
            strategy="mask",                   # 掩码：138****5678
            detector=r"1[3-9]\d{9}",           # 自定义检测正则：11位手机号
            apply_to_input=True,
            apply_to_tool_results=True,
            apply_to_output=True,
        ),
        PIIMiddleware(
            pii_type="id_card_number",         # 自定义 PII 类型名，检测身份证号
            strategy="mask",                   # 掩码：110101********1234
            detector=r"\d{17}[\dXx]",          # 自定义检测正则：18位身份证号
            apply_to_input=True,
            apply_to_tool_results=True,
            apply_to_output=True,
        ),

        # 第3层：高危操作人工审批
        HumanInTheLoopMiddleware(
            interrupt_on={
                "query_balance": False,       # 查询余额 —— 自动放行
                "query_transactions": False,  # 查询交易 —— 自动放行
                # 转账操作需审批
                "transfer_funds": {
                    "allowed_decisions": ["approve", "reject"],
                    "description": (
                        "转账操作需审批。请核实转出/转入账户及金额是否正确，确认无误后批准执行。"
                    ),
                },
                # 冻结账户需审批
                "freeze_account": {
                    "allowed_decisions": ["approve", "reject"],
                    "description": (
                        "账户冻结属极高风险操作，请谨慎操作。确认冻结原因合理后方可批准。"
                    ),
                },
            },
            description_prefix="高危操作需要人工审批",
        ),

        # 第4层：模型驱动的输出合规审核（兜底）
        output_compliance_review,
    ],
    checkpointer=InMemorySaver(),
    system_prompt=(
        "你是某银行的智能客服助手[银小助]，为用户提供账户查询、转账、账户管理等服务，可以给用户一些投资建议。\n"
        "工作规范：\n"
        "1. 回复简洁专业，使用[您]称呼客户。\n"
        "2. 涉及金额时精确到分，格式为 1,234.56 元。\n"
    ),
)


# =============================================================================
# 7. 中断处理函数（处理第3层 HITL 审批）
# =============================================================================

def handle_interrupts(result, agent, config):
    """
    处理一轮或多轮中断，直到 Agent 不再触发中断为止。

    返回值：最终的 GraphOutput（此时 result.interrupts 为空）
    """
    while result.interrupts:
        interrupt_data = result.interrupts[0].value
        action_requests = interrupt_data["action_requests"]
        review_configs = interrupt_data["review_configs"]

        # 展示所有待人工介入操作
        print(f"\n{'─' * 60}")
        print(f" Agent中断 —— {len(action_requests)} 个操作需要人工介入")
        print(f"{'─' * 60}")

        for i, req in enumerate(action_requests):
            cfg = review_configs[i]
            print(f"\n  [{i}] 工具名称 : {req['name']}")
            print(f"      参数    : {req['args']}")
            print(f"      允许决策 : {cfg['allowed_decisions']}")

        # 逐个收集决策（决策顺序 == action_requests 顺序）
        decisions = []

        print(f"\n{'·' * 40}")
        print("请按顺序对以上操作做出决策：")
        print(f"{'·' * 40}")

        for i, req in enumerate(action_requests):
            allowed = review_configs[i]["allowed_decisions"]

            print(f"\n 操作 [{i}] {req['name']}")
            # 展示当前参数供人工介入参考
            if req.get("args"):
                for k, v in req["args"].items():
                    print(f"     参数: {k} = {v}")

            # 可用的决策类型及说明
            hint_map = {
                "approve": "批准，按原参数执行工具",
                "edit":    "修改参数后执行工具",
                "reject":  "拒绝执行，附带反馈说明",
                "respond": "跳过工具执行，直接返回人工回复",
            }
            print("     可选操作：")
            for a in allowed:
                print(f"       > {a} — {hint_map.get(a)}")

            # 等待有效输入
            while True:
                decision = input(f"      >>> 输入操作 ({'/'.join(allowed)}): ").strip().lower()
                if decision in allowed:
                    break
                print(f"      无效输入，该操作只允许: {allowed}")

            # 根据决策类型构建决策对象
            if decision == "approve":
                decisions.append({"type": "approve"})
                print(f"      已批准 —— 工具将按原参数执行")

            elif decision == "edit":
                print(f"      请输入修改后的参数（直接回车保留原值）：")
                new_args = {}
                for k, v in req["args"].items():
                    new_val = input(f"         {k} [原值: {str(v)}]: ").strip()
                    if new_val == "":
                        new_args[k] = v  # 保留原值
                    else:
                        # 直接使用用户输入的字符串
                        new_args[k] = new_val
                decisions.append({
                    "type": "edit",
                    "edited_action": {"name": req["name"], "args": new_args},
                })
                print(f"      已修改参数: {new_args}")

            elif decision == "reject":
                reason = input(f"      请输入拒绝原因: ").strip()
                if not reason:
                    reason = "操作被人工拒绝"
                decisions.append({"type": "reject", "message": reason})
                print(f"      已拒绝:{reason}")

            elif decision == "respond":
                reply = input(f"      请输入回复内容: ").strip()
                if not reply:
                    reply = "已确认，没有补充信息。"
                decisions.append({"type": "respond", "message": reply})
                print(f"      已回复:{reply}")

        # 提交决策，恢复执行
        print(f"\n{'─' * 60}")
        print(f"提交决策列表:{decisions}")
        print(f"{'─' * 60}")

        result = agent.invoke(
            Command(resume={"decisions": decisions}),
            config=config,
            version="v2",
        )

    return result


# =============================================================================
# 8. 测试入口
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  金融客服系统[银小助]—— 四层安全护栏演示")
    print("=" * 60)
    print(" 四层防护：")
    print("  第1层：输入关键词过滤（before_agent）")
    print("  第2层：敏感信息自动脱敏（PIIMiddleware）")
    print("  第3层：高危操作人工审批（HITLMiddleware）")
    print("  第4层：输出合规审核（after_agent）")
    print()
    print(" 可用操作：")
    print("  - 查询余额 / 查交易记录 / 转账 / 冻结账户")
    print("  - 输入 exit 退出")
    print("=" * 60)

    config = {"configurable": {"thread_id": "session_01"}}

    while True:
        user_input = input("\n 客户: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "q"):
            print("  感谢使用银小助，再见！")
            break

        print("[银小助思考中...]")

        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
            version="v2",
        )

        # 处理人工审批中断
        result = handle_interrupts(result, agent, config)

        print("result",result)

        # 输出最终回复
        final_msg = result.value["messages"][-1]
        print(f"\n银小助: {final_msg.content}")
