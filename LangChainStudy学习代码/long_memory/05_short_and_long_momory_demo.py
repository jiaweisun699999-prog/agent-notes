"""
智能电商客服助手
功能：结合短期记忆、长期记忆、消息摘要，提供流式、个性化的客服服务。
前置准备：
1. 安装依赖: pip install langchain langgraph langgraph-checkpoint-mysql pymysql
2. 创建MySQL数据库: CREATE DATABASE langchain_memory_db;
"""
import uuid
import warnings
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import SummarizationMiddleware, wrap_tool_call
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver
from langgraph.store.mysql.pymysql import PyMySQLStore
from langgraph.prebuilt import ToolRuntime
from langgraph.types import Command
from init_llm import deepseek_llm

# 禁用Pydantic序列化警告
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic.main")

# ========== 1. 定义Context 上下文 Schema==========
class UserContext(BaseModel):
    """定义调用Agent时传入的静态上下文信息"""
    user_id: str = Field(description="用户的唯一标识符")
    channel: str = Field(description="用户咨询渠道，如: APP, Web, 小程序")


# ========== 2. 定义自定义短期记忆状态 (继承AgentState) ==========
class CustomerSessionState(AgentState):
    """自定义短期记忆状态，用于管理单次会话中的动态信息"""
    current_order_id: str  # 用户当前正在查询的订单号


# ========== 3. 模拟订单数据库 数据 ==========
MOCK_DATABASE = {
    "orders": {
        "order001": {"order_id": "order001", "status": "已发货", "product": "智能手机",
                     "preference_context": "华为手机P70"},
        "order002": {"order_id": "order002", "status": "待支付", "product": "智能手表",
                     "preference_context": "Apple Watch Series 8"},
    }

}


# ========== 4. 定义工具 ==========
@tool
def get_user_info(runtime: ToolRuntime) -> str:
    """
    获取用户当前用户信息
    Args:
        runtime (ToolRuntime): 包含上下文信息的运行时环境
    Returns:
        str: 用户当前用户信息
    """
    print("get_user_info 中 runtime:", runtime)
    # 从上下文中获取当前用户ID
    current_user_id = runtime.context.user_id

    # 从上下文中获取用户咨询渠道
    user_channel = runtime.context.channel

    # 从状态中获取用户当前正在查询的订单号
    state = runtime.state
    if "current_order_id" in state:
        current_order_id = state["current_order_id"]
    else:
        current_order_id = "无"

    # 获取当前用户信息
    return f"用户ID: {current_user_id}, 咨询渠道: {user_channel}, 当前查询订单号: {current_order_id}"


@tool
def query_order_status(order_id: str, runtime: ToolRuntime) -> Command:
    """
    查询用户订单状态
    Args:
        order_id (str): 用户订单号
        runtime (ToolRuntime): 包含上下文信息的运行时环境
    Returns:
        Command: 包含更新操作的命令对象：状态中更新当前订单ID，并返回订单信息（状态、商品、用户偏好）
    """

    # 查询订单状态
    order_info = MOCK_DATABASE["orders"].get(order_id)

    if not order_info:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"错误：订单 [{order_id}] 不存在",
                        tool_call_id=runtime.tool_call_id
                    )
                ]
            }
        )

    updates = {
        "current_order_id": order_id,
        "messages": [
            ToolMessage(
                content=f"订单 [{order_id}] 状态: {order_info['status']}, 商品: {order_info['product']}。"
                        f"需要进行用户偏好更新，用户偏好: {order_info['preference_context']}",
                tool_call_id=runtime.tool_call_id
            )
        ]
    }

    return Command(update=updates)


@tool
def update_user_preference(category: str, liked_item: str, runtime: ToolRuntime) -> str:
    """
    更新用户长期偏好
    Args:
        category (str): 商品类别，如: 手机、配件
        liked_item (str): 用户喜欢的具体商品
        runtime (ToolRuntime): 包含上下文信息的运行时环境
    Returns:
        str: 确认更新结果
    """
    user_id = runtime.context.user_id
    namespace = (f"user_{user_id}", "preferences")

    key = str(uuid.uuid4())

    value_to_store = {
        "category": category,
        "liked_item": liked_item,
    }

    # 写入到长期记忆
    runtime.store.put(namespace, key, value_to_store)
    return f"已成功将您的偏好记录到长期记忆: 喜欢 {category} 类的 {liked_item}。"


