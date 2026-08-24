> 📌 **[AI 大模型与云原生全栈知识库](../../README.md)** / **[Agent & LangGraph 题库套件](./README.md)**
> 🏠 [返回主页 README](../../README.md) | 📚 [专题索引](./README.md) | ⚡ [30分钟速记](../00_面试冲刺30分钟速记卡片.md)

---

# 🎓 05. Runtime 运行时与 MCP 协议面试题 (深度重构版)

## 七、Runtime 运行时上下文面试题


### Q0: 什么是 Agent 的 Runtime (运行时)？它的核心概念、职责与实现原理是什么？
**标准回答 (16K-22K 满分表达)**：
- **核心定义**：Runtime (运行时) 是 Agent 应用在执行过程中的**宿主环境与容器引擎**。它为上层的智能体逻辑提供底层资源调度、状态维护、生命周期管理与上下文隔离。
- **三大核心职责**：
  1. **上下文管理 (Context Management)**：隔离不同用户/会话的配置、全局变量与环境变量。
  2. **状态与记忆持久化 (State & Storage)**：向节点暴露 `State` 改写句柄与长期记忆 `Store` 读写接口。
  3. **数据流与事件分发 (Streaming & Event Dispatch)**：提供统一的 `streamWriter` 句柄，支持向前端实时推送 Token、任务事件或自定义 Trace 日志。
- **实现原理**：在 LangGraph / LangChain 中，Runtime 采用依赖注入 (Dependency Injection) 模式，在图启动时创建容器，将 `config`、`store` 和底层线程句柄自动注入到各个 Node 函数和 Tool 执行体中。


### Q1: Runtime 运行时承载哪些核心信息？
**标准回答 (16K-22K 满分表达)**：
- **定义**：Runtime 是 Agent 运行期间的容器环境。
- **五大核心承载组件**：
  1. **`context`**：运行时的静态与环境依赖配置。
  2. **`store`**：跨会话长期记忆访问句柄 (`BaseStore`)。
  3. **`streamWriter`**：自定义流输出器，用于向前端 `yield` 自定义日志或中间状态。
  4. **`ExecutionInfo`**：当前的 Superstep 步数、节点名称、线程 ID、重试次数。
  5. **`ServerInfo`**：部署服务的节点信息、环境变量与鉴权凭证。

---

### Q2: 运行时包含哪三种上下文？各自的作用是什么？
**标准回答 (16K-22K 满分表达)**：
1. **模型上下文 (Model Context)**：包含 System Prompt、当前对话 Message 历史、Tool 定义与模组参数（Temperature, MaxTokens）。
2. **工具上下文 (Tool Context)**：工具执行时所需的外部凭证 (API Keys)、当前用户 ID、数据库连接池。
3. **生命周期上下文 (Lifecycle Context)**：监听 `on_chain_start`, `on_tool_end`, `on_error` 等生命周期钩子，用于指标监控与日志收集。

---

### Q3: 模型上下文的五个核心维度是什么？
**标准回答 (16K-22K 满分表达)**：
1. **System Prompt (系统提示词)**
2. **Message History (消息历史列表)**
3. **Tool Definitions (工具 Schema 定义)**
4. **Model Selection (模型选择与参数配置)**
5. **Output Format (结构化输出约束)**

---

### Q4: 上下文数据的三大来源及其优先级策略。
**标准回答 (16K-22K 满分表达)**：
1. **`RuntimeContext` (初始化注入)**：环境变量、全局配置，优先级最高（只读）。
2. **`State` (图状态节点流动)**：单会话可变业务状态。
3. **`Store` (持久化长期记忆)**：按需检索加载的长期记忆库。

---

## 八、MCP (Model Context Protocol) 面试题

