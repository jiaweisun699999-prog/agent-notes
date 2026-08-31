from dataclasses import dataclass

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import (
    dynamic_prompt,
    before_model,
    after_model,
    ModelRequest,
)
from langgraph.runtime import Runtime
from langchain.tools import tool

from init_llm import deepseek_llm


@dataclass
class Context:
    """每次调用的上下文信息"""
    user_name: str
    user_role: str


# 简单工具：根据关键词查询常见问题解答
@tool
def query_faq(keyword: str) -> str:
    """根据关键词查询常见问题解答。"""
    faq = {
        "退货": "支持7天无理由退货，商品需完好且包装齐全。",
        "发货": "下单后48小时内发货。",
    }

    # 遍历 faq 每个key，判断每个key 是否 contain 包含 keyword
    for key in faq.keys():
        if keyword in key:
            return faq.get(key)

    return f"未找到关于'{keyword}'的FAQ条目"


# 动态系统提示词：根据用户角色和姓名定制提示
@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    """每次模型调用前，根据 Runtime Context 动态生成系统提示词"""
    ctx = request.runtime.context
    base_prompt = f"你是一个乐于助人的客服助手。当前在为用户 {ctx.user_name} 服务。"

    if ctx.user_role == "admin":
        base_prompt += " 你拥有管理员权限，可以查看和修改所有数据。"
    elif ctx.user_role == "customer":
        base_prompt += " 你可以帮用户查询订单、申请退款、修改收货地址。"
    else:
        base_prompt += " 你仅有只读权限，不能执行修改操作。"

    return base_prompt


# 模型调用前钩子：记录请求日志
@before_model
def log_before_model(state: AgentState, runtime: Runtime[Context]) -> dict | None:
    """每次调用模型前记录日志，包含用户信息和线程标识"""
    user_name = runtime.context.user_name
    print(f"[Agent日志] 用户={user_name}，开始调用模型...")
    return None  # 返回 None 表示不修改 State


# 模型调用后钩子：记录完成日志
@after_model
def log_after_model(state: AgentState, runtime: Runtime[Context]) -> dict | None:
    """每次模型调用完成后记录日志"""
    user_name = runtime.context.user_name
    print(f"[Agent日志] 用户={user_name}的模型调用已完成")
    return None


agent = create_agent(
    model=deepseek_llm,
    tools=[query_faq],
    middleware=[dynamic_system_prompt, log_before_model, log_after_model],
    context_schema=Context,
    system_prompt="",
)


result = agent.invoke(
    {"messages": [{"role": "user", "content": "你好！我想了解一下退货政策"}]},
    context=Context(user_name="张三", user_role="customer"),
)
print("result",result)
print(result["messages"][-1].content)

print("=" * 50)

result2 = agent.invoke(
    {"messages": [{"role": "user", "content": "你好！我想了解一下退货政策"}]},
    context=Context(user_name="李四", user_role="admin"),
)
print("result2",result2)
print(result2["messages"][-1].content)