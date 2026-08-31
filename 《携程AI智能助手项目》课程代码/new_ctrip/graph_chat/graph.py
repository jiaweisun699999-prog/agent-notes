import uuid

from langgraph.constants import END, START
from langgraph.graph import MessagesState, StateGraph
from langgraph.types import Command

from graph_chat.all_agent import supervisor_agent, research_agent, flight_booking_agent, hotel_booking_agent, \
    car_rental_booking_agent, excursion_booking_agent, memory
from graph_chat.draw_png import draw_graph
from graph_chat.fetch_user_info_node import get_user_info
from graph_chat.my_print import pretty_print_messages
from tools.init_db import update_dates



graph = (
    StateGraph(MessagesState)
    .add_node('fetch_user_info', get_user_info)
    # 添加一个主管agent节点
    .add_node(supervisor_agent, destinations=("research_agent", 'flight_booking_agent', 'hotel_booking_agent', 'car_rental_booking_agent', 'excursion_booking_agent' , END))
    .add_node(research_agent, destinations=(END,))
    .add_node(flight_booking_agent, destinations=(END,))
    .add_node(hotel_booking_agent, destinations=(END,))
    .add_node(car_rental_booking_agent, destinations=(END,))
    .add_node(excursion_booking_agent, destinations=(END,))
    .add_edge(START, 'fetch_user_info')
    .add_edge('fetch_user_info', 'supervisor')
    .compile(checkpointer=memory)
)

# draw_graph(graph, 'graph_supervisor.png')

session_id = str(uuid.uuid4())
# update_dates()  # 每次测试的时候：保证数据库是全新的，保证，时间也是最近的时间

# 配置参数，包含乘客ID和线程ID
config = {
    "configurable": {
        # passenger_id用于我们的航班工具，以获取用户的航班信息
        "passenger_id": "3442 587242",
        # 检查点由session_id访问
        "thread_id": session_id,
    }
}



def execute_graph(user_input: str) -> str:
    """ 执行工作流的函数"""
    result = ''  # AI助手的最后一条消息
    current_state = graph.get_state(config)
    if current_state.next:  # 出现了工作流的中断
        human_command = Command(resume={'answer': user_input})
        for chunk in graph.stream(human_command, config, stream_mode='values'):
            pretty_print_messages(chunk, last_message=True)
        return result
    else:
        for chunk in graph.stream({'messages': ('user', user_input)}, config):
            pretty_print_messages(chunk, last_message=True)


    current_state = graph.get_state(config)
    if current_state.next:  # 出现了工作流的中断
        result = current_state.interrupts[0].value

    return result


# 执行工作流
while True:
    user_input = input('用户：')
    res = execute_graph(user_input)
    if res:
        print('AI: ', res)