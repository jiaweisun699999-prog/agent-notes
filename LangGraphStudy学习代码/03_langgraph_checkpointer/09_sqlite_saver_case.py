
"""
LangGraph中Checkpointer使用
"""
import operator
import sqlite3
from typing import TypedDict, Annotated

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph


#1. 定义状态
class State(TypedDict):
    foo: str
    bar: Annotated[list[str],operator.add]


#2. 定义节点
def node_a(state: State):
    """节点A:写入 foo=a， bar中追加a"""
    return {"foo": "a", "bar": ["a"]}

def node_b(state: State):
    """节点B:写入 foo=b， bar中追加b"""
    return {"foo": "b", "bar": ["b"]}

#3.构建图
builder = StateGraph(State)
builder.add_node("node_a",node_a)
builder.add_node("node_b",node_b)

builder.add_edge(START,"node_a")
builder.add_edge("node_a","node_b")
builder.add_edge("node_b",END)

#4. 编译图
# 创建SQLiteSaver
conn = sqlite3.connect("checkpoints.db",check_same_thread=False)
checkpointer = SqliteSaver(conn)
graph = builder.compile(checkpointer=checkpointer)


#5. 运行图
config = {"configurable": {"thread_id": "thread_1"}}

result = graph.invoke({"foo": "", "bar": []},config=config)
print("result:",result)







