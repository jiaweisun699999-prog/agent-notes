> 📌 **[AI 大模型与云原生全栈知识库](../../README.md)** / **[Agent & LangGraph 题库套件](./README.md)**
> 🏠 [返回主页 README](../../README.md) | 📚 [专题索引](./README.md) | ⚡ [30分钟速记](../00_面试冲刺30分钟速记卡片.md)

---

# 🎓 11. DeepAgents & Harness Engineering 核心架构面试题

> 本文档深入剖析 LangChain 生态第三代智能体框架 DeepAgents 的核心设计理念——**Harness Engineering**，涵盖虚拟文件系统后端、多 Sub-Agent 协作、沙箱安全执行、上下文工程（渐进式披露、上下文压缩、长期记忆）等高频面试知识点，配备完整的 STAR 法则回答模板与追问应对。

---

## 一、DeepAgents 框架概述与 Harness Engineering

### Q1：什么是 DeepAgents？它与 LangChain、LangGraph 的关系是什么？

**标准回答（16K-22K 满分表达）**：

- **定位**：DeepAgents 是 LangChain 团队在 LangChain 和 LangGraph 之上推出的**第三个独立开源项目**，是一个面向"复杂任务"的**开箱即用深度智能体框架**，专门为处理复杂、多步骤、长时间运行任务的"深度"智能体而设计。

- **三层关系**：

  | 层次 | 框架 | 定位 |
  |------|------|------|
  | 底层 | LangChain | 工具链、链式调用、模型接入 |
  | 中层 | LangGraph | 有状态图编排、持久化、流程控制 |
  | 上层 | DeepAgents | 开箱即用的深度 Agent 框架，内置 Harness 基础设施 |

- **解决的核心问题**：早期 Agent 框架（如 ReAct）证明了 LLM 可以使用工具，但工程上存在三大痛点：上下文窗口溢出、执行不可靠、长任务难管理。DeepAgents 通过 Harness Engineering 在**模型外**构建系统化基础设施解决这些问题。

- **一句话定位**：如果说 LangGraph 是"图编排引擎"，那么 DeepAgents 就是"在图引擎之上为复杂任务配套了完整的生产级基础设施"。

> 💡 **面试亮点**：提到"第三个独立开源项目"和"三层递进架构"会让面试官印象深刻，体现你对整个 LangChain 生态有系统性理解。

---

### Q2：DeepAgents 证明了哪四个 Agent 必备能力？工程意义是什么？

**标准回答**：

DeepAgents 在实践中验证了复杂 Agent 必须具备的四个关键能力：

1. **规划能力（Planning）**：把复杂任务拆解成有序子步骤。工程意义：避免单轮上下文过载，支持长任务阶段性推进。

2. **文件系统（File System）**：Agent 需要持久化"草稿本"存储中间结果，而不是把所有信息塞进对话窗口。工程意义：解决上下文窗口爆炸的根本路径。

3. **子 Agent（Sub-Agents）**：主 Agent 无法精通所有领域，需要把专业任务委托给专业子 Agent。工程意义：实现上下文隔离、职责分离，提高可靠性和专业性。

4. **技能包（Skills）**：按需加载特定领域的能力指南，而不是在系统提示中堆砌所有知识。工程意义：实现渐进式信息披露，降低无效 token 消耗。

> 💡 **追问应对**："这四点的内在逻辑？" → 四点都指向同一核心矛盾：**LLM 上下文窗口是有限的，但复杂任务是无限的**。规划=分治；文件系统=外置记忆；子 Agent=分布式上下文；Skills=按需加载知识。

---

### Q3：什么是 Harness Engineering？它与 Prompt Engineering 的本质区别是什么？

**标准回答**：

- **Prompt Engineering**：关注如何设计更好的输入让模型输出更好的结果，边界在模型内部。

- **Harness Engineering（线束工程）**：在模型**外部**构建一整套系统化基础设施，消除模型不稳定性，让模型能更可靠地长时间处理复杂任务。

- **核心公式**：
  ```
  Agent = Model + Harness
  Model   → 负责"思考"与"决策"
  Harness → 负责把"思考"变成"稳定执行"
  ```

