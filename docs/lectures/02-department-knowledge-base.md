# 第二讲：部门知识库建设——让 AI 可靠使用我们的知识

> 状态：Final Lecture Draft v1.0  
> 日期：2026-09-30  
> 建议时长：100～120 分钟  
> 内容映射：原内容单元 2  
> 主线：**先回答部门为什么要建知识库，再回答不同知识怎么处理、怎么检索、怎么进入 Context、怎么治理，最后形成可落地的部门建设方案。**

---

# 0. 本讲不从“向量数据库”开始

部门准备建设知识库时，最容易出现一种直觉：

> 找一个知识库软件，把现有 PDF、Word 全部上传进去，再做 Embedding，知识库就建成了。

这个思路看起来简单，但很快会遇到实际问题：

- 同一份规范有三个版本，AI 应该相信哪个？
- 一个芯片型号写得很精确，为什么语义检索反而没有找到？
- 代码、数据库、API、日志也算部门知识，难道也全部转成 PDF？
- 一份 300 页手册已经上传，为什么模型还是找不到中间的一条关键规则？
- 一个员工没有权限查看某份文件，能不能因为 RAG 检索就把内容送给模型？
- Cherry Studio 建一套知识库、Open WebUI 再建一套、Agent 又建一套，以后谁来维护？
- 知识库回答了一个很像真的答案，我们怎么证明它引用的是正确版本、正确原文？

所以这一讲先不问：

> 用哪个向量数据库？

先问：

> **部门究竟希望 AI 使用什么知识，解决什么工作问题？**

---

# 1. 从一个真实问题开始：模型为什么需要部门知识？

假设问内网模型：

> 当前部门 Qwen 服务的上下文长度是多少？Thinking、Tool Calling、Vision 的实际兼容情况怎样？

这些信息有几个特点：

- 部分是部门内部部署信息；
- 部分来自我们自己的 API 实测；
- 会持续更新；
- 公开互联网未必存在；
- 即使网上有同名模型资料，也不一定等于我们当前部署。

如果直接让模型“凭自己知道的回答”，它没有稳定依据。

最原始的办法其实很简单：

```text
用户问题
+
相关内部资料
↓
一起交给模型
↓
模型基于资料回答
```

【截图占位 KB-01｜同一问题：裸模型回答 vs 带当前内部资料回答】

这里先建立第一个结论：

> **部门知识不能只依赖模型参数，必须有模型之外、可更新、可追溯的知识源。**

这个“知识源”才是知识库建设真正的起点。

---

# 2. 先盘点知识，而不是先选工具

如果现在让部门列出“知识库资料”，通常会想到：

- Word；
- PDF；
- PPT；
- 规范；
- 手册；
- 测试报告。

但技术部门真正使用的知识远不止这些。

可以现场问大家：

> 查一个当前 API 实测结果，你会去哪里？

可能是测试报告。

> 查一个函数到底怎么实现？

可能是 Git。

> 查服务器现在有没有排队？

应该查实时指标。

> 查某项配置当前值？

可能需要读配置文件或者调用 API。

因此部门知识至少可以先分成几类。

## 2.1 稳定自然语言文档

例如：

- 制度；
- 规范；
- 产品手册；
- 技术方案；
- 设计说明；
- FAQ；
- 测试结论。

这类知识很适合文档检索和传统 RAG。

## 2.2 代码和配置

例如：

- Python / C / C++；
- YAML；
- Docker Compose；
- 配置文件；
- API Schema；
- 错误码。

这类知识通常更适合：

```text
Tree
→ Search
→ Read
→ References
→ Git History
```

而不是先转 PDF。

## 2.3 结构化数据

例如：

- Excel；
- CSV；
- 测试数据库；
- SQL 表；
- 统计数据。

有些内容可以形成文档摘要，但涉及大量精确筛选、计算和聚合时：

> **让工具查询数据往往比把整张表 Embedding 更可靠。**

## 2.4 动态和实时数据

例如：

- 当前服务器状态；
- 模型 running / waiting；
- 实时 TPS；
- CI 状态；
- 最新 Release；
- 设备在线状态。

