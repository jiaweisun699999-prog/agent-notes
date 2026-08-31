from typing import TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    """图状态：卖点精炼前后的话题，以及最终生成的文案"""
    topic: str  # 原始话题
    copy: str  # 最终生成的文案


def refine_topic(state: State) -> dict:
    """节点一：精炼卖点，在原始话题后追加限定词"""
    return {"topic": state["topic"] + "，主打高性价比"}


def generate_copy(state: State) -> dict:
    """节点二：基于精炼后的卖点生成文案"""
    return {"copy": f"节日大促，{state['topic']}，错过再等一年！"}


# ============================================================
# 构建图
# ============================================================
builder = StateGraph(State)
builder.add_node("refine_topic", refine_topic)
builder.add_node("generate_copy", generate_copy)

builder.add_edge(START, "refine_topic")
builder.add_edge("refine_topic", "generate_copy")
builder.add_edge("generate_copy", END)

graph = builder.compile()


if __name__ == "__main__":
    # updates：只输出增量更新
    print("========== updates 模式（增量更新） ==========")
    for chunk in graph.stream(
        {"topic": "无线蓝牙耳机", "copy": ""},
        stream_mode="updates",
        version="v2",
    ):
        # print("chunk:",chunk)
        if chunk["type"] == "updates":
            for node_name, update in chunk["data"].items():
                print(f"节点 {node_name} 更新了: {update}")

    print()

    # values：输出完整状态快照
    print("========== values 模式（全量状态快照） ==========")
    for chunk in graph.stream(
        {"topic": "无线蓝牙耳机", "copy": ""},
        stream_mode="values",
        version="v2",
    ):
        # print("chunk:",chunk)
        if chunk["type"] == "values":
            data = chunk["data"]
            print(f"当前状态: {data}")
