"""
案例：AI回复内容安全审核
功能：使用 @after_agent 在Agent输出后进行语义层面的安全审核
"""
from typing import Any
from langchain.agents import create_agent
from langchain.agents.middleware import after_agent, AgentState
from langchain.tools import tool
from langgraph.runtime import Runtime

from init_llm import deepseek_llm


# ========== 1. 定义工具 ==========
@tool
def search_knowledge(keyword: str) -> str:
    """搜索知识库信息"""
    knowledge = {
        "感冒": "感冒通常由病毒引起，症状包括流鼻涕、咳嗽、喉咙痛等。建议多休息、多喝水。",
        "发烧": "发烧是身体对抗感染的防御机制。体温超过38.5°C可考虑使用退烧药。",
        "温度": "温度是指物体的热冷程度，通常用摄氏度（℃）或华氏度（℉）表示。",
    }

    for key in knowledge.keys():
        if key in keyword:
            return knowledge[key]

    return f"关于[{keyword}]暂无收录信息。"


# ========== 2. 定义 After Agent 守卫 ==========

@after_agent(can_jump_to=["end"])
def content_output_review(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """
    输出内容审核器（模型驱动守卫）
    在模型生成回复后，用模型对回复内容做二次审核
    如果回复不合适，替换为预设的安全回复
    """

    last_message = state["messages"][-1]

    print("last_message", last_message)

    # 用模型来评估回复内容是否安全合适
    review_prompt = f"""请判断以下回复是否安全、适当，只回复[安全]或[不安全]
                        安全标准：回复内容不能包含任何医疗建议或承诺。

                    回复内容：{last_message.content}

                    """

    review_result = deepseek_llm.invoke([
        {"role": "user", "content": review_prompt}
    ])

    # 如果审核不通过，替换回复内容
    if "不安全" in review_result.content:
        print("[内容审核] 模型输出未通过安全审核，已替换")
        last_message.content = "抱歉，我无法生成该回复。请换一个话题或重新描述您的问题。"

    return None


# ========== 3. 创建智能体 ==========

agent = create_agent(
    model=deepseek_llm,
    tools=[search_knowledge],
    middleware=[content_output_review],
    system_prompt="你是一个助手。回答用户问题时必须调用search_knowledge工具搜索知识库信息后回答"
)

# ========== 4. 测试 ==========
response1 = agent.invoke({
    "messages": [{"role": "user", "content": "发烧了怎么办"}],
})

print("response", response1)
print(f"助手回复: {response1['messages'][-1].content}")

response2 = agent.invoke({
    "messages": [{"role": "user", "content": "什么是温度？"}]
})

print("response", response2)
print(f"助手回复: {response2['messages'][-1].content}")