这类知识的关键不是“存进知识库”，而是：

> **在回答时访问当前系统。**

因此更适合 API、SQL、Monitoring、MCP 等方式。

## 2.5 图片、图纸和复杂版式

例如：

- 架构图；
- PCB 图；
- PPT；
- 扫描 PDF；
- 截图。

这时不仅要考虑文本，还要考虑：

- OCR 是否可靠；
- 图中的结构关系是否被保留；
- 表格是否被解析正确；
- 图片本身是否应该交给多模态模型。

【图示占位 KB-02｜部门知识资产分类：文档 / 代码 / 数据 / API / 日志 / 图片】

此处给出第二个结论：

> **知识库不是“把所有东西变成同一种格式”，而是让不同类型知识以合适方式被 AI 访问。**

---

# 3. 什么是 Source of Truth：哪份资料才算“真的”？

知识库真正危险的问题通常不是：

> 搜不到。

而是：

> 搜到了一份看起来很像真的旧资料。

假设项目目录里同时存在：

```text
技术方案_v1.docx
技术方案_修改版.docx
技术方案_最终版.docx
技术方案_最终版2.docx
```

如果四份都进入索引，Retriever 可能把其中任何一份找出来。

模型不会自动知道：

> 哪一份才是当前有效版本。

因此知识库必须先解决 Source of Truth。

可以把它理解为：

> **对某一类事实，部门约定“真正算数的原始来源在哪里”。**

例如：

```text
当前代码事实
→ Git main

当前接口实测
→ 自动测试结果 / 报告

当前部署配置
→ 配置仓库 / 运行环境

正式制度
→ 文控系统有效版本

知识库索引
→ 只是从这些 Source 派生出来的检索结构
```

这里必须明确：

> **Vector Index 不是 Source of Truth。**

Embedding 模型换了，可以重建索引。

客户端换了，可以重新接入。

但原始知识源必须稳定、可管理。

【截图/图示占位 KB-03｜Source of Truth → Index → Client 的关系】

---

# 4. RAG 到底解决什么问题？

现在再讲 RAG。

不要先讲缩写。

把它解释成：

> **先查资料，再把找到的资料给模型，然后再回答。**

```text
Question
↓
Retrieve
↓
Relevant Evidence
↓
LLM Context
↓
Answer
```

【图示占位 KB-04｜最简单 RAG 流程】

这时候就能理解：

RAG 实际上至少有两个完全不同的问题。

第一：

> **系统有没有把正确资料找出来？**

第二：

> **正确资料已经交给模型以后，模型有没有正确利用？**

后面长上下文问题就是第二层。

---

# 5. Parse：文件存在，不等于机器已经读对

假设有一份 PDF。

在人看来是：

> 标题、正文、表格、页眉、图片、脚注。

但机器拿到 PDF 后可能遇到：

- 文本顺序错乱；
- 两栏内容交叉；
- 表格被拆散；
- 扫描页没有文本层；
- 页眉页脚重复进入正文；
- 图片中的文字完全没有提取；
- 字符编码异常。

因此进入 RAG 前通常需要 Parse。

Parse 的目的不是：

> 把 PDF 变成 txt 就结束。

而是尽量把原始资料转换成机器可以稳定检索、还能保留结构的信息。

【截图占位 KB-06A｜同一 PDF 原页 → Parsed Text】

拍摄时最好选择：

- 一页有标题；
- 一页有表格；
- 一页有两栏或复杂结构。

让大家直观看到：

> “文件能打开”和“机器读对了”完全不是一回事。

---

# 6. Chunk：为什么一本 300 页手册不能每次整本送进去

如果一份资料只有两页，最简单的方法可能就是整份给模型。

但资料越来越多以后，每次都把全部内容送进 Context 会遇到：

- Token 增长；
- Prefill 变慢；
- 无关信息变多；
- 关键证据被淹没；
- 成本增加。

所以很多文档 RAG 会把长文档切成 Chunk。

可以用“书架”类比：

> 不需要每次为了查一句话，把整本书搬到桌上。

Chunk 的目的就是：

