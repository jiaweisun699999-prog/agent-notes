from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model, after_model
from langchain_core.messages import ToolMessage
from langchain_core.stores import InMemoryStore
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver
from langgraph.prebuilt import ToolRuntime
from langgraph.runtime import Runtime
from langgraph.types import Command

from init_llm import deepseek_llm


@tool
def get_weather(city:str) -> str:
    """根据城市名称获取天气信息"""
    return f"{city}天气晴朗"


@before_model
def before_model(state:AgentState,runtime:Runtime) -> dict[str,any] | None:
    print("before_model state:",state)
    print("before_model runtime:",runtime)
    tool_call_count = state.get("tool_call_count",0)

    tool_call_count = len([msg for msg in state["messages"] if isinstance(msg,ToolMessage)])

    return {"tool_call_count":tool_call_count}

@after_model
def after_model(state:AgentState,runtime:Runtime)-> dict[str,any] | None:
    print("after_model state:", state)
    print("after_model runtime:", runtime)

    model_call_count = state.get("model_call_count",0)

    model_call_count += 1

    return {"model_call_count":model_call_count}


class CustomState(AgentState):
    tool_call_count:int
    model_call_count:int


agent = create_agent(
    model=deepseek_llm,
    tools=[get_weather],
    middleware=[before_model,after_model],
    checkpointer=InMemorySaver(),
    state_schema=CustomState
)

config = {"configurable":{"thread_id":"session001"}}

resp1 = agent.invoke({"messages":[{"role":"user","content":"你好，我叫张三"}],},config=config)
print(resp1["messages"][-1].content)


print("-----------------")
resp2 = agent.invoke({"messages":[{"role":"user","content":"北京天气如何？"}]},config=config)
print(resp2["messages"][-1].content)

print("-----------------")

resp3 = agent.invoke({"messages":[{"role":"user","content":"你知道我的信息吗？"}]},config=config)
print(resp3["messages"][-1].content)


print("-----------------")
state = agent.get_state(config=config)
print(type(state))
print(state)


