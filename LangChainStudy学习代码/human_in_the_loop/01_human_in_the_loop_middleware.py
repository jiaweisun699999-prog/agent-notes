"""
HITL 人工介入 怎么做？

"""
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from init_llm import deepseek_llm


@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息。"""
    return f"{city}的天气为晴朗，25°C。"

@tool
def read_file(file_path: str) -> str:
    """读取指定文件"""
    return f"文件 {file_path} 已成功读取！"

@tool
def delete_file(file_path: str) -> str:
    """删除指定文件"""
    return f"文件 {file_path} 已成功删除！"

agent = create_agent(
    model=deepseek_llm,
    tools=[get_weather, read_file, delete_file],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on= {
                "read_file":False, # 读取文件时，不人工介入
                "delete_file":True, # 删除文件时，人工介入

            },
            description_prefix= "需要人工介入，请确认操作！"
        ),
    ],
    checkpointer=InMemorySaver(),
    system_prompt="你是一个智能助手，可以回答用户问题。"
)

config = {"configurable":{"thread_id":"session_01"}}

result = agent.invoke(
    {"messages":[{"role":"user","content":"先给我查询天气，在给我读取a.txt文件，最后删除这个文件"}]},
# {"messages":[{"role":"user","content":"你叫什么名字"}]},
    config=config,
    version="v2"
)

print(result)

# 获取中断信息
if result.interrupts:
    req = result.interrupts[0].value["action_requests"][0]
    print(f"待确认执行的工具：{req["name"]}")
    print(f"工具参数：{req["args"]}")
    print(f"描述：{req["description"]}")

    allowed_decisions = result.interrupts[0].value["review_configs"][0]["allowed_decisions"]
    print(f"用户可以确认的操作：{allowed_decisions}")


else:

    print(result.value["messages"][-1].content)

print("------------")

result2 = agent.invoke(
    Command(resume={"decisions":[{"type":"approve"}]}),
    config=config,
    version="v2"
)

print(result2.value["messages"][-1].content)






