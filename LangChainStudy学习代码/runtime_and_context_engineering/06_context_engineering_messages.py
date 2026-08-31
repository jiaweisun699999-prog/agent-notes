import os
from dataclasses import dataclass
from typing import Callable

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse

from init_llm import deepseek_llm

@dataclass
class Context:
    """每次调用时传入的静态配置"""
    user_name: str
    file_path: str = ""  # 要加载的文件路径，为空表示不加载任何文件


@wrap_model_call
def inject_file_to_messages(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """在模型调用前，根据 Context 中的 file_path 读取文件，注入到消息列表。
    注意点：
    - 文件路径来自 Runtime Context（静态配置，每次调用可不同）。
    - 文件内容在模型调用前被动态读取，拼装为自然语言后注入消息列表。
    - 下次模型调用时，如果 Context 中仍有 file_path，中间件会重新读取并注入。
    """
    print("request:", request)
    file_path = request.runtime.context.file_path

    if not file_path:
        # 没有传入文件路径，原样放行
        print("[消息注入] 未传入 file_path，消息列表保持不变")
        return handler(request)

    # 读取文件内容
    if not os.path.exists(file_path):
        error_msg = f"警告：文件不存在 —— {file_path}"
        messages = list(request.messages) + [{"role": "system", "content": error_msg}]
        request = request.override(messages=messages)
        return handler(request)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, "r", encoding="gbk") as f:
                content = f.read()
        except Exception:
            error_msg = f"警告：无法解码文件 {file_path}"
            messages = list(request.messages) + [{"role": "system", "content": error_msg}]
            request = request.override(messages=messages)
            return handler(request)

    file_name = os.path.basename(file_path)

    # 构造注入文本
    injected = (
        f"以下是从文件 '{file_name}' 中读取的内容：\n"
        f"========== 文件开始 ==========\n"
        f"{content}\n"
        f"========== 文件结束 ==========\n\n"
        f"请严格基于以上文件内容回答用户的问题。"
        f"如果文件中有明确信息，请直接引用；如果没有，请如实告知。"
    )

    # 注入消息：将文件内容通过“用户消息”追加到消息列表末尾
    messages = list(request.messages) + [{"role": "user", "content": injected}]
    request = request.override(messages=messages)

    print(f"[消息注入] 文件 '{file_name}' 已注入消息列表")

    return handler(request)

agent = create_agent(
    model=deepseek_llm,
    tools=[],
    middleware=[inject_file_to_messages],
    context_schema=Context,
    system_prompt="你是一个助手，可以回答用户问题。",
)

doc_path = os.path.join(
    # 获取当前脚本所在目录
    os.path.dirname(os.path.abspath(__file__)),
    "会议纪要.txt",
)

print("=" * 60)


result1 = agent.invoke(
    {"messages": [{
        "role": "user",
        "content": "项目总预算是多少？"
    }]},
    context=Context(
        user_name="张三",
        file_path=doc_path,
    ),
)
print(f"Agent 回复:{result1['messages'][-1].content}")


print("=" * 60)


result2 = agent.invoke(
    {"messages": [{
        "role": "user",
        "content": "项目总预算是多少？"
    }]},
    context=Context(
        user_name="李四",
    ),
)
print(f"Agent 回复:{result2['messages'][-1].content}")
