# 部门知识库 / RAG 证据基线（2026-09）

> 日期：2026-09-30  
> 用途：为 `docs/chapters/03-department-knowledge-base.md`、知识库架构、Demo 与后续部门试点提供事实和研究依据。  
> 原则：明确区分 **论文结论 / 官方产品事实 / 工程建议 / 待内网实测**，不把经验判断包装成学术结论。

---

## 1. 本次核验结论

现有知识库讲义的主方向是成立的，但此前证据链不完整。

当前可以被较强证据支持的结论：

1. RAG 的核心价值是让生成模型访问外部知识，而不是把全部知识固化在模型参数中；外部知识更容易更新并提供来源追溯。
2. RAG 不等于“向量数据库”。现代检索系统可以同时使用关键词/全文、Dense Vector、Hybrid、Rerank，以及由 Agent 主动控制的多轮检索。
3. BM25 不是过时方案。BEIR 的跨域基准显示 BM25 是稳健基线；Dense Retrieval 在某些问答任务上优势明显，但并非所有域都稳定优于词法检索。
4. Hybrid Retrieval 是值得优先验证的工程候选，但不能未经本部门语料测试就宣布它一定优于单一检索。
5. Long Context 与 RAG 不是简单替代关系。公开研究显示，在资源充足时 Long Context 在一些基准上可以优于 RAG，而 RAG 仍具有显著成本优势；两者适合按任务路由。
6. Agentic Retrieval 的关键变化是“模型决定是否检索、搜什么、是否继续搜”，而不是出现了一种新的向量算法。
7. Retrieval 本身会失败。错误召回、缺失召回、冲突版本和不相关上下文都会继续传导到生成端，因此知识库必须单独测试 Retriever。
8. RAG 不能保证消除幻觉。即使提供了检索内容，生成结果仍可能出现无依据或与证据矛盾的陈述。
9. 企业知识库的权限必须在检索/查询阶段执行；不能先把无权查看的片段取出再依靠 Prompt 要求模型“不要泄露”。
10. Chunk、Parser、Metadata、版本和引用并非附属功能，它们直接决定检索与追溯质量。
11. GraphRAG 等图结构方案针对“全局主题、跨实体关系、全语料 sensemaking”有明确价值，但不应该成为普通制度/手册问答的默认起点。

现有讲义中需要降级为“工程建议”而不是“研究结论”的内容：

- Markdown 适合作为技术知识的机器可读格式；
- PDF 不适合作为唯一机器知识源；
- XLSX/CSV 一般不应以向量检索作为主要访问方式；
- 代码默认不需要向量化；
- Open WebUI 更适合作为部门共享入口、Cherry Studio 更适合作为个人知识工作台。

这些判断总体合理，但属于结合产品形态和工程维护成本做出的架构建议，不是论文证明的普适结论。

---

## 2. 学术研究证据

