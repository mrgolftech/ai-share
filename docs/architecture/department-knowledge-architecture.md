# 部门知识库架构：不要把知识库做成某个客户端里的向量库

> 用途：AI 大模型与 Agent 工程实践培训 / 部门知识体系设计
> 日期：2026-09-29
> 核心问题：Cherry Studio、Open WebUI、Coding Agent 的检索方式不同，部门知识应该怎样组织，才能同时服务 Chat、RAG 和 Agent？

---

## 证据与验证状态

本架构于 2026-09-30 完成一次专项证据核验。设计依据分为：学术检索研究、成熟产品/开源实现、本项目工程建议和后续内网实测四层。完整证据矩阵见：

`docs/references/knowledge-base-rag-evidence-2026-09.md`

需要特别说明：

> **本文件定义的是部门知识架构候选基线，不代表 BM25 / Dense / Hybrid / Rerank / Agentic Retrieval 的具体组合已经在部门内网语料上证明最优。**

最终技术参数必须由真实问题集、Retrieval Benchmark、no-answer、版本冲突和 ACL 测试决定。

---

# 1. 核心判断

部门知识库不应该定义为：

> 在 Cherry Studio / Open WebUI 中上传一批文件，然后生成一个向量库。

更稳定的定义是：

> **部门知识库 = 权威知识源 + 可重建索引 + 检索接口 + 权限 + 评测 + 多种使用入口。**

因此必须区分：

~~~text
知识本体 / Source of Truth
        ↓
解析与标准化
        ↓
检索索引
        ↓
Retrieval Tools / API
        ↓
Open WebUI / Cherry / Agent
~~~

其中：

- 原始文档、Git Repo、制度库、项目资料才是知识资产；
- BM25 Index、Vector Index 是派生资产；
- Rerank 是查询时的排序能力；
- Open WebUI / Cherry Studio / Coding Agent 是消费知识的客户端或 Harness；
- 换客户端不应该意味着重新建设知识本体。

---

# 2. 为什么工具会反过来影响知识库长什么样

不同工具默认给模型的 Retrieval 能力不同。

## Cherry Studio

更偏桌面知识库：

- File / Note / Folder / Link；
- Parser / Chunk；
- BM25；
- 可选 Embedding / Vector Index；
- 可选 Rerank；
- Retrieval Test；
- Knowledge 可绑定 Chat / Agent。

因此 Cherry 适合：

> **个人资料库、专题资料包、快速试验和检索参数调优。**

## Open WebUI

更偏集中式 Knowledge Service：

- 多用户；
- Knowledge Base；
- BM25 + Vector + Rerank；
- Native Knowledge Tools；
- grep / view_file；
- kb_exec 文件系统式访问；
- 本地目录增量同步；
- Git / Confluence / S3 等外部知识源同步；
- RBAC / Group / per-resource ACL；
- API。

因此 Open WebUI 更适合：

> **部门统一知识入口、共享 Knowledge Service、权限控制和同步。**

## Coding / General Agent

例如 Codex / Claude Code / OpenCode / Pi / DSH / Hermes：

通常更习惯直接面对：

- File Tree；
- grep / ripgrep；
- glob / find；
- read；
- LSP；
- Git；
- Shell；
- Web Search；
- MCP / API；
- 必要时再使用 Semantic Search / Vector Search。

因此它们适合：

> **直接操作活的 Workspace / Repository / 数据源，而不是必须把所有内容预先切 Chunk 进入向量库。**

---

# 3. 这意味着部门知识至少有五种形态

## 3.1 原始文件 / 文档树

例如：

- Markdown；
- PDF / DOCX / PPTX；
- 规范；
- 项目文档；
- 测试报告；
- 设计记录。

适合：

- Open WebUI 同步；
- Cherry 导入；
- Agent grep/read；
- 后续向量化。

这是最基础、最可迁移的知识形态。

## 3.2 Git Repository

例如：

- 代码；
- README；
- AGENTS.md；
- ADR；
- API Spec；
- Test；
- CI；
- Release Notes。

