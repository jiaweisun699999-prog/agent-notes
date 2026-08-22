# 3\. **Checkpointer短期记忆**

## 3.1. **Checkpointer介绍**

Checkpointer 是 LangGraph 的线程级状态持久化机制，它在图的每个步骤自动保存一份图状态的完整快照（checkpoint），并将这些快照组织在一个线程（thread）内。当图因为中断、故障或人工介入而暂停后，Checkpointer 负责从最近的 checkpoint 恢复状态，让图能从断点继续执行，而不是从头再来。

没有 Checkpointer 的 LangGraph 图，每次 invoke() 之间无法保持状态——上一次调用的消息历史、计算结果在调用结束后全部丢失，下一次调用只能在空白状态上从头开始。Checkpointer 让 LangGraph 图从"一次性脚本"变成了"有记忆、可恢复、可回溯的服务"。

特别注意：使用 LangGraph dev 部署时，平台会自动注入持久化的 Checkpointer，开发者不需要手动配置。本章的内容主要面向本地开发和自定义部署场景。

## 3.2. **核心概念**

在动手写代码之前，需要先理解三个相互关联的核心概念。它们之间的关系决定了 Checkpointer 的行为方式。

### **3.2.1. Thread(线程)**

Thread 是组织 checkpoint 的基本容器，用一个唯一的 thread\_id 标识，同一 thread 内的所有执行共享一份状态历史，不同 thread 之间完全隔离。

调用图时，通过 config 传入 thread\_id,这是使用 Checkpointer 的唯一入口:

```python
... ...
# thread_id 是使用 Checkpointer 的唯一入口
config = {"configurable": {"thread_id": "user-session-001"}}

# 同一个 thread_id：后续调用能读到之前的对话历史
graph.invoke({"messages": [{"role": "user", "content": "你好"}]}, config)

# 不同的 thread_id：完全隔离
config2 = {"configurable": {"thread_id": "user-session-002"}}
graph.invoke({"messages": [{"role": "user", "content": "你好"}]}, config2)
```

注意：thread\_id 是 Checkpointer 存储和检索 checkpoint 的主键，没有它，Checkpointer 无法保存状态，也无法在中断后恢复执行。

### **3.2.2. checkpoint(检查点)**

Checkpoint 是图在执行过程中自动保存的状态快照。每执行完一步，LangGraph 就拍一张"照片"存下来，记录此刻所有状态字段的值、下一步要执行哪些节点。我们不需要手动创建 checkpoint，只要编译图时传入了 Checkpointer，整个过程是全自动的。

```python
... ...
# 编译时传入 Checkpointer，checkpoint 自动保存
graph = builder.compile(checkpointer=InMemorySaver())

# 执行后，自动产生了checkpoint
graph.invoke({"foo": "", "bar": []}, {"configurable": {"thread_id": "1"}})
```

我们可以通过 graph.get\_state(config) 拿到最新的 checkpoint，返回值是一个 StateSnapshot 对象：

```python
# 查看最新 checkpoint ：返回 StateSnapshot 对象
snapshot = graph.get_state({"configurable": {"thread_id": "1"}})

# StateSnapshot 里的关键信息
print(snapshot.values) # {'foo': 'b', 'bar': ['a', 'b']}， 当前状态值
print(snapshot.next) # ()  下一步要执行哪个节点，空元组表示图已结束
print(snapshot.metadata) # {'source': 'loop', 'step': 2, 'writes': {...}}
print(snapshot.config) # 包含 thread_id + checkpoint_id
print(snapshot.parent_config) # 上一个 checkpoint 的 config，形成链表
```

StateSnapshot 关键字段如下：

| **字段**          | **类型** | **含义**                                                           |
| ----------------------- | -------------- | ------------------------------------------------------------------------ |
| **values**        | dict           | 此时所有状态channel 的值                                                 |
| **next**          | tuple          | 下一步要执行的节点名，空 () 表示图执行完毕                               |
| **config**        | dict           | 包含thread_id、checkpoint_id、checkpoint_ns的checkpint信息               |
| **metadata**      | dict           | source（"input"/"loop"/"update"）、step（步号）、parents（父图的ck信息） |
| **parent_config** | dict或None     | 上一个checkpoint 的 config，第一个 checkpoint 为 None                    |
| **tasks**         | tuple          | 此步待执行的任务                                                         |
| **interrupts**    | tuple          | 中断信号，常规执行完毕时为空，人机协同暂停时此处有内容                   |

Checkpointer 案例:编译带 Checkpointer 的图、指定 thread\_id、查看最新的checkpoint

```python
import operator
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver


# 1. 定义状态：foo 是标量（覆盖），bar 是列表（追加）
class State(TypedDict):
    foo: str
    bar: Annotated[list[str], operator.add]


# 2. 定义节点
def node_a(state: State):
    """节点 A：写入 foo='a'，向 bar 追加 'a'"""
    return {"foo": "a", "bar": ["a"]}


def node_b(state: State):
    """节点 B：写入 foo='b'，向 bar 追加 'b'"""
    return {"foo": "b", "bar": ["b"]}


# 3. 构建图
builder = StateGraph(State)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)

# 4. 编译图 ，传入 Checkpointer
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)


# 5. 第一次调用:指定 thread_id
config = {"configurable": {"thread_id": "thread_001"}}

result = graph.invoke({"foo": "", "bar": []}, config)
print(f"最终 foo={result['foo']}, bar={result['bar']}")


print("=" * 60)

snapshot = graph.get_state(config)

print("type(snapshot):", type(snapshot))
print(snapshot)

```

以上代码运行后输出如下：

![image.png](./images/22Checkpointer短期记忆_c136179045594d9bbae39c0016384144_b626f4.jpg)

StateSnapshot对象内容如下：

```python
StateSnapshot(
    values={'foo': 'b', 'bar': ['a', 'b']},
    next=(),
    config={'configurable': {'thread_id': 'thread_001', 'checkpoint_ns': '', 'checkpoint_id': '...'}},
    metadata={'source': 'loop', 'step': 2, 'parents': {}},
    created_at='xxxx-xx-xxTxx:xx:10.551423+00:00',
    parent_config={'configurable': {'thread_id': 'thread_001', 'checkpoint_ns': '', 'checkpoint_id': '...'}},
    tasks=(),
    interrupts=()
)
```

以上代码需要注意如下几点：

1) InMemorySaver 是最简单的 Checkpointer 实现，将 checkpoint 存储在内存中，重启进程后这些 checkpoint 全部丢失。
2) 因为定义了 Annotated\[list\[str\], add\] 归并器，bar 的值是累积的。

### **3.2.3. Super-step(超级步)**

Super-step 是图执行的"一拍"，在这一拍内，所有被调度的节点执行完毕（可能并行），然后 LangGraph 创建一个 checkpoint，下一拍开始前，checkpoint 已经在存储中落盘。

以序列图 START → A → B → END 为例，执行一次 invoke 产生 4 个 checkpoint。基于以上案例通过“graph.get\_history(config)”来获取所有checkpoint历史并输出，可以看到每个Super-step执行后的checkpoint状态：

