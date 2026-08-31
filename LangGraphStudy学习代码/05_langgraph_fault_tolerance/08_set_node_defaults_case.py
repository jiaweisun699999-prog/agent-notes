"""
设置节点默认容错策略
"""
import asyncio
from typing import TypedDict

from langgraph.constants import START, END
from langgraph.errors import NodeError
from langgraph.graph import StateGraph
from langgraph.types import RetryPolicy, TimeoutPolicy, Command


class State(TypedDict):
    ticket_id: str # 工单ID
    status: str # 工单状态

async def default_error_handler(state:State,error:NodeError)->dict:
    print(f"[默认错误处理]执行，错误节点：{error.node},错误信息：{error.error}")
    return {"status":f"处理错误，错误节点：{error.node},错误信息：{error.error}"}


async def charge_fee_error_handler(state:State,error:NodeError)->Command:
    print(f"[charge_fee 专属错误处理]执行，错误节点：{error.node},错误信息：{error.error}")
    return Command(
        update={
            "status":"收费失败，已通知用户"
        },
        goto="finalize"
    )

async def classify_ticket(state: State) -> dict:
    """分类工单"""
    print(f"[classify_ticket] 分类工单={state['ticket_id']}")
    # 模拟TK-002 抛出异常，走全局默认错误处理器
    if state["ticket_id"] == "TK-002":
        raise RuntimeError("工单分类失败，异常：余额不足")
    return {"status": "已分类"}


async def charge_fee(state: State) -> dict:
    """收费：模拟失败"""
    print(f"[charge_fee] 收取服务费...")
    raise RuntimeError("支付网关超时")


async def finalize(state: State) -> dict:
    """完成处理"""
    print(f"[finalize] 工单处理完毕")
    return {"status": state.get("status", "") + "，已完结"}



builder = StateGraph(State)

# 设置默认的容错策略
builder.set_node_defaults(
    # 全局默认值:所有节点执行重试策略
    retry_policy=RetryPolicy(max_attempts=3),
    # 全局默认值：所有节点执行超时的策略
    timeout=TimeoutPolicy(run_timeout=20),
    # 全局默认值：所有节点执行错误处理器
    error_handler=default_error_handler
)


builder.add_node("classify_ticket", classify_ticket)
builder.add_node("charge_fee", charge_fee,error_handler=charge_fee_error_handler)
builder.add_node("finalize", finalize)

builder.add_edge(START, "classify_ticket")
builder.add_edge("classify_ticket", "charge_fee")
builder.add_edge("charge_fee", "finalize")
builder.add_edge("finalize", END)


graph = builder.compile()

async def main():
    result1 = await graph.ainvoke({"ticket_id": "TK-001"})
    print("result1:",result1)

    print("="*100)

    result2 = await graph.ainvoke({"ticket_id": "TK-002"})
    print("result2:",result2)


asyncio.run(main())
