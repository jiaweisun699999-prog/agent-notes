"""
案例：流式处理与 HITL 结合
"""

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from init_llm import deepseek_llm


# ===== 1. 定义工具 =====

@tool
def send_broadcast(message: str) -> str:
    """发送全员广播通知"""
    return f"已发送：{message} 广播"

@tool
def send_email(content: str) -> str:
    """发送邮件"""
    return f"邮件已发送，内容：{content}"

@tool
def get_weather(city: str) -> str:
    """查询天气"""
    return f"{city} 今天晴，22~28°C"


# ===== 2. 创建智能体 =====
agent = create_agent(
    model=deepseek_llm,
    tools=[get_weather, send_broadcast, send_email],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_broadcast": {"allowed_decisions": ["approve", "reject"]},
                "send_email": {"allowed_decisions": ["approve", "reject"]},
                "get_weather": False,
            },
            description_prefix="人工介入，请确认以下操作：",
        ),
    ],
    checkpointer=InMemorySaver(),
    system_prompt="你是一个助手，可以查询天气、发送全员广播通知和发送邮件。",
)


# ===== 3. 流式运行 =====
config = {"configurable": {"thread_id": "session_01"}}

#3.1 外层循环：对话轮次
while True:
    try:
        user_input = input("\n[你]: ").strip()

        if user_input.lower() in ("quit", "exit", "退出", "q"):
            print("已退出，再见！")
            break

        if not user_input:
            continue

        # 本轮对话的输入：首次是普通消息，中断后会被替换为 Command(resume=...)
        next_input = {"messages": [{"role": "user", "content": user_input}]}

        #3.2 内层循环：同一轮对话中可能发生多轮中断/恢复
        while True:
            print("[Agent 回复]: ", end="", flush=True)

            interrupted = False  # 本轮 stream 是否因中断而跳出

            for chunk in agent.stream(
                next_input,
                config=config,
                stream_mode=["updates", "messages"],
                version="v2",
            ):
                # print("chunk:", chunk)
                # 3.3 处理非中断消息流
                if chunk["type"] == "messages":
                    token_data = chunk["data"]
                    # token_data 是 (token_chunk, metadata) 元组
                    token_chunk = token_data[0]
                    if token_chunk.content:
                        # end="" 避免打印时自动换行，flush=True 及时刷新输出
                        print(token_chunk.content, end="", flush=True)
                # 3.4 处理中断消息流
                elif chunk["type"] == "updates":
                    update_data = chunk["data"]

                    # 检查是否有中断信号触发
                    if "__interrupt__" in update_data:
                        interrupted = True

                        print("=" * 60)
                        print("Agent中断已触发！Agent 等待人工确认…")
                        print("=" * 60)

                        # 提取中断详情
                        interrupt_raw = update_data["__interrupt__"]
                        action_requests = interrupt_raw[0].value["action_requests"]
                        review_configs = interrupt_raw[0].value["review_configs"]

                        print(f"\n  本次中断包含 {len(action_requests)} 个待审批操作：")
                        for i, req in enumerate(action_requests):
                            cfg = review_configs[i]
                            print(f"    [{i}] {req['name']}  |  参数: {req['args']}  |  允许: {cfg['allowed_decisions']}")

                        # 按顺序逐个收集决策（多工具同时中断时，顺序必须一致）
                        decisions = []
                        for i, req in enumerate(action_requests):
                            cfg = review_configs[i]
                            allowed = cfg["allowed_decisions"]

                            print(f"\n  ── 操作 [{i}] ：工具：{req['name']} ──")

                            while True:
                                decision = input(f"      >>> 请输入决策 ({'/'.join(allowed)}): ").strip().lower()
                                if decision in allowed:
                                    break
                                print(f"      只允许: {allowed}")

                            if decision == "approve":
                                decisions.append({"type": "approve"})
                                print(f"      已批准：按原参数执行")
                            elif decision == "reject":
                                reason = input(f"      拒绝原因: ").strip() or "操作被人工拒绝"
                                decisions.append({"type": "reject", "message": reason})
                                print(f"      已拒绝：{reason}")

                        print(f"\n  提交决策: {decisions}")

                        # 构造恢复命令，替换下一轮 stream 的输入
                        next_input = Command(resume={"decisions": decisions})

                        # 跳出 for 循环，回到内层 while 顶部，用 Command(resume=...) 重新 stream
                        break

            # ── 内层 while 的分岔口 ──
            if not interrupted:
                # for 循环正常结束 → 本轮对话完成，跳出内层 while，回到外层等下一句
                print()  # 末尾换行
                break
            else:
                # for 循环被 break（有中断）→ 内层 while 回到顶部，用 next_input 恢复执行
                # 打印一个空行作为中断→恢复执行分割标志
                print("\nAgent正在恢复执行…\n")

    except Exception as e:
        print(f"\n调用过程中出现错误：{e}")