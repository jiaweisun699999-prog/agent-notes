
"""
股票分析助手
1. 从MCP Server 获取股票分析方法论、当前股票市场概览 作为提示词设置在系统提示词中
2. 获取生成分析报告的提示词，也要设置在系统提示词中
3. 调用MCP Server 的工具进行数据查询
"""
import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from init_llm import deepseek_llm


async def main():
    client = MultiServerMCPClient(
        {
            "my_stock_server": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )


    #1. 获取股票分析方法论和当前股票市场概览
    blobs = await client.get_resources("my_stock_server",uris=["research://methodology","market://overview"])

    context = ""
    for blob in blobs:
        # print("metadata",blob.metadata)
        # print("mimetype",blob.mimetype)
        # print("data",blob.as_string())
        context += blob.as_string() + "\n\n"

    #2.获取提示词模版
    msg = await client.get_prompt("my_stock_server","analyze_report",arguments={"stock_name":"目标股票"})
    prompt = msg[0].content


    #3.准备系统提示词
    system_prompt = f"""
        你是一个股票分析助手，请遵循如下方法论进行股票分析：
        {context}
        
        输出分析报告时，请按照如下格式：
        {prompt}

        """

    # 4.获取工具
    tools = await client.get_tools()

    # 5.创建智能体
    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        system_prompt=system_prompt,
    )

    # 6.调用智能体
    result = await agent.ainvoke({"messages":[{"role":"user","content":"帮我分析特斯拉的股票，然后做一个分析报告"}]})
    print("result:",result)

    print(result["messages"][-1].content)



if __name__ == '__main__':
    asyncio.run(main())




