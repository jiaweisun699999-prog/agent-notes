"""
Graph 图/工作流：计算器演示
"""
import operator
from typing import TypedDict, Annotated, Literal

from langchain_core.messages import AnyMessage, SystemMessage, ToolMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.constants import START, END
from langgraph.graph import StateGraph, add_messages

from init_llm import deepseek_llm


#============ 1. 定义工具 ===========

@tool
def add(a: int, b: int) -> int:
    """两个整数相加，参数为a和b，返回a+b的结果"""
    return a + b

@tool
def sub(a: int, b: int) -> int:
    """两个整数相减，参数为a和b，返回a-b的结果"""
    return a - b

@tool
def mul(a: int, b: int) -> int:
    """两个整数相乘，参数为a和b，返回a*b的结果"""
    return a * b

@tool
def div(a:int ,b:int) ->int:
    """两个整数相除，参数为a和b，返回a/b的结果"""
    return a/b


tools = [add,sub,mul,div]

# {"add":add,"sub":sub,"mul":mul,"div":div}
tools_by_name = {tool.name:tool for tool in tools}

model_with_tools = deepseek_llm.bind_tools(tools)


#================2. 定义状态 ======================
class CalculatorState(TypedDict):
    """计算器状态"""
    # messages: Annotated[list[AnyMessage], operator.add]
    messages: Annotated[list[AnyMessage], add_messages]


#=================3. 定义节点 ======================
def llm_call(state: CalculatorState)->dict:
    """调用LLM返回相应"""
    response = model_with_tools.invoke(
        [SystemMessage(content="你是一个数学计算助手，请使用工具完成计算并给出答案")]+state['messages']
    )

    return {"messages": [response]}


def tool_node(state: CalculatorState)->dict:
    """调用工具节点"""
    last_msg = state["messages"][-1]
    results = []
    for tool_call in last_msg.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool = tools_by_name[tool_name]
        result = tool.invoke(tool_args)
        results.append(ToolMessage(content=result,tool_call_id=tool_call["id"]))

    return {"messages": results}

#=== 定义条件边 ======================
def should_continue(state: CalculatorState)-> Literal["tool_node",END]:
    """判断是否继续调用工具节点还是直接返回结果"""
    last_msg = state["messages"][-1]
    # 检查是否有工具调用
    if last_msg.tool_calls:
        return "tool_node"

    return END


#============ 4. 创建图/工作流 ===========
graph_builder=StateGraph(CalculatorState)

#添加节点
graph_builder.add_node("llm_call",llm_call)
graph_builder.add_node("tool_node",tool_node)

#添加边
graph_builder.add_edge(START, "llm_call")
graph_builder.add_conditional_edges("llm_call", should_continue,["tool_node",END])
graph_builder.add_edge("tool_node", "llm_call")


agent = graph_builder.compile()

#============ 5. 调用图/工作流 ===========

# result = agent.invoke({"messages":[HumanMessage(content="帮我计算 （3+5）*2 的结果")]})

result = agent.invoke({"messages":[{"role":"user","content":"帮我计算 （3+5）*2 的结果"}]})

print("result:",result)

for msg in result["messages"]:
    msg.pretty_print()






