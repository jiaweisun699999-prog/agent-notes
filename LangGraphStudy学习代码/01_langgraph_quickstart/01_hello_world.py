
"""
构建简单的Graph 图/工作流：
    一个节点（大模型节点）、两条边（连接起来整个流程）
    节点：对应的就是python函数


    1. 构建图/工作流 必须创建 graph_builder=StateGraph()，然后必须编译 graph = graph_builder.compile()后再invoke
    2. 图/工作流中要保存一些状态，所以必须定义一个状态类 MessagesState：graph_builder=StateGraph(MessagesState)
    3. 节点：对应的就是python函数，节点之间通过边连接起来，节点参数必须有 MessagesState，节点返回数据往往更新的是 MessagesState 中的 messages 字段
    4. MessagesState 是 LangGraph中默认的State，用户还可以自定义其他State，后续再学习
    5. add_node：添加节点，参数为节点名称和节点函数；add_edge：添加边，参数为源节点和目标节点
    6. 用户传入的消息必须符合 MessagesState 中定义的字段，否则会报错
    7. 用户提问可以使用 HumanMessage 或者 {"role":"user","content":"你好，请一句话介绍自己"} 格式传入

"""
from langgraph.constants import START, END
from langgraph.graph import StateGraph, MessagesState

from init_llm import deepseek_llm


# 定义LLM 节点：调用LLM 返回相应
# 节点参数必须有 MessagesState，节点返回数据往往更新的是 MessagesState 中的 messages 字段
def call_model(state: MessagesState):
    """获取用户输入消息，进行回复"""
    response = deepseek_llm.invoke(state["messages"])
    return {"messages": [response]}


# 创建Graph 图/工作流
graph_builder=StateGraph(MessagesState)

# 给图/工作流添加节点
graph_builder.add_node("call_model",call_model)

# 给图/工作流添加边
# 从START节点到call_model节点
graph_builder.add_edge(START, "call_model")
# 从call_model节点到END节点
graph_builder.add_edge("call_model", END)


# 编译Graph 图/工作流，才可以进行invoke调用
graph = graph_builder.compile()


# 调用Graph 图/工作流
# result = graph.invoke({"messages":[HumanMessage(content="你好，请一句话介绍自己")]})


result = graph.invoke({"messages":[{"role":"user","content":"你好，请一句话介绍自己"}]})


print("result:",result)

for msg in result["messages"]:
    msg.pretty_print()