### Q1: 什么是 MCP (模型上下文协议)？它的核心使命是什么？
**Standard Answer (16K-22K 满分表达)**：
- **定义**：MCP (Model Context Protocol) 是由 Anthropic 推出的**开放标准通信协议**。
- **核心使命**：解决 LLM 与外部数据源/工具连接的碎片化问题。类似于 Web 开发中的 HTTP 或硬设备接口中的 USB-C，为 LLM 提供统一标准的方式连接工具 (Tools)、资源 (Resources) 和提示词 (Prompts)。

---

### Q2: 深入对比：MCP 协议与 LangChain Agent Tools 的区别。
**标准回答 (16K-22K 满分表达)**：

| 维度 | LangChain Agent Tools | MCP 协议 (Model Context Protocol) |
| :--- | :--- | :--- |
| **本质定位** | 某个框架内部的具体 Python/JS 代码组件 | 跨语言、跨框架的底层 client-server 通信协议 |
| **耦合度** | 强绑定 LangChain 框架 | 彻底解耦（Client 可以是 Claude Desktop/Cursor，Server 可以是 Python/Go/Rust） |
| **安全与认证** | 依赖应用层手动编写 OAuth/鉴权 | 协议层原生提供鉴权、权限拦截与资源隔离 |
| **生态复用** | 仅限于 Python/JS 同项目内使用 | 编写一次 MCP Server，可在所有支持 MCP 的 IDE/Agent 中无缝调用 |

---

### Q3: MCP 的三个核心角色及其交互关系。
**标准回答 (16K-22K 满分表达)**：
1. **MCP Host / Client (客户端)**：发起交互的 Agent 容器或应用（如 Cursor, Claude Desktop, LangGraph App）。
2. **MCP Server (服务端)**：暴露工具、资源或 Prompt 的独立服务端程序（如 PostgreSQL MCP Server, GitHub MCP Server）。
3. **Local/Remote Resources (数据资源提供者)**：底层的数据库、文件系统、API 接口。

---

### Q4: MCP 的两种传输方式 (Transports) 及其技术差异。
**标准回答 (16K-22K 满分表达)**：
1. **Stdio Transport (标准输入输出传输)**：
   - 原理：Client 通过子进程 (Subprocess) 启动 Server，通过 `stdin/stdout` 传输 JSON-RPC 消息。
   - 场景：本地工具（文件系统、本地 SQLite 操作）。
2. **SSE Transport (Server-Sent Events + HTTP POST)**：
   - 原理：Client 通过 SSE 订阅 Server 的事件流，通过 HTTP POST 发送 Request。
   - 场景：远程集中部署的微服务、跨网关工具调用。

---

### Q5: MCP 拦截器 (Interceptors) 的作用及其可访问的四大信息。
**标准回答 (16K-22K 满分表达)**：
- **作用**：在工具调用前/后注入横切关注点（如权限校验、敏感数据遮挡、Rate Limit 限流、Audit Log 审计日志）。
- **可访问的四大信息**：
  1. `context`（全局上下文与请求头）
  2. `state`（会话状态）
  3. `store`（全局存储）
  4. `tool_call_id`（唯一调用 ID）

---

### Q6: 简述 MCP 的典型认证与鉴权流程。
**标准回答 (16K-22K 满分表达)**：
- **流程**：Client 启动握手 (`initialize`) $
\rightarrow$ 传递 Auth Bearer Token / API Key $
\rightarrow$ Server 的鉴权拦截器校验权限 $
\rightarrow$ 返回动态可用的 Tools 列表 $
\rightarrow$ 只有具备权限的工具才会被暴露给 LLM。

---

> 🏠 **[返回主页 README](../../README.md)** | 📚 **[专题索引](./README.md)** | ◀️ **上一篇：[04. HITL 人工介入与 Guardrails 安全护栏](./04_HITL人工介入与Guardrails安全护栏.md)** | ▶️ **下一篇：[06. LangGraph 工作流模式与架构设计](./06_LangGraph工作流模式与架构设计.md)** | ⚡ **[30分钟速记](../00_面试冲刺30分钟速记卡片.md)**
