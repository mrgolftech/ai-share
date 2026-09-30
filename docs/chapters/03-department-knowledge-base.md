# 培训讲义：部门知识库怎么设计、怎么建、怎么用

> 模块：Chat → Knowledge → RAG → Agent
> 日期：2026-09-29
> 面向对象：部门技术人员、知识库建设人员、AI 平台与应用建设人员
> 核心问题：在 Open WebUI、Cherry Studio 和各类 Agent 并存的情况下，部门知识资产应该采用什么形式、如何检索、哪些需要向量化，以及怎样保证长期复用和治理。

---

## 证据边界：哪些是研究结论，哪些是本培训的工程建议

本章设计基线已经在 2026-09-30 按学术论文、官方产品文档和成熟开源实现重新核验。

后续统一区分四类表述：

- **论文/Benchmark 结论**：例如 BEIR 说明 BM25 是稳健 baseline，Dense Retrieval 并非跨域场景下永远占优；
- **官方产品事实**：例如 Cherry Studio 当前允许 Embedding=None 使用 BM25，Open WebUI 当前支持 Hybrid / Full Context / Agentic Knowledge；
- **本培训工程建议**：例如技术资料优先维护 Markdown 镜像、部门共享知识源与检索索引分离；
- **待内网实测**：例如中文工程资料上 BM25 vs Dense vs Hybrid 的实际提升、Rerank 收益、ACL 和 no-answer 效果。

因此，本章不再把“Markdown 优先”“代码默认不向量化”“表格不向量化”等工程经验写成普适研究结论。

专项证据基线：

`docs/references/knowledge-base-rag-evidence-2026-09.md`

当前成熟度：

> **需求与架构已有研究/成熟实现支撑；具体检索参数与技术路线仍必须由本部门语料 Benchmark 决定。**

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
| 源代码 | Python、JS、C/C++、配置 | Git Repo | rg/grep/LSP/Git 为主，语义代码搜索按需补充 | 不是默认必需，需按任务实测 |
| API / 协议 | OpenAPI、JSON Schema、接口文档 | Git + YAML/JSON | 结构化解析 + grep | 可选 |
| 表格数据 | Excel、CSV、测试记录、BOM | XLSX/CSV/数据库 | 精确筛选/聚合优先表格查询 / Python / SQL；文本列可检索 | 向量检索可作为补充，不应替代结构化查询 |
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

## 4.1 工程建议：适合 Git 管理的技术知识优先考虑 Markdown

对技术方案、API 说明、操作手册、FAQ、设计记录、项目规则等，如果业务流程允许，建议同步维护 Markdown 或其他稳定的机器可读文本版本。

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

## 4.2 PDF：可以作为知识源，但必须验证解析结果并保留原件

【复用截图 KB-06A / KB-06｜P0】原 PDF 页面 → Parsed Text → Chunk 三联图。技术稿重点标注解析错误、页码丢失、表格/多栏等风险位置。


文本型、版式简单的 PDF 可以直接进入知识库；风险主要来自扫描件、复杂多栏、表格、公式和图示。

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

当任务涉及精确筛选、聚合、排序、计算或行列关系时，不应只把大量数值表格转成普通文本后依赖 Vector RAG。

更推荐把结构化查询作为主路径：

~~~text
XLSX / CSV
   ↓
Python / SQL / Data Tool
   ↓
Agent 分析
~~~

另外维护数据字典和指标口径 Markdown 供 RAG 查询。对于表头、字段说明、备注、故障描述等自然语言内容，仍可以按需建立文本/向量索引。

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

## 优先不依赖向量化，但可按需补充

典型包括：

- 代码中的标识符、函数名和路径；
- 配置键；
- API Path；
- 错误码；
- 型号；
- 日志；
- 标准编号；
- 精确术语；
- 很短且可以直接放进 Context 的文档。

这些内容通常先用 BM25 / grep / LSP / Full Context 获得更可控的精确匹配；如果存在大量“自然语言描述 → 代码/配置位置”的语义查找需求，可以再增加 Semantic Code Search 或 Vector Index，并用测试集决定是否保留。

## 不建议把向量索引作为实时事实主源

- 实时 Metrics；
- 时序数据；
- BOM 的精确数量/版本状态；
- 数据库记录；
- 当前服务器状态；
- 实时资产状态。