```python
import operator
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver


# 1. 定义状态：foo 是标量（覆盖），bar 是列表（追加）
class State(TypedDict):
    foo: str
    bar: Annotated[list[str], operator.add]


# 2. 定义节点
def node_a(state: State):
    """节点 A：写入 foo='a'，向 bar 追加 'a'"""
    return {"foo": "a", "bar": ["a"]}


def node_b(state: State):
    """节点 B：写入 foo='b'，向 bar 追加 'b'"""
    return {"foo": "b", "bar": ["b"]}


# 3. 构建图
builder = StateGraph(State)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)

# 4. 编译图 ，传入 Checkpointer
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)


# 5. 第一次调用:指定 thread_id
config = {"configurable": {"thread_id": "thread_001"}}

result = graph.invoke({"foo": "", "bar": []}, config)
print(f"最终 foo={result['foo']}, bar={result['bar']}")


print("=" * 60)

snapshot = graph.get_state(config)

print("type(snapshot):", type(snapshot))
print(snapshot)

print("=" * 60)

# 遍历所有 checkpoint 历史
for snapshot in graph.get_state_history(config):
    print(f"step={snapshot.metadata['step']}, next={snapshot.next}, values={snapshot.values}")

    # parent_config 为 None 说明这是最早的 checkpoint
    if snapshot.parent_config is None:
        print(f"这是最早的 checkpoint（根节点）")

```

以上代码运行后，输出的所有checkpoint历史内容如下：

```python
step=2, next=(), values={'foo': 'b', 'bar': ['a', 'b']}
step=1, next=('node_b',), values={'foo': 'a', 'bar': ['a']}
step=0, next=('node_a',), values={'foo': '', 'bar': []}
step=-1, next=('__start__',), values={'bar': []}
这是最早的 checkpoint（根节点）
```

以上代码还需注意如下几点：

1) get\_state\_history 返回顺序：最新 checkpoint 在最前面（倒序）。
2) 理解super-step的关键价值在于：时间旅行只能回到super-step边界（即checkpoint所在位置），不能回到某个节点执行到一半的状态。
3) 如果 A 和 B 是并行的（都从 START 出发），它俩就在同一拍里执行，都跑完这一拍才结束。如果其中 B 崩了而 A 成功了，A 的输出已经落盘（pending writes），恢复后只需重跑 B。

基于以上案例，同一个thread\_id第二次调用时，图会从上次的状态继续追加，而不是从空白状态开始。如下代码中直接使用相同的thread\_id继续进行invoke调用：

```python
"""
案例:验证checkpint“记忆”功能
"""
import operator
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver


# 1. 定义状态：foo 是标量（覆盖），bar 是列表（追加）
class State(TypedDict):
    foo: str
    bar: Annotated[list[str], operator.add]


# 2. 定义节点
def node_a(state: State):
    """节点 A：写入 foo='a'，向 bar 追加 'a'"""
    return {"foo": "a", "bar": ["a"]}


def node_b(state: State):
    """节点 B：写入 foo='b'，向 bar 追加 'b'"""
    return {"foo": "b", "bar": ["b"]}


# 3. 构建图
builder = StateGraph(State)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)

# 4. 编译图 ，传入 Checkpointer
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)


# 5. 第一次调用:指定 thread_id
config = {"configurable": {"thread_id": "thread_001"}}

result = graph.invoke({"foo": "", "bar": []}, config)
print(f"[第一次] foo={result['foo']}, bar={result['bar']}")


print("=" * 60)

# 第二次调用：同一个 thread_id，但初始状态仍传 foo="", bar=[]
# 注意：invoke 传的是"本次输入"，bar 有 add 归并器所以会追加
result2 = graph.invoke({"foo": "", "bar": []}, config)
print(f"[第二次] foo={result2['foo']}, bar={result2['bar']}")

print("=" * 60)
```

运行结果如下，bar 在第二次调用后变成了 \['a', 'b', 'a', 'b'\]——因为每次 invoke 都是一次完整的图执行（START → A → B → END），两次执行的输出被 add 归并器叠加在了一起。

![image.png](./images/22Checkpointer短期记忆_d143892abfef4f36b773faff4edfa5fa_f5fbf8.jpg)

## 3.3. **状态的读取与修改**

LangGraph中还提供了主动读取和手动修改checkpoint状态的能力，这在实际业务中很重要：比如人工审批时，需要查看当前 Agent 的状态再决定是否放行；或者发现状态数据有问题，需要手动修正后让图继续执行。

### **3.3.1. 获取当前最新状态**

graph.get\_state(config) 返回该线程的最新 checkpoint 对应的 StateSnapshot。如果 config 中指定了 checkpoint\_id，则返回指定的 checkpoint。

```python
"""
get_state() —— 获取线程的最新状态或指定 checkpoint 的状态
"""
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from typing import Annotated
from typing_extensions import TypedDict


class State(TypedDict):
    foo: str
    bar: Annotated[list[str],operator.add]


def node_a(state: State):
    return {"foo": "a", "bar": ["a"]}


def node_b(state: State):
    return {"foo": "b", "bar": ["b"]}


builder = StateGraph(State)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)


graph = builder.compile(checkpointer=InMemorySaver())



config = {"configurable": {"thread_id": "thread_001"}}
graph.invoke({"foo": "", "bar": []}, config)


# 获取最新状态
latest = graph.get_state(config)
print("【最新状态】")
print(f"  values:      {latest.values}")
print(f"  next:        {latest.next}")
print(f"  config:      {latest.config}")
print(f"  metadata:    {latest.metadata}")
print(f"  parent_config:      {latest.parent_config}")
print()


# 获取指定 checkpoint_id 的状态
target_checkpoint_id = latest.parent_config["configurable"]["checkpoint_id"]

target_config = {
    "configurable": {
        "thread_id": "thread_001",
        "checkpoint_id": target_checkpoint_id,
    }
}

snapshot = graph.get_state(target_config)
print("【指定 checkpoint 的状态】")
print(f"  values:      {snapshot.values}")
print(f"  next:        {snapshot.next}")
print(f"  config:      {snapshot.config}")
print(f"  metadata:    {snapshot.metadata}")
print(f"  parent_config:      {snapshot.parent_config}")

```

运行结果如下：

![image.png](./images/22Checkpointer短期记忆_45ca2dc350d442df85df3e172b0ebdbc_2f772c.jpg)

### **3.3.2. 获取状态历史**

graph.get\_state\_history(config) 返回该线程所有 checkpoint 的迭代器，按时间倒序。实际业务中，get\_state\_history 最常见的用法是按条件查找特定 checkpoint——比如找到触发中断的那一步、找到某个节点执行前的状态等。

```python
"""演示 get_state_history() —— 遍历 checkpoint 历史并按条件筛选"""
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from typing import Annotated
from typing_extensions import TypedDict
from operator import add


class State(TypedDict):
    foo: str
    bar: Annotated[list[str], add]


def node_a(state: State):
    return {"foo": "a", "bar": ["a"]}


def node_b(state: State):
    return {"foo": "b", "bar": ["b"]}


builder = StateGraph(State)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)

graph = builder.compile(checkpointer=InMemorySaver())


config = {"configurable": {"thread_id": "thread_001"}}
graph.invoke({"foo": "", "bar": []}, config)

# 获取所有的 checkpoint 历史
history = list(graph.get_state_history(config))
print(f"共 {len(history)} 个 checkpoint")



# 场景一：找到 node_b 执行前的那个 checkpoint
before_b = None
for s in history:
    print(f"s={s}")
    if s.next == ("node_b",):
        before_b = s
        break

if before_b:
    print(f"【node_b 执行前】values={before_b.values}")

# 场景二：找到第一个 checkpoint（根，parent_config 为 None）
root = None
for s in history:
    if s.parent_config is None:
        root = s
        break

if root:
    print(f"【根 checkpoint】step={root.metadata['step']}, values={root.values}")

```

