> 📌 **[AI 大模型与云原生全栈知识库](./README.md)** / **模块六：LangGraph 复杂 Workflow 与图状态网络**
> 🏠 [返回主页 README](./README.md) \| ⚡ [面试 30 分钟速记](./interview/00_面试冲刺30分钟速记卡片.md) \| 🎓 [本模块面试题](./interview/04_LangGraph高级工作流面试题.md)

---

# 4\. **Store长期记忆**

## 4.1. **什么是Store**

Store 是 LangGraph 的跨线程长期记忆存储层。它允许你将任意的键值数据持久化到命名空间中，并且这些数据可以被任何线程（thread）访问——无论是同一个用户的不同会话，还是整个应用的所有用户。

与 Checkpointer 保存图状态的完整快照不同，Store 保存的是应用自定义的、结构化的键值数据。你可以把它理解为一个带命名空间和语义搜索能力的 NoSQL 数据库，专为 Agent 记忆设计。

## 4.2. **Checkpointer与Store对比**

如下是短期记忆和长期记忆区别：

| **对比维度**     | **短期记忆（Short-term Memory）**                              | **长期记忆（Long-term Memory）**                                   |
| ---------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **作用域**       | 线程/会话范围记忆 (Thread-scoped)。与单个会话线程 (thread_id) 绑定。 | 跨线程/会话记忆。存储在自定义命名空间 (namespace) 中，可被多个线程共享。 |
| **核心目的**     | 保证单次对话的连贯性和上下文感知。                                   | 实现跨对话的个性化、知识积累和持续学习。                                 |
| **主要存储内容** | 图状态完整快照。                                                     | 从交互中提炼的结构化知识（如用户事实、行为经验、优化规则）。             |
| **管理组件**     | 检查点 (Checkpointer)，如 InMemorySaver、PyMySQLSaver。              | 存储 (Store)，如 InMemoryStore、PostgresStore。                          |
| **访问方式**     | 通过thread_id 在config 中指定，每个super-step自动保存                | 在节点/工具中通过 Runtime.store 读写，需手动读写                         |
| **典型应用场景** | 会话连续性、人机协同、时间旅行                                       | 用户偏好、知识积累、跨会话共享数据                                       |

## 4.3. **Store基本操作**

在将 Store 集成到 LangGraph 图之前，先理解 Store 本身的基本操作。Store 可以脱离 LangGraph 图独立使用——就像使用一个普通的键值数据库。

### **4.3.1. 初始化Store**

LangGrap中长期记忆通过存储（Store）组件来实现，Store允许你将记忆保存为JSON文档，并通过命名空间（namespace）和键（Key）进行组织和管理，便于后续的检索、更新与删除。

* 命名空间（namespace）：类似于文件夹，用于对记忆进行逻辑分组（例如，按应用场景划分）。
* 键（key）：命名空间内每个文档的唯一标识符。

Store存储支持基本的put（写入）、get（读取）、search（搜索）操作，如下案例中演示基于内存store存储的基本操作。

```python
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
    # 在不同命名空间存入数据，方便演示
    store.put(("user_001", "preferences"), "p1", {"theme": "dark", "language": "zh"})
    store.put(("user_002", "memories"), "m1", {"note": "新用户"})
    all_ns = store.list_namespaces()
    print(f"\n【所有命名空间】{all_ns}")

```

以上代码运行结果如下：

![image.png](./images/23Store长期记忆_822720b575454f7f8b529749798cc940_40abd3.jpg)

以上代码注意如下几点：

1) ("user\_001", "memories")是元组，元组的层级结构允许你用 ("user\_001",) 作为前缀匹配该用户的所有记忆类型，也可以精确匹配到 ("user\_001", "memories")。
2) 在同一个命名空间内，key 必须唯一；put 相同 key 会覆盖旧值。推荐使用 UUID 作为 key。
3) value是必须是可以 JSON 序列化的字典结构，不能存自定义 Python 对象。
4) InMemoryStore 在进程重启后数据丢失，仅适合开发测试，生产环境应使用持久化 Store。
5) [store.search](http://store.search)(ns) 默认 limit=10，最多返回 10 条；通过 limit 参数可以指定返回条数。
6) namespace设计建议

命名空间决定了数据的隔离和检索方式，设计得当可以避免很多后续问题：

```python
命名空间结构示例：
("user_001", "memories")     ← 用户001的记忆
("user_001", "preferences")  ← 用户001的偏好设置
("user_001", "orders")       ← 用户001的订单历史
("user_002", "memories")     ← 用户002的记忆
("global", "faq")            ← 全局FAQ知识
```

namespace设计建议如下：

* 第一级用user\_id或org\_id，确保用户间天然隔离
* 第二级用语义化的分类名："memories"、"preferences"、"orders" 等
* 可以扩展到更多层级：("org\_1", "dept\_a", "projects")

### **4.3.2. 分页查询**

当命名空间中的数据量很大时，需要通过分页来控制每次返回的数量：

```python
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


    # 列出命名空间 —— 支持前缀过滤和深度控制
    store.put(("user_001", "settings", "ui"), "s1", {"font": "large"})
    store.put(("user_001", "settings", "notifications"), "s2", {"email": True})

    # max_depth 控制返回的命名空间层级深度
    ns_list = store.list_namespaces(prefix=("user_001",), max_depth=2)
    print(f"\n【user_001 下前 2 层命名空间】{ns_list}")

    ns_list = store.list_namespaces(prefix=("user_001",), max_depth=3)
    print(f"\n【user_001 下前 3 层命名空间】{ns_list}")

```

