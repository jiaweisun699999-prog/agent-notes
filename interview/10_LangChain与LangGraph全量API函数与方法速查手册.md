> 📌 **[AI 大模型与云原生全栈知识库](../README.md)** / **面试高频题专区**
> 🏠 [返回主页 README](../README.md) \| ⚡ [面试 30 分钟速记](./00_面试冲刺30分钟速记卡片.md) \| 💻 [白板手写代码](./08_大厂手写代码与白板编程题.md)

---

# 🎓 LangChain & LangGraph 全量 API 函数与核心方法实战速查手册

> 本文档专为解决“面试被问到具体 API 函数/方法使用细节”设计，全量汇总了 LangChain、LangGraph、RAG 以及 Tool 开发中最核心的函数、装饰器、入参配置与方法签名。

---

## 一、 LangChain 模型与工具绑定核心 API

### 1. 模型实例化与调用方法 (`ChatOpenAI` / `ChatModel`)
- **实例化入参**：
  - `ChatOpenAI(model="gpt-4o", temperature=0.7, max_tokens=2048, streaming=True, api_key="...", base_url="...")`
- **核心方法**：
  - `model.invoke(input)`：同步单次调用，输入 `str` 或 `List[BaseMessage]`，返回 `AIMessage`。
  - `model.ainvoke(input)`：异步单次调用（协程 `await`）。
  - `model.stream(input)`：同步流式生成迭代器，逐 Token 返回 `AIMessageChunk`。
  - `model.astream(input)`：异步流式生成。
  - `model.batch([input1, input2])`：批量并发调用，返回结果列表。
  - **`model.bind_tools(tools=[...], tool_choice="auto|any|tool_name")`**：
    - 作用：将工具列表绑定至模型，生成包含 Function Calling 定义的 Model 实例。
  - **`model.with_structured_output(schema, method="function_calling", include_raw=False)`**：
    - 作用：强制模型输出指定的 Pydantic 类或 JSON Schema 对象。

---

### 2. 工具定义与装饰器 API (`@tool` / `StructuredTool`)
- **`@tool` 装饰器用法**：
  ```python
  from pydantic import BaseModel, Field
  from langchain_core.tools import tool

  class AddInput(BaseModel):
      a: int = Field(description="第一个加数")
      b: int = Field(description="第二个加数")

  @tool("custom_add_tool", args_schema=AddInput, return_direct=False)
  def add(a: int, b: int) -> int:
      """用于计算两个整数之和的工具"""
      return a + b
  ```
  - **参数说明**：
    - `args_schema`：指定入参 Pydantic 类，用于严格校验 LLM 生成的参数。
    - `return_direct`：若设为 `True`，工具执行完后直接将结果返回给用户，跳过 Agent 的后续 Thought 循环。

- **动态创建工具 API**：
  - `StructuredTool.from_function(func=my_func, name="my_tool", description="...", args_schema=MyInput)`

---

### 3. Prompt 与 OutputParser 核心 API
- **Prompt 模板 API**：
  - `ChatPromptTemplate.from_messages([("system", "系统提示词"), ("human", "{user_input}")])`
  - `ChatPromptTemplate.from_template("模板字符串: {variable}")`
  - `prompt.format_messages(**kwargs)`：返回格式化后的 `List[BaseMessage]`。
- **输出解析器 API**：
  - `PydanticOutputParser(pydantic_object=MyModel)`
    - `parser.get_format_instructions()`：获取注入 Prompt 的 JSON 格式说明字符串。
    - `parser.parse(text)`：解析纯文本返回 Pydantic 实例。
  - `OutputFixingParser.from_llm(parser=parser, llm=llm)`：
    - 作用：当 `parser.parse()` 报错时，自动调用 `llm` 进行二次纠错解析。
  - `StrOutputParser()`：将 `AIMessage` 提取为纯文本字符串。
  - `JsonOutputParser()`：解析文本返回原生 Python `dict`。

---

## 二、 LangChain LCEL 执行引擎 API

- **管道符 `|` 与 Runnable 基础组件**：
  - `chain = prompt | model | parser`（底层对应 `RunnableSequence`）。
- **高阶 Runnable 方法**：
  - **`RunnableParallel(a=chain_1, b=chain_2)`**：并行并发执行两个子链，输出 `{"a": res_1, "b": res_2}`。
  - **`RunnablePassthrough()`**：原样传递输入数据。
  - **`RunnableLambda(my_python_func)`**：将任意 Python 函数包装为 LCEL 组件。
- **高阶事件流 API**：
  - **`chain.astream_events(input, version="v2")`**：
    - 异步监听整条链上所有节点发出的事件。
    - 关键事件类型：
      - `"on_chat_model_stream"`：LLM 输出的增量 Token。
      - `"on_tool_start"` / `"on_tool_end"`：工具调用的开始与结束事件。
      - `"on_chain_start"` / `"on_chain_end"`：子链事件。