对 Coding Agent 来说：

> **Git Repo 本身就是一个高度结构化的知识库。**

优先检索：

~~~text
tree / glob
→ rg / grep
→ read
→ LSP / references
→ Git history
~~~

通常不需要先把整个 Repo 做成 Vector DB。

## 3.3 全文 / BM25 Index

适合：

- 型号；
- 错误码；
- 标准号；
- API；
- 人名；
- 项目名；
- 精确术语。

优点：

- 快；
- 可解释；
- 不需要 Embedding；
- 对技术资料中的精确字符串很强。

## 3.4 Vector Index

适合：

- 同义表达；
- 口语问题；
- 主题相近但措辞不同；
- 大量自然语言文档。

它是：

> **语义检索索引。**

它不应该成为知识本体，因为：

- 可以重新生成；
- 更换 Embedding Model 后通常要重建；
- 不利于直接人工审计；
- 向量本身无法替代原文。

## 3.5 结构化系统 / API

例如：

- 数据库；
- Jira / 禅道；
- CMDB；
- GitHub；
- 监控；
- 资产系统；
- 实验数据；
- model-metric；
- 业务系统。

不要为了统一成 RAG，就把所有结构化数据导出成 PDF 再向量化。

更合理：

~~~text
Agent
→ SQL / API / MCP
→ 获取实时结构化数据
~~~

然后再由模型分析。

---

# 4. 部门知识架构建议：Source 与 Index 分离

推荐：

~~~text
┌────────────────────────────────────────────┐
│         Layer 1: Source of Truth           │
│                                            │
│ Git / 文件服务器 / SharePoint / Confluence │
│ S3 / 数据库 / API / 项目系统 / Wiki        │
└───────────────────┬────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│      Layer 2: Parse / Normalize / Metadata │
│                                            │
│ 文本提取 / OCR / Chunk / Path / Version    │
│ Owner / Project / Classification / ACL     │
└───────────────────┬────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│          Layer 3: Retrieval Index          │
│                                            │
│ BM25 / Full-text / Vector / Metadata Index │
└───────────────────┬────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│   Layer 4: Retrieval & Context Control      │
│                                            │
│ Candidate Recall / Rerank / ACL / Version  │
│ Deduplicate / Threshold / Evidence Budget  │
│ Context Selection / Context Packing        │
└───────────────────┬────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│           Layer 5: Knowledge Tools         │
│                                            │
│ search / grep / read / query / SQL / API  │
│ MCP / Web Search / Git / LSP              │
└───────────────────┬────────────────────────┘
                    ↓
┌────────────────────────────────────────────┐
│           Layer 6: Consumption             │
│                                            │
│ Open WebUI / Cherry / Coding Agent / App   │
└────────────────────────────────────────────┘
~~~

原则：

> **Source 是长期资产；Index 是可重建缓存；Tool 是访问方式；Client 是可替换入口。**

---

# 5. Open WebUI 在部门架构中的位置

建议定位：

> **共享 Knowledge Service + 部门统一 AI Portal。**

理由：

1. 支持 Knowledge Base；
2. 支持 Hybrid Search；
3. 支持 Agentic Knowledge Tools；
4. 支持 Full Context；
5. 支持目录结构；
6. 支持增量目录同步；
7. 官方 oikb 可同步 Git / Confluence / S3 等外部 Source；
8. 支持 Group / RBAC / Knowledge Base ACL；
9. 可通过 API 被其他应用使用。

因此可以采用：

~~~text
Git / Wiki / 文件库
       ↓
   增量同步
       ↓
Open WebUI Knowledge
       ↓
BM25 + Vector + Rerank
       ↓
Chat / Workspace Model / Native Agent
~~~

但必须注意：

> **Open WebUI Knowledge 仍然应该是可重建服务层，不要成为唯一原始资料保存位置。**

原始知识仍保留在：

- Git；
- 文档管理系统；
- 文件服务器；
- 业务系统。

---

# 6. Cherry Studio 在部门架构中的位置

