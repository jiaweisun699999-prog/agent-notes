from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime

from init_llm import deepseek_llm


# 第一步：定义上下文的类型结构
@dataclass
class Context:
    """每次 Agent 调用时传入的静态配置信息"""
    user_name: str
    user_role: str          # 用户角色，如 "admin" / "viewer"


# 第二步：定义工具（模拟订单查询和用户信息获取）
@tool
def query_my_orders(runtime: ToolRuntime[Context]) -> str:
    """查询当前用户的订单列表。当用户想了解自己的订单状态时使用此工具。"""
    user_name = runtime.context.user_name
    print(f"[工具内部] 查询用户 {user_name} 的订单...")
    # 模拟数据库查询
    return f"用户 {user_name} 的订单：ORD-1001（已发货）、ORD-1002（待付款）"


@tool
def get_user_profile(runtime: ToolRuntime[Context]) -> str:
    """获取当前用户的个人档案信息，包括会员等级和积分。"""
    user_name = runtime.context.user_name
    user_role = runtime.context.user_role
    return f"用户名：{user_name}，角色：{user_role}，会员等级：VIP，积分：1280"


# 第三步：创建 Agent 时声明 context_schema
agent = create_agent(
    model=deepseek_llm,
    tools=[query_my_orders, get_user_profile],
    context_schema=Context,  # 声明该 Agent 期望接收的上下文类型
    system_prompt="你是一个电商客服助手，帮助用户查询订单和个人信息。",
)


# 第四步：调用 Agent 时传入实际的上下文数据
result = agent.invoke(
    {"messages": [{"role": "user", "content": "帮我查一下我的订单状态"}]},
    context=Context(
        user_name="张三",
        user_role="customer",
    ),
)
print(result["messages"][-1].content)

print("=" * 50)
result2 = agent.invoke(
    {"messages": [{"role": "user", "content": "查看我的个人档案"}]},
    context=Context(
        user_name="李四",
        user_role="admin",
    ),
)
print(result2["messages"][-1].content)