from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from pydantic import BaseModel, Field

from init_llm import deepseek_llm

class PersonInfo(BaseModel):
    name: str = Field(description="姓名")
    email: str  = Field(description="邮箱")
    phone: str  = Field(description="手机号")


agent = create_agent(
    model=deepseek_llm,
    system_prompt="你是一个专业的信息提取助手",
    response_format=ToolStrategy(
        PersonInfo,
        tool_message_content="对象提取完成!",
        handle_errors=True
    )
)

response = agent.invoke({"messages": [{"role": "user", "content": "请提取以下文本中的姓名、邮箱和手机号：姓名：张三，邮箱：zhangsan@example.com，手机号：13812345678"}]})
print("response:", response)

for msg in response["messages"]:
    msg.pretty_print()

print(response["structured_response"])



