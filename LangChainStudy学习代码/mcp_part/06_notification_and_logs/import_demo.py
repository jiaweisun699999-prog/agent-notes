"""
MCCP Client 端，导入数据
"""
import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp.types import LoggingMessageNotificationParams

from init_llm import deepseek_llm

async def my_on_progress(
        progress:float, #当前阶段进度
        total:float, #总进度
        message:str, #当前阶段消息
        context:CallbackContext
    ):

    print(f"【进度】MCP 服务器名称：{context.server_name},当前工具名称：{context.tool_name}，当前阶段进度：{progress}%，当前处理消息：{message}")


async def my_on_logging_message(
       params:LoggingMessageNotificationParams,
       context:CallbackContext
    ):

    print(f"【日志】MCP 服务器名称：{context.server_name},当前工具名称：{context.tool_name}，日志级别：{params.level}，日志消息：{params.data}")



async def main():
    client = MultiServerMCPClient(
        {
            "import_server":{
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            },
        },
        callbacks=Callbacks(
            on_progress=my_on_progress,
            on_logging_message=my_on_logging_message,
        )
    )

    tools = await client.get_tools()

    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        system_prompt="你是一个数据导入助手，你可以调用 import_data 工具将数据 导入到数据库中",
    )

    result = await agent.ainvoke({"messages":[{"role":"user","content":"将 data.zip 给我导入到数据库中"}]})


    print(result["messages"][-1].content)


if __name__ == '__main__':
    asyncio.run(main())



