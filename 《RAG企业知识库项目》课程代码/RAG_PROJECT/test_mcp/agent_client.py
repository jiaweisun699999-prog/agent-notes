from langchain.agents import create_react_agent, create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_mcp_adapters.client import MultiServerMCPClient

from llm_models.all_llm import llm

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


# 2. 定义远程 MCP 服务（天气查询，需先启动 weather_server.py）
weather_server_config = {
    "url": "http://localhost:8000/sse",
    "transport": "sse"
}


prompt = ChatPromptTemplate.from_messages([
    ('system', '你是一个智能助手，尽可能的调用工具回答用户的问题'),
    MessagesPlaceholder(variable_name='chat_history', optional=True),
    ('human', '{input}'),
    MessagesPlaceholder(variable_name='agent_scratchpad', optional=True),
])

async def main():
    async with MultiServerMCPClient({
        "weather": weather_server_config
    }) as client:
        tools = client.get_tools()
        # agent = create_react_agent(llm, client.get_tools())
        agent = create_tool_calling_agent(llm, tools, prompt)
        executor = AgentExecutor(agent=agent, tools=tools)
        # 调用数学工具
        response1 = await executor.ainvoke({"input": "计算 2 和 4的乘积"})
        print(response1)
        response2 = await executor.ainvoke({"input": "计算 6+19的结果"})
        print(response2)
        response3 = await executor.ainvoke({"input": "今天，北京的天气怎么样？"})
        print(response3)


if __name__ == "__main__":
    asyncio.run(main())