以上代码运行结果如下：

![image.png](./images/23Store长期记忆_19554b9ed7894c499d1d27d6c549a685_9bae8f.jpg)

以上代码注意如下几点：

1) limit 和 offset 是控制返回数量的标准分页参数，和 SQL 的 LIMIT / OFFSET 语义一致。
2) 不同 Store 后端的默认排序不同，InMemoryStore 按插入顺序返回（最旧在前）；PostgresStore 按 updated\_at 降序（最新更新在前）。如果顺序重要，在客户端自行排序。
3) list\_namespaces 的 max\_depth 用于控制命名空间层级深度

### **4.3.3. 语义搜索**

除了通过 key 精确查找和 namespace 前缀匹配外，Store 还支持语义搜索——根据含义（而非精确文本）来查找相关记忆。比如用户问"我喜欢吃什么？"，不需要精确匹配"food"这个 key，Store 会根据语义找到最相关的记忆。

#### **4.3.3.1. 语义搜索原理-余弦相似度**

余弦相似度是一种衡量两个向量方向相似程度的度量方法，通过计算它们夹角的余弦值来评估相似性，广泛应用于文本分析、数据挖掘等领域‌。

余弦相似度的数学本质是向量空间模型中夹角的余弦值，计算公式为两个向量的点积除以它们的模长乘积。对于n维向量A和B，公式可表示为：

![image.png](./images/23Store长期记忆_47f80957dcc5477d9bbf8b303f521be8_a7b2c1.jpg)

其值范围在-1到1之间，1表示完全相同，-1表示完全相反，0表示无关。

余弦相似度典型应用场景如下：

* 文本相似度计算‌：将文档转化为词频向量后，通过余弦相似度比较内容相似性。‌‌
* 聚类分析‌：衡量数据点在高维空间中的分布方向是否相近，常用于推荐系统或异常检测。

在LangGraph中，语义搜索的原理就是将存入到Store中的文字通过Embedding Model（嵌入模型）转换成向量，当用户进行查询时，将用户的输入也转换成向量，然后使用余弦相似度找出与用户输入最相似的内容。

特别注意：Store 在 put() 时立即计算并存储向量，search(query=...) 时只对查询文本做一次向量化，然后与已存储的向量做相似度匹配，存储在Store中的向量并不提供对外暴漏的API。

#### **4.3.3.2. 语义搜索代码**

在创建Store时通过index参数配置并嵌入模型，如下案例使用阿里云百炼（DashScope）的“text-embedding-v1”模型演示如何使用。

关于更多阿里云百炼提供的嵌入模型可以参考：[https://help.aliyun.com/zh/model-studio/embedding#ee47f9d186aa2](https://help.aliyun.com/zh/model-studio/embedding#ee47f9d186aa2)

首先在对应的python环境中安装依赖：

```python
pip install langchain-community==0.4.2
pip install dashscope
```

```python
"""
Store 语义搜索
"""
import uuid

from env_utils import DASHSCOPE_API_KEY
from langchain_community.embeddings import DashScopeEmbeddings
from langgraph.store.memory import InMemoryStore

# 1. 初始化千问嵌入模型
embed_model = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=DASHSCOPE_API_KEY,
)


# 先测一下嵌入维度（text-embedding-v1 输出 1536 维向量）
test_vec = embed_model.embed_query("你好")

dims = len(test_vec)

print(f"嵌入维度: {dims}")


# 2. 创建带语义索引的 Store，需要传入index 参数
store = InMemoryStore(
    index={
        "embed": embed_model,       # 嵌入模型实例
        "dims": dims,               # 向量维度，必须和模型输出一致
        "fields": ["$"],            # 要嵌入的字段，"$" 表示所有 key 的 value 串成一条 JSON 一起嵌入
    }
)


if __name__ == "__main__":
    ns = ("user_001", "memories")

    # 3. 存入中文用户偏好
    store.put(ns, str(uuid.uuid4()), {"food_preference": "我喜欢吃川菜，尤其是麻辣火锅"})
    store.put(ns, str(uuid.uuid4()), {"food_preference": "夏天最喜欢喝冰镇柠檬茶"})
    store.put(ns, str(uuid.uuid4()), {"hobby": "周末喜欢去爬山和徒步"})
    store.put(ns, str(uuid.uuid4()), {"food_preference": "喜欢清淡的粤菜，不爱吃辣"})

    # 4. 语义搜索：按含义匹配，返回结果带 score
    # 这里limit返回1表示找到最相关的条目
    results = store.search(ns, query="用户喜欢吃什么辣的东西？", limit=1)
    for item in results:
        print(f"  score={item.score} | {item.value}")

    results = store.search(ns, query="用户喜欢什么户外运动？", limit=1)
    for item in results:
        print(f"  score={item.score} | {item.value}")

    # 5. 当不传 query 时，退化为普通列表查询（无 score）
    all_items = store.search(ns)
    for item in all_items:
        print(f"key: {item.key}, value: {item.value}")

```

以上代码运行结果如下：

![image.png](./images/23Store长期记忆_4d50ed190ad34ebdb8dd9f73d3a56d92_0a1f11.jpg)

以上代码注意如下几点：

1) 需要在env\_[utils.py](http://utils.py)文件中配置DASHSCOPE\_API\_KEY,可以通过“[https://bailian.console.aliyun.com/cn-beijing?tab=model#/api-key”获取apikey。](https://bailian.console.aliyun.com/cn-beijing?tab=model#/api-key”获取apikey。)
2) index 的三个参数：embed（嵌入模型实例）、dims（向量维度，必须和模型输出一致，text-embedding-v1 输出 1536 维）、fields（要嵌入的字段，"$" 表示整个 value 字典的所有值都会被嵌入，"$" 会把整个 value 字典序列化成一条 JSON 字符串，生成一个向量）。
3) query传入自然语言查询，Store 会自动将其转为向量，与存储的记忆做余弦相似度计算。结果中每条 SearchItem 多出一个 score 字段（取值范围 -1 到 1，越大越相关）。
4) 不传 query 退化为普通列表查询,结果不带 score，按后端默认顺序返回，不需要语义搜索时，不传 query 即可，不需要额外配置。
5) 存数据时可以通过 put(..., index=False) 让某条数据不参与语义搜索（可被精确查询但不可被语义搜索命中），或通过 put(..., index=\["food\_preference"\]) 只索引指定字段而非整个 value。

