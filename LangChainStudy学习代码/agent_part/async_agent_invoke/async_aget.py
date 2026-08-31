import asyncio
from typing import Dict, Any
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.graph.state import CompiledStateGraph

from init_llm import deepseek_llm


# 1. 定义工具
@tool
def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息。
    Args：
        city (str): 要查询天气的城市名称。
    Returns：
        str: 包含城市天气信息的字符串。
    """
    weather_data = {
        "北京": "晴朗，15°C",
        "上海": "多云，18°C",
        "广州": "小雨，22°C",
        "深圳": "晴间多云，25°C"
    }
    return f"{city}的天气：{weather_data.get(city, '信息暂缺')}"


@tool
def get_transport_info(from_city: str, to_city: str) -> str:
    """
    查询两个城市之间的交通信息。
    Args：
        from_city (str): 出发城市名称。
        to_city (str): 到达城市名称。
    Returns：
        str: 包含交通信息的字符串。
    """
    transport_data = {
        "北京-上海": "高铁约4.5小时，航班约2小时",
        "上海-广州": "高铁约7小时，航班约2.5小时",
        "广州-深圳": "高铁约0.5小时，驾车约1.5小时"
    }
    key = f"{from_city}-{to_city}"
    return f"{from_city}到{to_city}：{transport_data.get(key, '请查询具体班次')}"


@tool
def get_scenic_spots(city: str, interest_type: str = "通用") -> str:
    """
    根据兴趣类型推荐城市景点。
    Args：
        city (str): 要查询景点的城市名称。
        interest_type (str, optional): 兴趣类型，默认值为"通用"。
    Returns：
        str: 包含景点推荐的字符串。
    """
    scenic_spots_data = {
        "北京": {
            "历史": "推荐：故宫、天坛、长城",
            "美食": "推荐：全聚德烤鸭、王府井小吃街",
            "通用": "推荐：故宫、长城、颐和园、天坛"
        },
        "上海": {
            "现代": "推荐：外滩、东方明珠、陆家嘴",
            "文化": "推荐：博物馆、艺术馆、田子坊",
            "通用": "推荐：外滩、迪士尼、南京路"
        }
    }
    city_scenic_spots = scenic_spots_data.get(city, {})
    recommendation = city_scenic_spots.get(interest_type, city_scenic_spots.get("通用", "暂无推荐"))
    return f"{city}{interest_type}景点：{recommendation}"


# 2. 创建智能体
def create_travel_agent() -> CompiledStateGraph:
    """创建旅行规划智能体"""
    # 创建智能体
    agent = create_agent(
        model=deepseek_llm,
        tools=[get_weather, get_transport_info, get_scenic_spots],
        system_prompt="你是一个专业的旅行规划助手，能够帮助用户查询天气、交通和景点信息。拒绝回答与旅行规划无关的问题。",
    )
    return agent


# 3. 顺序异步查询函数
async def async_sequential_query() -> Dict[str, Any]:
    # 创建智能体实例
    agent = create_travel_agent()

    # 异步调用智能体
    response = await agent.ainvoke({"messages": [
        {"role": "user", "content": "请帮我查询北京的天气信息，并推荐一些历史类型的景点"},
        # {"role": "user", "content": "我要从北京出发到上海，请帮我查询上海的天气信息，并推荐一些现代类型的景点"},
        # {"role": "user", "content": "天空为什么是蓝色的"},
    ]})

    return response


# 4. 运行程序
if __name__ == "__main__":
   response = asyncio.run(async_sequential_query())
   print(response)
   print(response['messages'][-1].content)