这类数据的“当前事实”应优先通过 API / SQL / Tool 获取；其字段说明、历史分析结论和自然语言备注仍可进入知识检索层。

---

# 八、BM25、Embedding、Rerank 的职责

【复用截图 KB-04 / KB-05 / KB-10｜P0】Embedding=None/BM25、BM25 vs Embedding Retrieval Test、Top-K/Rerank 配置。此处只解释机制，实际操作录屏复用 `KB-R02`。


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

## 9.1 检索命中，不等于 LLM 一定能把证据用好

这是知识库设计中非常容易漏掉的一层。

传统 RAG 图经常画成：

~~~text
Question
→ Retrieval
→ Top-K
→ LLM
→ Answer
~~~

这张图容易造成一种错觉：

> Retriever 只要把正确 Chunk 找出来，后面的事情就解决了。

实际上至少存在两层不同问题：

~~~text
第一层：外部检索
Question
→ Retriever
→ 正确资料有没有进入候选集？

第二层：上下文内利用
Retrieved Context
→ LLM
→ 模型能不能在长上下文中重新定位、关联并正确使用证据？
~~~

培训中建议明确区分：

- **External Retrieval Recall**：搜索系统有没有把正确资料找出来；
- **In-context Retrieval / Context Utilization**：正确资料已经放进 Prompt 后，模型能不能稳定使用。

这两层都会失败。

### 9.1.1 为什么不能把 Context Window 当成“有效知识容量”

模型声明：

~~~text
128K / 256K / 1M Context
~~~

首先表示的是：

> **接口允许接收多长输入。**

它不自动意味着：

> **模型可以在整个窗口内，对任意位置、任意复杂度的信息保持同等可靠的定位、关联和推理能力。**

已有研究给出了比较一致的风险证据。

#### Lost in the Middle（TACL 2024）

Liu 等人的实验显示：

- 相关信息在 Context 中的位置会影响回答效果；
- 多个模型常表现出开头 / 结尾优于中间的现象；
- 在开放域 QA case study 中，继续增加检索文档可以提升 Retriever Recall，但 Reader 的最终收益很快趋于饱和；
- 论文报告从 20 篇检索文档增加到 50 篇时，GPT-3.5-Turbo 与 Claude-1.3 的最终表现只得到约 1%–1.5% 的边际提升。

这说明：

> **检索更多 ≠ 模型有效使用更多。**

#### RULER（2024）

RULER 专门指出简单 Needle-in-a-Haystack 测试不足以代表真实长上下文能力。

它增加：

- 多个 needle；
- multi-hop tracing；
- aggregation；
- 更复杂的 Context 任务。

论文测试的 17 个长上下文模型中，即使很多模型在简单 NIAH 上接近满分，随着 Context Length 和任务复杂度增加仍出现明显下降。

因此：

> **标称 Context Size ≠ Effective Context Size。**

#### NoLiMa（ICML 2025）

NoLiMa 去掉 Query 与答案证据之间明显的字面匹配，要求模型通过语义关系找到证据。

论文测试 13 个声称至少支持 128K Context 的模型：

> 在 32K 输入时，其中 11 个模型已经跌到各自短上下文强基线的 50% 以下。

这与企业知识库很相关，因为真实用户经常不会使用文档中的原词提问。

#### 2025：即使“完美检索”，长 Context 仍然可能伤害结果

Findings of EMNLP 2025 的：

> **Context Length Alone Hurts LLM Performance Despite Perfect Retrieval**

进一步控制了一个关键变量：

> 正确证据已经完整提供给模型，不存在 Retriever 漏召回。

但论文在 5 个开放/闭源模型、数学、QA、代码任务上仍然观察到：

> 随输入增长，任务表现出现 13.9%–85% 的下降。

这个结果对知识库设计尤其重要：

> **知识库系统不能只优化 Recall，还要控制最终交给 LLM 的 Context。**

#### 2025 Context Rot：最新产业实验也看到类似现象

Chroma 在 2025 年技术报告中，对包括 GPT-4.1、Claude 4、Gemini 2.5、Qwen3 在内的 18 个模型进行了长上下文控制实验，报告输入增长时模型表现并非均匀稳定。

这不是同行评审论文，因此培训中应标为：

> **产业实测 / Technical Report**

但它说明长上下文问题并没有随着 2025 年新模型完全消失。

### 9.1.2 因此知识库需要的不只是 Context Window，而是 Context Budget

