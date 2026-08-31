from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from init_llm import deepseek_llm_flash


class State(TypedDict):
    """图状态：商品、回答、优惠信息"""
    product: str # 商品名称
    answer: str # 商品咨询回答
    discount: str # 优惠信息


def generate_answer(state: State) -> dict:
    """节点一：生成商品咨询回答"""
    response = deepseek_llm_flash.invoke(
        [{"role": "user", "content": f"用一句话介绍商品【{state['product']}】的优点"}]
    )

    return {"answer": response.content}


def add_discount(state: State) -> dict:
    """节点二：补充优惠信息（纯字符串，不经过 LLM）"""
    return {"discount": f"{state['product']} 限时 8 折，领券再减 30 元"}


# ============================================================
# 构建图
# ============================================================
builder = StateGraph(State)
builder.add_node("generate_answer", generate_answer)
builder.add_node("add_discount", add_discount)

builder.add_edge(START, "generate_answer")
builder.add_edge("generate_answer", "add_discount")
builder.add_edge("add_discount", END)

graph = builder.compile()


if __name__ == "__main__":
    inputs = {"product": "降噪蓝牙耳机", "answer": "", "discount": ""}

    # ============================================================
    # stream.messages：迭代每一步LLM的 message
    # ============================================================
    # 通过 stream_events(version="v3") 拿到运行流对象
    # stream = graph.stream_events(inputs, version="v3")
    #
    # # 遍历 stream.messages：每个 message 对应一次 LLM 调用
    # for message in stream.messages:
    #     print(f"\n[节点 {message.node}] ", end="")
    #     # message.text 可逐 token 迭代，str(message.text) 得到完整文本
    #     for token in message.text:
    #         print(token, end="", flush=True)
    #     # message.output.usage_metadata 携带本次调用的 token 用量
    #     usage = message.output.usage_metadata
    #     print("\nmessage.output:", message.output)
    #     print(
    #         f"\n[token 用量] 输入 {usage['input_tokens']} + 输出 {usage['output_tokens']} = 总计 {usage['total_tokens']}")

    # ============================================================
    # stream.values：迭代每一步的状态快照
    # ============================================================
    # print("========== stream.values 投影（状态快照） ==========")
    # stream = graph.stream_events(inputs, version="v3")
    # for snapshot in stream.values:
    #     print("snapshot:", snapshot)

    # ============================================================
    # stream.output：最终状态（一次性拿到）
    # ============================================================
    print("\n========== stream.output 投影（最终状态） ==========")
    stream = graph.stream_events(inputs, version="v3")
    final_state = stream.output
    print("final_state:", final_state)
