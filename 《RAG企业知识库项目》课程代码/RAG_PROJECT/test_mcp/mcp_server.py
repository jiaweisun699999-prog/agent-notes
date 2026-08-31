# math_server.py
from mcp.server.fastmcp import FastMCP
from zhipuai import ZhipuAI

from utils.env_utils import ZHIPU_API_KEY

mcp = FastMCP("Math")
zhipu_client = ZhipuAI(api_key=ZHIPU_API_KEY, base_url='https://open.bigmodel.cn/api/paas/v4/')


@mcp.tool(name='my_search_tool', description='搜索互联网上的内容')
def my_search(query: str) -> str:
    """
    搜索互联网上的内容
    :param query: 需要搜索的内容或者关键词
    :return: 返回搜索结果
    """
    response = zhipu_client.web_search.web_search(
        search_engine="search-pro",
        # search_engine="search-std",
        search_query=query
    )
    print(response)
    if response.search_result:
        return "\n\n".join([d.content for d in response.search_result])
    return '没有搜索到任何内容！'


@mcp.tool()
def add(a: int, b: int) -> int:
    """加法运算: 计算两个数字相加"""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """乘法运算：计算两个数字相乘"""
    return a * b


@mcp.resource("datas://users/{user_id}/email", name='get_user_email')
async def get_user_email(user_id: str) -> str:
    """检索给定用户ID的电子邮件地址。"""
    emails = {"123": "alice@example.com", "456": "bob@example.com"}
    return emails.get(user_id, "not_found@example.com")


if __name__ == "__main__":
    mcp.run(transport='sse')