以上代码运行结果如下：

![image.png](./images/22Checkpointer短期记忆_fe794ab11d9a4c148e5fc0cb6a90e43e_a58e06.jpg)

以上代码注意如下几点：

1) get\_state\_history 返回的是迭代器，需要 list() 或 for 循环消费。
2) StateSnapshot 提供了 next、metadata、tasks 等结构化字段，条件筛选非常灵活。

### **3.3.3. 从历史Checkpoint重放状态**

除了查看历史状态，Checkpointer 还支持时间旅行重放：在 invoke() 时指定一个历史的 checkpoint\_id，图会从该 checkpoint 之后重新执行节点——之前节点的结果直接复用，之后的节点（包括 LLM 调用和中断）重新运行。

```python
# 从历史 checkpoint 重放执行
history = list(graph.get_state_history(config))
past_checkpoint = history[2]  # 假设要回到第 3 个 checkpoint
graph.invoke(None, past_checkpoint.config)  # 从该 checkpoint 之后重新执行
```

如下示例中是LangGraph中基于过去的某个checkpoint进行重放。

```python
"""Checkpoint Replay:从历史 checkpoint 重放执行"""
import operator
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver


class State(TypedDict):
    foo: str
    bar: Annotated[list[str], operator.add]


def node_a(state: State):
    """节点 A：写入 foo='a'，向 bar 追加 'a'"""
    print("=== node_a 被执行 ===")
    return {"foo": "a", "bar": ["a"]}


def node_b(state: State):
    """节点 B：写入 foo='b'，向 bar 追加 'b'"""
    print("=== node_b 被执行 ===")
    return {"foo": "b", "bar": ["b"]}


builder = StateGraph(State)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)

graph = builder.compile(checkpointer=InMemorySaver())

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "thread_001"}}

    # ---- 第一次：正常执行 ----
    print("第一次：正常执行")
    graph.invoke({"foo": "", "bar": []}, config)

    print("=" * 55)

    # ---- 查看历史 ----
    history = list(graph.get_state_history(config))
    print("\ncheckpoint 历史：")
    for i, snap in enumerate(history):
        print(f"  [{i}] step={snap.metadata['step']}, "
              f"next={snap.next}, "
              f"foo='{snap.values.get('foo', '')}', "
              f"bar={snap.values.get('bar', [])}")

    print("=" * 55)

    # ---- Replay：从 step=1（node_a 已跑完，node_b 还没跑）重放 ----
    replay_snapshot = history[1]  # next=('node_b',)
    print(f"Replay：从 step=1 重放（next={replay_snapshot.next}）")
    replay_result = graph.invoke(None, replay_snapshot.config)
    print(f"replay_result 结果：{replay_result}")

```

以上代码运行结果如下：

![image.png](./images/22Checkpointer短期记忆_4c98024a3af94f1fab93ad11076435c1_b5e475.jpg)

可以看到基于step1进行checkpoint重放，node\_a节点没有执行，只有node\_b节点执行。

### **3.3.4. 手动修改状态**

graph.update\_state(config, values) 创建一个新的 checkpoint，其中包含你指定的状态更新。它不修改原有 checkpoint（checkpoint 是不可变的），而是在历史链上追加一个新 checkpoint。

update\_state的核心用途：

* 人机协同：人工审批后，将审批结果注入图状态，然后让图从更新后的位置继续执行

案例：手动修改状态，并基于某个节点进行状态分支。

```python
"""
    update_state()：手动修改状态并观察效果
"""
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from typing import Annotated
from typing_extensions import TypedDict


class State(TypedDict):
    foo: str
    bar: Annotated[list[str], operator.add]


def node_a(state: State):
    return {"foo": "a", "bar": ["a"]}


def node_b(state: State):
    return {"foo": "b", "bar": ["b"]}


builder = StateGraph(State)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)

graph = builder.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "thread_001"}}

    # 调用graph
    graph.invoke({"foo": "", "bar": []}, config)

    # 获取最新的 checkpoint 状态
    latest = graph.get_state(config)
    print(f"【最新状态】：{latest}")

    print("="*50)

    # 使用 update_state 手动修改状态
    updated_config = graph.update_state(
        config,
        values={"foo": "aaa", "bar": ["bbb"]},
    )

    # 获取最新的 checkpoint 状态
    latest = graph.get_state(config)
    print(f"【更新后最新状态】：{latest}，\n类型:{latest.metadata["source"]}")

    print("="*50)

    # 获取所有checkpoint
    history = list(graph.get_state_history(config))
    for checkpoint in history:
        print(f"【checkpoint】：{checkpoint}")

    print("=" * 50)

    # 找到node_a 执行后的 checkpoint
    after_a = None
    for checkpoint in history:
        if checkpoint.next == ("node_b",):
            after_a = checkpoint
            break

    # 从 node_a 之后的 checkpoint 位置
    fork_config = graph.update_state(
        after_a.config, # after_a.config 中包含checkpoint_id ，表示从这个after_a处进行checkpoint分叉
        values={"foo": "aaaa", "bar": ["bbbb"]}
    )

    fork_snapshot = graph.get_state(fork_config)
    print(f"【node_a分支：】 {fork_snapshot}")

```

以上代码运行结果如下：

![image.png](./images/22Checkpointer短期记忆_06645914325f415da1ba92d436455246_e729cf.jpg)

以上代码注意如下几点：

1) update\_state不修改原checkpoint,会创建一个新checkpoint，其metadata\["source"\]为"update"，parent\_config指向当前最新 checkpoint，原有 checkpoint 链完整保留。
2) update\_state返回新的config，这个config中包含了新checkpoint的checkpoint\_id可以继续用于后续操作。

## 3.4. **持久化模式（Durability Modes）**

持久化模式控制在图执行过程中，checkpoint 数据何时写入存储后端。LangGraph 提供了三种模式，在性能和可靠性之间提供不同的权衡。

持久化使用方式：

```python
# 指定持久化模式
graph.invoke(input_data, config, durability="sync")  
```

持久化三种模式对比如下：

| **对比/模式**      | **exit**                             | **async（默认）**                | **sync**                       |
| ------------------------ | ------------------------------------------ | -------------------------------------- | ------------------------------------ |
| **写入时机**       | 仅在图执行退出时（正常/异常/中断）         | 下一步执行时异步写入上一步的checkpoint | 每步开始前同步写入上一步的checkpoint |
| **性能**           | 最高                                       | 中等                                   | 最低                                 |
| **checkpoint数量** | 只保留最终                                 | 全部保留                               | 全部保留                             |
| **可靠性**         | 最低（中间状态全部丢弃，进程崩溃无法恢复） | 较高（进程崩溃可能丢最后一个）         | 最高（每步都确保落盘）               |

