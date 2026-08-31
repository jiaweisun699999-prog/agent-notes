"""
编排者-工作者：
业务：生成产品公告，首先规划公告的章节，然后并行动态的生成每个章节内容，最终合并成一个完整的公告。
"""
import operator
from typing import List, TypedDict, Annotated

from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.types import Send
from pydantic import BaseModel, Field

from init_llm import deepseek_llm

# 1. 构建大模型结构化输出内容
class Section(BaseModel):
    "公告章节"
    name:str = Field(description="章节名称")
    description:str = Field(description="该章节要覆盖的内容要点")


class Sections(BaseModel):
    "公告章节列表"
    sections:list[Section]


planner = deepseek_llm.with_structured_output(Sections)


#2.构建状态
class State(TypedDict):
    topic:str # 公告主题
    sections:list[Section] # 公告章节列表
    completed_sections:Annotated[list[str],operator.add] # 已完成的章节列表
    final_report:str # 最终公告

class WorkerState(TypedDict):
    section:Section


#3. 定义节点
def orchestrator(state: State)->dict:
    "根据用户输入的公告主题，规划公告的章节"
    msg = planner.invoke(f"为产品发布公告规划章节结构，3个章节以内。公告主题：{state['topic']}")
    return {"sections":msg.sections}


def write_section(worker_state: WorkerState)->dict:
    "编写当前章节的内容"
    section = worker_state["section"]
    name = section.name
    description = section.description
    msg = deepseek_llm.invoke(f"按照给定章节的名称和要点来给我编写公告章节内容，使用MD格式，100字以内。章节名字：{name},章节要点：{description}")
    return {"completed_sections":[msg.content]}


def synthesizer(state: State)->dict:
    "合并所有章节内容，生成最终公告"
    final_report = "\n\n ------ \n\n".join(state["completed_sections"])
    return {"final_report":final_report}



#构建条件边
def assign_workers(state: State):
    "根据当前章节个数来动态的分配工作者"
    # workes = []
    # for current_section in state["sections"]:
    #     workes.append(Send("write_section",{"section":current_section}))
    #
    # return workes

    return [Send("write_section",{"section":current_section}) for current_section in state["sections"]]



# 4.构建Graph工作流
graph_builder = StateGraph(State)
# 添加节点
graph_builder.add_node("orchestrator", orchestrator)
graph_builder.add_node("write_section", write_section)
graph_builder.add_node("synthesizer", synthesizer)


# 添加边
graph_builder.add_edge(START, "orchestrator")
graph_builder.add_conditional_edges("orchestrator", assign_workers, ["write_section"])
graph_builder.add_edge("write_section", "synthesizer")
graph_builder.add_edge("synthesizer", END)

graph = graph_builder.compile()

# 输出Graph 图/工作流为 PNG
png_data = graph.get_graph().draw_mermaid_png()
with open("orchestrator_worker.png", "wb") as f:
    f.write(png_data)
print("图片已保存到 orchestrator_worker.png")

result = graph.invoke({"topic":"华为手机 P70发布"})

print(result["final_report"])

