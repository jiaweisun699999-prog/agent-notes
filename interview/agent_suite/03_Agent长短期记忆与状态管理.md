> 📌 **[AI 大模型与云原生全栈知识库](../../README.md)** / **[Agent & LangGraph 题库套件](./README.md)**
> 🏠 [返回主页 README](../../README.md) | 📚 [专题索引](./README.md) | ⚡ [30分钟速记](../00_面试冲刺30分钟速记卡片.md)

---

# 🎓 03. Agent 长短期记忆与状态管理面试题 (深度重构版)

## 三、短期记忆与状态管理面试题

### Q1: 什么是 Agent 的短期记忆？它的生命周期与实现原理是什么？
**标准回答 (16K-22K 满分表达)**：
- **定义**：短期记忆 (Short-term Memory) 是 Agent 在**单次对话会话或单次任务运行周期内**的上下文记忆。
- **生命周期**：绑定特定的 `thread_id`，随任务开启而创建，任务结束或会话关闭后不再主动保留到全局公共空间。
- **底层实现**：在 LangGraph 中通过 `Checkpointer` 实现，每个节点执行完毕后将当前的 `State` 序列化为快照存入持久化介质。

---

### Q2: 短期记忆的两种主要存储方式及其优缺点。
**标准回答 (16K-22K 满分表达)**：
1. **内存级存储 (`MemorySaver`)**：
   - 特点：状态纯保存在 Python 进程内存中，读写极快。
   - 缺点：进程重启或服务多实例部署（如 K8s 扩容）时数据丢失，仅适合本地开发测试。
2. **持久化数据库存储 (`PostgresSaver` / `SqliteSaver`)**：
   - 特点：每次 Superstep 将 Checkpoint 写入关系型数据库或 SQLite。
   - 优点：支持服务无状态重启、生产环境断点恢复与多节点共享。

---

### Q3: 什么是自定义 State？它的定义方式与 Reducer 合并机制是什么？
**标准回答 (16K-22K 满分表达)**：
- **定义**：自定义 State 是图网络中所有节点共享的全局状态字典。
- **定义方式与 Reducer 机制**：
  ```python
  from typing import Annotated, TypedDict
  from langgraph.graph import add_messages

  class AgentState(TypedDict):
      messages: Annotated[list, add_messages] # 使用 add_messages 作为 Reducer 追加消息
      user_id: str
      retry_count: int
  ```
  - **Reducer (合并函数)**：如 `add_messages`，决定当节点返回 `{"messages": [new_msg]}` 时是**直接替换**原列表还是**追加/合并**（通过 `id` 去重更新）。

---

### Q4: 在 LangGraph 中如何读取与动态改写 State 状态？
**标准回答 (16K-22K 满分表达)**：
- **节点内部读取与修改**：Node 函数接收当前 `state: AgentState`，返回一个包含增量修改字段的 Python `dict`。
- **外部运行时读取与修改**：
  - **读取**：`snapshot = app.get_state(config)` $
\rightarrow$ `snapshot.values` 获取状态。
  - **动态改写**：`app.update_state(config, {"retry_count": 0}, as_node="tool_node")`，模拟某个节点发出更新，实现状态修正。

---

### Q5: State (状态) 与 Context (运行时上下文) 的核心区别是什么？
**标准回答 (16K-22K 满分表达)**：
- **State (状态)**：存放**业务层面**的动态数据（如消息列表、中间计算结果、用户选定选项）。随节点流动而被改写，属于可变数据。
- **Context (运行时上下文)**：存放**引擎与环境层面**的静态/单例配置（如底层模型实例、数据库连接池、鉴权 Token、流输出器）。在整个任务生命周期内只读传递。

---

### Q6: 消息超过 LLM 上下文窗口时的四种主流处理策略及其生产实现。
**标准回答 (16K-22K 满分表达)**：
1. **滑动窗口截断 (Before Model Truncation)**：
   - 使用 `trim_messages(messages, max_tokens=4000, strategy="last")` 仅保留最近的 $N$ 个 Token，防止 Token 超限。
2. **特定历史消息删除 (After Model Deletion)**：
   - 返回 `RemoveMessage(id=target_msg_id)` 从 State 消息列表中物理删除不重要的中间工具调用结果。
3. **对话历史摘要压缩 (Summarize Strategy)**：
   - 专门触发一个轻量级 LLM 节点，将过往的 20 轮对话压缩为一段 `SystemMessage("历史对话摘要：...")`。
4. **Hybrid 混合策略 (推荐生产方案)**：系统提示词不变 + 最近 5 轮完整对话 + 远期历史摘要。

---

## 四、长期记忆面试题

### Q1: 什么是 Agent 的长期记忆？它的核心应用场景是什么？
**标准回答 (16K-22K 满分表达)**：
- **定义**：长期记忆 (Long-term Memory) 是**跨会话、跨 Task、跨设备持久化保存**的知识与用户画像库。
- **核心场景**：
  1. **用户个性化偏好 (User Profiles)**：记录用户的语言偏好、职业信息、代码风格。
  2. **跨会话经验总结 (Agent Reflection/Experience)**：记录 Agent 过去解决某些报错的成功案例，未来遇同类问题直接检索复用。

---

### Q2: 长期记忆的存储空间与检索机制是什么？
**标准回答 (16K-22K 满分表达)**：
- **存储介质**：依托 `BaseStore`（如 `InMemoryStore` 或 `PostgresStore`）。
- **层次化 Namespace (命名空间)**：按 `(tenant_id, user_id, memory_type)` 隔离数据。
- **检索机制**：
  - 键值精准查询：`store.get(namespace, key)`
  - 语义向量检索：对记忆文本生成 Embedding，调用 `store.search(namespace, query="用户喜欢什么编程语言")` 实现 Top-K 相关记忆召回。

---

### Q3: 深度对比：Agent 的短期记忆与长期记忆。
**标准回答 (16K-22K 满分表达)**：

| 维度 | 短期记忆 (Short-term Memory) | 长期记忆 (Long-term Memory) |
| :--- | :--- | :--- |
| **隔离标识** | 基于 `thread_id` (会话级别) | 基于 `namespace` (用户/租户级别) |
| **底层实现** | `Checkpointer` (状态快照) | `Store` / VectorStore (长期存储库) |
| **数据生命周期** | 随单次会话结束而存档/清理 | 永久持久化保存 |
| **检索方式** | 顺序读取线性消息列表 | 键值精准匹配 + 向量语义检索 |
| **典型用途** | 维持当前多轮对话的上下文指代 | 个性化 Recommendation、用户 Portrait、经验沉淀 |

---

> 🏠 **[返回主页 README](../../README.md)** | 📚 **[专题索引](./README.md)** | ◀️ **上一篇：[02. LangChain 与 Agent 核心基础](./02_LangChain与Agent核心基础.md)** | ▶️ **下一篇：[04. HITL 人工介入与 Guardrails 安全护栏](./04_HITL人工介入与Guardrails安全护栏.md)** | ⚡ **[30分钟速记](../00_面试冲刺30分钟速记卡片.md)**
