from dataclasses import dataclass, field

from langchain_core.messages import SystemMessage
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, TypedDict, Annotated
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.tools import tool

from init_llm import deepseek_llm


# 定义工具
@tool
def search_customer_database(query: str) -> str:
    """
    在客户数据库中搜索信息
    Args:
        query (str): 客户查询字符串，例如 "张三" 或 "李四"
    Returns:
        str: 客户记录字符串，包含客户姓名、等级、最近购买日期和累计消费
    """
    # 模拟数据库查询结果
    if "张三" in query.lower():
        return "客户记录：张三，VIP客户，最近购买日期：2024-01-15，累计消费：$15,000"
    elif "李四" in query.lower():
        return "客户记录：李四，普通客户，最近购买日期：2023-12-20，累计消费：$3,200"
    else:
        return f"关于客户{query}，无记录"

@tool
def send_email(customer: str) -> str:
    """
    发送感谢邮件
    Args:
        customer (str): 客户名称，例如 "张三" 或 "李四"
    Returns:
        str: 确认消息，包含已发送的客户名称
    """
    return f"已向 {customer} 发送感谢邮件"



class CustomerAnalysis(TypedDict):
    """客户分析报告"""
    customer_name: Annotated[str, None, "客户姓名"]
    customer_tier: Annotated[Literal["潜在客户", "普通客户", "VIP客户", "流失风险"], None, "客户等级,只能是潜在客户、普通客户、VIP客户或流失风险"]
    spending_level: Annotated[Literal["低", "中", "高"], None, "消费水平"]
    send_email: Annotated[bool, None, "是否已发送感谢邮件"]


# 创建智能体
agent = create_agent(
    model=deepseek_llm,
    system_prompt=SystemMessage(content=""
                                        "请分析指定客户的情况："
                                        "1. 先搜索客户数据库了解最新情况，调用“search_customer_database” 工具去搜索"
                                        "2. 如果是VIP客户，则发送感谢邮件，否则不发送 "
                                        "3. 基于搜索结果生成结构化分析报告 "
                                        "4. 如果用户提问与客户记录无关或找不到客户信息，则返回空对象，不发送感谢邮件"
                                        ),
    tools=[search_customer_database, send_email],
    response_format=ToolStrategy(CustomerAnalysis)
)

# 执行分析
result = agent.invoke({
    "messages": [{"role": "user","content": "请分析客户张三"}]
    # "messages": [{"role": "user","content": "请分析客户李四"}]
    # "messages": [{"role": "user","content": "请分析客户王五"}]
    # "messages": [{"role": "user","content": "今天天气如何"}]
})


# 处理结果
print("result:", result)
if "structured_response" in result:
    analysis = result["structured_response"]
    print(analysis)