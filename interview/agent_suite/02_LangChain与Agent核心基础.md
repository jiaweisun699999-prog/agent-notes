> 📌 **[AI 大模型与云原生全栈知识库](../../README.md)** / **[Agent & LangGraph 题库套件](./README.md)**
> 🏠 [返回主页 README](../../README.md) | 📚 [专题索引](./README.md) | ⚡ [30分钟速记](../00_面试冲刺30分钟速记卡片.md)

---

# 🎓 02. LangChain 与 Agent 核心基础面试题 (深度重构版)

## 二、LangChain & Agent 核心面试题

### Q1: 什么是 LangChain？它的核心定位与解决的开发痛点是什么？
**标准回答 (16K-22K 满分表达)**：
- **定义**：LangChain 是目前最主流的大语言模型 (LLM) 应用开发框架。
- **解决的核心痛点**：
  1. **模型接口统一**：无缝切换 OpenAI、Claude、DeepSeek、Ollama 等不同 Provider 的 API。
  2. **组件编排抽象 (LCEL)**：通过 LangChain Expression Language (LCEL) 管道符 `|` 提供声明式、流式与异步并行的链式组合能力。
  3. **丰富生态集成**：封装了工具调用 (Tools)、向量数据库 (VectorStores)、记忆管理 (Memory) 以及智能体编排 (Agent) 等上层模块。

---

### Q2: 详细说明 LangChain 的四大核心架构特点。
**标准回答 (16K-22K 满分表达)**：
1. **统一模型接口 (Standardized Interfaces)**：将所有 LLM 抽象为 `BaseChatModel`，统一暴露 `invoke` / `stream` / `batch` API。
2. **LCEL 模块化管道 (Composability)**：所有组件继承自 `Runnable` 基类，天然支持同步/异步、单条/批量、流式与中间事件监听。
3. **原生工具与智能体支持 (Tools & Agents)**：提供 `@tool` 装饰器、Pydantic 模式校验以及基于 ReAct / Tool Calling 的动态智能体循环。
4. **灵活的状态与记忆管理 (Memory Management)**：支持基于对话历史 (BufferWindow)、向量数据库以及状态机 (Checkpointer) 的多层记忆流。

---

### Q3: 简述 LLM 模型的两种初始化方式及其生产适用场景。
**标准回答 (16K-22K 满分表达)**：
1. **常规实例化初始化**：
   - 方式：`llm = ChatOpenAI(model="gpt-4o", temperature=0.7, api_key="...")`
   - 适用场景：单模型调用、本地调试与简单 Prompt 试验。
2. **配置参数批量/工厂初始化 (Init Chat Model)**：
   - 方式：通过 `init_chat_model(model_name, model_provider, temperature=...)` 或读取 `.env` / 配置字典动态工厂加载。
   - 适用场景：生产环境多 Provider 容错降级（如 OpenAI 超时自动切 DeepSeek）、动态按用户等级切换模型档次。

---

### Q4: LangChain 中 MessageType 包含哪些角色类型？各自的作用与生产注意细节是什么？
**标准回答 (16K-22K 满分表达)**：
- **四大核心角色类型**：
  1. **SystemMessage (系统消息)**：定义 Agent 角色人设、全局安全规约、输出格式要求。置于 Prompt 最头部。
  2. **HumanMessage (用户消息)**：代表真实用户的输入文本或多模态消息（图片/文档）。
  3. **AIMessage (助手消息)**：LLM 返回的响应。若触发了工具调用，其内部包含 `tool_calls` 字典列表（含 `id`, `name`, `args`）。
  4. **ToolMessage (工具结果消息)**：保存外部工具/API 运行结果，必须传入对应的 `tool_call_id` 与 `AIMessage` 绑定。
- 💡 **面试加分项**：在 Agent 多轮循环中，若工具报错（如 API 超时），**绝对不能让 Python 进程崩溃**，而是应捕捉 Exception 并包装为 `ToolMessage(content="Error: API Timeout", tool_call_id=...)` 传给模型，触发 LLM 自自我修正与重试。

---

### Q5: LangChain 流式输出的返回对象是什么？如何在后端进行实时 Token 拼接与推送？
**标准回答 (16K-22K 满分表达)**：
- **返回对象**：流式输出逐块返回 **`AIMessageChunk`** 对象。
- **拼接原理**：`AIMessageChunk` 重写了加法运算符 `+`。在后端循环读取时，可以通过 `final_chunk += chunk` 实时累加文本内容 `chunk.content` 以及工具调用片段 `chunk.tool_call_chunks`。
- **生产推送**：在 FastAPI / Server-Sent Events (SSE) 中，直接将 `chunk.content` 实时 `yield` 到前端实现打字机效果。

