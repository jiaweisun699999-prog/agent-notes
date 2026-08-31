"""
案例：多工具同时中断 —— 批量操作审批

"""

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from init_llm import deepseek_llm


# =====================================================================
# 1. 定义工具
# =====================================================================

@tool
def restart_service(service_name: str, environment: str) -> str:
    """重启指定的微服务"""
    return f"服务[{service_name}]（{environment}环境）已成功重启，耗时 3.2 秒"


@tool
def send_notification(channel: str, title: str, content: str) -> str:
    """向指定渠道发送通知消息"""
    return (f"已通过[{channel}]发送通知：\n   标题：{title}\n   内容：{content}")


@tool
def update_config(config_key: str, config_value: str) -> str:
    """更新系统配置项"""
    return f"配置项[{config_key}]已更新为[{config_value}]"


@tool
def query_service_status(service_name: str) -> str:
    """查询服务当前运行状态"""
    return f"服务[{service_name}]当前状态：CPU 92%, 内存 78%, 错误率 15%"


# =====================================================================
# 2. 创建 Agent：三个工具都需要审批
# =====================================================================

agent = create_agent(
    model=deepseek_llm,
    tools=[
        query_service_status,
        restart_service,
        send_notification,
        update_config,
    ],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                # 以下三个工具全部需要人工介入
                "restart_service": {
                    "allowed_decisions": ["approve", "reject"],
                    "description": "敏感操作：重启生产服务，请确认是否继续执行？",
                },
                "send_notification": {
                    "allowed_decisions": ["approve", "reject"],
                    "description": "敏感操作：向外发送通知，请确认是否继续执行？",
                },
                "update_config": {
                    "allowed_decisions": ["approve", "reject"],
                    "description": "敏感操作：修改系统配置，请确认是否继续执行？",
                },
                # 查询操作：无需审批，直接放行
                "query_service_status": False,
            },
            description_prefix="需要人工介入，确认是否继续",
        ),
    ],
    checkpointer=InMemorySaver(),
    system_prompt=(
        "你是运维工程师的 AI 助手。处理故障时，你可以同时执行多个操作来提高效率。"
    ),
)


# =====================================================================
# 3. 运行：触发多工具同时中断
# =====================================================================

config = {"configurable": {"thread_id": "session_01"}}

print("=" * 70)
print("【用户请求】处理订单服务故障，要求同时执行三个操作")
print("=" * 70)

result = agent.invoke(
    {"messages": [{
        "role": "user",
        "content": (
            "订单服务（order-service）在 production 环境出现大量超时错误，"
            "请立即执行以下三个操作：\n"
            "1）重启[production 环境]环境的[订单服务]；\n"
            "2）给[运维告警群]发送通知，标题[订单服务紧急重启]，内容[因超时率过高，正在重启订单服务]；\n"
            "3）把配置项[order.max_retry]改成 5。\n"
            "这三个操作现在一起执行，不要逐个处理。"
        ),
    }]},
    config=config,
    version="v2",
)


# 中断信息 处理：展示中断信息，等待人工审批
if result.interrupts:
    print("触发中断，result:", result)
    interrupt_data = result.interrupts[0].value
    action_requests = interrupt_data["action_requests"]
    review_configs = interrupt_data["review_configs"]

    print(f"\nAgent 已暂停！本次中断包含 {len(action_requests)} 个待审批操作：\n")
    for i, req in enumerate(action_requests):
        print(f" ==== 操作 [{i}] ====")
        print(f" 工具名称: {req['name']}")
        print(f" 参数:     {req['args']}")
        print(f" 允许决策: {review_configs[i]['allowed_decisions']}")
        print(f" 描述:     {req['description']}")
        print(f" =====================")
    print(f"\n注意：需要按操作顺序 [0]→[1]→[2] 提供{len(action_requests)}个决策")


    # =====================================================================
    # 4. 人工逐个确认 —— 决策顺序必须与 action_requests 一致
    # =====================================================================

    print("\n" + "=" * 70)
    print("【人工确认】对每个操作逐一做出决策")
    print("=" * 70)

    decisions = []

    for i, req in enumerate(action_requests):
        print(f"\n **** 正在确认操作 [{i}]：{req['name']} ****")
        print(f"   参数: {req['args']}")
        allowed = review_configs[i]["allowed_decisions"]

        while True:
            d = input(f"   请输入决策（{'/'.join(allowed)}）: ").strip().lower()
            if d in allowed:
                break
            print(f"无效决策，该操作只允许: {allowed}")

        if d == "approve":
            decisions.append({"type": "approve"})
            print(f"已批准 —— 工具将按原参数执行")
        elif d == "reject":
            reason = input(f"请输入拒绝原因: ").strip()
            if not reason:
                reason = "人工拒绝了该操作"
            decisions.append({"type": "reject", "message": f"用户拒绝操作,原因：{reason}"})
            print(f"已拒绝 —— 原因：{reason}")

    # 确认决策列表
    print(f"\n即将提交的决策列表：{decisions}")

    # =====================================================================
    # 5. 恢复执行：将决策列表传给 Command(resume=...)
    # =====================================================================

    print("\n" + "=" * 70)
    print("【恢复 Agent 执行】")
    print("=" * 70)

    result = agent.invoke(
        Command(resume={"decisions": decisions}),
        config=config,
        version="v2",
    )

    print("result:", result)
    print(f"\n最终结果：\n{result.value['messages'][-1].content}")

else:
    print(f"\n[Agent 回复]: {result.value['messages'][-1].content}")
