# 🎓 大模型基础、Transformer 架构与 LLM 硬核理论面试高频题 (全量进阶版)

> 本文档针对大语言模型 (LLM) 研发、AI 算法工程师面试中的核心高频硬核考点，深度剖析 Transformer 架构细节、Self-Attention 数学推导、位置编码及微调量化机制。

---

## 一、 Transformer 架构与 Self-Attention 数学原理

### Q1: Self-Attention 注意力机制的公式是什么？为什么计算点积后要除以 $\sqrt{d_k}$？
**标准回答**：
- **缩放点积注意力公式 (Scaled Dot-Product Attention)**：
  $$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$
  其中 $Q \in \mathbb{R}^{N \times d_k}$, $K \in \mathbb{R}^{M \times d_k}$, $V \in \mathbb{R}^{M \times d_v}$，$d_k$ 为 Key 的向量维度。

- **为什么除以 $\sqrt{d_k}$（缩放因子 Scaling Factor 的作用）**：
  1. **防止梯度消失**：假设 $Q$ 和 $K$ 的各个元素独立同分布，均值为 0，方差为 1。则点积结果 $q \cdot k = \sum_{i=1}^{d_k} q_i k_i$ 的均值为 0，方差为 $d_k$。
  2. 当 $d_k$ 很大时（例如 $d_k = 64$ 或 $128$），点积数值可能非常大（方差达到 $d_k$），导致传入 `Softmax` 函数后结果落在极端饱和区（靠近 0 或 1）。
  3. `Softmax` 落在饱和区会导致梯度极小（梯度消失），影响反向传播时的梯度更新。除以 $\sqrt{d_k}$ 可将方差放缩回 1，使 `Softmax` 的输入保持在梯度平滑的范围内。

---

### Q2: 请对比 Multi-Head Attention（多头注意力）与 Single-Head Attention 的优势，并说明 MHA、MQA、GQA 的区别。
**标准回答**：
- **Multi-Head Attention 优势**：
  - 将高维映射空间切分为多个低维子空间，使模型能够在不同的线性子空间中**同时捕捉不同位置、不同语义层面的交互特征**（例如一个头关注语法关系，另一个头关注长距离实体指代）。
- **MHA / MQA / GQA 的演进对比**：
  - **MHA (Multi-Head Attention)**：$H$ 个 Query 头，对应 $H$ 个 Key 头和 $H$ 个 Value 头。表达能力强，但推理时 KV Cache 占用显存极大。
  - **MQA (Multi-Query Attention)**：$H$ 个 Query 头，所有 Query 头共享 **1 个 Key 头** 和 **1 个 Value 头**。大幅降低 KV Cache（减少到 $1/H$），极大地加速推理吞吐，但模型容量有所微弱下降。
  - **GQA (Grouped-Query Attention)**：折中方案（LLama 2/3、Qwen 2 广泛采用）。将 Query 头分为 $G$ 组，每组共享 1 个 Key 头和 1 个 Value 头。兼顾了 MHA 的模型性能与 MQA 的推理速度/显存节省。

---

### Q3: 什么是 FlashAttention (1/2/3)？它如何解决标准 Attention 的 $O(N^2)$ 内存开销？
**标准回答**：
- **标准 Attention 的瓶颈**：标准 Attention 需要在 GPU 显存 (HBM) 中保存中间过程巨大的 $N \times N$ 注意力矩阵 $S = QK^T$ 与 $P = \text{softmax}(S)$，导致大量的 HBM 内存读写瓶颈（Memory Bandwidth Bound）与 $O(N^2)$ 显存占用。
- **FlashAttention 核心优化**：
  1. **分块 (Tiling)**：将输入矩阵 $Q, K, V$ 划分为多个能够一次性装入 GPU 内部极速片上静态内存 (SRAM) 的小 Block。
  2. **在线 Softmax (Online Softmax)**：在 SRAM 内部边分块读取边更新 Softmax 局部归一化因子，无需显式保存全局的 $N \times N$ 中间矩阵。
  3. **重算 (Recomputation)**：反向传播时不保存中间注意力矩阵，而是根据 SRAM 内部的数据快速重新计算，大幅降低 HBM 读写，显存开销降至 $O(N)$，训练/推理速度提升 2~4 倍。

