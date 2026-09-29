# 培训讲义：部门知识库怎么设计、怎么建、怎么用

> 模块：Chat → Knowledge → RAG → Agent
> 日期：2026-09-29
> 面向对象：部门技术人员、知识库建设人员、AI 平台与应用建设人员
> 核心问题：在 Open WebUI、Cherry Studio 和各类 Agent 并存的情况下，部门知识资产应该采用什么形式、如何检索、哪些需要向量化，以及怎样保证长期复用和治理。

---

# 一、先重新定义部门知识库

知识库不应该等同于：

> 上传一批 PDF → 做 Embedding → 存入 Vector DB。

更合理的定义是：

> **部门知识库是一套让模型和 Agent 可靠访问部门知识资产的体系。**

它至少包含：

~~~text
权威知识源
  ↓
文档与数据标准
  ↓
解析 / OCR / Metadata
  ↓
全文 / BM25 / Vector / 结构化索引
  ↓
Search / Read / API / MCP
  ↓
Open WebUI / Cherry / Agent
  ↓
引用 / 权限 / 评测 / 更新
~~~

培训统一强调：

> **知识本体与检索索引必须分离。**

- 原始文件、Git Repo、Wiki、数据库和业务系统是知识资产；
- BM25 Index、Vector Index 是可以重新生成的派生索引；
- Embedding 不是知识本身；
- Cherry Studio、Open WebUI、Codex/OpenCode/Hermes 等是知识消费入口；
- 将来换客户端，不应该重新建设知识本体。

---

# 二、先盘点知识资产类型

不同资产不能用同一种方式处理。

| 资产类型 | 典型内容 | 推荐权威载体 | 主要检索方式 | 是否建议向量化 |
|---|---|---|---|---|
| 制度 / 流程 / 标准 / 手册 | 管理制度、规范、产品手册 | DMS / Wiki / Git + 原始 Office/PDF | Hybrid RAG | 建议 |
| 技术设计文档 | 方案、架构、测试报告 | Git / DMS，优先保留 Markdown/可解析文档 | BM25 + Vector | 建议或可选 |
| 项目 Markdown / ADR | README、方案决策、会议结论 | Git | grep/BM25 + Vector | 可选 |
| 源代码 | Python、JS、C/C++、配置 | Git Repo | rg/grep/LSP/Git | 默认不必 |
| API / 协议 | OpenAPI、JSON Schema、接口文档 | Git + YAML/JSON | 结构化解析 + grep | 可选 |
| 表格数据 | Excel、CSV、测试记录、BOM | XLSX/CSV/数据库 | 表格查询 / Python / SQL | 一般不作为主方法 |
| 实时数据 | Metrics、监控、业务状态 | API / DB / 时序数据库 | API / SQL | 不建议 |
| 日志 | 服务日志、测试日志 | 日志平台 / 文件 | Exact / Regex / grep | 通常不需要 |
| FAQ / 固定问答 | 常见问题 | Markdown / Wiki / Q&A | BM25 + Vector + Rerank | 建议 |
| 图片 / 图纸 / 截图 | 架构图、原理图、测试截图 | 原图 + 说明文字 | OCR/VLM + Metadata | 文字说明可向量化 |
| 音视频 | 培训录屏、会议音频 | 原文件 + Transcript | Transcript 检索 | 转写文本建议 |
| Issue / 工单 / PR | 问题、过程、解决方案 | GitHub/Jira 等原系统 | API / Search | 按需 |
| 个人临时资料 | 调研文献、项目附件 | Cherry 本地 KB / 工作目录 | BM25 起步 | 按需 |

核心原则：

> **不要为了统一成 RAG，把所有东西都转成 PDF 再向量化。**

结构化数据保持结构化，代码保持 Git 结构，实时数据通过 API 查询。

---

# 三、知识资产应该采用什么文件形式

建议采用双层资产：

~~~text
Original
PDF / DOCX / PPTX / XLSX / 图片
          +
Machine-readable
Markdown / TXT / CSV / YAML / JSON
~~~

原始文件用于：

- 审计；
- 签批；
- 保留版式；
- 人工阅读。

