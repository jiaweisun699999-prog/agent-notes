# 🎓 AI Agent、LangChain、LangGraph 全套面试题库 (16K-22K 深度重构版)

> 本文档已完成全面深度重构，将原版简短提示升级为符合 **16K-22K 高薪岗位** 要求的**“Senior 架构师标准回答模型”**（涵盖：核心概念 + 底层机制/计算公式 + 代码 API 细节 + 生产实战踩坑加分项）。

---

## 一、Transformer 相关面试题

### Q1: Transformer 中包含哪三种注意力机制？它们分别应用在模型的什么阶段？
**标准回答 (16K-22K 满分表达)**：
1. **自注意力机制 (Self-Attention / 自内注意力)**：
   - **机制与应用**：$Q, K, V$ 均来自同一个输入序列自身。应用于 Transformer Encoder 以及 Decoder 的前半部分，用于计算同一个句子内部 Token 之间的上下文关联与语义依赖（如关联代词“它”与实体“猫”）。
2. **交叉注意力机制 (Cross-Attention / 互注意力)**：
   - **机制与应用**：$Q$ 来自 Decoder 的隐藏状态，$K, V$ 来自 Encoder 的最终输出。应用于 Transformer Decoder 的中间层，用于实现目标序列与源头序列（或条件提示与生成文本）之间的特征对齐。
3. **掩码自注意力机制 (Masked Self-Attention / 因果注意力)**：
   - **机制与应用**：在 Self-Attention 的 Softmax 之前加入下三角掩码矩阵 (Causal Mask)，强制将未来位置的注意力得分置为 $-\infty$。应用于 Decoder 自回归文本生成阶段，防止模型在预测当前 Token 时“偷看”未来的真实词。

---

### Q2.1: Q、K、V 矩阵是如何计算出来的？自注意力的完整计算数据流是什么？
**标准回答 (16K-22K 满分表达)**：
1. **输入表达与线性投影**：
   - 假设输入文本序列由 $N$ 个 Token 组成，经 Word Embedding 与位置编码合并后得到矩阵 $X \in \mathbb{R}^{N \times d_{model}}$。
   - 定义 3 个独立的可学习权重矩阵 $W^Q \in \mathbb{R}^{d_{model} \times d_k}, W^K \in \mathbb{R}^{d_{model} \times d_k}, W^V \in \mathbb{R}^{d_{model} \times d_v}$。
   - 通过矩阵相乘生成 Query, Key, Value 矩阵：
     $$Q = X W^Q, \quad K = X W^K, \quad V = X W^V$$
2. **完整数据流 5 步步阶**：
   - **Step 1 (投影)**：$X \rightarrow Q, K, V$
   - **Step 2 (相似度点积)**：计算 $S = Q K^T \in \mathbb{R}^{N \times N}$，代表任意两 Token 间的相关得分。
   - **Step 3 (缩放)**：$S_{scaled} = \frac{S}{\sqrt{d_k}}$。
   - **Step 4 (Softmax 归一化)**：$A = \text{softmax}(S_{scaled}) \in \mathbb{R}^{N \times N}$，得到注意力概率权重矩阵。
   - **Step 5 (加权特征输出)**：$O = A V \in \mathbb{R}^{N \times d_v}$。


### Q2: 详细介绍自注意力机制 (Self-Attention) 的计算公式与数学原理。
**标准回答 (16K-22K 满分表达)**：
- **核心公式**：
  $$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}
