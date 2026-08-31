from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    """图状态：文章标题与正文"""
    title: str # 文章标题
    article: str # 文章正文


title_count = 0
article_count = 0


def plan_title(state: State) -> dict:
    """节点一：拟定标题"""
    global title_count
    title_count += 1
    return {"title": f"AI 时代的编程学习（第 {title_count} 版标题）"}


def write_article(state: State) -> dict:
    """节点二：撰写正文"""
    global article_count
    article_count += 1
    return {"article": f"基于[{state['title']}]撰写的正文（第 {article_count} 次撰写）"}


builder = StateGraph(State)
builder.add_node("plan_title", plan_title)
builder.add_node("write_article", write_article)

builder.add_edge(START, "plan_title")
builder.add_edge("plan_title", "write_article")
builder.add_edge("write_article", END)

graph = builder.compile(checkpointer=InMemorySaver())

config = {"configurable": {"thread_id": "thread001"}}


if __name__ == "__main__":
    # 首次执行
    result = graph.invoke({"title": "", "article": ""}, config)
    print(f"首次执行：{result}")
    print(f"计数器：title_count={title_count}, article_count={article_count}")

    print("=" * 50)

    # 检查点历史（倒序）
    history = list(graph.get_state_history(config))
    print("========== 检查点历史（倒序） ==========")
    for s in history:
        print(f"  next={s.next}")

    # Replay：从 write_article 之前重放
    print("\n========== Replay：从 write_article 之前重放 ==========")
    before_article = next(s for s in history if s.next == ("write_article",))
    replay_result = graph.invoke(None, before_article.config)
    print(f"重放结果：{replay_result}")

    print("========== 再次检查点历史（倒序） ==========")
    history = list(graph.get_state_history(config))
    for s in history:
        print(f"  next={s.next}，article={s.values.get('article')!r}")
