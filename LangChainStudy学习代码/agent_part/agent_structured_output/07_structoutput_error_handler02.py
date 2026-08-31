from pydantic import BaseModel, Field
from typing import Literal
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy, StructuredOutputValidationError, \
    MultipleStructuredOutputsError
from langchain_core.messages import SystemMessage

from init_llm import deepseek_llm


# 自定义错误处理函数
def custom_error_handler(error: Exception) -> str:
    """自定义错误处理器"""
    error_str = str(error)

    print(f"捕获到错误类型: {type(error).__name__}")
    print(f"错误详情: {error_str}")

    if isinstance(error, StructuredOutputValidationError):
        return "评价数据格式有误，请检查字段是否符合要求。请重新分析评价内容。"
    elif isinstance(error, MultipleStructuredOutputsError):
        return "检测到多个响应，请选择最相关的一个进行返回。"
    else:
        return f"Error: error_str"

# 定义产品评价Schema
class ProductEvaluation(BaseModel):
    """产品评价分析"""
    product_name: str = Field(default="", description="产品名称")
    rating: int = Field(default=1, description="评分1-5", ge=1, le=5)
    sentiment: Literal["正面", "负面", "中性"] = Field(default="", description="情感倾向")


# 创建agent
agent = create_agent(
    model=deepseek_llm,
    tools=[],
    # 创建会诱导错误的系统提示
    system_prompt=SystemMessage(content="""
                    你是一个产品评价分析助手。请分析用户提供的产品评价,并结构化输出产品评价分析结果。
                    如果评价中提到"10分"或"满分"，请将rating设置为10
                    如果评价情感复杂，请尝试使用"复杂"作为sentiment值
                    """),
    response_format=ToolStrategy(
        ProductEvaluation,
        tool_message_content="产品评价分析完成!",
        handle_errors=custom_error_handler  # 启用自定义错误处理
    )
)

# 调用agent
response = agent.invoke({
            # "messages": [{"role": "user","content": "这个产品太棒了，我给5分满分！超级喜欢！"}]
            # "messages": [{"role": "user","content": "这个产品太棒了，我给满分！超级喜欢！"}]
            "messages": [{"role": "user","content": "这个苹果手机用起来感觉复杂，既好又不好"}]
        })


print("response:", response)

for msg in response["messages"]:
    msg.pretty_print()

if "structured_response" in response:
    result = response["structured_response"]
    print(result)