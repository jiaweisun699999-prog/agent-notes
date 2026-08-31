"""
售后助手
"""
import asyncio
import operator
import time
from dataclasses import dataclass
from typing import Annotated

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext, LoggingMessageNotificationParams, \
    ElicitRequestParams
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from mcp.client.streamable_http import RequestContext
from mcp.types import ElicitResult
from numpy._core.strings import isdigit

from init_llm import deepseek_llm



@dataclass
class CustomContext:
    user_id:str
    user_name:str

class CustomState(AgentState):
    audit_log: Annotated[list[str],operator.add]


#中断处理方法
async def handle_interrupts(result, agent, config, ctx):
    """
    处理一轮或多轮中断，直到 Agent 不再触发中断为止。

    返回值：最终的 GraphOutput（此时 result.interrupts 为空）
    """
    while result.interrupts:
        interrupt_data = result.interrupts[0].value
        action_requests = interrupt_data["action_requests"]
        review_configs = interrupt_data["review_configs"]

        # 展示所有待人工介入操作
        print(f"\n{'─' * 60}")
        print(f" Agent中断 —— {len(action_requests)} 个操作需要人工介入")
        print(f"{'─' * 60}")

        for i, req in enumerate(action_requests):
            cfg = review_configs[i]
            print(f"\n  [{i}] 工具名称 : {req['name']}")
            print(f"      参数    : {req['args']}")
            print(f"      允许决策 : {cfg['allowed_decisions']}")

        # 逐个收集决策（决策顺序 == action_requests 顺序）
        decisions = []

        print(f"\n{'·' * 40}")
        print("请按顺序对以上操作做出决策：")
        print(f"{'·' * 40}")

        for i, req in enumerate(action_requests):
            allowed = review_configs[i]["allowed_decisions"]

            print(f"\n 操作 [{i}] {req['name']}")
            # 展示当前参数供人工介入参考
            if req.get("args"):
                for k, v in req["args"].items():
                    print(f"     参数: {k} = {v}")

            # 可用的决策类型及说明
            hint_map = {
                "approve": "批准，按原参数执行工具",
                "edit":    "修改参数后执行工具",
                "reject":  "拒绝执行，附带反馈说明",
                "respond": "跳过工具执行，直接返回人工回复",
            }
            print("     可选操作：")
            for a in allowed:
                print(f"       > {a} — {hint_map.get(a)}")

            # 等待有效输入
            while True:
                decision = input(f"      >>> 输入操作 ({'/'.join(allowed)}): ").strip().lower()
                if decision in allowed:
                    break
                print(f"      无效输入，该操作只允许: {allowed}")

            # 根据决策类型构建决策对象
            if decision == "approve":
                decisions.append({"type": "approve"})
                print(f"      已批准 —— 工具将按原参数执行")

            elif decision == "edit":
                print(f"      请输入修改后的参数（直接回车保留原值）：")
                new_args = {}
                for k, v in req["args"].items():
                    new_val = input(f"         {k} [原值: {str(v)}]: ").strip()
                    if new_val == "":
                        new_args[k] = v  # 保留原值
                    else:
                        # 直接使用用户输入的字符串
                        new_args[k] = new_val
                decisions.append({
                    "type": "edit",
                    "edited_action": {"name": req["name"], "args": new_args},
                })
                print(f"      已修改参数: {new_args}")

            elif decision == "reject":
                reason = input(f"      请输入拒绝原因: ").strip()
                if not reason:
                    reason = "操作被人工拒绝"
                decisions.append({"type": "reject", "message": reason})
                print(f"      已拒绝:{reason}")

            elif decision == "respond":
                reply = input(f"      请输入回复内容: ").strip()
                if not reply:
                    reply = "已确认，没有补充信息。"
                decisions.append({"type": "respond", "message": reply})
                print(f"      已回复:{reply}")

        # 提交决策，恢复执行
        print(f"\n{'─' * 60}")
        print(f"提交决策列表:{decisions}")
        print(f"{'─' * 60}")

        result =await agent.ainvoke(
            Command(resume={"decisions": decisions}),
            config=config,
            context=ctx,
            version="v2",
        )

    return result


# 本地工具
@tool
def validate_phone(phone:str)->str:
    "验证手机号是否合法"
    if len(phone)==11 and phone.isdigit() and phone.startswith("1"):
        return "手机号格式正确"
    return "手机号格式错误，手机号是11位数字，且以1开头。"

# ===== 拦截器 =====
async def auth_inject(request:MCPToolCallRequest,handler):
    "从context中获取用户信息注入到工具调用参数中"
    ctx = request.runtime.context

    user_id = ctx.user_id
    user_name = ctx.user_name
    return await handler(request.override(
        args={**request.args,"caller_id":f"{user_id}({user_name})"}
    ))


