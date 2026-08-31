"""
LangGraph中Checkpointer使用
"""
import operator
from typing import TypedDict, Annotated

from langgraph.checkpoint.memory import InMemorySaver
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
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)


# 输出Graph 图/工作流为 PNG
png_data = graph.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(png_data)
print("图片已保存到 graph.png")


#5. 运行图
config = {"configurable": {"thread_id": "thread_1"}}

result = graph.invoke({"foo": "", "bar": []},config=config)
print("result:",result)

#获取checkpointer 最新的状态
state = graph.get_state(config)
print(type(state))
print("state:",state)







