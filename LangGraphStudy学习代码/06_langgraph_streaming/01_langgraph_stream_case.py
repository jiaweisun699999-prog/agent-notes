from typing import TypedDict

from langgraph.config import get_stream_writer
from langgraph.constants import START, END
from langgraph.graph import StateGraph


class State(TypedDict):
    order_id:str # 订单ID
    result:str #处理结果

def query_order(state:State):
    """查询订单"""
    writer = get_stream_writer()
    writer({"step": "查询订单", "percent": 50})
    return {"result":f"查询订单{state['order_id']}，查询成功"}


def create_delivery(state:State):
    """创建配送单"""
    writer = get_stream_writer()
    writer({"step": "生成发货单", "percent": 100})
    return {"result": f"创建配送单{state['order_id']}，成功"}

builder = StateGraph(State)
builder.add_node("query_order", query_order)
builder.add_node("create_delivery", create_delivery)

builder.add_edge(START, "query_order")
builder.add_edge("query_order", "create_delivery")
builder.add_edge("create_delivery", END)

graph = builder.compile()

if __name__ == '__main__':
    inputs = {"order_id":"ORD001","result":""}
    print("=========== v1 输出模式（默认），对于单个stream_mode 返回的dict =============")
    for chunk in graph.stream(inputs,stream_mode="updates"):
        print("chunk:",chunk)

    print("=========== v1 输出模式（默认），对于组合的 stream_mode 返回的 (mode,data)=============")
    for chunk in graph.stream(inputs,stream_mode=["updates","custom"]):
        print("chunk:",chunk)