> **让系统能够检索到一个足够小、但仍然能独立理解的证据单元。**

【截图占位 KB-06｜同一文档：原文 → Heading-aware Chunk】

但不能简单说：

> 每 500 字切一刀。

好的 Chunk 通常需要考虑：

- 标题层级；
- 段落；
- 表格；
- 列表；
- 代码块；
- 语义完整性；
- 文档类型。

例如：

> “适用条件”切在一个 Chunk，“具体规则”被切到另一个 Chunk，

检索命中其中一个时，模型可能得到半句话。

因此：

> **Chunk 是知识工程，不只是字符串切割。**

---

# 7. Metadata：正文之外，机器还必须知道“这是谁的资料”

一条 Chunk 如果只剩正文：

> “系统默认超时时间为 30 秒。”

其实仍然不够。

至少还应该知道：

- 来自哪份文档；
- 哪一章节；
- 什么版本；
- 谁负责；
- 生效时间；
- 产品型号；
- 项目；
- 权限；
- 是否已过期。

这就是 Metadata。

对于部门知识库，Metadata 的价值非常大，因为很多检索问题其实应该先过滤：

> “只查当前型号。”

> “只查 2026 年有效版本。”

> “只查当前用户有权限看的资料。”

再做全文或向量搜索。

【图示占位 KB-07｜正文 Chunk + Metadata】

---

# 8. BM25 和 Embedding：为什么需要两种“找资料”的方式

这一部分不要从算法公式讲。

先问两个问题。

## 8.1 问题 A：我知道准确名字

例如：

> QWEN_CONTEXT_131072 这个字段在哪份文档？

或者：

> 错误码 SYNC_CONFLICT 的定义是什么？

这种场景有非常明确的词。

全文检索 / BM25 很擅长：

> **字面上就是这个词。**

【截图占位 KB-04A｜BM25 精确词命中】

## 8.2 问题 B：我只知道意思

例如原文写：

> “陈旧写入返回 409 SYNC_CONFLICT。”

用户问：

> 多设备同时修改时怎样避免后提交的数据把先提交的数据直接覆盖？

这时用户没有使用原文关键词。

Embedding / Vector Search 的优势是：

> **文本写法不同，但语义接近，也可以找到。**

【截图占位 KB-05｜同一 Corpus：关键词不一致但 Vector 命中】

## 8.3 为什么实际系统常用 Hybrid？

真实部门问题不会只属于一种类型。

所以常见做法是：

```text
BM25 / Full-text
+
Vector Search
↓
Candidate Set
↓
Rerank
```

这里不要给大家形成：

> Vector 比 BM25 高级。

更准确的是：

> **它们解决不同问题。**

---

# 9. Rerank：先找到一批，再重新判断谁最值得给模型看

假设检索已经找到 20 个 Chunk。

如果全部交给模型：

- Context 变长；
- 无关证据增加；
- 成本增加。

所以可以增加 Rerank：

> 对已经找到的候选，再更精细地判断和当前问题的相关性。

可以继续使用开卷考试类比：

```text
Retriever
= 先从书架上找出 20 页可能相关的资料

Reranker
= 再挑出最值得放到桌面上的 5 页
```

【图示占位 KB-10｜Retrieve Top-20 → Rerank → Top-5 Evidence】

---

# 10. 为什么 Context 很长仍然不能“全塞进去”

这是本讲需要重点讲透的一部分。

现在很多模型 Context Window 已经很大，很容易产生一个问题：

> 既然能放几十万 Token，为什么还要 RAG？

答案不是：

> 长上下文没用。

而是：

> **Context 容量和信息利用效率是两个不同问题。**

已有长上下文研究反复观察到几个现象：

- 信息位置会影响利用效果；
- Context 越长，并不保证检索和推理能力等比例提高；
- 即使正确证据已经在 Context 中，模型也可能没有稳定利用；
- 多条相似证据、无关证据会增加干扰。

这里可以提到 Lost in the Middle、RULER、NoLiMa、LongBench v2 等研究，但现场不展开论文细节。

【图示占位 KB-08｜External Retrieval Recall vs In-context Utilization】