- **Harness 的六个职责**：
  1. **访问控制**：决定 Agent 能访问什么资源（文件系统后端、沙箱边界）
  2. **工具管理**：决定 Agent 能调用什么工具（技能包、子 Agent）
  3. **流程控制**：决定 Agent 能走到哪一步（规划任务列表、节点中断）
  4. **终止条件**：决定什么时候停下（工具调用次数限制、任务完成判断）
  5. **错误回退**：出了错怎么回退（Checkpoint 恢复、异常处理中间件）
  6. **结果校验**：结果如何验证（输出格式检查、人工介入审批）

> 💡 **一句话总结**：Prompt Engineering 优化模型本身的思维质量；Harness Engineering 在模型外部建造可靠的脚手架，让即使不完美的模型也能稳定完成复杂任务。

---

### Q4：DeepAgents 提供了哪些 Harness Engineering 的具体实现？

**标准回答**：

| 模块 | 作用 | 解决的问题 |
|------|------|------------|
| **规划能力** | 内置 Todo List 机制，Agent 先制定分步计划再执行 | 复杂任务无法一次完成 |
| **虚拟文件系统** | 提供可插拔的文件后端，支持读写、搜索、编辑 | 中间结果无处存放，上下文爆炸 |
| **任务委托/子智能体** | task() 工具 + SubAgentMiddleware，主 Agent 将任务分发给专业子 Agent | 单 Agent 上下文臃肿、缺乏专业性 |
| **上下文管理** | 自动压缩（卸载+摘要）、记忆文件、技能包渐进式加载 | Token 消耗不可控，上下文腐烂 |
| **代码执行和安全沙箱** | 集成 E2B 等沙箱提供商，在隔离容器中执行 shell 命令 | Agent 执行代码的安全风险 |
| **人工介入（HITL）** | 基于 LangGraph Interrupt，在关键步骤暂停等待人工确认 | 高风险操作无人审批 |
| **技能包加载和管理** | Skills 按需加载机制，只在命中时才完整读取技能文档 | 系统提示过长导致注意力稀释 |

---

### Q5：DeepAgents 框架的五大核心设计原理是什么？

**标准回答**：

1. **配置优于编码**：通过配置字典（name、description、system_prompt、tools）定义子 Agent，降低使用门槛。

2. **中间件架构**：采用类似 Web 框架的中间件模式，在请求/响应链上插拔各种功能（SubAgentMiddleware、ToolCallLimitMiddleware、@dynamic_prompt），实现横切关注点的解耦。

3. **后端协议抽象**：文件系统操作通过 BackendProtocol 接口统一抽象，支持状态存储、本地磁盘、LangGraph Store、云存储等任意后端无缝切换。

4. **上下文工程自动化**：自动管理系统提示拼接顺序、记忆文件注入、技能按需加载、上下文压缩，开发者无需手动管理 token 预算。

5. **从智能到系统**：核心哲学——不依赖模型"足够聪明"来解决可靠性问题，而是通过工程手段（隔离、校验、回退、限制）构建健壮的 Agent 系统。

---

## 二、文件系统后端（File System Backend）

### Q6：DeepAgents 的文件系统后端是什么？为什么采用"可插拔后端"的设计？

**标准回答**：

- **是什么**：DeepAgents 为 Agent 提供了虚拟文件系统抽象。Agent 不直接操作存储，而是通过统一工具集（read_file、write_file、edit_file、ls、grep 等）与文件交互。这些工具的底层实际存储行为，由一个**可插拔的后端（Backend）** 来决定。

- **可插拔设计的意义**：
  - **开发阶段**：使用 StateBackend（临时状态），快速验证逻辑，无副作用
  - **生产阶段**：切换到 LocalDiskBackend 或 StoreBackend，持久化存储结果
  - **高安全场景**：接入沙箱后端，在完全隔离的容器内执行
  - **多租户场景**：使用 CompositeBackend 按路径前缀路由到不同存储
  - **切换成本为零**：Agent 代码完全不感知后端变化

- **默认后端**：StateBackend，将文件存储在 LangGraph 的 Agent 运行时 State 中，仅在一次执行线程内有效，线程结束数据消失。主子 Agent 之间共享这个状态后端。

---

### Q7：请详细介绍 DeepAgents 的七种文件系统后端及各自的适用场景。

**标准回答**：

