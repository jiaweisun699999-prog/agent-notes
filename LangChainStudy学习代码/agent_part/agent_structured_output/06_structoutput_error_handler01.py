from typing import Union

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from pydantic import BaseModel, Field

from init_llm import deepseek_llm

class PersonInfo(BaseModel):
    name: str = Field(description="姓名")
    email: str = Field(description="邮箱")
    phone: str = Field(description="手机号")


class EventInfo(BaseModel):
    event_name:str = Field(description="活动名称")
    dt:str = Field(description="活动时间")

agent = create_agent(
    model=deepseek_llm,
    system_prompt="你是一个专业的信息提取助手",
    response_format=ToolStrategy(
        Union[PersonInfo,EventInfo],
        tool_message_content="对象提取完成!",
        handle_errors="数据结构存在问题！"
    )
)

# response = agent.invoke({"messages": [{"role": "user", "content": "请提取以下文本中的姓名、邮箱和手机号：姓名：张三，邮箱：zhangsan@example.com，手机号：13812345678"}]})

response = agent.invoke({"messages": [{"role": "user", "content": "从如下内容提取信息：姓名：张三，邮箱：zhangsan@example.com，手机号：13812345678，活动名称：公司年会，活动时间：2025-12-01"}]})
print("response:", response)

for msg in response["messages"]:
    msg.pretty_print()

print(response["structured_response"])



