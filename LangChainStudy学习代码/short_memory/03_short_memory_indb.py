from langchain.agents import create_agent
from langchain_core.stores import InMemoryStore
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver

from init_llm import deepseek_llm

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




DB_URI = "mysql+pymysql://root:123456@localhost:3306/langchain_db?charset=utf8mb4"


with PyMySQLSaver.from_conn_string(DB_URI) as checkpointer:

    # 创建表
    checkpointer.setup()

    agent = create_agent(
        model=deepseek_llm,
        tools=[get_user_info],
        checkpointer=checkpointer
    )

    config = {"configurable":{"thread_id":"session001"}}

    resp1 = agent.invoke({"messages":[{"role":"user","content":"你好,我叫张三"}]},config=config)
    print(resp1["messages"][-1].content)

    print("-----------------")

    resp2 = agent.invoke({"messages":[{"role":"user","content":"你知道我的信息吗？"}]},config=config)
    print(resp2["messages"][-1].content)

    state = agent.get_state(config=config)
    print(type(state))
    print(state)


