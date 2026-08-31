from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import after_model, before_model
from langchain_core.messages import RemoveMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.runtime import Runtime
from langchain_core.messages import SystemMessage

from init_llm import deepseek_llm, tongyi_llm


@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气
    Args:
        city (str): 要查询天气的城市名称

    Returns:
        str: 包含城市天气信息的字符串
    """
    return f"{city}的天气是晴朗的，温度是25摄氏度"


@before_model
def print_before_model_state(state: AgentState, runtime: Runtime) -> dict | None:
    # 打印当前消息
    print("before_model_state：", state)

    messages = state["messages"]

    return {"messages": messages}


@after_model
def custom_summarizer(state: AgentState, runtime) -> dict | None:
    """自定义摘要逻辑，保留最近N条消息，并对N条消息前的所有消息进行摘要
        最后保留的最近N条消息中要保证包含完整调用工具链
    """
    # 打印当前消息
    print("after_model_state：", state)

    messages = state["messages"]
    # 触发摘要的阈值
    threshold = 5
    # 保留最近N条消息
    max_retain = 2

    # 如果 messages 条数达到触发摘要的阈值，那么就进行摘要处理，否则直接返回 None
    if len(messages) <= threshold:
        return None

    # 最近保留N条消息的集合
    recent_messages = messages[-max_retain:]

    # 遍历最近保留N条消息，判断第1条消息是否是 ToolMessage, 如果是那么多往前保留1条消息, 直到第1条消息不是 ToolMessage 为止
    while True:
        # 获取最近保留消息中的第1条消息，判断是不是ToolMessage
        if isinstance(recent_messages[0], ToolMessage):
            # 如果是那么多往前保留1条消息
            max_retain += 1
            recent_messages = messages[-max_retain:]
        else:
            # 如果第一条消息不是 ToolMessage 那么就跳出循环
            break

    early_messages = messages[:-max_retain]  # 保留最近N条消息前的所有消息

    # 准备摘要提示
    summary_prompt = f"""
        请将以下对话内容总结成一段简洁的摘要，保留重要信息和细节：

        对话历史：
        {"".join([f"{msg.type}: {msg.content}" for msg in early_messages])}

        摘要要求：
        1. 保留人物、地点、关键事件等重要信息
        2. 保持第三人称叙述
        3. 长度不超过200字
        4. 使用中文总结

        """

    try:
        # 调用模型生成摘要
        summary_response = tongyi_llm.invoke(summary_prompt)
        summary_content = f"对话摘要: {summary_response.content}"

        # 创建摘要消息
        summary_message = SystemMessage(content=summary_content)

        # 组合新消息列表：摘要 + 最近消息
        new_messages = [summary_message] + recent_messages

        return {
            "messages": [
                RemoveMessage(id=REMOVE_ALL_MESSAGES),
                *new_messages
            ]
        }

    except Exception as e:
        print(f"摘要生成失败: {e}")
        return None


agent = create_agent(
    model=deepseek_llm,
    tools=[get_weather],
    middleware=[print_before_model_state, custom_summarizer],
    checkpointer=InMemorySaver(),
)

config = {"configurable": {"thread_id": "session_001"}}

# 模拟对话
response1 = agent.invoke({"messages": [{"role": "user", "content": "你好，我是张三"}], }, config=config)
print(response1["messages"][-1].content)

print("***" * 20)
response2 = agent.invoke({"messages": [{"role": "user", "content": "今天北京天气好吗？"}]}, config=config)
print(response2["messages"][-1].content)

print("***" * 20)
response3 = agent.invoke({"messages": [{"role": "user", "content": "我的名字叫什么？"}]}, config=config)
print(response3["messages"][-1].content)