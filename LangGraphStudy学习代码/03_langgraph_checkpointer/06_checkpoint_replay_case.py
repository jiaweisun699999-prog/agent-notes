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
    print("====== node_a 执行了=====")
    return {"foo": "a", "bar": ["a"]}

def node_b(state: State):
    """节点B:写入 foo=b， bar中追加b"""
    print("====== node_b 执行了=====")
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


# 获取历史所有的checkpointer
state_history = list(graph.get_state_history(config))
for i,snapshot in enumerate(state_history):
    print(f"{i}:",snapshot)


print("*"*100)
replay_config = state_history[1].config

# 重放：接着指定的checkpint 继续运行
replay_result = graph.invoke(None,replay_config)
print("replay_result:",replay_result)