| 后端 | 存储位置 | 生命周期 | 典型场景 |
|------|----------|----------|----------|
| **StateBackend（临时状态后端）** | LangGraph Agent State（内存） | 单次执行线程 | 临时草稿纸、中间结果暂存；主子 Agent 共享临时数据 |
| **LocalDiskBackend（本地磁盘后端）** | 本地机器文件系统 | 持久化 | 开发调试，须开启 virtual_mode=True 防目录逃逸 |
| **LocalShellBackend（本地 Shell 后端）** | 本地磁盘 + Shell 执行能力 | 持久化 | 磁盘后端之上额外赋予 execute 工具；**仅在可信受控内网使用，严禁生产环境** |
| **StoreBackend（LangGraph Store 后端）** | LangGraph BaseStore（数据库） | 跨会话持久化 | 长期记忆存储、跨线程/跨用户的知识库 |
| **CompositeBackend（复合/路由后端）** | 多个底层后端 | 取决于子后端 | 按文件路径前缀路由到不同存储策略 |
| **沙箱后端（Sandbox Backend）** | 隔离容器（如 E2B） | 沙箱生命周期 | 编程 Agent、数据分析 Agent 等需要安全执行代码的场景 |
| **自定义后端（Custom Backend）** | 任意（云存储、数据库等） | 自定义 | 将 S3、数据库、企业内部存储系统接入 Agent 文件系统 |

> 💡 **追问应对**："LocalShellBackend 和沙箱后端有什么区别？" → LocalShellBackend 直接在宿主机执行命令，危险但简单，适合受信任的内网环境；沙箱后端在隔离容器内执行，安全且隔离，适合生产环境。两者都提供 execute 工具，但安全边界截然不同。

---

### Q8：如果要实现自定义后端（Custom Backend），需要实现哪些核心方法？

**标准回答**：

自定义后端需要实现 BackendProtocol 接口，六个核心方法如下：

| 方法 | 作用 |
|------|------|
| `ls_info(path)` | 列出指定路径下的文件和目录信息（名称、大小、类型等） |
| `read(path)` | 读取指定文件的完整内容，返回字符串 |
| `write(path, content)` | 创建新文件或覆盖写入文件内容 |
| `edit(path, old_str, new_str)` | 精准替换文件中指定文本块（类似 IDE 代码重构），而非全量覆盖 |
| `grep_raw(pattern, path, glob)` | 在文件中搜索正则表达式 pattern，可限制路径或用 glob 过滤文件 |
| `glob_info(pattern, path)` | 使用 glob 模式在指定路径下搜索匹配的文件列表 |

**工程价值**：通过实现以上六个方法，可以将任意存储系统（AWS S3、MongoDB GridFS、企业 NAS、Redis 等）无缝接入 DeepAgents 工具体系，Agent 代码零修改。

---

## 三、Sub-Agent 子智能体协作

### Q9：为什么复杂 Agent 系统需要多 Agent 协作架构？单 Agent 的瓶颈在哪里？

**标准回答**：

**单 Agent 的三大瓶颈**：

1. **上下文臃肿**：复杂任务需要同时维护大量背景信息、工具调用历史、中间结果，单 Agent 的上下文窗口很快被填满。
2. **缺乏专业性**：一个泛化的 Agent 很难在所有领域都表现优秀，"什么都会"往往意味着"什么都不精"。
3. **可靠性差**：单点故障影响全局，难以对特定子任务实施独立的限速、重试、安全策略。

**多 Agent 的解决方案**：
- **主 Agent**：负责全局协调、规划任务拆解、结果整合，自身上下文保持精简
- **子 Agent**：在**完全隔离的上下文**中执行特定专业子任务，只将精炼的结果摘要返回给主 Agent

**核心价值——上下文隔离**：子 Agent 完成任务后，大量的中间过程数据留在子 Agent 的上下文里消失，主 Agent 只接收到一个简洁的结果摘要。这是多 Agent 架构最关键的工程收益。

> 💡 **STAR 法则表达**："在我们的 RAG 项目中，当遇到需要同时处理文档解析、向量检索和答案生成的复杂任务时，单 Agent 的上下文很快超过 128K 限制。我们引入了 DeepAgents 的子 Agent 架构，将三个子任务分发给专门的 Agent，主 Agent 只接收摘要结果，上下文使用量降低了 70%。"

---

### Q10：DeepAgents 中 task() 工具的工作机制是什么？底层 SubAgentMiddleware 如何运作？

**标准回答**：

**task() 工具**是主 Agent 发起任务委托的入口：
- **参数**：name（目标子 Agent 名称）+ task（任务描述提示词）
- **行为**：主 Agent 调用后立即暂停，等待子 Agent 执行完毕，再继续执行