| 研究 | 核心发现 | 对部门知识库设计的含义 | 证据类型 |
|---|---|---|---|
| Lewis et al., **Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks**, NeurIPS 2020 | 将生成模型与显式外部非参数知识结合；论文动机包含知识更新与 provenance 问题 | 知识不应只依赖模型参数；需要外部可更新知识层与来源追溯 | 经典 RAG 原始论文 |
| Karpukhin et al., **Dense Passage Retrieval**, EMNLP 2020 | Dense Retriever 在论文测试的 open-domain QA 数据集上明显优于强 BM25 基线 | Embedding/Dense Retrieval 对语义问法有价值，但结论限定于具体任务/语料 | 同行评审 |
| Thakur et al., **BEIR**, NeurIPS 2021 | 18 个异构检索数据集上，BM25 是稳健 baseline；reranking / late-interaction 平均更强但计算成本更高 | 不应默认“向量一定优于关键词”；需要自己的语料 Benchmark，Rerank 是质量/成本权衡 | 同行评审 |
| Liu et al., **Lost in the Middle**, TACL 2024 | 长上下文模型对相关信息位置敏感，中间位置可能明显退化 | “能塞进上下文”不等于“稳定利用全部上下文”；Full Context 仍需测试 | 同行评审；模型代际较早，作为风险证据而非 2026 模型定论 |
| Li et al., **RAG or Long-Context LLMs?**, EMNLP Industry 2024 | 资源充足时 LC 平均表现更好，RAG 成本显著更低；提出按任务路由的混合方法 | 不应把 RAG 与 Full Context 做成二选一教条，应按文档规模、问题类型和成本路由 | 同行评审 |
| Asai et al., **Self-RAG**, 2023 | 固定无差别检索可能带来无用上下文；模型可按需检索并自反思 | 为 Agentic/Adaptive Retrieval 提供研究依据，但不意味着所有问题都应使用 Agent 循环 | 研究论文 |
| Yan et al., **Corrective RAG**, 2024 | RAG 对检索文档质量高度敏感；提出检索质量评估与纠正动作 | Retriever 质量必须被独立测试；“查到了内容”不等于证据可用 | 研究论文 |
| Es et al., **RAGAS**, 2023 | RAG 需要从 retrieval、faithfulness、answer quality 等多个维度评估 | 知识库验收不能只看最终回答；需要分层指标 | 研究论文/评测框架 |
| Ru et al., **RAGChecker**, 2024 | 对 Retrieval 与 Generation 进行细粒度诊断，8 套 RAG 系统显示架构选择存在明显 trade-off | 建议把检索错误与生成错误分开定位，建立回归测试 | 研究论文/开源框架 |
| Niu et al., **RAGTruth**, ACL 2024 | RAG 输出仍可能包含无支持或矛盾陈述 | RAG 只能降低风险，不能作为“不会幻觉”的保证 | 同行评审 |
| Gao et al., **ALCE / Enabling LLMs to Generate Text with Citations**, EMNLP 2023 | 引用质量可独立评测；当时最佳系统仍存在大量 citation support 缺失 | “有引用按钮”不等于引用完整/正确；要测试 Citation Correctness / Completeness | 同行评审 |
| Edge et al., **From Local to Global: GraphRAG**, 2024 | 普通 chunk retrieval 对全语料全局问题存在局限；图+社区摘要对特定全局 sensemaking 问题有优势 | GraphRAG 应作为特殊问题类型的扩展，而不是部门知识库默认第一阶段 | Microsoft Research / preprint |

### 2.1 长上下文不是“检索命中以后就解决了”

知识库系统实际上存在两次不同意义上的“召回/利用”：

```text
用户问题
  ↓
外部 Retrieval
  ↓
候选 Chunk / Document
  ↓
Rerank / Filter / Context Packing
  ↓
LLM Context
  ↓
模型在上下文中再次定位、关联、理解证据
  ↓
生成答案
```

为了避免概念混淆，培训中建议区分：

1. **External Retrieval Recall**：Retriever 有没有把正确资料找出来；
2. **In-context Retrieval / Context Utilization**：正确资料已经进入 Prompt 后，LLM 能否在长上下文和干扰内容中稳定找到并使用它。

已有研究表明第二层同样会失败：

- **Lost in the Middle（TACL 2024）**：相关信息在长上下文中的位置会显著影响模型使用效果，常见现象是开头/结尾优于中间；其开放域 QA case study 中，把检索文档从 20 增加到 50，Retriever Recall 继续提升，但 Reader 最终性能只得到约 1%–1.5% 的边际提升。这直接说明“多召回一些文档”不等于“模型能有效利用更多文档”。
- **RULER（2024）**：把简单 Needle-in-a-Haystack 扩展到多 needle、多跳和聚合任务。论文测试的 17 个长上下文模型虽然很多在简单 NIAH 上接近满分，但随着长度和复杂度增加几乎都明显下降；支持的“标称 Context Window”不能等同于“有效可用 Context”。
- **NoLiMa（ICML 2025）**：去掉 query 与 needle 之间的直接字面匹配后，长上下文检索明显变难；论文测试的 13 个至少支持 128K Context 的模型中，32K 时有 11 个跌到其短上下文强基线的 50% 以下。
- **LongBench v2（ACL 2025）**：将长上下文评估扩展到更真实的单/多文档 QA、代码仓库、结构化数据等任务，说明真实长上下文问题远比简单 NIAH 更难。
- **Context Length Alone Hurts LLM Performance Despite Perfect Retrieval（Findings of EMNLP 2025）**：进一步控制“相关信息已经被完美检索”的条件，在 5 个开放/闭源模型的数学、QA、代码任务上仍观察到随着输入变长而出现 13.9%–85% 的性能下降。它说明问题不只是 Retriever 找不找得到，Context Length 本身也可能影响后续推理和利用。
- **Context Rot（Chroma Technical Report, 2025）**：对包括 GPT-4.1、Claude 4、Gemini 2.5、Qwen3 在内的 18 个模型做控制实验，观察到输入增长时可靠性并非均匀保持。该项属于产业技术报告而非同行评审论文，应作为“最新实践证据”，不能与 ACL/ICML 论文同级表述。

