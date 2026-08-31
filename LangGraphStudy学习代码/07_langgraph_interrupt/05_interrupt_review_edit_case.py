from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command

from init_llm import deepseek_llm_flash


class State(TypedDict):
    """图状态：用户问题、最终回复文案、最近一次审核输入"""
    question: str
    reply: str
    review_input: str


def generate_reply(state: State) -> dict:
    """节点一：LLM 生成回复草稿"""
    response = deepseek_llm_flash.invoke(
        [{"role": "user", "content": f"你是客服，用户问：{state['question']}，写一句礼貌的回复，不要让用户选择。"}]
    )
    return {"reply": response.content[0]["text"]}


def review_reply(state: State) -> dict:
    """节点二：interrupt 一次收集审核输入，不判断合法性（判断交给条件边路由）"""
    edited = interrupt({
        "question": "请审核并修改以下回复：\n- 输入[通过] = 原样采用\n- 输入修改后的完整文案 = 采用新文案\n- 空输入 = 重新询问",
        "待审核草稿": state["reply"],
    })
    return {"review_input": edited.strip()}


def apply_original(state: State) -> dict:
    """节点：审核员输入[通过]，原样采用草稿"""
    return {"review_input": ""}


def apply_edited(state: State) -> dict:
    """节点：审核员给了新文案，采用新文案（从 review_input 读取）"""
    return {"reply": state["review_input"], "review_input": ""}


def route_review(state: State) -> str:
    """路由函数：审核输入分流 —— 通过→原稿 / 非空→新文案 / 空→回跳重新审核"""
    edited = state.get("review_input", "")
    if edited == "通过":
        return "apply_original"
    if edited:
        return "apply_edited"
    return "review_reply"   # 空输入：回跳 review_reply 重新询问


# ============================================================
# 构建图（带 Checkpointer）
# ============================================================
builder = StateGraph(State)
builder.add_node("generate_reply", generate_reply)
builder.add_node("review_reply", review_reply)
builder.add_node("apply_original", apply_original)
builder.add_node("apply_edited", apply_edited)

builder.add_edge(START, "generate_reply")
builder.add_edge("generate_reply", "review_reply")
builder.add_conditional_edges("review_reply", route_review, {
    "review_reply": "review_reply",
    "apply_original": "apply_original",
    "apply_edited": "apply_edited",
})
builder.add_edge("apply_original", END)
builder.add_edge("apply_edited", END)

graph = builder.compile(checkpointer=InMemorySaver())


def get_user_input(interrupt_info) -> str:
    """根据中断信息向用户提问并读取输入（通用：字符串/字典都行）"""
    if isinstance(interrupt_info, str):
        return input(f"\n[系统]: {interrupt_info}\n[用户]: ").strip()

    # 字典场景：遍历所有键值对展示，原样返回输入
    show_info = "\n".join(f"{k}:{v}" for k, v in interrupt_info.items())
    return input(f"\n[系统]: {show_info}\n[用户]: ").strip()


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "review-hitl-1"}}

    stream_input: dict | Command = {"question": "我的订单三天没发货了", "reply": "", "review_input": ""}

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
            print(f"\n===== 最终回复：{final_state} =====")
            break

        # 4. 图中断，读取中断信息向用户提问
        try:
            user_response = get_user_input(stream.interrupts[0].value)
        except (EOFError, KeyboardInterrupt):
            print("\n[系统] 用户中断退出，会话结束")
            break

        # 5. 用户输入作为 resume 继续，进入下一轮
        stream_input = Command(resume=user_response)

