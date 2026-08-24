> 📌 **[AI 大模型与云原生全栈知识库](../../README.md)** / **[Agent & LangGraph 题库套件](./README.md)**
> 🏠 [返回主页 README](../../README.md) | 📚 [专题索引](./README.md) | ⚡ [30分钟速记](../00_面试冲刺30分钟速记卡片.md)

---

### Q2.1: Q、K、V 矩阵是如何计算出来的？自注意力的完整计算数据流是什么？
**标准回答 (16K-22K 满分表达)**：
1. **输入表达与线性投影**：
   - 假设输入文本序列由 $N$ 个 Token 组成，经 Word Embedding 与位置编码合并后得到矩阵 $X \in \mathbb{R}^{N 	imes d_{model}}$。
   - 定义 3 个独立的可学习权重矩阵 $W^Q \in \mathbb{R}^{d_{model} 	imes d_k}, W^K \in \mathbb{R}^{d_{model} 	imes d_k}, W^V \in \mathbb{R}^{d_{model} 	imes d_v}$。
   - 通过矩阵相乘生成 Query, Key, Value 矩阵：
     $$Q = X W^Q, \quad K = X W^K, \quad V = X W^V$$
2. **完整数据流 5 步步阶**：
   - **Step 1 (投影)**：$X 
\rightarrow Q, K, V$
   - **Step 2 (相似度点积)**：计算 $S = Q K^T \in \mathbb{R}^{N 	imes N}$，代表任意两 Token 间的相关得分。
   - **Step 3 (缩放)**：$S_{scaled} = rac{S}{\sqrt{d_k}}$。
   - **Step 4 (Softmax 归一化)**：$A = 	ext{softmax}(S_{scaled}) \in \mathbb{R}^{N 	imes N}$，得到注意力概率权重矩阵。
   - **Step 5 (加权特征输出)**：$O = A V \in \mathbb{R}^{N 	imes d_v}$。


# 🎓 01. Transformer 与深度学习基础高分面试题 (深度重构版)

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
