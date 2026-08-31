from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command


class State(TypedDict):
    name:str

def ask_name(state:State)->State:
    name = interrupt("你的姓名是什么？")
    return {"name":name}


builder = StateGraph(State)
builder.add_node("ask_name",ask_name)

builder.add_edge(START,"ask_name")
builder.add_edge("ask_name",END)

graph = builder.compile(checkpointer=InMemorySaver())


def get_user_input(interrupt_info)->str:
    "根据中断信息向用户展示，并等待用户输入内容"
    if isinstance(interrupt_info,str):
        return input(f"\n[系统]：{interrupt_info} \n[用户]:").strip()


    #dict 类型
    show_info = "\n".join([f"{k}:{v}" for k,v in interrupt_info.items()])
    return input(f"\n[系统]：{show_info} \n[用户]:").strip()



if __name__ == '__main__':

    config = {"configurable":{"thread_id":"thread001"}}

    stream_input :dict | Command = {"name":""}

    while True:
        # 1.调用图
        stream = graph.stream_events(stream_input,config=config,version="v3")

        # 2.流式显示 LLM 回复
        print("【LLM】",end="",flush=True)
        for message in stream.messages:
            for token in message.text:
                print(token,end="",flush=True)
        print()

        # 3.图没有中断，直接输出结果
        if not stream.interrupted:
            final_state = stream.output
            print(f"\n=========最终state:{final_state}=============")
            break

        # 4.图有中断，获取中断信息展示，获取用户输入
        interrupt_info = stream.interrupts[0].value
        user_response = get_user_input(interrupt_info)

        # 5.把用户响应作为下一次 stream_events 的输入（resume）
        stream_input = Command(resume=user_response)

