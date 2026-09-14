# 🤖 AI Agent、LangChain、LangGraph 模块化精简面试题库套件

> 📌 **[AI 大模型与云原生全栈知识库](../../README.md)** / **Agent & LangGraph 模块化题库套件**
> 🏠 [返回主页 README](../../README.md) | ⚡ [面试 30 分钟速记](../00_面试冲刺30分钟速记卡片.md) | 💻 [白板手写代码](../08_大厂手写代码与白板编程题.md)

---

> 本套件由用户整理的《AI Agent、LangChain、LangGraph 全套面试题库》重构拆分而成。将原本融为一体的长文档按技术模块细分为 **11 篇高度聚焦的专题文档**，方便模块化专项复习与查阅。

---

## 🗺️ 拆分模块导航 (Table of Contents)

| 序号 | 专题名称 | 核心知识点与包含问题数 | 快速跳转 |
| :---: | :--- | :--- | :---: |
| 01 | **Transformer 与深度学习基础面试题** | 注意力机制、自注意力 QKV 推导、多头自注意力、位置编码、Transformer 流程、RNN、CNN 卷积池化、正向/反向传播 (共 9 题) | [📄 阅读文档](./01_Transformer与深度学习基础.md) |
| 02 | **LangChain 与 Agent 核心基础面试题** | LangChain 框架特点、LLM 2 种初始化、MessageType 角色、6 种调用与 `invoke()` 3 种传参、Tools 与 Agent 区别、静态/动态模型与提示词、toolStrategy 结构化输出 (共 19 题) | [📄 阅读文档](./02_LangChain与Agent核心基础.md) |
| 03 | **Agent 长短期记忆与状态管理面试题** | 短期记忆存储、自定义 State、State vs Context、超出窗口的 4 种截断策略、长期记忆与存储介质 (共 9 题) | [📄 阅读文档](./03_Agent长短期记忆与状态管理.md) |
| 04 | **HITL 人工介入与 Guardrails 安全护栏面试题** | HITL 中间件+Checkpointer 机制、4 种介入策略与流程、Guardrails 两大类、PII 个人敏感信息 4 种处理方式 (共 8 题) | [📄 阅读文档](./04_HITL人工介入与Guardrails安全护栏.md) |
| 05 | **Runtime 运行时与 MCP 模型上下文协议** | Runtime 核心定义与 3 种上下文、MCP 概念与 LangChain Tools 区别、3 大角色与 2 种传输模式、MCP 拦截器与认证流程 (共 14 题) | [📄 阅读文档](./05_Runtime运行时与MCP协议.md) |
| 06 | **LangGraph 工作流模式与架构设计面试题** | LangGraph 基础能力、五步设计法、5 种工作流模式、ToolRunTime vs ToolNode、Checkpointer 3 核心概念与持久化模式 (共 13 题) | [📄 阅读文档](./06_LangGraph工作流模式与架构设计.md) |
| 07 | **LangGraph 容错机制与全量流式输出面试题** | 3 种容错策略（重试/超时/错误处理）、go_to 作用、7 种流式输出模式、v1/v2/v3 差异、LLM 过滤与事件流/运行流 (共 12 题) | [📄 阅读文档](./07_LangGraph容错机制与全量流式输出.md) |
| 08 | **LangGraph 高级 HITL 与 Interrupt 核心规则** | interrupt 正常工作 3 必要条件与内部 5 步骤、中断恢复要点、v3 惰性流、交互式 HITL 5 种模式与 5 条黄金规则 (共 6 题) | [📄 阅读文档](./08_LangGraph高级HITL与Interrupt核心规则.md) |
| 09 | **LangGraph 子图与时间旅行高级实战** | 子图定义与通信模式（挂载 vs 显式 invoke）、Schema 映射与坑点、3 种持久化模式、Sub-Agent 模式、Time-Travel、Replay/Fork、中断中 Fork (共 13 题) | [📄 阅读文档](./09_LangGraph子图与时间旅行高级实战.md) |
| 10 | **三大企业级项目实战面试题精通指南** | 携程 AI 助手 (自定义 Loop 演进 LangGraph、多 Agent 隔离、Saga 事务)、RAG 知识库 (merge_title_content、Milvus BM25+Dense、RRF、CRAG/Adaptive、MCP)、多模态 RAG (dots_ocr、Vision-LLM 描述、RateLimiter 防 429、RAGAS 评估)、项目上下文工程 (Tool返回值剪枝、Handle模式、Prefix Caching)、多 Agent 架构选型 (4大拓扑对比)、格式自愈与三层高可用降级 (共 15 题) | [📄 阅读文档](./10_三大企业级项目实战面试题精通指南.md) |
| 11 | **DeepAgents & Harness Engineering 核心架构面试题** | DeepAgents 与 LangChain/LangGraph 三层定位、Harness Engineering 核心设计理念、虚拟文件系统状态后端、多 Sub-Agent 隔离、沙箱安全执行、渐进式披露与上下文压缩、STAR 答题话术与追问 (共 16 题) | [📄 阅读文档](./11_DeepAgents%20&%20Harness%20Engineering%20核心架构面试题.md) |

---

> 🏠 **[返回主页 README](../../README.md)** | ⚡ **[面试 30 分钟速记](../00_面试冲刺30分钟速记卡片.md)** | 💻 **[白板手写代码](../08_大厂手写代码与白板编程题.md)**
