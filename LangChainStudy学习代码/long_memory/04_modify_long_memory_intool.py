from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langchain.tools import tool, ToolRuntime
from typing import TypedDict, Literal

from pydantic import BaseModel, Field

from init_llm import deepseek_llm
import uuid


class UserContext(BaseModel):
    user_id: str

# 定义工具输入的类型
class UserPreference(BaseModel):
    category: Literal["color", "food", "music"] = Field(description=" 用户偏好类别，必须是 'color', 'food', 'music' 中的一个")
    preference: str = Field(description="具体偏好内容，如'红色'、'中国美食'等")


# 1. 初始化存储
store = InMemoryStore()
checkpointer = InMemorySaver()


# 2. 定义写入长期记忆的工具
@tool(args_schema=UserPreference)
def save_user_preference(category: str, preference: str, runtime: ToolRuntime) -> str:
    """
    将用户偏好保存到长期记忆中。

    Args:
        category: 用户偏好类别，必须是 "color", "food", "music" 中的一个
        preference: 具体偏好内容，如'红色'、'中国美食'等
        runtime: ToolRuntime  # 包含长期记忆存储和上下文
    Returns:
        str: 操作结果描述
    """
    user_id = runtime.context.user_id

    # 创建命名空间：(user_id, "preferences")
    namespace = (user_id, "preferences")

    # 生成唯一记忆ID
    memory_id = str(uuid.uuid4())

    # 准备要保存的数据
    memory_value = {
        "category": category,
        "preference": preference,
    }

    # 保存到长期记忆
    runtime.store.put(namespace, memory_id, memory_value)

    return f"已成功保存你的{category}偏好：{preference}"


# 3. 定义读取用户偏好的工具
@tool
def get_user_preferences(runtime: ToolRuntime) -> str:
    """
    从长期记忆中获取用户特定类别的所有偏好。

    Returns:
        str: 用户的偏好列表
    """
    user_id = runtime.context.user_id
    namespace = (user_id, "preferences")

    # 搜索该命名空间下的所有记忆
    memories = runtime.store.search(namespace)

    if not memories:
        return f"您还没有保存过偏好"

    print("memories:", memories)

    # 格式化所有偏好为字符串列表
    preferences_list = []
    for mem in memories:
        pref = mem.value
        preferences_list.append(f"- 种类：{pref['category']}，偏好：{pref['preference']}")

    return f"你的偏好有：\n" + "\n".join(preferences_list)


# 4. 创建带有长期记忆读写工具的Agent
memory_agent = create_agent(
    model=deepseek_llm,
    tools=[save_user_preference, get_user_preferences],
    checkpointer=checkpointer,
    store=store,
    context_schema=UserContext
)

# 5. 演示：完整的长时期记忆读写流程
print("=== 完整演示：长期记忆的写入与跨线程读取 ===")

# 第一轮：用户保存颜色偏好（线程1）
print("第一轮（线程1）：用户保存颜色偏好")
result1 = memory_agent.invoke(
    {"messages": [{"role": "user", "content": "请记住我喜欢的颜色是蓝色"}]},
    config={"configurable": {"thread_id": "thread1"}},
    context=UserContext(user_id="current_user")
)
print(f"Agent回复: {result1['messages'][-1].content}")

# 第二轮：用户保存食物偏好（同一线程）
print("第二轮（同一线程）：用户保存食物偏好")
result2 = memory_agent.invoke(
    {"messages": [{"role": "user", "content": "我还喜欢的食物是意大利面"}]},
    config={"configurable": {"thread_id": "thread1"}},  # 同一线程
    context=UserContext(user_id="current_user")
)
print(f"Agent回复: {result2['messages'][-1].content}")

# 第三轮：在新线程中查询所有偏好
print("第三轮（新线程）：查询我的所有偏好")
result3 = memory_agent.invoke(
    {"messages": [{"role": "user", "content": "告诉我我都喜欢什么颜色和食物"}]},
    config={"configurable": {"thread_id": "thread2"}},  # 新线程
    context=UserContext(user_id="current_user")  # 相同用户
)
print(f"Agent回复: {result3['messages'][-1].content}")


# # 直接验证：从store中读取数据
# print("=== 直接验证：从长期记忆存储中读取数据 ===")
# # 读取颜色偏好
# color_memories = store.search(("current_user", "preferences"))
# print(f"长期记忆中存储的颜色偏好: {[m.value for m in color_memories if m.value['category'] == 'color']}")
#
# # 读取食物偏好
# food_memories = store.search(("current_user", "preferences"))
# print(f"长期记忆中存储的食物偏好: {[m.value for m in food_memories if m.value['category'] == 'food']}")
