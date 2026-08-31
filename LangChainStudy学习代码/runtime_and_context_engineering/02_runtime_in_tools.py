from dataclasses import dataclass

from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langgraph.store.memory import InMemoryStore

from init_llm import deepseek_llm


# 定义上下文类型
@dataclass
class Context:
    """每次 Agent 调用时传入的用户相关信息"""
    user_id: str
    user_name: str


# 定义工具：在签名中使用 ToolRuntime[Context] 来注入 Runtime
@tool
def fetch_user_preferences(runtime: ToolRuntime[Context]) -> str:
    """获取当前客服的邮件偏好设置（来自长期记忆 Store）。

    当需要了解客服希望在邮件中使用什么语气、什么格式时调用此工具。
    """
    print("runtime",runtime)
    user_id = runtime.context.user_id

    # 尝试从 Store（长期记忆）中读取已有偏好
    if runtime.store is not None:
        memory = runtime.store.get(("email_preferences",), user_id)
        if memory is not None:
            prefs = memory.value
            return (
                f"客服 {runtime.context.user_name} 的邮件偏好："
                f"语气={prefs.get('tone', '专业')}，"
                f"签名格式={prefs.get('signature', '标准')}"
            )

    # 如果 Store 中没有记录，返回默认偏好
    return f"用户 {runtime.context.user_name} 暂无特殊偏好，使用默认设置（专业语气，标准签名）"


@tool
def send_email(
    email_content: str,
    runtime: ToolRuntime[Context],
) -> str:
    """向全部用户发送邮件

    Args:
        email_content: 邮件的正文内容
    """
    user = runtime.context.user_name
    print(f"邮件内容：{email_content}")
    # 在真实场景中，这里会调用邮件服务的 API
    return f"客服 {user} 已向全部用户发送邮件，内容：{email_content}"


# 初始化 Store，预置一些用户偏好数据
store = InMemoryStore()
store.put(("email_preferences",), "user_001", {
    "tone": "亲切",
    "signature": "此致敬礼，客服小张",
})

# 创建 Agent
agent = create_agent(
    model=deepseek_llm,
    tools=[fetch_user_preferences, send_email],
    context_schema=Context,
    store=store,
    system_prompt="你是一个电商客服助手，可以调用fetch_user_preferences工具获取客服邮件偏好设置，"
                  "并使用send_email工具向全部用户发送邮件。",
)

# 调用 Agent：传入具体的上下文
result = agent.invoke(
    {"messages": [{
        "role": "user",
        "content": "查看我的邮件偏好设置，然后给所有用户发送感谢邮件。",
    }]},
    context=Context(user_id="user_001", user_name="客服张三"),
)

print(result)
print(result["messages"][-1].content)