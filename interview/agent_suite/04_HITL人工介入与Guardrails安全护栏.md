> 📌 **[AI 大模型与云原生全栈知识库](../../README.md)** / **[Agent & LangGraph 题库套件](./README.md)**
> 🏠 [返回主页 README](../../README.md) | 📚 [专题索引](./README.md) | ⚡ [30分钟速记](../00_面试冲刺30分钟速记卡片.md)

---

# 🎓 04. HITL 人工介入与 Guardrails 安全护栏面试题 (深度重构版)

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
