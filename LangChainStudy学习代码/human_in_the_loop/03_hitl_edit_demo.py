# ===== 1. 定义工具 =====
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from init_llm import deepseek_llm

# ===== 1. 模拟商品数据库 =====

PRODUCTS = {
    "P001": {"name": "AirPods Pro", "price": 1000},
    "P002": {"name": "iPhone 15", "price": 2000},
    "P003": {"name": "MacBook Air", "price": 3000},
}


# ===== 2. 定义工具 =====
@tool
def batch_update_discount(product_ids: list, discount_rate: float) -> str:
    """
    批量更新商品折扣
    Args:
        product_ids: 商品ID列表，如 ["P001", "P002"]
        discount_rate: 折扣率，0.1~1.0，如 0.5 表示打5折
    """
    results = []
    for pid in product_ids:
        if pid in PRODUCTS:
            product_name = PRODUCTS[pid]['name']
            price = PRODUCTS[pid]["price"]
            new_price = price * discount_rate
            results.append(f"{product_name}: 原价¥{price} → ¥{new_price}")
    return "折扣更新完成：\n" + "\n".join(results)


@tool
def query_product(product_id: str) -> str:
    """查询商品信息"""
    p = PRODUCTS.get(product_id)
    product_name = p['name']
    price = p['price']
    return f"{product_name} 当前售价 ¥{price}" if p else "未找到"


agent = create_agent(
    model=deepseek_llm,
    tools=[batch_update_discount, query_product],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on= {
                "batch_update_discount":{ # 批量更新商品折扣时，人工介入
                    "allowed_decisions": ["approve", "reject", "edit"],
                    "description":"请确认是否更新折扣率？"
                },
                "query_product":False, # 查询商品信息时，不人工介入
            },
            description_prefix= "需要人工介入，请确认操作！"
        ),
    ],
    checkpointer=InMemorySaver(),
    system_prompt="你是一个智能助手，可以回答用户问题。"
)

config = {"configurable":{"thread_id":"session_01"}}

result = agent.invoke(
    {"messages":[{"role":"user","content":"将 P001 和P002 商品给我打5折"}]},
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


    else:
        print("位置的操作!")
    #4.回复Agent 执行
    result = agent.invoke(resume_cmd,config=config,version="v2")

    print("Agent 恢复执行，result:", result)
    print("[Agent 回复]：", result.value["messages"][-1].content)
else:
    print("Agent 没有中断，直接执行完成。")
    print(result.value["messages"][-1].content)