【图示占位 KB-08B｜Lost in the Middle 直觉图】

本讲只让学员留下：

> **找到资料，是第一关；模型用好资料，是第二关。**

---

# 11. Context Budget 和 Evidence Budget：不是“越多越好”

现在把前面知识合起来。

一次问答可以理解成有一个有限“桌面”。

桌面上除了知识库证据，还可能有：

- System Prompt；
- 历史对话；
- 用户问题；
- Tool Result；
- Agent Plan；
- 代码片段。

所以要考虑 Context Budget。

而知识证据本身也应该控制 Evidence Budget。

【图示占位 KB-09｜Context Budget / Evidence Budget】

例如：

```text
候选检索结果：30 个 Chunk
↓
去重 / Filter
↓
Rerank
↓
最终 5～8 个关键证据
↓
LLM
```

结论：

> **知识库的目标不是尽可能多地把资料塞给模型，而是让最相关、最可信、当前有权限的证据进入 Context。**

---

# 12. Full Context、Pipeline RAG、Agentic Retrieval：三种给模型资料的方法

这部分帮助大家避免把“知识库”只理解成一种固定流程。

## 12.1 Full Context

如果资料很短：

> 直接把整份资料给模型可能是最简单、最可靠的方法。

不要为了“用了 RAG”而强行切 Chunk。

## 12.2 Pipeline RAG

典型固定流程：

```text
Question
→ Retriever
→ Top-K
→ Rerank
→ Context
→ Answer
```

适合：

- 大量文档；
- 问题相对稳定；
- 希望统一检索过程。

## 12.3 Agentic Retrieval

复杂任务中，Agent 可能不会只查一次。

例如：

> 当前 qwen3.6 是否已经适合部门 Agent 连续任务？

Agent 可以：

```text
先查共享知识库
↓
发现需要原始实测证据
↓
去 Git 找测试报告
↓
发现还需要当前运行状态
↓
调用 Metrics API
↓
交叉核验
↓
回答
```

【截图占位 KB-18｜Agent Tool Trace：KB → Git → API/Metrics】

这时 Retrieval 不再是一次固定流水线，而是：

> **模型根据中间证据决定下一步去哪里取证。**

---

# 13. Cherry Studio、Open WebUI、Agent：不要当成三个知识库世界

现在回到部门实际工具。

## 13.1 Cherry Studio：个人知识工作台

适合：

- 个人资料；
- 小规模项目资料；
- 临时知识库；
- 本地桌面使用；
- 快速测试 BM25 / Vector / Rerank。

【截图占位 KB-12｜Cherry Knowledge Base 总览】

【截图占位 KB-13｜Cherry Retrieval 配置 / 测试】

## 13.2 Open WebUI：共享知识入口

更适合：

- 集中式模型入口；
- 多用户；
- Shared Knowledge；
- 权限；
- 团队共享。

【截图占位 KB-15｜Open WebUI Shared Knowledge】

【截图占位 KB-16｜Open WebUI Knowledge / Retrieval 设置】

【截图占位 KB-21｜ACL / Group 权限】

## 13.3 Agent：知识编排层

Agent 的强项不是再建第三套孤立知识库。

而是可以组合：

```text
Shared KB
+
Workspace
+
Git
+
File Search
+
Database
+
API
+
MCP
```

根据任务逐步取证。

因此：

> **Agent 可以使用 RAG，但 Agent 不等于 RAG。**

【图示占位 KB-19｜同一 Source，Cherry / Open WebUI / Agent 三种入口】

---

# 14. 为什么三个 Demo 一定使用同一套资料？

如果 Cherry 用资料 A，Open WebUI 用资料 B，Agent 用资料 C，最后只能看到三个不同效果，无法知道差异来自哪里。

所以本培训固定：

> **Source of Truth 相同。**

只改变：

- Retrieval；
- Governance；
- Orchestration。

推荐 Demo Corpus 就使用本培训自己的 Qwen API 资料：

- API 测试报告；
- 模型接口说明；
- 部署说明；
- model-metric 说明；
- 一段相关代码。

固定一组 Benchmark Questions。

这样同一知识可以贯穿第一讲和第二讲。

