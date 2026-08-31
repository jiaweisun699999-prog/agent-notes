from typing import Annotated, TypedDict
import operator

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command


class State(TypedDict):
    """图状态：收集结果列表（用 operator.add 累加）"""
    results: Annotated[list[str], operator.add]


def ask_city(state: State) -> dict:
    """节点 A：询问城市"""
    city = interrupt("问题A：您所在的城市是？")
    return {"results": [f"城市={city}"]}


def ask_age(state: State) -> dict:
    """节点 B：询问年龄"""
    age = interrupt("问题B：您的年龄是？")
    return {"results": [f"年龄={age}"]}


# ============================================================
# 构建图（两个节点从 START 并行出发，带 Checkpointer）
# ============================================================
builder = StateGraph(State)
builder.add_node("ask_city", ask_city)
builder.add_node("ask_age", ask_age)

builder.add_edge(START, "ask_city")
builder.add_edge(START, "ask_age")
builder.add_edge("ask_city", END)
builder.add_edge("ask_age", END)

graph = builder.compile(checkpointer=InMemorySaver())


def get_user_input(interrupt_info) -> str:
    """根据中断信息向用户提问并读取输入（通用：字符串/字典都行）"""
    if isinstance(interrupt_info, str):
        return input(f"\n[系统]: {interrupt_info}\n[用户]: ").strip()

    # 字典场景：遍历所有键值对展示，原样返回输入
    show_info = "\n".join(f"{k}:{v}" for k, v in interrupt_info.items())
    return input(f"\n[系统]: {show_info}\n[用户]: ").strip()


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "thread001"}}

    stream_input: dict | Command = {"results": []}

    while True:
        # 1. 调用图，事件流驱动
        stream = graph.stream_events(stream_input, config=config, version="v3")

        # 2. 流式显示 LLM 回复
        print("【LLM】", end="", flush=True)
        for message in stream.messages:
            for token in message.text:
                if token.strip():
                    print(token, end="", flush=True)
        print()

        # 3. 图没有中断，完整跑完
        if not stream.interrupted:
            final_state = stream.output
            print(f"\n===== 最终 results：{final_state} =====")
            break

        # 4. 多个并行中断：逐个读取中断信息向用户提问，配对成 resume map
        print(f"---- 本轮有 {len(stream.interrupts)} 个待处理中断 ----")
        resume_map = {}
        for i in stream.interrupts:
            user_response = get_user_input(i.value)
            # 用 i.id 作为键构建 resume map
            resume_map[i.id] = user_response

        # 5. 用 resume map 一次性恢复所有中断
        stream_input = Command(resume=resume_map)