知识库设计建议引入：

> **Context Budget / Evidence Budget**

也就是：

> **不是检索到多少就塞多少，而是在覆盖必要证据的前提下，只把最相关、最可靠、最有信息量的内容交给模型。**

可以把完整流程画成：

~~~text
                Knowledge Source
                       ↓
              Candidate Retrieval
              BM25 / Vector / Hybrid
                       ↓
                 Broad Recall
                       ↓
                    Rerank
                       ↓
            Metadata / ACL / Version
                       ↓
           Deduplicate / Merge / Filter
                       ↓
               Context Selection
                 Evidence Budget
                       ↓
              Context Packing
                       ↓
                     LLM
                       ↓
          Grounded Answer + Citation
~~~

这里：

- Retrieval 负责“不要漏”；
- Rerank / Filter 负责“把最有价值的排前面”；
- Context Selection 负责“不要把所有候选都塞进去”；
- LLM 负责基于最终证据理解和生成。

所以 **Recall 越高不代表最终答案一定越好**。

### 9.1.3 Top-K 不是越大越好

Top-K 本质上是：

> **Recall 与 Context Pollution 之间的权衡。**

Top-K 太小：

- 可能漏证据；
- 跨文档问题可能缺少必要上下文。

Top-K 太大：

- 无关 Chunk 增多；
- 重复内容增多；
- 新旧版本可能同时进入；
- Context 变长；
- TTFT / Token Cost 增加；
- LLM 在上下文中定位和综合证据的负担增加。

成熟系统本身就在暴露这类控制参数。

例如 Open WebUI 当前提供：

- `RAG_TOP_K`；
- `RAG_TOP_K_RERANKER`；
- `RAG_RELEVANCE_THRESHOLD`；
- Hybrid Search；
- Agentic Knowledge Tools。

其 `kb_exec` 还默认限制单次 Tool 输出量，并明确说明限制的目的之一是避免 Tool Result 挤占 Context Window。

RAGFlow 当前官方 Retrieval Configuration 也明确说明：

> Top N 增大可以提供更多 Context，但会增加 Context Length、响应时间和成本，应根据数据集与检索效果调节。

因此培训中不要给出类似：

> “Top-K 固定设成 5 / 10 就最好。”

更合理的是：

> **Top-K 是 Dataset + Query Type + Model + Context Budget 的联合参数。**

### 9.1.4 Rerank 的意义不只是提高搜索分数

Rerank 还有一个很重要的工程价值：

> **让较大的 Candidate Recall 集合，在进入 LLM 之前压缩成更小、更高质量的 Evidence Set。**

例如：

~~~text
Hybrid Search
→ 召回 30 个候选
→ Rerank
→ 留下 5 个高相关 Chunk
→ 去重 / 合并相邻片段
→ LLM
~~~

这通常比：

~~~text
召回 30 个
→ 30 个全部塞进 Prompt
~~~

更符合长上下文风险控制思路。

Anthropic 2024 的 Contextual Retrieval 工程实验也采用：

> BM25 + Embedding → Candidate Retrieval → Reranking → Top-K Context

并报告其数据集上加入 Contextual Retrieval 和 Reranking 后，Top-20 Chunk retrieval failure rate 显著下降。

需要注意：

> 这是 Anthropic 自己实验数据，不应当成所有部门语料都会得到同样提升幅度。

### 9.1.5 Chunk 设计与 Context Budget 是连在一起的

Chunk 太大不仅影响 Retrieval Precision，也直接增加最终 Context。

Chunk 太小则可能导致：

- 一个事实被拆碎；
- 前提与结论分离；
- 表头与数据分离；
- Retrieval 找到局部，但 LLM 缺乏解释它的上下文。

因此更合理的是：

~~~text
小范围 Candidate Retrieval
        ↓
找到目标 Chunk
        ↓
按需要扩展 Parent / Neighbor Context
        ↓
只把必要局部交给 LLM
~~~

而不是：

> 为了防止切碎，把每个 Chunk 做得非常大。

对于 Markdown / HTML / 技术文档，可以优先保留：

- Heading Path；
- Parent Section；
- Previous / Next Chunk；
- Document ID；
- Version。

让系统可以：

> **先精确找到，再按需扩展。**

### 9.1.6 多文档问题尤其要防止“Context Pollution”

实际知识库很容易出现：

