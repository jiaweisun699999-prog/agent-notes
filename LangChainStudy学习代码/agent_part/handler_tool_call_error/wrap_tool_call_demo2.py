from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool, ToolException
import json
import random

from init_llm import deepseek_llm

# 模拟工单数据库
TICKET_DATABASE = {
    "T001": {"title": "登录问题", "status": "处理中", "assignee": "张三"},
    "T002": {"title": "支付失败", "status": "已解决", "assignee": "李四"},
    "T003": {"title": "页面加载慢", "status": "待处理", "assignee": "王五"}
}


@tool
def query_ticket(ticket_id: str) -> str:
    """
    根据工单ID查询工单详情
    Args:
        ticket_id (str): 工单ID
    Returns:
        str: 工单详情的JSON字符串
    """
    # 模拟网络不稳定：50%概率失败
    if random.random() < 0.5:
        raise ConnectionError("数据库连接超时，请稍后重试")

    if ticket_id not in TICKET_DATABASE:
        raise ToolException(f"工单ID {ticket_id} 不存在")

    ticket = TICKET_DATABASE[ticket_id]
    return json.dumps(ticket, ensure_ascii=False, indent=2)


@tool
def update_ticket_status(ticket_id: str, new_status: str) -> str:
    """
    更新工单状态
    Args:
        ticket_id (str): 工单ID
        new_status (str): 工单新状态
    Returns:
        str: 更新成功的消息
    """
    valid_statuses = ["待处理", "处理中", "已解决", "已关闭"]

    if ticket_id not in TICKET_DATABASE:
        raise ToolException(f"工单ID {ticket_id} 不存在")

    if new_status not in valid_statuses:
        raise ToolException(f"状态必须是: {', '.join(valid_statuses)}")

    # 模拟权限检查失败
    if random.random() < 0.2:
        raise PermissionError("权限不足：只有管理员可以关闭工单")

    TICKET_DATABASE[ticket_id]["status"] = new_status
    return f"工单 {ticket_id} 状态已更新为: {new_status}"


# 分层错误处理中间件
@wrap_tool_call
def intelligent_error_handler(request, handler):
    """智能错误处理：根据错误类型返回不同的指导信息"""
    try:
        return handler(request)
    except ConnectionError as e:
        return ToolMessage(
            content=f"系统暂时繁忙：{str(e)}。建议您稍后重试此操作。",
            tool_call_id=request.tool_call["id"]
        )
    except PermissionError as e:
        return ToolMessage(
            content=f"权限限制：{str(e)}。如需执行此操作，请联系管理员。",
            tool_call_id=request.tool_call["id"]
        )
    except ToolException as e:
        return ToolMessage(
            content=f"输入验证失败：{str(e)}。请检查输入参数是否正确。",
            tool_call_id=request.tool_call["id"]
        )
    except Exception as e:
        return ToolMessage(
            content=f"意外错误：{str(e)}。技术团队已收到通知，请稍后重试。",
            tool_call_id=request.tool_call["id"]
        )


# 创建智能体
agent = create_agent(
    model=deepseek_llm,
    tools=[query_ticket, update_ticket_status],
    middleware=[intelligent_error_handler],
    system_prompt=SystemMessage(content= """你是企业客服工单系统助手，可以帮助用户查询和更新工单状态。
    当工具调用失败时，你会收到明确的错误提示，请根据错误类型给予用户相应的指导。""")
)



"""测试各种错误场景"""
test_cases = [
    "查询工单T999的详情",  # 不存在的工单ID
    "把工单T001状态更新为完结状态",  # 无效状态
    "查询工单T001的详情",  # 正常查询（可能触发随机错误）
    "关闭工单T002"  # 权限相关操作
]

for query in test_cases:
    print("=" * 50)
    response = agent.invoke({
        "messages": [{"role": "user", "content": query}]
    })

    print("response",response)

    print(f"用户查询: {query}")
    # 提取最后一条消息内容
    result = response["messages"][-1]
    print(f"助手回复: {result.content}")



