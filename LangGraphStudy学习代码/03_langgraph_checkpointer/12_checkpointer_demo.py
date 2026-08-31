import operator
from typing import TypedDict, Annotated

from langchain_core.messages import content, SystemMessage, HumanMessage, AIMessage
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph

from init_llm import deepseek_llm


# 1.定义状态
class ServiceState(TypedDict):
    messages: Annotated[list[str],operator.add]
    user_input:str
    intent:str # 用户意图,refund(退款）/tech(技术问题)/consult(咨询)/feedback(反馈)
    department:str #路由到的部门
    response:str # 生成回复

# 2. 定义节点
def check_intent(state: ServiceState):
    """检查用户意图"""
    prompt = SystemMessage(content=(
        "你是一个客服意图识别助手。分析用户消息，判断意图属于以下哪一种：\n"
        "- refund: 退款、退货、赔偿相关问题\n"
        "- tech: 产品使用故障、技术问题\n"
        "- consult: 产品咨询、业务询问\n"
        "- feedback: 投诉、建议、意见反馈\n"
        "只回复一个单词：refund / tech / consult / feedback"
    ))

    user_input = state["user_input"]
    response = deepseek_llm.invoke([prompt,HumanMessage(content=user_input)])

    intent = response.content

    return {
        "messages": [AIMessage(content=f"[意图识别] 用户输入：{user_input} ,意图识别为：{intent}")],
        "intent": intent
    }

def handle_refund(state: ServiceState):
    """处理退款意图"""
    prompt =  SystemMessage(content=(
        "你是退款客服专员。用户想退款或投诉账单问题，请礼貌地了解具体情况，"
        "并告知退款流程："
        "   1)核实订单 "
        "   2)提交退款申请 "
        "   3)3-5个工作日到账。"
        "回复控制在80字以内。"
    ))

    user_input = state["user_input"]

    response = deepseek_llm.invoke([prompt, HumanMessage(content=user_input)])

    return {
        "department": "退款部门",
        "response": response.content,
        "messages": [AIMessage(content=f"[路由-退款] 已转到退款部门，回复内容：{response.content}")]
    }


def handle_tech(state: ServiceState):
    """处理技术问题意图"""
    prompt = SystemMessage(content=(
            "你是技术支持工程师。用户遇到了产品使用问题，请先表示理解，"
            "然后给出排查步骤："
            "   1)确认问题现象 "
            "   2)尝试基础排查（重启/更新）"
            "   3)如无法解决则升级到高级工程师。"
            "回复控制在80字以内。"
        ))

    user_input = state["user_input"]

    response = deepseek_llm.invoke([prompt, HumanMessage(content=user_input)])

    return {
        "department": "技术部门",
        "response": response.content,
        "messages": [AIMessage(content=f"[路由-技术问题] 已转到技术部门，回复内容：{response.content}")]
    }

def handle_consult(state: ServiceState):
    """处理咨询意图"""
    prompt = SystemMessage(content=(
            "你是业务咨询顾问。用户想了解产品信息，请热情、专业地回答问题。"
            "如果不确定具体细节，请引导用户联系人工客服或查看官网帮助中心。"
            "回复控制在80字以内。"
        ))

    user_input = state["user_input"]

    response = deepseek_llm.invoke([prompt, HumanMessage(content=user_input)])

    return {
        "department": "咨询部门",
        "response": response.content,
        "messages": [AIMessage(content=f"[路由-咨询] 已转到咨询部门，回复内容：{response.content}")]
    }

def handle_feedback(state: ServiceState):
    """处理反馈意图"""
    prompt = SystemMessage(content=(
            "你是客户关系专员。用户提出了投诉或建议，请真诚道歉或感谢，"
            "并告知已记录反馈、会尽快改进。对于投诉承诺24小时内由主管回访。"
            "回复控制在80字以内。"
        ))

    user_input = state["user_input"]

    response = deepseek_llm.invoke([prompt, HumanMessage(content=user_input)])

    return {
        "department": "反馈部门",
        "response": response.content,
        "messages": [AIMessage(content=f"[路由-反馈] 已转到反馈部门，回复内容：{response.content}")]
    }

def summarize(state: ServiceState):
    """总结对话"""
    user_input = state["user_input"]
    intent = state["intent"]
    department = state["department"]
    response = state["response"]

    return {
        "messages":[AIMessage(content=f"[汇总] 用户输入：{user_input}，意图识别：{intent}，处理部门：{department}，客服回复：{response}")]
    }

#定义条件边
def route_by_intent(state: ServiceState):
    """根据意图路由"""

    intent_map = {
        "refund": "refund",
        "tech": "tech",
        "consult": "consult",
        "feedback": "feedback"
    }

    intent = state["intent"]

    return intent_map.get(intent,"consult")



# 构建图
builder = StateGraph(ServiceState)
builder.add_node("check_intent",check_intent)
builder.add_node("handle_refund",handle_refund)
builder.add_node("handle_tech",handle_tech)
builder.add_node("handle_consult",handle_consult)
builder.add_node("handle_feedback",handle_feedback)
builder.add_node("summarize",summarize)

builder.add_edge(START,"check_intent")

builder.add_conditional_edges(
    "check_intent",
    route_by_intent,
    {"refund": "handle_refund",
     "tech": "handle_tech",
     "consult": "handle_consult",
     "feedback": "handle_feedback"}
)

builder.add_edge("handle_refund","summarize")
builder.add_edge("handle_tech","summarize")
builder.add_edge("handle_consult","summarize")
builder.add_edge("handle_feedback","summarize")
builder.add_edge("summarize",END)

#运行
if __name__ == '__main__':
    DB_URI = "postgresql://postgres:postgres123@192.168.179.5:5432/langgraph_db"

    with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
        # 首次运行需要创建表
        checkpointer.setup()

        # 4. 编译图
        graph = builder.compile(checkpointer=checkpointer)


        MESSAGES = [
            ("user_001", "我上周买的耳机有杂音，我要退货退款！"),
            ("user_002", "你好，请问你们的企业版和个人版有什么区别？"),
            ("user_003", "你们的App更新之后就一直在闪退，根本用不了！"),
            ("user_004", "App更新后一直闪退，怎么解决？"),
        ]

        for thread_id, msg in MESSAGES:
            config = {"configurable": {"thread_id": thread_id}}

            result = graph.invoke(
                {
                    "messages": [HumanMessage(content=msg)],
                    "user_input": msg,
                    "intent": "",
                    "department": "",
                    "response": "",
                },
                config,
            )
            print("=" * 60)
            print(f"对话内容：{msg}; 意图: {result['intent']} ;部门: {result['department']}")
            print(f"回复: {result['response']}")
            print("result:", result)








