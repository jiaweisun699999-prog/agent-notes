> 📌 **[AI 大模型与云原生全栈知识库](../../README.md)** / **[Agent & LangGraph 题库套件](./README.md)**
> 🏠 [返回主页 README](../../README.md) | 📚 [专题索引](./README.md) | ⚡ [30分钟速记](../00_面试冲刺30分钟速记卡片.md)

---

# 🎓 07. LangGraph 容错机制与全量流式输出面试题 (深度重构版)

## 九、LangGraph 核心面试题 (Part 2：容错与流式传输)

### Q14 & Q15: 什么是 LangGraph 容错机制？详细说明三种可组合的容错策略。
**标准回答 (16K-22K 满分表达)**：
- **定义**：防止因网络波动、第三方 API 超时或工具报错导致整图崩溃的防御机制。
- **三种可组合策略**：
  1. **自动重试策略 (`RetryPolicy`)**：
     ```python
     from langgraph.types import RetryPolicy
     builder.add_node("api_node", call_api, retry=RetryPolicy(max_attempts=3, retry_on=ValueError))
     ```
  2. **节点超时策略 (`timeout`)**：为节点指定最大允许执行时间（如 `timeout=10`），超时强制抛出 TimeoutError。
  3. **捕获降级路由 (`Command(goto=...)`)**：在 Node 内 `try...except` 捕获异常后，返回 `Command(goto="fallback_node", update={"error": str(e)})` 跳转至降级处理节点。

---

### Q16: 运行超时 (Run Timeout) 与空闲超时 (Idle Timeout) 的本质区别。
**标准回答 (16K-22K 满分表达)**：
- **运行超时 (Run Timeout)**：限制单次节点或整图从开始到结束的**最大允许总耗时**。
- **空闲超时 (Idle Timeout)**：限制图在等待外部输入（如等待 HITL 人工恢复）或底层 I/O 响应时的**最大静默等待时长**。

---

### Q17 & Q18: 错误处理中 `goto` 的作用与默认容错机制解决的痛点。
**标准回答 (16K-22K 满分表达)**：
- **`goto` 的作用**：在发生错误时打破原有的图路径，动态重定向到指定的恢复节点（如重试或者降级返回通用答案）。
- **默认容错机制**：框架默认会在未显式捕获错误时保存当前快照，防止进程崩溃导致会话状态丢失，便于事后排查和从断点恢复。

---

### Q19: 详细说明 LangGraph 支持的七种流式输出模式。
**标准回答 (16K-22K 满分表达)**：
1. **`values`**：在每个 Superstep 结束时输出当前图的全量状态对象。
2. **`updates`**：仅输出当前节点产生的增量修改。
3. **`messages`**：流式推送 LLM 生成的实时 Token 增量及对应节点信息。
4. **`tasks`**：流式输出后台节点的启动与完成任务事件。
5. **`debug`**：输出底层图引擎执行的详细调试信息。
6. **`checkpoints`**：输出每次快照存盘的检查点数据。
7. **`custom`**：在 Node 内部调用 `stream_writer("自定义日志")` 时抛出自定义流。

---

### Q20: 流式输出 v1、v2、v3 版本演进与差异。
**标准回答 (16K-22K 满分表达)**：
- **v1 (Legacy)**：仅支持简单的字符串及基础消息 Token 流式推送。
- **v2**：引入统一的 `astream_events` 规范，支持按事件类型 (`on_chat_model_stream`, `on_tool_start`) 做结构化过滤。
- **v3 (惰性流/Lazy Stream)**：性能最优，按需消费机制（只在被订阅时才计算和推送），降低无用序列化开销。

---

### Q21 & Q22: 事件流与运行流的区别，以及如何做流式数据过滤？
**标准回答 (16K-22K 满分表达)**：
- **运行流 (`stream`)**：站在图的视角，推送 Superstep / Node 级别的状态改变。
- **事件流 (`astream_events`)**：站在底层的视角，深度监听内部所有组件发生的微观事件（如 Tool 何时开始执行、LLM 产生了哪些 Token）。
- **过滤方案**：
  - 按节点过滤：指定 `stream_mode` 参数。
  - 按标签/名称过滤：在 `astream_events(include_tags=["public"])` 中过滤。

---

### Q23 & Q24: `GraphRunStream` 投影字段与 `messages` 属性的组成。
**标准回答 (16K-22K 满分表达)**：
- **`messages` 属性四要素**：
  1. `node`：产生该消息的节点名称。
  2. `text`：当前增量或完整的文本内容。
  3. `output`：标准的 `AIMessageChunk` 或 `ToolMessage` 实例。
  4. `usage_metadata`：该次调用消耗的 `input_tokens` 与 `output_tokens` 统计。

---

> 🏠 **[返回主页 README](../../README.md)** | 📚 **[专题索引](./README.md)** | ◀️ **上一篇：[06. LangGraph 工作流模式与架构设计](./06_LangGraph工作流模式与架构设计.md)** | ▶️ **下一篇：[08. LangGraph 高级 HITL 与 Interrupt 核心规则](./08_LangGraph高级HITL与Interrupt核心规则.md)** | ⚡ **[30分钟速记](../00_面试冲刺30分钟速记卡片.md)**
