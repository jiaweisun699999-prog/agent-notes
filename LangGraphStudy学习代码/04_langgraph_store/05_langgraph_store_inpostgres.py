
"""
基于内存的Store
"""
import operator
from dataclasses import dataclass
from typing import TypedDict, Annotated

from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore
from langgraph.store.postgres import PostgresStore
from pygments.lexers import data


@dataclass
class Context:
    user_id:str

# 定义状态类型
class ChatState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

# 初始化 checkpointer、store
checkpointer = InMemorySaver()
store = InMemoryStore()


# 定义节点
def save_preference(state:ChatState,runtime:Runtime):
    print("runtime:",runtime)

    # 创建namespace
    user_id = runtime.context.user_id
    ns = (user_id,"memories")

    # 获取用户对话信息，找出偏好
    msg = state["messages"][-1].content
    if "偏好" in msg:
        preference = msg.split("偏好")[-1].strip()

        # 保存偏好到store
        runtime.store.put(
            ns,
            "user_preference",
            {"preference":preference}
        )

        return {"messages":[AIMessage(content=f"已经记住你的偏好：{preference}")]}

    return {"messages": [AIMessage(content=f"没有发现偏好信息")]}


def greet_with_preference(state:ChatState,runtime:Runtime):
    "从Store中获取偏好信息，给用户回复"
    user_id = runtime.context.user_id
    ns = (user_id,"memories")

    # 从store中获取偏好
    if runtime.store:
        preference_list = runtime.store.search(ns)
    else:
        preference_list = []

    if preference_list:
        # 从长期记忆中获取偏好信息
        prefs = [item.value.get("preference","") for item in preference_list ]
        preference = "\n".join(prefs)

        return {"messages":[AIMessage(content=f"你好，你的偏好是：{preference}，我会根据你的偏好推荐相关的内容")]}
    else:

        return {"messages": [AIMessage(content=f"你好，没有记录偏好信息")]}



#构建图
builder = StateGraph(
    state_schema = ChatState,
    context_schema=Context
)

builder.add_node("save_preference",save_preference)
builder.add_node("greet_with_preference",greet_with_preference)

builder.add_edge(START,"save_preference")
builder.add_edge("save_preference","greet_with_preference")
builder.add_edge("greet_with_preference",END)


DB_URI="postgresql://postgres:postgres123@192.168.179.5:5432/langgraph_db"

with (
    PostgresSaver.from_conn_string(DB_URI) as checkpointer,
    PostgresStore.from_conn_string(DB_URI) as store
):

    checkpointer.setup()
    store.setup()

    graph = builder.compile(checkpointer=checkpointer,store=store)



    # 使用graph
    config1 = {"configurable":{"thread_id":"thread_001"}}

    result1 = graph.invoke(
        {"messages": [HumanMessage(content="我的偏好喜欢吃辣的")]},
        config1,
        context=Context(user_id="user_001")
    )
    for msg in result1["messages"]:
        msg.pretty_print()

    print("****"*100)

    config2 = {"configurable":{"thread_id":"thread_002"}}

    result2 = graph.invoke(
        {"messages": [HumanMessage(content="你好")]},
        config2,
        context=Context(user_id="user_001")
    )
    for msg in result2["messages"]:
        msg.pretty_print()

    print("****"*100)

    config3 = {"configurable":{"thread_id":"thread_003"}}

    result3 = graph.invoke(
        {"messages": [HumanMessage(content="你好")]},
        config3,
        context=Context(user_id="user_002")
    )
    for msg in result3["messages"]:
        msg.pretty_print()

