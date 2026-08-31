from typing import Literal, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.types import interrupt, Command, RetryPolicy

from init_llm import deepseek_llm_flash


# ================================================================
# 一、物流状态子图（独立 schema，供售后"节点内调用"）
# ================================================================
class LogisticsState(TypedDict):
    """物流子图状态：订单号与物流轨迹（与父 schema 无共享字段）"""
    order_id: str  # 订单号
    status: str    # 物流轨迹


def query_package(state: LogisticsState) -> dict:
    """物流子图节点一：查询包裹当前所在节点"""
    return {"status": f"包裹 {state['order_id']} 已到达转运中心"}


def estimate_delivery(state: LogisticsState) -> dict:
    """物流子图节点二：补充预计送达时间"""
    return {"status": state["status"] + "，预计明天送达，快递员派送中"}


logistics_builder = StateGraph(LogisticsState)
logistics_builder.add_node("query_package", query_package)
logistics_builder.add_node("estimate_delivery", estimate_delivery)

logistics_builder.add_edge(START, "query_package")
logistics_builder.add_edge("query_package", "estimate_delivery")
logistics_builder.add_edge("estimate_delivery", END)
logistics_subgraph = logistics_builder.compile()


# ================================================================
# 二、聊天分支（create_agent 子图，作为主图节点）
# ================================================================
@tool
def get_weather(location: str) -> str:
    """查询指定地点的天气。用户询问天气时使用。"""
    return f"：{location}天气晴朗"


chat_agent = create_agent(
    model=deepseek_llm_flash,
    name="chat_agent",
    tools=[get_weather],
    system_prompt=(
        "你是电商网站的小助手，性格轻松友好。用户找你聊天时陪聊即可，"
        "可以用 get_weather 查询天气。回答保持简短自然。"
    ),
    checkpointer=True,
)


# ================================================================
# 三、售前分支（StateGraph 子图，作为主图节点，固定三步）
# ================================================================
class Product(BaseModel):
    """售前：从用户消息中提取商品名称（LLM 结构化输出）"""
    product: str = Field(description="用户咨询的商品名称")


class PresaleState(MessagesState):
    """售前子图状态：共享 messages，额外增加商品与查询结果字段"""
    product: str
    reply: str = ""


def extract_product(state: PresaleState) -> dict:
    """售前节点一：LLM 提取用户咨询的商品名"""
    model_struct = deepseek_llm_flash.with_structured_output(Product)
    resp = model_struct.invoke(
        [SystemMessage(content="从用户咨询中提取商品名称。"),
         HumanMessage(content=state["messages"][-1].content)]
    )
    if resp.product == "":
        product = interrupt("输入你要咨询的商品名称，例如（钻戒、手机、耳机）")
        return {"product": product}
    return {"product": resp.product}


def query_product(state: PresaleState) -> dict:
    """售前节点二：一次查全规格 / 价格 / 物流方式"""
    product = state["product"]
    price = {"钻戒": "¥2999 起", "手机": "¥1999 起", "耳机": "¥399 起"}.get(product, "¥199 起")
    reply = "没有找到相关商品信息"
    if product == "钻戒":
        reply = f"钻戒规格：主石-30 分天然钻石，价格：{price}；物流：珠宝专送 + 全额保价，顺丰发货，预计 2–3 天送达"
    elif product == "手机":
        reply = f"手机规格：5.1 英寸屏 / 8GB 内存 / 256GB 存储，黑色银色可选；价格：{price}；物流：满 99 包邮，顺丰发货，预计 2 天送达。"
    else:
        reply = f"耳机规格：主动降噪 / 30h 续航；黑白两色可选；价格：{price}；物流：满 99 包邮，顺丰发货，预计 2 天送达。"
    return {"reply": reply}


def ask_coupon(state: PresaleState) -> dict:
    """售前节点三：中断，询问用户是否领取优惠券"""
    decision = interrupt(f"你咨询了【{state['product']}】，是否领取 10 元优惠券？确认 ok，取消 no")
    coupon_text = "已为你领取 10 元优惠券。" if decision.strip().lower() == "ok" else "未领取优惠券。"
    return {"messages": [AIMessage(content=state.get("reply", "") + "," + coupon_text)]}


presale_builder = StateGraph(PresaleState)
presale_builder.add_node("extract_product", extract_product)
presale_builder.add_node("query_product", query_product, retry_policy=RetryPolicy(max_attempts=3))
presale_builder.add_node("ask_coupon", ask_coupon)

presale_builder.add_edge(START, "extract_product")
presale_builder.add_edge("extract_product", "query_product")
presale_builder.add_edge("query_product", "ask_coupon")
presale_builder.add_edge("ask_coupon", END)

presale_subgraph = presale_builder.compile(checkpointer=True)


# ================================================================
# 四、售后退款分支（StateGraph 子图，作为主图节点，固定三步）
# ================================================================
class Order(BaseModel):
    """售后：从用户消息中提取订单号（LLM 结构化输出）"""
    order_id: str = Field(description="用户提到的订单号")


class AftersaleState(MessagesState):
    """售后子图状态：共享 messages，额外增加订单相关字段"""
    order_id: str
    reply: str = ""