因此知识库设计必须加入一个独立概念：

> **Context Budget / Evidence Budget：不是检索到多少就塞多少，而是在覆盖必要证据的前提下，尽量减少无关、重复、冲突和低价值 Context。**

这也是为什么 Top-K、Similarity Threshold、Rerank、Metadata Filter、去重、上下文压缩、分阶段读取和 Agentic Retrieval 都不仅是“节省 Token”的优化，也是在控制 LLM 最终需要处理的信息负荷。

### 2.2 重要边界

- Lewis 2020 的原始 RAG 实现使用 Dense Vector Index，但今天工程实践中的 “RAG” 已广泛指 **Retrieval → Context Augmentation → Generation** 的系统范式；因此可以使用 BM25、Hybrid、SQL/API 等检索方式，但培训应说明这是工程上扩展后的概念用法。
- DPR 在其 open-domain QA 数据集上的优势不能外推成“Dense 永远优于 BM25”；BEIR 正好说明跨域泛化中 BM25 仍然很强。
- “Lost in the Middle”证明了长上下文存在利用风险，但不能直接拿 2023/2024 模型结果断言 2026 所有旗舰模型仍保持相同幅度的退化。培训应把它作为设计风险和评测理由。
- GraphRAG 的优势集中于特定的 global question / sensemaking 场景，不能据此要求所有知识库都先做知识图谱。

---

## 3. 当前成熟产品 / 开源实现提供的事实

### 3.1 Cherry Studio（官方文档，2026-09 核验）

官方知识库文档明确说明：

- Embedding Model 可以选择 **None**，先使用 BM25 keyword retrieval；
- Embedding 与 Reranker 都是可选的；
- 导入后应先检查 Parsed Text / Chunks；
- 提供 Retrieval Test；
- 官方建议保留 3–5 个现实测试问题，修改数据或设置后重复测试；
- 知识库可以在 Chat 中选择，也可以绑定到 Agent；
- 如果使用云端 Embedding/Rerank，其数据处理和费用取决于对应 Provider。

这直接支持培训中的两个关键 Demo：

1. **RAG 不等于向量检索**；
2. **先验证 Parsed Text / Chunk / Retrieval，再讨论生成回答**。

官方资料：
- https://cherryai.com/docs/en/knowledge-base/knowledge-base/
- https://cherryai.com/docs/en/

### 3.2 Open WebUI（官方文档，2026-09 核验）

当前官方 Knowledge/RAG 文档支持：

- Focused Retrieval（RAG）；
- Full Context；
- BM25 + Vector Hybrid Search；
- Cross-Encoder Reranking；
- Native Agentic Knowledge Tools；
- 可选 `kb_exec`，提供类 shell 的 `ls/tree/grep/cat` 等知识访问；
- 多种文档提取/OCR 引擎；
- 嵌套目录；
- REST API；
- 官方 `oikb` companion tool 将 Git、Confluence、S3、Jira、Slack、Notion 等源增量同步到 Knowledge Base。

`oikb` 使用 SHA-256 比较文件变化，只重新上传/重解析/重嵌入新增和修改内容，并处理删除。

这支持：

- **Source of Truth 与 Retrieval Index 分离**作为工程架构；
- 知识同步应工程化而不是人工重复上传；
- Agentic Retrieval 与 Hybrid Retrieval 可以组合，而不是互斥。

官方资料：
- https://docs.openwebui.com/features/workspace/knowledge/
- https://docs.openwebui.com/features/chat-conversations/rag/
- https://docs.openwebui.com/ecosystem/knowledge-base-sync/
- https://docs.openwebui.com/reference/env-configuration/

### 3.3 Azure AI Search（Microsoft 官方文档，2026-09 核验）

Microsoft 当前文档明确支持：

- Keyword/full-text 与 Vector 并行 Hybrid Query；
- 使用 Reciprocal Rank Fusion (RRF) 合并结果；
- 可叠加 Semantic Ranking；
- 官方说明产品编号、术语、日期、人名等场景往往更适合 keyword exact matching；
- 文档级 ACL / RBAC / Security Filter 在 query time 限制返回结果；
- 对无法使用原生 ACL 的系统，可以在索引中保存 principal/group 字段并在每次查询时执行 security trimming。

这强力支持：

> **权限过滤必须发生在模型看到检索结果之前。**

