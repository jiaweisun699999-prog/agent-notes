"""
拦截器上下文注入示例
"""
import asyncio
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest

from init_llm import deepseek_llm

@dataclass
class CustomerContext:
    user_id:str #用户id
    user_name:str #用户姓名
    token:str # 用户token


#定义拦截器
async def auth_inject_interceptor(request:MCPToolCallRequest,handler):
    "将用户id参数传入给工具"

    runtime = request.runtime
    ctx = runtime.context

    # 增加调用工具的参数
    modified_request = request.override(
        # 将原来的参数拿过来，然后增加 caller_id参数
        args={**request.args, "caller_id": ctx.user_id},
        # 设置 请求头，携带token
        headers={"Authorization": f"Bearer {ctx.token}"}
    )

    return await handler(modified_request)




async def main():
    client = MultiServerMCPClient(
        {
            "my_match_server": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        },
        # 传入拦截器列表
        tool_interceptors=[auth_inject_interceptor]
    )

    tools = await client.get_tools()

    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        context_schema=CustomerContext,
        system_prompt="你是一个助手"
    )

    result = await agent.ainvoke(
        {"messages":[{"role":"user","content":"查询订单 ORD-001 信息"}]},
        context=CustomerContext(user_id="uid_zhangsan",user_name="张三",token="tk-123456")
    )

    print(result["messages"][-1].content)

    result2 = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "订单ORD-003 退款"}]},
        context=CustomerContext(user_id="uid_lisi", user_name="李四", token="tk-123456")
    )

    print(result2["messages"][-1].content)


if __name__ == '__main__':
    asyncio.run(main())