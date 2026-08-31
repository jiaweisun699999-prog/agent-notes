"""
Store 基础操作演示
"""
import uuid
from langgraph.store.memory import InMemoryStore

# 创建内存型 Store
store = InMemoryStore()

if __name__ == "__main__":
    # 1. 定义命名空间 —— 元组格式，建议包含用户ID和分类
    user_id = "user_001"
    namespace = (user_id, "memories")

    # 2. 存入一条记忆 —— put(namespace, key, value)
    memory_id = str(uuid.uuid4())
    store.put(namespace, memory_id, {"food_preference": "不吃辣，喜欢清淡口味"})

    # 存入第二条记忆
    memory_id_2 = str(uuid.uuid4())
    store.put(namespace, memory_id_2, {"allergy": "花生过敏"})

    # 3. 读取单条记忆 —— get(namespace, key)
    item = store.get(namespace, memory_id)
    print("item:", item)
    print(f"    namespace: {item.namespace}")
    print(f"    key: {item.key}")
    print(f"    value: {item.value}")


    # 4. 搜索命名空间下的所有记忆 —— search(namespace_prefix)
    # items = store.search(namespace)
    items = store.search((user_id,))
    print(f"\n【命名空间 {namespace} 下的所有记忆（共 {len(items)} 条）】")
    for it in items:
        print(f"  [{it.key}] {it.value}")

    # 5. 删除一条记忆 —— delete(namespace, key)
    store.delete(namespace, memory_id)
    items_after = store.search(namespace)
    print(f"\n【删除后剩余 {len(items_after)} 条】")
    for it in items_after:
        print(f"  [{it.key}] {it.value}")

    # 6. 列出所有命名空间
    # 在不同命名空间存入数据，方便演示 ，已有：("user_001", "memories")
    store.put(("user_001", "preferences"), "p1", {"theme": "dark", "language": "zh"})
    store.put(("user_002", "memories"), "m1", {"note": "新用户"})
    all_ns = store.list_namespaces()
    print(f"\n【所有命名空间】{all_ns}")