---

### Q6: 简述调用 LLM 模型的六种常用 API 方式及其场景。
**标准回答 (16K-22K 满分表达)**：
1. **`model.invoke(input)`**：同步单次调用，返回最终完整 `AIMessage`。
2. **`model.ainvoke(input)`**：异步单次调用（用于 AsyncIO 高并发后端）。
3. **`model.stream(input)`**：同步流式生成，返回 `AIMessageChunk` 迭代器。
4. **`model.astream(input)`**：异步流式生成打字机响应。
5. **`model.batch([input1, input2])`**：批量并发调用，底层自动做并发加速。
6. **`model.bind_tools(tools=[...])`**：工具绑定调用，将自定义工具转化为 API 要求的 JSON Schema 并绑定到模型。
---

### Q6.1: 详解 LangChain `invoke()` 方法支持的三种入参数据传递类型及底层转换机制。
**标准回答 (16K-22K 满分表达)**：
LangChain 组件（`Runnable`）的 `invoke(input)` 方法支持以下三种主流数据传递类型：
1. **String (纯字符串类型)**：
   - 用法：`chain.invoke("什么是 Agent？")`
   - 底层机制：最简调用方式。框架内部会自动将其包装转换为单个 `HumanMessage(content="什么是 Agent？")` 传给底层模型。
2. **Dict (字典类型)**：
   - 用法：`chain.invoke({"input": "什么是 Agent？", "chat_history": [...]})`
   - 底层机制：多变量与模组渲染方式。当 Chain/Prompt 中包含多个动态变量（如 Prompt 模板中声明了 `{input}` 和 `{chat_history}`）时，必须以 Dict 形式传参，由 `ChatPromptTemplate` 格式化渲染。
3. **List[BaseMessage] (消息对象列表类型)**：
   - 用法：`chain.invoke([SystemMessage("人设提示"), HumanMessage("用户提问")])`
   - 底层机制：原生多轮对话透传方式。跳过 Prompt 模组解析，直接将完整消息历史列表传递给底层 `ChatModel`，常用于多轮对话历史维护与 Agent 状态恢复。


---

### Q7 & Q8: LLM结构化输出的三种实现方式是什么？如何获取及各自的优缺点？
**标准回答 (16K-22K 满分表达)**：
1. **提示词约束 + OutputParser (Legacy/传统方案)**：
   - 机制：用 `PydanticOutputParser` 生成格式说明注入 Prompt，最后用 `parser.parse()` 提取。
   - 缺点：依靠 Prompt 约束，格式易失控，解析失败需用 `OutputFixingParser` 重试。
2. **LLM Native JSON Mode (`response_format={"type": "json_object"}`)**：
   - 机制：API 保证输出语法合法的 JSON，但仍需手动校验 Schema 字段。
3. **框架封装原生绑定 `model.with_structured_output(schema)` (推荐生产方案)**：
   - 机制：基于 OpenAI Tool Calling / Strict Schema，直接返回 Pydantic 实例。0 解析异常，类型安全。

---

### Q9: 什么是 Tools 工具？它在 LangChain 中如何定义与校验？
**Standard Answer (16K-22K 满分表达)**：
- **定义**：Tools 是 LLM 接入外部世界的桥梁，允许模型执行数据库查询、网络搜索、代码运行或第三方 API 调用。
- **定义与校验方式**：
  ```python
  from pydantic import BaseModel, Field
  from langchain_core.tools import tool
  
  class SearchInput(BaseModel):
      query: str = Field(description="搜索关键词")
  
  @tool("google_search", args_schema=SearchInput, return_direct=False)
  def google_search(query: str) -> str:
      # 用于在 Google 上搜索最新新闻与信息的工具
      return "搜索结果文本..."
  ```
  - **核心参数**：`args_schema` 强制使用 Pydantic 做参数类型校验；`return_direct=True` 则工具运行后直接结束 Agent 并返回给用户。

---

### Q10: 什么是 Agent 智能体？它与传统链式 (Chain) 调用的本质区别是什么？
**标准回答 (16K-22K 满分表达)**：
- **定义**：Agent 是以大语言模型为“大脑”的自主决策系统。
- **本质区别**：
  - **Chain (链式)**：硬编码的固定执行路径（A $
  \rightarrow$ B $
  \rightarrow$ C），无法根据中间结果动态调整步骤。
  - **Agent (智能体)**：依据 **ReAct (Reasoning + Acting)** 循环，由 LLM 动态决定下一步是调用工具、结束任务还是向用户追问，具备自主思考、任务拆解与动态路由能力。

---