**SubAgentMiddleware 底层工作流程**：

```
主 Agent 调用 task("搜索Agent", "搜索最新的 LangGraph 文档")
    ↓
SubAgentMiddleware 拦截 task() 工具调用
    ↓
根据 name 在已注册的子 Agent 列表中查找配置
    ↓
在全新的、完全隔离的上下文中实例化子 Agent（独立 system_prompt、独立工具集）
    ↓
子 Agent 执行任务（可能经过多轮工具调用）
    ↓
执行结束后，将所有 AIMessage 打包压缩成一个 ToolMessage
    ↓
ToolMessage 作为 task() 工具的返回结果回传给主 Agent
    ↓
主 Agent 恢复执行，以摘要结果为输入继续后续步骤
```

> 💡 **面试补充**："官方文档提到，当前版本主 Agent 等待子 Agent 时是同步阻塞的，下一个版本将支持异步并发调度（主 Agent 无需暂停等待）。提到框架路线图的了解会给面试官留下深刻印象。"

---

### Q11：配置子 Agent 有哪两种方式？各自的适用场景是什么？

**标准回答**：

**方式一：字典配置（最常用）**

```python
sub_agents = [
    {
        "name": "web_search_agent",
        "description": "当需要搜索互联网上的最新信息时使用此 Agent",
        "system_prompt": "你是一个专业的网络搜索 Agent...",  # 不继承主 Agent，必须独立定义
        "tools": [search_tool, fetch_tool],  # 不继承主 Agent，按需配置最小工具集
        "model": ChatOpenAI(model="gpt-4o"),  # 可选，不填则继承主 Agent 的模型
    }
]
```

**方式二：预编译 LangGraph 图**

```python
compiled_graph = builder.compile(checkpointer=memory)
sub_agents = [
    {
        "name": "complex_workflow_agent",
        "description": "当需要执行复杂多步骤工作流时使用",
        "graph": compiled_graph,
    }
]
```

**适用场景对比**：
- **字典配置**：适合大多数场景，简单快速，配置即可用
- **预编译图**：适合需要精细控制子 Agent 内部工作流（内部包含条件分支、循环、自定义 Checkpointer）的高级场景

---

### Q12：开发子 Agent 有哪些关键最佳实践？

**标准回答**：

**精细化配置的三个维度**：

1. **专用模型选择**：根据任务类型选择最合适的模型
   - 图像分析子 Agent → GPT-4 Vision 或 Claude 3 Opus
   - 代码生成子 Agent → Claude 3.5 Sonnet 或 DeepSeek-Coder
   - 快速摘要子 Agent → GPT-3.5-Turbo（降本增效）

2. **专用中间件**：给高风险子 Agent 配置安全护栏
   - 如给代码执行子 Agent 配置 `ToolCallLimitMiddleware(max_calls=10)` 防止无限循环

3. **技能包显式配置**：主 Agent 的 Skills 默认**不会**自动传递给子 Agent，需要显式配置

**四大开发最佳实践**：

| 实践 | 要点 | 原因 |
|------|------|------|
| description 描述精确 | 明确说明"在什么情况下"使用这个子 Agent | 主 Agent 靠 description 选择子 Agent，模糊会导致错误路由 |
| system_prompt 详细完整 | 说明如何使用工具、如何格式化输出、强调返回摘要而非原始数据 | 子 Agent 不继承主 Agent 的任何上下文 |
| 工具集最小化 | 只给子 Agent 完成任务必要的工具 | 减少干扰，提高安全性，降低误调用概率 |
| 返回结果简洁 | 在给子 Agent 的 task 指令中明确要求"提炼、总结，控制输出长度" | 这是实现上下文隔离收益的关键 |

---

## 四、沙箱安全执行

### Q13：什么是 DeepAgents 的沙箱？它解决了什么核心问题？

**标准回答**：

- **定义**：沙箱是一种**特殊的文件系统后端**，在提供常规文件读写能力的基础上，额外给 Agent 提供了 execute 工具——允许 Agent 在**完全隔离的容器环境**中执行任意 shell 命令。

- **通俗比喻**：如果把 Agent 比作一个程序员，沙箱就是给这个程序员提供了一台**虚拟机**——他可以在里面随意安装软件、运行代码、删除文件，但无论他怎么操作，宿主机（真实服务器）的文件、账号、网络都不受影响。

