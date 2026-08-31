"""
LangChain Agent 使用 MCP Server 工具
包含：stdio和http两种通信方式
"""
import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from init_llm import deepseek_llm


async def main():
    # 1. 创建MCP Client 客户端 ，配置多个MCP Server 信息
    client = MultiServerMCPClient(
        {
            # stdio 本地进程
            "my_math_server": {
                "transport": "stdio",
                "command": "D:\\ProgramData\\miniconda3\\envs\\langchain_study\\python.exe",
                "args": ["D:/PyCharmSpace/LangChainStudy/mcp_part/01_quick_start/math_server.py"],
                "env":{
                    "PYTHONIOENCODING": "utf-8",
                }
            },

            # http 远程Server
            "my_weather_server": {
                "transport": "http",
                "url": "http://localhost:8001/mcp-a",
            },
        }
    )

    # 2. 从多个Server中加载工具，通过get_tools() 方法将工具转化成LangChain的工具格式
    tools = await client.get_tools()

    print("tools:", tools)

    # 3.创建LangChain Agent
    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
    )

    # 4. 运行Agent
    math_result = await agent.ainvoke({"messages": [{"role": "user", "content": "计算 3加上5 ,再乘以2的值"}]})

    weather_result = await agent.ainvoke({"messages": [{"role": "user", "content": "北京的天气"}]})


    print("math_result:", math_result)
    print("weather_result:", weather_result)

    print("数学结果：", math_result["messages"][-1].content)
    print("天气结果：",weather_result["messages"][-1].content)



if __name__ == '__main__':
    asyncio.run(main())
