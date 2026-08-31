from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from init_llm import deepseek_llm_flash


# ============================================================
# 子 Agent 自己的工作工具
# ============================================================
@tool
def fruit_info(fruit_name: str) -> str:
    """查询水果信息。"""
    return f"{fruit_name}：富含维生素，建议每天食用。"


@tool
def veggie_info(veggie_name: str) -> str:
    """查询蔬菜信息。"""
    return f"{veggie_name}：低热量高纤维，适合减脂期。"


# ============================================================
# 子 Agent（create_agent 底层就是 LangGraph 图）
# ============================================================
fruit_agent = create_agent(
    model=deepseek_llm_flash,
    tools=[fruit_info],
    system_prompt="你是水果专家。回答一定要基于 fruit_info 工具的真实结果。",
    checkpointer=True,
)

veggie_agent = create_agent(
    model=deepseek_llm_flash,
    tools=[veggie_info],
    system_prompt="你是蔬菜专家。回答一定要基于 veggie_info 工具的真实结果。",
    checkpointer=True,
)


# ============================================================
# 把子 Agent 打包成工具
# ============================================================
@tool
def ask_fruit_expert(question: str) -> str:
    """询问水果专家。所有水果问题都必须交给这个工具。"""
    response = fruit_agent.invoke({"messages": [{"role": "user", "content": question}]})
    return response["messages"][-1].content


@tool
def ask_veggie_expert(question: str) -> str:
    """询问蔬菜专家。所有蔬菜问题都必须交给这个工具。"""
    response = veggie_agent.invoke({"messages": [{"role": "user", "content": question}]})
    return response["messages"][-1].content


# ============================================================
# 主 Agent：per-thread 子 Agent 必须用 ToolCallLimitMiddleware
# 限制同一工具单次只能调用一次，避免并行调用写同一 namespace 产生冲突
# ============================================================
outer_agent = create_agent(
    model=deepseek_llm_flash,
    tools=[ask_fruit_expert, ask_veggie_expert],
    system_prompt=(
        "你是客服主管。你有两个助手：ask_fruit_expert（水果）和 ask_veggie_expert（蔬菜）。"
        "遇到水果问题就调用 ask_fruit_expert，蔬菜问题就调用 ask_veggie_expert。"
    ),
    middleware=[
        ToolCallLimitMiddleware(tool_name="ask_fruit_expert", run_limit=1),
        ToolCallLimitMiddleware(tool_name="ask_veggie_expert", run_limit=1),
    ],
    checkpointer=InMemorySaver(),
)


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "thread001"}}

    # 第一次调用：同时问水果和蔬菜
    response1 = outer_agent.invoke(
        {"messages": [{"role": "user", "content": "樱桃和西兰花哪个更适合减脂？"}]},
        config=config,
    )
    print(f"第 1 次对话消息数：{len(response1['messages'])}")
    print(f"回复：{response1['messages'][-1].content}")

    print("="*100)

    # 第二次调用：子 Agent 记住上次对话，消息数累积
    response2 = outer_agent.invoke(
        {"messages": [{"role": "user", "content": "那橙子和胡萝卜呢？"}]},
        config=config,
    )
    print(f"第 2 次对话消息数：{len(response2['messages'])}")
    print(f"回复：{response2['messages'][-1].content}")

