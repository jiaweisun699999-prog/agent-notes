from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from init_llm import deepseek_llm_flash


class State(TypedDict):
    """图状态：商品与生成的文案"""
    product: str
    copy: str



def write_copy(state: State) -> dict:
    """节点：生成商品文案"""
    response = deepseek_llm_flash.invoke(
        [{"role": "user", "content": f"为商品[{state['product']}]写一句 20 字以内的卖点文案，直接输出正文"}]
    )
    return {"copy": response.content}


# ============================================================
# 构建图
# ============================================================
builder = StateGraph(State)
builder.add_node("write_copy", write_copy)

builder.add_edge(START, "write_copy")
builder.add_edge("write_copy", END)

graph = builder.compile()


if __name__ == "__main__":
    print("========== interleave 多投影交织消费 ==========")

    stream = graph.stream_events({"product": "无线蓝牙耳机", "copy": ""}, version="v3")

    # interleave 把 values 和 messages 两个投影按到达顺序交织
    for name, item in stream.interleave("values", "messages"):
        print(f"name: {name}, item: {item}")
        if name == "values":
            print(f"[状态快照] copy={item['copy']}")
        elif name == "messages":
            print("[LLM 回复] ", str(item.text))
