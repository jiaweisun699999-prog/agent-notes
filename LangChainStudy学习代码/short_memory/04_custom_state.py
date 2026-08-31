from langchain.agents import create_agent, AgentState
from langchain_core.stores import InMemoryStore
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver

from init_llm import deepseek_llm

"""
自定义状态步骤：
 1.需要自定义一个继承自AgentState的类，将自定义的状态字段添加到类中。
 2.在创建agent时，将自定义的状态类作为state_schema参数传递。
 3.自定义状态可以在agent.invoke的时候传入，也可以在agent运行过程中通过tool/中间件设置
 
"""




@tool
def get_user_info(name: str) -> str:
    """
    根据姓名查询用户信息
    Args:
        name (str): 要查询的用户姓名
    Returns:
        str: 包含用户信息的字符串
    """
    user_db = {
        "张三": {"age": 28, "hobby": "旅游、滑雪、喝茶"},
        "李四": {"age": 32, "hobby": "编程、阅读、电影"}
    }
    info = user_db.get(name, {"age": "未知", "hobby": "未知"})
    return f"姓名: {name}, 年龄: {info['age']}岁, 爱好: {info['hobby']}"


class CustomState(AgentState):
    user_id: str
    hobby: str
    other_info: dict

agent = create_agent(
    model=deepseek_llm,
    tools=[get_user_info],
    checkpointer=InMemorySaver(),
    state_schema=CustomState
)

config = {"configurable":{"thread_id":"session001"}}

resp1 = agent.invoke({
    "messages":[{"role":"user","content":"你好,我叫张三"}],
    "user_id":"user001",
    "hobby":"旅游、滑雪、喝茶",
    "other_info":{"age":28,"gender":"男"}
},config=config)
print(resp1["messages"][-1].content)

print("-----------------")

resp2 = agent.invoke({"messages":[{"role":"user","content":"你知道我的信息吗？"}]},config=config)
print(resp2["messages"][-1].content)


print("-----------------")
state = agent.get_state(config=config)
print(type(state))
print(state)


