"""
客户端以子进程方式启动脚本，通过标准输入/输出通信
"""
from fastmcp import FastMCP

mcp = FastMCP("math_server")


# 定义工具
@mcp.tool
def add(a: int, b: int) -> int:
    """计算两数之和
    Args:
        a: 第一个数字
        b: 第二个数字
    Returns:
        返回两数的和
    """
    return a + b

@mcp.tool
def multiply(a: int, b: int) -> int:
    """
    计算两数之积
    Args:
        a: 第一个数字
        b: 第二个数字
    Returns:
        返回两数的积
    """
    return a * b

if __name__ == '__main__':
    # 后续由client以子进程的方式启动
    mcp.run(transport="stdio")