from typing import Annotated

from langchain_core.tools import tool, InjectedToolCallId
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent, InjectedState
from langgraph.types import Command

from graph_chat.my_llm import llm
from tools.car_tools import search_car_rentals, book_car_rental, update_car_rental, cancel_car_rental
from tools.flights_tools import search_flights, update_ticket_to_new_flight, cancel_ticket
from tools.hotels_tools import search_hotels, book_hotel, update_hotel, cancel_hotel
from tools.retriever_vector import lookup_policy
from tools.search_tool import MySearchTool
from tools.trip_tools import search_trip_recommendations, book_excursion, update_excursion, cancel_excursion

# 这是整个状态图的完整内存
memory = InMemorySaver()

# 网络搜索的 子智能体
research_agent = create_react_agent(
    model=llm,
    tools=[MySearchTool()],
    prompt=(
        "你是一个网络搜索的智能体(Agent)。\n\n"
        "指令：\n"
        "- 仅网络数据获取、网络查询、数据查询相关的任务\n"
        "- 回复时仅包含工作结果，不要包含任何其他文字"
    ),
    checkpointer=memory,
    name="research_agent",
)

# 定义安全工具（只读操作）和敏感工具（涉及更改的操作）
update_flight_safe_tools = [search_flights, lookup_policy]
update_flight_sensitive_tools = [update_ticket_to_new_flight, cancel_ticket]

# 合并所有工具
update_flight_tools = update_flight_safe_tools + update_flight_sensitive_tools
# 航班预订的 子智能体
flight_booking_agent = create_react_agent(
    model=llm,
    tools=update_flight_tools,
    prompt=(
        "您是专门处理航班查询，改签政策查询，改签和预定的智能体(Agent)。\n\n"
        "指令：\n"
        "- 在搜索航班时，请坚持不懈。如果第一次搜索没有结果，请扩大查询范围。\n"
        "- 如果您的工具都不适用或客户改变主意，直接回复，并给出理由。\n"
        "- 回复时仅包含工作结果，不要包含任何其他文字"
    ),
    checkpointer=memory,
    name="flight_booking_agent",
)

# 定义安全工具（只读操作）和敏感工具（涉及更改的操作）
book_hotel_safe_tools = [search_hotels]
book_hotel_sensitive_tools = [book_hotel, update_hotel, cancel_hotel]

# 合并所有工具
book_hotel_tools = book_hotel_safe_tools + book_hotel_sensitive_tools

# 酒店处理的 子智能体
hotel_booking_agent = create_react_agent(
    model=llm,
    tools=book_hotel_tools,
    prompt=(
        "您是专门处理酒店查询，酒店预定，酒店订单修改的智能体(Agent)。\n\n"
        "指令：\n"
        "- 在搜索时，请坚持不懈。如果第一次搜索没有结果，请扩大查询范围。\n"
        "- 根据用户的偏好搜索可用酒店，并与客户确认预订详情。\n"
        "- 如果您的工具都不适用或客户改变主意，直接回复，并给出理由。\n"
        "- 回复时仅包含工作结果，不要包含任何其他文字"
    ),
    checkpointer=memory,
    name="hotel_booking_agent",
)

# 定义安全工具（只读操作）和敏感工具（涉及更改的操作）
book_car_rental_safe_tools = [search_car_rentals]
book_car_rental_sensitive_tools = [
    book_car_rental,
    update_car_rental,
    cancel_car_rental,
]

# 合并所有工具
book_car_rental_tools = book_car_rental_safe_tools + book_car_rental_sensitive_tools
# 汽车租赁处理的 子智能体
car_rental_booking_agent = create_react_agent(
    model=llm,
    tools=book_car_rental_tools,
    prompt=(
        "您是专门处理汽车租赁查询，汽车租赁预定，汽车租赁订单修改的智能体(Agent)。\n\n"
        "指令：\n"
        "- 在搜索时，请坚持不懈。如果第一次搜索没有结果，请扩大查询范围。\n"
        "- 根据用户的偏好搜索可用租车，并与客户确认预订详情。\n"
        "- 如果您的工具都不适用或客户改变主意，直接回复，并给出理由。\n"
        "- 回复时仅包含工作结果，不要包含任何其他文字"
    ),
    name="car_rental_booking_agent",
)

# 定义安全工具（只读操作）和敏感工具（涉及更改的操作）
book_excursion_safe_tools = [search_trip_recommendations]
book_excursion_sensitive_tools = [book_excursion, update_excursion, cancel_excursion]