案例：演示三种模式使用。

```python
"""三种持久化模式 —— 观察 checkpoint 数量差异"""
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import AIMessage, HumanMessage


def echo_node(state: MessagesState):
    """简单回显节点"""
    return {"messages": [AIMessage(content="处理完成")]}


builder = StateGraph(MessagesState)
builder.add_node("echo_node", echo_node)
builder.add_edge(START, "echo_node")
builder.add_edge("echo_node", END)

graph = builder.compile(checkpointer=InMemorySaver())

if __name__ == "__main__":
    # ---- exit 模式：仅退出时保存 ----
    config_exit = {"configurable": {"thread_id": "thread_001"}}
    graph.invoke(
        {"messages": [HumanMessage(content="测试")]},
        config_exit,
        durability="exit",
    )

    # ---- async 模式：每步同步保存 ----
    config_async = {"configurable": {"thread_id": "thread_002"}}
    graph.invoke(
        {"messages": [HumanMessage(content="测试")]},
        config_async,
        durability="async",
    )

    # ---- sync 模式：每步同步保存 ----
    config_sync = {"configurable": {"thread_id": "thread_003"}}
    graph.invoke(
        {"messages": [HumanMessage(content="测试")]},
        config_sync,
        durability="sync",
    )


    # ---- 对比 ----
    exit_history = list(graph.get_state_history(config_exit))
    async_history = list(graph.get_state_history(config_async))
    sync_history = list(graph.get_state_history(config_sync))

    print(f"\nexit 模式: 只有 1 个（step=1），中间 step=-1 和 step=0 被丢弃")
    for s in exit_history:
        print(f"  step={s.metadata['step']}, next={s.next}")

    print(f"\nasync 模式: 3 个（step=-1, step=0, step=1），完整保留")
    for s in async_history:
        print(f"  step={s.metadata['step']}, next={s.next}")

    print(f"\nsync 模式: 3 个（step=-1, step=0, step=1），完整保留")
    for s in sync_history:
        print(f"  step={s.metadata['step']}, next={s.next}")

```

以上代码运行结果如下：

![image.png](./images/22Checkpointer短期记忆_670c8c42fddd44c4bf95fd24efc8e706_86b12e.jpg)

以上代码注意如下几点：

1) exit模式中间状态全部丢弃，意味着 get\_state\_history 只能看到最后一个 checkpoint，时间旅行、容错恢复都无从谈起。
2) 对InMemorySaver来说，sync和async几乎没有性能差异（内存写入都是同步的），区别在 PostgreSQL 等远程后端上才会体现。
3) 生产环境建议不要用 exit，除非你的图是纯无状态的批处理任务且你确定永远不需要查看中间状态，对时效性要求高的用"async"，金融等关键业务用"sync"。

## 3.5. **Checkpoint存储实现**

在之前学习中，LangGraph将checkpint存储在内存中，使用的是InMemorySaver，这是LangGraph中checkpoint实现的一种方式，仅适用于开发测试场景，对于生成环境Checkpoint的持久化存储尤为重要。LangGraph 提供了如下几种主要的 Checkpointer 实现，分别对应不同的环境和使用场景。

| **实现**          | **使用场景**                                                    |
| ----------------------- | --------------------------------------------------------------------- |
| **InMemorySaver** | 将Checkpoint存储在内存中，适用于开发测试、实验场景                    |
| **SqliteSaver**   | 将Checkpoint存储在SQLite文件中，适用于本地开发、单机部署LangGraph场景 |
| **MySQLSaver**    | 将Checkpoint存储在MySQL中，适用于生产环境、多实例部署场景。           |
| **PostgresSaver** | 将Checkpoint存储在PostgreSQL中，适用于生产环境、多实例部署场景。      |

特别注意：持久化存储支持的数据库可以通过“https://pypi.org/search/[”查看，搜索“langgraph-checkpoint-\*”查看对应需要安装的依赖和使用方式。](https://pypi.org/search/?o=&q=langgraph-checkpoint&page=2”查看，搜索“langgraph-checkpoint-*”查看对应需要安装的依赖和使用方式。)

![image.png](./images/22Checkpointer短期记忆_985df7200fcb46f0a864e76b3d7703bc_69697e.jpg)

### **3.5.1. PostgreSQL搭建与操作**

PostgreSQL（简称 Postgres）是一个开源的对象-关系型数据库管理系统（ORDBMS），由全球开发者社区维护，拥有超过 35 年的活跃开发历史。它被广泛认为是"世界上最先进的开源关系型数据库"，以可靠性、功能丰富性和 SQL 标准兼容性著称。

PostgreSQL中有如下几个核心概念：

* Cluster（实例）:PostgreSQL 把一个由单个服务进程管理的所有数据库统称为一个实例，例如：在Docker中启动一个PostgreSQL容器就是一个实例。
* Database（数据库）:一个实例下可以有多个数据库，每个数据库之间物理隔离，与MySQL不同，PostgreSQL 中两个数据库之间不能直接 JOIN，需要通过 Foreign Data Wrapper 扩展才能跨库查询。
* Schema：Schema是数据库内部的一个逻辑命名空间。可以把它理解为数据库内部的"文件夹"。同一个数据库里，public.orders 和 archive.orders 是同名的两张表，因为它们在各自的 Schema 下，互不冲突。而在mysql同一个数据库中表名必须全局唯一。
* Table：数据表。
* Column:数据列。

结合mysql来理解以上这几个概念：MySQL 的数据组织层级是：

```python
MySQL:  实例(Server) → 数据库(Database) → 表(Table) → 列(Column)
```

PostgreSQL 在数据库和表之间多了一层 Schema：

```python
PostgreSQL:  实例(Cluster) → 数据库(Database) → Schema → 表(Table) → 列(Column)
```

#### **3.5.1.1. PostgreSQL搭建**

下面基于Linux中的docker搭建PostgreSQL，这里默认你已经安装好了Linux以及docker。可以直接运行如下命令拉取镜像及启动PostgreSQL：

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
```

以上命令首次执行会先拉取postgresql的镜像，然后启动。以上命令解释如下：

| **参数**        | **含义**                                                                                                                                                                                                                               |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **docker run**  | 创建并启动一个新容器                                                                                                                                                                                                                         |
| **-d**          | detach，后台运行容器，不占用当前终端                                                                                                                                                                                                         |
| **--name**      | 给容器起个名字，后续用 docker stop&#x3c;xx>等命令操作它，不用记容器 ID                                                                                                                                                                       |
| **-p**          | port 端口映射。宿主机端口:容器内端口。PostgreSQL 的默认端口是 5432                                                                                                                                                                           |
| **-e**          | environment，设置容器内环境变量。POSTGRES_PASSWORD是必填项。POSTGRES_DB表示首次启动时，自动创建一个名为langgraph_db的数据库                                                                                                                  |
| **-v**          | volume，数据卷挂载。卷名:容器内路径。/var/lib/postgresql/data 是PostgreSQL 存放数据文件的目录。挂载后，即使docker rm删了容器，数据还在postgres_data这个卷里。注意：postgre16版本前必须挂载这个具体路径，不能挂载其父目录/var/lib/postgresql |
| **--shm-size**  | 共享内存大小。PostgreSQL 用共享内存做进程间通信，Docker 默认只给 64MB，不够用时会报错。                                                                                                                                                      |
| **--restart**   | 重启策略。unless-stopped= 容器异常退出时 Docker 自动重启它；除非你手动 docker stop。服务器重启后 Docker 也会自动拉起来这个容器                                                                                                               |
| **postgres:16** | 镜像名。16= PostgreSQL 16 版本                                                                                                                                                                                                               |

#### **3.5.1.2. 操作PostgreSQL命令**

docker 操作PostgreSQL命令：

```python
#查看PostgreSQL容器日志
docker logs -f postgres16

