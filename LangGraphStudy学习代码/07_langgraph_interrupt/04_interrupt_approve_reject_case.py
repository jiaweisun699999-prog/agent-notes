from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command


class State(TypedDict):
    """图状态：退款详情、处理结果、最近一次审批输入"""
    refund_detail: str
    status: str
    approval_answer: str


def approval_node(state: State) -> dict:
    """节点：interrupt 一次收集审批输入，不判断合法性（判断交给条件边路由）"""
    decision = interrupt({
        "question": "是否批准这笔退款？请回复[是/否]",
        "detail": state["refund_detail"],
    })
    return {"approval_answer": str(decision).strip()}


def proceed_node(state: State) -> dict:
    """节点：审批通过，执行退款"""
    return {"status": "已批准，退款已执行"}


def cancel_node(state: State) -> dict:
    """节点：审批拒绝，取消退款"""
    return {"status": "已拒绝，退款已取消"}


def route_approval(state: State) -> str:
    """路由函数：根据审批输入分流 —— 是→执行 / 否→取消 / 其它→回跳重新审批"""
    answer = state.get("approval_answer", "")
    if answer == "是":
        return "proceed"
    if answer == "否":
        return "cancel"
    return "approval"   # 非是/否：回跳 approval 重新询问


# ============================================================
# 构建图（带 Checkpointer）
# ============================================================
builder = StateGraph(State)
builder.add_node("approval", approval_node)
builder.add_node("proceed", proceed_node)
builder.add_node("cancel", cancel_node)

builder.add_edge(START, "approval")
builder.add_conditional_edges("approval", route_approval, {
    "approval": "approval",
    "proceed": "proceed",
    "cancel": "cancel",
})
builder.add_edge("proceed", END)
builder.add_edge("cancel", END)

graph = builder.compile(checkpointer=InMemorySaver())


def get_user_input(interrupt_info) -> str:
    """根据中断信息向用户提问并读取输入（通用：字符串/字典都行）"""
    if isinstance(interrupt_info, str):
        return input(f"\n[系统]: {interrupt_info}\n[用户]: ").strip()

    # 字典场景：遍历所有键值对展示，原样返回输入
    show_info = "\n".join(f"{k}:{v}" for k, v in interrupt_info.items())
    return input(f"\n[系统]: {show_info}\n[用户]: ").strip()


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "thread001"}}

    # 输入退款详情
    stream_input: dict | Command = {
        "refund_detail": "退款 500 元至订单 ORD001",
        "status": "",
        "approval_answer": "",
    }

    while True:
        # 1. 调用图，事件流驱动
        stream = graph.stream_events(stream_input, config=config, version="v3")

        # 2. 流式显示回复（本图无 LLM 节点，仅保证事件流模式可用）
        print("【LLM】", end="", flush=True)
        for message in stream.messages:
            for token in message.text:
                if token.strip():
                    print(token, end="", flush=True)
        print()

        # 3. 图没有中断，完整跑完
        if not stream.interrupted:
            final_state = stream.output
            print(f"\n===== 最终状态：{final_state} =====")
            break

        # 4. 图中断，读取中断信息向用户提问
        try:
            user_response = get_user_input(stream.interrupts[0].value)
        except (EOFError, KeyboardInterrupt):
            print("\n[系统] 用户中断退出，会话结束")
            break

        # 5. 用户输入作为 resume 继续，进入下一轮
        stream_input = Command(resume=user_response)
