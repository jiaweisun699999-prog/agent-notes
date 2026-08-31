from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver
from langgraph.prebuilt import ToolRuntime
from langgraph.store.memory import InMemoryStore
from langgraph.store.mysql import PyMySQLStore
from pydantic import BaseModel

from init_llm import deepseek_llm

@tool
def get_user_info(runtime:ToolRuntime) -> str:
    """
    从长期记忆中查询用户信息
    """
    print("runtime:",runtime)

    user_id = runtime.context.user_id

    user_info_item = store.get(
        ("users",),
        user_id
    )

    if user_info_item:
        value = user_info_item.value
        return f"用户id:{user_id},用户姓名：{value['name']},用户age:{value['age']}，用户city:{value['city']},用户hobby:{value['hobby']}"
    else:
        return "用户不存在"

class UserContext(BaseModel):
    user_id: str


DB_URI = "mysql+pymysql://root:123456@localhost:3306/langchain_db?charset=utf8mb4"


with (
    PyMySQLSaver.from_conn_string(DB_URI) as checkpointer,
    PyMySQLStore.from_conn_string(DB_URI) as store
      ):

    # 初始化数据库
    checkpointer.setup()
    store.setup()

    # 预先在长期记忆中存储一些用户信息
    store.put(
        ("users",),  # 命名空间：用户数据
        "user_123",  # 键：用户ID
        {"name": "张三", "age": 28, "city": "北京", "hobby": "编程、阅读"}  # 值：用户信息
    )
    store.put(
        ("users",),
        "user_456",
        {"name": "李四", "age": 32, "city": "上海", "hobby": "旅游、摄影"}
    )

    agent = create_agent(
        model=deepseek_llm,
        tools=[get_user_info],
        checkpointer=checkpointer,
        store = store,
        system_prompt="每次查询用户信息时，都要调用工具get_user_info",
        context_schema=UserContext
    )

    config = {"configurable":{"thread_id":"session001"}}

    resp1 = agent.invoke(
        {"messages":[{"role":"user","content":"你知道我的信息吗？"}]},
        config=config,
        context=UserContext(user_id="user_123")
    )
    print(resp1["messages"][-1].content)

    resp1 = agent.invoke(
        {"messages":[{"role":"user","content":"你知道我的信息吗？"}]},
        config=config,
        context=UserContext(user_id="user_456")
    )
    print(resp1["messages"][-1].content)