建议定位：

> **个人 Knowledge Workspace / Edge Knowledge Cache。**

适合工程师：

- 导入当前项目资料；
- 建一个专题 KB；
- 测 BM25；
- 测 Embedding；
- 测 Rerank；
- 把 KB 绑定到个人 Assistant / Agent；
- 临时研究和总结。

例如：

~~~text
部门中央资料
      ↓
工程师选择当前任务相关资料
      ↓
Cherry Personal KB
      ↓
BM25 / Vector
      ↓
个人 Assistant / Agent
~~~

不建议把部门唯一知识库只放在每个人的 Cherry 本地实例。

原因：

- 每个人副本不同；
- 更新难统一；
- 权限与共享不是其最核心的部门治理能力；
- 容易产生我的知识库和官方知识漂移；
- 云 Embedding / Rerank 时还要单独考虑资料是否会发往 Provider。

因此：

> **Cherry 适合个人使用层，不适合作为部门唯一 Source of Truth。**

---

# 7. Agent 在部门知识架构中的位置

Agent 的价值在于：

> **它可以同时访问多种知识形态，而不是只能查一个 RAG Index。**

例如用户问：

> 这个 API 最近为什么变慢，代码里有没有相关改动？

一个真正的工程 Agent 可以：

~~~text
1. 搜 model-metric 监控数据
2. 查 API 测试报告
3. grep Git Repo
4. 看 Git Diff / Commit
5. 查部署配置
6. 必要时再查部门文档 KB
7. 综合证据
~~~

它访问的可能同时包括：

- Open WebUI Knowledge；
- Git；
- 文件；
- SQL；
- Metrics API；
- Web；
- MCP。

这就是部门知识体系从：

> **一个知识库**

升级为：

> **一个 Knowledge Fabric / Knowledge Access Layer。**

---

# 8. Pipeline RAG 与 Agentic Retrieval 在部门知识库中的分工

## 8.1 Pipeline RAG

适合：

- 高频制度问答；
- FAQ；
- 产品手册；
- 标准规范；
- 答案通常来自一两段文档。

工作方式：

~~~text
Question
→ Hybrid Retrieval
→ Rerank
→ Top-K
→ LLM
~~~

优势：

- 快；
- 稳定；
- 易测；
- 成本低；
- 容易控制引用。

## 8.2 Agentic Retrieval

适合：

- 跨文档研究；
- 跨代码 + 文档；
- 多跳问题；
- 故障分析；
- 项目调研；
- 需要查询多个系统的数据。

工作方式：

~~~text
Question
→ Search
→ Read
→ 判断
→ Search Another Source
→ Compare
→ Query API
→ Read More
→ Answer
~~~

优势：

- 灵活；
- 能跨源；
- 能根据中间结果改变检索策略。

代价：

- 更多 Token；
- 更多工具调用；
- 更慢；
- 更依赖模型能力；
- 更难复现。

因此：

> **部门知识库不应该全部 Agentic，也不应该全部向量 RAG。**

正确方式是按任务路由。

---

# 9. 推荐的 Retrieval Strategy

## 9.1 先明确：知识库有“外部检索”和“上下文内利用”两道关

知识库系统不能只优化 Retriever。

更完整的链路是：

~~~text
Question
  ↓
External Retrieval
  ↓
Candidate Chunks
  ↓
Rerank / Filter / ACL / Version
  ↓
Context Selection / Evidence Budget
  ↓
LLM Context
  ↓
In-context Retrieval / Context Utilization
  ↓
Answer
~~~

因此必须区分：

- **External Retrieval Recall**：正确资料是否被搜索系统召回；
- **In-context Retrieval / Context Utilization**：正确资料进入 Prompt 后，模型是否能在长上下文、干扰项和多证据条件下稳定使用。

TACL 2024 的 Lost in the Middle、RULER 2024、ICML 2025 NoLiMa、ACL 2025 LongBench v2，以及 Findings of EMNLP 2025 的 “Context Length Alone Hurts LLM Performance Despite Perfect Retrieval” 都说明：