### Q11: 简述 LLM、LLM + Tool、Agent 三者的演进与能力区别。
**标准回答 (16K-22K 满分表达)**：

| 维度 | 单纯 LLM | LLM + Tool | Agent 智能体 |
| :--- | :--- | :--- | :--- |
| **交互模式** | 纯文本输入 、纯文本输出 |单次工具调用（硬编码调用）|多轮 Reasoning-Action 动态循环|
| **外部能力** | 仅依赖训练静态知识 | 可被动获取外部 API 数据 | 自主决定何时调用何种工具 |
| **任务规划** | 无规划能力 | 无规划能力 | 具备子任务拆解、状态追踪与自愈能力 |

---

### Q12: 什么是 Agent 的静态模型与动态模型？动态模型如何实现？
**标准回答 (16K-22K 满分表达)**：
- **静态模型**：Agent 在启动时绑定的底层 LLM、工具集合、Prompt 模板全部固定，不可在运行期变更。
- **动态模型**：根据运行时上下文、用户权限或任务复杂度，在任务执行中**动态注册/卸载工具、动态切换底层 LLM 级别（如普通对话用 8B，写代码切 70B）**。
- **实现机制**：通过在 LangGraph 的 Node 函数内部读取 State，根据条件返回重新绑定了不同工具/模型的 Runnable 实例。

---

### Q13: 静态 Prompt 与动态 Prompt 的区别？动态 Prompt 如何在生产中实现？
**标准回答 (16K-22K 满分表达)**：
- **静态 Prompt**：写死的模板文本。
- **动态 Prompt**：在运行时根据**用户角色权限、历史对话摘要、当前时间、状态机内部变量**实时生成与拼接 Prompt。
- **生产实现**：使用 LangChain 的 `ChatPromptTemplate` 配合 `RunnablePassthrough` 或在 Node 中编写 Prompt 工厂函数做动态 Jinja2 / Python f-string 渲染。

---

### Q14: Agent 有哪些调用方式？其流式输出包含哪七种模式？
**标准回答 (16K-22K 满分表达)**：
- **调用方式**：`invoke` (同步)、`ainvoke` (异步)、`stream` (流式)。
- **七种流式模式 (LangGraph / Agent 暴露)**：
  1. `values`：每个 Superstep 后输出全量 State。
  2. `updates`：仅输出当前节点产生的增量 State 修改。
  3. `messages`：实时输出 LLM 生成的 Token 增量及元数据。
  4. `tasks`：输出后台任务调度与节点启动事件。
  5. `debug`：输出底层图引擎执行详细调试日志。
  6. `checkpoints`：输出持久化快照保存事件。
  7. `custom`：输出节点内自定义 `stream_writer` 抛出的自定义日志。

---

### Q15 & Q16 & Q18: Agent 结构化输出的四种方式是什么？为什么推荐 `toolStrategy`？其三大核心参数是什么？
**标准回答 (16K-22K 满分表达)**：
- **四种方式**：`providerStrategy` (模型自带)、`toolStrategy` (工具调用仿真)、`type` (原生 Schema 强制)、`none` (无约束)。
- **推荐 `toolStrategy` 的原因**：利用底层大模型极其成熟的 Tool Calling / Function Calling 微调能力，将结构化输出伪装成一次“工具调用”，稳定性最高，输出符合 100% 语法规范。
- **三大核心参数**：
  1. `tool_choice`：强制模型必须调用指定结构化工具（如 `tool_choice="ResponseSchema"`）。
  2. `schema`：绑定的 Pydantic 类或 JSON Schema 校验字典。
  3. `error_handler` / `max_retries`：当输出字段校验失败时的自动捕获与二次重试策略。

---

### Q17: Agent 结构化输出 Schema 的四种定义方式有哪些？
**标准回答 (16K-22K 满分表达)**：
1. **`pydantic.BaseModel` (最推荐)**：支持类型自动转换、`Field(description=...)` 提示词自动提取及强校验。
2. **`dataclass` (Python 原生)**：轻量级，但缺乏强类型自动转换与详细描述注入。
3. **`jsonschema` (字典形式)**：跨语言标准，适合从 API 动态加载 Schema。
4. **`TypedDict`**：轻量级键值字典定义。

---

> 🏠 **[返回主页 README](../../README.md)** | 📚 **[专题索引](./README.md)** | ◀️ **上一篇：[01. Transformer 与深度学习基础](./01_Transformer与深度学习基础.md)** | ▶️ **下一篇：[03. Agent 长短期记忆与状态管理](./03_Agent长短期记忆与状态管理.md)** | ⚡ **[30分钟速记](../00_面试冲刺30分钟速记卡片.md)**
