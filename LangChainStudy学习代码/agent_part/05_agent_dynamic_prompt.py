# 工具1：模拟查询订单信息
import json
from typing import TypedDict

from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain_core.tools import tool

from init_llm import deepseek_llm


@tool
def query_order_info(order_id: str) -> str:
    """根据订单ID查询订单的详细信息，包括状态、商品列表和创建时间。"""
    # 模拟数据库查询结果
    order_database = {
        "ORD123456": {"status": "已发货", "items": ["手机X1"], "create_time": "2025-01-15"},
        "ORD654321": {"status": "待付款", "items": ["耳机Y1"], "create_time": "2025-01-18"}
    }
    order_data = order_database.get(order_id)
    if order_data:
        return json.dumps(order_data, ensure_ascii=False)
    else:
        return f"错误：未找到订单 {order_id}。"

# 工具2：模拟检索常见问题解答
@tool
def search_faq(keyword: str) -> str:
    """根据关键词从知识库中检索相关的政策条款或解决方案。"""
    # 模拟FAQ知识库
    faq_knowledge_base = {
        "退货": "支持7天无理由退货，商品需完好且包装齐全。",
        "保修": "电子产品享受1年免费保修服务。",
        "发货": "下单后48小时内发货，偏远地区可能延迟。"
    }
    # 简单关键词匹配
    for topic, answer in faq_knowledge_base.items():
        if topic in keyword:
            return answer
    return f"未找到与'{keyword}'直接相关的政策，请尝试其他关键词或联系人工客服。"

class AgentContext(TypedDict):
    query_type:str
    uid:str

@dynamic_prompt
def dynamic_support_prompt(request:ModelRequest) -> str:
    print("request",request)
    query_type = request.runtime.context["query_type"]
    # 根据不同的query_type 设置不同的提示词
    base_instruction = "你是一名专业的电商客服助手。请根据工具查询结果，准确、清晰地回答用户问题。"

    if query_type == "vip":
        # 针对复杂或需要升级处理的问题
        return f"""{base_instruction}
                    当前角色：高级支持专员
                    工作要求：
                    1.深度分析：仔细分析用户描述，识别潜在的根本问题。
                    2.精准分类：将问题明确归类（如“物流问题”、“产品质量”、“售后申请”）。
                    3.方案规划：若工具能解决，提供具体步骤；若需人工，明确告知后续流程。
                    请使用更专业、严谨的语言。
                    """
    else:
        # 针对常规客服问题
        return f"""{base_instruction}
                    当前角色：一线客服助手
                    工作要求：
                    1.简洁友好：回复要简单明了，避免复杂术语。
                    保持友好和高效的沟通风格。
                    """


agent = create_agent(
    model=deepseek_llm,
    tools=[query_order_info, search_faq],
    middleware=[dynamic_support_prompt],
    context_schema=AgentContext
)

print("==== vip ====")
response1 = agent.invoke(
    {"messages": [{"role": "user", "content": "查询订单ORD123456的状态？"}]},
    context={"query_type":"vip","uid":"user123"}
)


print(response1["messages"][-1].content)

print("==== 普通用户 ====")

response2 = agent.invoke(
    {"messages": [{"role": "user", "content": "查询订单ORD123456的状态？"}]},
    context={"query_type":"xxx","uid":"user123"}
)

print(response2["messages"][-1].content)
