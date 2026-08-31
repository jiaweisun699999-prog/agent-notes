
"""
 retry_policy 重试策略
 执行某个节点，该节点执行报错：ConnectionError ，重试3次
"""
import asyncio
from typing import TypedDict

from langgraph.constants import START, END
from langgraph.errors import NodeError
from langgraph.graph import StateGraph
from langgraph.types import RetryPolicy, TimeoutPolicy, Command


class State(TypedDict):
    result:str # 订单查询结果
    notify_user:str # 通知用户结果

attempt_counter = 0


async def fetch_order_status(state:State):
    """
    从订单系统查询订单状态
    """
    global attempt_counter
    attempt_counter += 1

    print(f"[fetch_order_status 节点执行] 第{attempt_counter}次尝试调用查询订单状态")

    if attempt_counter < 3:
        await asyncio.sleep(5)

    return {"result":"订单状态查询成功"}


def notify_user(state:State):
    return {"notify_user":"已经给用户发送消息，通知用户"}



def error_handler(state:State, error:NodeError)-> Command | dict:
    """
    错误处理节点
    """
    print(f"[error_handler 节点执行] 执行错误节点：{error.node}, 错误信息：{error.error}")

    return Command(
        update={
            "result":"订单状态查询失败"
        },
        goto="notify_user"
    )



builder = StateGraph(State)
builder.add_node(
    "fetch_order_status",
    fetch_order_status,
    # 重试策略，max_attempts=3 表示最多重试3次，initial_interval=0.5 表示初始重试间隔为0.5秒，backoff_factor 表示退避因子
    retry_policy=RetryPolicy(max_attempts=2,initial_interval=0.5,backoff_factor=2),
    timeout=TimeoutPolicy(run_timeout=2), # 超时2秒
    # 错误处理，当节点执行报错后进行托底处理
    error_handler=error_handler
)
builder.add_node("notify_user",notify_user)

builder.add_edge(START,"fetch_order_status")
builder.add_edge("fetch_order_status",END)
builder.add_edge("notify_user",END)

graph = builder.compile()

async def main():
    result = await graph.ainvoke({"result":""})
    print(result)

asyncio.run(main())



