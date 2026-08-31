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


#5. 运行图
config = {"configurable": {"thread_id": "thread_1"}}

result = graph.invoke({"foo": "", "bar": []},config=config)
# print("result:",result)


# 获取最新的状态
latest = graph.get_state(config)
# print("latest:",latest)

# 基于最后的状态更新状态
graph.update_state(config,values={"foo":"aaa","bar":["bbb"]})

latest = graph.get_state(config)
# print("更新后的latest:",latest)


#获取所有graph 历史状态
history = list(graph.get_state_history(config))
for snapshot in history:
    # print("snapshot:",snapshot)
    print(f"step={snapshot.metadata['step']},next={snapshot.next},values={snapshot.values}")



# 找到after_a 对应的状态
after_a = None
for snapshot in history:
    if snapshot.next ==('node_b',):
        after_a = snapshot
        break

# 基于after_a 更新状态
update_config = graph.update_state(after_a.config,values={"foo":"aaaa","bar":["bbbb"]})

flag = graph.get_state(update_config)
print("flag:",flag)




