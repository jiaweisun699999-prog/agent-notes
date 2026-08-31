import operator
from typing import TypedDict, Annotated

from langchain_core.messages import content, AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph, MessagesState
from langgraph.types import interrupt, Command


class State(MessagesState):
    info: Annotated[list[str],operator.add]
    confirm_answer:str


def ask_name(state:State)->State:
    name = interrupt("请输入您的姓名？")
    return {"info":[f"姓名={name}"],"messages":[AIMessage(content=f"好的，您输入的姓名是{name}")]}


def ask_age(state:State)->State:
    age = interrupt("请输入您的年龄？")
    return {"info":[f"年龄={age}"],"messages":[AIMessage(content=f"收到，您输入的年龄是{age}岁")]}

def confirm(state:State)->State:
    summary = "|".join(state["info"])

    confirm = interrupt({
        "question":"确认您的信息吗？只能回复是或否",
        "确认的信息":summary
    })
    return {"confirm_answer":confirm}

def route_confirm(state:State)->str:
    confirm_answer = state.get("confirm_answer","")
    if confirm_answer=="是":
        return "complete"
    if confirm_answer=="否":
        return "cancel"
    return "confirm"


def complete(state:State)->State:
    summary = "|".join(state["info"])
    return {"messages":[AIMessage(content=f"登记完成：{summary},欢迎加入！")]}


def cancel(state:State)->State:
    return {"messages":[AIMessage(content=f"已经取消登记")]}


builder = StateGraph(State)
builder.add_node("ask_name",ask_name)
builder.add_node("ask_age",ask_age)
builder.add_node("confirm",confirm)
builder.add_node("cancel",cancel)
builder.add_node("complete",complete)


builder.add_edge(START,"ask_name")
builder.add_edge("ask_name","ask_age")
builder.add_edge("ask_age","confirm")

builder.add_conditional_edges("confirm",route_confirm,{
    "complete":"complete",
    "cancel":"cancel",
    "confirm":"confirm",
})

builder.add_edge("cancel",END)
builder.add_edge("complete",END)


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

    stream_input :dict | Command = {
        "messages":[HumanMessage(content="请登记我的信息")],
        "info":[],
        "confirm_answer":""
    }


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