官方资料：
- https://learn.microsoft.com/azure/search/hybrid-search-overview
- https://learn.microsoft.com/azure/search/hybrid-search-how-to-query
- https://learn.microsoft.com/en-us/azure/search/search-document-level-access-overview
- https://learn.microsoft.com/en-us/azure/search/search-security-trimming-for-azure-search

### 3.4 RAGFlow（官方文档，2026-09 核验）

当前 RAGFlow 文档把 Ingestion 明确拆成：

`Parser → Transformer → Chunker → Indexer`

并支持：

- Full-text / Embedding / Hybrid；
- 结构化文档的 title-based / hierarchical chunking；
- Metadata 限制检索范围；
- Rerank；
- Citation；
- Empty Response（证据不足时不继续生成）；
- 将知识库 retrieval 暴露为 MCP tool。

这与我们把知识库拆成“知识源、解析、分块、索引、检索、生成、引用、评测”的分层思路高度一致。

官方资料：
- https://ragflow.io/docs/v0.27.2/category/ingestion-pipeline
- https://ragflow.io/docs/v0.27.2/configure_chunker_component
- https://ragflow.io/docs/v0.27.2/configure_indexer_component
- https://ragflow.io/docs/v0.27.2/chat_configuration
- https://ragflow.io/docs/mcp_overview

### 3.5 Microsoft GraphRAG

GraphRAG 官方项目将其定义为区别于 naive semantic-search RAG 的结构化、层次化方法，通过实体图、community hierarchy 与 community summaries 支持全局问题。

它说明企业知识体系不应假设：

> 所有问题都能靠“Top-K 相似 chunk”解决。

但其索引构建成本、复杂度和问题类型决定它更适合作为后续专项能力，而不是当前部门知识库 MVP 的默认组件。

官方资料：
- https://microsoft.github.io/graphrag/
- https://www.microsoft.com/en-us/research/publication/from-local-to-global-a-graph-rag-approach-to-query-focused-summarization/

---

## 4. 对当前讲义关键结论的审计

| 当前结论 | 审计结果 | 应怎样表述 |
|---|---|---|
| RAG 不等于向量数据库 | **保留** | 有 Cherry BM25、Open WebUI Hybrid、现代 RAG 研究/实现共同支持 |
| BM25 → Embedding → Rerank 的渐进建设方式 | **保留为工程策略** | BEIR 支持 BM25 是稳健 baseline；是否增加 Dense/Rerank必须由本部门测试集决定 |
| Hybrid 是共享知识库推荐方案 | **保留，但加“候选默认”** | Azure/Open WebUI/RAGFlow 均采用 Hybrid；不能替代本地 Benchmark |
| Full Context 适合短而关键文档 | **保留** | Open WebUI 官方提供该模式；RAG vs LC 研究支持按成本/效果路由 |
| Agentic Retrieval 适合复杂跨源任务 | **保留** | Self-RAG 和当前 Open WebUI/RAGFlow/Agent 工具形态支持“按需、多步检索” |
| Agentic Retrieval 应替代固定 RAG | **明确否定** | 高频、低延迟、稳定 FAQ 仍适合固定 Pipeline；Agentic 有额外 token、工具调用和不确定性 |
| Markdown 是最佳知识格式 | **降级为工程建议** | 它对 Git、Diff、heading chunk、grep 友好，但不是所有正式/复杂文档的唯一最佳格式 |
| PDF 不适合作为唯一机器知识源 | **改写** | 文本简单的 PDF 可以直接使用；扫描件、双栏、复杂表格/图示要验证解析质量并保留原件 |
| XLSX/CSV 不建议向量化 | **改写** | 精确聚合/筛选应优先 SQL/Python/表格工具；表头、字段说明、文本列和语义描述仍可进入检索索引 |
| 代码默认不必向量化 | **改写** | 标识符/结构导航优先 grep/LSP/Git；语义代码搜索可作为补充，是否建 embedding index 应实测 |
| Source 与 Index 分离 | **保留为架构原则** | Open WebUI oikb / Azure 等成熟实现均体现“源→索引→检索”分层；属于工程架构，不是学术定律 |
| ACL 必须在 Retrieval 前 | **强化** | Azure query-time ACL/security trimming 明确支持该模式 |
| 有 RAG 就不会幻觉 | **明确否定** | RAGTruth、ALCE 表明检索后仍会有 unsupported claims / citation 缺失 |
| GraphRAG 应作为部门知识库基础 | **暂不采用** | 只在“全局主题/跨实体/全库综合”问题证明普通 chunk RAG 不足后再评估 |