> **标称 Context Window 不能直接等同于有效知识容量；即使相关证据已经进入 Context，输入继续变长仍可能损害任务表现。**

因此架构中必须把：

> **Context Selection / Evidence Budget**

当成独立的一层，而不是简单执行：

> Search → 所有结果 → Prompt。

详细证据见：

`docs/references/knowledge-base-rag-evidence-2026-09.md`

## 9.2 共享知识库的候选检索思路

部门技术资料通常同时包含：

- 自然语言；
- 型号；
- API；
- 错误码；
- 标准号；
- 表格；
- 代码；
- 日志。

因此推荐默认思路：

~~~text
          Query
         /     \
        /       \
     BM25      Vector
        \       /
         \     /
       Candidate Set
             ↓
           Rerank
             ↓
 ACL / Version / Deduplicate
             ↓
      Evidence Budget
             ↓
       Selected Context
~~~

即：

> **Hybrid Retrieval 作为共享文档知识库的主力候选。**

但这里的目标不是把 Hybrid 召回的结果尽可能多地送给模型，而是：

> **先扩大 Candidate Recall，再通过 Rerank / Metadata / Version / 去重压缩为足够的小证据集。**

Top-K 应被理解成 **Recall 与 Context Pollution 的权衡参数**，不能固定认为越大越好。

然后复杂任务：

~~~text
Hybrid Search
     +
grep / read
     +
API / SQL / Git
     ↓
Agentic Retrieval
~~~

---

# 10. 不同知识类型，不要使用同一种检索方式

| 知识类型 | 推荐 Source | 第一检索方式 | 第二检索方式 | 是否建议 Vector |
|---|---|---|---|---|
| 制度 / 规范 / 手册 | 文档库 / Git | Hybrid RAG | Agentic Read | 建议 |
| 项目 Markdown / 设计记录 | Git | BM25 / grep | Vector | 可选 |
| 源代码 | Git Repo | rg / LSP / glob | Semantic Code Search | 默认不必 |
| API Spec | Git / OpenAPI | grep / structured parse | Vector | 可选 |
| 错误日志 | 日志平台 / 文件 | Exact / grep | Agent分析 | 通常不需要 |
| 测试与性能数据 | DB / CSV / Metrics API | SQL / API | Agent分析 | 不作为主方法 |
| FAQ / 制度问答 | 文档库 | Hybrid + Rerank | - | 建议 |
| Wiki / 长文档 | Wiki | Hybrid | Agentic Retrieval | 建议 |
| 实时业务状态 | API / DB | API / SQL | Agent | 不建议先向量化 |
| 个人临时研究资料 | Cherry Local KB | BM25 起步 | Vector / Rerank | 按需 |

---

# 11. 权限必须跟着知识走，而不是只跟着 Chat 走

部门知识库最容易忽略的是：

> **用户能不能看到答案，取决于检索层是否正确执行了权限，而不只是模型界面有没有登录。**

Open WebUI 当前支持：

- Group；
- per-resource ACL；
- Knowledge Base Read / Write；
- 模型绑定 Knowledge 时仍检查具体用户是否具有底层 KB 权限。

这适合部门集中部署。

设计原则：

~~~text
User Identity
   ↓
Knowledge ACL
   ↓
Retrieval
   ↓
只有有权限的结果进入 Context
~~~

而不是：

~~~text
先把所有知识搜出来
↓
再指望 Prompt 告诉模型不要泄露
~~~

后者不是真正的权限控制。

对于 Cherry：

> 个人本地数据并不意味着所有计算都留在本机。

如果使用云端 Chat / Embedding / Rerank / Search Provider，相应内容仍可能发送给 Provider。

因此内部资料应优先使用：

- 内网 Embedding；
- 内网 Rerank；
- 内网 LLM；
- 内网 Search / API；
- 明确的数据分级与访问边界。

---

# 12. 知识库建设真正应该建设什么

不要只建设：

- 一个 Vector DB；
- 一批 Embedding。

