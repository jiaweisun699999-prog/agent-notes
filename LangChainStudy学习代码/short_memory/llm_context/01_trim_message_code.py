from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model
from langchain_core.messages import RemoveMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime

from init_llm import deepseek_llm


@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气
    Args:
        city (str): 要查询天气的城市名称

    Returns:
        str: 包含城市天气信息的字符串
    """
    return f"{city}的天气是晴朗的，温度是25摄氏度"


@before_model
def trim_message(state:AgentState,runtime:Runtime) -> dict|None:
    print("当前state:",state)
    print("当前runtime:",runtime)

    messages = state["messages"]
    if len(messages) > 5:
        retain_msg_count = 3

        if messages[-retain_msg_count].type == "tool":
            retain_msg_count = 2

        print("保留的消息:",messages[-retain_msg_count:])

        return {"messages": [RemoveMessage(id=msg.id) for msg in messages[:-retain_msg_count]]}

    return None


agent = create_agent(
    model=deepseek_llm,
    tools=[get_weather],
    middleware=[trim_message],
    checkpointer=InMemorySaver()
)


config = {"configurable": {"thread_id": "session_001"}}

# 模拟对话
response1 = agent.invoke({"messages": [{"role": "user", "content": "你好，我是张三"}]}, config=config)
print(response1["messages"][-1].content)
print("***"*20)
response2 = agent.invoke({"messages": [{"role": "user", "content": "今天北京天气好吗？"}]}, config=config)
print(response2["messages"][-1].content)
print("***"*20)
response3 = agent.invoke({"messages": [{"role": "user", "content": "上海天气怎么样？"}]}, config=config)
print(response3["messages"][-1].content)
print("***"*20)
final_response = agent.invoke({"messages": [{"role": "user", "content": "我的名字叫什么？"}]}, config=config)
print(final_response["messages"][-1].content)

