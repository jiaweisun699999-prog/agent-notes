from typing import Annotated, TypedDict
import operator

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command


class State(TypedDict):
    """图状态：收集结果列表（operator.add 累积，避免重跑覆盖）"""
    value: Annotated[list[str], operator.add]


def ask_order(state: State) -> dict:
    """节点一：收集订单号（中断）"""
    return {"value": [f"订单号={interrupt('请输入订单号：')}"]}


def ask_reason(state: State) -> dict:
    """节点二：收集退款原因"""
    return {"value": ["原因=商品破损"]}


def confirm(state: State) -> dict:
    """节点三：确认退款"""
    return {"value": ["确认=确认退款"]}


builder = StateGraph(State)
builder.add_node("ask_order", ask_order)
builder.add_node("ask_reason", ask_reason)
builder.add_node("confirm", confirm)

builder.add_edge(START, "ask_order")
builder.add_edge("ask_order", "ask_reason")
builder.add_edge("ask_reason", "confirm")
builder.add_edge("confirm", END)

graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "thread001"}}


if __name__ == "__main__":
    # 正常完成三个中断
    graph.invoke({"value": []}, config)            # 订单号中断
    final = graph.invoke(Command(resume="ORD123"), config)      # 原因中断
    print(f"完整流程：{final}")

    # fork 到"订单号之后、原因之前"的检查点，改订单号
    print("\n========== Fork：改订单号，只重问原因与确认 ==========\n")
    history = list(graph.get_state_history(config))
    ask_order = next(s for s in history if s.next == ("ask_reason",))

    fork_config1 = graph.update_state(
        ask_order.config,
        values={"value": ["订单号=ORD999"]},
        as_node="ask_order",
    )

    result1 = graph.invoke(None, fork_config1)
    print(f"fork 后result1结果：{result1}")

    print("\n========== Fork：直接跳过某些节点，直接执行最后节点 ==========\n")

    fork_config2 = graph.update_state(
        ask_order.config,
        values={"value": ["订单号=ORD1000", "原因=商品质量"]},
        as_node="ask_reason", # 通过模拟发出"原因"节点的中断，直接跳过"确认"节点
    )
    result2 = graph.invoke(None, fork_config2)
    print(f"fork 后result2结果: {result2}")


