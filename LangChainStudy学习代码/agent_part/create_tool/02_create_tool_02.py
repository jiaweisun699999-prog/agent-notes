import json
from typing import Optional, Literal

from langchain.agents import create_agent
from langchain_core.tools import tool
from pydantic import BaseModel, Field, field_validator

from init_llm import deepseek_llm

class QueryTicketsSchema(BaseModel):
    ticket_id: Optional[str] = Field(default=None, description="工单ID")
    assigner: Optional[str] = Field(default=None, description="工单分配人")
    status: Optional[Literal["open", "resolved", "closed"]] = Field(default=None, description="工单状态,open(待处理),resolved(已处理),closed(已关闭)")
    priority: Optional[Literal["low", "medium", "high"]] = Field(default=None, description="工单优先级,low(低),medium(中),high(高)")

    @field_validator("ticket_id")
    def validate_ticket_id(cls, v):
        return v.upper() if v else None


@tool(args_schema=QueryTicketsSchema)
def query_tickets(
        ticket_id: str=None,
        assigner: str =None,
        status: str =None,
        priority: str =None
) -> str:
    """
    根据工单ID查询工单的详细信息。
    Args:
        ticket_id (str, optional): 工单ID
        assigner (str, optional): 工单分配人
        status (str, optional): 工单状态
        priority (str, optional): 工单优先级
    Returns:
        str: 工单详细信息
    """
    mock_tickets_db = [
        {"ticket_id": "TK2025012001", "assigner": "张三", "title": "登录页面加载缓慢", "status": "open","priority": "low"},
        {"ticket_id": "TK2025012002", "assigner": "李四", "title": "用户头像上传失败", "status": "open","priority": "medium"},
        {"ticket_id": "TK2025011901", "assigner": "张三", "title": "支付成功通知未发送", "status": "resolved","priority": "high"},
        {"ticket_id": "TK2025011902", "assigner": "马六", "title": "订单查询接口返回空值", "status": "closed","priority": "high"},
    ]

    filtered_tickets = mock_tickets_db

    if ticket_id:
        filtered_tickets = [ticket for ticket in filtered_tickets if ticket["ticket_id"] == ticket_id]
    if assigner:
        filtered_tickets = [ticket for ticket in filtered_tickets if ticket["assigner"] == assigner]
    if status:
        filtered_tickets = [ticket for ticket in filtered_tickets if ticket["status"] == status]
    if priority:
        filtered_tickets = [ticket for ticket in filtered_tickets if ticket["priority"] == priority]

    if not filtered_tickets:
        return "没有找到任何工单"

    result = {
        "total_count":len(filtered_tickets),
        "tickets":filtered_tickets
    }

    return json.dumps(result, ensure_ascii=False, indent=2)




agent = create_agent(
    model=deepseek_llm,
    tools=[query_tickets],
    system_prompt="你是一个工单查询助手，你可以根据工单ID查询工单的详细信息。"

)

# result = agent.invoke({"messages": [{"role": "user", "content": "查询工单ID tk2025012001 的详细信息"}]})
# result = agent.invoke({"messages": [{"role": "user", "content": "查询马六 负责的工单信息"}]})

result = agent.invoke({"messages": [{"role": "user", "content": "请帮我查询一下张三负责的优先级别为高的工单信息"}]})
print("result",result)

print(result["messages"][-1].content)