#停止容器
docker stop postgres16

#后续启动容器
docker start postgres16

#重启容器
docker restart postgres16

# 删除容器（不会删数据卷，数据还在）
docker rm postgres16

# 删除容器 + 数据卷（数据永久丢失）
docker rm postgres16
docker volume rm postgres_data
```

PostgreSQL操作命令：

```python
#检查容器状态（STATUS 列显示 "Up X seconds" 即为正常）
docker ps

查看启动日志，确认没有错误
docker logs postgres16

#进入PostgreSQL容器，用 psql 连接数据库验证
docker exec -it postgres16 psql -U postgres -d langgraph_db

#查看当前数据库
langgraph_db=# SELECT current_database();
 current_database 
------------------
 langgraph_db
(1 row)

#查看PostgreSQL版本
langgraph_db=# SELECT version();
                                                       version  
----------------------------------------------------------------------------------------------------------------------
 PostgreSQL 16.14 (Debian 16.14-1.pgdg13+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 14.2.0-19) 14.2.0, 64-bit
(1 row)

#使用“\q”退出
langgraph_db=# \q

```

psql连接数据库验证参数解释如下：

| **参数**            | **含义**                       |
| ------------------------- | ------------------------------------ |
| **docker exec**     | 在已运行的容器内执行一条命令         |
| **-it**             | 进入可交互的命令行界面               |
| **postgres16**      | 容器名，就是docker run时--name指定的 |
| **psql**            | PostgreSQL自带的命令行客户端         |
| **-U postgres**     | User，以postgres用户身份连接         |
| **-d langgraph_db** | database，连接到langgraph_db数据库   |

#### **3.5.1.3. Navicate操作PostgreSQL**

按照如下操作通过Navicate连接PostgreSQL。

![image.png](./images/22Checkpointer短期记忆_95be5cf300b84ba89a3773661e2518cf_1350b0.jpg)

![image.png](./images/22Checkpointer短期记忆_9154cd1f5a3d4bebb584f394fab700d2_09769a.jpg)

![image.png](./images/22Checkpointer短期记忆_68fa73a6ec99493aa49b3c4a9d393f78_d369df.jpg)

![image.png](./images/22Checkpointer短期记忆_13bc662d62bb41b0bd89def012c0859a_fa36e0.jpg)

新建查询，测试如下语句：

```python
-- ============================================================
-- 1. 创建 person 表
-- ============================================================
CREATE TABLE person (
    -- SERIAL：自增整数，PostgreSQL 会自动创建一个 Sequence 对象
    -- 等价于 MySQL 的 AUTO_INCREMENT，但底层机制不同
    id      SERIAL       PRIMARY KEY,
    -- VARCHAR(50)：最长 50 个字符的变长字符串
    name    VARCHAR(50)  NOT NULL,
    -- INT：整数类型，和 MySQL 的 INT 一样
    age     INT          CHECK (age > 0 AND age < 150)
);


-- ============================================================
-- 2. INSERT（插入数据）
-- ============================================================
-- 插入单行
INSERT INTO person (name, age) VALUES ('张三', 25);

-- 一次插入多行
INSERT INTO person (name, age) VALUES
    ('李四', 30),
    ('王五', 22);

-- id 是 SERIAL 自动生成的，不用手动指定
-- 如果想显式指定 id 也可以：
-- INSERT INTO person (id, name, age) VALUES (100, '赵六', 28);

-- 查看插入后的数据
SELECT * FROM person;


-- ============================================================
-- 3. UPDATE
-- ============================================================
-- 把张三的年龄改为 26
UPDATE person SET age = 26 WHERE name = '张三';

-- 查看修改后数据
SELECT * FROM person;


-- ============================================================
-- 4. DELETE
-- ============================================================
-- 删除年龄小于 25 的行
DELETE FROM person WHERE age < 25;

-- 查看修改后数据
SELECT * FROM person;
```

### **3.5.2. InMemorySaver**

InMemorySaver适用于开发调试、编写测试用例，不适用于任何需要数据持久化的场景（进程重启数据丢失）。该方式前面章节已经大量使用，这里不再重复展示完整案例。核心使用方式：

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```

### **3.5.3. SqliteSaver**

SqliteSaver 将 checkpoint 持久化到本地的 SQLite 文件，重启不丢。适用于本地开发、单机部署的小型应用。不适用于多实例并发写入（SQLite 的写锁限制），生产级高并发场景建议用 PostgresSaver。

使用SqliteSaver需要安装如下依赖：

```python
pip install langgraph-checkpoint-sqlite==3.1.1
```

案例：使用SqliteSaver存储Checkpoint。

```python
"""
SqliteSaver ：使用 SQLite 文件持久化 checkpoint
"""
import operator
import sqlite3
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver


class State(TypedDict):
    foo: str
    bar: Annotated[list[str],operator.add]


def node_a(state: State):
    return {"foo": "a", "bar": ["a"]}


def node_b(state: State):
    return {"foo": "b", "bar": ["b"]}


builder = StateGraph(State)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)


# 连接 SQLite 数据库文件
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)

# 创建 SqliteSaver
checkpointer = SqliteSaver(conn)
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "thread_001"}}
result = graph.invoke({"foo": "", "bar": []}, config)
print(f"result:{result}")

```

以上代码当运行第一次时，在当前代码目录下会生成“checkpoints.db”文件，当第二次运行后会从该文件中获取到上次运行的状态，基于上次状态进行更新状态。

![image.png](./images/22Checkpointer短期记忆_e4308f5d016e4206abc41229f0159a62_95458e.jpg)

以上代码需要注意“sqlite3.connect("checkpoints.db", check\_same\_thread=False)”中的check\_same\_thread参数设置为False表示允许多个线程安全地共享同一个连接对象。

### **3.5.4. MySQLSaver**

MySQLSaver 适合生产环境的多实例部署场景，可用于需要高可用和数据持久化的环境。使用MySqlSaver需要在对应环境中先安装如下依赖：

```python
pip install langgraph-checkpoint-mysql==3.0.0 pymysql==1.1.2 cryptography==46.0.3
```

案例:使用MySqlSaver存储Checkpoint。

```python
"""
MySqlSaver ：使用 MySQL 文件持久化 checkpoint
"""
import operator
from typing import Annotated

from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    foo: str
    bar: Annotated[list[str],operator.add]


def node_a(state: State):
    return {"foo": "a", "bar": ["a"]}


def node_b(state: State):
    return {"foo": "b", "bar": ["b"]}


builder = StateGraph(State)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)


DB_URI = "mysql://root:123456@localhost:3306/langgraph_db"

with PyMySQLSaver.from_conn_string(DB_URI) as checkpointer:
    # 自动创建数据库表（首次运行）
    checkpointer.setup()

    # 创建 MySqlSaver
    graph = builder.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "thread_001"}}
    result = graph.invoke({"foo": "", "bar": []}, config)
    print(f"result:{result}")

```

