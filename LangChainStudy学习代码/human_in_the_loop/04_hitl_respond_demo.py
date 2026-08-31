# ===== 1. 定义工具 =====
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from init_llm import deepseek_llm

# ===== 1. 定义工具 =====

@tool
def ask_customer(message: str) -> str:
    """
    向客户询问确认信息（占位工具——由人工回复来实现）
    注意：这个工具本身不做任何事，它的"返回值"就是人工的回复
    """
    # 正常流程下这个函数体不会被执行——respond 决策会跳过工具执行
    # 但如果有人错误地配置为 approve，这个函数会被调用
    raise RuntimeError("ask_customer 必须由人工回复，不允许直接执行！")


@tool
def query_order(order_id: str) -> str:
    """查询订单信息"""
    return f"订单 {order_id}：已付款，待发货，金额 ¥299.00"


@tool
def update_shipping_address(order_id: str, address: str) -> str:
    """更新收货地址"""
    return f"订单 {order_id} 的收货地址已更新为：{address}"


agent = create_agent(
    model=deepseek_llm,
    tools=[ask_customer, query_order, update_shipping_address],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on= {
                "ask_customer":{ # 向客户询问确认信息时，人工介入
                    "allowed_decisions": ["respond"],
                    "description":"请回复确认信息！"
                },
                "query_order":False, # 查询订单信息时，不人工介入
                "update_shipping_address": False, # 更新收货地址时，不人工介入
            },
            description_prefix= "需要人工介入，请确认操作！"
        ),
    ],
    checkpointer=InMemorySaver(),
    system_prompt="你是一个电商客服助手，如果需要用户输入一些确认信息(例如用户收货地址)，请使用ask_customer工具。"
)

config = {"configurable":{"thread_id":"session_01"}}

result = agent.invoke(
    {"messages":[{"role":"user","content":"需要将订单order001 更新收货地址，请向客户确认新地址"}]},
            config=config,
            version="v2"
)

print("result:", result)

if result.interrupts:
    # 1.输出中断信息
    req = result.interrupts[0].value["action_requests"][0]
    print("==== Agent 暂停执行，申请操作：======")
    # 中断工具的信息
    print(f"    待确认执行的工具：{req["name"]}")
    print(f"    工具参数：{req["args"]}")
    print(f"    描述：{req["description"]}")
    # 用户可以确认的操作
    allowed_decisions = result.interrupts[0].value["review_configs"][0]["allowed_decisions"]
    print(f"    用户可以确认的操作：{allowed_decisions}")

    # 2.用户确认操作
    while True:
        decision = input(f"    请输入确认操作，从{allowed_decisions}中选择一种：").strip().lower()
        if decision in allowed_decisions:
            break
        print(f"    请输入正确的确认操作！从{allowed_decisions}中选择一种。当前的输入：{decision}")

    # 3.确认操作
    if decision == "approve":
        resume_cmd = Command(resume={"decisions": [{"type":"approve"}]})
    elif decision == "reject":
        reason = input(f"    请输入拒绝原因：").strip().lower()
        if not reason:
            reason="用户拒绝了操作"
        resume_cmd = Command(resume={"decisions": [{"type":"reject", "message":f"用户拒绝操作,原因：{reason}"}]})
    elif decision == "edit":
        new_product_ids = input("请输入新的商品ID列表，用逗号分隔：").strip().split(",")
        new_discount_rate = float(input("请输入折扣：").strip())

        resume_cmd = Command(
            resume={
                "decisions": [
                    {
                        "type":"edit",
                        "edited_action":{
                            "name":"batch_update_discount",
                            "args": {
                                "product_ids": new_product_ids,
                                "discount_rate": new_discount_rate
                            }
                        }
                    }
                ]
            }
        )

    elif decision == "respond":
        input = input("请输入信息：")
        resume_cmd = Command(resume={"decisions": [{"type":"respond", "message":f"用户回复：{input}"}]})

    else:
        print("位置的操作!")
    #4.回复Agent 执行
    result = agent.invoke(resume_cmd,config=config,version="v2")

    print("Agent 恢复执行，result:", result)
    print("[Agent 回复]：", result.value["messages"][-1].content)
else:
    print("Agent 没有中断，直接执行完成。")
    print(result.value["messages"][-1].content)