@tool
def get_recommendation(runtime: ToolRuntime) -> str:
    """
    获取用户推荐商品
    Args:
        runtime (ToolRuntime): 包含上下文信息的运行时环境
    Returns:
        str: 包含推荐商品信息的字符串
    """
    user_id = runtime.context.user_id
    current_order = runtime.state.get("current_order_id", "未知订单")
    namespace = (f"user_{user_id}", "preferences")
    prefs = runtime.store.search(namespace)

    pref_list = []
    if prefs:
        for p in prefs[-3:]:  # 仅取最近3条偏好记录，[-3:] 表示取最后3条记录
            pref_list.append(f"{p.value.get('category')}({p.value.get('liked_item')})")

    return f"基于用户当前的订单 [{current_order}] 和长期偏好 {pref_list if pref_list else '无'}，为用户推荐相关配件或类似风格商品。"


@wrap_tool_call
def handle_tool_errors(request, handler):
    """使用自定义消息处理工具执行错误"""
    try:
        return handler(request)
    except Exception as e:
        # 向模型返回自定义错误消息
        return ToolMessage(
            content=f"调用工具错误:请稍后重试，错误信息：({str(e)})",
            tool_call_id=request.tool_call["id"]
        )


# ========== 5. 创建Agent，控制台交互循环 ==========
DB_URI = "mysql+pymysql://root:123456@localhost:3306/langchain_db?charset=utf8mb4"

# 初始化MySQL存储 (短期记忆Checkpointer 和 长期记忆Store)
with (
    PyMySQLSaver.from_conn_string(DB_URI) as checkpointer,
    PyMySQLStore.from_conn_string(DB_URI) as store
):
    # 首次运行时自动建表
    checkpointer.setup()
    store.setup()

    # 创建Agent
    agent = create_agent(
        model=deepseek_llm,
        tools=[get_user_info, query_order_status, update_user_preference, get_recommendation],
        system_prompt="""
                        你是一个智能电商客服助手，具备回答用户咨询、获取用户信息、查询订单状态、更新用户偏好和推荐商品功能。"
                        获取用户信息请调用 get_user_info 工具。
                        查询订单状态请调用 query_order_status 工具，查询到订单状态后，还需要调用 update_user_preference 工具更新用户偏好。
                        更新用户偏好请调用 update_user_preference 工具。
                        获取推荐商品请调用 get_recommendation 工具。
                      """,
        checkpointer=checkpointer,
        store=store,
        state_schema=CustomerSessionState,
        context_schema=UserContext,
        middleware=[
            SummarizationMiddleware(
                model=deepseek_llm,
                summary_prompt="请总结以下对话内容：{messages}",
                trigger=("messages", 10),  # 每10条消息触发一次摘要
                keep=("messages", 5),  # 保留最后5条消息
            ),
            handle_tool_errors
        ],
    )

    # 控制台交互循环 (流式调用)
    print("=" * 50)
    print("智能电商客服助手")
    print("功能: 查询订单、更新偏好、获取推荐。")
    print("输入 'quit' 或 '退出' 结束对话。")
    print("=" * 50)

    # 初始化用户上下文 (模拟从登录态获取)
    user_context = UserContext(user_id="customer_001", channel="Web")
    # 会话线程ID
    # config = {"configurable": {"thread_id": "session_01"}}
    config = {"configurable": {"thread_id": "session_02"}}

    # 对话循环
    while True:
        try:
            user_input = input("[你]: ").strip()

            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("客服助手: 感谢你的咨询，再见！")
                break

            # 过滤空输入
            if not user_input:
                continue

            # 准备输入消息
            input_data = {"messages": {"role": "user", "content": user_input}}

            print("[客服助手]: ")
            # 流式调用Agent
            for chunk in agent.stream(input_data, config=config, context=user_context):
                # print("chunk:", chunk)
                for step, data in chunk.items():  # 遍历dict的key-value对
                    # print("step:", step)
                    # print("data:", data)

                    # 只有当 step为model或者tools时，才打印消息
                    if step in ["model", "tools"]:
                        message = data["messages"][-1]
                        message.pretty_print()

        except Exception as e:
            print(f"调用过程中出现错误: {e}")