以上代码连续运行两次效果与SqliteSaver中的结果一样，但需要注意如下几点：

1) “with PyMySQLSaver.from\_conn\_string(DB\_URI) as checkpointer:”通过连接字符串DB\_URI创建与MySQL数据库的持久化连接，用于管理对话状态检查点的存储。
2) 使用mysql存储短期记忆需要提前在数据库中创建对应的数据库，然后代码首次运行执行“checkpointer.setup()”（首次运行需要，首次运行后可以不再执行该代码）会自动在该数据库中创建对应数据库表。

### **3.5.5. PostgreSaver**

PostgresSaver 适合生产环境的多实例部署场景，使用PostgreSaver之前需要在对应的python环境中安装如下依赖：

```python
pip install langgraph-checkpoint-postgres==3.1.1
pip install psycopg-binary==3.3.4
```

案例：使用PostgreSaver存储Checkpoint。

```python
"""
PostgresSaver：使用 PostgreSQL 持久化 checkpoint
"""
import operator
from typing import Annotated

from langgraph.checkpoint.postgres import PostgresSaver
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    foo: str
    bar: Annotated[list[str],operator.add]


def node_a(state: State):
    return {"foo": "a", "bar": ["a"]}


def node_b(state: State):
    return {"foo": "b", "bar": ["b"]}


builder = StateGraph(State)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)


# 替换为你的实际数据库连接串
DB_URI = "postgresql://postgres:postgres123@192.168.179.5:5432/langgraph_db"

# from_conn_string 创建实例
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    # 首次使用需要建表（后续可省略）
    checkpointer.setup()

    # 创建 PostgresSaver
    graph = builder.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "thread_001"}}
    result = graph.invoke({"foo": "", "bar": []}, config)
    print(f"result:{result}")

```

以上代码连续运行两次效果与MySQLSaver中的结果一样且代码编写方式与MySQLSaver几乎一样。

## 3.6. **Checkpoint案例**

前面各小节分别讲解了 Checkpointer 的核心概念、状态读写 API、持久化模式和checkpoint选型。本小节通过一个完整的业务案例，演示在langgraph中两种方式使用PostgreSQL存储checkpoint：直接 Python 脚本运行和使用 langgraph dev 部署运行。

业务背景：公司客服中心每天收到大量用户消息，包括退款投诉、技术问题、业务咨询、意见建议。人工客服处理不过来的核心痛点是：每条消息先要花时间判断"这人到底想干什么"。本案例做的事情就是：用户发消息 → LLM 自动识别意图 → 按意图路由到不同的处理部门 → LLM 生成回复。

整个流程是确定的，LLM 只在特定节点被调用（识别意图、生成回复），而不是自主决定整个流程，所以我们这里使用LangGraph来实现这个业务需求。

![image.png](./images/22Checkpointer短期记忆_885369804f5f4116bb0a5ccfc528dcad_53606d.jpg)

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

如果PostgreSQL中有表和数据，需要删除表，以免影响后续存储。

### **3.6.1. python脚本直接运行**

这种模式适合本地开发和调试，所有组件（图定义、Checkpointer、调用逻辑）都在一个 .py 文件中。Checkpointer 直接在代码里创建并传给 compile()。

```python
"""
checkpoint 案例
"""
import operator
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, AnyMessage


from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver

from init_llm import deepseek_llm


# 1. 定义状态
class ServiceState(TypedDict):
    """一条客服会话的完整状态"""
    # 消息历史（add 归并器，追加不覆盖）
    messages: Annotated[list[AnyMessage], operator.add]

    # 业务字段（标量，每次覆盖最新值）
    user_input: str          # 用户最新输入
    intent: str              # 识别的意图：refund(退款) / tech(技术) / consult(咨询) / feedback(投诉)
    department: str          # 路由目标部门
    response: str            # 生成的回复


# 2. 定义节点
def check_intent(state: ServiceState):
    """节点1：LLM 识别用户意图（四选一）"""
    prompt = SystemMessage(content=(
        "你是一个客服意图识别助手。分析用户消息，判断意图属于以下哪一种：\n"
        "- refund: 退款、退货、赔偿相关问题\n"
        "- tech: 产品使用故障、技术问题\n"
        "- consult: 产品咨询、业务询问\n"
        "- feedback: 投诉、建议、意见反馈\n"
        "只回复一个单词：refund / tech / consult / feedback"
    ))

    user_input = state["user_input"]
    response = deepseek_llm.invoke([prompt, HumanMessage(content=user_input)])

    intent = response.content.strip().lower()

    return {
        "intent": intent,
        "messages": [AIMessage(content=f"[意图识别] 用户输入：{user_input}，意图识别为： {intent}")],
    }


def handle_refund(state: ServiceState):
    """节点2a：退款处理组：生成退款相关回复"""
    response = deepseek_llm.invoke([
        SystemMessage(content=(
            "你是退款客服专员。用户想退款或投诉账单问题，请礼貌地了解具体情况，"
            "并告知退款流程："
            "   1)核实订单 "
            "   2)提交退款申请 "
            "   3)3-5个工作日到账。"
            "回复控制在80字以内。"
        )),
        HumanMessage(content=state["user_input"]),
    ])
    return {
        "department": "退款组",
        "response": response.content,
        "messages": [AIMessage(content=f"[路由] 已转到退款组，回复内容：{response.content}")],
    }


def handle_tech(state: ServiceState):
    """节点2b：技术支持组：生成技术问题回复"""
    response = deepseek_llm.invoke([
        SystemMessage(content=(
            "你是技术支持工程师。用户遇到了产品使用问题，请先表示理解，"
            "然后给出排查步骤："
            "   1)确认问题现象 "
            "   2)尝试基础排查（重启/更新）"
            "   3)如无法解决则升级到高级工程师。"
            "回复控制在80字以内。"
        )),
        HumanMessage(content=state["user_input"]),
    ])
    return {
        "department": "技术组",
        "response": response.content,
        "messages": [AIMessage(content=f"[路由] 已转到技术组，回复内容：{response.content}")],
    }


def handle_consult(state: ServiceState):
    """节点2c：业务咨询组 —— 生成咨询回复"""
    response = deepseek_llm.invoke([
        SystemMessage(content=(
            "你是业务咨询顾问。用户想了解产品信息，请热情、专业地回答问题。"
            "如果不确定具体细节，请引导用户联系人工客服或查看官网帮助中心。"
            "回复控制在80字以内。"
        )),
        HumanMessage(content=state["user_input"]),
    ])
    return {
        "department": "咨询组",
        "response": response.content,
        "messages": [AIMessage(content=f"[路由] 已转到咨询组，回复内容：{response.content}")],
    }


def handle_feedback(state: ServiceState):
    """节点2d：投诉建议组：生成反馈回复"""
    response = deepseek_llm.invoke([
        SystemMessage(content=(
            "你是客户关系专员。用户提出了投诉或建议，请真诚道歉或感谢，"
            "并告知已记录反馈、会尽快改进。对于投诉承诺24小时内由主管回访。"
            "回复控制在80字以内。"
        )),
        HumanMessage(content=state["user_input"]),
    ])
    return {
        "department": "客服组",
        "response": response.content,
        "messages": [AIMessage(content=f"[路由] 已转到客服组，回复内容：{response.content}")],
    }


def summarize(state: ServiceState):
    """节点3：汇总：生成最终处理摘要"""
    return {
        "messages": [
            AIMessage(content=(
                f"【处理摘要】意图={state['intent']} | "
                f"部门={state['department']} | "
                f"回复={state['response']}"
            ))
        ],
    }


# 3. 路由逻辑
def route_by_intent(
    state: ServiceState,
) -> Literal["handle_refund", "handle_tech", "handle_consult", "handle_feedback"]:
    """按识别的意图路由到对应处理节点"""
    intent_map = {
        "refund": "handle_refund",
        "tech": "handle_tech",
        "consult": "handle_consult",
        "feedback": "handle_feedback",
    }
    # 如果 LLM 返回了无法识别的意图，默认走咨询
    return intent_map.get(state["intent"], "handle_consult")


# 4. 构建图
builder = StateGraph(ServiceState)

builder.add_node("check_intent", check_intent)
builder.add_node("handle_refund", handle_refund)
builder.add_node("handle_tech", handle_tech)
builder.add_node("handle_consult", handle_consult)
builder.add_node("handle_feedback", handle_feedback)
builder.add_node("summarize", summarize)

builder.add_edge(START, "check_intent")

builder.add_conditional_edges(
    "check_intent",
    route_by_intent,
    {
        "handle_refund": "handle_refund",
        "handle_tech": "handle_tech",
        "handle_consult": "handle_consult",
        "handle_feedback": "handle_feedback",
    },
)

# 四个处理分支汇聚到汇总节点
for node in ["handle_refund", "handle_tech", "handle_consult", "handle_feedback"]:
    builder.add_edge(node, "summarize")

builder.add_edge("summarize", END)


# 5. 运行
if __name__ == "__main__":
    # 替换为你的实际连接信息
    DB_URI = "postgresql://postgres:postgres123@192.168.179.5:5432/langgraph_db"

    with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
        checkpointer.setup()
        graph = builder.compile(checkpointer=checkpointer)

        # 5.1 绘制图
        png_data = graph.get_graph().draw_mermaid_png()

        with open("service_graph.png", "wb") as f:
            f.write(png_data)
        print("图片已保存到 service_graph.png")

        # 5.2 模拟四个用户发送不同消息
        MESSAGES = [
            ("user_001", "我上周买的耳机有杂音，我要退货退款！"),
            ("user_002", "你好，请问你们的企业版和个人版有什么区别？"),
            ("user_003", "你们的App更新之后就一直在闪退，根本用不了！"),
            ("user_004", "App更新后一直闪退，怎么解决？"),
        ]

        for thread_id, msg in MESSAGES:
            config = {"configurable": {"thread_id": thread_id}}

            result = graph.invoke(
                {
                    "messages": [HumanMessage(content=msg)],
                    "user_input": msg,
                    "intent": "",
                    "department": "",
                    "response": "",
                },
                config,
            )
            print("="*60)
            print(f"对话内容：{msg}; 意图: {result['intent']} ;部门: {result['department']}")
            print(f"回复: {result['response']}")
            print("result:", result)

```

