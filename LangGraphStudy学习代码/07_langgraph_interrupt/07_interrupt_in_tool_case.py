from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt, Command

from init_llm import deepseek_llm_flash  # noqa: E402


# ============================================================
# 工具：发送邮件（内含 interrupt）
# ============================================================
@tool
def send_email(to: str, subject: str, body: str) -> str:
    """发送邮件给收件人。当用户要发送邮件时使用。"""
    # 暂停，把邮件详情抛给审批人；恢复后 response 是审批人的决策
    response = interrupt({
        "action": "send_email",
        "发送收件人": to,
        "邮件主题": subject,
        "邮件内容": body,
        "question": "请审批发送这封邮件：[approve] 发送 / [其它任意内容] 取消",
    })


    if response == "approve":
        # 审批通过，模拟发送邮件
        print(f"[send_email] 已发送 → 收件人={to} 主题={subject} 正文={body}")
        return f"邮件已发送给 {to}（主题：{subject}）"

    # 审批拒绝
    return "邮件已取消发送"


# ============================================================
# 绑定工具的大模型
# ============================================================
tools = [send_email]
model = deepseek_llm_flash.bind_tools(tools)


# ============================================================
# 定义节点
# ============================================================
def agent(state: MessagesState) -> dict:
    """Agent 节点：LLM 决定调用工具还是直接回答"""
    return {"messages": [model.invoke(state["messages"])]}

def should_continue(state: MessagesState):
    """路由函数：最后一条消息含 tool_calls 则进 tools，否则结束"""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END


# ============================================================
# 构建图（带 Checkpointer）
# ============================================================
builder = StateGraph(MessagesState)
builder.add_node("agent", agent)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue, ["tools", END])
builder.add_edge("tools", "agent")

graph = builder.compile(checkpointer=InMemorySaver())


def get_user_input(interrupt_info):
    """根据中断信息向用户提问并读取输入（通用：字符串/字典都行）"""
    if isinstance(interrupt_info, str):
        return input(f"\n[系统]: {interrupt_info}\n[用户]: ").strip()

    # 字典场景：遍历所有键值对展示，原样返回输入
    show_info = "\n".join(f"{k}:{v}" for k, v in interrupt_info.items())
    return input(f"\n[系统]: {show_info}\n[用户]: ").strip()


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "thread001"}}

    stream_input: dict | Command = {
        "messages": [{"role": "user", "content": "请给 alice@example.com 发送一封邮件，主题是'项目会议'，内容是'明天下午3点开会'"}]
    }

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
            print(f"\n===== 最终回复：{final_state['messages'][-1].content} =====")
            break

        # 4. 图中断，读取中断信息向用户提问
        print(f"---- 本轮有 {len(stream.interrupts)} 个待处理中断 ----")
        resume_map = {}
        for i in stream.interrupts:
            user_response = get_user_input(i.value)
            # 用 i.id 作为键构建 resume map
            resume_map[i.id] = user_response

        # 5. 用户输入作为 resume 继续，进入下一轮
        stream_input = Command(resume=user_response)