\right)V$$
- **三步推导过程**：
  1. **相似度矩阵计算 ($QK^T$)**：输入序列经线性变换得到 $Q \in \mathbb{R}^{N \times d_k}, K \in \mathbb{R}^{N \times d_k}$，矩阵相乘点积衡量每对 Token 之间的相关性原始得分。
  2. **维度缩放与 Softmax 归一化 ($\frac{\cdot}{\sqrt{d_k}} 
\rightarrow \text{Softmax}$)**：除以缩放因子 $\sqrt{d_k}$（$d_k$ 为向量维度），防止维度很大时点积数值过大，导致传给 Softmax 后落在极端饱和区（解决梯度消失问题）；随后经 Softmax 归一化为和为 1 的概率权重分布。
  3. **特征加权聚合 ($\cdot V$)**：将概率权重作用于 Value 矩阵 $V \in \mathbb{R}^{N \times d_v}$，加权求和融合得到上下文特征向量。

---

### Q3: 什么是多头自注意力机制 (Multi-Head Self-Attention)，作用是什么？
**标准回答 (16K-22K 满分表达)**：
- **定义**：将 $Q, K, V$ 通过 $h$ 组独立的线性投影矩阵映射到 $h$ 个低维子空间，并行独立计算 $h$ 次 Scaled Dot-Product Attention，最后将 $h$ 个头的输出拼接 (Concat) 并通过 $W^O$ 矩阵再次投影。
  $$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \dots, \text{head}_h) W^O$$
- **核心作用与优势**：
  1. **多子空间特征捕捉**：单头注意力容易被全局主导语义吸引；多头机制允许模型同时在不同的表达子空间中关注多样化特征（例如 Head 1 关注句法结构，Head 2 关注代词指代，Head 3 关注时态关系）。
  2. **提升模型表达容量**：在保持总计算复杂度基本不变（每个头维度缩减为 $d_{model}/h$）的前提下，极大地丰富了模型的特征吸收能力。

---

### Q4: Transformer 为什么需要位置编码？有哪些主流实现方案？
**标准回答 (16K-22K 满分表达)**：
- **必要性**：Self-Attention 运算本质上仅包含点积与加权求和，具有**置换不变性 (Permutation Invariance)**（打乱 Token 输入顺序，计算输出完全一致）。如果没有位置编码，模型无法识别“猫吃鱼”和“鱼吃猫”的语义差异。
- **主流实现方案演进**：
  1. **绝对位置编码 (Sinusoidal / Learned)**：在 Embedding 上直接相加固定周期的正弦余弦向量或可学习的位置向量（经典 Transformer / BERT）。
  2. **相对位置编码 (Relative PE / RoPE / ALiBi)**：
     - **RoPE (旋转位置编码 - LLaMA / DeepSeek 标配)**：通过在复数空间对 $Q, K$ 向量施加旋转矩阵，让点积计算显式包含相对距离，具备极佳的长文本外推性能。
     - **ALiBi**：在 Attention Score 上直接叠加随距离增加而线性衰减的偏置，外推能力极强。

---

### Q5: 简述 Transformer 的完整执行流程？
**标准回答 (16K-22K 满分表达)**：
1. **输入处理**：输入 Token 序列经过 Word Embedding 转换为连续向量，加上 Positional Encoding 注入位置特征。
2. **Encoder 编码阶段 ($N$ 层 Stack)**：
   - 向量传入 **Multi-Head Self-Attention** 提取全局依赖。
   - 经过 **Add & Norm**（残差连接 + Layer Normalization / RMSNorm）。
   - 传入 **Feed-Forward Network (FFN / SwiGLU)** 做非线性映射，再次过 **Add & Norm**。
3. **Decoder 解码阶段 ($N$ 层 Stack)**：
   - 传入 **Masked Multi-Head Self-Attention**（受因果掩码限制，只能看到左侧已生成的 Token）。
   - 经过 **Cross-Attention**，以 Decoder 当前隐藏状态为 $Q$，Encoder 最终输出为 $K, V$，融合源头编码信息。
   - 经过 FFN 与 Add & Norm。
4. **输出预测**：最终隐藏状态通过 Linear 映射到词表大小的 Logits，配合 Softmax 计算概率，自回归逐词生成下一个 Token。

---

