from typing import NotRequired, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


# ================================================================
# 一、定义状态
# ================================================================
class State(TypedDict):
    action_to_execute: NotRequired[str]      # AI 生成的退款方案
    final_message: NotRequired[str]          # 最终结果


# ================================================================
# 二、定义节点
# ================================================================
def plan_action(state: State):
    """模拟 AI 生成退款方案"""
    planned_action = "为订单 ORD123 退款 100 元（原因为：商品破损）"
    print(f"\n>>> [AI 方案] {planned_action}")
    return {"action_to_execute": planned_action}


def human_approval_node(state: State):
    """HITL 核心节点：中断等待人工审批/修改/取消"""
    planned_action = state.get("action_to_execute", "无方案")
    # 中断，等待用户通过 Command(resume=...) 恢复
    user_feedback = interrupt({
        "message": "请审批或修改以下退款方案(approve/modify:退款新方案/其他输入取消)：",
        "current_plan": planned_action
    })

    if user_feedback.lower() == 'approve':
        print(">>> 退款方案已批准。")
        return {}
    else:
        print(">>> 退款方案已取消。")
        return {"action_to_execute": None}


def execute_action(state: State):
    """执行最终确定的退款方案（模拟执行退款）"""
    action = state.get("action_to_execute")
    if not action:
        return {"final_message": "没有可执行的退款方案。"}
    return {"final_message": f"退款成功：{action}"}


# ================================================================
# 三、构建主图
# ================================================================
builder = StateGraph(State)
builder.add_node("plan_action", plan_action)
builder.add_node("human_approval_node", human_approval_node)
builder.add_node("execute_action", execute_action)

builder.add_edge(START, "plan_action")
builder.add_edge("plan_action", "human_approval_node")
builder.add_edge("human_approval_node", "execute_action")
builder.add_edge("execute_action", END)

graph = builder.compile(checkpointer=InMemorySaver())

# ================================================================
# 四、辅助函数
# ================================================================
def get_user_input(interrupt_value):
    """根据中断信息向用户提问并读取输入"""
    if isinstance(interrupt_value, str):
        return input(f"\n[助手]: {interrupt_value}\n[用户]: ").strip()
    if isinstance(interrupt_value, dict):
        show = "\n".join(f"  {k}: {v}" for k, v in interrupt_value.items())
        return input(f"\n[助手]: 需要人工确认 -\n{show}\n[用户]: ").strip()
    return input(f"\n[用户]: ").strip()


# ================================================================
# 五、实时对话主循环（使用 stream_events）
# ================================================================
def run_dialog():
    config = {"configurable": {"thread_id": "thread001"}}

    # 首次启动：传入空状态
    stream_input: dict | Command = {}

    while True:
        # 使用 stream_events 事件流 API
        stream = graph.stream_events(stream_input, config=config, version="v3")

        # 检查是否发生中断
        if stream.interrupted:
            interrupt_value = stream.interrupts[0].value if stream.interrupts else None
            print("\n===== 等待人工决策 =====")

            # 获取用户输入
            user_decision = get_user_input(interrupt_value)

            # ===== 时间旅行分支 =====
            if user_decision.lower().startswith('modify:'):
                new_plan = user_decision[len('modify:'):].strip()
                print(f"\n>>> 用户修改退款方案为: {new_plan}")

                # 1. 获取当前中断点的配置（即历史检查点）
                history = list(graph.get_state_history(config))
                before_human_approval_node = next(s for s in history if s.next == ("human_approval_node",))

                # 2. 使用 update_state 在历史检查点上创建新分支
                #    创建一个新检查点，action_to_execute 更新为新计划
                new_config = graph.update_state(
                    before_human_approval_node.config,
                    {"action_to_execute": new_plan},
                    as_node="human_approval_node"  # 表示该修改由该节点产生
                )

                # 3. 更新 config 为新分支的配置
                config = new_config

                # 4. 用 Command(resume=...) 放行本次中断
                stream_input = Command(resume="xxx")

            else:
                # 普通审批或取消，直接恢复
                stream_input = Command(resume=user_decision)

        else:
            # 如果没有中断，说明图执行完毕
            final_state = stream.output
            final_msg = final_state.get("final_message", "未返回最终信息")
            print(f"\n===== 最终回复：{final_msg} =====")
            print("\n===== 本轮任务结束 =====\n")
            break


if __name__ == "__main__":
    run_dialog()