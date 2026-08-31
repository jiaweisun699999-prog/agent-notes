"""
 优雅处理工具调用错误
"""
import requests
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.prebuilt.tool_node import ToolCallRequest

from init_llm import deepseek_llm


@tool
def get_stock_price(symbol: str) -> str:
    """
    获取指定股票代码的当前价格
    Arg:
        symbol: 股票代码（例如：TCEHY）
    Returns:
        股票当前价格（例如："股票 TCEHY 当前价格为 123.45"）
    """
    print(f"=====调用股票查询工具: {symbol}")
    try:
        # 模拟可能失败的API调用
        response = requests.get(f"https://api.xxx.com/stocks/{symbol}", timeout=1)
        return f"股票 {symbol} 当前价格为 {response['price']}"
    except requests.exceptions.RequestException as e:
        print(f"=====查询股票数据失败: {str(e)}")
        raise Exception(f"查询股票数据失败: {str(e)}")


@wrap_tool_call
def handle_tool_call_error(request:ToolCallRequest ,handler):
    print("request",request)

    # 介入错误处理
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(
            content=f"当前股票查询服务不可用，错误信息: {str(e)}",
            tool_call_id=request.tool_call["id"]
        )


agent = create_agent(
    model=deepseek_llm,
    tools=[get_stock_price],
    middleware=[handle_tool_call_error]
)

result = agent.invoke({"messages":[{"role":"user","content":"查询TCEHY的股票价格"}]})

print("result",result)

print(result["messages"][-1].content)



