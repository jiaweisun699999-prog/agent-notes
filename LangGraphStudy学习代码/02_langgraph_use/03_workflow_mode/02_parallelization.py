"""
并行化
业务：商品评论多维分析：情感分析、关键词提取、检查是否是垃圾评论，最后聚合结果输出评论分析报告
"""
from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph

from init_llm import deepseek_llm


# 1. 构建状态
class ReviewAnalysisState(TypedDict):
    review: str # 商品评论
    sentiment: str # 情感分析结果
    keywords: str # 关键词提取结果
    spam_check: str # 垃圾评论检查结果
    report:str # 分析报告

#2. 定义节点

def analyze_sentiment(state: ReviewAnalysisState)->dict:
    "并行任务1：情感分析"
    msg = deepseek_llm.invoke(f"请对这条评论进行情感分析，只输出情感倾向（正面、负面、中性），并一句话总结：{state["review"]}")
    return {"sentiment":msg.content}


def check_spam(state: ReviewAnalysisState)->dict:
    "并行任务2：检查是否是垃圾评论"
    msg = deepseek_llm.invoke(f"请对这条评论进行垃圾评论检查，输出检查结果（是垃圾评论/不是垃圾评论）,并输出检查原因：{state["review"]}")
    return {"spam_check":msg.content}


def extract_keywords(state: ReviewAnalysisState)->dict:
    "并行任务3：关键词提取"
    msg = deepseek_llm.invoke(f"请对这条评论进行关键词提取，输出关键词本身即可，多个关键词之间用逗号隔开：{state["review"]}")
    return {"keywords":msg.content}


def aggregate(state: ReviewAnalysisState)->dict:
    "任务：聚合结果"
    report = (
        f"[评论分析报告：]\n"
        f"原文：{state["review"]}\n"
        f"情感分析：{state["sentiment"]}\n"
        f"关键词提取：{state["keywords"]}\n"
        f"垃圾评论检查：{state["spam_check"]}"
    )

    return {"report":report}


# 3.创建Graph
graph_builder = StateGraph(ReviewAnalysisState)

# 添加节点
graph_builder.add_node("analyze_sentiment", analyze_sentiment)
graph_builder.add_node("check_spam", check_spam)
graph_builder.add_node("extract_keywords", extract_keywords)
graph_builder.add_node("aggregate", aggregate)

# 添加边
graph_builder.add_edge(START, "analyze_sentiment")
graph_builder.add_edge(START, "check_spam")
graph_builder.add_edge(START, "extract_keywords")

graph_builder.add_edge("analyze_sentiment", "aggregate")
graph_builder.add_edge("check_spam", "aggregate")
graph_builder.add_edge("extract_keywords", "aggregate")

graph_builder.add_edge("aggregate", END)

graph = graph_builder.compile()

# 输出Graph 图/工作流为 PNG
png_data = graph.get_graph().draw_mermaid_png()
with open("parallelization.png", "wb") as f:
    f.write(png_data)
print("图片已保存到 parallelization.png")



result = graph.invoke({"review":"这个耳机音质非常好，降噪效果也是顶流，就是耳机戴久了有点夹耳朵，总体还是很满意的。"})

print(result["report"])