---

# 15. 三层同源 Demo：现场真正怎么演

## Demo A：Cherry Studio——看检索算法

先用固定 Corpus 创建知识库。

### 问题 1：精确词

例如：

> Responses Vision 正式测试状态是什么？

观察 BM25。

### 问题 2：换一种说法

不要使用资料中的原词，问同一语义问题。

观察 Vector / Hybrid。

### 问题 3：跨文件

例如：

> 当前 Qwen 是否适合做带图片并调用工具的 Agent 任务？请给出证据。

观察多个 Chunk 如何进入答案。

【录屏占位 KB-R01｜Cherry 建库 → Parse/Chunk → Retrieval Test → Chat】

【录屏占位 KB-R02｜同问题 BM25 vs Embedding/Hybrid/Rerank】

---

## Demo B：Open WebUI——看共享和治理

同一批资料进入 Shared Knowledge。

重点不是再重复讲 Embedding。

展示：

- 创建 Shared KB；
- 用户 / Group；
- Knowledge 绑定；
- 检索；
- 引用；
- ACL。

【录屏占位 KB-R03｜Open WebUI Shared KB + ACL】

结论：

> **共享知识库的价值不仅是 Retrieval，还有 Governance。**

---

## Demo C：Agent——看多源逐步取证

给 Agent：

> 基于共享知识和当前仓库证据，判断内网 Qwen 当前哪些 Agent 能力已经验证、哪些仍需要进一步验证。所有结论标明来源。

预期：

```text
Shared KB
↓
得到总体结论
↓
Agent 判断证据不足
↓
Search / Read Git
↓
找到实测报告
↓
必要时调用 API / Metrics
↓
交叉核验
↓
Final Answer
```

【录屏占位 KB-R05｜Agent：Shared KB → Git → API/Metrics → 引用回答】

这一段是第二讲非常重要的 Demo，因为它把知识库从：

> 一个聊天附件

提升成：

> **Agent 可调用的部门知识基础设施。**

---

# 16. 版本冲突 Demo：这是最值得给领导和技术人员看的失败案例

准备两份内容几乎一样的文档：

```text
部署规范 v1：端口 8000
部署规范 v2：端口 8765
```

故意都放入知识库。

问：

> 当前正式部署端口是什么？

如果没有 Metadata / Version / Source of Truth 约束：

Retriever 可能同时返回两个版本。

【截图占位 KB-20｜旧版与新版同时被检索】

然后加入：

- current=true；
- version；
- effective_date；
- source status。

再问一次。

【录屏占位 KB-R06｜版本冲突 → 加版本治理 → 回归】

这比单纯讲“Metadata 很重要”更有说服力。

---

# 17. No-answer Demo：知识库也应该会说“不知道”

准备一个 Corpus 中根本不存在的问题。

错误系统会：

> 利用相似 Chunk 拼一个看似合理的答案。

更可靠的知识库应该做到：

- Retrieval 证据不足；
- 明确指出没有找到可靠依据；
- 不用模型常识冒充内部事实。

这一点要纳入验收。

知识库好不好，不只是看：

> 有答案的问题答对多少。

也要看：

> 没有答案的问题会不会乱答。

---

# 18. 权限必须发生在“证据进入模型”之前

假设员工 A 无权查看某项目资料。

错误做法：

```text
先从全库检索
→ 把机密 Chunk 放入 Context
→ 再告诉模型“不要回答”
```

此时信息实际上已经进入模型上下文。

正确逻辑应接近：

```text
User Identity
↓
ACL Filter
↓
Authorized Corpus
↓
Retrieval
↓
Context
↓
LLM
```

【图示占位 KB-21｜ACL before Retrieval】

结论：

> **权限控制应该尽量在 Retrieval / Data Access 层生效，而不是只靠 Prompt。**

---

# 19. 知识库不能保证“不幻觉”

这里也要避免向领导和学员形成错误预期。

知识库可以显著提升：

- 内部知识可用性；
- 新知识获取；
- 引用；
- 可追溯性。

但不能自动保证：

> 每个答案 100% 正确。

因为还可能发生：

