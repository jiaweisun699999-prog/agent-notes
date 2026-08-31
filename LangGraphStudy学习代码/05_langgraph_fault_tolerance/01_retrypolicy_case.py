
"""
 retry_policy 重试策略
 执行某个节点，该节点执行报错：ConnectionError ，重试3次
"""
from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import RetryPolicy


class State(TypedDict):
    result:str # 订单查询结果

attempt_counter = 0


def fetch_order_status(state:State):
    """
    从订单系统查询订单状态
    """
    global attempt_counter
    attempt_counter += 1

    print(f"[fetch_order_status 节点执行] 第{attempt_counter}次尝试调用查询订单状态")

    if attempt_counter < 3:
        raise ConnectionError(f"订单系统连接失败，第{attempt_counter}次尝试调用")

    return {"result":"订单状态查询成功"}


builder = StateGraph(State)
builder.add_node(
    "fetch_order_status",
    fetch_order_status,
    # 重试策略，max_attempts=3 表示最多重试3次，initial_interval=0.5 表示初始重试间隔为0.5秒，backoff_factor 表示退避因子
    retry_policy=RetryPolicy(max_attempts=3,initial_interval=0.5,backoff_factor=2)
)

builder.add_edge(START,"fetch_order_status")
builder.add_edge("fetch_order_status",END)

graph = builder.compile()

result = graph.invoke({"result":""})

print(result)



