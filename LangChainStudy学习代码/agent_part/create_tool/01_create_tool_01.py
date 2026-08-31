from langchain.agents import create_agent
from langchain_core.tools import tool

from init_llm import deepseek_llm


@tool("get_employee_info",description="根据员工ID查询员工的姓名、部门、职务和邮箱。")
def get_employee_info(employee_id: str) -> str:
    """
    根据员工ID查询员工的姓名、部门、职务和邮箱。
    Args:
        employee_id (str): 员工ID
    Returns:
        str: 员工信息
    """

    # 模拟数据
    mock_employee_database = {
        "E001": {"name": "张三", "department": "技术部", "position": "高级软件工程师", "email": "zhangsan@company.com"},
        "E002": {"name": "李四", "department": "市场部", "position": "市场经理", "email": "lisi@company.com"},
        "E003": {"name": "王五", "department": "人力资源部", "position": "招聘专员", "email": "wangwu@company.com"}
    }


    employee_record = mock_employee_database.get(employee_id)

    if employee_record:
        return f"员工ID {employee_id} 的信息如下：姓名 - {employee_record['name']}，部门 - {employee_record['department']}，职务 - {employee_record['position']}，邮箱 - {employee_record['email']}"
    else:
        return f"员工ID {employee_id} 不存在"

agent = create_agent(
    model=deepseek_llm,
    tools=[get_employee_info],
    system_prompt="你是一个员工信息查询助手，你可以根据员工ID查询员工的姓名、部门、职务和邮箱。"

)

result = agent.invoke({"messages": [{"role": "user", "content": "查询员工ID E001 的信息"}]})
print(type(result))
print("result:", result)

print(result["messages"][-1].content)




