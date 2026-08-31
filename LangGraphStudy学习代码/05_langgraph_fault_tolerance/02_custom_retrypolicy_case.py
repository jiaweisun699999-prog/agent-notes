
from typing import TypedDict

from langgraph._internal._retry import default_retry_on
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import RetryPolicy


class State(TypedDict):
    result:str

class InsufficientBalanceError(Exception):
    pass


def process_payment(state:State):
    """
    处理支付
    """
    print(f"[process_payment 节点执行]，尝试处理支付...")

    # 模拟支付失败
    raise InsufficientBalanceError(f"账户余额不足，无法支付")


def custom_retry_on(error:Exception) -> bool:
    if isinstance(error,InsufficientBalanceError):
        return False # 不重试
    return default_retry_on(error)

builder = StateGraph(State)
builder.add_node(
    "process_payment",
    process_payment,
    # 重试策略，max_attempts=3 表示最多重试3次，initial_interval=0.5 表示初始重试间隔为0.5秒，backoff_factor 表示退避因子
    retry_policy=RetryPolicy(max_attempts=3,initial_interval=0.5,backoff_factor=2,
                             retry_on=custom_retry_on
                             )
)

builder.add_edge(START,"process_payment")
builder.add_edge("process_payment",END)

graph = builder.compile()

result = graph.invoke({"result":""})

print(result)



