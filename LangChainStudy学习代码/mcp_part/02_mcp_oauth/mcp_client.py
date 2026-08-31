import asyncio
from email import header

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from init_llm import deepseek_llm

# 获取 JWT Token
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJteV9hZ2VudCIsImlzcyI6Im15X2NvbXBhbnlfYXV0aF9zZXJ2ZXIiLCJpYXQiOjE3ODQwODY2NTksImV4cCI6MTc4NDA5MDI1OSwiYXVkIjoiaW50ZXJuYWxfbWNwX3NlcnZlciJ9.xv67OBceNUia01vkm8OTB7YlMkKAXz69fOH3tKxs6NVoshial9xYKUBmUlgD9rRNs4pG5H1eQ0y8r3uv5cZ4YDEPOD1TbwBjxKTcZA-8F8sbOuLxF_7uZXlTp9f_UtAkij-ko2qSz5KX9yqgjYwukIHZf9bN1kGK9p3mrE1ppOPMfz0qRlEFCePw-D4J3Olu3Mn2tHupeqYo-l-InvjucELWqth-xrrU1xbVntbTlhZLxnQeENBKCT9nnzk_z7_VNOG-HKCNqWXyWLjyALTrdtGCHUjoq10EsCtzyHqFxE1zgAdr3vnPMM_6MaBHStAzOla3j-r_uQqUblBoB-RMmA"

async def main():
    # 创建client
    client = MultiServerMCPClient(
        {
            "internal_mcp_server":{
                "transport":"http",
                "url":"http://localhost:8000/mcp",
                # 将token添加到headers中
                "headers":{
                    "Authorization":"Bearer "+token
                }
            }
        }
    )


    tools = await client.get_tools()


    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
    )

    result1 = await agent.ainvoke({"messages":[{"role":"user","content":"查询一下E002员工信息"}]})
    print(result1["messages"][-1].content)

    result2 = await agent.ainvoke({"messages": [{"role": "user", "content": "查询一下财务部的预算"}]})
    print(result2["messages"][-1].content)


if __name__ == '__main__':
    asyncio.run(main())


