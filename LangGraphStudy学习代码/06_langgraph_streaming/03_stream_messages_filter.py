"""
用户输入商品 -> 生成商品文案 -> 内部校验生成的文案是否合规
输出内容以打字机方式输出，这里使用 stream_mode="messages" 模式
"""
from typing import TypedDict

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from init_llm import deepseek_llm_flash


class State(TypedDict):
    product:str #商品名称
    copy:str #生成的商品文案
    notes:str #检查备注

copy_model = deepseek_llm_flash.with_config({"tags":["copy"]})

internal_model = deepseek_llm_flash.with_config({"tags":["nostream"]})

def write_copy(state:State):
    response = copy_model.invoke([AIMessage(content=f"给商品{state['product']}写一句卖点文案。要求：字数不能超过20字，不需要任何解释。请直接返回卖点文案。")])
    print("\nresponse:",response)

    response2 = internal_model.invoke(
        [AIMessage(content=f"检查商品{state['product']}的卖点文案{state['copy']}是否包含风险点，一句话总结。")])

    return {"copy":response.content}


def write_internal_notes(state:State):
    response = internal_model.invoke([AIMessage(content=f"检查商品{state['product']}的卖点文案{state['copy']}是否包含风险点，一句话总结。")])

    return {"notes":response.content}

builder = StateGraph(State)
builder.add_node("write_copy",write_copy)
builder.add_node("write_internal_notes",write_internal_notes)

builder.add_edge(START, "write_copy")
builder.add_edge("write_copy", "write_internal_notes")
builder.add_edge("write_internal_notes", END)

graph = builder.compile(checkpointer=InMemorySaver())


if __name__ == '__main__':
    # for chunk in graph.stream(
    #     {"product":"降噪蓝牙耳机","copy":"","notes":""},
    #     stream_mode="messages",
    #     version="v2"
    # ):
    #     # print("chunk:",chunk)
    #     if chunk["type"] == "messages":
    #         msg, metadata = chunk["data"]
    #         if msg.content and metadata.get("langgraph_node") == "write_copy":
    #             print(msg.content, end="", flush=True)


    config = {"configurable":{"thread_id":"001"}}

    for chunk in graph.stream(
        {"product":"降噪蓝牙耳机","copy":"","notes":""},
        stream_mode="messages",
        version="v2",
        config=config
    ):
        print("chunk:",chunk)
        # if chunk["type"] == "messages":
        #     msg, metadata = chunk["data"]
        #     if msg.content and metadata.get("tags") == ["copy"]:
        #         print(msg.content, end="", flush=True)

    print(graph.get_state(config))