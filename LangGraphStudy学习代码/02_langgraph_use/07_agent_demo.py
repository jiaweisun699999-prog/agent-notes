from langchain.agents import create_agent
from langchain.tools import tool

from init_llm import deepseek_llm


@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息。"""
    return f"{city}的天气为晴朗，25°C。"


agentx = create_agent(
    model=deepseek_llm,
    tools=[get_weather],
    system_prompt="你是能查询任何问题的助手"
)