### Q6: 什么是 RNN？它的核心特点、致命缺陷及 LSTM / GRU 的改进原理是什么？
**标准回答 (16K-22K 满分表达)**：
- **RNN 核心特点**：专为序列数据设计，按时间步递推更新隐藏状态 $h_t = 	anh(W_{hh} h_{t-1} + W_{xh} x_t + b)$ 保存历史信息。
- **致命缺陷**：
  1. **强串行依赖不可并行**：$t$ 时刻计算强依赖 $t-1$ 时刻输出，GPU 无法并行化，训练极慢。
  2. **梯度消失与梯度爆炸**：时间轴反向传播 (BPTT) 时雅可比矩阵连乘导致长距离梯度衰减为 0 或飙升为 $\infty$，无法捕捉长文本依赖。
- **LSTM / GRU 改进**：
  - **LSTM (长短期记忆网络)**：引入细胞状态 $C_t$ 和三大门控（**遗忘门**决定丢弃历史、**输入门**决定写入新值、**输出门**决定输出），构建加性梯度通路，彻底解决梯度消失。
  - **GRU (门控循环单元)**：精简为**更新门 (Update Gate)** 与 **重置门 (Reset Gate)**，性能接近 LSTM 但参数更少、计算更快。

---

### Q7: 什么是 CNN 中的卷积 (Convolution) 与池化 (Pooling)？它们的核心特性与作用是什么？
**标准回答 (16K-22K 满分表达)**：
- **卷积 (Convolution)**：
  - 原理：滑动卷积核（Kernel/Filter）在局部感受野（Receptive Field）上与输入特征相乘求和加偏置。
  - 两大核心特性：
    1. **局部连接 (Local Connectivity)**：每个神经元仅与输入的局部空间区域相连，提取局部图像/文本边缘与语义特征。
    2. **权值共享 (Weight Sharing)**：同一个卷积核在整个输入特征图上共享参数，极大降低模型参数量与过拟合风险。
- **池化 (Pooling)**：
  - 原理：降低特征图空间分辨率的下采样 (Sub-sampling) 操作。
  - 分类：**最大池化 (Max Pooling)** 提取区域最显著特征；**平均池化 (Average Pooling)** 保留平滑背景信息。
  - 核心作用：**降维减少计算量**、提供**平移不变性 (Translation Invariance)**，增强模型鲁棒性。


---

### Q8: 什么是神经网络的正向传播 (Forward Propagation) 与反向传播 (Backpropagation / BP)？
**标准回答 (16K-22K 满分表达)**：
1. **正向传播 (Forward Propagation / 前向传播)**：
   - **定义**：输入数据从网络输入层出发，经过各个隐藏层的线性变换（矩阵乘法 $W \cdot x + b$）与非线性激活函数（如 ReLU、GeLU、Softmax）逐层向前递推，最终在输出层计算出预测值 $\hat{y}$，并与真实标签 $y$ 计算得到损失函数值 $\mathcal{L}$ (Loss)。
   - **核心职责**：评估模型在当前参数下的预测表现，并计算标量 Loss。
2. **反向传播 (Backpropagation / BP 算法)**：
   - **原理**：基于微积分中的**链式法则 (Chain Rule)**，从输出层的损失函数 $\mathcal{L}$ 出发，沿网络相反方向（从后往前）逐层求导，计算出 Loss 对每一个可学习参数（权重 $W$ 与偏置 $b$）的**梯度 (Gradients $\frac{\partial \mathcal{L}}{\partial W}$)**。
   - **参数更新**：计算得到的梯度交由优化器（如 SGD、AdamW）按照学习率 $\eta$ 沿梯度的反方向更新权重：
     $$W_{new} = W_{old} - \eta \cdot \frac{\partial \mathcal{L}}{\partial W}$$
   - **核心职责**：将预测误差逆向传导，求解各个参数的梯度以指导模型自我学习迭代。