## 4.4. **在LangGraph中使用Store**

以上是 Store 的独立用法，下面演示在 LangGraph 图内部使用 Store ，在图执行时读写长期记忆。

如下案例构建的Graph通过 builder.compile(store=store) 将 Store 注入Graph图，节点函数通过 Runtime 对象访问 Store。

```python
"""
Store 跨线程共享：在一个线程中存入偏好，另一个线程中读取
"""
from dataclasses import dataclass
from typing import Annotated
from operator import add
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.runtime import Runtime
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage


# ============================================================
# 1. 数据结构
# ============================================================
@dataclass
class Context:
    user_id: str


class ChatState(TypedDict):
    messages: Annotated[list[AnyMessage], add]


# ============================================================
# 2. 初始化
# ============================================================
store = InMemoryStore()
checkpointer = InMemorySaver()


# ============================================================
# 3. 节点
# ============================================================
def save_preference(state: ChatState, runtime: Runtime[Context]):
    """节点1：从用户消息中提取偏好，存入 Store"""
    user_id = runtime.context.user_id
    user_msg = state["messages"][-1].content

    # 如果消息中包含"偏好"，则解析并存入 Store
    if "偏好" in user_msg:
        # 获取偏好后的内容存储在store中
        preference = user_msg.split("偏好")[-1].strip() if "偏好" in user_msg else user_msg

        # 存储偏好到 Store
        runtime.store.put(
            (user_id, "memories"),
            "user_pref",
            {"preference": preference},
        )
        return {"messages": [AIMessage(content=f"已记住你的偏好: {preference}")]}
    return {"messages": [AIMessage(content="收到你的消息。")]}


def greet_with_preference(state: ChatState, runtime: Runtime[Context]):
    """节点2：从 Store 读取偏好，生成个性化问候"""
    user_id = runtime.context.user_id
    ns = (user_id, "memories")

    # 读取该用户在 Store 中的所有记忆
    if runtime.store:
        items = runtime.store.search(ns)
    else:
        items = []

    # 组装偏好信息
    if items:
        prefs = [item.value.get("preference", "") for item in items if "preference" in item.value]
        pref_text = "\n".join(prefs)
        greeting = f"你好！根据你的偏好：【{pref_text}】，为你推荐相关内容。"
    else:
        greeting = "你好，新用户！请告诉我你的偏好，我会记住的。"

    return {"messages": [AIMessage(content=greeting)]}


# ============================================================
# 4. 构建图: START → save_preference → greet_with_preference → END
# ============================================================
builder = StateGraph(state_schema=ChatState, context_schema=Context)

builder.add_node("save_preference", save_preference)
builder.add_node("greet_with_preference", greet_with_preference)

builder.add_edge(START, "save_preference")
builder.add_edge("save_preference", "greet_with_preference")
builder.add_edge("greet_with_preference", END)

graph = builder.compile(checkpointer=checkpointer, store=store)

# ============================================================
# 5. 使用graph图
# ============================================================
if __name__ == "__main__":
    # 场景1：user_001 设置偏好 (thread_1)
    config1 = {"configurable": {"thread_id": "thread_1"}}

    result1 = graph.invoke(
        {"messages": [HumanMessage(content="我的偏好喜欢吃辣的")]},
        config1,
        context=Context(user_id="user_001"),
    )

    for msg in result1["messages"]:
        msg.pretty_print()

    print("*" * 100)


    # 场景2：user_001 新会话 (thread_2),可以看到在 Store 跨线程中读取到偏好

    config2 = {"configurable": {"thread_id": "thread_2"}}
    result2 = graph.invoke(
        {"messages": [HumanMessage(content="随便聊聊")]},
        config2,
        context=Context(user_id="user_001"),
    )
    for msg in result2["messages"]:
        msg.pretty_print()

    print("*" * 100)

    # 场景3：user_002 在 thread_1 中，可以看到过往的State，但是Store中存储没有user_002的偏好
    config3 = {"configurable": {"thread_id": "thread_1"}}
    result3 = graph.invoke(
        {"messages": [HumanMessage(content="你好")]},
        config3,
        context=Context(user_id="user_002"),
    )
    for msg in result3["messages"]:
        msg.pretty_print()

```

以上代码运行结果如下：

![image.png](./images/23Store长期记忆_a8c4b447f498477bbb7d8dd2cdbd70dc_90ff41.jpg)

