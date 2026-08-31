from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from init_llm import deepseek_llm


store=InMemoryStore()

# 定义命名空间
namespace = ("user1","preferences")

store.put(
    namespace,
    "city",
    {"like":["北京","上海"],"dislike":["广州"]}
)


store.put(
    namespace,
    "fruit",
    {"like":["苹果","香蕉"],"dislike":["橙子"]}
)

memoery = store.get(
    namespace,"city"
    )
# print("memoery:",memoery)


all_memory = store.search(namespace)
for item in all_memory:
    print("key",item.key)
    print("value",item.value)

# print("all_memory:",all_memory)





# print("-----------------")
#
# store.put(
#     namespace,
#     "张三",
#     {"like":["北京","广州"],"dislike":["美国"]}
# )
#
#
# memoery = store.get(
#     namespace,key="张三"
#     )
#
#
# print("memoery:",memoery)