~~~text
同一制度 v1
同一制度 v2
旧会议纪要
新的正式决定
个人笔记
重复 PDF
不同部门复制件
~~~

即使 Retriever 每一条都“相关”，同时塞给模型也会产生：

- 冲突；
- 冗余；
- 版本判断困难；
- 对注意力和推理造成额外负担。

所以 Metadata / Version / Status 的价值不仅是方便管理，还可以在进入 Context 前：

> **先过滤错误证据。**

正确思路：

~~~text
Retrieve Broadly
→ ACL
→ Version / Status Filter
→ Rerank
→ Deduplicate
→ Context Budget
→ LLM
~~~

### 9.1.7 Agentic Retrieval 为什么在复杂长文档场景有价值

传统 Pipeline 往往一次性：

~~~text
Top-K
→ 全部注入
→ Answer
~~~

Agentic Retrieval 可以改成：

~~~text
Search
→ 看少量结果
→ Read 某个 Section
→ 判断还缺什么
→ 再 Search
→ 再 Read
→ Evidence 足够
→ Answer
~~~

这实际上是在用：

> **多轮、逐步取证**

替代：

> **一次性塞大量 Context。**

所以 Agentic Retrieval 一个很重要的价值不是“搜索算法更先进”，而是：

> **把 Context Allocation 也交给任务过程动态控制。**

代价是：

- Tool Call 更多；
- Token 更多；
- 延迟更长；
- 对模型工具调用能力要求更高。

因此仍然不能替代所有 Pipeline RAG。

### 9.1.8 这一节最终让学员记住三个数字不是重点，三个概念才是重点

第一：

> **Context Window 是容量上限，不是有效利用能力保证。**

第二：

> **Retriever 找到了 ≠ LLM 一定能用好。**

第三：

> **知识库追求的是“足够且高质量的证据”，不是“尽可能多的 Context”。**

完整研究证据：

`docs/references/knowledge-base-rag-evidence-2026-09.md`

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

## 11.1 Open WebUI 中哪些知识库配置是管理员做，哪些可以下放给普通用户

Open WebUI 要区分两层权限。

### 平台级 RAG 配置：管理员负责

例如：

- Embedding Provider / Embedding Model；
- Rerank Model；
- Chunk Size / Overlap；
- Document Extraction / OCR Engine；
- Hybrid Search；
- Full Context 默认行为；
- External Knowledge Source；
- 上传大小等全局限制。

这些位于：

~~~text
Settings → Admin → Documents
~~~

属于实例级配置。

### Knowledge Base 的创建和使用：可以下放给普通用户

普通 User 默认受 RBAC 控制。

管理员可以在：

~~~text
Admin Panel
→ Users
→ Groups
→ Default Permissions / Group Permissions
~~~

开放：

~~~text
Workspace → Knowledge Access
~~~

获得该权限后，普通用户可以进入：

~~~text
Workspace → Knowledge
~~~

创建和管理自己的 Knowledge Base。

新创建的 Knowledge Base 默认是私有资源。

如果需要共享，还应单独配置：

- Knowledge Sharing；
- Knowledge Public Sharing；
- Share to specific users / groups；
- Read / Write Access。

因此：

> **Open WebUI 不是“只有管理员才能建知识库”，而是“平台参数由管理员集中治理，知识库创建权限可通过 RBAC 下放”。**

这与部门场景非常匹配：

~~~text
平台管理员
→ 统一 Parser / Embedding / Rerank / 安全策略

知识库管理员 / Power User
→ 建部门或项目 KB、维护资料、做 Retrieval Test

普通用户
→ 查询已授权 Knowledge Base
~~~

需要特别注意：

> **把 Knowledge Base 绑定到一个共享 Model，并不会自动把底层 Knowledge 权限授给所有使用该 Model 的用户。**

用户仍然需要对该 Knowledge Base 拥有 Read 权限，否则 Knowledge Tool 查询会返回空结果。

### 对培训 Demo 的建议

Open WebUI 不必承担“现场从零搭一个个人知识库”的主要演示。

更适合演示：

1. 管理员统一设置 Embedding / Rerank / Hybrid Search；
2. 创建一个共享 Knowledge Base；
3. 将 KB 授权给 Engineering Group；
4. 普通用户通过共享 Model / Chat 使用 KB；
5. 展示同一个 KB 在 Focused Retrieval / Agentic Knowledge Tool 下的使用；
6. 说明 ACL 如何限制不同用户看到的知识。

