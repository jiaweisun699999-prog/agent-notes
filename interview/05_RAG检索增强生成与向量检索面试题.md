# 🎓 RAG 检索增强生成与向量检索面试高频题 (全量进阶版)

> 本文档聚焦企业级 RAG (Retrieval-Augmented Generation) 架构、文本切块策略、向量数据库 (Milvus/Pgvector) 索引原理、多模态 RAG、混合检索与重排序 (Rerank) 调优。

---

## 一、 RAG 核心切片 (Chunking) 与 Embedding 向量化

### Q1: 在企业级 RAG 中，文本切块 (Chunking) 有哪些策略？如何解决固定大小切块导致上下文断裂的问题？
**标准回答**：
- **切块策略分类**：
  1. **固定大小切块 (Fixed-size Chunking)**：如每块 500 字符，带有 50 字符重叠 (Overlap)。简单但容易打断完整语义。
  2. **按递归分隔符切块 (Recursive Character Chunking)**：优先按段落 `\n\n` 切分，其次按句号 `\n`、逗号 `,` 逐步降级，保证段落语义完整性。
  3. **语义切块 (Semantic Chunking)**：计算相邻句子间的嵌入向量余弦相似度，当相似度突变时作为切分边界。
  4. **文档结构切块 (Markdown/Code Chunking)**：按标题 `#`, `##` 或代码块标记切分。
- **解决上下文断裂的进阶方案**：
  - **父子文档切块 (Parent-Child Chunking)**：将大文本切分为小块（如 100 Tokens）用于向量检索匹配，命中后提取其对应的父级大块文本（如 1000 Tokens）喂给 LLM，兼顾检索精度与上下文完整性。
  - **滑动窗口重叠 (Chunk Overlap)**：在切块时保留 10%~20% 的重叠区域，防止关键短语被切分在两个 Chunk 边缘。

---

### Q2: 什么是 Dense Embedding 与 Sparse Embedding？为什么单用向量检索效果不佳？
**标准回答**：
- **Dense Embedding（稠密向量）**：
  - 使用 BGE, M3, OpenAI Text-Embedding-3 等模型提取语义向量（如 1024 维浮点数）。
  - **优点**：能够捕捉同义词、隐式语义表达（如“苹果”与“iPhone”的语义关联）。
  - **缺点**：对专有名词、产品型号、精确代码、数字、人名等**精确匹配极差**。
- **Sparse Embedding（稀疏向量 / 关键词匹配）**：
  - 使用 BM25 或 TF-IDF，输出高维稀疏向量。
  - **优点**：对特定关键词、型号、编号的精确匹配极其准确。
  - **缺点**：无法识别同义词与泛化语义。
- **结论**：在生产环境中，单一的 Dense 检索准确率往往不够。**混合检索 (Hybrid Search)** 是 16K-22K 岗位必须掌握的落地标准。

---

## 二、 高级检索技术：混合检索、HyDE 与 Rerank

### Q3: 详细剖析企业级 RAG 混合检索 (Hybrid Search) + Rerank 架构的完整链路。
**标准回答**：

```
[User Query] ──┬──> Dense Search (Vector Store, HNSW) ────> Top 50
               ├──> Sparse Search (BM25 Engine) ──────────> Top 50
               └──────────────────┬─────────────────────────────
                                  ▼
                   [RRF (Reciprocal Rank Fusion) 融合]
                                  │
                                  ▼ (初步合并 Top 30)
                       [Cross-Encoder Reranker] (如 BGE-Reranker-Large)
                                  │
                                  ▼ (重排序精筛选 Top 5)
                            [Context to LLM]
```

