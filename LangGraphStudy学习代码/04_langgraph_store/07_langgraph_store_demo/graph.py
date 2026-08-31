"""
综合案例：智能购物助手
============================================
Checkpointer（短期记忆）：同一会话的消息历史
Store（长期记忆）：跨会话的用户画像（偏好、尺码、预算等）

流程：START → 读Store画像 → LLM提取新偏好 → 写Store → 个性化回复 → END
"""
import json
import operator
from dataclasses import dataclass
from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, AnyMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from langgraph.runtime import Runtime
from init_llm import deepseek_llm


# ============================================================
# 1. 数据结构
# ============================================================
@dataclass
class Context:
    """每次调用时传入的运行时上下文"""
    user_id: str


class ShopState(TypedDict):
    """图状态 —— Checkpointer 管理的短期记忆"""
    messages: Annotated[list[AnyMessage], operator.add]   # 消息历史
    user_profile: str                         # 从 Store 读取的用户画像摘要


# ============================================================
# 2. 节点
# ============================================================
def extract_profile(state: ShopState, runtime: Runtime[Context]):
    """节点1：从 Store 读取用户画像"""
    user_id = runtime.context.user_id
    ns = (user_id, "profile")

    if runtime.store:
        items = runtime.store.search(ns)
    else:
        items = []

    if items:
        # 将 Store 中的多条画像信息拼接成一段文字
        profile_parts = []
        for item in items:
            for key, val in item.value.items():
                profile_parts.append(f"{key}: {val}")
        profile_text = "；".join(profile_parts)
        return {
            "user_profile": profile_text,
        }
    else:
        return {
            "user_profile": "",
        }


def process_message(state: ShopState, runtime: Runtime[Context]):
    """节点2：LLM 分析用户消息，提取偏好信息"""
    profile = state["user_profile"]
    user_msg = state["messages"][-1]["content"]  # 取最新的用户输入

    prompt = SystemMessage(content=(
        "你是一个用户画像分析助手。根据用户的消息，提取以下信息（如果有的话）：\n"
        "- 尺码偏好（如 M码、L码）\n"
        "- 预算范围（如 2000以内）\n"
        "- 颜色偏好（如 喜欢黑色）\n"
        "- 品牌偏好（如 喜欢Nike）\n"
        "- 品类需求（如 想买运动鞋）\n\n"
        "请以 JSON 格式输出，只包含能从消息中明确提取到的字段。"
        "如果用户没有提到某个字段，不要编造。\n"
        '示例输出: {"尺码": "M码", "预算": "2000以内", "颜色偏好": "不喜欢红色"}\n\n'
        f"用户已有画像: {profile if profile else '暂无'}"
    ))

    response = deepseek_llm.invoke([prompt, HumanMessage(content=user_msg)])
    extracted = response.content.strip()

    return {
        "messages": [AIMessage(content=f"[画像分析] 提取结果: {extracted}")],
    }


def save_to_store(state: ShopState, runtime: Runtime[Context]):
    """节点3：将 LLM 提取的偏好存入 Store"""
    user_id = runtime.context.user_id
    ns = (user_id, "profile")

    # 从节点2的输出中取 LLM 返回的 JSON 数据
    # 节点2的 AIMessage 内容是 "[画像分析] 提取结果: {...}"
    last_ai_msg = state["messages"][-1].content

    if "提取结果:" in last_ai_msg:
        json_str = last_ai_msg.split("提取结果:", 1)[-1].strip()

    # 将提取到的字段逐个存入 Store
    # json.loads 解析 JSON 字符串为 Python 字典
    data = json.loads(json_str)
    if runtime.store and data:
        profile_text = ""
        for key, val in data.items():
            # 这里将每个字段的值拼接成一个字符串，用 "；" 分隔开，方便本次工作流中使用偏好信息
            profile_text += f"{key}: {val}；"
            runtime.store.put(ns, f"pref_{key}", {key: val})
        return {
            "user_profile": profile_text,
            "messages": [AIMessage(content=f"[存储] 已更新用户画像: {len(data)} 个字段，更新内容: {data}")]
        }

    return {"messages": [AIMessage(content="[存储] 本次未提取到新的偏好信息")]}


def generate_reply(state: ShopState):
    """节点4：LLM 结合画像 + 对话历史 生成个性化回复"""
    profile = state["user_profile"]

    # 构建系统提示词（包含用户画像）
    system_content = "你是一个智能购物助手，请根据用户画像提供个性化推荐。回复控制在100字以内。"
    if profile:
        system_content += f"\n\n当前用户画像: {profile}"

    response = deepseek_llm.invoke([
        SystemMessage(content=system_content),
        HumanMessage(content=state["messages"][-1].content),
    ])

    return {"messages": [AIMessage(content=response.content)]}


# ============================================================
# 3. 构建图
# ============================================================
builder = StateGraph(state_schema=ShopState, context_schema=Context)

builder.add_node("extract_profile", extract_profile)
builder.add_node("process_message", process_message)
builder.add_node("save_to_store", save_to_store)
builder.add_node("generate_reply", generate_reply)

builder.add_edge(START, "extract_profile")
builder.add_edge("extract_profile", "process_message")
builder.add_edge("process_message", "save_to_store")
builder.add_edge("save_to_store", "generate_reply")
builder.add_edge("generate_reply", END)


graph = builder.compile()


