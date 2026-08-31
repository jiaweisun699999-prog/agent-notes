"""
MCCP Client 端，导入数据
"""
import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp.client.streamable_http import RequestContext
from mcp.types import LoggingMessageNotificationParams, ElicitRequest, ElicitRequestParams, ElicitResult
from numpy._core.strings import isdigit

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



async def my_on_elicitation(
        mcp_context:RequestContext,
        params:ElicitRequestParams,
        context:CallbackContext
    ):


    # print("mcp_context:",mcp_context)
    # print("params:",params)
    # print("context:",context)


    message = params.message

    print(f"【系统询问】-{message}")


    #用户可以选择的输入：
    options = params.requestedSchema["properties"]["value"]["enum"]

    if options:
        #打印可选选项
        for i,opt in enumerate(options,1):
            print(f"{i}. {opt}")

        #用户输入
        while True:
            selected = input(f"请输入编号（1-{len(options)}）：").strip()
            if isdigit(selected) and 0<=int(selected)<=len(options):
                selected = options[int(selected)-1]
                break
            else:
                print(f"请输入正确的选项（1-{len(options)}）")

        print(f"用户选择了：{selected}")

    else:
        selected = input("请输入：").strip()

    return ElicitResult(action="accept",content={"value": selected})


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
            on_elicitation=my_on_elicitation
        )
    )

    tools = await client.get_tools()

    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        system_prompt="你是一个数据导入助手，你可以调用 import_file 工具将数据导入",
    )

    result1 = await agent.ainvoke({"messages":[{"role":"user","content":"将 data.zip 给我导入"}]})
    print("result1:",result1)
    print(result1["messages"][-1].content)



    result2 = await agent.ainvoke({"messages": [{"role": "user", "content": "查看已经存在的文件"}]})
    print(result2["messages"][-1].content)


if __name__ == '__main__':
    asyncio.run(main())