- Source 本身错误；
- Parse 错误；
- Retrieval 漏召回；
- 版本错误；
- Context 过载；
- 模型理解错误；
- 引用和结论不匹配。

因此知识库需要评测和验收。

---

# 20. 部门知识库到底应该怎么建？

到这里再给落地方案。

不要从：

> “我们选哪个向量数据库？”

开始。

建议按照六步。

## 第一步：盘点 Source of Truth

建立知识资产清单：

```text
知识域
→ Source
→ Owner
→ 更新频率
→ 权限
→ 当前版本规则
```

## 第二步：按知识类型决定访问机制

建立矩阵：

| 知识类型 | 推荐主要方式 |
|---|---|
| 制度/规范/手册 | Parse + RAG |
| 精确型号/错误码 | Full-text / BM25 |
| 语义问答 | Vector / Hybrid |
| Git 代码 | Search / Read / Git |
| Excel/CSV 大数据 | Data Tool / Python / SQL |
| 数据库 | SQL / API |
| 实时系统 | API / MCP |
| 日志/指标 | Search / Monitoring |
| 图片/图纸 | Multimodal + Metadata |

## 第三步：定义入库规范

包括：

- 标题；
- Owner；
- Version；
- effective_date；
- source_uri；
- ACL；
- product / project；
- document_type；
- current / stale。

## 第四步：建立 Retrieval

根据场景选择：

- BM25；
- Vector；
- Hybrid；
- Filter；
- Rerank。

不要一次把参数调到“最好”，而是基于 Benchmark 测。

## 第五步：控制 Context

- Top-K；
- Deduplicate；
- Rerank；
- Evidence Budget；
- Citation。

## 第六步：建立验收测试集

知识库上线前必须有固定问题集。

---

# 21. 知识库验收，不要只做“感觉挺好”

建议至少覆盖以下问题类型：

## Answerable

资料里明确存在答案。

## No-answer

资料里不存在。

## Exact ID

型号、错误码、编号。

## Paraphrase

换一种说法。

## Long document

答案位于长文档中间。

## Cross-document

需要多份资料组合。

## Version conflict

旧版 + 新版。

## ACL

不同权限用户。

## Citation

答案必须能定位证据。

## Dynamic fact

如果属于实时信息，应明确转去 API，而不是使用旧索引。

验收可以记录：

```text
Question
Expected Source
Retrieved Source
Answer
Citation
Pass / Fail
Failure Type
```

让知识库从：

> “大家试试看挺好用”

变成：

> **可以回归测试的系统。**

---

# 22. 部门知识架构最终希望长成什么样

最终不是绑定 Cherry，也不是绑定 Open WebUI。

更合理的是：

```text
               Department Source of Truth
      ┌──────────────┼───────────────┐
      ↓              ↓               ↓
  Documents         Git           DB / API
      │              │               │
 Parse/Chunk     Search/Read       Query
      │              │               │
      └────── Knowledge Access ──────┘
                     │
        ACL / Version / Metadata
                     │
           Retrieval / Evidence
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
     Cherry      Open WebUI      Agent
                                   │
                                App/Task
```

【图示占位 KB-17 / KB-19｜部门统一知识架构】

这里给出本讲最重要的一句话：

> **知识原文是资产，索引是派生物，客户端只是入口。**

---

# 23. 本讲最后让大家带走八个认识

1. **知识库建设先从需求和 Source of Truth 开始，不从向量库开始。**
2. **不同知识类型需要不同访问机制。**
3. **RAG 是“先检索证据，再给模型回答”，不等于 Vector Search。**
4. **BM25、Vector、Hybrid 是互补，不是简单的高低级关系。**
5. **Context Window 很长，不等于有效知识容量无限。**
6. **权限、版本、过期、冲突属于知识库核心工程问题。**
7. **Cherry、Open WebUI、Agent 应尽量复用同一批权威知识，而不是各建孤岛。**
8. **知识库必须有固定测试集和引用证据，才能真正用于部门工作。**

---

# 24. 第二讲截图执行清单

## 24.1 P0 必拍

### KB-01：裸模型 vs 带资料

