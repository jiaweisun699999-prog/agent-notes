from typing import Dict, Any
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import PIIMiddleware, before_agent, before_model, after_model, wrap_tool_call, after_agent
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.runtime import Runtime
from langgraph.types import Command

from init_llm import deepseek_llm


# 工具定义
@tool
def get_user_info(email: str) -> str:
    """模拟获取用户信息工具"""
    print("\n" + "=" * 60)
    user_info = f"用户信息: 用户的邮箱为 {email}"
    print(f"【get_user_info工具正在执行】- 返回用户信息: {user_info}")
    print("\n" + "=" * 60)
    return user_info

@before_agent
def track_before_agent(state:AgentState, runtime: Runtime) -> Dict[str, Any] | None:
    """观察代理执行前的初始状态"""
    print("\n" + "="*60)
    print("【before_agent】 - 代理开始执行前")
    if state.get('messages'):
        print("初始消息（用户输入）:")
        for msg in state['messages']:
            print(f"  - 类型: {type(msg).__name__}, 内容: {msg.content}")
    else:
        print("状态中暂无消息。")
    print("="*60 + "\n")
    return None

@before_model
def track_before_model(state:AgentState, runtime: Runtime) -> Dict[str, Any] | None:
    """观察模型调用前的状态"""
    print("\n" + "="*60)
    print("【before_model】 - 模型调用前")
    if state.get('messages'):
        print("当前消息:")
        for msg in state['messages']:
            print(f"  - 类型: {type(msg).__name__}, 内容: {msg.content}")
    print("="*60 + "\n")
    return None


@after_model
def track_after_model(state:AgentState, runtime: Runtime) -> Dict[str, Any] | None:
    """观察模型调用后的状态"""
    print("\n" + "="*60)
    print("【after_model】 - 模型调用后")
    if state.get('messages'):
        print("当前消息:")
        for msg in state['messages']:
            print(f"  - 类型: {type(msg).__name__}, 内容: {msg.content}")
    print("="*60 + "\n")
    return None


@wrap_tool_call
def track_wrap_tool_call(request:ToolCallRequest, handler) -> ToolMessage | Command:
    """观察工具调用前的状态"""
    print("\n" + "="*60)
    print("【wrap_tool_call】 - 工具调用前")
    print(f"【即将调用工具】{request.tool_call['name']} 被调用，参数: {request.tool_call['args']}")
    print("="*60)
    return handler(request)


@after_agent
def track_after_agent(state:AgentState, runtime: Runtime) -> Dict[str, Any] | None:
    """观察代理执行后的状态"""
    print("\n" + "="*60)
    print("【after_agent】 - 代理执行完成")
    print("当前消息:")
    for msg in state['messages']:
        print(f"  - 类型: {type(msg).__name__}, 内容: {msg.content}")
    print("="*60 + "\n")
    return None

# 创建包含Pii中间件的 Agent
agent = create_agent(
    model=deepseek_llm,
    tools=[get_user_info],
    middleware=[
        # 安全中间件
        PIIMiddleware(
            pii_type="email",
            strategy="redact",
            apply_to_input=True, # 在模型调用前检查用户消息
            apply_to_tool_results=True, # 在工具调用后检查工具响应
            apply_to_output=True, # 在模型调用后检查模型响应
        ),
        # 添加其他中间件
        track_before_agent,   # 最先执行
        track_before_model,   # 其次执行
        track_wrap_tool_call,   # 工具调用前执行
        track_after_model,   # 最后执行模型调用后执行
        track_after_agent,   # 最后执行
    ],
)

# 测试
result = agent.invoke({
    "messages": [{"role": "user", "content": "我的邮箱是 zhangsan@company.com，请输出我的信息"}]
})
print(result)
print(f"模型响应: {result['messages'][-1].content}")
