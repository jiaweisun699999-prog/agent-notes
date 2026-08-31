from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command


class State(TypedDict):
    name:str


# def ask_name(state:State)->State:
#     name = interrupt("请问你的姓名是？")
#     print("name:",name)
#     return {"name":name}

def ask_name(state:State)->State:
    info = interrupt({"question":"请问你的姓名是？","info":"这是info"})
    print("info:",info)
    return {"name":info}


builder = StateGraph(State)
builder.add_node("ask_name",ask_name)

builder.add_edge(START,"ask_name")
builder.add_edge("ask_name",END)

graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable":{"thread_id":"thread001"}}

stream = graph.stream_events({"name":""},config=config,version="v3")

print("是否中断:",stream.interrupted)
print("中断信息：",stream.interrupts)
print("中断值：",stream.interrupts[0].value)

#恢复中断
resumed = graph.stream_events(Command(resume={"my_name":"张三","age":18}),config=config,version="v3")
print("最终state:",resumed.output)