---

## 三、 LangGraph 图网络与状态管理核心 API

### 1. 图构建 API (`StateGraph`)
```python
from langgraph.graph import StateGraph, START, END

# 1. 初始化图结构
builder = StateGraph(StateSchema)

# 2. 添加节点
builder.add_node("node_name", node_function)

# 3. 添加静态无条件边
builder.add_edge("source_node", "target_node")

# 4. 添加条件动态路由边
builder.add_conditional_edges(
    source="source_node",
    path=routing_function,  # 接收 State，返回目标节点名称字符串
    path_map={"route_a": "node_a", "route_b": "node_b"} # 选填映射表
)

# 5. 编译生成可执行图对象
app = builder.compile(
    checkpointer=memory_saver,      # 挂载状态快照持久化
    store=in_memory_store,          # 挂载跨会话长期存储
    interrupt_before=["node_x"],    # 节点执行前拦截
    interrupt_after=["node_y"]      # 节点执行后拦截
)
```

---

### 2. 节点内部与人机交互 (HITL) API
- **`interrupt(value)`**：
  - 在 Node 内部调用，挂起当前图的执行，并将 `value`（如审批提示字典）抛出给调用方。
  - 示例：`user_decision = interrupt({"question": "是否批准调用删除 API？"})`
- **`Command(resume=..., update=..., goto=...)`**：
  - **恢复执行**：`app.invoke(Command(resume="Approved"), config)`，解除 `interrupt()` 挂起并返回值给节点。
  - **更新状态**：`Command(update={"messages": [...]})`
  - **跳转节点**：`Command(goto="other_node")`

---

### 3. 图运行时状态操作 API
- **`app.invoke(input, config)`**：同步执行图，返回最终整图 State 字典。
- **`app.stream(input, config, stream_mode="values|updates|messages|custom")`**：
  - `stream_mode="values"`：返回每个 Superstep 的全量 State。
  - `stream_mode="updates"`：仅返回当前节点输出的增量更新。
  - `stream_mode="messages"`：返回实时 LLM 消息 Token 及 node 元数据。
- **`app.get_state(config)`**：
  - 返回 `StateSnapshot` 对象，包含 `.values` (当前状态)、`.next` (下一步准备执行的节点列表)、`.config`。
- **`app.update_state(config, values, as_node="node_name")`**：
  - 动态重写/修改持久化存储里的 State 字典，可指定模拟某个节点发出的更新。
- **`app.get_state_history(config)`**：
  - 遍历返回当前 `thread_id` 下的所有历史 Checkpoint 快照迭代器（用于时间旅行 Time-travel）。

---

### 4. 持久化存储 API (`Checkpointer` / `Store`)
- **Checkpointer 选项**：
  - `MemorySaver()`：内存级临时快照（开发调试用）。
  - `PostgresSaver.from_conn_string("postgresql://...")`：生产级 PostgreSQL 持久化快照。
  - `AsyncSqliteSaver.from_conn_string("sqlite.db")`：SQLite 异步快照。
- **Store 选项 (长期跨会话记忆)**：
  - `InMemoryStore()` / `AsyncPostgresStore()`
  - `store.put(namespace=("users", user_id), key="preferences", value={"theme": "dark"})`
  - `store.get(namespace, key)`
  - `store.search(namespace, query="语义检索文本")`

---

## 四、 RAG & 向量数据库核心 API

### 1. 文本切块 API (`RecursiveCharacterTextSplitter`)
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,           # 每个 Chunk 的目标字符数
    chunk_overlap=50,         # 相邻 Chunk 间的重叠字符数
    separators=["\n\n", "\n", "。", "！", "？", " ", ""] # 降级切分分隔符优先级
)
chunks = splitter.split_documents(docs)
```

---

### 2. 向量存储与检索 API (`VectorStore`)
- **创建与写入**：
  - `vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)`
  - `vectorstore.add_documents(new_chunks)`
- **检索调用**：
  - `docs_and_scores = vectorstore.similarity_search_with_score(query="...", k=5)`
  - **`retriever = vectorstore.as_retriever(search_type="similarity|mmr", search_kwargs={"k": 5, "filter": {"tenant_id": "123"}})`**
    - `search_type="mmr"`：最大边际相关性（Maximal Marginal Relevance），兼顾相关性与结果多样性，防止返回重复 Chunk。

---

---
> 🏠 **[返回主页 README](../README.md)** \| ◀️ **上一篇：[09. 面试反问与薪资谈判](./09_%E9%9D%A2%E8%AF%95%E5%8F%8D%E9%97%AE%E4%B8%8E%E9%AB%98%E6%83%85%E5%95%86%E6%B2%9F%E9%80%9A%E6%8A%80%E5%B7%A7.md)** \| ⚡ **[面试 30 分钟速记](./00_面试冲刺30分钟速记卡片.md)**
