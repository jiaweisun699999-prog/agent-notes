"""
Functional API 计算器 Agent
使用 @entrypoint + @task 构建带工具调用的 Agent。
"""

from langchain.tools import tool
from langchain.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.messages import BaseMessage
from langgraph.func import entrypoint, task
from langgraph.graph import add_messages

from init_llm import deepseek_llm


# 1. 定义工具
@tool
def add(a: int, b: int) -> int:
    """两个整数相加"""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """两个整数相乘"""
    return a * b


@tool
def divide(a: int, b: int) -> float:
    """两个整数相除"""
    return a / b


tools = [add, multiply, divide]
tools_by_name = {t.name: t for t in tools}
model_with_tools = deepseek_llm.bind_tools(tools)

# 2. 定义 @task 装饰的任务函数
@task
def call_model(messages: list[BaseMessage]) -> BaseMessage:
    """调用 LLM，返回响应消息"""
    return model_with_tools.invoke(
        [SystemMessage(content="你是一个数学计算助手。请使用工具完成计算并给出最终答案。")]
        + messages
    )


@task
def execute_tool(tool_call: dict) -> ToolMessage:
    """执行单个工具调用"""
    tool = tools_by_name[tool_call["name"]]
    result = tool.invoke(tool_call["args"])
    return ToolMessage(content=str(result), tool_call_id=tool_call["id"])


# 3. 定义 @entrypoint 入口函数（Agent 主循环）
@entrypoint()
def calculator_agent(messages: list[BaseMessage]) -> list[BaseMessage]:
    """计算器 Agent：在 while 循环中反复执行 LLM→工具→LLM"""
    response = call_model(messages).result()
    print("type(response):",type(response))
    print("response:",response)

    while True:
        if not response.tool_calls:
            # 没有工具调用:最终答案，退出循环
            break

        # 并行执行所有工具调用
        tool_futures = [execute_tool(tc) for tc in response.tool_calls]
        tool_results = [f.result() for f in tool_futures]

        # 用 add_messages 合并消息列表，自动处理追加语义
        messages = add_messages(messages, [response] + tool_results)
        response = call_model(messages).result()

    # add_messages: 合并最终答案
    return add_messages(messages, response)


# 4. 运行
if __name__ == "__main__":
    final_messages = calculator_agent.invoke([HumanMessage(content="请帮我算一下：100 除以 4 再乘以 3 的结果是多少？")])
    print("--- 完整对话记录 ---")
    for msg in final_messages:
        msg.pretty_print()