- **解决的核心问题**：
  1. **代码执行安全**：Agent 生成的代码可能包含危险命令，沙箱将危害限制在容器内
  2. **环境污染**：Agent 安装的依赖包、创建的临时文件不会污染宿主机环境
  3. **多租户隔离**：不同用户的 Agent 任务在独立容器中运行，互不干扰

- **典型使用场景**：编程 Agent（代码生成+执行+调试循环）、数据分析 Agent（执行 Python/SQL 分析脚本）

---

### Q14：沙箱的五大核心优势是什么？如何在生产中接入沙箱？

**标准回答**：

**五大核心优势**：

| 优势 | 说明 |
|------|------|
| **文件系统隔离** | 容器内的文件操作完全不影响宿主机，Agent 可以随意读写、删除 |
| **防止上下文爆炸** | shell 命令可能产生大量输出（如 npm install 的日志），沙箱可截断/过滤，防止 token 消耗失控 |
| **环境隔离** | 每个 Agent 任务在独立的 Python/Node 环境中运行，避免依赖版本冲突 |
| **进程隔离** | Agent 启动的进程在容器内运行，容器销毁时自动清理，不影响宿主机进程列表 |
| **网络控制** | 可以配置容器的网络策略，限制 Agent 只能访问特定域名或完全断网 |

**生产接入流程（以 E2B 为例）**：

```python
# Step 1: 配置沙箱（API Key + Docker 容器模板 ID）
sandbox = Sandbox(template_id="your-template-id", api_key="e2b_xxx")

# Step 2: 将沙箱实例包装为 DeepAgents 可用的 Backend
backend = E2BBackend(sandbox=sandbox)

# Step 3: 将 backend 传入 deep_agent 创建函数
agent = create_deep_agent(model=llm, backend=backend, ...)
```

**文件进出沙箱的两种方式**：

1. **Agent 工具操作**：通过 Agent 的 execute 工具执行 shell 命令，或调用 read_file/write_file，适合 Agent 在任务执行中自主管理文件

2. **宿主机文件传输 API**：在应用程序代码层面直接调用沙箱提供商 SDK API
   - **预置依赖**：任务前上传必要的数据文件到沙箱
   - **检索产物**：任务后从沙箱下载 Agent 生成的报告、图表等
   - **初始化环境**：上传自定义脚本到沙箱供 Agent 调用

---

## 五、上下文工程（Context Engineering）

### Q15：DeepAgents 是如何自动管理输入上下文的？系统提示的拼接顺序是什么？

**标准回答**：

DeepAgents 在每次调用 Agent 时，会**自动按固定顺序**将各组件的上下文拼接成完整的系统提示：

```
① 自定义系统提示词（system_prompt）   ← 用户定义的业务角色与规则
② 基础 Agent 提示                     ← 框架内置的通用 Agent 行为规范
③ 待办事项提示（Planning）             ← 当前任务计划/Todo List
④ 记忆提示（Memory）                  ← AGENTS.md 等持久化记忆文件（如已配置）
⑤ 技能提示（Skills）                  ← 命中的 Skill 文档全文（按需加载）
⑥ 虚拟文件系统提示                    ← 当前文件系统的状态描述
⑦ 子智能体提示                        ← 可用子 Agent 的 name + description 列表
⑧ 用户自定义中间件提示                ← @dynamic_prompt 等中间件注入的动态内容
⑨ 人机交互提示（HITL）                ← 如果设置了 interrupt_on，注入操作规范提示
```

**设计意义**：这种固定顺序确保了**静态内容（角色定义、规范）在前，动态内容（任务状态、记忆、技能）在后**，符合模型对上下文的注意力分配规律。

---

### Q16：DeepAgents 中的记忆（Memory）和技能（Skills）有什么区别？各自的加载机制是什么？

**标准回答**：

| 对比维度 | 记忆（Memory/AGENTS.md） | 技能（Skills） |
|----------|--------------------------|----------------|
| **加载时机** | 每次调用都**全量注入** | 按需加载，只有命中匹配才完整读取 |
| **典型内容** | 项目规范、用户偏好、跨会话准则 | 特定领域的操作手册（如"如何使用搜索工具"） |
| **token 消耗** | 固定消耗，内容越多消耗越大 | 低消耗（只读 1KB frontmatter），命中后才完整加载 |
| **适用场景** | 需要始终生效的、高优先级的基础规则 | 可能用到的、领域特定的专业能力 |
| **推荐原则** | 内容保持**精简**，避免堆砌 | 可以有大量 Skills，不影响基础 token 消耗 |

