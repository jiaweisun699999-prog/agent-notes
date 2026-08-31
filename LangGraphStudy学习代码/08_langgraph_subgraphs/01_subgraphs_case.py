"""
案例:订单支付后触发发货
    主图：处理订单 -> 子图（作为主图的节点）
    子图：发货动作（扣减库存、生成物流单号）
"""
from langchain_core.messages import AIMessage
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph


# 定义状态
class OrderState(MessagesState):
    order_id:str # 订单ID
    stock:int # 库存数量

# 构建子图
def deduct_stock(state:OrderState):
    "步骤一：减去库存"
    return {"stock":state["stock"] -1,"messages":[AIMessage(content=f"扣减库存成功，剩余库存{state["stock"] -1}")]}

def create_logistics(state:OrderState):
    "步骤二：生成发货单"

    return {"messages":[AIMessage(content=f"生成物流单号成功，物流单号为:SF-{state["order_id"]}")]}

sub_builder = StateGraph(OrderState)
sub_builder.add_node("deduct_stock",deduct_stock)
sub_builder.add_node("create_logistics",create_logistics)

sub_builder.add_edge(START,"deduct_stock")
sub_builder.add_edge("deduct_stock","create_logistics")
sub_builder.add_edge("create_logistics",END)

ship_subgraph = sub_builder.compile()



# 构建主图
def confirm_payment(state:OrderState):
    ship_subgraph.invoke
    return {"messages":[AIMessage(content=f"确认订单{state["order_id"]}支付,可以发货")]}

builder = StateGraph(OrderState)
builder.add_node("confirm_payment",confirm_payment)
builder.add_node("ship",ship_subgraph)

builder.add_edge(START,"confirm_payment")
builder.add_edge("confirm_payment","ship")
builder.add_edge("ship",END)
graph = builder.compile()



if __name__ == '__main__':
    result = graph.invoke({"order_id":"order_123","stock":10})

    print("result:",result)

    for msg in result["messages"]:
        msg.pretty_print()
