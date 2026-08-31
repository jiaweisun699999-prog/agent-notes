from dataclasses import dataclass

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model
from langgraph.runtime import Runtime
from langchain.tools import tool

from init_llm import deepseek_llm


@dataclass
class Context:
    user_name: str


# 获取当前系统时间工具
@tool
def get_current_time() -> str:
    """获取当前系统时间。当用户询问时间时使用。"""
    from datetime import datetime
    return f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


@before_model
def auth_gate(state: AgentState, runtime: Runtime ) -> dict | None:
    server_info = runtime.server_info
    exec_info = runtime.execution_info

    print("server_info",server_info)
    print("exec_info",exec_info)

    return None


agent = create_agent(
    model=deepseek_llm,
    tools=[get_current_time],
    middleware=[auth_gate],
    context_schema=Context,
    system_prompt="你是一个助手，可以帮助用户查询时间。",
)

print("=" * 50)
config = {"configurable": {"thread_id": "123"}}
result = agent.invoke(
    {"messages": [{"role": "user", "content": "现在几点了？"}]},
    context=Context(user_name="张三"),
    config=config,
)
print(result["messages"][-1].content)