机器可读版本用于：

- grep；
- Diff；
- Git；
- Agent Read；
- Chunk；
- RAG；
- 自动评测。

不要只保存转换后的文本，也不要只保存扫描 PDF。

---

# 四、推荐文档格式规范

## 4.1 Markdown：技术知识优先格式

技术方案、API 说明、操作手册、FAQ、设计记录、项目规则等优先推荐 Markdown。

原因：

- 纯文本；
- Git 友好；
- Diff 友好；
- 标题层级明确；
- grep / Agent 可直接读取；
- RAG 容易按 Heading 切分；
- 不依赖特定客户端。

建议至少包含：

- 标题；
- Owner；
- Version；
- Updated At；
- Classification；
- Source；
- 正文层级；
- 变更记录。

## 4.2 PDF：适合作为发布版，不适合作为唯一机器知识源

文本型 PDF 一般可以解析。

扫描型 PDF 必须：

> OCR → 检查抽取结果 → 再进入索引。

重点检查：

- 页眉页脚污染；
- 双栏阅读顺序；
- 表格错位；
- 公式；
- 图片中的文字；
- 中文 OCR；
- 页码与章节关系。

如果 Parsed Text 本身就是错的：

> **Embedding 和更强的 LLM 都无法补回已经丢失的事实。**

Open WebUI 当前提供多种 Document Extraction / OCR Engine；Cherry 也要求在 Retrieval Test 前检查 Parsed Text 和 Chunks。

## 4.3 DOCX / PPTX

可以保留为权威原始文件，但重要技术资料建议同步生成 Markdown / Plain Text 镜像。

PPT 尤其要注意：

- 单纯抽字会丢失图形关系；
- 箭头、流程、层级可能消失；
- 关键页面需要补充标题、Notes 或图片说明。

## 4.4 XLSX / CSV

大量数值表格不建议直接当普通文本做 Vector RAG。

更推荐：

~~~text
XLSX / CSV
   ↓
Python / SQL / Data Tool
   ↓
Agent 分析
~~~

另外维护数据字典和指标口径 Markdown 供 RAG 查询。

## 4.5 图片 / 原理图 / 架构图

关键图片至少附带：

- 标题；
- 来源；
- 版本；
- 文字说明；
- 图中关键结论。

OCR / VLM 生成的描述属于派生知识，不能替代原图。

---

# 五、文件名、目录和 Metadata 也是知识设计

不建议出现：

~~~text
最终版.docx
最终版2.docx
最新最终版.pdf
新建文档3.docx
~~~

建议：

~~~text
qwen-api-compatibility-2026-09.md
vpn-performance-test-v2.1.md
rk3588-six-camera-interface-v1.3.pdf
~~~

目录建议体现：

~~~text
domain/
  project/
    docs/
    specs/
    decisions/
    tests/
    data/
    references/
~~~

对 Agent 来说：

> **清晰目录和文件名本身就是低成本 Retrieval Index。**

Metadata 建议至少记录：

- title；
- owner；
- project；
- document_type；
- version；
- created_at；
- updated_at；
- source；
- classification；
- status；
- effective_from / expires_at；
- tags；
- supersedes / superseded_by。

Metadata 解决的是：

- 哪份是最新版；
- 谁负责更新；
- 哪些已失效；
- 哪些人能看；
- 答案应该引用哪一版。

---

# 六、RAG 和向量化的关系

统一公式：

> **RAG = Retrieval + Context Augmentation + Generation。**

因此：

> **RAG 不等于 Vector Search。**

Retrieval 可以是：

- BM25；
- Full-text；
- Vector；
- Hybrid；
- grep；
- SQL；
- API；
- Search Engine。

向量化只是：

> **给文档建立语义相似度索引。**

所以下列都属于 RAG：

~~~text
BM25 → Context → LLM
Vector → Context → LLM
BM25 + Vector + Rerank → Context → LLM
~~~

---

# 七、哪些知识需要向量化

## 建议向量化

适合：

- 制度；
- 规范；
- 长技术文档；
- Wiki；
- 产品手册；
- FAQ；
- 大量自然语言资料；
- 用户问法与原文措辞差异大的内容。

