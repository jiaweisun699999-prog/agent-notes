import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from init_llm import deepseek_llm


async def test_retry():

    client = MultiServerMCPClient(
        {
            "remote_server":{
                "transport":"http",
                "url":"http://localhost:8000/mcp"
            }
        },
        handle_tool_errors=False
    )


    tools = await client.get_tools()

    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        system_prompt="你是一个助手，调用search_database工具查询数据库中的信息，如果出现错误，请重试最多5次，如果依然失败，请返回错误信息"
    )

    # result = await agent.ainvoke({"messages":[{"role":"user","content":"帮我查询U999用户信息"}]})
    # print(f"result:",result)

    result = await agent.ainvoke({"messages":[{"role":"user","content":"去数据库中查询 大模型 关键词相关的信息"}]})
    print(f"result:",result)

    print(result["messages"][-1].content)


if __name__ == '__main__':
    asyncio.run(test_retry())