![image.png](./images/23Store长期记忆_deceae2789574ee0b592bec9aa96632d_d11f78.jpg)

以上代码中注意如下几点：

1) Runtime 是自动注入的，只要在节点函数参数中声明 runtime: Runtime\[Context\]，LangGraph 会在执行时自动注入，不需要在 add\_node 时做任何特殊处理。
2) Context 是每次调用的动态数据，通过 graph.invoke(..., context=Context(user\_id="...")) 传入，context 中的数据不会被 Checkpointer 持久化，每次调用都需要显式传入。

## 4.5. **Store后端存储实现**

与 Checkpointer 类似，Store 也有相同的后端实现，例如InMemoryStore、PostgreStore、MongoDBStore、RedisStore，InMemoryStore适合开发、测试环境，后面的适合生产环境。

下面改造之前案例，使用PostgreStore存储Checkpoint和Store。

```python
"""
Store 跨线程共享，使用PostgreSQL数据库存储用户偏好
"""
from dataclasses import dataclass
from typing import Annotated
from operator import add
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from langgraph.runtime import Runtime
from langchain_core.messages import HumanMessage, AIMessage, AnyMessage


# ============================================================
# 1. 数据结构
# ============================================================
@dataclass
class Context:
    user_id: str


class ChatState(TypedDict):
    messages: Annotated[list[AnyMessage], add]


# ============================================================
# 2. 节点
# ============================================================
def save_preference(state: ChatState, runtime: Runtime[Context]):
    user_id = runtime.context.user_id
    user_msg = state["messages"][-1].content

    if "偏好" in user_msg:
        preference = user_msg.split("偏好")[-1].strip()
        runtime.store.put(
            (user_id, "memories"),
            "user_pref",
            {"preference": preference},
        )
        return {"messages": [AIMessage(content=f"已记住你的偏好: {preference}")]}
    return {"messages": [AIMessage(content="收到你的消息。")]}


def greet_with_preference(state: ChatState, runtime: Runtime[Context]):
    user_id = runtime.context.user_id
    ns = (user_id, "memories")

    if runtime.store:
        items = runtime.store.search(ns)
    else:
        items = []

    if items:
        prefs = [item.value.get("preference", "") for item in items if "preference" in item.value]
        pref_text = "\n".join(prefs)
        greeting = f"你好！根据你的偏好：【{pref_text}】，为你推荐相关内容。"
    else:
        greeting = "你好，新用户！请告诉我你的偏好，我会记住的。"

    return {"messages": [AIMessage(content=greeting)]}


# ============================================================
# 3. 构建图
# ============================================================
builder = StateGraph(state_schema=ChatState, context_schema=Context)
builder.add_node("save_preference", save_preference)
builder.add_node("greet_with_preference", greet_with_preference)
builder.add_edge(START, "save_preference")
builder.add_edge("save_preference", "greet_with_preference")
builder.add_edge("greet_with_preference", END)


# ============================================================
# 4. 运行 —— 仅此处改为 PostgreSQL
# ============================================================
if __name__ == "__main__":
    DB_URI = "postgresql://postgres:postgres123@192.168.179.5:5432/langgraph_db"

    # PostgresSaver 和 PostgresStore 都是上下文管理器,所有 graph 操作必须在这两个 with 内部完成
    with (
        PostgresSaver.from_conn_string(DB_URI) as checkpointer,
        PostgresStore.from_conn_string(DB_URI) as store,
    ):
        checkpointer.setup()   # 首次运行建表
        store.setup()           # 首次运行建表
        graph = builder.compile(checkpointer=checkpointer, store=store)

        # ---- 场景1 ----
        config1 = {"configurable": {"thread_id": "thread_1"}}
        result1 = graph.invoke(
            {"messages": [HumanMessage(content="我的偏好喜欢吃辣的")]},
            config1,
            context=Context(user_id="user_001"),
        )
        for msg in result1["messages"]:
            msg.pretty_print()
        print("*" * 100)

        # ---- 场景2 ----
        config2 = {"configurable": {"thread_id": "thread_2"}}
        result2 = graph.invoke(
            {"messages": [HumanMessage(content="随便聊聊")]},
            config2,
            context=Context(user_id="user_001"),
        )
        for msg in result2["messages"]:
            msg.pretty_print()
        print("*" * 100)

        # ---- 场景3 ----
        config3 = {"configurable": {"thread_id": "thread_1"}}
        result3 = graph.invoke(
            {"messages": [HumanMessage(content="你好")]},
            config3,
            context=Context(user_id="user_002"),
        )
        for msg in result3["messages"]:
            msg.pretty_print()

```

运行代码前，首先需要运行起来docker中的PostgreSQL:

```python
docker run -d \
  --name postgres16 \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres123 \
  -e POSTGRES_DB=langgraph_db \
  -v postgres_data:/var/lib/postgresql/data \
  --shm-size=256mb \
  --restart=unless-stopped \
  postgres:16

# 如果存在对应的Postgre容器，可以直接启动
docker start postgres16
```

然后运行代码效果与之前案例一样。

以上代码注意：各个Store存储使用方式与 InMemoryStore 完全相同，无论底层是什么存储后端，上层的 CRUD API 保持一致，切换后端只需修改初始化代码。

## 4.6. **Store综合案例**