以上代码运行结果如下：

![image.png](./images/22Checkpointer短期记忆_c07addc78d4f405899df07999f99708b_88a6f2.jpg)

当多次重复运行代码后，可以看到最终每个thread\_id输出的result\['messages'\]会有之前的状态。

### **3.6.2. langgraph dev 部署运行**

如果要对外提供服务（前端页面调用、其他微服务调用），需要部署为 HTTP API，可以通过langgraph dev 把编译好的 graph 暴露为 REST API，同时提供一个 Studio Web UI 用于可视化调试。

langgraph dev 会自动注入一个 Checkpointer，默认是存储在内存中，如果我们启动langgraph dev使用自己的Checkpointer 需要在langgraph.json中配置“checkpointer”，这样运行langgraph dev后会自动注入自己的checkpointer替换原有的内存Checkpointer。

案例代码文件结构如下：

```python
项目根目录/
├── langgraph.json                              # 部署配置
├── .env                                        # 环境变量
├── init_llm.py                                 # LLM 初始化
└── 03_langgraph_checkpointer/
    └── 13_langgraph_checkpoint_demo/
        ├── graph.py                            # 图定义
        ├── checkpointer.py                     # 自定义Checkpointer
        └── client.py                           # 远程调用客户端
```

#### **3.6.2.1. langgraph.json代码**

首先在langgraph.json中增加如下代码

```python
{
  ... ...
  "graphs": {
    "agent": "./02_langgraph_use/05_langgraph_dev_demo.py:graph",
    "weather_agent": "./02_langgraph_use/06_agent_demo.py:agent",
    "langgraph_checkpoint":       "./03_langgraph_checkpointer/13_langgraph_checkpoint_demo/graph.py:graph"
  },


  "checkpointer": {
    "backend": "custom",
    "path": "./03_langgraph_checkpointer/13_langgraph_checkpoint_demo/checkpointer.py:get_checkpointer"
  },

  ... ...
}

```

以上配置注意如下几点：

1) graphs 下的 key（如 "langgraph\_checkpoint"）是客户端的Graph图名，后续client要调用该Graph图名来指定执行对应的Graph图。
2) checkpointer.backend配置为custom表示使用自己的checkpointer，“path”表示自己checkpointer实现的类以及获取自定义checkpointer的方法。增加的该配置就是告诉LangGraph用哪个文件提供 Checkpointer。

#### **3.6.2.2.** [**checkpointer.py**](http://checkpointer.py)**代码**

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

#### **3.6.2.3.** [**graph.py**](http://graph.py)**代码**

