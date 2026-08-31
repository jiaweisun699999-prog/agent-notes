from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.graph.state import CompiledStateGraph

from init_llm import deepseek_llm


@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息。"""
    return f"{city}的天气为晴朗，25°C。"


agent = create_agent(
    model=deepseek_llm,
    tools=[get_weather],
    # system_prompt="你是能查询任何问题的助手",
    system_prompt = SystemMessage(content="你是能查询任何问题的助手")
)

resp = agent.invoke( {
    "messages": [
        {"role": "system", "content": "你是一个天气查询助手，只回答天气相关的问题，其他问题请直接回答：我不清楚这问题答案。"},
        {"role": "user", "content": "北京天气如何？"}

    ]
})

for msg in resp["messages"]:
    msg.pretty_print()