例如：

~~~text
文档：
长上下文会显著增加 TTFT。

用户：
为什么材料一多，模型半天才开始出字？
~~~

Vector Search 很有价值。

## 可以不向量化

典型：

- 代码；
- 配置；
- API Path；
- 错误码；
- 型号；
- 日志；
- 标准编号；
- 精确术语；
- 很短且可以直接放进 Context 的文档。

## 不建议主要依赖向量化

- 实时 Metrics；
- 时序数据；
- BOM；
-数据库记录；
-当前服务器状态；
-实时资产状态。

这类数据应该直接通过 API / SQL / Tool 获取。

---

# 八、BM25、Embedding、Rerank 的职责

BM25 回答：

> 字面上像不像？

Embedding 回答：

> 意思上像不像？

Rerank 回答：

> 已经召回的候选里谁最相关？

推荐共享文档知识库采用：

~~~text
         Query
        /     \
     BM25    Vector
        \     /
      Candidates
          ↓
        Rerank
          ↓
        Top-K
          ↓
         LLM
~~~

也就是：

> **Hybrid Retrieval。**

但建设顺序建议：

~~~text
解析
→ Chunk
→ BM25
→ Retrieval Test
→ 再加 Embedding
→ 再判断是否需要 Rerank
~~~

不要把所有组件一次性叠上去，否则失败时无法定位问题。

---

# 九、Chunk 怎么设计

Chunk 太小：

- 上下文断裂；
- 表头和数据分开；
- 标题和正文分开。

Chunk 太大：

- 检索不精确；
- Token 浪费；
- 无关内容进入 Context。

优先按文档逻辑结构切分：

~~~text
Document
→ Chapter
→ Section
→ Paragraph / Logical Block
~~~

而不是只按固定字符数机械切。

特别注意：

- Heading 应随 Chunk 保留；
- 表格不要把表头和数据拆开；
- 操作步骤不要拆掉前置条件；
- API 参数表要保留 Endpoint / Method / 参数关系。

因此：

> **先检查 Parsed Text 和 Chunk，再讨论 Embedding 模型。**

---

# 十、Cherry Studio 中如何使用部门知识

Cherry 当前官方 Knowledge Base 支持：

- File；
- Note；
- Folder；
- Link；
- Parsed Text / Chunk 检查；
- Retrieval Test；
- Embedding 可选；
- Embedding=None 时使用 BM25；
- Reranker 可选；
- Chat 选择 Knowledge；
- Agent 绑定 Knowledge。

建议定位：

> **个人 Knowledge Workspace。**

典型模式：

~~~text
部门权威 Source
       ↓
选择当前任务相关资料
       ↓
Cherry Personal KB
       ↓
先 BM25
       ↓
需要语义时再 Embedding
       ↓
按需 Rerank
       ↓
Assistant / Agent
~~~

适合：

- 个人专题研究；
- 项目资料包；
- 临时文档问答；
- Retrieval 调试；
- 个人助手。

不建议把部门唯一知识库只存在个人 Cherry 实例，因为容易产生：

- 多份副本；
- 版本漂移；
- 更新不同步；
- 权限治理困难。

---

# 十一、Open WebUI 中如何使用部门知识

Open WebUI 当前更适合：

> **部门共享 Knowledge Service / AI Portal。**

当前官方能力包括：

- Knowledge Base；
- Focused Retrieval；
- Full Context；
- BM25 + Vector Hybrid Search；
- Cross-Encoder Rerank；
- Agentic Knowledge Tools；
- query / grep / view_file；
- kb_exec；
- Nested Directory；
- Incremental Sync；
- REST API；
- Group / RBAC / Knowledge ACL。

官方 oikb 可以把 Git、Local Folder、Confluence、S3、Jira、Slack、Notion 等知识源增量同步到 Open WebUI Knowledge Base。

推荐：

~~~text
Git / Wiki / 文件库
       ↓
自动 / 增量同步
       ↓
Open WebUI Shared KB
       ↓
Hybrid Retrieval
       ↓
Chat / Workspace Model / Native Agent
~~~

但：