固定同一内部问题。

左侧：

> 不提供资料。

右侧：

> 带当前实测报告。

目标：

> 一眼看出外部知识的价值。

### KB-06A：PDF → Parsed Text

选一页有表格或复杂结构的真实非敏感资料。

至少截：

1. 原始 PDF；
2. Parse 后文本/结构。

### KB-06：Chunk

最好使用带标题层级的 Markdown / PDF。

展示：

- 原文；
- Chunk 边界；
- Metadata。

### KB-04A / KB-05：BM25 vs Vector

必须使用同一个 Corpus。

准备：

- 一个精确关键词问题；
- 一个语义改写问题。

### KB-10：Rerank

如果工具能展示候选分数，截：

- 初始候选；
- rerank 后顺序。

如果工具不显示，制作基于实测结果的图示，但注明“示意”。

### KB-12～13：Cherry

拍：

- Knowledge Base；
- Retrieval Config / Test；
- 引用结果。

### KB-15～16：Open WebUI

拍：

- Shared Knowledge；
- 绑定入口；
- Retrieval / Citation。

### KB-21：ACL

拍用户/Group 和知识权限配置，敏感账号名称脱敏。

### KB-18：Agent 多源取证

要求画面中同时能看到：

- KB Search；
- File/Git Search；
- API / Metrics Tool；
- 最终引用。

---

# 25. 第二讲录屏执行脚本

## KB-R01：Cherry 建库完整流程

建议原始录屏 3～5 分钟，后期剪成 60～90 秒。

步骤：

1. 创建知识库；
2. 导入固定资料；
3. 展示 Parse / Chunk 设置；
4. 做 Retrieval Test；
5. 进入 Chat；
6. 查看引用。

目的：

> 让大家看到“上传文件”中间实际还有处理过程。

## KB-R02：BM25 vs Vector / Hybrid

固定两个问题。

过程：

1. 只启用 BM25 或关键词模式；
2. 问精确词问题；
3. 问语义改写问题；
4. 切 Vector / Hybrid；
5. 重复；
6. 对比召回。

不要为了展示效果临时换 Corpus。

## KB-R03：Open WebUI Shared KB + ACL

步骤：

1. 管理员创建 / 查看 Shared KB；
2. 绑定 Group；
3. 用户 A 查询成功；
4. 若条件允许，用户 B 无权限或看不到；
5. 展示引用。

## KB-R05：Agent 多源逐步取证

固定任务：

> “判断当前内网 Qwen 哪些 Agent 能力已有实测证据，哪些还没有。必须基于共享资料和仓库证据回答。”

录屏必须保留：

- 先 KB；
- 再 Git；
- 再 API/Metrics（如可用）；
- 最终答案和引用。

这条录屏是第二讲最重要素材之一。

## KB-R06：版本冲突 / No-answer

可以分两段。

版本冲突：

1. 同时放入 v1 / v2；
2. 观察不加 Filter 的结果；
3. 加 Version / current Metadata；
4. 回归。

No-answer：

1. 问 Corpus 中没有的问题；
2. 检查系统是否明确证据不足。

---

# 26. 第二讲现场 Demo 与备用策略

建议真正现场操作：

1. Cherry Retrieval Test；
2. 同一问题 BM25 vs Hybrid；
3. Agent 多源检索。

Open WebUI ACL、Parse、版本冲突等更适合预录，因为配置过程可能较长。

每个 Demo 都准备：

- 最终截图；
- 60～90 秒剪辑版；
- 原始完整录屏。

---

# 27. 第二讲结束后应形成的部门建设输出

这一讲不应只留下 PPT。

建议培训后继续沉淀七项资产：

1. **知识资产分类表**；
2. **Source of Truth 清单**；
3. **文档入库规范**；
4. **知识类型 → Retrieval / Access 方式矩阵**；
5. **ACL / Version / Stale 治理规则**；
6. **知识库 Benchmark / Acceptance Set**；
7. **Cherry / Open WebUI / Agent 共用的部门 Knowledge Architecture**。

做到这里，第二讲才真正从“知识库科普”变成部门知识库建设的起点。