[graph.py](http://graph.py)代码如下：

```python
import operator
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, AnyMessage


from langgraph.graph import StateGraph, START, END

from init_llm import deepseek_llm


# 1. 定义状态
class ServiceState(TypedDict):
    """一条客服会话的完整状态"""
    # 消息历史（add 归并器，追加不覆盖）
    messages: Annotated[list[AnyMessage], operator.add]

    # 业务字段（标量，每次覆盖最新值）
    user_input: str          # 用户最新输入
    intent: str              # 识别的意图：refund(退款) / tech(技术) / consult(咨询) / feedback(投诉)
    department: str          # 路由目标部门
    response: str            # 生成的回复


# 2. 定义节点
def check_intent(state: ServiceState):
    """节点1：LLM 识别用户意图（四选一）"""
    prompt = SystemMessage(content=(
        "你是一个客服意图识别助手。分析用户消息，判断意图属于以下哪一种：\n"
        "- refund: 退款、退货、赔偿相关问题\n"
        "- tech: 产品使用故障、技术问题\n"
        "- consult: 产品咨询、业务询问\n"
        "- feedback: 投诉、建议、意见反馈\n"
        "只回复一个单词：refund / tech / consult / feedback"
    ))

    user_input = state["user_input"]
    response = deepseek_llm.invoke([prompt, HumanMessage(content=user_input)])

    intent = response.content.strip().lower()

    return {
        "intent": intent,
        "messages": [AIMessage(content=f"[意图识别] 用户输入：{user_input}，意图识别为： {intent}")],
    }


def handle_refund(state: ServiceState):
    """节点2a：退款处理组：生成退款相关回复"""
    response = deepseek_llm.invoke([
        SystemMessage(content=(
            "你是退款客服专员。用户想退款或投诉账单问题，请礼貌地了解具体情况，"
            "并告知退款流程："
            "   1)核实订单 "
            "   2)提交退款申请 "
            "   3)3-5个工作日到账。"
            "回复控制在80字以内。"
        )),
        HumanMessage(content=state["user_input"]),
    ])
    return {
        "department": "退款组",
        "response": response.content,
        "messages": [AIMessage(content=f"[路由] 已转到退款组，回复内容：{response.content}")],
    }


def handle_tech(state: ServiceState):
    """节点2b：技术支持组：生成技术问题回复"""
    response = deepseek_llm.invoke([
        SystemMessage(content=(
            "你是技术支持工程师。用户遇到了产品使用问题，请先表示理解，"
            "然后给出排查步骤："
            "   1)确认问题现象 "
            "   2)尝试基础排查（重启/更新）"
            "   3)如无法解决则升级到高级工程师。"
            "回复控制在80字以内。"
        )),
        HumanMessage(content=state["user_input"]),
    ])
    return {
        "department": "技术组",
        "response": response.content,
        "messages": [AIMessage(content=f"[路由] 已转到技术组，回复内容：{response.content}")],
    }


def handle_consult(state: ServiceState):
    """节点2c：业务咨询组 —— 生成咨询回复"""
    response = deepseek_llm.invoke([
        SystemMessage(content=(
            "你是业务咨询顾问。用户想了解产品信息，请热情、专业地回答问题。"
            "如果不确定具体细节，请引导用户联系人工客服或查看官网帮助中心。"
            "回复控制在80字以内。"
        )),
        HumanMessage(content=state["user_input"]),
    ])
    return {
        "department": "咨询组",
        "response": response.content,
        "messages": [AIMessage(content=f"[路由] 已转到咨询组，回复内容：{response.content}")],
    }


def handle_feedback(state: ServiceState):
    """节点2d：投诉建议组：生成反馈回复"""
    response = deepseek_llm.invoke([
        SystemMessage(content=(
            "你是客户关系专员。用户提出了投诉或建议，请真诚道歉或感谢，"
            "并告知已记录反馈、会尽快改进。对于投诉承诺24小时内由主管回访。"
            "回复控制在80字以内。"
        )),
        HumanMessage(content=state["user_input"]),
    ])
    return {
        "department": "客服组",
        "response": response.content,
        "messages": [AIMessage(content=f"[路由] 已转到客服组，回复内容：{response.content}")],
    }


def summarize(state: ServiceState):
    """节点3：汇总：生成最终处理摘要"""
    return {
        "messages": [
            AIMessage(content=(
                f"【处理摘要】意图={state['intent']} | "
                f"部门={state['department']} | "
                f"回复={state['response']}"
            ))
        ],
    }


# 3. 路由逻辑
def route_by_intent(
    state: ServiceState,
) -> Literal["handle_refund", "handle_tech", "handle_consult", "handle_feedback"]:
    """按识别的意图路由到对应处理节点"""
    intent_map = {
        "refund": "handle_refund",
        "tech": "handle_tech",
        "consult": "handle_consult",
        "feedback": "handle_feedback",
    }
    # 如果 LLM 返回了无法识别的意图，默认走咨询
    return intent_map.get(state["intent"], "handle_consult")


# 4. 构建图
builder = StateGraph(ServiceState)

builder.add_node("check_intent", check_intent)
builder.add_node("handle_refund", handle_refund)
builder.add_node("handle_tech", handle_tech)
builder.add_node("handle_consult", handle_consult)
builder.add_node("handle_feedback", handle_feedback)
builder.add_node("summarize", summarize)

builder.add_edge(START, "check_intent")

builder.add_conditional_edges(
    "check_intent",
    route_by_intent,
    {
        "handle_refund": "handle_refund",
        "handle_tech": "handle_tech",
        "handle_consult": "handle_consult",
        "handle_feedback": "handle_feedback",
    },
)

# 四个处理分支汇聚到汇总节点
for node in ["handle_refund", "handle_tech", "handle_consult", "handle_feedback"]:
    builder.add_edge(node, "summarize")

builder.add_edge("summarize", END)


# 不传 checkpointer，通过langgraph dev 从 langgraph.json 读取配置自动注入
graph = builder.compile()

```

[以上graph.py](http://以上graph.py)代码注意点如下：

1) compile()不传checkpointer，langgraph dev从langgraph.json读取配置自动注入。

#### **3.6.2.4.** [**client.py**](http://client.py)**代码**

[client.py](http://client.py)代码如下：

```python
"""
客服路由系统 —— 交互式命令行客户端
"""
import asyncio
import uuid

from langgraph_sdk import get_client

client = get_client(url="http://127.0.0.1:2024")


async def main():
    # 首次启动如果用户输入thread_id 就用用户的thread_id 否则自动创建一个thread_id
    current_thread_id = "435973d3-40f0-49d1-8bb4-1fb2574d55ca"

    if len(current_thread_id.strip()) != 36:
        # 如果用户没有输入thread_id 则自动创建一个thread_id
        current_thread_id = str(uuid.uuid4())

    # 在服务端注册这个 thread_id
    # if_exists="do_nothing"：已存在则复用（恢复 Checkpointer 保存的上下文），不存在则新建
    await client.threads.create(thread_id=current_thread_id, if_exists="do_nothing")

    print(f"当前thread_id: {current_thread_id}")

    while True:
        try:
            user_input = input("[用户]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n 【输出错误，再见！】\n")
            break

        if not user_input:
            continue

        print("处理中...\n\n")

        try:
            result = await client.runs.wait(
                current_thread_id,
                "langgraph_checkpoint",
                input={
                    "messages": [{"role": "user", "content": user_input}],
                    "user_input": user_input,
                    "intent": "",
                    "department": "",
                    "response": "",
                },
            )

            print(f"对话内容：{user_input}; 意图: {result['intent']} ;部门: {result['department']}")
            print(f"回复: {result['response']}")
            print("result:", result)

        except Exception as e:
            print(f"请求失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())

```

[以上client.py](http://以上client.py)代码注意如下几点：

1) 关于thread\_id，LangGraph dev中必须要求thread\_id是UUID格式。
2) thread\_id必须先在服务端注册然后再使用，“await client.threads.create(thread\_id=current\_thread\_id, if\_exists="do\_nothing")”就是 把 UUID 注册到服务端。

#### **3.6.2.5. 案例运行**

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

![image.png](./images/22Checkpointer短期记忆_dadaeb38b51e45608d535820149aeba7_c2ef02.jpg)

**3\.** [**启动client.py**](http://启动client.py)**，输入如下对话**

```python
我上周买的耳机有杂音，我要退货退款！
你好，请问你们的企业版和个人版有什么区别？
你们的App更新之后就一直在闪退，根本用不了！
App更新后一直闪退，怎么解决？
```

重启client后，再次对话，只要thread\_id相同，之前保存的状态也可以看到。