---

## 5. 因此，部门知识库需求应从问题而不是技术组件出发

第一阶段不要先问：

> 用哪个向量数据库？选哪个 Embedding？

先定义真实问题集合。

### 5.1 问题类型

至少覆盖：

1. **Exact Lookup**：型号、接口路径、错误码、制度编号、参数；
2. **Semantic Paraphrase**：用户问法与原文措辞不同；
3. **Multi-document Synthesis**：答案分布在多份文档；
4. **Version-sensitive**：新旧版本冲突；
5. **Structured Data**：表格数值、BOM、测试记录、指标统计；
6. **No-answer**：资料中根本没有答案；
7. **ACL-sensitive**：不同用户应看到不同内容；
8. **Global / Sensemaking**：全资料主线、共性问题、关系网络；
9. **Fresh / Live Data**：实时 metrics、数据库、服务状态。

问题类型决定 Retrieval：

| 问题 | 优先方式 |
|---|---|
| Exact Lookup | BM25 / Full-text / grep |
| Semantic Paraphrase | Dense / Hybrid |
| Multi-document | Hybrid + Rerank，必要时 Agentic |
| Version-sensitive | Metadata filter + source priority |
| Structured Data | SQL / Python / Data Tool，RAG 负责字段说明/口径 |
| No-answer | Retrieval threshold + grounded generation + no-answer policy |
| ACL-sensitive | Query-time ACL filter |
| Global/Sensemaking | 先测试 Agentic 多文档综合；必要时再考虑 GraphRAG |
| Fresh/Live | API / DB / Metrics Tool，不把静态 Vector Index 当实时事实源 |

---

## 6. 近期部门 PoC 应怎样验证

### 6.1 同一套真实资料

继续使用当前已经选定的真实 Qwen / model-metric / API 测试资料，不换成演示性质的虚构制度。

这样可以比较：

- Cherry Studio；
- Open WebUI；
- Agent；
- BM25；
- Dense；
- Hybrid；
- Rerank；
- Full Context；
- Agentic Retrieval。

### 6.2 测试集不要只有“两个感觉不错的问题”

培训现场 smoke test 可以保留 3–5 个问题，但部门 PoC 建议至少形成 **50–100 个真实问题**，并包含：

- 20%左右 Exact Lookup；
- 20%左右 Semantic Paraphrase；
- 15%左右跨文档；
- 10%左右版本/冲突；
- 10%左右结构化数据；
- 10%左右明确 No-answer；
- 若平台涉及权限，再加入 ACL 测试；
- 余量覆盖实际业务高频问法。

50–100 是本项目的工程起步建议，不是论文规定的统计阈值。

### 6.3 每个问题至少保存

- Question
- Question Type
- Expected Source
- Expected Passage / Section
- Expected Fact
- Should Answer
- Access Role
- Current Version
- Notes

### 6.4 分层指标

**Retrieval 层**

- Hit@K / Recall@K
- MRR 或 nDCG（需要更细排名比较时）
- Correct Source Rate
- Version Filter Accuracy
- ACL Leakage = 0

**Generation 层**

- Answer Correctness
- Faithfulness / Groundedness
- Citation Correctness
- Citation Completeness
- No-answer Accuracy

**工程层**

- TTFT / Total Latency
- Prompt / Retrieved Tokens
- Rerank Cost
- Index Build / Update Time
- 增量更新延迟

---

## 7. 当前还没有证据的部分

截至 2026-09-30，仓库目前 **还没有** 以下实测结果，因此讲义不能写成已经验证：

1. 同一批 Qwen 资料在 Cherry Studio 上 BM25 vs Dense 的真实召回对比；
2. 加 Reranker 后的提升幅度；
3. Open WebUI Hybrid Retrieval 在内网中文工程资料上的效果；
4. Open WebUI Agentic Knowledge / `kb_exec` 对内网 qwen3.6 的工具调用稳定性；
5. Full Context vs RAG 在内网 qwen3.6 上的质量、TTFT 与 token 成本；
6. 扫描 PDF / 复杂表格 / PPT 在当前选定 Parser 下的真实解析质量；
7. 版本冲突时 Metadata/source priority 是否有效；
8. “无答案不编”的回归测试；
9. 部门 ACL / 分组权限端到端测试；
10. 中文 Embedding / Reranker 的模型选型和资源成本。

因此当前成熟度应定义为：

