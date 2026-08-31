"""
远程运行的 MCP Server ,通信使用http
"""
from fastmcp import FastMCP

mcp = FastMCP("weather_server")


@mcp.tool
async def get_weather(city: str) -> str:
    """
    获取城市的天气信息
    Args:
        city: 城市名称
    Returns:
        返回城市的天气信息
    """
    weather_data = {
        "北京":"20度，晴朗的天气",
        "上海": "23度，阴雨天气",
        "广州": "30度，多云天气",
    }

    return weather_data.get(city, "未找到该城市的天气信息")


if __name__ == '__main__':
    # 以 http模式启动 ，默认端口是8000端口
    # mcp.run(transport="stramable-http")
    mcp.run(
        transport="http",
        port=8001,
        host="127.0.0.1",
        path="/mcp-a"
    )
