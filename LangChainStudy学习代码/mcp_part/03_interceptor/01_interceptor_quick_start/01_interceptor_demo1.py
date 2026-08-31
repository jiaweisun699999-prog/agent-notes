"""
使用日志拦击器
"""
import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest

from init_llm import deepseek_llm


async def logging_interceptor(request:MCPToolCallRequest,handler):
    "每次调用工具前后都要打印调用工具的日志信息"
    print("request",request)
    print(f"【拦截器】调用前，调用的工具名称：{request.name} ,工具参数：{request.args}")

    result = await handler(request) #调用工具/拦截器

    print(f"【拦截器】调用后，调用的工具名称：{request.name} ,result：{result}")

    return result


async def main():
    client = MultiServerMCPClient(
        {
            "my_match_server":{
                "transport":"http",
                "url":"http://localhost:8000/mcp",
            }
         },
        # 传入拦截器列表
        tool_interceptors=[logging_interceptor]
    )

    tools = await client.get_tools()

    agent = create_agent(
        model=deepseek_llm,
        tools=tools

    )


    result= await agent.ainvoke({"messages":[{"role":"user","content":"给我计算 3加上5是多少"}]})

    print(result["messages"][-1].content)


if __name__ == '__main__':
    asyncio.run(main())