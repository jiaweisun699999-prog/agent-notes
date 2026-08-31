"""
路由
业务：电商业务处理助手：对于用户输入的问题，根据问题的类型，路由到不同的处理流程
"""
from typing import Literal, TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph
from pydantic import BaseModel, Field

from init_llm import deepseek_llm

class RouteResult(BaseModel):
    category:Literal["refund","technical","general"] = Field(description="用户问题的类型")

router = deepseek_llm.with_structured_output(RouteResult)

# 1. 定义状态
class RouteState(TypedDict):
    input:str # 用户输入的问题
    category:str # 用户问题的类型
    response:str # 回复内容


#2. 定义节点
def classify(state: RouteState)->dict:
    "分类用户问题的类型"
    msg = router.invoke(f"将用户的请求分类为：refund（退款）,technical（技术问题）,general（一般问题）：{state["input"]}")
    return {"category":msg.category}


def handle_general(state: RouteState)->dict:
    "处理一般问题"
    msg = deepseek_llm.invoke(f"请根据用户问题{state["input"]}，请以客服的身份做一般性回复")
    return {"response":msg.content}


def handle_refund(state: RouteState)->dict:
    "处理退款问题"
    msg = deepseek_llm.invoke(f"请根据用户问题{state["input"]}，请以客服的身份做退款回复")
    return {"response":msg.content}

def handle_technical(state: RouteState)->dict:
    "处理技术问题"
    msg = deepseek_llm.invoke(f"请根据用户问题{state["input"]}，请以客服的身份做技术回复")
    return {"response":msg.content}

# 定义条件边
def route_by_category(state: RouteState)->str:
    "根据用户问题的类型，路由到不同的处理流程"
    category = state["category"]

    if category == "refund":
        return "refund"
    elif category == "technical":
        return "technical"
    else:
        return "general"



#3.构建Graph
graph_builder = StateGraph(RouteState)

#添加节点
graph_builder.add_node("classify", classify)
graph_builder.add_node("handle_general", handle_general)
graph_builder.add_node("handle_refund", handle_refund)
graph_builder.add_node("handle_technical", handle_technical)

#添加边
graph_builder.add_edge(START, "classify")
graph_builder.add_conditional_edges("classify", route_by_category, {"refund": "handle_refund", "technical": "handle_technical", "general": "handle_general"})
graph_builder.add_edge("handle_general", END)
graph_builder.add_edge("handle_technical", END)
graph_builder.add_edge("handle_refund", END)

graph = graph_builder.compile()

# 输出Graph 图/工作流为 PNG
png_data = graph.get_graph().draw_mermaid_png()
with open("routing.png", "wb") as f:
    f.write(png_data)
print("图片已保存到 routing.png")


result1 = graph.invoke({"input":"我的商品被重复扣款，请帮我退款"})
print(result1["response"])
print("="*20)

result2 = graph.invoke({"input":"你们的app在华为手机上不兼容，怎么处理？"})
print(result2["response"])
print("="*20)

result3 = graph.invoke({"input":"你们周六日上班吗？"})
print(result3["response"])
print("="*20)