而“从零创建 KB → 添加文件 → BM25 → Embedding → Retrieval Test”的快速演示优先放在 Cherry Studio。


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

> **短而关键 → 可以优先考虑 Full Context；大而稀疏使用 → 优先 Retrieval。**

但这里不能只看“是否塞得进模型 Context Window”。

还必须考虑：

- 问题需要使用多少份证据；
- 无关内容比例；
- 文档是否存在重复/冲突；
- 模型对当前长度的实际利用能力；
- TTFT / Token / 成本。

因此更准确的决策不是：

~~~text
能塞进去？
→ 能
→ 全塞
~~~

而是：

~~~text
资料规模 + 问题类型 + 证据密度 + Context 利用能力 + 成本
→ Full Context / RAG / Agentic Retrieval
~~~

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

【复用图示 KB-21｜P0】错误流程“先检索后过滤” vs 正确流程“先 ACL 再 Retrieval”。

【复用录屏 KB-R03｜P0】Open WebUI Shared Knowledge / Group 权限实际验证。


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

【复用截图 KB-22｜P0】一个带 Source / Section / Version / Commit 或页码引用的回答。技术稿中应放大引用字段，而不是只截最终自然语言。


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

# 二十九、统一演示设计：同一知识源，三种使用层次

这一部分统一使用同一批真实 Qwen 资料，不为 Cherry、Open WebUI 和 Agent 分别准备三套事实。

资料包括：

- docs/chapters/01-intranet-qwen-api.md
- api/qwen/README.md
- api/qwen/reports/qwen36_api_test_report_20260929.md
- api/qwen/results/20260929_v2/evidence.md
- api/qwen/results/20260929_105316/evidence.md

这样可以固定：

> **Source of Truth 不变，只改变 Retrieval、Governance 和 Orchestration。**

统一准备三类问题：

1. 精确事实：qwen3.6 当前服务配置的 max_model_len 是多少？
2. 语义改写：为什么复杂推理任务跑完以后，后面的简单请求有时也会突然变慢？
3. 综合判断：当前 qwen3.6 是否已经适合部门 Agent 连续任务？区分已验证能力、已观察风险和未验证项，并给出来源。

## Demo A：Cherry Studio —— 知识怎么建

【素材占位｜P0】静态复用 `KB-12～14`；动态复用 `KB-R01`（建库到问答）与 `KB-R02`（BM25/Embedding/Rerank 对比）。


Cherry 负责演示：

~~~text
Source
→ Parse
→ Chunk
→ BM25
→ Embedding
→ Rerank
→ Retrieval Test
~~~

先设置 Embedding=None，用问题 1 做 BM25 Retrieval Test。

再用问题 2 观察关键词检索效果，然后配置 Embedding 并重新索引，比较语义召回。

如果正确 Chunk 已经召回但排序不理想，再加入 Rerank。

最后把同一个 Knowledge Base 绑定到 Cherry Agent，使用问题 3 做综合问答。

要讲清：

> **Cherry Agent 可以承接 Cherry 自己的 RAG KB；RAG 与 Agent 并不是互斥路线。**

## Demo B：Open WebUI —— 知识怎么共享和治理

【素材占位｜P0】静态复用 `KB-15～17`；动态复用 `KB-R03`（Shared KB + ACL）与 `KB-R04`（Pipeline vs Agentic）。


Open WebUI 不再重复完整的建库教学。

重点展示：

- 平台管理员统一 Parser / Embedding / Rerank / Hybrid Search；
- 建立共享 Knowledge Base；
- Group / ACL；
- Workspace Model 绑定 Knowledge；
- 普通用户通过共享 Model 使用统一知识；
- 没有 KB Read 权限的用户不能通过共享 Model 绕过底层权限。

如果当前部署支持 Native Knowledge Tools，再展示同一 Shared KB 的两种使用：

~~~text
Pipeline / Focused Retrieval
vs
Agentic Knowledge Tool
~~~

Open WebUI 当前还提供 Knowledge API 和 server-side tool calling。

因此它不仅可以作为 Chat Portal，也可以成为外部 Agent 的 Shared Retrieval Service：

~~~text
External Agent
   ↓
Open WebUI Knowledge API / Tool Service
   ↓
