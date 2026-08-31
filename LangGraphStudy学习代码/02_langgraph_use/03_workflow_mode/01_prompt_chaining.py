
"""
提示链:用户输入产品生成文案，如果文案大于等于40字符，直接输出文案，如果文案小于40字符，那么扩写文案，然后再润色，最后输出文案
"""
from typing import TypedDict

from langgraph.constants import START, END
from langgraph.graph import StateGraph

from init_llm import deepseek_llm


#1. 定义状态
class CopywritingState(TypedDict):
    product: str # 产品名称
    draft:str # 初稿文案
    expanded:str # 扩写文案
    final:str # 最终文案



#2. 定义节点
def generate_draft(state: CopywritingState)->dict:
    "生成初稿文案"
    msg = deepseek_llm.invoke(f"为产品{state["product"]}写一句营销文案，只输出文案本身即可")
    return {"draft":msg.content}


def expand_draft(state: CopywritingState)->dict:
    "扩写文案"
    msg = deepseek_llm.invoke(f"请将这句文案扩写到60字，扩充产品卖点和使用场景：{state["draft"]}")
    return {"expanded":msg.content}


def polish_draft(state: CopywritingState)->dict:
    "润色文案"
    msg = deepseek_llm.invoke(f"请将这句文案润色,使其更具感染力，保持60字左右：{state["expanded"]}")
    return {"final": msg.content}


#3.定义条件边
def check_length(state: CopywritingState)->str:
    "检查文案长度"
    if len(state["draft"]) >= 40:
        return "Pass"
    else:
        return "Fail"


# 构建Graph
graph_builder = StateGraph(CopywritingState)
# 添加节点
graph_builder.add_node("generate_draft", generate_draft)
graph_builder.add_node("expand_draft", expand_draft)
graph_builder.add_node("polish_draft", polish_draft)


# 添加条件边
graph_builder.add_edge(START, "generate_draft")
graph_builder.add_conditional_edges("generate_draft", check_length, {"Pass": END, "Fail": "expand_draft"})
graph_builder.add_edge("expand_draft", "polish_draft")
graph_builder.add_edge("polish_draft", END)

graph = graph_builder.compile()


# 输出Graph 图/工作流为 PNG
png_data = graph.get_graph().draw_mermaid_png()
with open("copywriting_graph.png", "wb") as f:
    f.write(png_data)
print("图片已保存到 copywriting_graph.png")

result = graph.invoke({
    "product": "蓝牙降噪耳机",
})

print("result:",result)

print(result["final"])


