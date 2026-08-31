"""
Store 分页查询演示
"""
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

if __name__ == "__main__":
    ns = ("user_001", "logs")
    # 存入 15 条模拟日志
    for i in range(15):
        store.put(ns, f"log_{i}", {"event": f"action_{i}", "result": "ok"})


    # 默认limit是10，这里设置为100，查看是否返回所有条目
    print(f"\n总条目数: {len(store.search(ns, limit=100))}")

    # 分页查询：每页 5 条
    page_size = 5
    offset = 0
    page_num = 1

    while True:
        # limit 是每页返回的条目数，offset 是偏移量，表示从第 offset 条开始返回
        page = store.search(ns, limit=page_size, offset=offset)
        if not page:
            break
        print(f"--- 第 {page_num} 页（limit={page_size}, offset={offset}）---")
        for it in page:
            print(f"  [{it.key}] {it.value}")
        offset += page_size
        page_num += 1


    # 列出命名空间 —— 支持前缀过滤和深度控制 ,已有：("user_001", "logs")
    store.put(("user_001", "settings", "ui"), "s1", {"font": "large"})
    store.put(("user_001", "settings", "notifications"), "s2", {"email": True})

    # max_depth 控制返回的命名空间层级深度
    ns_list = store.list_namespaces(prefix=("user_001",), max_depth=2)
    print(f"\n【user_001 下前 2 层命名空间】{ns_list}")

    ns_list = store.list_namespaces(prefix=("user_001",), max_depth=3)
    print(f"\n【user_001 下前 3 层命名空间】{ns_list}")
