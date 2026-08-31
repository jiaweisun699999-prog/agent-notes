from typing import TypedDict, Literal

from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.types import Command
from pydantic import BaseModel, Field

from init_llm import deepseek_llm

#======定义大模型返回的结构化输出 ======
class EmailClassification(BaseModel):
    """邮件分类结果"""
    category: Literal["question","bug","billing","other"]  = Field(description="邮件类别")# 邮件分类
    urgency: Literal["low","medium","high"] = Field(description="邮件紧急程度")
    summary:str = Field(description="邮件摘要")



# ===== 定义状态 =====
class EmialState(TypedDict):
    """邮件处理中的状态"""
    sender: str # 邮件发送者
    email_content: str # 邮件内容
    classification: dict # 邮件分类结果
    search_results: list[str] # 搜索结果
    email_response:str # 邮件回复内容


classifier = deepseek_llm.with_structured_output(EmailClassification)

#====== 定义节点 ======
def classify_email(state: EmialState):
    "邮件分类，大模型进行意图识别进行邮件分类"
    result = classifier.invoke(f"""
        分析一下客户邮件，给出邮件类别、邮件紧急程度、邮件摘要：
        发件人：{state["sender"]}
        邮件内容：{state["email_content"]}
        """)

    # 将result转换为字典
    classification = result.model_dump()

    return {"classification":classification}



def classify_email_conditional(state: EmialState) -> str:
    "根据邮件紧急程度判断是否需要人工审核"
    urgency = state["classification"]["urgency"]
    if urgency == "high":
        return "email_reply"
    return "search_info"


def search_info(state: EmialState) -> dict:
    "根据邮件分类，搜索相关文档"
    category = state["classification"]["category"]

    # "question","bug","billing","other"
    data = {
        "question":["忘记密码请进入设置找到安全输入账号和绑定的手机号进行密码重置"],
        "bug":["请描述一下你遇到的问题，我们会尽快修复"],
        "billing":["退款政策：7天内可以申请退款，退款金额为订单金额的80%。"],
        "other":["请联系我们，我们会尽快处理"],
    }

    results = data.get(category,["没有找到相关文档"])

    return {"search_results": results}


def email_reply(state: EmialState) -> dict:
    "根据搜索结果，生成邮件回复"
    #原始邮件
    email_content = state["email_content"]
    #邮件分类
    category = state["classification"]["category"]
    #邮件紧急程序
    urgency = state["classification"]["urgency"]
    #知识库参考
    search_results = state.get("search_results",[])
    knowledge = "\n".join(search_results)

    #AIMessage对象
    response = deepseek_llm.invoke(f"""
        你是专业的邮件编写助手，根据如下内容来给我草拟回复邮件：
        原始邮件：{email_content}
        分类：{category}
        紧急程度：{urgency}
        知识库参考：{knowledge}
        生成的回复邮件要求：语气专业，友好。
    """)

    return {"email_response":response.content}

def email_reply_conditional(state: EmialState) -> str:
    "根据邮件紧急程度判断是否需要人工审核"
    urgency = state["classification"]["urgency"]

    if urgency == "high":
        return "review"

    return END


def review_email_reply(state: EmialState)->dict:
    "模拟人工审核"
    return {"email_response":state["email_response"]+"[此内容已经通过人员审核，符合要求]"}




##===== 构建 graph =====
graph_builder = StateGraph(EmialState)

# 添加节点
graph_builder.add_node("classify_email",classify_email)
graph_builder.add_node("search_info",search_info)
graph_builder.add_node("email_reply",email_reply)
graph_builder.add_node("review",review_email_reply)

#添加边
graph_builder.add_edge(START,"classify_email")
graph_builder.add_conditional_edges("classify_email",classify_email_conditional,["search_info","email_reply"])
graph_builder.add_edge("search_info","email_reply")
graph_builder.add_conditional_edges("email_reply",email_reply_conditional,["review",END])
graph_builder.add_edge("review",END)

graph = graph_builder.compile()


# 绘制 Mermaid 图
# print(graph.get_graph().draw_ascii()) # 打印 ASCII 图

# 保存 Mermaid 图为 PNG
png_data = graph.get_graph().draw_mermaid_png()

# wb表示二进制写入模式
with open("email_graph.png", "wb") as f:
    f.write(png_data)
print("图片已保存到 email_graph.png")


# ====== 使用 graph ======
result1 = graph.invoke({
    "sender": "user@example.com",
    "email_content": "非紧急问题：我的账号密码错误了，我应该怎么处理？",
})

print(result1["email_response"])

print("*"*20)


result2 = graph.invoke({
    "sender": "user@example.com",
    "email_content": "紧急问题：我的订单中的商品损坏了，我要退款，怎么操作？",
})
print(result2["email_response"])
