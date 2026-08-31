from dataclasses import dataclass
from typing import Callable

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain.tools import tool, ToolRuntime

from init_llm import deepseek_llm


@dataclass
class Context:
    user_role: str  # admin / customer


# ========== 全量工具定义 ==========

@tool
def query_order_status(order_id: str, runtime: ToolRuntime[Context]) -> str:
    """查询指定订单的当前状态。"""
    return f"订单 {order_id} 的状态：已发货，查询人角色：{runtime.context.user_role}"


@tool
def cancel_order(order_id: str, runtime: ToolRuntime[Context]) -> str:
    """取消指定订单并退款。仅管理员可操作。"""
    return f"订单 {order_id} 已取消，退款已处理。操作人角色：{runtime.context.user_role}"


@tool
def view_all_orders(runtime: ToolRuntime[Context]) -> str:
    """查看系统中所有订单。仅管理员可操作。"""
    return f"系统订单总数：1250 笔，查询人角色：{runtime.context.user_role}"


# ========== 动态工具过滤中间件 ==========

@wrap_model_call
def role_based_tool_filter(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """根据用户角色动态过滤工具列表。

    注意：
    - 所有工具在 create_agent 中全量注册（Agent 知道每个工具怎么执行）。
    - 中间件根据角色裁剪 request.tools，控制模型实际"看到"哪些工具。
    - 管理员看到 3 个工具，普通用户只看到 1 个 → 减少上下文 Token 占用。
    """
    user_role = request.runtime.context.user_role

    if user_role == "admin":
        # 管理员：保留全部工具，不做过滤
        pass
    else:
        # 普通用户：只保留 query_order_status，过滤掉管理员专用工具
        allowed = {"query_order_status"}
        filtered = [t for t in request.tools if t.name in allowed]
        request = request.override(tools=filtered)

    return handler(request)


# 全量注册所有工具，中间件负责运行时裁剪
agent = create_agent(
    model=deepseek_llm,
    tools=[query_order_status, cancel_order, view_all_orders],  # 全量注册
    middleware=[role_based_tool_filter],                        # 运行时过滤
    context_schema=Context,
    system_prompt="你是一个电商客服助手，帮助用户处理商品查询和订单管理。",
)

print("=" * 50)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "你可以调用的工具有哪些？"}]},
    context=Context(user_role="customer"),
)
print(result["messages"][-1].content)


print("=" * 50)
result2 = agent.invoke(
    {"messages": [{"role": "user", "content": "你可以调用的工具有哪些？"}]},
    context=Context(user_role="admin"),
)
print(result2["messages"][-1].content)