# 合并所有工具
book_excursion_tools = book_excursion_safe_tools + book_excursion_sensitive_tools
# 旅行推荐处理的 子智能体
excursion_booking_agent = create_react_agent(
    model=llm,
    tools=book_excursion_tools,
    prompt=(
        "您是专门处理旅行推荐查询，旅行产品预定，旅行订单修改的智能体(Agent)。\n\n"
        "指令：\n"
        "- 在搜索时，请坚持不懈。如果第一次搜索没有结果，请扩大查询范围。\n"
        "- 根据用户的偏好搜索可行的旅行推荐，并与客户确认预订详情。\n"
        "- 如果您的工具都不适用或客户改变主意，直接回复，并给出理由。\n"
        "- 回复时仅包含工作结果，不要包含任何其他文字"
    ),
    name="excursion_booking_agent",
)

def create_handoff_tool(*, agent_name: str, description: str | None = None):
    """
    创建一个用于将当前会话转接到指定代理的工具函数。

    该函数返回一个装饰器包装的工具函数，当调用时会生成一个工具消息并返回转接命令，
    指示流程控制器将控制权转移给指定的代理。

    参数:
        agent_name (str): 目标代理的名称，用于标识要转接的代理
        description (str | None): 工具的描述信息，如果未提供则使用默认描述

    返回:
        handoff_tool: 一个装饰器包装的工具函数，用于执行转接操作
    """
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_tool(
            state: Annotated[MessagesState, InjectedState],
            tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        """
        执行实际的转接操作。

        创建一个工具消息表明转接成功，并返回一个命令对象指示流程控制器
        将控制权转移给指定代理，同时更新会话状态。

        参数:
            state (MessagesState): 当前会话状态，包含消息历史等信息
            tool_call_id (str): 工具调用的唯一标识符

        返回:
            Command: 包含转接指令和状态更新的命令对象
        """
        # 构造工具消息，记录转接操作的成功执行
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": name,
            "tool_call_id": tool_call_id,
        }
        # 返回转接命令，指定目标代理和更新后的状态
        return Command(
            goto=agent_name,
            update={**state, "messages": state["messages"] + [tool_message]},
            graph=Command.PARENT,
        )

    return handoff_tool


# Handoffs
assign_to_research_agent = create_handoff_tool(
    agent_name="research_agent",
    description="将任务分配给：research_agent智能体。",
)

assign_to_flight_booking_agent = create_handoff_tool(
    agent_name="flight_booking_agent",
    description="将任务分配给：flight_booking_agent智能体。",
)
assign_to_hotel_booking_agent = create_handoff_tool(
    agent_name="hotel_booking_agent",
    description="将任务分配给：hotel_booking_agent智能体。",
)
assign_to_car_rental_booking_agent = create_handoff_tool(
    agent_name="car_rental_booking_agent",
    description="将任务分配给：car_rental_booking_agent智能体。",
)
assign_to_excursion_booking_agent = create_handoff_tool(
    agent_name="excursion_booking_agent",
    description="将任务分配给：excursion_booking_agent智能体。",
)

# 主管 智能体
supervisor_agent = create_react_agent(
    model=llm,
    tools=[assign_to_research_agent, assign_to_flight_booking_agent, assign_to_hotel_booking_agent, assign_to_car_rental_booking_agent, assign_to_excursion_booking_agent],
    prompt=(
        "你是一个监督者或者管理者，管理五个智能体：\n"
        "- 网络搜索智能体：分配与网络搜索、数据查询相关的任务\n"
        "- 航班预订能体：分配与航班查询，预定，改签等相关的任务\n"
        "- 酒店预订智能体：分配与酒店查询，预定，修改订单等相关的任务\n"
        "- 汽车租赁预定智能体：分配与汽车租赁查询，预定，修改订单等相关的任务\n"
        "- 旅行产品预定智能体：分配与旅行推荐查询，预定，修改订单等相关的任务\n"
        "处理规则：\n"
        "1. 如果问题属于以下类别，直接回答：\n"
        "   - 可以根据上下文记录直接回答的内容（如'你的航班信息，起飞时间等'）。\n"
        "   - 不需要工具的一般咨询（如'你好'）。\n"
        "   - 确认类问题（如'你收到我的请求了吗'）。\n"
        "2. 其他情况按类型分配给对应智能体。\n"
        "3. 一次只分配一个任务给一个智能体。\n"
        "4. 不要自己执行需要工具的任务。\n"
    ),
    # checkpointer=memory,
    name="supervisor",
)