> **Open WebUI Knowledge 仍然是服务层，不应该成为唯一 Source of Truth。**

---

# 十二、Agent 中的知识库是什么形式

Coding / General Agent 的知识观不同于传统 Chat 知识库。

Agent 可以直接访问：

- Workspace；
- Git Repo；
- Markdown；
- 代码；
- 配置；
- 日志；
- 数据库；
- API；
- MCP；
- Web；
- 共享 RAG Service。

例如：

~~~text
用户：
为什么这个服务最近变慢？

Agent：
1. grep 配置
2. read API 测试记录
3. 查询 metrics
4. 看 Git 最近提交
5. 搜共享 KB 的部署说明
6. 综合证据
~~~

所以对 Agent：

> **文件树、Git、API、数据库本身就是知识源。**

Agent 使用 Agentic Retrieval 主动决定：

- 什么时候搜；
- 搜哪个 Source；
- 用 grep 还是 Semantic Search；
- 是否继续搜索；
- 什么时候证据足够。

---

# 十三、Pipeline RAG 与 Agentic Retrieval 的分工

## Pipeline RAG

~~~text
Question
→ 固定 Retrieval
→ Top-K
→ Context
→ LLM
~~~

适合：

- 制度问答；
- FAQ；
- 手册查询；
- 高并发；
- 低延迟；
- 稳定引用。

## Agentic Retrieval

~~~text
Question
→ Agent
→ Search
→ Read
→ 判断
→ Search Again
→ Query API
→ Read Another Source
→ Answer
~~~

适合：

- 故障分析；
- 跨文档问题；
- 多跳问题；
- 调研；
- 代码 + 文档 + 数据联合分析。

推荐路由：

~~~text
高频简单问答
→ Pipeline Hybrid RAG

复杂研究 / 工程任务
→ Agentic Retrieval

实时结构化数据
→ API / SQL

代码
→ Git / grep / LSP
~~~

---

# 十四、不同工具分别适合哪些知识库形式

| 工具 | 最适合的知识形态 | 主要 Retrieval | 不应承担的角色 |
|---|---|---|---|
| Cherry Studio | 个人专题文件、Notes、链接、项目资料包 | BM25 → Vector → Rerank，Chat/Agent 使用 | 部门唯一权威知识源 |
| Open WebUI | 部门共享文档、Wiki/Git 同步资料、公共知识集 | Hybrid RAG + ACL + Agentic Tools | 原始文档唯一保存地 |
| Codex / OpenCode / Claude Code 等 | Git Repo、Workspace、代码、配置、项目规则 | grep/read/LSP/Git + Agentic Retrieval | 把所有数据都预先向量化 |
| Hermes 等通用 Agent | 文件、Web、Session、API、MCP、多知识源 | 多源 Agentic Retrieval | 高频固定 FAQ 唯一入口 |
| 业务应用 | 稳定、边界明确的业务知识 | API + 固定 RAG Pipeline | 无约束通用搜索 |

---

# 十五、Full Context 什么时候比 RAG 更合适

如果资料很短，而且每次都应该完整看到，例如：

- 编码规范；
- 小型术语表；
- 一页项目规则；
- 短 System Spec；

可以直接注入全文。

优点：

- 不会因 Retrieval 漏掉关键内容；
- 实现简单。

缺点：

- 每轮消耗 Token；
- 大资料成本高；
- Context 容易膨胀。

Open WebUI 当前正式提供 Full Context Mode，与 Focused Retrieval 并列。

建议：

> **短而关键 → Full Context；大而稀疏使用 → Retrieval。**

---

# 十六、知识更新和版本管理

知识库一定会过期。

必须回答：

- 谁更新；
- 多久同步；
- 旧版如何失效；
- 是否保留历史；
- 向量什么时候重建；
- 新旧内容冲突怎么办。

建议流程：

~~~text
Source Change
   ↓
Git / DMS Version
   ↓
Incremental Sync
   ↓
Re-Parse
   ↓
Re-Index
   ↓
Retrieval Regression Test
   ↓
Publish
~~~

Open WebUI oikb 当前使用 SHA-256 Diff，只同步新增、修改和删除文件，适合把知识同步工程化。