真正应该沉淀：

## 12.1 Source

- 权威原文；
- Owner；
- 版本；
- 更新时间；
- 项目；
- 数据分级；
- 有效期。

## 12.2 Metadata

例如：

~~~text
project=ai-platform
type=api-spec
owner=platform-team
version=2.1
classification=internal
updated_at=2026-09-29
~~~

Metadata 对：

- 权限；
- Filter；
- 搜索；
- 引用；
- 版本判断；

都非常重要。

## 12.3 Retrieval Test Set

每一个重要 KB 至少保留：

- 10～50 个真实问题；
- 正确来源；
- 期望命中资料；
- 是否允许无答案。

例如：

~~~text
Question
Expected Source
Expected Fact
Should Retrieve?
~~~

更换：

- Parser；
- Chunk；
- Embedding；
- Rerank；
- Top-K；

以后重新跑。

否则：

> **知识库能打开不等于检索质量可靠。**

## 12.4 Citation / Provenance

回答最好能够回到：

- 文件；
- 路径；
- 页面；
- 行号；
- URL；
- Commit；
- Version。

这比单纯模型说答案来自知识库可靠得多。

---

# 13. 对部门的推荐最终形态

推荐目标不是：

~~~text
所有资料
  ↓
一个巨大的向量库
  ↓
所有人问
~~~

更推荐：

~~~text
                ┌─────────────────────┐
                │ 权威 Source of Truth │
                │ Git / Wiki / DMS/API │
                └─────────┬───────────┘
                          ↓
              Parse / Metadata / ACL
                          ↓
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
     BM25 Index       Vector Index      API / SQL
        └──────────┬──────┘                 │
                   ↓                        │
                 Rerank                     │
                   └──────────┬─────────────┘
                              ↓
                     Knowledge Tool Layer
             search / grep / read / query / MCP
                              ↓
       ┌──────────────────────┼──────────────────────┐
       ↓                      ↓                      ↓
  Open WebUI              Cherry Studio          Agent
  部门统一入口             个人工作台          工程/研究任务
~~~

其中：

- Open WebUI：共享、权限、统一入口；
- Cherry：个人专题知识与试验；
- Agent：跨文件 / Git / API / 数据源的主动检索与执行；
- Source of Truth：独立存在，不与任何客户端绑定。

---

# 14. 对培训应该留下的核心观点

第一：

> **知识库不是 Vector DB；Vector DB 是知识检索的一种索引。**

第二：

> **不同工具的 Retrieval 能力不同，所以同一批知识需要保留可被多种方式访问的原始形态。**

第三：

> **Cherry 适合个人 Knowledge Workspace；Open WebUI 更适合部门共享 Knowledge Service；Agent 擅长直接搜索 Workspace 和多个真实系统。**

第四：

> **简单高频问答使用 Pipeline RAG；复杂、多源、多跳任务使用 Agentic Retrieval。**

第五：

> **真正可复用的部门知识资产是 Source + Metadata + ACL + Retrieval Test，而不是某个客户端生成的一批 Embedding。**

第六：

> **Context Window 是输入容量上限，不是有效知识容量保证；知识库最终要管理的是 Evidence Budget，而不是把检索结果尽可能多地塞给模型。**

---

# 15. 当前官方参考

## Open WebUI

- Knowledge: https://docs.openwebui.com/features/workspace/knowledge/
- RAG: https://docs.openwebui.com/features/chat-conversations/rag/
- Agentic Search: https://docs.openwebui.com/features/chat-conversations/web-search/agentic-search/
- Knowledge Base Sync: https://docs.openwebui.com/ecosystem/knowledge-base-sync/
- RBAC / Groups: https://docs.openwebui.com/features/authentication-access/rbac/groups/

## Cherry Studio

- Knowledge Base: https://cherryai.com/docs/en/knowledge-base/knowledge-base/
- Agent: https://cherryai.com/docs/en/advanced-basic/agent/
- Data / Privacy: https://cherryai.com/docs/en/mobile/data-privacy/
