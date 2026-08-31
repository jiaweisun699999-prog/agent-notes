from langgraph.checkpoint.memory import MemorySaver, InMemorySaver
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.types import interrupt, Command


# ============================================================
# 子图：退款审批（MessagesState 上扩展私有字段 refund_amount）
# ============================================================
class RefundState(MessagesState):
    """退款子图状态：共享 messages，额外增加退款金额私有字段"""
    refund_amount: int


def plan_refund(state: RefundState) -> dict:
    """子图节点一：生成退款方案"""
    return {
        "refund_amount": 88,
        "messages": [{"role": "assistant", "content": "建议退款 88 元"}],
    }


def approve_refund(state: RefundState) -> dict:
    """子图节点二：interrupt 暂停，等待人工审批"""
    decision = interrupt({"question": "是否批准退款？", "amount": state["refund_amount"]})
    return {"messages": [{"role": "assistant", "content": "已退款" if decision == "approve" else "已拒绝"}]}


refund_builder = StateGraph(RefundState)
refund_builder.add_node("plan_refund", plan_refund)
refund_builder.add_node("approve_refund", approve_refund)

refund_builder.add_edge(START, "plan_refund")
refund_builder.add_edge("plan_refund", "approve_refund")
refund_builder.add_edge("approve_refund", END)

refund_subgraph = refund_builder.compile()


# ============================================================
# 主图：退款子图作为节点
# ============================================================
builder = StateGraph(MessagesState)
builder.add_node("refund", refund_subgraph)

builder.add_edge(START, "refund")
builder.add_edge("refund", END)

graph = builder.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "thread001"}}

    # 调用：执行到子图内的 interrupt，暂停
    graph.invoke({"messages": [{"role": "user", "content": "耳机有质量问题，申请退款"}]}, config)

    print("\n========== 子图状态（get_state(subgraphs=True)） ==========")
    snap1 = graph.get_state(config, subgraphs=True)
    print("snap1:",snap1)

    # 审批通过，恢复执行
    graph.invoke(Command(resume="approve"), config)
    snap2 = graph.get_state(config, subgraphs=True)
    print("snap2:", snap2)
