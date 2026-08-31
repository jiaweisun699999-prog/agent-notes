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
    """节点二：收集退款原因（中断）"""
    return {"value": [f"原因={interrupt('请输入退款原因：')}"]}


def confirm(state: State) -> dict:
    """节点三：确认退款（中断）"""
    return {"value": [f"确认={interrupt('确认退款？(yes/no)')}"]}


builder = StateGraph(State)
builder.add_node("ask_order", ask_order)
builder.add_node("ask_reason", ask_reason)
builder.add_node("confirm", confirm)
builder.add_edge(START, "ask_order")
builder.add_edge("ask_order", "ask_reason")
builder.add_edge("ask_reason", "confirm")
builder.add_edge("confirm", END)

graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "form-1"}}


if __name__ == "__main__":
    # 正常完成三个中断
    graph.invoke({"value": []}, config)            # 订单号中断
    graph.invoke(Command(resume="ORD123"), config)      # 原因中断
    graph.invoke(Command(resume="商品破损"), config)     # 确认中断
    final = graph.invoke(Command(resume="yes"), config)
    print(f"完整流程：{final['value']}\n")

    # fork 到"订单号之后、原因之前"的检查点，改订单号
    print("========== Fork：改订单号，只重问原因与确认 ==========")
    history = list(graph.get_state_history(config))
    ask_order = next(s for s in history if s.next == ("ask_reason",))

    fork_config = graph.update_state(
        ask_order.config,
        values={"value": ["订单号=ORD999"]},
        as_node="ask_order",
    )

    result = graph.invoke(None, fork_config)
    print(f"result: {result}")
    print(f"fork 后暂停：{result['value']}")   # 停在"原因"中断

    # 继续 resume：原因 -> 确认
    graph.invoke(Command(resume="外包装划痕"), config)
    end = graph.invoke(Command(resume="yes"), config)
    print(f"最后结果：{end['value']}")
