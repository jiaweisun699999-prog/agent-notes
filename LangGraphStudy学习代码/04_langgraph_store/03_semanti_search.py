

"""
store 语义搜索
"""
import uuid

from langgraph.store.memory import InMemoryStore

from env_utils import DASHSCOPE_API_KEY
from langchain.embeddings import init_embeddings
from langchain_community.embeddings import DashScopeEmbeddings

# 1. 准备嵌入模型 - Embedding Model
embedding_model = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=DASHSCOPE_API_KEY,
)

test_vec = embedding_model.embed_query("你好")

print(test_vec)

dims = len(test_vec)

print(dims)

# 2.创建带语义索引的 Store，需要通过index参数来指定嵌入模型相关参数
store = InMemoryStore(
    index={
        "embed": embedding_model, # 指定嵌入模型
        "dims": dims, # 指定嵌入维度
        "fields": ["$"] # 要嵌入的字段，"$"表示所有的key的value 串成一个json 一起嵌入
    }

)

ns = ("user_001", "memories")

# 3. 存入中文用户偏好
store.put(ns, str(uuid.uuid4()), {"food_preference": "我喜欢吃川菜，尤其是麻辣火锅"})
store.put(ns, str(uuid.uuid4()), {"food_preference": "夏天最喜欢喝冰镇柠檬茶"})
store.put(ns, str(uuid.uuid4()), {"hobby": "周末喜欢去爬山和徒步"})
store.put(ns, str(uuid.uuid4()), {"food_preference": "喜欢清淡的粤菜，不爱吃辣"})


# 4. 语义搜索
results = store.search(ns,query="用户喜欢吃什么辣的东西？",limit=2)

for item in results:
    print(item.key, item.value)


print("=====================")
results = store.search(ns,query="用户喜欢什么运动？",limit=1)

for item in results:
    print(item.key, item.value)

print("=====================")
#不传入query，退化为普通列表查询
results = store.search(ns)

for item in results:

    print(item.key, item.value)
