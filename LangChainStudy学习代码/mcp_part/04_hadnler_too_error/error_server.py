"""
MCP Server端，工具调用出现错误
"""
import random

from fastmcp import FastMCP

mcp = FastMCP("我的mcp服务")

USERS = {"U001":"张三","U002":"李四","U003":"王五"}


@mcp.tool()
def get_user(user_id:str):
    """根据用户ID查询用户信息

    Args:
        user_id (str): 用户ID
    Returns:
        str: 用户信息
    """
    if user_id not in USERS:
        raise ValueError(f"用户{user_id} 不存在，请确认ID是否正确")

    return f"用户{user_id}的姓名是：{USERS[user_id]}"


@mcp.tool()
def search_database(keyword:str)-> str:
    """根据关键词搜索数据库
    Args:
        keyword (str): 搜索关键词
    Returns:
        str: 搜索结果
    """
    if random.random() < 0.1:
        return f"关键词{keyword}的搜索结果找到了10条数据"
    raise RuntimeError("网络波动了，数据库连接超时，重试一下即可")


if __name__ == '__main__':
    mcp.run(
        transport="http",
        port=8000,
        host="0.0.0.0",
    )
