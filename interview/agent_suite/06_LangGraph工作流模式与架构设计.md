> 📌 **[AI 大模型与云原生全栈知识库](../../README.md)** / **[Agent & LangGraph 题库套件](./README.md)**
> 🏠 [返回主页 README](../../README.md) | 📚 [专题索引](./README.md) | ⚡ [30分钟速记](../00_面试冲刺30分钟速记卡片.md)

---

# 🎓 06. LangGraph 工作流模式与架构设计面试题 (深度重构版)

## 九、LangGraph 核心面试题 (Part 1：架构与设计模式)

### Q1: 什么是 LangGraph？为什么在复杂生产项目中推荐使用它而非传统的 AgentExecutor？
**标准回答 (16K-22K 满分表达)**：
- **定义**：LangGraph 是基于图（Graph）结构的大模型 Agent 编排框架。
- **对比传统 AgentExecutor 的优势**：
  1. **显式状态可控 (StateGraph)**：通过 Directed Graph 显式定义节点 (Nodes) 与条件边 (Edges)，彻底消除死循环。
  2. **细粒度持久化与断点 (Checkpointer)**：原生支持基于 Superstep 的快照保存、人工介入 (HITL) 与时间旅行 (Time-travel)。
  3. **原生支持循环与分支 (Cycles & Branching)**：完美支持多轮反思迭代与多 Agent 拓扑网络。

---

### Q2: 详细说明 LangGraph 的五个关键基础能力。
**标准回答 (16K-22K 满分表达)**：
1. **持久化存储 (Persistence)**：基于 Checkpointer 保存历史状态。
2. **人工介入 (Human-in-the-Loop)**：支持在任意节点前/后挂起图。
3. **全量流式输出 (Streaming)**：支持 Token 级、State 级与自定义日志流式推送。
4. **完整记忆系统 (Short & Long Memory)**：Checkpointer (单会话) + Store (跨会话)。
5. **强可观测性 (Observability)**：原生集成 LangSmith，支持 Call Tree 追溯。

---

### Q3: 生产级 Agent 开发的“LangGraph 五步设计法”是什么？
**标准回答 (16K-22K 满分表达)**：
1. **步骤拆解**：将复杂业务需求拆解为离散的孤立节点（如“检索”、“LLM 生成”、“格式校验”）。
2. **操作分类**：识别哪些是 LLM 节点，哪些是纯 Python 代码节点，哪些是工具节点。
3. **State 设计**：使用 `TypedDict` 设计全局状态结构，并分配 Reducer 合并函数。
4. **Node 编写**：编写无状态或仅改写指定 State 字典的节点函数。
5. **Graph 组装**：添加 `add_node`, `add_edge`, `add_conditional_edges` 并 `compile()` 编译。

---

### Q4: 深入剖析 Anthropic / LangChain 总结的五种典型 Agent 工作流模式。
**标准回答 (16K-22K 满分表达)**：
1. **Prompt Chaining (提示链)**：线性流水线（Node A $
\rightarrow$ Node B $
\rightarrow$ Node C）。
2. **Routing (路由分发)**：LLM 判断输入意图，动态跳转到专有子节点（条件边）。
3. **Parallelization (并行化)**：一个节点触发多个平行子节点并发执行（Guardrail 校验与 Tool 并发）。
4. **Orchestrator-Workers (编排者-工作者)**：主控 Node 拆解任务分配给多个 Worker 节点处理，最后汇总。
5. **Evaluator-Optimizer (评估器-优化器)**：LLM 生成 $
\rightarrow$ 校验节点检测评分 $
\rightarrow$ 不合格打回优化循环（如代码生成与自修复）。

---

### Q5: `ToolRuntime` 与 `ToolNode` 的区别与适用场景。
**标准回答 (16K-22K 满分表达)**：
- **`ToolNode`**：LangGraph 内置的预置节点，自动接收 `messages` 中的 `tool_calls` 并标准化并行执行工具。适合大多数通用工具。
- **`ToolRuntime`**：允许工具内部直接读取/修改图的全局 `State` 或调用 `store`。适合需要操作全局状态的高级自定义工具。

---

### Q6 & Q7: 什么是 Checkpointer？它的三个核心概念与底层机制是什么？
**标准回答 (16K-22K 满分表达)**：
- **定义**：Checkpointer 是 LangGraph 实现状态保存与会话恢复的核心组件。
- **三个核心概念**：
  1. **`Thread` (会话线程)**：隔离不同用户/会话的唯一标识 (`thread_id`)。
  2. **`Checkpoint` (检查点快照)**：包含该步的 `values` (状态)、`next` (即将执行的节点)、`metadata`。
  3. **`Superstep` (超级步)**：图计算的一个同步执行单元（同步并行节点执行算作一步）。

---

### Q8: 状态持久化的三种模式与四种实现方式。
**标准回答 (16K-22K 满分表达)**：
- **三种模式**：`exit` (退出时持久化)、`async` (异步无阻塞写入)、`sync` (同步阻塞写入)。
- **四种实现方式**：`MemorySaver` (内存)、`SqliteSaver` (本地数据库)、`AsyncPostgresSaver` (生产级 PostgreSQL)、`MySQLSaver`。

---

### Q9: 如何在 LangGraph 中获取历史状态并实现“时间旅行 (Time-Travel)”？
**标准回答 (16K-22K 满分表达)**：
- **历史获取**：`history = list(app.get_state_history(config))`，遍历返回所有 Superstep 的快照。
- **时间旅行 (Time-travel)**：
  1. 选中历史某个 `checkpoint_id` 的配置 `target_config = {"configurable": {"thread_id": "123", "checkpoint_id": "abc"}}`。
  2. 调用 `app.update_state(target_config, {"messages": [...]})` 修正该历史状态。
  3. 再次 `app.invoke(None, target_config)`，图将基于该历史分叉点继续往下执行。

---

### Q10 & Q11 & Q12 & Q13: Checkpointer 与 Store 的深度对比及其语义检索实现。
**标准回答 (16K-22K 满分表达)**：
- **核心对比**：Checkpointer 存单会话状态快照；Store 存跨会话全局长期记忆。
- **语义检索实现**：实例化 Store 时传入 `index={"embed": embeddings, "dims": 1536}`，调用 `store.search(namespace, query="用户喜好")` 自动执行余弦相似度检索返回相关记忆项。

---

> 🏠 **[返回主页 README](../../README.md)** | 📚 **[专题索引](./README.md)** | ◀️ **上一篇：[05. Runtime 运行时与 MCP 协议](./05_Runtime运行时与MCP协议.md)** | ▶️ **下一篇：[07. LangGraph 容错机制与全量流式输出](./07_LangGraph容错机制与全量流式输出.md)** | ⚡ **[30分钟速记](../00_面试冲刺30分钟速记卡片.md)**