---

### Q4: 位置编码 (Positional Encoding) 解决了什么问题？请对比正弦位置编码 (Absolute Sinusoidal) 与 旋转位置编码 (RoPE)。
**标准回答**：
- **解决的问题**：Self-Attention 具有**置换不变性 (Permutation Invariance)**（点积计算与 Token 的先后顺序无关）。如果没有位置编码，模型无法识别词序信息。
- **编码方式对比**：
  - **绝对正弦位置编码 (Sinusoidal Positional Encoding)**：
    - 在 Input Embedding 上直接加算静态的正弦/余弦周期函数向量。外推能力差，无法直接支持超出训练序列长度的文本。
  - **RoPE (Rotary Position Embedding, 旋转位置编码)**：
    - 主流 LLM（Llama, Qwen, Mistral）的标准配置。
    - 原理：通过复数旋转矩阵，将绝对位置信息以旋转角的方式作用到 $Q$ 和 $K$ 向量上（保持复数内积特性），使得 $Q_m^T K_n$ 的内积直接包含两者的**相对位置差 $(m-n)$**。
    - 优点：具备极佳的相对位置表征能力，且易于通过 NTK-aware 或 YaRN 方法进行长上下文外推。

---

## 二、 现代 LLM 架构细节与计算显存估算

### Q5: 为什么当前大语言模型（GPT-4, Llama, Qwen）普遍采用 Decoder-Only 架构，而不是 Encoder-Decoder 或 Prefix-LM？
**标准回答**：
1. **注意力掩码 (Causal Mask) 与自回归预训练一致性**：Decoder-Only 架构采用因果下三角注意力掩码，预测下一个 Token 的任务与预训练目标完全一致。
2. **长序列扩展与 KV Cache 效率**：Decoder-Only 在生成文本时，历史 Token 的 Key-Value 向量可以缓存（KV Cache），每次增量推理只需计算当前最新 Token 的 $Q$，时间复杂度从 $O(N^2)$ 降为 $O(N)$。
3. **模型容量与上下文泛化能力**：研究（如 LLaMA、PaLM 论文）表明，在同等参数量和训练 Token 吞吐下，Decoder-Only 在零样本 (Zero-Shot) 与少样本 (Few-Shot) 涌现能力（In-Context Learning）上优于 Encoder-Decoder 架构。

---

### Q6: 详细解释 Layer Normalization 的 Pre-LN 与 Post-LN 区别，为什么大模型普遍选用 Pre-LN (或 RMSNorm)？
**标准回答**：
- **Post-LN（原始 Transformer 方案）**：
  - 结构：$\text{Output} = \text{LayerNorm}(X + \text{SubLayer}(X))$
  - 问题：随着网络层数加深，反向传播时靠近输入的层梯度容易衰减或不稳定，训练超深模型时容易发散。
- **Pre-LN（主流 LLM 方案）**：
  - 结构：$\text{Output} = X + \text{SubLayer}(\text{LayerNorm}(X))$
  - 优势：残差主干路径（Residual Stream）没有被 LayerNorm 阻断，梯度可以无阻碍地反向传播到最底层，极大地提升了训练稳定性。
- **RMSNorm（Root Mean Square Normalization）**：
  - 进一步简化 Pre-LN：只计算均方根缩放，舍弃了均值平移（Mean Center）操作，计算速度提升约 10%~50%。

---

### Q7: 什么是 KV Cache？如何精确计算一个大模型在推理时的 KV Cache 显存占用？
**标准回答**：
- **原理**：在自回归生成时，前文 Token 的 Key 和 Value 向量在后续每一个生成步都是固定不变的。将它们保存在 GPU 显存中（KV Cache），避免每生成一个新 Token 都重新计算整个前文。
- **精确计算公式**：
  $$\text{KV Cache 显存 (Bytes)} = 2 \times 2 \times n_{\text{layers}} \times d_{\text{model}} \times s \times b$$
  - 第一个 $2$ 表示 Key 和 Value 两个向量。
  - 第二个 $2$ 表示每个元素占用 2 个字节（FP16 / BF16 数据类型）。
  - $n_{\text{layers}}$：Transformer 隐藏层数。
  - $d_{\text{model}}$：模型隐藏层维度。
  - $s$：当前序列长度 (Sequence Length)。
  - $b$：Batch Size。
