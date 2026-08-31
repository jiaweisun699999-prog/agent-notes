from typing import Any, Dict

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import after_model
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime
from langgraph.types import interrupt, Command

from init_llm import deepseek_llm

# ===== 1. 模拟订单数据库 =====

ORDERS = {
    "ORD001": {"user": "张三", "amount": 200,   "status": "已付款"},
    "ORD002": {"user": "李四", "amount": 3000,  "status": "已付款"},
    "ORD003": {"user": "王五", "amount": 15000, "status": "已发货"},
}


# ===== 2. 定义工具 =====

@tool
def query_order(order_id: str) -> str:
    """
    查询订单信息
    Args：
      order_id: 订单编号，如 ORD002
    Returns：
      订单信息
    """
    order = ORDERS.get(order_id)
    if not order:
        return f"订单 {order_id} 不存在"
    return (f"订单 {order_id}：用户 {order['user']}，"
            f"金额 ¥{order['amount']}，状态 {order['status']}")


@tool
def process_refund(order_id: str) -> str:
    """
    执行退款操作
    Args：
      order_id: 订单编号，如 ORD002
    Returns：
      退款成功消息
    """
    order = ORDERS.get(order_id)
    if not order:
        return f"订单 {order_id} 不存在，无法退款"
    return f"订单 {order_id}（{order['user']}）已退款，退款金额{order['amount']}"

@after_model
def human_in_the_loop(state: AgentState,runtime: Runtime) -> Dict[str, Any] | None:
    """
        1. 获取AIMessage消息
        2. 判断工具是否是 process_refund，如果不是，直接放行，返回 None
        3. 如果是 process_refund 工具
            3.1 查看订单金额，如果小于等于 500 ，直接放行
            3.2 如果订单金额大于 500 ，进行中断，用户介入
        4.根据用户输入的中断响应，组织返回的数据
    """
    print("state",state)

    last_message = state["messages"][-1] if state.get("messages") else None

    if not last_message or not hasattr(last_message,"tool_calls"):
        return None

    for tool_call in last_message.tool_calls:
        if tool_call["name"] != "process_refund":
            continue

        # 获取订单
        order_id = tool_call["args"]["order_id"]
        order = ORDERS.get(order_id)

        # 判断订单金额
        # {"user": "李四", "amount": 3000, "status": "已付款"}
        if order["amount"] <= 500:
            print(f"订单：{order_id},订单金额：{order["amount"]},小于500，直接放行")
            return None

        # 订单金额大于 500 ，需要人工介入

        review_result = interrupt({
            "action_requests": [{
                "name": tool_call["name"],
                "args": tool_call["args"],
                "description": f"退款审批：订单{order_id}，金额{order['amount']}，是否退款？",
            }],
            "review_configs": [{
                "action_name": tool_call["name"],
                "allowed_decisions": ["approve", "reject"],
            }],
        })

        # print("review_result",review_result)
        # {'decisions': [{'type': 'reject', 'message': '已经签收了，不能退款'}]}
        decision = review_result["decisions"][0]
        if decision["type"] == "approve":
            return None
        elif decision["type"] == "reject":
            reject_reason = decision["message"]
            return {"messages": [
                ToolMessage(
                    content=f"拒绝退款，原因：{reject_reason}",
                    tool_call_id=tool_call["id"]
                )
            ]}

    return None



agent = create_agent(
    model=deepseek_llm,
    tools=[query_order, process_refund],
    middleware=[human_in_the_loop],
    checkpointer = InMemorySaver(),
    system_prompt="你是一个电商助手，可以处理用户订单问题。",
)

config = {"configurable": {"thread_id": "123"}}

#3.1 外层循环：对话轮次
while True:
    try:
        user_input = input("\n[你]: ").strip()

        if user_input.lower() in ("quit", "exit", "退出", "q"):
            print("已退出，再见！")
            break

        if not user_input:
            continue

        # 本轮对话的输入：首次是普通消息，中断后会被替换为 Command(resume=...)
        next_input = {"messages": [{"role": "user", "content": user_input}]}

        #3.2 内层循环：同一轮对话中可能发生多轮中断/恢复
        while True:
            print("[Agent 回复]: ", end="", flush=True)

            interrupted = False  # 本轮 stream 是否因中断而跳出

            for chunk in agent.stream(
                next_input,
                config=config,
                stream_mode=["updates", "messages"],
                version="v2",
            ):
                # print("chunk:", chunk)
                # 3.3 处理非中断消息流
                if chunk["type"] == "messages":
                    token_data = chunk["data"]
                    # token_data 是 (token_chunk, metadata) 元组
                    token_chunk = token_data[0]
                    if token_chunk.content:
                        # end="" 避免打印时自动换行，flush=True 及时刷新输出
                        print(token_chunk.content, end="", flush=True)
                # 3.4 处理中断消息流
                elif chunk["type"] == "updates":
                    update_data = chunk["data"]

                    # 检查是否有中断信号触发
                    if "__interrupt__" in update_data:
                        interrupted = True

                        print("=" * 60)
                        print("Agent中断已触发！Agent 等待人工确认…")
                        print("=" * 60)

                        # 提取中断详情
                        interrupt_raw = update_data["__interrupt__"]
                        action_requests = interrupt_raw[0].value["action_requests"]
                        review_configs = interrupt_raw[0].value["review_configs"]

                        print(f"\n  本次中断包含 {len(action_requests)} 个待审批操作：")
                        for i, req in enumerate(action_requests):
                            cfg = review_configs[i]
                            print(f"    [{i}] {req['name']}  |  参数: {req['args']}  |  允许: {cfg['allowed_decisions']}")

                        # 按顺序逐个收集决策（多工具同时中断时，顺序必须一致）
                        decisions = []
                        for i, req in enumerate(action_requests):
                            cfg = review_configs[i]
                            allowed = cfg["allowed_decisions"]

                            print(f"\n  ── 操作 [{i}] ：工具：{req['name']} ──")

                            while True:
                                decision = input(f"      >>> 请输入决策 ({'/'.join(allowed)}): ").strip().lower()
                                if decision in allowed:
                                    break
                                print(f"      只允许: {allowed}")

                            if decision == "approve":
                                decisions.append({"type": "approve"})
                                print(f"      已批准：按原参数执行")
                            elif decision == "reject":
                                reason = input(f"      拒绝原因: ").strip() or "操作被人工拒绝"
                                decisions.append({"type": "reject", "message": reason})
                                print(f"      已拒绝：{reason}")

                        print(f"\n  提交决策: {decisions}")

                        # 构造恢复命令，替换下一轮 stream 的输入
                        next_input = Command(resume={"decisions": decisions})

                        # 跳出 for 循环，回到内层 while 顶部，用 Command(resume=...) 重新 stream
                        break

            # ── 内层 while 的分岔口 ──
            if not interrupted:
                # for 循环正常结束 → 本轮对话完成，跳出内层 while，回到外层等下一句
                print()  # 末尾换行
                break
            else:
                # for 循环被 break（有中断）→ 内层 while 回到顶部，用 next_input 恢复执行
                # 打印一个空行作为中断→恢复执行分割标志
                print("\nAgent正在恢复执行…\n")

    except Exception as e:
        print(f"\n调用过程中出现错误：{e}")