3. 💡 **16K-22K 大模型生产加分项 (激活重算 Activation Checkpointing)**：
   - 在反向传播计算梯度时，必须依赖正向传播时暂存在显存里的**中间激活值 (Activations)**。
   - 在超大模型训练时，激活值显存占用甚至超过模型权重本身。生产中普遍采用 **Activation Checkpointing (重算机制)**：正向传播时不保存全部激活值，反向传播时按需重新计算，用少量计算时间换取巨大的显存节省。


---

> 🏠 **[返回主页 README](../../README.md)** | 📚 **[专题索引](./README.md)** | ▶️ **下一篇：[02. LangChain 与 Agent 核心基础面试题](./02_LangChain与Agent核心基础.md)** | ⚡ **[30分钟速记](../00_面试冲刺30分钟速记卡片.md)**

---

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

### Q7 & Q8: 结构化输出的三种实现方式是什么？如何获取及各自的优缺点？
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

---

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

---

## 五、HITL 人工介入面试题

### Q1: 什么是 HITL (Human-in-the-Loop)？它依靠什么底层机制实现？
**标准回答 (16K-22K 满分表达)**：
- **定义**：HITL (人工介入机制) 允许 Agent 在执行高风险操作（如退款、删除数据库、发送邮件）前强行挂起任务，等待人工审核、修改参数或确认后继续恢复执行。
- **底层依靠**：依托 **`Checkpointer` 持久化快照** 与 **`interrupt()` 打断函数** 共同实现。通过在快照中保存当前的 Supstep 状态，断开与主线程的连接，等待外部提交 `Command(resume=...)` 后从断点恢复。

---

### Q2: 详细说明 HITL 的四种策略方式及其场景。
**标准回答 (16K-22K 满分表达)**：
1. **前置审批策略 (Approval Before Execution)**：在节点/工具执行前拦截（如 `interrupt_before=["delete_db_node"]`），等待管理员 Click Approve。
2. **事中中断与编辑策略 (Interrupt & Edit)**：在 Node 内部抛出 `user_input = interrupt({"msg": "请确认修改SQL"})`，允许人工修改输入后再继续。
3. **事后校验与反馈策略 (Human Review & Correction)**：节点执行完后拦截，人工检查 LLM 生成的草稿，若不满意打回重写。
4. **自定义条件介入策略 (Conditional HITL)**：仅当 LLM 的 Confidence 得分低于阈值或转账金额 $> \$10,000$ 时才动态触发人工拦截。

---

### Q3: 简述 HITL 从挂起到恢复的完整五步执行流程。
**标准回答 (16K-22K 满分表达)**：
1. **触发挂起**：Agent 节点内部执行到 `interrupt(payload)` 逻辑。
2. **状态保存**：LangGraph 捕获中断信号，将当前 State 和中断 Payload 保存到 `Checkpointer` 中。
3. **任务暂停**：图终止当前 Superstep，线程释放，控制权交还前端/调用方。
4. **人工操作**：人工在 UI 界面查看审批内容，点击批准或输入修正后的数据。
5. **断点恢复**：调用 `app.invoke(Command(resume=user_response), config)`，框架读取 `thread_id` 对应的快照，将 `user_response` 赋值给 `interrupt()` 并继续执行后续节点。

---

### Q4: 自定义 HITL 的典型生产适用场景有哪些？
**标准回答 (16K-22K 满分表达)**：
- **高风险写操作**：涉及金融转账、数据库修改、生产环境部署。
- **敏感合规审查**：公开发布推文/新闻稿前的内容人工审核。
- **低置信度降级**：RAG 检索结果置信度很低时，提示人工接入客服（Human Handoff）。

---

## 六、Guardrails 护栏面试题