Shared Knowledge Base
~~~

## Demo C：Agent —— 承接原始知识和 RAG 知识

【素材占位｜P0】静态复用 `KB-18～19`；动态复用 `KB-R05`（Shared KB → Git → API/Metrics 的跨源取证）。


Agent 不应该再演示成第三套互斥知识库。

更准确的定位是：

> **Knowledge Orchestrator。**

推荐任务：

> 基于部门共享知识库和当前 Git Repo，分析 qwen3.6 是否适合部门 Agent 连续任务。先检索共享知识库获得总体结论，再读取 Git 中的原始测试报告进行核验；需要实时信息时说明还应查询哪些 Metrics/API。所有结论必须给出来源，不允许根据模型名称推测。

预期过程：

~~~text
Goal
 ↓
Shared RAG KB
 ↓
得到候选结论
 ↓
Agent 判断需要原始证据
 ↓
grep / read Git
 ↓
交叉核验
 ↓
必要时 API / Metrics
 ↓
Final Answer
~~~

这说明 Agent 可以同时承接：

- Open WebUI 一类共享 RAG KB；
- Cherry Agent 内绑定的个人 KB；
- Git / Workspace 原始文件；
- API / DB / Metrics 实时知识。

但对于外部 Codex/OpenCode/Hermes 等 Agent：

> **不要默认它们可以直接读取 Cherry 的本地知识索引。**

更稳定的方式是：

- 访问相同 Source of Truth；
- 或调用有正式 API / MCP 的共享 Retrieval Service，例如 Open WebUI Shared KB。

## 为什么同一套资料更适合演示

因为固定了：

~~~text
Source = Same
~~~

只改变：

~~~text
Cherry
→ Retrieval Algorithm

Open WebUI
→ Shared Retrieval + Governance

Agent
→ Retrieval Orchestration + Multi-source
~~~

这样学员看到的差异可以归因于工具和工作方式，而不是资料本身不同。

但不建议三个工具机械重复完全相同的问题。

推荐：

- 问题 1：三种工具都问，作为可比基线；
- 问题 2：重点由 Cherry 演示 BM25 / Vector / Rerank；
- 问题 3：重点由 Open WebUI 和 Agent 演示 Shared Knowledge 与 Agentic Retrieval。

完整 Demo 规范：

demos/knowledge-retrieval/README.md

---

# 三十、培训中要留下的结论

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

# 三十一、当前官方参考

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


---

# 附：本章证据与实测状态

完整论文、官方文档、成熟实现和结论审计见：

`docs/references/knowledge-base-rag-evidence-2026-09.md`

当前仍待完成的部门实测包括：

- Cherry Studio：BM25 vs Dense vs Rerank；
- Open WebUI：Hybrid Retrieval；
- Full Context vs RAG 的质量、TTFT 和 Token 成本；
- Agentic Knowledge / kb_exec 对内网 qwen3.6 的稳定性；
- 复杂 PDF / PPT / XLSX 解析；
- 版本冲突、no-answer、ACL 回归测试；
- 中文 Embedding / Reranker 的模型与资源选型。

在这些测试完成之前，讲义中的检索方案均应表述为“**候选设计 / 推荐验证顺序**”，而不是“部门已验证最佳方案”。


---

# 附二：本技术稿的素材引用索引

本技术稿不再另建一套截图编号，统一复用教学版的 `KB-01～KB-22` 与 `KB-R01～KB-R06`。这样后续替换真实截图时只维护一份素材。

| 技术主题 | 静态素材 | 动态素材 |
|---|---|---|
| 知识源 / 不同资产类型 | KB-02、KB-03 | — |
| Parse / Chunk | KB-06A、KB-06 | KB-R01 |
| BM25 / Embedding / Rerank | KB-04、KB-05、KB-10 | KB-R02 |
| Long Context / Evidence Budget | KB-08、KB-08B、KB-09 | — |
| Full / Pipeline / Agentic | KB-11、KB-17 | KB-R04 |
| Cherry Studio | KB-12～14 | KB-R01、KB-R02 |
| Open WebUI | KB-15～17 | KB-R03、KB-R04 |
| Agent 多源取证 | KB-18、KB-19 | KB-R05 |
| ACL | KB-21 | KB-R03 |
| 引用与可追溯 | KB-22 | KB-R05 |
| No-answer / 冲突 | — | KB-R06 |