前面各小节分别讲解了 Store 的基础 CRUD、语义搜索以及在 LangGraph 节点中通过 Runtime 读写 Store。本小节通过一个完整的业务案例，演示Checkpointer（短期记忆）+ Store（长期记忆）的配合使用，以及两种运行模式。

业务背景：一个电商平台的智能购物助手。用户在多轮对话中会透露自己的偏好（"我一般穿M码"、"预算2000以内"、"不喜欢红色"），助手需要将这些信息持久化为用户画像。下次用户换一个新会话再来，助手仍然能读取到之前的画像，给出个性化推荐，而不需要用户重复介绍自己。

![image.png](./images/23Store长期记忆_51356545452d4087b772da3d0ceeb8dc_2cf9a2.jpg)

### **4.6.1. python脚本直接运行**

```python
"""
综合案例：智能购物助手
============================================
Checkpointer（短期记忆）：同一会话的消息历史
Store（长期记忆）：跨会话的用户画像（偏好、尺码、预算等）

流程：START → 读Store画像 → LLM提取新偏好 → 写Store → 个性化回复 → END
"""
import json
import operator
from dataclasses import dataclass
from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, AnyMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from langgraph.runtime import Runtime
from init_llm import deepseek_llm


# ============================================================
# 1. 数据结构
# ============================================================
@dataclass
class Context:
    """每次调用时传入的运行时上下文"""
    user_id: str


class ShopState(TypedDict):
    """图状态 —— Checkpointer 管理的短期记忆"""
    messages: Annotated[list[AnyMessage], operator.add]   # 消息历史
    user_profile: str                         # 从 Store 读取的用户画像摘要


# ============================================================
# 2. 节点
# ============================================================
def extract_profile(state: ShopState, runtime: Runtime[Context]):
    """节点1：从 Store 读取用户画像"""
    user_id = runtime.context.user_id
    ns = (user_id, "profile")

    if runtime.store:
        items = runtime.store.search(ns)
    else:
        items = []

    if items:
        # 将 Store 中的多条画像信息拼接成一段文字
        profile_parts = []
        for item in items:
            for key, val in item.value.items():
                profile_parts.append(f"{key}: {val}")
        profile_text = "；".join(profile_parts)
        return {
            "user_profile": profile_text,
        }
    else:
        return {
            "user_profile": "",
        }


def process_message(state: ShopState, runtime: Runtime[Context]):
    """节点2：LLM 分析用户消息，提取偏好信息"""
    profile = state["user_profile"]
    user_msg = state["messages"][-1].content  # 取最新的用户输入

    prompt = SystemMessage(content=(
        "你是一个用户画像分析助手。根据用户的消息，提取以下信息（如果有的话）：\n"
        "- 尺码偏好（如 M码、L码）\n"
        "- 预算范围（如 2000以内）\n"
        "- 颜色偏好（如 喜欢黑色）\n"
        "- 品牌偏好（如 喜欢Nike）\n"
        "- 品类需求（如 想买运动鞋）\n\n"
        "请以 JSON 格式输出，只包含能从消息中明确提取到的字段。"
        "如果用户没有提到某个字段，不要编造。\n"
        '示例输出: {"尺码": "M码", "预算": "2000以内", "颜色偏好": "不喜欢红色"}\n\n'
        f"用户已有画像: {profile if profile else '暂无'}"
    ))

    response = deepseek_llm.invoke([prompt, HumanMessage(content=user_msg)])
    extracted = response.content.strip()

    return {
        "messages": [AIMessage(content=f"[画像分析] 提取结果: {extracted}")],
    }


def save_to_store(state: ShopState, runtime: Runtime[Context]):
    """节点3：将 LLM 提取的偏好存入 Store"""
    user_id = runtime.context.user_id
    ns = (user_id, "profile")

    # 从节点2的输出中取 LLM 返回的 JSON 数据
    # 节点2的 AIMessage 内容是 "[画像分析] 提取结果: {...}"
    last_ai_msg = state["messages"][-1].content

    if "提取结果:" in last_ai_msg:
        json_str = last_ai_msg.split("提取结果:", 1)[-1].strip()

    # 将提取到的字段逐个存入 Store
    # json.loads 解析 JSON 字符串为 Python 字典
    data = json.loads(json_str)
    if runtime.store and data:
        profile_text = ""
        for key, val in data.items():
            # 这里将每个字段的值拼接成一个字符串，用 "；" 分隔开，方便本次工作流中使用偏好信息
            profile_text += f"{key}: {val}；"
            runtime.store.put(ns, f"pref_{key}", {key: val})
        return {
            "user_profile": profile_text,
            "messages": [AIMessage(content=f"[存储] 已更新用户画像: {len(data)} 个字段，更新内容: {data}")]
        }

    return {"messages": [AIMessage(content="[存储] 本次未提取到新的偏好信息")]}


def generate_reply(state: ShopState):
    """节点4：LLM 结合画像 + 对话历史 生成个性化回复"""
    profile = state["user_profile"]

    # 构建系统提示词（包含用户画像）
    system_content = "你是一个智能购物助手，请根据用户画像提供个性化推荐。回复控制在100字以内。"
    if profile:
        system_content += f"\n\n当前用户画像: {profile}"

    response = deepseek_llm.invoke([
        SystemMessage(content=system_content),
        HumanMessage(content=state["messages"][-1].content),
    ])

    return {"messages": [AIMessage(content=response.content)]}


# ============================================================
# 3. 构建图
# ============================================================
builder = StateGraph(state_schema=ShopState, context_schema=Context)

builder.add_node("extract_profile", extract_profile)
builder.add_node("process_message", process_message)
builder.add_node("save_to_store", save_to_store)
builder.add_node("generate_reply", generate_reply)

builder.add_edge(START, "extract_profile")
builder.add_edge("extract_profile", "process_message")
builder.add_edge("process_message", "save_to_store")
builder.add_edge("save_to_store", "generate_reply")
builder.add_edge("generate_reply", END)


# ============================================================
# 4. 运行
# ============================================================
if __name__ == "__main__":
    DB_URI = "postgresql://postgres:postgres123@192.168.179.5:5432/langgraph_db"

    with (
        PostgresSaver.from_conn_string(DB_URI) as checkpointer,
        PostgresStore.from_conn_string(DB_URI) as store,
    ):
        checkpointer.setup()
        store.setup()

        graph = builder.compile(checkpointer=checkpointer, store=store)

        # ---- 场景1: user_001 首次对话，透露偏好 ----
        print("*" * 100)
        config1 = {"configurable": {"thread_id": "thread_1"}}
        result1 = graph.invoke(
            {"messages": [HumanMessage(
                content="我想买一双运动鞋，预算2000以内，我穿42码，不喜欢红色"
            )]},
            config1,
            context=Context(user_id="user_001"),
        )
        print("result:",result1["messages"][-1].content)

        print("=" * 100)
        print("当前store中的数据:")
        items = store.search(("user_001", "profile"))
        for it in items:
            print(f"  [{it.key}] {it.value}")
        print("=" * 100)


        # ---- 场景2: user_001 开新会话（Store 跨线程读取画像）----
        config2 = {"configurable": {"thread_id": "thread_2"}}
        result2 = graph.invoke(
            {"messages": [HumanMessage(content="推荐性价比最高的一双鞋")]},
            config2,
            context=Context(user_id="user_001"),
        )

        print("result:", result2["messages"][-1].content)

        print("=" * 100)
        print("当前store中的数据:")
        items = store.search(("user_001", "profile"))
        for it in items:
            print(f"  [{it.key}] {it.value}")
        print("=" * 100)

```

