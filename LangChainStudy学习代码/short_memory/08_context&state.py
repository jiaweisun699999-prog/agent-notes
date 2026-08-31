from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import after_model
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolRuntime
from langgraph.runtime import Runtime

from init_llm import deepseek_llm


@tool
def get_weather(location:str,state:AgentState,runtime:ToolRuntime)->str:
    """获取指定位置的天气"""
    # 工具中可以获取上下文 和状态
    print("get_weather state:",state)
    print("get_weather runtime:",runtime)

    return f"{location}的天气是晴天"


@after_model
def after_model(state:AgentState,runtime:Runtime)-> dict[str,any] | None:
    print("after_model state:",state)
    print("after_model runtime:",runtime)
    # 从runtime中获取上下文
    context = runtime.context
    if context:
        user_name = context["user_name"]
        channel = context["channel"]
    else:
        user_name = state["user_name"]
        channel = state["channel"]

    if "call_llm_count" not in state:
        return {"user_name":user_name,"channel":channel,"call_llm_count":1}

    # 从runtime中获取状态
    call_llm_count = state["call_llm_count"]
    call_llm_count +=1

    return {"user_name":user_name,"channel":channel,"call_llm_count":call_llm_count}

class ConversationState(AgentState):
    user_name:str
    channel:str
    call_llm_count:int



agent = create_agent(
    model=deepseek_llm,
    tools=[get_weather],
    middleware=[after_model],
    state_schema=ConversationState,
    # context_schema=xxx,
    checkpointer=InMemorySaver()
)

config={"configurable":{"thread_id":"1"}}

resp = agent.invoke(
    {"messages":[{"role":"user","content":"你好，北京天气怎么样"}]},
    config=config,
    context= {"user_name":"张三","channel":"微信"} #dict /pydantic 类型 /dataclass类型
)


resp2 = agent.invoke(
    {"messages":[{"role":"user","content":"上海天气怎么样"}]},
    config=config,
)


print(resp["messages"][-1].content)

print(agent.get_state(config=config))