- **链路步步详解**：
  1. **双路召回 (Dual Recall)**：查询同时送入向量数据库（语义召回 Top 50）与 BM25 检索器（精确关键词召回 Top 50）。
  2. **倒数排名融合 (RRF, Reciprocal Rank Fusion)**：
     - 公式：$RRF\_Score(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$，无需做得分归一化即可合并两路排名。
  3. **精排重排序 (Reranking)**：
     - 使用 Cross-Encoder 重排序模型（如 `bge-reranker-large`），将 Query 与候选 Chunk 拼接输入计算相关性得分。
     - 得益于 Cross-Encoder 的自注意力机制交叉计算，重排序能将真正最相关的 Top 3-5 结果精准筛选给 LLM。

---

### Q4: 什么是 HyDE (Hypothetical Document Embeddings，假设性文档嵌入)？适用场景是什么？
**标准回答**：
- **原理**：针对用户提问 (Query) 与知识库文档 (Document) 在语义空间不完全对称的问题：
  1. 让 LLM 根据用户 Query 预先生成一份“假设的解答文档”（Hypothetical Document）。
  2. 将这份假设文档转换为 Embedding 向量。
  3. 使用该向量去向量数据库中检索相似的真实文档 Chunk。
- **适用场景**：用户提问非常简短、抽象或缺少背景信息，直接用 Query 去检索效果较差的情况。
- **缺点**：增加了一次额外的 LLM 调用开销，若假设文档产生严重幻觉可能影响检索方向。

---

## 三、 向量数据库与索引机制

### Q5: 向量数据库的核心索引算法有哪些？请对比 HNSW 与 IVFFlat 的优缺点。
**标准回答**：
- **HNSW (Hierarchical Navigable Small World, 分层可导航小世界网格)**：
  - 原理：构建多层图结构。最上层节点稀疏，用于快速跨越式跳跃；最底层包含全量节点，进行细粒度最近邻查找。
  - **优点**：检索速度极快（$O(\log N)$），召回率高（通常 > 95%）。
  - **缺点**：构建索引极其耗费内存（RAM），不适合超大规模（数十亿级）海量向量。
- **IVFFlat (Inverted File with Flat, 倒排文件索引)**：
  - 原理：使用 K-Means 将向量空间划分为 $N$ 个聚类质心（Centroids）。检索时先找到最近的几个质心，只在这些质心对应的倒排列表中查找。
  - **优点**：内存占用小，索引构建速度较快。
  - **缺点**：召回率依赖聚类质量，高并发下召回率低于 HNSW。

---

### Q6: 向量检索中的标量过滤 (Scalar Filtering) 有哪些实现方式？预过滤 (Pre-filtering) vs 后过滤 (Post-filtering) 的区别？
**标准回答**：
- **后过滤 (Post-filtering)**：先对全量向量进行 Top-K 最近邻检索，然后再从 Top-K 结果中过滤掉不满足属性条件（如 `tenant_id == 'A'`）的记录。
  - 缺点：极易导致最终返回的结果数远远少于 K，甚至返回空集合。
- **预过滤 (Pre-filtering)**：在向量检索之前或检索过程中（Single-stage Filtering），先通过标量索引（如 B-Tree、Bitset 掩码）过滤出满足条件的候选向量集合，再在该集合内进行向量距离计算。
  - 优势：生产环境标准选型（如 Milvus / Qdrant 支持原生高效单阶段预过滤）。

---

### Q7: 向量余弦相似度 (Cosine Similarity)、点积 (Dot Product) 与欧氏距离 (Euclidean / L2) 的数学关系与选型？
**标准回答**：
- **欧氏距离 (L2 Distance)**：计算高维空间中两点间的绝对直线距离，数值越小越相似。对向量的模长非常敏感。
- **余弦相似度 (Cosine Similarity)**：计算两个向量夹角的余弦值，取值区间 $[-1, 1]$，数值越大越相似。只关注向量方向，忽略模长大小。
- **内积 / 点积 (Inner Product, IP)**：计算两个向量的点积 $\sum a_i b_i$。
- **数学关联与选型**：当向量已经做过**单位归一化 (L2 Normalized)** 之后，点积在数值上与余弦相似度完全等价，且点积在 GPU/CPU 上可以利用矩阵乘法直接加速。因此推荐预先对向量归一化，检索时直接选用内积 (IP) 索引。

---

## 四、 RAG 评测与多模态扩展

### Q8: RAG 系统的核心指标如何评估？（介绍 Ragas 评估框架）
**标准回答**：
- **Ragas 框架四大评估指标**：
  1. **Faithfulness（忠实度 / 拒绝幻觉）**：回答的内容是否完全基于检索到的上下文，是否存在胡乱捏造。
  2. **Answer Relevance（回答相关性）**：LLM 生成的回答是否直接、切题地解答了用户的提问。
  3. **Context Precision（上下文精确率）**：检索到的 Chunk 中，真正有用的信息是否排在最前面。
  4. **Context Recall（上下文召回率）**：为了回答该问题，所需的所有关键事实是否都被成功检索出来。