async def audit_log(request:MCPToolCallRequest,handler):
    "调用工具记录审计日志，设置到状态中"
    ctx = request.runtime.context

    user_id = ctx.user_id
    user_name = ctx.user_name

    result = await handler(request)

    text = result.content[0].text

    tool_msg = ToolMessage(
        content=text,
        tool_call_id=request.runtime.tool_call_id
    )

    #准备审计日志
    logs = f"[{time.strftime("%H:%M:%S")}] {user_name} -> {request.name}:{str(request.args)}"

    return Command(
        update={
            "messages":[tool_msg],
            "audit_log":[logs]
        }
    )



# ==== 回调函数 =====
# 1. on_progress : 进度回调，用于打印当前进度
async def on_progress(
    progress:float, #当前阶段进度
        total:float, #总进度
        message:str, #当前阶段消息
        context:CallbackContext
):
    print(
        f"【进度】MCP 服务器名称：{context.server_name},当前工具名称：{context.tool_name}，当前阶段进度：{progress/total}%，当前处理消息：{message}")

# 2. on_logging_message : 日志回调，用于打印日志消息
async def on_logging_message(
       params:LoggingMessageNotificationParams,
       context:CallbackContext
    ):

    print(f"【日志】MCP 服务器名称：{context.server_name},当前工具名称：{context.tool_name}，日志级别：{params.level}，日志消息：{params.data}")

# 3. 服务端向客户端确认消息

async def on_elicitation(
        mcp_context:RequestContext,
        params:ElicitRequestParams,
        context:CallbackContext
    ):

    message = params.message

    print(f"【系统询问】-{message}")


    #用户可以选择的输入：
    options = params.requestedSchema["properties"]["value"]["enum"]

    if options:
        #打印可选选项
        for i,opt in enumerate(options,1):
            print(f"{i}. {opt}")

        #用户输入
        while True:
            selected = input(f"请输入编号（1-{len(options)}）：").strip()
            if isdigit(selected) and 0<=int(selected)<=len(options):
                selected = options[int(selected)-1]
                break
            else:
                print(f"请输入正确的选项（1-{len(options)}）")

        print(f"用户选择了：{selected}")

    else:
        selected = input("请输入：").strip()

    return ElicitResult(action="accept",content={"value": selected})


async def main():
    #1.创建MCP Client
    client = MultiServerMCPClient(
        {
            "my_order_server":{
                "transport":"http",
                "url":"http://localhost:8010/mcp"
            },
            "my_notify_server": {
                "transport": "http",
                "url": "http://localhost:8020/mcp"
            }
        },
        tool_interceptors=[auth_inject,audit_log],
        callbacks=Callbacks(
            on_progress=on_progress,
            on_logging_message=on_logging_message,
            on_elicitation=on_elicitation
        )
    )

    # 2.获取远程工具
    tools = await client.get_tools()

    # 3.加载Resource和Prompt
    blobs = await client.get_resources("my_notify_server",uris=["company://policies/return"])
    policy_text = "\n".join(b.as_string() for b in blobs)

    msgs = await client.get_prompt("my_notify_server","refund_response_prompt",
                                      arguments={"order_id":"{退款订单号}","amount":"{退款金额}"})
    # 提示词模版
    prompts = msgs[0].content

    # 4.创建Agent
    all_tools = tools+[validate_phone]
    agent = create_agent(
        model=deepseek_llm,
        tools=all_tools,
        checkpointer=MemorySaver(),
        context_schema=CustomContext,
        state_schema=CustomState,
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "process_refund":{
                        "allowed_decisions":["approve","reject"],
                        "description":"退款操作需要人工确认，是否同意退款？"
                    }
                }

            )
        ],
        system_prompt=f"""你是电商售后客服助手。
            工作流程：
            1. 查询订单时调用 query_order。如果订单不存在，直接告知用户不要重试。
            2. 退款时先查询订单确认状态和金额。
            3. 退款成功后询问用户是否需要短信通知。如果要通知，先调用 validate_phone 校验手机号，再用 send_sms 发送。
            4. 涉及退换货政策问题时，参考以下政策：
            {policy_text}
            5. 回复退款结果时，参考以下模板：
            {prompts}
        """
    )

    ctx = CustomContext(user_id="user_zhangsan",user_name="张三")

    config={"configurable":{"thread_id":"session_001"}}

    print("="*70)
    print("电商智能售后客服")
    print("=" * 70)

    while True:
        try:
            user_input = input("[用户]：").strip()

            if not user_input:
                continue

            if user_input=="exit":
                print("系统退出...")
                break

            result = await agent.ainvoke(
                {"messages":[{"role":"user","content":user_input}]},
                config=config,
                context=ctx,
                version="v2"
            )

            # 处理中断
            result = await handle_interrupts(result, agent, config, ctx)

            # 输出最终回复
            final_msg = result.value["messages"][-1].content
            print("[助手]：",final_msg)

            # 获取审计记录
            audit_logs = result.value.get("audit_log",[])
            print("审计记录：")
            for log in audit_logs:
                print(log)

        except Exception as e:
            print(f"发生错误：{e}")



if __name__ == '__main__':
    asyncio.run(main())