**技能（Skills）的渐进式披露机制——三步流程**：

1. **启动阶段**：Agent 只读取每个 SKILL.md 文件的 **YAML frontmatter 前置元数据**（限制在 1024 字符），正文**不加载**

   ```yaml
   ---
   name: web_search
   description: 当需要在互联网搜索最新信息时使用本技能
   ---
   # 正文：详细的搜索工具使用教程...（启动时不加载）
   ```

2. **运行阶段**：模型根据任务判断是否需要某个 Skill；如果命中，再**完整读取技能文档**正文注入上下文

3. **优势**：无论有多少个 Skill 文件，启动时的 token 消耗都极低，实现真正的按需加载

---

### Q17：什么是上下文腐烂（Context Rot）？DeepAgents 如何通过上下文压缩解决这个问题？

**标准回答**：

- **什么是上下文腐烂**：当对话历史中积累了大量**低价值、高噪声**的内容（如已完成任务的工具调用日志、中间错误信息、冗余的格式提示），模型的有效注意力被这些无用信息稀释，导致模型在长任务中性能逐渐下降，错误率上升。这种现象叫**上下文腐烂（Context Rot）**。

- **重要认知**：**上下文窗口并非越大越好**，无用信息越多，有效信息的权重越低。128K 的窗口填满了噪声，不如 8K 的窗口装满精华。

**DeepAgents 的三层压缩策略**：

| 策略 | 触发场景 | 处理方式 |
|------|----------|----------|
| **大模型输出卸载** | 某次工具调用返回了超长的原始结果（如爬虫返回整个网页 HTML） | 将该工具调用的返回内容移出上下文，仅保留摘要引用 |
| **大模型输入卸载** | 早期的消息轮次已不再重要 | 将老旧消息从活跃上下文中移除，归档到文件系统 |
| **对话摘要（Summarization）** | 上下文总量接近阈值 | 双组件协同：生成结构化摘要 + 归档原始对话 |

**对话摘要的双组件机制**：

1. **上下文内摘要**：生成包含三要素的结构化摘要注入上下文：
   - 用户核心意图：用户最终想要达成什么目标
   - 已完成的工件：到目前为止已生成的文件、报告、代码等
   - 后续计划：接下来还需要完成哪些步骤

2. **文件系统归档**：被移出上下文的**完整原始对话**被序列化写入文件系统，作为永久记录保存——既不占用上下文窗口，又保证了可审计性和可恢复性。

---

### Q18：什么是运行时上下文（Runtime Context）？它与系统提示的区别是什么？

**标准回答**：

- **是什么**：运行时上下文是每次调用 Agent 时传入的**配置数据容器**，存储与本次调用相关的动态配置信息，如用户 API Key、用户 ID、数据库连接字符串、权限级别等。

- **与系统提示的核心区别**：**运行时上下文不会直接进入 LLM 的输入**，只有当工具或中间件**显式读取并将其加入提示**时，模型才能感知到这些信息。这是一种"按需暴露"的安全设计，避免将敏感配置直接暴露在模型输入中。

- **使用方式**：

  ```python
  # 1. 定义上下文结构（dataclass 或 TypedDict）
  from dataclasses import dataclass
  @dataclass
  class MyContext:
      user_id: str
      api_key: str

  # 2. 在工具中访问上下文
  @tool
  def fetch_user_data(query: str, config: RunnableConfig) -> str:
      runtime = ToolRuntime.from_config(config)
      ctx: MyContext = runtime.context  # 类型安全地访问上下文
      # 使用 ctx.user_id、ctx.api_key ...

  # 3. 在调用时传入上下文
  result = agent.invoke(
      {"messages": [HumanMessage("查询我的数据")]},
      config={"context": MyContext(user_id="u123", api_key="sk-xxx")}
  )
  ```

- **适用场景**：多用户 SaaS 平台（每个用户有不同的 API Key 和权限）、不同环境切换（开发/测试/生产使用不同的数据库连接）

---

### Q19：DeepAgents 如何实现跨会话长期记忆？命名空间隔离机制是如何设计的？

**标准回答**：

- **底层原理**：DeepAgents 将长期记忆也统一抽象为"文件系统"——记忆文件被存储在 StoreBackend（LangGraph BaseStore）中，Agent 通过与读写普通文件相同的工具（read_file、write_file、edit_file）来管理长期记忆。

