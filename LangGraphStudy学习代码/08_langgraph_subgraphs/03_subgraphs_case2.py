from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from init_llm import deepseek_llm_flash


# ============================================================
# 子图：营销文案（description 共享，note 私有）
# ============================================================
class SubgraphState(TypedDict):
    """子图状态：description 与父图共享，note 是子图私有字段"""
    description: str # 描述
    note: str # 促销文案


def generate_note(state: SubgraphState) -> dict:
    """子图节点一：写入私有字段 note"""
    resp = deepseek_llm_flash.invoke("给商品生成20字以内的营销文案，商品描述：" + state["description"])
    return {"note": resp.content}


def update_description(state: SubgraphState) -> dict:
    """子图节点二：读取私有字段 note，更新共享字段 description"""
    # note 是子图私有字段，只在子图内部可读
    return {"description": "产品描述：" + state["description"] + "，促销文案：" + state["note"]}


subgraph_builder = StateGraph(SubgraphState)
subgraph_builder.add_node("generate_note", generate_note)
subgraph_builder.add_node("update_description", update_description)

subgraph_builder.add_edge(START, "generate_note")
subgraph_builder.add_edge("generate_note", "update_description")
subgraph_builder.add_edge("update_description", END)

subgraph = subgraph_builder.compile()


# ============================================================
# 主图：商品描述 -> 营销子图（主图 schema 只有 description）
# ============================================================
class ParentState(TypedDict):
    """主图状态：只有 description，没有 note"""
    description: str


def generate_desc(state: ParentState) -> dict:
    """主图节点：生成商品基础描述"""
    return {"description": state["description"] + "，超长续航!"}


builder = StateGraph(ParentState)
builder.add_node("generate_desc", generate_desc)
builder.add_node("marketing", subgraph)  # 子图作为节点，description 共享，note 私有

builder.add_edge(START, "generate_desc")
builder.add_edge("generate_desc", "marketing")
builder.add_edge("marketing", END)

graph = builder.compile()


if __name__ == "__main__":
    result = graph.invoke({"description": "降噪蓝牙耳机"})
    print(result)