运行代码前，如果PostgreSQL中有表和数据，需要删除对应表，以免影响后续存储。代码运行结果如下：

![image.png](./images/23Store长期记忆_56bf32a1e0614044a1385f1a45b70c48_a3d64a.jpg)

### **4.6.2. langgraph dev部署运行**

在checkpointer中，我们启动langgraph dev使用自己的Checkpointer ，需要在langgraph.json中配置“checkpointer”，这样运行langgraph dev后会自动注入自己的checkpointer。

同样，如果想要使用Store，也需要在langgraph.json中配置“store”，这样运行langgraph dev后会自动注入自己的Store。

本案例中需要同时提供自定义 Checkpointer 和自定义 Store。案例代码文件结构如下：

```python
项目根目录/
├── langgraph.json                              # 部署配置
├── .env                                        # 环境变量
├── init_llm.py                                 # LLM 初始化
└── 04_langgraph_store/
    └── 07_langgraph_store_demo/
        ├── graph.py                            # 图定义
        ├── checkpointer.py                    # 自定义Checkpointer
        ├── store.py                            # 自定义Store
        └── client.py                           # 远程调用客户端
```

#### **4.6.2.1. langgraph.json代码**

首先在langgraph.json中增加如下代码：

```python
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./02_langgraph_use/05_langgraph_dev_demo.py:graph",
    "weather_agent": "./02_langgraph_use/06_agent_demo.py:agent",
    "langgraph_checkpoint": "./03_langgraph_checkpointer/13_langgraph_checkpoint_demo/graph.py:graph",
    "langgraph_store": "./04_langgraph_store/07_langgraph_store_demo/graph.py:graph"
  },

  "checkpointer": {
    "backend": "custom",
    "path": "./03_langgraph_checkpointer/13_langgraph_checkpoint_demo/checkpointer.py:get_checkpointer"
  },

  "store": {
    "backend": "custom",
    "path": "./04_langgraph_store/07_langgraph_store_demo/store.py:get_store"
  },

  "env": ".env",
  "image_distro": "wolfi"
}

```

#### **4.6.2.2.** [**checkpointer.py**](http://checkpointer.py)**代码**

