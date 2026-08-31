"""
案例二：电商后台管理系统——高危操作人工审批
功能：对退款、改价等敏感操作设置人工审批流程
前置准备：
1. 安装依赖: pip install langgraph-checkpoint-mysql pymysql
2. 创建MySQL数据库: CREATE DATABASE langchain_guardrails_db;
"""
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver
from langgraph.types import Command

from init_llm import deepseek_llm


# ========== 1. 模拟订单数据库 ==========

ORDER_DATABASE = {
    "ORD001": {"user": "张三", "product": "iPhone 15", "amount": 6999, "status": "已发货"},
    "ORD002": {"user": "李四", "product": "AirPods Pro", "amount": 1999, "status": "待发货"},
}


# ========== 2. 定义工具 ==========
@tool
def query_order(order_id: str) -> str:
    """查询订单基本信息"""
    order = ORDER_DATABASE.get(order_id)
    if not order:
        return f"订单【{order_id}】不存在"
    return (f"订单【{order_id}】：用户{order['user']}，"
            f"商品{order['product']}，金额{order['amount']}元，状态【{order['status']}】")


@tool
def process_refund(order_id: str) -> str:
    """
    执行订单退款操作
    Args:
        order_id: 订单号
    """
    order = ORDER_DATABASE[order_id]
    return (f"退款成功！订单【{order_id}】已退款{order['amount']}元。退款将原路返回至用户账户。")


# ========== 3. 创建HITL的Agent ==========
agent = create_agent(
    model=deepseek_llm,
    tools=[query_order, process_refund],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "process_refund": True,   # 退款需要人工审批
                "query_order": False,      # 查询自动放行
            }
        ),
    ],
    checkpointer=InMemorySaver(),
    system_prompt="你是一个电商运营助手，可以回答用户问题"
)


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

# ========== 4. 运行流程 ==========
# 会话线程ID
config = {"configurable": {"thread_id": "session_01"}}

while True:
    # 获取用户输入
    user_input = input("\n你: ").strip()

    if not user_input:
        continue

    lower_input = user_input.lower()

    # 退出
    if lower_input in ("exit", "quit", "q"):
        print("  再见！")
        break

    # 调用 Agent
    print("Agent 思考中…")

    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config,
        version="v2",
    )

    # 处理中断（可能多轮）
    result = handle_interrupts(result, agent, config)

    # 输出最终回复
    final_msg = result.value["messages"][-1]
    print(f"\nAgent回复: {final_msg.content}")