def extract_order(state: AftersaleState) -> dict:
    """售后节点一：LLM 提取订单号"""
    model_struct = deepseek_llm_flash.with_structured_output(Order)
    result = model_struct.invoke(
        [SystemMessage(content="从用户消息中提取订单号，格式如 ORD123456。"),
         HumanMessage(content=state["messages"][-1].content)]
    )
    if result.order_id == "":
        order_id = interrupt("请输入退款订单号")
        return {"order_id": order_id}
    return {"order_id": result.order_id}


def query_order(state: AftersaleState) -> dict:
    """售后节点二：查订单状态 + 节点内调用物流子图（不同 schema，做状态转换）"""
    order_status = f"订单 {state['order_id']} 已支付，正在出库"
    result = logistics_subgraph.invoke({"order_id": state["order_id"], "status": ""})
    reply = f"{order_status}；{result['status']}"
    return {"reply": reply}


def handle_complaint(state: AftersaleState) -> dict:
    """售后节点三：中断，处理退款"""
    decision = interrupt(
        f"订单 {state['order_id']} 当前状态：{state.get('reply', '暂无')}。\n"
        "是否确认退款？确认 yes，取消 no"
    )
    refund_text = "已为你提交退款，3日内到账。" if decision.strip().lower() == "yes" else "退款未提交，客服将稍后回访。"
    return {"messages": [AIMessage(content=state.get("reply", "") + refund_text)]}


aftersale_builder = StateGraph(AftersaleState)
aftersale_builder.add_node("extract_order", extract_order)
aftersale_builder.add_node("query_order", query_order, retry_policy=RetryPolicy(max_attempts=3))
aftersale_builder.add_node("handle_complaint", handle_complaint)

aftersale_builder.add_edge(START, "extract_order")
aftersale_builder.add_edge("extract_order", "query_order")
aftersale_builder.add_edge("query_order", "handle_complaint")
aftersale_builder.add_edge("handle_complaint", END)

aftersale_subgraph = aftersale_builder.compile(checkpointer=True)


# ================================================================
# 五、主图：意图识别 -> 条件边路由到三个分支
# ================================================================
class Intent(BaseModel):
    """用户意图：LLM 结构化输出"""
    intent: Literal["chat", "presale", "aftersale"] = Field(
        description="用户意图：chat=聊天（与购物无关）， presale=售前咨询（固定商品信息），aftersale=售后退款"
    )


class MainState(MessagesState):
    """主图状态：共享 messages，额外增加意图字段"""
    intent: str


def classify(state: MainState) -> dict:
    """主图节点：LLM 识别用户意图（结构化输出）"""
    model_struct = deepseek_llm_flash.with_structured_output(Intent)
    result = model_struct.invoke(
        [SystemMessage(content="判断用户意图：与购物无关的聊天为 chat，咨询商品规格/价格/物流方式为 presale，售后退款为 aftersale。"),
         HumanMessage(content=state["messages"][-1].content)]
    )
    return {"intent": result.intent}


def route(state: MainState) -> str:
    """条件边路由：按意图分发到对应分支"""
    return state["intent"]


builder = StateGraph(MainState)
builder.add_node("classify", classify)
builder.add_node("chat_agent", chat_agent)
builder.add_node("presale_subgraph", presale_subgraph)
builder.add_node("aftersale_subgraph", aftersale_subgraph)

builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route, {
    "chat": "chat_agent",
    "presale": "presale_subgraph",
    "aftersale": "aftersale_subgraph"
})
builder.add_edge("chat_agent", END)
builder.add_edge("presale_subgraph", END)
builder.add_edge("aftersale_subgraph", END)

graph = builder.compile(checkpointer=InMemorySaver())


# ================================================================
# 六、实时对话主循环
# ================================================================
def extract_text(content) -> str:
    """把 v3 stream 的 content（字符串或 content blocks 列表）统一提取为纯文本"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(block.get("text", "") for block in content if isinstance(block, dict))
    return str(content)


def get_user_input(info):
    """根据中断信息向用户提问并读取输入（字符串 / 字典都支持）"""
    if isinstance(info, str):
        return input(f"\n[助手]: {info}\n[用户]: ").strip()
    show = "\n".join(f"  {k}: {v}" for k, v in info.items())
    return input(f"\n[助手]: 需要人工确认 - {show}\n[用户]: ").strip()


def run_dialog():
    """Console 实时对话主循环"""
    config = {"configurable": {"thread_id": "shop-001"}}
    print("电商网站智能客服助手已就绪。输入 q / exit / 退出 结束。")
    print("例：推荐点好物 / 这款手机什么配置多钱 / 我的订单 ORD123456 需要退款\n")

    while True:
        user_input = input("[用户]: ").strip()
        if user_input.lower() in ("q", "quit", "exit", "退出"):
            print("助手: 再见，欢迎再次光临！")
            break
        if not user_input:
            continue

        stream_input: dict | Command = {"messages": [HumanMessage(content=user_input)]}

        while True:
            stream = graph.stream_events(stream_input, config=config, version="v3")

            print("【助手】", end="", flush=True)
            for message in stream.messages:
                for token in message.text:
                    if token.strip():
                        print(token, end="", flush=True)
            print()

            if not stream.interrupted:
                final_state = stream.output
                print(f"\n===== 最终回复：{extract_text(final_state['messages'][-1].content)} =====")
                break

            try:
                user_response = get_user_input(stream.interrupts[0].value)
            except (EOFError, KeyboardInterrupt):
                print("\n[系统] 对话中断，会话结束")
                return

            stream_input = Command(resume=user_response)


if __name__ == "__main__":
    run_dialog()