- **记忆工作三步骤**：

  | 步骤 | 操作 | 说明 |
  |------|------|------|
  | **配置记忆路径** | 通过 memory=["path/to/AGENTS.md"] 指定 | 将记忆路径映射到 CompositeBackend + StoreBackend |
  | **读取记忆** | 全量注入或按需加载 | Agent 在每次对话开始时获取历史偏好和上下文 |
  | **更新记忆** | Agent 调用内置的 edit_file 或 write_file 工具 | Agent 自主决定哪些信息值得持久化保存 |

- **命名空间隔离机制（实现多租户记忆隔离）**：

  ```python
  # 用户级作用域：A 用户的记忆与 B 用户完全隔离
  namespace = ("users", user_id, "memory")

  # Agent 级作用域：不同 Agent 类型有独立的记忆空间
  namespace = ("agents", agent_type, "memory")

  # 组合作用域：特定用户 + 特定 Agent 的专属记忆
  namespace = ("users", user_id, "agents", agent_type, "memory")
  ```

---

### Q20：DeepAgents 在多用户记忆场景下如何保障安全性？

**标准回答**：

虽然命名空间隔离提供了基础的用户间隔离，但还需要以下额外的安全措施：

**1. 只读共享策略（防止 Prompt Injection 篡改策略文件）**

存在全公司共享的政策文件时，应将这些文件设置为**只读模式**，防止恶意用户通过精心构造的输入诱导 Agent 修改政策文件：

```python
backend = LocalDiskBackend(
    root_dir="/data",
    read_only_paths=["/data/policies/"]
)
```

**2. 敏感路径写入审批（Human-in-the-Loop）**

对于写入共享策略文件、删除关键数据等高风险操作，配置 interrupt_on 规则，触发人工审批后才允许执行：

```python
agent = create_deep_agent(
    ...
    interrupt_on=["write_file"],  # 每次写文件前暂停，等待人工确认
)
```

**3. 最小权限原则**
- 子 Agent 只获得完成自身任务所需的最小工具集
- LocalShellBackend 绝对不在生产环境赋予
- 本地磁盘后端开启 virtual_mode=True，防止 Agent 使用 .. 或 ~ 逃逸指定目录

> 💡 **面试亮点**："在我们的多租户 Agent 平台设计中，我们采用了三层防御：命名空间隔离确保数据不跨用户读写，只读策略防止 Prompt Injection 攻击，HITL 中断确保所有写入操作都经过人工审批。这三层防护缺一不可。"

---

## 六、综合架构设计

### Q21：如果让你从零设计一个基于 DeepAgents 的生产级代码生成 Agent，你会怎么做？

**标准回答（STAR 法则）**：

**Situation**：需要构建一个生产级的代码生成 Agent，能够接受复杂需求，自动生成、测试并部署代码，同时保证安全性和可靠性。

**Action（分六个层次设计）**：

1. **安全执行层 → 沙箱后端**：所有代码生成和执行都在 E2B 沙箱中进行，宿主机零风险

2. **专业化分工 → 子 Agent 拆分**：
   - `requirement_analyst_agent`：需求分析，输出结构化技术方案
   - `code_generator_agent`：代码生成，输出符合规范的代码文件
   - `test_agent`：单元测试生成与执行
   - `code_review_agent`：静态分析与代码审查

3. **上下文管理 → 文件系统 + 压缩**：
   - 中间代码文件写入文件系统，不占用上下文窗口
   - 配置上下文压缩策略，防止长任务上下文腐烂

4. **知识注入 → Skills**：为代码 Agent 配置语言特定的 Skill（Python 规范、API 使用指南），按需加载

5. **安全审批 → HITL**：在最终 write_file（写入生产代码库）前配置 interrupt_on，等待人工 Code Review 审批

6. **可观测性 → 上下文归档**：利用文件系统归档功能，将完整的生成过程作为永久记录保存，支持后续审计

**Result**：该架构实现了安全隔离、专业分工、上下文可控、人工审批四个核心目标，可以可靠处理复杂的企业级代码生成任务。

---

> 🏠 **[返回主页 README](../../README.md)** | 📚 **[专题索引](./README.md)** | ◀️ **上一篇：[10. 三大企业级项目实战面试题精通指南](./10_三大企业级项目实战面试题精通指南.md)** | ⚡ **[30分钟速记](../00_面试冲刺30分钟速记卡片.md)**
