import asyncio
from typing import TypedDict

from langgraph._internal._retry import default_retry_on
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import RetryPolicy, TimeoutPolicy


class State(TypedDict):
    result:str


async def process_payment(state:State):
    """
    处理支付
    """
    print(f"[process_payment 节点执行]...")

    # 模拟等待时间
    await asyncio.sleep(5)

    return {"result":"支付成功"}



builder = StateGraph(State)
builder.add_node(
    "process_payment",
    process_payment,
    timeout=TimeoutPolicy(run_timeout=20, idle_timeout=3) # 超时20秒，空闲超时3秒
)


builder.add_edge(START,"process_payment")
builder.add_edge("process_payment",END)

graph = builder.compile()

async def main():
    result = await graph.ainvoke({"result": ""})
    print(result)


asyncio.run(main())


