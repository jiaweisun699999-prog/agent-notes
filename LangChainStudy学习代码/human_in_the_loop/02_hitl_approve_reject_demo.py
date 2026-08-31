# ===== 1. 定义工具 =====
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from init_llm import deepseek_llm


@tool
def query_user_info(user_id: str) -> str:
    """查询用户基本信息"""
    return f"用户 {user_id} 共有订单23笔，账户余额¥520.00。"


@tool
def delete_user_info(user_id: str) -> str:
    """删除用户数据信息"""
    return f"用户 {user_id} 的所有记录已删除。"


agent = create_agent(
    model=deepseek_llm,
    tools=[query_user_info, delete_user_info],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on= {
                "query_user_info":False, # 查询用户信息时，不人工介入

                "delete_user_info":{ # 删除用户数据时，人工介入
                    "allowed_decisions": ["approve", "reject"],
                    "description":"请确认是否删除用户数据？"
                },
            },
            description_prefix= "需要人工介入，请确认操作！"
        ),
    ],
    checkpointer=InMemorySaver(),
    system_prompt="你是一个智能助手，可以回答用户问题。"
)

config = {"configurable":{"thread_id":"session_01"}}

result = agent.invoke(
# {"messages":[{"role":"user","content":"你叫什么名字"}]},
    {"messages":[{"role":"user","content":"删除用户123的所有记录"}]},
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
            reason="用户拒绝了删除用户数据的操作"
        resume_cmd = Command(resume={"decisions": [{"type":"reject", "message":f"用户拒绝操作,原因：{reason}"}]})

    #4.回复Agent 执行
    result = agent.invoke(resume_cmd,config=config,version="v2")

    print("Agent 恢复执行，result:", result)
    print("[Agent 回复]：", result.value["messages"][-1].content)
else:
    print("Agent 没有中断，直接执行完成。")
    print(result.value["messages"][-1].content)



