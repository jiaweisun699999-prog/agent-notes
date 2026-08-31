"""
订单处理主流程中，需要调用"订单查询子图"
子图有独立的订单状态 schema（order_id/ status），与主图（order_id / result）没有共享字段：
"""
from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph


#子图状态
class OrderQueryState(TypedDict):
    order_id:str # 订单号
    status:str # 订单状态

def lookup_order(state:OrderQueryState):
    "步骤一：查询订单支付状态"
    return {"status":f"订单{state["order_id"]} 已经支付！"}

def lookup_logistics(state:OrderQueryState):
    """步骤二：查询订单物流状态"""
    return {"status":f"{state["status"]} 状态为物流已经揽收，发货中"}

order_subgraph_builder = StateGraph(OrderQueryState)
order_subgraph_builder.add_node("lookup_order",lookup_order)
order_subgraph_builder.add_node("lookup_logistics",lookup_logistics)

order_subgraph_builder.add_edge(START,"lookup_order")
order_subgraph_builder.add_edge("lookup_order","lookup_logistics")
order_subgraph_builder.add_edge("lookup_logistics",END)

order_subgraph = order_subgraph_builder.compile()


#主图状态
class OrderState(TypedDict):
    order_id:str # 订单号
    result:str # 订单查询结果

def call_order_subgraph(state:OrderState):
    """调用订单查询子图"""
    subgraph_output = order_subgraph.invoke({"order_id":state["order_id"],"status":""})
    return {"result":subgraph_output["status"]}

#构建主图
builder = StateGraph(OrderState)
builder.add_node("call_order_subgraph",call_order_subgraph)
builder.add_edge(START,"call_order_subgraph")
builder.add_edge("call_order_subgraph",END)

graph = builder.compile()

result = graph.invoke({"order_id":"order_123"})

print(result)
