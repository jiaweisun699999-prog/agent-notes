from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState

from tools.flights_tools import fetch_user_flight_information


def format_flight_info(flight_data: list[dict]) -> str:
    """将航班数据格式化为中文字符串"""
    flight = flight_data[0]  # 假设返回的是单条航班信息
    return (
        f"已查询到您的航班信息：\n"
        f"- 机票号：{flight['ticket_no']}\n"
        f"- 预订编号：{flight['book_ref']}\n"
        f"- 航班号：{flight['flight_no']}（{flight['flight_id']}）\n"
        f"- 出发机场：{flight['departure_airport']}\n"
        f"- 到达机场：{flight['arrival_airport']}\n"
        f"- 计划起飞时间：{flight['scheduled_departure']}\n"
        f"- 计划到达时间：{flight['scheduled_arrival']}\n"
        f"- 座位号：{flight['seat_no']}\n"
        f"- 舱位条件：{flight['fare_conditions']}"
    )



def get_user_info(state: MessagesState, config: RunnableConfig):
    """
    获取用户的航班信息并更新状态字典。
    参数:
        state (State): 当前状态字典。
    返回:
        dict: 包含用户信息的新状态字典。
    """
    # return {"user_info": fetch_user_flight_information.invoke({})}

    if 'messages' in state:
        for message in state['messages']:
            # 如果已经查了航班信息，则直接返回
            if isinstance(message, AIMessage) and message.id == 'user_info_success':
                return

    flight_data = fetch_user_flight_information(config)
    if flight_data:
        flight_message = AIMessage(
            content=format_flight_info(flight_data),  # 中文格式化字符串
            additional_kwargs={},  # 按需留空
            id='user_info_success',  # 随机生成一个唯一的 ID
        )
    else:
        flight_message = AIMessage(
            content="未找到您的航班信息。请检查输入的旅客信息是否正确。",
            additional_kwargs={},
            id='user_info_fail',
        )
    # 返回更新部分，MessagesState 会自动处理消息追加
    return {
        "messages": [flight_message],  # 新增 AIMessage
    }