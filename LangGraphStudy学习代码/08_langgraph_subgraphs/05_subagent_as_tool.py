from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command, interrupt

from init_llm import deepseek_llm_flash
from langchain.agents import create_agent
from langchain_core.tools import tool

# ========= 定义子Agent的工具 =========
@tool
def fruit_info(fruid_name:str) -> str:
    """查询水果信息"""
    user_input = interrupt("是否确认继续查询该水果？输入“是”继续查询，输入其他内容结束查询")
    if user_input.lower() != "是":
        return "用户取消查询"
    return f"{fruid_name}:富含维生素，建议每天食用100g"


@tool
def viggie_info(viggie_name:str) -> str:
    """查询蔬菜信息"""
    return f"{viggie_name}:低热量高纤维，建议每天食用200g"


#==== 构建子Agent====
fruit_agent = create_agent(
    model=deepseek_llm_flash,
    tools=[fruit_info],
    system_prompt="你是水果专家，回答一定要基于 fruit_info 的工具真实结果 ",
)


veggie_agent = create_agent(
    model=deepseek_llm_flash,
    tools=[viggie_info],
    system_prompt="你是蔬菜专家，回答一定要基于 viggie_info 的工具真实结果 "
)

# === 构建主Agent的工具 ======、
@tool
def ask_fruit_expert(question:str)->str:
    """水果专家助手，所有水果问题都必须交个这个工具"""
    response = fruit_agent.invoke({"messages":[{"role":"user","content":question}]})
    return response["messages"][-1].content

@tool
def ask_viggie_expert(question:str)->str:
    """蔬菜专家助手，所有蔬菜问题都必须交个这个工具"""
    response = veggie_agent.invoke({"messages":[{"role":"user","content":question}]})
    return response["messages"][-1].content


# ====构建主Agent ===
outer_agent = create_agent(
    model=deepseek_llm_flash,
    tools=[ask_fruit_expert,ask_viggie_expert],
    system_prompt="你是客服主管，你有两个助手：ask_fruit_expert(水果专家),ask_viggie_expert(蔬菜专家)"
                  "当遇到水果问题就调用ask_fruit_expert,当遇到蔬菜问题就调用ask_viggie_expert",
    checkpointer=InMemorySaver()

)


def get_user_input(interrupt_info):
    """根据中断信息向用户提问并读取输入（通用：字符串/字典都行）"""
    if isinstance(interrupt_info, str):
        return input(f"\n[系统]: {interrupt_info}\n[用户]: ").strip()

    # 字典场景：遍历所有键值对展示，原样返回输入
    show_info = "\n".join(f"{k}:{v}" for k, v in interrupt_info.items())
    return input(f"\n[系统]: {show_info}\n[用户]: ").strip()


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "thread001"}}
    while True:
        user_input = input("[用户]:").strip()

        if user_input.lower() in ["quit","exit","退出","q"]:
            print("[助手]：感谢你的咨询，再见")
            break

        if not user_input:
            continue

        stream_input: dict | Command = {
            "messages": [{"role": "user", "content": user_input}]
        }

        while True:
            # 1. 调用图，事件流驱动
            stream = outer_agent.stream_events(stream_input, config=config, version="v3")

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

