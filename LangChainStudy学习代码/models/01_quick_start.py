"""
创建一个Agent，调用工具回答用户问题，
"""
from langchain.agents import create_agent
from langchain_core.tools import tool

from my_llm import deepseek_llm

@tool
def get_weather(location: str) -> str:
    """
    获取指定位置的天气信息
    """
    return f"天气信息：{location}的天气是晴朗的"

agent = create_agent(
    model=deepseek_llm,
    tools=[get_weather],
    system_prompt="你是一个天气助手，你可以帮助用户获取指定位置的天气信息。",
)

# 调用Agent
resp = agent.invoke({"messages": [{"role": "user", "content": "北京的天气"}]})
print(type(resp))
print(resp)