> **知识库需求与架构：已有研究和成熟实现证据支撑；知识库技术路线：已有候选方案；部门内网效果：仍待实测。**

---

## 8. 建议的建设顺序（经证据核验后）

```text
真实问题集
→ 知识源盘点 / Source of Truth
→ 权限与版本模型
→ Parser 质量检查
→ 逻辑 Chunk + Metadata
→ BM25 baseline
→ Retrieval Benchmark
→ Dense / Embedding
→ Hybrid
→ Rerank
→ Grounded Answer + Citation
→ No-answer / Conflict / ACL Tests
→ Full Context 路由
→ Agentic Retrieval
→ 如全局问题仍不足，再评估 GraphRAG
```

这比：

```text
买向量数据库
→ 全量向量化
→ 接一个聊天框
```

更符合已有研究与成熟产品的共同经验。

---

## 9. 参考资料

### 学术

1. Lewis et al. 2020, Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks  
   https://arxiv.org/abs/2005.11401
2. Karpukhin et al. 2020, Dense Passage Retrieval for Open-Domain Question Answering  
   https://aclanthology.org/2020.emnlp-main.550/
3. Thakur et al. 2021, BEIR  
   https://arxiv.org/abs/2104.08663
4. Liu et al. 2024, Lost in the Middle  
   https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00638/119630/
5. Li et al. 2024, Retrieval Augmented Generation or Long-Context LLMs?  
   https://aclanthology.org/2024.emnlp-industry.66/
6. Asai et al. 2023, Self-RAG  
   https://arxiv.org/abs/2310.11511
7. Yan et al. 2024, Corrective Retrieval Augmented Generation  
   https://arxiv.org/abs/2401.15884
8. Es et al. 2023, RAGAS  
   https://arxiv.org/abs/2309.15217
9. Ru et al. 2024, RAGChecker  
   https://arxiv.org/abs/2408.08067
10. Niu et al. 2024, RAGTruth  
    https://aclanthology.org/2024.acl-long.585/
11. Gao et al. 2023, Enabling Large Language Models to Generate Text with Citations (ALCE)  
    https://aclanthology.org/2023.emnlp-main.398/
12. Gao et al. 2023/2024, Retrieval-Augmented Generation for Large Language Models: A Survey  
    https://arxiv.org/abs/2312.10997
13. Edge et al. 2024, From Local to Global: A Graph RAG Approach to Query-Focused Summarization  
    https://arxiv.org/abs/2404.16130
14. Hsieh et al. 2024, RULER: What's the Real Context Size of Your Long-Context Language Models?  
    https://arxiv.org/abs/2404.06654
15. Modarressi et al. 2025, NoLiMa: Long-Context Evaluation Beyond Literal Matching  
    https://proceedings.mlr.press/v267/modarressi25a.html
16. Bai et al. 2025, LongBench v2: Towards Deeper Understanding and Reasoning on Realistic Long-context Multitasks  
    https://aclanthology.org/2025.acl-long.183/
17. Du et al. 2025, Context Length Alone Hurts LLM Performance Despite Perfect Retrieval  
    https://aclanthology.org/2025.findings-emnlp.1264/
18. Hong et al. 2025, Context Rot: How Increasing Input Tokens Impacts LLM Performance（Chroma Technical Report）  
    https://www.trychroma.com/research/context-rot

### 官方实现

19. Cherry Studio Knowledge Base  
    https://cherryai.com/docs/en/knowledge-base/knowledge-base/
20. Open WebUI Knowledge  
    https://docs.openwebui.com/features/workspace/knowledge/
21. Open WebUI RAG  
    https://docs.openwebui.com/features/chat-conversations/rag/
22. Open WebUI Knowledge Base Sync (oikb)  
    https://docs.openwebui.com/ecosystem/knowledge-base-sync/
23. Azure AI Search Hybrid Search  
    https://learn.microsoft.com/azure/search/hybrid-search-overview
24. Azure AI Search Document-Level Access Control  
    https://learn.microsoft.com/en-us/azure/search/search-document-level-access-overview
25. RAGFlow Ingestion Pipeline / Retrieval Configuration  
    https://ragflow.io/docs/v0.27.2/category/ingestion-pipeline
26. Microsoft GraphRAG  
    https://microsoft.github.io/graphrag/

---

## 10. 培训中建议保留的一句话

> **知识库建设不是“把文件向量化”，而是把权威知识源、解析、版本、权限、检索、引用和评测做成一个可持续的知识访问系统。**