---

# 十七、权限与数据安全必须在 Retrieval 前执行

错误方式：

~~~text
先搜索所有资料
↓
把敏感资料送给模型
↓
Prompt 要求模型不要泄露
~~~

正确方式：

~~~text
User Identity
↓
ACL / Classification Filter
↓
Retrieval
↓
只有有权限的数据进入 Context
↓
LLM
~~~

必须考虑：

- 文档访问权限；
- 项目隔离；
- 数据分级；
- Embedding Provider；
- Rerank Provider；
- LLM Provider；
- Search Provider；
- Query / Document 日志；
- Agent Tool 权限。

尤其要强调：

> **本地客户端不等于所有数据都在本地处理。**

如果 Embedding / Rerank / LLM 使用外部 Provider，内容仍可能发送给外部服务。

---

# 十八、引用与可追溯性是硬要求

回答最好能够回到：

- 文件名；
- 文档路径；
- 页面；
- 章节；
- 行号；
- URL；
- Git Commit；
- Version。

目标不是：

> AI 说这是知识库里的。

而是：

> **用户可以回到权威原文进行确认。**

---

# 十九、重复、冲突和过期知识怎么处理

知识库最危险的场景之一：

~~~text
v1 文档
v2 文档
会议纪要
个人笔记
旧 PPT
~~~

都在说同一件事，但内容不同。

必须定义 Source Priority，例如：

~~~text
1. 已发布正式制度
2. 当前 Git main / Release
3. 已批准设计文档
4. 测试记录
5. 会议纪要
6. 个人笔记
~~~

并用 Metadata 标记：

- effective；
- obsolete；
- draft；
- version；
- effective_date；
- supersedes。

否则再好的 RAG 也可能准确找到一份旧资料。

---

# 二十、知识库必须有 Benchmark

不能以：

> 我问了两个问题感觉不错。

作为验收。

每个重要知识库都应该有 Retrieval Test Set。

建议至少记录：

| 字段 | 内容 |
|---|---|
| Question | 真实用户问题 |
| Expected Source | 应命中的文件 |
| Expected Passage | 应命中的章节 |
| Expected Fact | 正确事实 |
| Should Answer | 是否应该回答 |
| Access Role | 哪类用户可见 |

可以观察：

- Hit@K；
- Recall@K；
- 排序质量；
- Citation Correctness；
- Answer Groundedness；
- No-answer Accuracy；
- Latency；
- Token / Cost。

培训阶段不需要展开全部数学定义，但必须建立：

> **知识库也需要测试和回归。**

Cherry 当前官方 Knowledge Base 指南也建议保留现实测试问题，并在修改数据和检索设置后重新跑 Retrieval Test。

---

# 二十一、必须测试无答案场景

可靠知识库不仅要做到：

> 有答案时答对。

还要做到：

> **没有资料时不编。**

Test Set 应包含：

- 文档根本没有的问题；
- 无权限问题；
- 已失效知识问题；
- 存在冲突版本的问题。

期望：

~~~text
没有可靠资料
→ 明确说明没有依据
→ 必要时提示去哪个 Source 查询
~~~

---

# 二十二、推荐的部门最终架构

~~~text
┌──────────────────────────────────────────────┐
│             Source of Truth                  │
│ Git / Wiki / DMS / File Server / DB / API  │
└─────────────────────┬────────────────────────┘
                      ↓
┌──────────────────────────────────────────────┐
│ Parse / OCR / Normalize / Metadata / ACL     │
└─────────────────────┬────────────────────────┘
                      ↓
        ┌─────────────┼──────────────┐
        ↓             ↓              ↓
      BM25          Vector        Structured
   Full-text       Embedding       API / SQL
        └──────┬──────┘              │
               ↓                     │
             Rerank                  │
               └─────────┬───────────┘
                         ↓
┌──────────────────────────────────────────────┐
│             Knowledge Tool Layer             │
│ search / grep / read / query / MCP / Git    │
└─────────────────────┬────────────────────────┘
                      ↓
       ┌──────────────┼───────────────┐
       ↓              ↓               ↓
 Open WebUI       Cherry Studio      Agent
 部门统一入口      个人工作台       工程/研究任务
