from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END

from init_llm import deepseek_llm_flash


# ============================================================
# 子图：营销文案（description 共享，note 私有）
# ============================================================
class SubgraphState(TypedDict):
    result : str # 子图结果
    visit_count: int # 访问次数


def sub_node(state: SubgraphState) -> dict:
    count = state.get("visit_count", 0) + 1
    return {"visit_count":count,"result":f"第{count}次访问"}


subgraph_builder = StateGraph(SubgraphState)
subgraph_builder.add_node("sub_node", sub_node)

subgraph_builder.add_edge(START, "sub_node")
subgraph_builder.add_edge("sub_node", END)

# subgraph = subgraph_builder.compile(checkpointer=None)
subgraph = subgraph_builder.compile(checkpointer=False)

# ============================================================
# 主图
# ============================================================
class ParentState(TypedDict):
    result: str

builder = StateGraph(ParentState)

builder.add_node("subgraph", subgraph)  # 子图作为节点，description 共享，note 私有

builder.add_edge(START, "subgraph")
builder.add_edge("subgraph", END)

graph = builder.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "thread001"}}

    for i in range(3):
        result = graph.invoke({"result": ""}, config=config)

        print(result)

