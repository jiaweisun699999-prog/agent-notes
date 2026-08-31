from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langgraph.store.memory import InMemoryStore
from langchain.tools import tool

from init_llm import deepseek_llm


@dataclass
class Context:
    """用户上下文"""
    user_id: str
    user_role: str          # admin(管理员） / customer（客户）
    deployment_env: str     # production（生产环境） / staging（测试环境） / development（开发环境）


# 订单查询工具
@tool
def query_order(order_id: str) -> str:
    """根据订单ID查询订单详情。"""
    orders = {
        "ORD-1001": "蓝牙耳机（¥299），状态：已发货",
        "ORD-1002": "手机壳（¥39），状态：已签收",
    }
    return orders.get(order_id, f"未找到订单 {order_id}")


@dynamic_prompt
def context_dynamic_prompt(request: ModelRequest) -> str:
    """结合 State、Store、Runtime Context 三个数据源动态生成提示词"""

    # 从 State 中读取：当前消息数量
    message_count = len(request.messages)

    # 从 Store 中读取：用户偏好
    store = request.runtime.store
    user_prefs = None
    if store is not None:
        user_prefs = store.get(("preferences",), request.runtime.context.user_id)

    # 从 Runtime Context 中读取：用户角色和环境
    user_role = request.runtime.context.user_role
    env = request.runtime.context.deployment_env

    # 构造基础提示词
    base = "你是一个电商客服助手，帮助用户解决订单、退货、支付相关问题。"

    # 根据用户角色添加权限提示
    if user_role == "admin":
        base += "\n你拥有管理员权限，可以查看和修改所有用户的订单数据。"
    elif user_role == "customer":
        base += "\n你只能查看和操作当前用户自己的订单，不可访问其他用户的数据。"
    else:
        base += "\n你只有只读权限，不能修改任何数据。如果用户要求修改，请告知需要管理员权限。"

    # 根据对话长度调整回复风格
    if message_count > 20:
        base += "\n当前对话较长，请保持回复简洁，直接给出结论。"

    # 根据用户偏好调整语气
    if user_prefs and user_prefs.value.get("communication_style") == "温和":
        base += "\n用户偏好温和的沟通方式，请使用礼貌、体贴的语气。"

    # 根据部署环境添加注意事项
    if env == "production":
        base += "\n当前是生产环境，进行数据修改操作时务必先确认用户身份。"

    print("提示词：", base)
    return base


# 初始化 Store 并预置偏好
store = InMemoryStore()
store.put(("preferences",), "user_001", {"communication_style": "温和"})

agent = create_agent(
    model=deepseek_llm,
    tools=[query_order],
    middleware=[context_dynamic_prompt],
    context_schema=Context,
    store=store,
)

# 场景：温和偏好用户（user_001）在生产环境下查订单
result = agent.invoke(
    {"messages": [{"role": "user", "content": "你好，我想查一下订单 ORD-1001"}]},
    context=Context(user_id="user_001", user_role="customer", deployment_env="production"),
)
print(result["messages"][-1].content)


print("=" * 50)
# 场景：管理员在开发环境下查订单（无特殊语气偏好）
result2 = agent.invoke(
    {"messages": [{"role": "user", "content": "你好，我想查一下订单 ORD-1001"}]},
    context=Context(user_id="admin_001", user_role="admin", deployment_env="development"),
)
print(result2["messages"][-1].content)