- **实例计算**：对 Llama-3 8B 模型（$n_{\text{layers}}=32, d_{\text{model}}=4096$），当 $b=4, s=4096$ 时：
  $$\text{KV Cache} = 4 \times 32 \times 4096 \times 4096 \times 4 = 8,589,934,592 \text{ Bytes} \approx 8.59 \text{ GB}$$

---

## 三、 大模型参数高效微调 (PEFT) 与量化技术

### Q8: 详细剖析 LoRA (Low-Rank Adaptation) 的原理、数学公式及优点。
**标准回答**：
- **核心思想**：在大模型微调过程中，权重矩阵的更新量 $\Delta W$ 具有很高的**低秩性 (Low-Intrinsic Rank)**。因此不需要更新整个原始权重矩阵 $W_0 \in \mathbb{R}^{d \times k}$，而是使用两个低秩矩阵 $A \in \mathbb{R}^{r \times k}$ 和 $B \in \mathbb{R}^{d \times r}$（其中 $r \ll \min(d, k)$）来近似拟合 $\Delta W$。
- **数学公式**：
  $$h = W_0 x + \Delta W x = W_0 x + \frac{\alpha}{r} (B \cdot A) x$$
  - 初始化：$A$ 矩阵采用高斯分布初始化，$B$ 矩阵初始化为零矩阵，确保在训练开始时 $\Delta W = 0$，初始输出与原模型完全一致。
  - $\frac{\alpha}{r}$ 为常数缩放因子（Scaling Factor）。
- **优势**：
  1. 显存开销极大降低：通常只占用总参数量的 0.01% ~ 0.1% 可训参数。
  2. 部署极具弹性：推理时可直接将 $B \cdot A$ 权重融合（Merge）回 $W_0$，实现零额外的推理延迟。

---

### Q9: 解释模型量化 (Quantization) 中的 INT8 与 INT4 (如 AWQ / GPTQ) 原理，FP16 到 INT8 如何映射？
**标准回答**：
- **基本原理**：将浮点数（FP32/FP16）高精度权重与激活值，映射到低精度的定点整数（INT8/INT4），从而将显存占用降低 50%~75%，并利用硬件 Tensor Core 加速整数计算。
- **非对称量化映射公式 (Quantization Scheme)**：
  $$q = \text{round}\left(\frac{x}{S}\right) + Z, \quad S = \frac{x_{\max} - x_{\min}}{2^b - 1}$$
  - $S$ (Scale) 为缩放因子，$Z$ (Zero-point) 为零点偏置，$b$ 为目标比特数（如 8 或 4）。
- **主流 PTQ 方案对比**：
  - **GPTQ**：基于二阶 Hessian 矩阵逆运算，逐层优化量化误差。
  - **AWQ (Activation-aware Weight Quantization)**：观察到只有 1% 的显著激活（Salient Weights）对模型性能至关重要，通过保护这 1% 的重要权重不进行粗暴量化，实现 INT4 下几乎无损的生成效果。

---

### Q10: 什么是 QLoRA？它相比经典 LoRA 做了哪些重大创新？
**标准回答**：
- **定义**：QLoRA 是将量化技术与 LoRA 微调完美结合的超低显存微调方案。
- **三大创新**：
  1. **NF4 (NormalFloat 4) 数据类型**：专为正态分布的模型权重设计的信息论最优 4 位量化类型。
  2. **双量化 (Double Quantization)**：对量化缩放因子（Quantization Scales）再进行一次 8 位量化，每参数额外节省 0.37 个 Bit 的显存。
  3. **分页优化器 (Paged Optimizers)**：利用 CUDA 统一内存，在 Gradient Checkpointing 显存峰值时自动将优化器状态页移入系统 CPU 内存，防止 OOM。
- **效果**：可以在单卡 24GB 显存（如 3090/4090）上微调 65B/70B 参数规模的超大模型。
