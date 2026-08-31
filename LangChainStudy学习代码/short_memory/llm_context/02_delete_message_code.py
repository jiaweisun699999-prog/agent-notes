from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import after_model
from langchain.messages import RemoveMessage
from langchain_core.messages import ToolMessage, AIMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.prebuilt import ToolRuntime
from langgraph.runtime import Runtime
from langgraph.types import Command

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

@tool
def update_delete_history_state(runtime:ToolRuntime,delete_history:bool) ->Command:
    """是否清空聊天历史记录
    Args:
        delete_history (bool): 是否清空聊天历史记录

    Returns:
        Command: 包含更新状态的命令
    """
    # 准备更新内容
    updates = {
        "delete_history": delete_history,
        "messages": [
            ToolMessage(
                content=f"已更新删除聊天历史记录状态：{delete_history}",
                tool_call_id=runtime.tool_call_id
            )
        ]
    }

    return Command(update=updates)


@after_model
def delete_messages(state: AgentState, runtime: Runtime) -> dict|None:
    print("当前state：", state)

    # 获取删除聊天历史记录状态，决定是否清空聊天历史记录，只在最后一条消息是AIMessage时清空
    delete_history = state.get("delete_history")
    if delete_history:
        return {
          "delete_history": False,
          # "messages": [RemoveMessage(id=m.id) for m in state["messages"],AIMessage(content="已清空聊天历史记录")]
          "messages": [RemoveMessage(id=m.id) for m in state["messages"][:-1]]
        }
        # return {
        #     "delete_history": False,
        #     "messages":[RemoveMessage(id=REMOVE_ALL_MESSAGES),
        #                 AIMessage(content="聊天历史记录已经成功删除，现在我们的对话将从新的状态开始，有什么其他我可以帮助你的吗？")]
        #     }
    return None

class CustomState(AgentState):
    delete_history: bool

agent = create_agent(
    model=deepseek_llm,
    tools=[get_weather,update_delete_history_state],
    middleware=[delete_messages],
    checkpointer=InMemorySaver(),
    state_schema=CustomState
)

config = {"configurable": {"thread_id": "session_001"}}

# 模拟对话
response1 = agent.invoke({
    "messages": [{"role": "user", "content": "你好，我是张三"}],
    "delete_history": False,
}, config=config)

print(response1["messages"][-1].content)

print("***"*20)
response2 = agent.invoke({"messages": [{"role": "user", "content": "今天北京天气好吗？"}]}, config=config)
print(response2["messages"][-1].content)

print("***"*20)
response3 = agent.invoke({"messages": [{"role": "user", "content": "我的名字叫什么？"}]}, config=config)
print(response3["messages"][-1].content)

print("***"*20)
response4 = agent.invoke({"messages": [{"role": "user", "content": "请给我删除聊天历史记录"}]}, config=config)
print(response4["messages"][-1].content)

print("***"*20)
final_response = agent.invoke({"messages": [{"role": "user", "content": "我的名字叫什么？"}]}, config=config)
print(final_response["messages"][-1].content)