### Q1: 什么是 Guardrails 护栏机制？它分为哪两大类？
**标准回答 (16K-22K 满分表达)**：
- **定义**：Guardrails 是 LLM 应用中的安全防控屏障，防止越狱攻击、毒性输出、隐私泄漏与幻觉。
- **两大类**：
  1. **输入护栏 (Input Guardrails)**：在 Prompt 提交给 LLM 前拦截（防 Prompt 注入、防 Prompt 越狱、敏感词过滤）。
  2. **输出护栏 (Output Guardrails)**：在 LLM 生成结果返回给用户前校验（幻觉检测、JSON 语法校验、PII 脱敏、合规审计）。

---

### Q2: 什么是 PII 检测？包含哪四种主流处理方式？
**标准回答 (16K-22K 满分表达)**：
- **定义**：PII (Personally Identifiable Information) 个人敏感身份信息检测（如身份证号、手机号、信用卡、真实姓名）。
- **四种处理方式**：
  1. **Redact (重写替换)**：将敏感数据直接替换为占位符（如 `[PHONE_NUMBER]`）。
  2. **Mask (掩码遮挡)**：部分打码（如 `138****1234`）。
  3. **Hash (哈希加密)**：通过不可逆 Hash 转化为唯一 ID，常用于日志保存。
  4. **Block (直接拦截)**：触发强安全规则，直接中断请求并给用户提示“包含敏感信息，禁止发送”。

---

### Q3: 什么是自定义 Guardrails？如何利用代码/微模型实现？
**标准回答 (16K-22K 满分表达)**：
- **实现机制**：通过在 Agent 的入口/出口挂载轻量级校验函数或部署专门的小模型（如 Llama-Guard / NeMo Guardrails）。
- **流程**：输入 $
\rightarrow$ 自定义正则/小模型评分 $
\rightarrow$ 若低于安全阈值，直接短路返回拒绝提示，跳过昂贵的主 LLM 调用（既节省 Token 成本又提升响应速度）。

---

### Q4: 生产环境下多层 Guardrails 的最优组合策略是什么？
**标准回答 (16K-22K 满分表达)**：
- **三层递进组合策略**：
  1. **第 1 层 (极速层 - 正则与黑名单)**：耗时 $< 1\text{ms}$，拦截常见 SQL 注入、极度违规词。
  2. **第 2 层 (轻量分类模型层 - Llama-Guard / Presidio)**：耗时 $< 50\text{ms}$，执行 PII 识别与越狱检测。
  3. **第 3 层 (业务语义层 - 自定义 LLM Evaluator)**：对 LLM 生成的最终答案做 Faithfulness (忠实度) 与幻觉审计。

---

> 🏠 **[返回主页 README](../../README.md)** | 📚 **[专题索引](./README.md)** | ◀️ **上一篇：[03. Agent 长短期记忆与状态管理](./03_Agent长短期记忆与状态管理.md)** | ▶️ **下一篇：[05. Runtime 运行时与 MCP 协议](./05_Runtime运行时与MCP协议.md)** | ⚡ **[30分钟速记](../00_面试冲刺30分钟速记卡片.md)**

---

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

---

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

---

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

---

## 九、LangGraph 核心面试题 (Part 3：Interrupt 机制与避坑黄金法则)

### Q25: 什么是 LangGraph 的 `interrupt()` 机制？
**标准回答 (16K-22K 满分表达)**：
- **定义**：`interrupt()` 是 LangGraph 在节点内部显式触发人机交互 (HITL) 的核心函数。
- **机制**：当代码运行到 `value = interrupt({"question": "确认删除？"})` 时，图强行挂起，并将 payload 抛给客户端。外部提交 `Command(resume="Approved")` 后，`interrupt()` 函数直接返回 `"Approved"` 并继续向下执行。

---