[checkpointer.py](http://checkpointer.py)代码如下：

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from contextlib import asynccontextmanager

DB_URI = "postgresql://postgres:postgres123@192.168.179.5:5432/langgraph_db"

@asynccontextmanager
async def get_checkpointer():
    """创建 AsyncPostgresSaver 实例"""
    async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
        await checkpointer.setup()
        yield checkpointer
```

[checkpointer.py](http://checkpointer.py)代码注意如下几点：

1) 自定义checkpointer中需要使用异步方式（因为langgraph dev服务启动后使用异步方式调用图，所以这里需要设置为异步），
2) @asynccontextmanager 装饰器将一个 async generator 函数转为异步上下文管理器，使得 get\_checkpointer() 可以用 async with 调用。yield checkpointer 之前的代码在进入 async with 块时执行（建立数据库连接），yield 之后的代码在退出 async with 块时执行（关闭连接）。

#### **4.6.2.3.** [**store.py**](http://store.py)**代码**

和 [checkpointer.py](http://checkpointer.py) 结构完全一样，只是导入的是 AsyncPostgresStore，langgraph dev 同样走异步路径。

```python
from langgraph.store.postgres.aio import AsyncPostgresStore
from contextlib import asynccontextmanager

DB_URI = "postgresql://postgres:postgres123@192.168.179.5:5432/langgraph_db"

@asynccontextmanager
async def get_store():
    """自定义 Store 工厂 —— langgraph dev 自动调用"""
    async with AsyncPostgresStore.from_conn_string(DB_URI) as store:
        await store.setup()
        yield store
```

#### **4.6.2.4.** [**graph.py**](http://graph.py)**代码**

[graph.py](http://graph.py)代码如下：

```python
# graph.py —— 部署到 langgraph dev
# compile() 不传 checkpointer 和 store，平台自动注入
import json
import operator
from dataclasses import dataclass
from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, AnyMessage
from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime
from init_llm import deepseek_llm


# ============================================================
# 1. 数据结构
# ============================================================
@dataclass
class Context:
    """每次调用时传入的运行时上下文"""
    user_id: str


class ShopState(TypedDict):
    """图状态 —— Checkpointer 管理的短期记忆"""
    messages: Annotated[list[AnyMessage], operator.add]   # 消息历史
    user_profile: str                         # 从 Store 读取的用户画像摘要


# ============================================================
# 2. 节点
# ============================================================
def extract_profile(state: ShopState, runtime: Runtime[Context]):
    """节点1：从 Store 读取用户画像"""
    user_id = runtime.context.user_id
    ns = (user_id, "profile")

    if runtime.store:
        items = runtime.store.search(ns)
    else:
        items = []

    if items:
        # 将 Store 中的多条画像信息拼接成一段文字
        profile_parts = []
        for item in items:
            for key, val in item.value.items():
                profile_parts.append(f"{key}: {val}")
        profile_text = "；".join(profile_parts)
        return {
            "user_profile": profile_text,
        }
    else:
        return {
            "user_profile": "",
        }


def process_message(state: ShopState, runtime: Runtime[Context]):
    """节点2：LLM 分析用户消息，提取偏好信息"""
    profile = state["user_profile"]

    # messages 中的 Message 对象经过 HTTP 传输时被序列化为 dict，取 content 字段需要用 ["content"]
    user_msg = state["messages"][-1].get("content", "")

    prompt = SystemMessage(content=(
        "你是一个用户画像分析助手。根据用户的消息，提取以下信息（如果有的话）：\n"
        "- 尺码偏好（如 M码、L码）\n"
        "- 预算范围（如 2000以内）\n"
        "- 颜色偏好（如 喜欢黑色）\n"
        "- 品牌偏好（如 喜欢Nike）\n"
        "- 品类需求（如 想买运动鞋）\n\n"
        "请以 JSON 格式输出，只包含能从消息中明确提取到的字段。"
        "如果用户没有提到某个字段，不要编造。\n"
        '示例输出: {"尺码": "M码", "预算": "2000以内", "颜色偏好": "不喜欢红色"}\n\n'
        f"用户已有画像: {profile if profile else '暂无'}"
    ))

    response = deepseek_llm.invoke([prompt, HumanMessage(content=user_msg)])
    extracted = response.content.strip()

    return {
        "messages": [AIMessage(content=f"[画像分析] 提取结果: {extracted}")],
    }


def save_to_store(state: ShopState, runtime: Runtime[Context]):
    """节点3：将 LLM 提取的偏好存入 Store"""
    user_id = runtime.context.user_id
    ns = (user_id, "profile")

    # 从节点2的输出中取 LLM 返回的 JSON 数据
    # 节点2的 AIMessage 内容是 "[画像分析] 提取结果: {...}"
    last_ai_msg = state["messages"][-1].content   #这里是上个节点传入的AIMessage 并不是dict

    if "提取结果:" in last_ai_msg:
        json_str = last_ai_msg.split("提取结果:", 1)[-1].strip()

    # 将提取到的字段逐个存入 Store
    # json.loads 解析 JSON 字符串为 Python 字典
    data = json.loads(json_str)
    if runtime.store and data:
        profile_text = ""
        for key, val in data.items():
            # 这里将每个字段的值拼接成一个字符串，用 "；" 分隔开，方便本次工作流中使用偏好信息
            profile_text += f"{key}: {val}；"
            runtime.store.put(ns, f"pref_{key}", {key: val})
        return {
            "user_profile": profile_text,
            "messages": [AIMessage(content=f"[存储] 已更新用户画像: {len(data)} 个字段，更新内容: {data}")]
        }

    return {"messages": [AIMessage(content="[存储] 本次未提取到新的偏好信息")]}


def generate_reply(state: ShopState):
    """节点4：LLM 结合画像 + 对话历史 生成个性化回复"""
    profile = state["user_profile"]

    # 构建系统提示词（包含用户画像）
    system_content = "你是一个智能购物助手，请根据用户画像提供个性化推荐。回复控制在100字以内。"
    if profile:
        system_content += f"\n\n当前用户画像: {profile}"

    response = deepseek_llm.invoke([
        SystemMessage(content=system_content),
        HumanMessage(content=state["messages"][-1].content),
    ])

    return {"messages": [AIMessage(content=response.content)]}


# ============================================================
# 3. 构建图
# ============================================================
builder = StateGraph(state_schema=ShopState, context_schema=Context)

builder.add_node("extract_profile", extract_profile)
builder.add_node("process_message", process_message)
builder.add_node("save_to_store", save_to_store)
builder.add_node("generate_reply", generate_reply)

builder.add_edge(START, "extract_profile")
builder.add_edge("extract_profile", "process_message")
builder.add_edge("process_message", "save_to_store")
builder.add_edge("save_to_store", "generate_reply")
builder.add_edge("generate_reply", END)

# 不传 checkpointer 和 store，平台自动注入
graph = builder.compile()

```

[以上graph.py](http://以上graph.py)代码注意点如下：

1) compile() 既不传 checkpointer 也不传 store，两者都由 langgraph dev 从 langgraph.json 自动注入。
2) 在Graph首执行节点“process\_message”中从messages中获取数据时，需要注意messages 中的 Message 对象经过 HTTP 传输时被序列化为 dict，取 content 字段需要用 \["content"\]。

#### **4.6.2.5.** [**client.py**](http://client.py)**代码**

[client.py](http://client.py)代码如下：

```python
"""
智能购物助手:交互式命令行客户端
通过 LangGraph SDK 远程调用 langgraph dev 服务
"""
import asyncio
import uuid

from langchain_core.messages import HumanMessage
from langgraph_sdk import get_client

client = get_client(url="http://127.0.0.1:2024")


async def main():
    # 输入业务 ID
    raw = input("请输入用户ID (如 user_001，回车默认为user_001): ").strip()
    user_id = raw if raw else "user_001"

    # 首次启动如果用户输入thread_id 就用用户的thread_id 否则自动创建一个thread_id
    current_thread_id = "435973d3-40f0-49d1-8bb4-1fb2574d55ca"

    if len(current_thread_id.strip()) != 36:
        # 如果用户没有输入thread_id 则自动创建一个thread_id
        current_thread_id = str(uuid.uuid4())

    # 在服务端注册这个 thread_id
    # if_exists="do_nothing"：已存在则复用（恢复 Checkpointer 保存的上下文），不存在则新建
    await client.threads.create(thread_id=current_thread_id, if_exists="do_nothing")

    print(f"用户: {user_id} | thread: {current_thread_id}...")

    while True:
        try:
            user_input = input("[用户]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue

        print("处理中...\n\n")
        try:
            result = await client.runs.wait(
                current_thread_id,
                "langgraph_store",    # 对应 langgraph.json 中 graphs 的 key
                input={
                    "messages": [HumanMessage(content=user_input)],
                    "user_profile": "",
                },
                context={"user_id": user_id},
            )

            print("result:",result)
            # messages 中的 Message 对象经过 HTTP 传输时被序列化为 dict，取 content 字段需要用 ["content"]
            print(f"回复: {result['messages'][-1]["content"]}")

            print("=" * 100)
            # 读取 Store 中长期记忆
            resp = await client.store.search_items(
                (user_id, "profile"), limit=10
            )
            print("resp:",resp)
            store_items = resp["items"]
            print("Store 中长期记忆:")
            for item in store_items:
                print(f"  [{item['key']}] {item['value']}")
            print("=" * 100)


        except Exception as e:
            print(f"请求失败: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())

```

[以上client.py](http://以上client.py)代码注意如下几点：

1) 关于thread\_id，LangGraph dev中必须要求thread\_id是UUID格式。
2) thread\_id必须先在服务端注册然后再使用，“await client.threads.create(thread\_id=current\_thread\_id, if\_exists="do\_nothing")”就是 把 UUID 注册到服务端。
3) messages 中的 Message 对象经过 HTTP 传输时被序列化为 dict，取 content 字段需要用 \["content"\]，Client传给Server端是这样，Server端把最终结果传给Client也是一样。
4) 可以通过“await [client.store.search](http://client.store.search)\_items(...)”获取长期记忆内容。其返回的是字典 {"items": \[...\]}，取结果列表需要用 resp\["items"\]。

#### **4.6.2.6. 案例运行**

**1\. 启动PostgreSQL**

首先需要运行起来docker中的PostgreSQL:

```python
docker run -d \
  --name postgres16 \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres123 \
  -e POSTGRES_DB=langgraph_db \
  -v postgres_data:/var/lib/postgresql/data \
  --shm-size=256mb \
  --restart=unless-stopped \
  postgres:16

# 如果存在对应的Postgre容器，可以直接启动
docker start postgres16
```

**2\. 启动LangGraph dev**

在项目中断启动LangGraph dev:

![image.png](./images/23Store长期记忆_c5e83047482c447ba0440148da921ddc_032f59.jpg)

**3\.** [**启动client.py**](http://启动client.py)**，输入如下对话**

如果PostgreSQL中有表和数据，需要删除表，以免影响后续存储。

```python
我想买一双运动鞋，预算2000以内，我穿42码，不喜欢红色

推荐性价比最高的一双鞋

我想买一款手机，预算1000内，我不喜欢黑色手机
```

可以看到对话内容中有存入对应的长期记忆，输出内容如下：

![image.png](./images/23Store长期记忆_2b731dac76b54e44acefbf453a36d8db_1aba7c.jpg)

---
> 🏠 **[返回主页 README](./README.md)** \| ◀️ **上一篇：[22. Checkpointer 短期记忆](./22Checkpointer%E7%9F%AD%E6%9C%9F%E8%AE%B0%E5%BF%86.md)** \| ▶️ **下一篇：[24. LangGraph 容错机制](./24LangGraph%E5%AE%B9%E9%94%99.md)** \| 🎓 **[进入本模块面试高频题](./interview/04_LangGraph高级工作流面试题.md)**
