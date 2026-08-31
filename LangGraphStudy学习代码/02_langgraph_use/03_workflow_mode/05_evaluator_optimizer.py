"""
评估优化器
业务：生成产品的文案，然后判断文案是否满足要求，不满足继续生成，当重复生成文案3次/满足要求，接受文案
"""
from typing import TypedDict, Literal

from langgraph.constants import START, END
from langgraph.graph import StateGraph
from pydantic import BaseModel, Field

from init_llm import deepseek_llm, deepseek_llm_flash

class ReviewResult(BaseModel):
    grade:Literal["pass","fail"] = Field(description="文案是否达标，pass=达标，fail=不达标")
    feedback:str  = Field(description="不达标时具体的修改建议，达标时返回空字符串")

evaluator = deepseek_llm_flash.with_structured_output(ReviewResult)

# 1. 状态
class TextState(TypedDict):
    product:str #产品名称
    draft:str #当前文案
    grade:str # 评估结论（pass /fail)
    feedback:str #修改建议
    iteration:int #迭代次数

# 2.定义节点
def generate_text(text_state:TextState)->dict:
    "生成产品文案，如果有修改建议，根据建议进行修改"
    iteration = text_state.get("iteration",0) +1

    if text_state.get("feedback"):
        prompt = f"请为产品{text_state['product']}写一条公告，字数30字以内，根据修改建议{text_state['feedback']}，修改当前文案{text_state['draft']}，字数30字以内，要求简洁有力、突出卖点"
    else:
        prompt = f"请为产品{text_state['product']}写一条公告，字数30字以内，要求简洁有力、突出卖点"

    msg = deepseek_llm.invoke(prompt)

    return {"iteration":iteration,"draft":msg.content}


def review_text(text_state:TextState)->dict:
    "评估文案是否满足要求"
    evalresult = evaluator.invoke(f"""请评估这段营销文案是否达标。评估标注：30字以内、简洁有力、突出卖点、有感染力。文案：{text_state["draft"]}""")

    return {"grade":evalresult.grade,"feedback":evalresult.feedback}


#定义路由函数
def route_review(text_state: TextState) -> str:
    "根据评估结果判断是否继续生成文案"
    if text_state["grade"] == "pass":
        return END
    elif text_state.get("iteration",0) >= 3:
        return END
    else:
        return "generate_text"


# 3. 定义工作流
graph_builder = StateGraph(TextState)
graph_builder.add_node("generate_text",generate_text)
graph_builder.add_node("review_text",review_text)

#添加边
graph_builder.add_edge(START,"generate_text")
graph_builder.add_edge("generate_text","review_text")
graph_builder.add_conditional_edges("review_text",route_review,["generate_text",END])

graph = graph_builder.compile()

# 输出Graph 图/工作流为 PNG
png_data = graph.get_graph().draw_mermaid_png()
with open("evaluator_optimizer.png", "wb") as f:
    f.write(png_data)
print("图片已保存到 evaluator_optimizer.png")

result = graph.invoke({"product":"智能手表"})
print("result:",result)
print(result["draft"])