### Q26: `interrupt()` 能够正常工作的三个必要条件是什么？
**标准回答 (16K-22K 满分表达)**：
1. **必须挂载 `Checkpointer`**：如果没有持久化快照，图无法在中断后保存状态，调用 `interrupt` 会直接抛错。
2. **必须指定 `thread_id`**：调用时配置中必须包含 `configurable: {"thread_id": "xxx"}` 用于唯一定位快照。
3. **传入与恢复的参数必须可序列化**：`interrupt(payload)` 中的 `payload` 及 `Command(resume=...)` 传递的值必须支持 msgpack / JSON 序列化。

---

### Q27: 调用 `interrupt()` 后，LangGraph 框架内部会依次执行哪五件事？
**标准回答 (16K-22K 满分表达)**：
1. **捕获中断信号**：底层引擎捕获节点抛出的 `GraphInterrupt` 异常。
2. **存盘快照**：自动将当前 Superstep 的完整状态和中断 Payload 保存到 Checkpointer 存储中。
3. **设置 `next` 节点**：将当前的断点节点记录到快照的 `.next` 字段中。
4. **暂停图执行**：释放当前运行线程，终止图调用的执行流。
5. **抛出中断事件**：在 API / 流式响应中向调用方发出中断通知。

---

### Q28: 恢复中断的核心要点是什么？恢复后从哪里开始继续执行？
**标准回答 (16K-22K 满分表达)**：
- **核心要点**：使用完全相同的 `thread_id` 调用 `app.invoke(Command(resume=value), config)`。
- **执行起始位置**：恢复后**直接从上次调用 `interrupt()` 的那一行代码之后**继续向下执行，**绝对不会重新执行该节点前面已经跑过的代码**（保证幂等性）。

---

### Q29: 什么是 v3 惰性流 (Lazy Stream)？如何正确消费？
**标准回答 (16K-22K 满分表达)**：
- **特点**：惰性求值流，如果不主动消费或未挂接 Handler，后端不会浪费 CPU/网络资源进行序列化推送。
- **消费方式**：必须在 Python 中使用 `async for event in app.astream(...)` 显式迭代消费。

---

### Q30: 生产环境下交互式 HITL 的五种常见模式。
**标准回答 (16K-22K 满分表达)**：
1. **审批模式 (Approve / Reject)**：人工传回布尔值决定分支。
2. **审核并编辑模式 (Review & Edit)**：人工改写 LLM 生成的草稿后再提交。
3. **补充输入模式 (Elicit Input)**：LLM 发现槽位缺失（如缺失手机号），打断等待用户补充。
4. **多节点并行中断模式**：多个并发分支各自触发中断，各自独立等待恢复。
5. **Tool 内部中断模式**：在自定义 Tool 函数内部直接调用 `interrupt()`。

---

### Q31: **[面试必考避坑项]** 使用 `interrupt()` 的五条黄金规则。
**标准回答 (16K-22K 满分表达)**：
1. ⚠️ **禁止用裸 `try...except Exception` 包裹 `interrupt()`**：因为 `interrupt()` 本质是通过抛出 `GraphInterrupt` 结构性异常实现的，裸 `except` 会误捕获该异常导致中断失效。
2. ⚠️ **禁止改变节点内部 `interrupt()` 的调用顺序与次数**：恢复执行时框架依赖调用的顺序号（Index）精准返回值。
3. ⚠️ **中断前产生的副作用 (Side Effects) 必须保证幂等**：如中断前发了 HTTP 请求，需防止恢复时重复触发（注意：恢复不会重跑中断前的代码，但分支重试时需要注意）。
4. ⚠️ **传递的参数必须可 JSON / MsgPack 序列化**：禁止传入数据库连接、Class 实例。
5. ⚠️ **禁止编写 `while True: interrupt(...)` 无限死循环**。

---

> 🏠 **[返回主页 README](../../README.md)** | 📚 **[专题索引](./README.md)** | ◀️ **上一篇：[07. LangGraph 容错机制与全量流式输出](./07_LangGraph容错机制与全量流式输出.md)** | ⚡ **[30分钟速记](../00_面试冲刺30分钟速记卡片.md)**

---