~~~

核心：

> **同一份知识可以拥有多个索引和多个入口，但只能有明确的权威 Source。**

---

# 二十三、建议部门近期落地方式

不建议一开始建设覆盖所有资料的大一统知识库。

## Phase 1：选一个可控专题

优先建议：

> AI 平台 / 内网模型使用知识库。

纳入：

- API 文档；
- 模型服务说明；
- 常见问题；
- 测试报告；
- 运维说明；
- model-metric 结论；
- 相关 Git 文档。

## Phase 2：做 Retrieval Benchmark

对同一组真实问题比较：

1. BM25 Only；
2. Vector Only；
3. Hybrid + Rerank；
4. Agentic Retrieval。

观察：

- 是否找到正确资料；
- 排序；
- 回答准确性；
- 引用；
- 延迟；
- Token。

## Phase 3：再定部门规范

根据实测决定：

- Parser；
- Chunk Strategy；
- Embedding Model；
- Rerank Model；
- Top-K；
- Open WebUI Shared KB；
- Cherry Personal KB；
- Agent Knowledge Tool；
- ACL；
- 同步方式。

原则：

> **先用真实问题验证，再定平台规范。**

---

# 二十四、建议最终形成五类知识资产规范

1. **Knowledge Source Standard**：什么进入知识体系、权威源在哪里；
2. **Document Standard**：格式、命名、目录、Metadata、版本；
3. **Retrieval Standard**：BM25 / Vector / Hybrid / Agentic 的使用规则；
4. **Security Standard**：ACL、数据分级、模型/Embedding/Rerank Provider 边界；
5. **Evaluation Standard**：Test Set、指标、上线门槛、回归测试。

这五类规范比单纯规定：

> 统一使用某一个 Embedding 模型

更重要、更能长期复用。

---

# 二十五、Embedding / Rerank 模型怎么选

不建议在知识库项目一开始就先拍板：

> 统一使用某一个 Embedding 模型。

应该先明确知识特点和测试集，再选模型。

## Embedding 重点关注

- 中文 / 中英混合能力；
- 技术术语和长文档效果；
- 最大输入长度；
- 向量维度；
- 查询吞吐；
- 建库速度；
- API 兼容性；
- 是否可以内网部署；
- 数据是否会离开内网；
- 更换模型后的 Reindex 成本。

对部门内部资料：

> **数据边界优先于公开 Benchmark 分数。**

如果当前没有经过批准的内网 Embedding：

> **可以先使用 BM25 建立第一版知识库，而不是为了做 Vector RAG 把内部文档发送到外部服务。**

## Rerank 重点关注

- 中文相关性排序；
- Query + Passage 最大长度；
- 每次可处理候选数量；
- 延迟；
- 并发；
- 是否支持内网部署；
- API 接口与客户端兼容性。

Rerank 应解决：

> 已经召回正确资料，但正确资料排得不够靠前。

如果第一阶段根本召回不到正确文档，应该先检查：

- Parsed Text；
- Chunk；
- BM25 / Embedding；
- Query；
- Metadata Filter。

而不是直接叠加 Rerank。

---

# 二十六、哪些场景根本不应该优先建设成知识库

## 26.1 实时状态

例如：

- 当前服务器 CPU；
- 当前 GPU 利用率；
- 当前模型实例数；
- 当前项目 CI 状态。

应该：

> API / Metrics / Tool 实时查询。

## 26.2 强结构化数据

例如：

- BOM；
- 财务数据；
- 资产清单；
- 测试数据库；
- 工单字段。

应该：

> SQL / API / Data Tool。

知识库只保存：

> 字段定义、口径、使用说明。

## 26.3 高频变化的代码

源代码优先：

> Git + grep + LSP + Agent。

不是每天重新做整库 Embedding。

## 26.4 强事务业务

例如：

- 创建工单；
- 修改资产；
- 发布版本；
- 审批流程。

知识库只能解释规则。

真正操作应该：

> API / MCP / Workflow。

所以：

