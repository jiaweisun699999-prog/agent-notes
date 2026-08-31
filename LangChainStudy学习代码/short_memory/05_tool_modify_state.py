from langchain.agents import create_agent, AgentState
from langchain_core.messages import ToolMessage
from langchain_core.stores import InMemoryStore
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver
from langgraph.prebuilt import ToolRuntime
from langgraph.types import Command

from init_llm import deepseek_llm

@tool
def get_info(runtime:ToolRuntime)->str:
    """获取用户信息
    """
    print("get_info runtime:",runtime)

    user_id = runtime.state["user_id"]
    user_level = runtime.state["user_level"]

    return f"用户ID: {user_id}, 用户等级: {user_level}"

@tool
def update_info(runtime:ToolRuntime,user_id:str,user_level:str)-> Command:
    """更新用户信息
    Args:

        user_id (str): 用户ID
        user_level (str): 用户等级
        runtime (ToolRuntime): 工具运行时环境
    Returns:
        Command: 更新用户信息的命令
    """
    print("update_info runtime:",runtime)

    if not user_id or not user_level:
        return Command(update={
            "messages":[ToolMessage(
                content=f"用户ID不能为空或用户等级不能为空，没有更新用户信息",
                tool_call_id=runtime.tool_call_id
            )]
        })

    return Command(update={
        "user_id":user_id,
        "user_level":user_level,
        "messages":[ToolMessage(
            content=f"用户信息已经更改，用户ID: {user_id}, 用户等级: {user_level}",
            tool_call_id=runtime.tool_call_id
        )]
    })


class CustomState(AgentState):
    user_id: str
    user_level: str

agent = create_agent(
    model=deepseek_llm,
    tools=[get_info,update_info],
    checkpointer=InMemorySaver(),
    state_schema=CustomState
)

config = {"configurable":{"thread_id":"session001"}}

resp1 = agent.invoke({
    "messages":[{"role":"user","content":"获取我的信息"}],
    "user_id":"user_001",
    "user_level":"VIP",
},config=config)
print(resp1["messages"][-1].content)

print("-----------------")
resp2 = agent.invoke({"messages":[{"role":"user","content":"我把我的信息user_id改成 user_002，用户等级改成 normal"}]},config=config)
print(resp2["messages"][-1].content)

print("-----------------")

resp3 = agent.invoke({"messages":[{"role":"user","content":"你知道我的信息吗？"}]},config=config)
print(resp3["messages"][-1].content)


print("-----------------")
state = agent.get_state(config=config)
print(type(state))
print(state)


