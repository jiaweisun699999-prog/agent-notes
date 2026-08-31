from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.errors import NodeError
from langgraph.types import Command, RetryPolicy


class State(TypedDict):
    order_id: str # 订单ID
    status: str # 订单状态
    message: str # 订单状态描述


def charge_payment(state: State) -> dict:
    """支付扣款节点，模拟支付网关超时，始终失败"""
    print(f"[charge_payment] 尝试扣款, 订单={state['order_id']}")
    raise RuntimeError("支付网关连接超时")


def success(state: State) -> dict:
    """成功节点，模拟支付成功"""
    print(f"[success] 订单{state['order_id']}支付成功")
    return {"status": "支付成功"}


def payment_error_handler(state: State, error: NodeError) -> Command:
    """
    支付错误处理器，在重试耗尽后执行。
    记录失败原因等状态，然后路由到通知节点。
    error: NodeError 包含 node（失败节点名）和 error（异常对象）
    """
    print(f"[error_handler] 节点 '{error.node}' 失败: {error.error}")
    return Command(
        update={
            "status": "支付失败",
            "message": f"扣款失败，已记录: {error.error}",
        },
        goto="notify_user",
    )


def notify_user(state: State) -> dict:
    """通知用户节点 —— 发送支付失败通知"""
    print(f"[notify_user] 发送通知: 订单{state['order_id']}支付失败")
    return {"status": "已通知用户"}


# ============================================================
# 构建图
# ============================================================
builder = StateGraph(State)
builder.add_node(
    "charge_payment",
    charge_payment,
    retry_policy=RetryPolicy(
        max_attempts=2,
        retry_on=RuntimeError # 本身RuntimeError不会重试，这里设置重试，重试2次后失败，执行error_handler
    ),
    error_handler=payment_error_handler,
)
builder.add_node("notify_user", notify_user)
builder.add_node("success", success)


builder.add_edge(START, "charge_payment")
builder.add_edge("charge_payment", "success")
builder.add_edge("success", END)

# charge_payment 通过 Command goto 路由，不需要显式边
builder.add_edge("notify_user", END)

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke({"order_id": "ORD-xxx", "status": "", "message": ""})
    print(f"最终状态: {result}")
