from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    """图状态：文章标题与正文"""
    title: str # 文章标题
    article: str # 文章正文


def plan_title(state: State) -> dict:
    """节点一：拟定标题（保留传入值）"""
    return {"title": state["title"]}


def write_article(state: State) -> dict:
    """节点二：基于标题撰写正文"""
    return {"article": f"《{state['title']}》正文：这是一篇关于该主题的深度解读……"}


builder = StateGraph(State)
builder.add_node("plan_title", plan_title)
builder.add_node("write_article", write_article)

builder.add_edge(START, "plan_title")
builder.add_edge("plan_title", "write_article")
builder.add_edge("write_article", END)

graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "article-2"}}


if __name__ == "__main__":
    # 首次执行，标题 A
    result = graph.invoke({"title": "LangGraph 入门", "article": ""}, config)
    print(f"首次执行（标题 A）：{result['article']}")

    # 定位 write_article 之前的检查点
    history = list(graph.get_state_history(config))
    before_article = next(s for s in history if s.next == ("write_article",))

    # Fork：修改标题，创建新分支
    print("========== Fork：换标题探索不同正文 ==========")
    fork_config = graph.update_state(
        before_article.config,
        values={"title": "LangGraph 深度实战"},
    )

    fork_result = graph.invoke(None, fork_config)
    print(f"分叉结果（标题 B）：{fork_result['article']}")

    # fork 后新分支成为线程最新状态；原分支仍在历史中
    print(f"fork 后 get_state 返回最新状态：{graph.get_state(config).values['title']}")

    print("完整历史（含原始分支与 fork 分支）：")
    for s in graph.get_state_history(config):
        print(f"  next={s.next}  title={s.values.get('title')}")