> **Knowledge Retrieval 负责知道，Tool / API 负责做。**

---

# 二十七、部门知识库最常见的十个误区

1. **把 Vector DB 当成知识库本身**；
2. **所有文件不分类直接上传**；
3. **扫描 PDF 没检查 OCR 就开始 Embedding**；
4. **代码、日志、实时数据也全部向量化**；
5. **只调 Embedding，不检查 Parsed Text 和 Chunk**；
6. **没有 Version / Owner / Effective Status**；
7. **权限只控制 Chat 登录，不控制 Retrieval**；
8. **知识更新后没有 Reindex 和回归测试**；
9. **只测试“有答案”，不测试“无答案”和冲突资料**；
10. **把客户端本地 KB 当成部门唯一 Source of Truth**。

如果避免这十个问题，知识库建设的可靠性通常比单纯更换更强模型提升更明显。

---

# 二十八、什么时候考虑 Knowledge Graph / GraphRAG

知识图谱不是第一阶段默认组件。

当问题大量涉及：

- 人 / 项目 / 产品 / 设备 / 组织之间的关系；
- 多跳关系查询；
- 影响链；
- 依赖链；
- 配置项关联；

并且单纯文档 Retrieval 难以稳定回答时，再考虑：

> Entity / Relation Extraction + Graph Query + RAG。

例如：

~~~text
设备 A
→ 使用板卡 B
→ 板卡 B 使用芯片 C
→ 芯片 C 的某版本影响哪些项目？
~~~

这类问题图结构可能有价值。

但对：

- FAQ；
- 制度；
-普通技术文档问答；

没有必要一开始就上 GraphRAG。

原则仍然是：

> **问题驱动架构，不为了技术名词堆组件。**

---

# 二十九、培训中要留下的结论

第一：

> **知识库不是某一个产品，也不是 Vector DB，而是一套知识访问体系。**

第二：

> **源文件是资产，Embedding 是索引。索引可以重建，Source of Truth 必须稳定。**

第三：

> **技术文档适合 Hybrid RAG；代码适合 grep/LSP/Git；实时数据适合 API/SQL；复杂跨源问题适合 Agentic Retrieval。**

第四：

> **Cherry Studio 更适合个人专题知识库；Open WebUI 更适合部门共享 Knowledge Service；Agent 更适合跨知识源主动检索和工程执行。**

第五：

> **知识库建设不仅要解决搜得到，还要解决版本、权限、引用、更新和评测。**

第六：

> **未来真正应该建设的是可被不同 Chat 和 Agent 复用的 Knowledge Access Layer，而不是绑定某个客户端的一批向量。**

---

# 三十、当前官方参考

## Cherry Studio

- Knowledge Base: https://cherryai.com/docs/en/knowledge-base/knowledge-base/
- Project / Supported Knowledge Formats: https://cherryai.com/docs/en/
- Agent: https://cherryai.com/docs/en/advanced-basic/agent/

当前官方文档明确：

- Knowledge Source 支持 File / Note / Folder / Link；
- 支持 PDF、DOCX、PPTX、XLSX、TXT、MD 等多种知识文件；
- Embedding Model 可以设为 None，以 BM25 开始；
- Reranker 可选；
- 使用前建议检查 Parsed Text、Chunks 和 Retrieval Test；
- 可在 Chat 中选择 KB，或绑定 Agent。

## Open WebUI

- Knowledge: https://docs.openwebui.com/features/workspace/knowledge/
- RAG: https://docs.openwebui.com/features/chat-conversations/rag/
- Document Extraction: https://docs.openwebui.com/features/chat-conversations/rag/document-extraction/
- Knowledge Base Sync: https://docs.openwebui.com/ecosystem/knowledge-base-sync/
- Tools: https://docs.openwebui.com/features/extensibility/plugin/tools/

当前官方能力包括：

- Focused Retrieval；
- Full Context；
- Hybrid BM25 + Vector；
- Cross-Encoder Rerank；
- Agentic Knowledge Tools；
- query / grep / view_file / kb_exec；
- 多种文档抽取/OCR引擎；
- 增量 Knowledge Sync；
- API 与访问控制。
