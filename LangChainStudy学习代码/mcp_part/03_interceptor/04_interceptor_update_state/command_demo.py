"""
通过拦截器修改状态（调用工具时间），如果遇到退款工具就直接跳转到 end 节点
"""
import asyncio
import time

from langchain.agents import create_agent, AgentState
from langchain_core.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langgraph.types import Command

from init_llm import deepseek_llm


class CustomState(AgentState):
    last_op_time:str # 最后操作时间


#定义拦截器
async def refund_control_interceptor(request:MCPToolCallRequest,handler):
    "每次工具调用拦截器最后返回Command，都会记录工具调用时间，如果遇到退款工具，直接跳转到 end 节点"
    result = await handler(request)

    tool_msg = ToolMessage(
        content=result.content[0].text,
        tool_call_id=request.runtime.tool_call_id
    )

    if request.name == "process_refund":
        return Command(
            update={
                "last_op_time": time.strftime("%H:%M:%S"),
                "messages":[tool_msg]
            },
            goto="__end__"
        )

    return Command(
        update={
            "last_op_time": time.strftime("%H:%M:%S"),
            "messages": [tool_msg]
        }
    )




async def main():

    client = MultiServerMCPClient(
        {
            "my_server": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        },
        # 传入拦截器列表
        tool_interceptors=[refund_control_interceptor]
    )

    tools = await client.get_tools()

    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        state_schema=CustomState,
        system_prompt="你是电商售后助手"
    )

    result1 = await agent.ainvoke({"messages":[{"role":"user","content":"给我查询订单ORD-001的状态"}]})

    print("result1",result1)
    print(result1["messages"][-1].content)
    print("最后操作时间:",result1.get("last_op_time"))


    print("-----------------")

    result2 = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "ORD-002给我退款"}]},
    )
    print("result2",result2)
    print(result2["messages"][-1].content)
    print("最后操作时间:",result2.get("last_op_time"))


if __name__ == '__main__':
    asyncio.run(main())
