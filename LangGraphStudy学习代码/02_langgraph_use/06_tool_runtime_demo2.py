"""
ToolRuntime&ToolNode
业务：电商客服——查订单、查库存。使用 ToolRuntime 访问图状态
"""
from typing import Literal
from langchain.tools import ToolRuntime, tool
from langchain.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

from init_llm import deepseek_llm


class CustomerState(MessagesState):
    """在标准消息状态基础上增加 user_id"""
    user_id: str


@tool
def check_order(runtime: ToolRuntime, order_id: str) -> str:
    """查询订单状态
    Args:
        order_id: 订单号，如 ORD-001
    Returns:
        订单状态描述
    """
    print("runtime:",runtime)
    # 通过 ToolRuntime 从图状态中读取 user_id
    user_id = runtime.state.get("user_id", "unknown")

    mock_orders = {
        "ORD-001": "已发货，预计明天到达",
        "ORD-002": "正在处理中",
        "ORD-003": "已签收",
    }

    status = mock_orders.get(order_id, "未找到该订单")
    return f"用户{user_id}的订单{order_id}：{status}"


@tool
def check_inventory(product_name: str) -> str:
    """查询商品库存
    Args:
        product_name: 商品名称
    Returns:
        商品库存描述
    """
    inventory = {
        "蓝牙耳机": "库存充足（>100件）",
        "机械键盘": "库存紧张（仅剩5件）"
    }
    return inventory.get(product_name, f"未找到商品[{product_name}]")


tools = [check_order, check_inventory]
model_with_tools = deepseek_llm.bind_tools(tools)


def llm_node(state: CustomerState) -> dict:
    """LLM 节点：决定调用工具还是直接回答"""
    response = model_with_tools.invoke(
        [SystemMessage(content="你是电商客服助手，用工具查询信息后回答。")]
        + state["messages"]
    )
    return {"messages": [response]}


def should_continue(state: CustomerState) -> Literal["tools", END]:
    """条件边：有工具调用则进入工具节点，否则结束"""
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"
    return END


builder = StateGraph(CustomerState)
builder.add_node("llm", llm_node)
builder.add_node("tools", ToolNode(tools))  # 使用 ToolNode 预置节点

builder.add_edge(START, "llm")
builder.add_conditional_edges("llm", should_continue, ["tools", END])
builder.add_edge("tools", "llm")

agent = builder.compile()


if __name__ == "__main__":
    print("ToolRuntime + ToolNode：电商客服助手")
    print("=" * 60)

    result = agent.invoke({
        "messages": [HumanMessage(content="帮我查一下订单 ORD-001 的状态")],
        "user_id": "user_123",
    })
    print(f"客服: {result['messages'][-1].content}")

    print("-" * 40)

    result = agent.invoke({
        "messages": [HumanMessage(content="蓝牙耳机还有货吗？")],
        "user_id": "user_123",
    })
    print(f"客服: {result['messages'][-1].content}")

