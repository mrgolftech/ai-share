# 教学版讲义：从“把资料给 AI”到“真正可用的部门知识库”

> 场次：系列培训第 2 次（独立专题）  
> 主题：部门知识库建设——从知识资产到可治理的 AI 知识基础设施  
> 版本：Teaching Draft v0.3  
> 日期：2026-09-30  
> 面向对象：部门技术人员、知识库建设人员、AI 应用开发人员  
> 定位：**用于培训讲解的教学版，不替代完整研究稿。**  
> 完整技术稿：`docs/chapters/03-department-knowledge-base.md`  
> 证据基线：`docs/references/knowledge-base-rag-evidence-2026-09.md`  
> 架构稿：`docs/architecture/department-knowledge-architecture.md`

---

# -1. 独立培训定位

这一章从原来的“Chat → Agent 过渡内容”中独立出来，作为系列培训第 2 次完整授课。

原因不是 RAG 概念很多，而是部门知识库建设需要同时解决：

```text
知识资产
+ 数据源
+ 文档规范
+ 解析
+ 索引
+ Retrieval
+ Context
+ 权限
+ 版本
+ 引用
+ 评测
+ 维护治理
+ 多种 AI 使用入口
```

这些问题已经超过一个 Chat 软件功能介绍的范围。

本场培训结束后，目标不是让学员“会上传 PDF”，而是能够回答：

1. 部门有哪些知识资产；
2. 哪份资料是 Source of Truth；
3. 哪些内容应该全文搜索、哪些适合向量检索、哪些应该直接读文件/API/数据库；
4. 文档进入知识库前应该怎样规范化；
5. 怎样处理版本、权限、重复、冲突和过期资料；
6. Cherry Studio、Open WebUI、Agent 应怎样共用同一套知识资产；
7. 怎样设计测试集证明知识库确实可用；
8. 部门最终应该建设怎样的知识架构，而不是绑定某一个客户端。

> **这是一场“知识工程与治理”培训，不是一场“向量数据库入门课”。**

---

# 0. 这份讲义怎么用

现有 `03-department-knowledge-base.md` 保留为完整技术稿，里面包含较多架构、评测、权限、GraphRAG、模型选型等细节。

这份教学版重新组织，不追求“知识点最多”，而追求：

> **让第一次系统接触知识库 / RAG 的工程师，沿着一条主线真正理解为什么这样设计。**

教学主线：

```text
模型不知道部门资料
        ↓
把整份资料塞进 Context 行不行？
        ↓
资料多了以后怎么办？
        ↓
需要 Retrieval
        ↓
RAG 到底是什么？
        ↓
BM25 / Vector / Hybrid 分别解决什么问题？
        ↓
文档为什么要 Parse / Chunk / Metadata？
        ↓
检索到了为什么还不能结束？
        ↓
Context Window ≠ 有效知识容量
        ↓
需要 Rerank + Evidence Budget
        ↓
不同知识采用不同访问方式
        ↓
Cherry / Open WebUI / Agent 分别怎么用？
        ↓
部门知识库到底应该建设什么？
```

本章采用：

> **一个问题 → 一个例子 → 一个原理 → 一个结论**

截图和实测暂不强行补齐，统一保留占位，后续根据实际部署界面和验证结果替换。

## 0.1 第一次听这一章，只需要先记住五个词

这一章会出现不少英文术语。第一次听不要求记定义，先把下面五个词和一个直觉对应起来：

| 词 | 先这样理解就够了 |
|---|---|
| **Source** | 原始资料从哪里来，哪份才算真的 |
| **Retrieval** | 先把可能有用的资料找出来 |
| **Chunk** | 为了方便查找，把长资料拆成能独立理解的小块 |
| **Rerank** | 已经找出一批候选以后，再重新排一次优先级 |
| **Context** | 最终真正交给 LLM 阅读的内容 |

整章其实都在回答一件事：

> **怎样从大量真实资料里，挑出“这一次回答真正需要看的那一小部分”，并且让它可靠地进入模型。**

如果后面的 BM25、Embedding、Top-K 一时记不住没有关系，只要一直抓住这条主线即可。

## 0.2 用“开卷考试”先建立一个直觉

可以把 LLM 回答知识库问题先类比成一次开卷考试。

- **Source**：书架上的全部教材和资料；
- **Retrieval**：先找到可能相关的几本书、几页内容；
- **Chunk**：事先给长书做好可检索的小节；
- **Rerank**：把最相关的几页放到最前面；
- **Context**：最终摆到考生桌面上、允许本次作答阅读的材料。

这时候很容易理解两个问题：

第一，**书架上有正确答案，不代表你一定翻到了它。**

第二，**桌面上摆 200 页资料，也不代表比摆 5 页最关键的资料答得更好。**

后面整章的技术设计，基本都是围绕这两个问题展开。

> 类比只用于建立直觉。真实 RAG 系统还要处理版本、权限、解析、索引、成本和模型能力等工程问题。

---



# 1. 先从一个最简单的问题开始：模型为什么需要知识库？

假设我们问内网模型：

> 我们当前 Qwen 服务的上下文长度是多少？Thinking 接口实测有什么注意事项？

如果这些资料：

- 不在模型训练数据中；
- 是部门内部资料；
- 最近刚刚更新；
- 或者来自我们自己的 API 实测；

模型就不能只依靠参数里的“已有知识”稳定回答。

最直接的方法是：

```text
问题
+
相关资料
↓
一起发给 LLM
↓
根据资料回答
```

这就是知识库问题最原始的起点。

## 1.1 为什么不能只依赖模型自己记住？

部门知识有几个明显特点：

- 很多内容不公开；
- 更新频繁；
- 有版本；
- 有权限；
- 需要引用原文；
- 有些内容根本不是自然语言文档，而是代码、数据库、API、日志和实时指标。

因此：

> **部门知识不能只存在模型参数里，必须有模型之外的权威知识源。**

这也是经典 RAG 工作提出的重要动机之一：让生成模型能够访问外部、可更新、可追溯的知识。

【截图占位 KB-01：一个“直接问模型”和“带内部资料问模型”的对比画面】

讲师强调：

> **知识库首先解决的不是“向量化”，而是“模型怎样可靠获得它原本不知道的外部知识”。**

---

# 2. 所以，部门知识库到底是什么？

很多人第一次接触 RAG，容易把知识库理解成：

```text
上传 PDF
→ Embedding
→ Vector DB
→ Chat
```

这个理解太窄。

更适合部门建设的定义是：

> **知识库是一套让 Chat、应用和 Agent 能够可靠访问部门知识资产的体系。**

完整链路更接近：

```text
权威知识源
Git / Wiki / DMS / PDF / DB / API
        ↓
解析与标准化
Parse / OCR / Metadata
        ↓
检索索引
BM25 / Full-text / Vector
        ↓
检索与上下文控制
Rerank / ACL / Version / Deduplicate
        ↓
知识访问方式
Search / Read / SQL / API / MCP
        ↓
使用入口
Open WebUI / Cherry / Agent / 业务应用
```

这里最重要的一句话：

> **知识原文是资产，检索索引是派生物，客户端只是入口。**

换一个 Embedding 模型，可以重建 Vector Index。

换 Cherry Studio、Open WebUI 或 Agent，不应该重新建设一遍部门知识。

【图示占位 KB-02：Source → Parse → Index → Context Control → Client 五层知识架构】

---

# 3. 第一个设计原则：不同知识，不要用同一种方法处理

这是部门知识库设计里最容易犯的错误：

> 为了统一，把所有东西都转成 PDF，再全部向量化。

实际工程资料差异很大。

## 3.1 自然语言文档

例如：

- 制度；
- 规范；
- 产品手册；
- 技术方案；
- Wiki；
- FAQ；
- 测试报告中的结论部分。

适合：

```text
Parse
→ Chunk
→ BM25 / Vector / Hybrid
→ Rerank
→ LLM
```

这类内容是传统 RAG 最典型的对象。

## 3.2 代码和配置

例如：

- Python / C / C++；
- YAML；
- Docker Compose；
- API 配置；
- 错误码；
- 函数名；
- 文件路径。

工程上通常优先：

```text
tree / glob
→ grep / rg
→ read
→ LSP / references
→ Git history
```

原因很简单：

用户问：

> CFG_LDO1 在哪里配置？

这类问题首先是精确字符串和代码结构问题，不一定需要先把整个仓库做成向量库。

语义代码搜索可以作为补充，但不是所有 Repo 的默认前提。

## 3.3 Excel / CSV / 测试数据

如果问题是：

> 过去 30 次测试里平均 TTFT 是多少？

正确主路径通常是：

```text
CSV / XLSX / DB
→ Python / SQL
→ 计算
→ LLM 解释
```

而不是：

```text
把 30 万行表格转成文本
→ Vector Search
→ 让 LLM 猜平均值
```

但是：

- 字段说明；
- 指标口径；
- 异常备注；
- 测试结论；

仍然可以进入文档知识库。

## 3.4 实时信息

例如：

- 当前 GPU / NPU 利用率；
- 服务实例状态；
- 最新 metrics；
- CMDB 当前资产；
- 当前 GitHub Issue 状态。

应该优先：

```text
API / SQL / MCP / Tool
→ 当前事实
→ LLM
```

静态知识库不应该成为实时事实的唯一来源。

## 3.5 图片、图纸、PPT

这类资料的问题不是“有没有 Embedding”，而是：

> **机器到底有没有正确读懂内容。**

例如一张架构图只抽取文字，可能会丢失：

- 箭头；
- 拓扑关系；
- 层级；
- 连线含义。

因此重要图片应保留原图，并附：

- 标题；
- 来源；
- 版本；
- 文字说明；
- 关键结论。

【截图占位 KB-03：同一知识库里 PDF、Markdown、Excel、代码、API 的不同处理路径示意】

本节结论：

> **知识库设计首先是“知识类型设计”，不是“Embedding 模型选型”。**

---

# 4. RAG 到底是什么？先把“查资料”和“回答问题”分开

先不要把 RAG 理解成某一种数据库。

假设用户问：

> 我们当前 Qwen 服务的 Thinking 接口有什么实测注意事项？

模型自己不知道部门内部实测结果，于是系统先做一件很朴素的事：

```text
第 1 步：查资料
找到与 Thinking、Qwen、接口实测相关的内容

第 2 步：把找到的资料交给模型
作为本轮额外 Context

第 3 步：让模型根据这些资料回答
```

这三步就是 RAG 最核心的结构：

> **Retrieval → Augmentation → Generation**

翻成更容易记的话：

> **先查，再给，再答。**

其中最容易产生误解的是第一步：

> **Retrieval 不等于 Vector Search。**

“查资料”可以有很多方式：

- 搜关键词；
- 做全文搜索；
- 做向量语义搜索；
- 两种一起搜；
- grep 代码；
- 查数据库；
- 调 API；
- 让 Agent 自己继续找。

所以这一章后面所有检索技术，其实都只是回答：

> **第一步“怎么查”更合适？**

【图示占位 KB-04A：RAG 三步图——先查、再给、再答】

---

# 5. BM25、Embedding、Hybrid：先理解“为什么要有两种查法”

这里先不讲算法公式。

只看两个非常不同的问题。

## 5.1 第一类：用户知道准确名字

文档写：

```text
当前模型 max_model_len 为 131072。
```

用户问：

> max_model_len 是多少？

这里最有价值的是：

- `max_model_len` 这个精确字符串；
- 型号；
- API Path；
- 错误码；
- 标准编号。

这类检索更像：

> **“帮我找出现过这个词的地方。”**

BM25 / Full-text 属于这一类能力。

可以先把 BM25 理解为：

> **很会找“字面上相关”的内容。**

它不是“老旧搜索”，在工程技术资料里反而非常重要，因为大量关键信息就是精确词。

## 5.2 第二类：用户只知道意思，不知道原文怎么写

文档写：

```text
长上下文会导致首 Token 延迟明显增加。
```

用户问：

> 为什么一次塞很多材料以后，模型半天才开始出字？

用户没有说：

- 长上下文；
- 首 Token；
- TTFT。

但意思是相关的。

Embedding 的价值就在这里。

可以先把 Embedding 理解成：

> **把一段文字变成一组便于比较“语义接近程度”的数值表示。**

这里最需要讲清的一点：

> **Embedding 不是把知识“存进模型”，也不是知识本身。**

原始知识仍然是：

```text
文档 / Git / Wiki / PDF / 数据
```

Embedding 只是为了让系统更容易回答：

> **“哪几段文字和这个问题意思比较接近？”**

因此 Vector Index 更像一种：

> **语义目录 / 语义索引。**

换 Embedding 模型以后，这个索引通常可以重新生成；原始资料不能因此丢掉。

【图示占位 KB-04B：原文 → Embedding → Vector Index；强调 Index 可重建、Source 才是资产】

## 5.3 为什么实际系统常把两种查法一起用？

部门技术资料经常长这样：

```text
“Qwen3.6 在 /v1/messages/count_tokens 接口返回 token 数量，
长 Context 下 TTFT 可能明显增加……”
```

一句话里同时有：

- 自然语言；
- 型号；
- API Path；
- 英文缩写；
- 精确术语。

如果只做关键词搜索，可能漏掉用户的语义改写。

如果只做语义搜索，又可能对：

- 错误码；
- 型号；
- API；
- 标准编号；

不如精确词检索稳定。

所以工程上经常采用：

```text
                 用户问题
                /       \
        BM25 / Fulltext   Vector
          找字面相关      找语义相关
                \       /
                 候选集合
                    ↓
                  Rerank
                    ↓
             少量高质量证据
```

这就是 Hybrid Retrieval 的基本直觉：

> **两种查法互补，而不是谁取代谁。**

公开研究给出的稳妥结论也不是“Vector 一定更高级”。

BEIR 等跨域检索研究说明 BM25 仍然是很强的基线；Dense Retrieval、Rerank 的收益与具体语料和问题类型有关。

所以培训里不让学员背：

> BM25 < Vector < Hybrid。

而是建立：

> **精确词多不多？用户会不会换一种说法？两种需求是不是同时存在？**

再决定检索方式。

【截图占位 KB-04：Cherry Studio Embedding=None / BM25 配置界面】

【截图占位 KB-05：同一问题 BM25 与 Embedding Retrieval Test 对比】

---

# 6. Parse 和 Chunk：为什么“有文件”还不等于“机器能查”

把一个 PDF 上传到知识库，并不意味着系统已经获得了里面的知识。

中间至少还有两件事：

```text
文件
↓
Parse：先把内容正确读出来
↓
Chunk：再把长内容拆成适合查找的知识块
↓
Index：给这些知识块建立检索入口
```

## 6.1 Parse：先确保“读对了”

例如一个扫描 PDF：

人眼看到的是正常表格，但机器抽取后可能变成：

```text
列顺序错乱
页眉反复插入正文
表头和数据分家
图片里的文字完全丢失
```

如果 Parse 已经错了，后面再换更好的 Embedding、Rerank 或 LLM，也无法凭空恢复被解析丢掉的事实。

所以一个很重要的工程顺序是：

> **先看 Parsed Text 对不对，再讨论检索效果。**

【截图占位 KB-06A：原 PDF 页面 vs Parsed Text 对照】

## 6.2 Chunk：一本 300 页手册，不能每次整本送进去

假设用户只问：

> 某接口超时时间是多少？

整本 300 页都交给模型显然很浪费。

所以通常会把长文档拆成：

```text
第 1 章
  ├─ 1.1 ...
  ├─ 1.2 ...
第 2 章
  ├─ 2.1 ...
  └─ 2.2 ...
```

让检索器可以找到其中少数相关块。

这就是 Chunk。

可以先把 Chunk 理解成：

> **为了让机器查资料而准备的“可独立阅读的小节”。**

## 6.3 为什么不能简单“每 500 字切一刀”？

例如原文：

```text
3.2 API 调用限制
前置条件……
参数……
超时时间……
异常处理……
```

如果机械地从“超时时间”前面切开，模型虽然看到了：

> 超时 30 秒。

却可能不知道：

- 哪个 API；
- 在什么条件下；
- 对哪个版本；
- 例外是什么。

所以 Chunk 最重要的不是固定长度，而是：

> **尽量保持一个知识块可以脱离其他页面被正确理解。**

对技术文档，经常需要一起保留：

- 章节标题；
- Heading Path；
- 文档名；
- Version；
- Parent Section；
- 必要的相邻内容。

## 6.4 Chunk 太小和太大都不好

可以用一句话记：

> **太小会“断章取义”，太大会“夹带太多无关内容”。**

太小：

- 条件和结论被拆开；
- 表头和数据分开；
- API 与参数分开。

太大：

- 检索不精准；
- 无关内容更多；
- 最终 Context 更长。

因此 Chunk 的目标不是：

> 越小越精准。

而是：

> **尽量形成“刚好能独立表达一个知识点”的单元。**

【截图占位 KB-06：Cherry / Open WebUI Parsed Text 与 Chunk 查看界面】

---

# 7. Metadata 为什么和正文一样重要？

知识库最危险的问题不一定是“搜不到”，也可能是：

> 搜到了错误版本。

例如同时存在：

```text
设计方案 v1
设计方案 v2
会议纪要
旧 PPT
个人笔记
最终批准版
```

它们都可能包含非常相似的文字。

单纯做语义相似搜索，很可能全部召回。

所以知识不能只有正文，还需要 Metadata。

建议至少考虑：

```text
title
owner
project
document_type
version
updated_at
status
classification
effective_from
expires_at
supersedes
superseded_by
```

这些 Metadata 可以帮助系统先做：

```text
权限过滤
版本过滤
状态过滤
项目过滤
时间过滤
```

再进入语义检索和 LLM。

本节结论：

> **知识库不是只有“内容相似度”，还要知道这份内容是谁的、哪一版、是否有效、谁有权看。**

【截图占位 KB-07：同一文档 v1 / v2 / obsolete Metadata 示例】

---

# 8. Retriever 找到了，为什么还不算结束？

到这里很容易产生一个新的误解：

> 只要 Retrieval 把正确 Chunk 找到了，后面就万事大吉。

实际上有两道完全不同的关。

## 8.1 第一关：系统有没有把资料找到？

例如正确答案在：

`qwen-api.md`

但 Top-5 里一个相关 Chunk 都没有。

这是：

> **External Retrieval Recall 问题。**

也就是：

> **外部搜索有没有把证据召回。**

## 8.2 第二关：资料已经给了模型，模型能不能真的用好？

假设 Top-5 已经包含正确答案。

模型还必须：

- 在 Context 中找到它；
- 理解它；
- 和其他证据建立关系；
- 排除干扰项；
- 判断哪个版本更新；
- 最后把证据用于回答。

这是：

> **In-context Retrieval / Context Utilization 问题。**

这两个问题不要混在一起。

可以用前面的开卷考试类比：

```text
第一关：
正确教材有没有被拿到桌面上？

第二关：
桌面上的资料很多时，
考生能不能快速找到并正确使用关键页？
```

所以：

> **“检索命中”是必要条件，但不是最终回答可靠的充分条件。**

【图示占位 KB-08：两道关——External Retrieval vs In-context Utilization】

---

# 9. Context Window 很长，为什么仍然不能“能塞多少塞多少”？

这是这一章最值得建立的第二个核心认知。

模型可能标称：

```text
128K
256K
1M Context
```

它首先说明：

> **接口允许接收这么长的输入。**

但它不能自动证明：

> **模型在整个长度范围内，对任意位置、任意数量的证据、任意复杂任务，都能保持同样稳定的利用能力。**

## 9.1 先不用记论文名，只记住公开研究反复观察到三个现象

**现象一：信息放在哪里会影响模型使用。**

一些长上下文研究观察到，相关信息在中间位置时，利用效果可能比开头或结尾差。

**现象二：简单“找针”不代表真实长文档能力。**

模型可能很会在十万字里找一个完全相同的特殊字符串，但当任务变成：

- 多个证据；
- 多跳关系；
- 语义改写；
- 代码；
- 多文档综合；

效果会明显不同。

**现象三：即使正确证据已经给进 Context，输入继续变长也可能让任务表现下降。**

这意味着：

> **长 Context 的问题不只发生在 Retriever，也发生在模型最终阅读和推理阶段。**

## 9.2 这些结论有什么研究依据？

这里给学员知道“不是我们凭经验猜的”即可，不需要现场展开每篇论文的方法。

- **Lost in the Middle（TACL 2024）**：研究长上下文中相关信息位置与利用效果；
- **RULER（2024）**：说明简单 Needle-in-a-Haystack 不能充分代表真实 Effective Context；
- **NoLiMa（ICML 2025）**：在缺少明显字面匹配时，长上下文检索明显更难；
- **LongBench v2（ACL 2025）**：把评估扩展到更真实的长文档、多文档、代码和结构化任务；
- **Context Length Alone Hurts LLM Performance Despite Perfect Retrieval（Findings of EMNLP 2025）**：在“正确证据已经提供”的条件下，仍观察到随 Context 增长的性能下降。

完整数字、实验条件和证据等级统一放在：

`docs/references/knowledge-base-rag-evidence-2026-09.md`

培训主线只留下：

> **Context Window 是容量上限，不是“有效知识容量”的保证。**

【图示占位 KB-08B：标称 128K Context Window vs 实际高价值 Evidence 区域的概念图】

---

# 10. Top-K、Rerank、Evidence Budget：其实都在解决“桌面别堆太多资料”

假设一次搜索找到了 30 个候选 Chunk。

最简单的做法是：

```text
30 个全部送给 LLM
```

但里面可能同时有：

- 2 个真正关键证据；
- 8 个内容重复；
- 5 个只沾一点边；
- 3 个旧版本；
- 其他项目的同名内容。

问题就出现了。

## 10.1 Top-K 是什么？

Top-K 可以先理解成：

> **“最终取前几个结果”。**

例如：

```text
Top-3
Top-5
Top-10
```

很多初学者会直觉认为：

> Top-K 越大越保险。

因为更多结果似乎意味着更不容易漏。

但另一面是：

> **拿进来的无关内容、重复内容和冲突内容也会更多。**

所以 Top-K 不是“越大越好”的旋钮，而是：

> **漏证据风险 与 Context Pollution 风险之间的权衡。**

## 10.2 Rerank 是什么？

第一轮检索往往更强调：

> **先别漏掉候选。**

Rerank 则像第二轮筛选：

> **“这 30 个候选里，哪几个最值得真正交给模型？”**

因此可以把流程想成：

```text
第一次搜索
→ 找 30 个“可能相关”

Rerank
→ 重新认真比较这 30 个

最终
→ 只留下 5 个真正高价值证据
```

所以 Rerank 的价值不只是“排名更准”。

它还有一个很重要的作用：

> **帮助把较大的 Candidate Set 压缩成较小的 Evidence Set。**

【截图占位 KB-10：Rerank 配置与 Top-K 参数界面】

## 10.3 Evidence Budget 是什么？

这是教学里最值得留下的新概念。

可以继续用开卷考试类比。

桌面面积是有限的。

你真正关心的不是：

> 一共从书架搬来了多少页。

而是：

> **桌面上最终留下的这些页，是否足够回答问题，而且尽量没有废纸。**

所以 Evidence Budget 可以先理解成：

> **本轮回答允许交给模型的“有效证据预算”。**

它不一定只是一个固定 Token 数。

实际还涉及：

- 哪些证据必须保留；
- 重复内容能否去掉；
- 旧版本能否过滤；
- 相邻 Chunk 是否需要合并；
- 是否还要保留引用信息；
- 多文档问题是否需要多个来源。

完整流程因此更像：

```text
Broad Retrieval
先尽量别漏
      ↓
Rerank
重新排序
      ↓
ACL / Version Filter
不能看的、过期的先去掉
      ↓
Deduplicate / Merge
重复的去掉，必要邻接内容合并
      ↓
Evidence Budget
决定本轮真正给多少高价值证据
      ↓
LLM
```

一句话：

> **Retrieval 负责“找”，Evidence Budget 负责“克制”。**

【图示占位 KB-09：30 Candidates → 筛选 → 5 Evidence Chunks → LLM】

---

# 11. 现在回头看 Chunk：它为什么和长 Context 是一回事？

Chunk 不是孤立的“文档切分参数”。

它会直接影响：

```text
检索精度
+
最终送进 Context 的长度
```

Chunk 太大：

> 找到一段有用内容，同时带进大量无关内容。

Chunk 太小：

> 找到一句答案，但上下文不足，无法正确解释。

因此一个更好的思路是：

```text
先用较小的知识块准确定位
        ↓
如果需要
        ↓
再读取 Parent Section / Neighbor Chunk
        ↓
只扩展真正需要的上下文
```

这也是很多 Agent 工作方式看起来不像传统 RAG 的原因：

它不是一次把很多 Chunk 全塞进 Prompt，而是：

> **先找到位置，再按需要读更多。**

---

# 12. Full Context、Pipeline RAG、Agentic Retrieval：其实是三种“给模型资料”的策略

到这里再讲这三个词，学员会容易很多。

| 方式 | 直觉 | 适合什么 | 主要风险 |
|---|---|---|---|
| **Full Context** | 整份资料直接给 | 很短、每次都必须完整看的规则/小文档 | 资料一大就浪费 Context |
| **Pipeline RAG** | 先固定搜索，再给少量 Top Evidence | FAQ、制度、手册、高频稳定问答 | 一次检索可能不足以处理复杂问题 |
| **Agentic Retrieval** | 模型边查边判断，还缺什么再继续查 | 跨文档、代码+日志+API、多步调查 | 更慢、更贵、更依赖模型能力 |

## 12.1 Full Context：短资料可以不必折腾检索

例如：

- 一页编码规范；
- 很短的系统规则；
- 小型术语表。

可以直接：

```text
完整资料 + 问题 → LLM
```

它的优势是简单，而且没有 Retriever 漏召回问题。

但判断标准不是：

> 只要 Context Window 放得下就全部塞。

而应该是：

> **资料是否真的短、每次是否都必须完整看到、无关内容比例是否很低。**

## 12.2 Pipeline RAG：像“固定流程查资料”

典型：

```text
Question
→ Search
→ Rerank
→ Top Evidence
→ LLM
```

适合：

- 制度问答；
- FAQ；
- 产品手册；
- 边界清晰的知识问答。

可以理解为：

> **每次都按一套固定检索流水线工作。**

优点是快、稳定、容易测试。

## 12.3 Agentic Retrieval：像“调查员逐步取证”

复杂问题例如：

> 最近 API 为什么变慢？和部署配置、代码修改、模型运行状态有没有关系？

答案可能不在一个知识库 Chunk 里。

Agent 可能这样工作：

```text
先搜性能测试
→ 发现时间点
→ 再看 Git 最近改动
→ 再查部署配置
→ 再调 Metrics API
→ 发现还缺一个版本信息
→ 再读 Release Notes
→ 综合证据
```

它的关键不是“用了更高级的搜索算法”。

而是：

> **模型可以根据上一轮证据，决定下一步还要查什么。**

所以最容易记的一句话是：

> **Pipeline RAG 是“一次检索后回答”；Agentic Retrieval 是“边查边判断、逐步取证”。**

现实中 Agent 也可以调用 BM25、Vector、Hybrid、grep、SQL、API。

因此：

> **Agentic Retrieval 与 Vector Search 不是二选一，它是“谁来控制检索过程”的区别。**

【图示占位 KB-11：Full Context / Pipeline RAG / Agentic Retrieval 三路对比】

---

## 12.4 到这里停一下：把几个容易混的词放到一张表里

| 名词 | 它是什么 | 它不是什么 |
|---|---|---|
| **Embedding** | 用数值表示文本语义，方便比较相似度 | 不是知识本身 |
| **Vector Index / DB** | 用来快速找相似向量的索引/存储能力 | 不等于完整知识库 |
| **BM25** | 关键词/词项相关性检索方法 | 不是“低级版 RAG” |
| **Chunk** | 文档为了检索而拆出的知识单元 | 不是越小越好 |
| **Rerank** | 对候选结果重新排序 | 不是另一套知识源 |
| **RAG** | 检索 → 把资料加入 Context → 生成 | 不等于 Vector Search |
| **Agentic Retrieval** | 由 Agent 动态决定搜什么、是否继续搜 | 不等于一种新 Embedding 算法 |
| **Context Window** | 模型允许接收的最大上下文容量 | 不保证整个窗口都能同等有效利用 |

如果这一张表能看懂，后面的 Cherry / Open WebUI / Agent 就只是：

> **这些机制被不同产品以不同方式组合起来。**

---

# 13. Cherry Studio、Open WebUI、Agent 应该怎么理解？

这里不要把它们讲成三个互相竞争的“知识库产品”。

更容易理解的方式是：

> **同一套知识，不同使用层次。**

---

## 13.1 Cherry Studio：个人知识工作台

【录屏占位 KB-R01｜P0｜60–90 秒】Cherry Studio 从零建立同源知识库：新建 KB → 添加资料 → 检查 Parsed Text/Chunk → Embedding=None/BM25 → Retrieval Test → 在 Chat 中使用 KB。录屏重点是流程，不要长时间停留在等待索引。

【录屏占位 KB-R02｜P0｜60–90 秒】同一资料、同一问题，对比 BM25 与 Embedding；如当前版本支持清晰的 Rerank 对比，再追加 Rerank。必须保留 Retrieval 命中的实际片段，不能只录最终回答。


适合演示：

```text
添加文件
→ 看 Parsed Text
→ 看 Chunk
→ Embedding=None
→ BM25
→ Retrieval Test
→ 加 Embedding
→ 按需 Rerank
```

它特别适合培训里帮助大家“看到知识库是怎么建出来的”。

定位：

> **个人 Knowledge Workspace。**

适合：

- 临时研究资料；
- 项目资料包；
- 个人助手；
- Retrieval 调试。

不建议把部门唯一知识源只放在个人客户端里。

【截图占位 KB-12：Cherry Knowledge Base 首页】

【截图占位 KB-13：Cherry Parsed Text / Chunk】

【截图占位 KB-14：Cherry Retrieval Test】

---

## 13.2 Open WebUI：部门共享知识入口

【录屏占位 KB-R03｜P0｜60–90 秒】Open WebUI：管理员/有权限用户创建或打开 Shared Knowledge → 绑定 Model/入口 → 不同用户或 Group 验证可见性。敏感账号信息脱敏。

【录屏占位 KB-R04｜P1｜60–90 秒】同一个 Shared KB，依次展示 Focused/Pipeline Retrieval 与 Native Knowledge Tool/Agentic Retrieval（以当前部署实际支持为准）。重点录模型是否主动决定再次检索，而不是只看最终答案。


Open WebUI 更适合讲：

- 多用户；
- Shared Knowledge；
- Group / ACL；
- Hybrid Search；
- Rerank；
- Full Context；
- Agentic Knowledge；
- 增量同步。

可以把它理解成：

> **部门 Shared Knowledge Service / AI Portal。**

部门统一维护：

- Parser；
- Embedding；
- Rerank；
- 安全策略；

知识库管理员维护：

- 资料；
- Metadata；
- 权限；
- 更新。

普通用户：

- 查询自己有权看到的 Knowledge。

【截图占位 KB-15：Open WebUI Shared Knowledge】

【截图占位 KB-16：Open WebUI Group / Knowledge ACL】

【截图占位 KB-17：Open WebUI Focused RAG / Agentic Knowledge 对比】

---

## 13.3 Agent：知识的编排和执行层

【录屏占位 KB-R05｜P0｜90–150 秒】Agent 多源取证：先查共享 KB → 判断证据不足 → grep/read Git 原始报告 → 如需要再调用 API/Metrics → 带来源回答。建议预先设计一个确实需要跨源核验的问题，避免录成“工具乱调用”。


Agent 不一定先把所有东西建成向量库。

它可以直接面对：

- Workspace；
- Git；
- Markdown；
- 代码；
- API；
- DB；
- Metrics；
- Web；
- MCP；
- Shared RAG。

例如：

```text
为什么最近模型 Agent 连续调用体验变差？

Agent
→ 搜 model-metric 测试结果
→ 看 Qwen API 报告
→ 查 metrics
→ 查部署文档
→ 必要时再查 Shared KB
→ 综合回答
```

所以 Agent 更像：

> **Knowledge Orchestrator。**

它可以调用知识库，也可以绕过传统知识库直接查询真实系统。

【截图占位 KB-18：Agent Search → Read → API → 综合的工具调用轨迹】

---

# 14. 为什么三个 Demo 应该使用同一批资料？

培训建议继续使用我们已经准备的：

- Qwen API 说明；
- Thinking 实测；
- model-metric 长上下文 / 性能资料。

因为这样学员看到的是：

> **知识没变，访问知识的方法在变。**

教学递进：

```text
Cherry Studio
→ 看知识怎样 Parse / Chunk / Retrieve

Open WebUI
→ 看同类知识怎样共享、授权、集中治理

Agent
→ 看知识怎样和 Git / API / Metrics 一起被主动调用
```

这比三个工具分别准备三套完全不同资料更容易理解底层机制。

【截图占位 KB-19：同一套 Qwen 资料在 Cherry / Open WebUI / Agent 中的三联图】

---

## 14.1 先不要选工具，先判断“我现在到底在找什么”

给学员一张最实用的判断表：

| 我的问题 | 优先考虑 |
|---|---|
| “这个错误码在哪里出现？” | BM25 / Full-text / grep |
| “这句话换一种说法后还能找到吗？” | Embedding / Vector |
| “既有术语又有自然语言” | Hybrid |
| “30 万行数据平均值是多少？” | SQL / Python |
| “服务器现在状态怎样？” | API / Metrics Tool |
| “整个项目哪个文件实现了这个功能？” | Git / rg / LSP，必要时语义代码搜索 |
| “这几份文档综合起来说明什么？” | Hybrid + Rerank，复杂时 Agentic Retrieval |
| “代码、日志、文档、实时数据之间有什么关系？” | Agentic Retrieval |
| “资料只有两页，而且每次都必须完整遵守” | Full Context |

这张表的目的不是给出永远正确的答案，而是训练一个习惯：

> **先判断问题和知识形态，再选检索方式。**

---

# 15. 部门知识库应该怎样建设？

到这里，学员应该已经能理解：

> 部门知识库建设不能从“选哪个向量数据库”开始。

更合理的顺序是：

## 第一步：先盘点 Source of Truth

先回答：

- 哪些知识已经存在？
- 原件在哪里？
- 谁负责？
- 哪一版有效？
- 权限是什么？

例如：

```text
Git
DMS
文件服务器
Wiki
数据库
API
业务系统
```

---

## 第二步：按知识类型决定处理方式

例如：

```text
自然语言文档
→ Parse / Chunk / Hybrid RAG

代码
→ Git / rg / LSP

结构化数据
→ SQL / Python

实时状态
→ API / Metrics

图片
→ 原图 + OCR/VLM + 文字说明
```

---

## 第三步：设计 Metadata、版本和权限

至少解决：

- 谁负责；
- 哪个项目；
- 哪一版；
- 是否有效；
- 谁能看。

否则 Retriever 可能非常准确地找到一份：

> **过期但是相似度最高的错误资料。**

---

## 第四步：建立 Retrieval

先理解问题类型：

```text
精确词？
语义改写？
跨文档？
实时数据？
代码？
```

再决定：

```text
BM25
Vector
Hybrid
SQL
API
Agentic Retrieval
```

---

## 第五步：控制最终 Context

不要止步于：

```text
搜到 Top-K
→ 全塞
```

还要做：

```text
Rerank
ACL
Version
Deduplicate
Evidence Budget
Context Packing
```

---

## 第六步：最后才讨论具体参数和 Benchmark

例如：

- Chunk 多大；
- Top-K 多少；
- Embedding 用哪个；
- 是否需要 Rerank；
- BM25 / Dense / Hybrid 谁更合适。

这些问题没有一个脱离语料和真实问题集的“万能答案”。

本教学版先建立方法。

后续再通过部门真实资料做 Benchmark。

---

# 16. 部门知识架构最终应该长什么样？

建议目标：

```text
┌──────────────────────────────────────┐
│        Source of Truth               │
│ Git / Wiki / DMS / DB / API         │
└────────────────┬─────────────────────┘
                 ↓
┌──────────────────────────────────────┐
│ Parse / OCR / Metadata / ACL         │
└────────────────┬─────────────────────┘
                 ↓
┌──────────────────────────────────────┐
│ Retrieval Index                     │
│ BM25 / Full-text / Vector           │
└────────────────┬─────────────────────┘
                 ↓
┌──────────────────────────────────────┐
│ Retrieval & Context Control          │
│ Rerank / Version / Deduplicate       │
│ Evidence Budget / Context Packing    │
└────────────────┬─────────────────────┘
                 ↓
┌──────────────────────────────────────┐
│ Knowledge Tools                     │
│ Search / Read / SQL / API / MCP     │
└────────────────┬─────────────────────┘
                 ↓
      ┌──────────┼───────────┐
      ↓          ↓           ↓
 Open WebUI    Cherry      Agent
 部门共享入口  个人工作台   工程任务
```

最终最值得长期维护的是：

> **Source + Metadata + ACL + Retrieval 能力 + 可追溯引用。**

而不是：

> 某个软件里已经生成的一批 Embedding。

【图示占位 KB-20：部门知识库最终架构正式版】

---

# 17. 权限为什么必须放在 Retrieval 前？

一个错误做法：

```text
先搜整个知识库
→ 敏感 Chunk 已进入 Prompt
→ 再告诉模型“不要泄露”
```

这不是真正的权限控制。

更合理：

```text
User Identity
→ ACL / Classification
→ Retrieval
→ 只有授权内容进入 Context
→ LLM
```

Microsoft Azure AI Search 等企业搜索系统已经把 Document-Level ACL / Security Trimming 做成明确的查询时能力。

所以：

> **知识安全是 Retrieval 架构问题，不只是 System Prompt 问题。**

【图示占位 KB-21：错误 ACL 流程 vs 正确 ACL 流程】

---

# 18. 知识库不能保证“不幻觉”

【录屏占位 KB-R06｜P1｜60–90 秒】无答案/证据不足场景：知识库中故意不放答案，观察系统是否明确说“证据不足”以及引用了什么。后续可与版本冲突测试合并为知识库回归测试录屏。


即使 Retriever 找到了正确资料，模型仍然可能：

- 漏用证据；
- 错误综合；
- 生成证据中没有的内容；
- 引用与结论不匹配。

RAGTruth、ALCE、RAGChecker 等研究都说明：

> **有 RAG 不代表生成结果天然可靠。**

因此最终回答应该尽量支持：

- 文件名；
- 路径；
- 页码；
- Section；
- URL；
- Commit；
- Version。

目标不是：

> “AI 说知识库里是这样。”

而是：

> **工程师能够回到原始 Source 验证。**

【截图占位 KB-22：一个带 Source / Section / Version 引用的回答】

---

# 19. 这一章暂时不展开什么？

为了避免教学主线过载，本版暂不深入：

- Hit@K / Recall@K / MRR / nDCG 数学细节；
- RAGAS / RAGChecker 的完整指标体系；
- Embedding 模型排行榜；
- Reranker 模型横评；
- Vector DB 产品对比；
- GraphRAG 内部算法；
- 大规模 Benchmark 设计；
- 内网 qwen3.6 的最终检索参数。

这些内容不是不重要。

而是：

> **应该在学员先理解“知识为什么这样组织、为什么这样检索”以后再讲。**

完整材料继续保留在：

`docs/chapters/03-department-knowledge-base.md`

和：

`docs/references/knowledge-base-rag-evidence-2026-09.md`

---

## 19.1 讲师控制节奏：哪些要讲透，哪些只点到为止

现场建议把内容分三层。

**必须讲透：**

- 知识库不等于 Vector DB；
- RAG 是“先查、再给、再答”；
- BM25 vs Embedding 的直觉差异；
- Parse / Chunk 为什么决定上限；
- 检索命中以后还有 Context Utilization；
- Top-K 不是越大越好；
- Cherry / Open WebUI / Agent 的角色差异。

**讲到能理解即可：**

- Rerank；
- Metadata；
- Evidence Budget；
- Full Context / Pipeline / Agentic 三种路由。

**先告诉学员“存在”，暂不展开：**

- MRR / nDCG；
- RAGAS / RAGChecker；
- GraphRAG；
- Embedding / Reranker 模型横评；
- Vector DB 产品差异；
- 复杂 ACL 实现细节。

这样可以避免这一章重新变成：

> **把所有 RAG 名词一次灌给学员。**

---

# 20. 本章最后让学员带走八个认知

第一：

> **知识库不是 Vector DB，而是一套让模型可靠访问外部知识的系统。**

第二：

> **不同知识类型应该使用不同的访问方式，不能全部转成 PDF 再向量化。**

第三：

> **RAG = Retrieval → Context → Generation；Retrieval 可以是 BM25、Vector、Hybrid、grep、SQL 或 API。**

第四：

> **BM25 解决精确词，Embedding 补语义表达差异，Rerank 帮助从候选中压缩高质量 Evidence。**

第五：

> **Retriever 找到了只是第一关；Context Window 是输入容量上限，不是有效知识容量保证。**

第六：

> **知识库追求的是“足够而高质量的证据”，不是尽可能多地往 Prompt 里塞内容。**

第七：

> **真正值得部门长期建设的是 Source、Metadata、Version、ACL 和可复用的知识访问能力，而不是绑定某个客户端。**

第八：

> **先判断问题需要什么知识，再选择 Retrieval；不要先选 Vector DB，再把所有资料硬塞进同一种方案。**

---

# 21. 后续截图与验证清单

| 编号 | 待补素材 | 建议来源 | 目的 |
|---|---|---|---|
| KB-01 | 无内部资料 vs 带资料回答 | 内网 qwen3.6 / Chat | 引出“外部知识” |
| KB-02 | 部门知识五层架构 | 后续绘图 | 建立全局框架 |
| KB-03 | 不同知识不同处理方式 | 后续绘图 | 防止“全部向量化” |
| KB-04A | RAG“先查、再给、再答”三步图 | 后续绘图 | 降阶解释 RAG |
| KB-04B | Source → Embedding → Vector Index | 后续绘图 | 强调 Embedding/Index 不是知识本体 |
| KB-04 | Embedding=None / BM25 | Cherry Studio | 证明 RAG ≠ Vector |
| KB-05 | BM25 vs Embedding Retrieval | Cherry Studio | 展示精确词 vs 语义 |
| KB-06A | 原 PDF 与 Parsed Text 对照 | Cherry / Open WebUI | 强调先验证解析质量 |
| KB-06 | Parsed Text / Chunk | Cherry / Open WebUI | 解释 Parse / Chunk |
| KB-07 | v1/v2 Metadata | 自制示例 | 解释版本治理 |
| KB-08 | 两层召回 | 后续绘图 | External vs In-context |
| KB-08B | 标称 Context Window vs 有效 Evidence | 后续绘图 | 解释“放得下 ≠ 用得好” |
| KB-09 | Candidate → Evidence Budget | 后续绘图 | 解释 Context Control |
| KB-10 | Top-K / Rerank 配置 | Open WebUI / Cherry | 参数与 Context 的关系 |
| KB-11 | Full Context / Pipeline / Agentic | 后续绘图 | 三种知识访问模式 |
| KB-12~14 | Cherry 知识库操作 | Cherry Studio | 个人知识工作台 Demo |
| KB-15~17 | Shared KB / ACL / Agentic | Open WebUI | 部门知识治理 Demo |
| KB-18 | Agent 工具调用轨迹 | Agent | 多源逐步取证 |
| KB-19 | 同源三工具对比 | 三个工具 | 展示“知识不变，入口变化” |
| KB-20 | 部门最终架构 | 后续正式绘图 | 收束设计 |
| KB-21 | ACL 正误对比 | 后续绘图 | 安全边界 |
| KB-22 | 带引用回答 | 后续实测 | 可追溯性 |

---

## 21.1 录屏准备清单

| 编号 | 优先级 | 录什么 | 必须看到的关键动作 | 状态 |
|---|---:|---|---|---|
| KB-R01 | P0 | Cherry 从建库到问答 | Source → Parse/Chunk → BM25 → Retrieval Test → Chat | ⬜ |
| KB-R02 | P0 | BM25 vs Embedding / Rerank | 同一资料、同一问题、命中片段发生变化 | ⬜ |
| KB-R03 | P0 | Open WebUI Shared Knowledge + ACL | Shared KB、用户/Group 权限、实际可见性 | ⬜ |
| KB-R04 | P1 | Pipeline vs Agentic Retrieval | 固定检索一次 vs 模型主动继续检索 | ⬜ |
| KB-R05 | P0 | Agent 跨源逐步取证 | Shared KB → Git 原文 → API/Metrics → 引用回答 | ⬜ |
| KB-R06 | P1 | 无答案 / 版本冲突回归 | 证据不足时不编、冲突时说明版本 | ⬜ |

> 建议实际备课时优先完成 `KB-R01`、`KB-R02`、`KB-R03`、`KB-R05`。它们基本能覆盖“个人知识库 → 部门共享知识 → Agent 编排”的完整教学链。

---

# 22. 事实与证据说明

本讲义中的关键技术判断均应能够回溯到：

`docs/references/knowledge-base-rag-evidence-2026-09.md`

其中已经区分：

- 同行评审论文 / Benchmark；
- Research / Preprint；
- 官方产品文档；
- 产业技术报告；
- 本项目工程建议；
- 待部门内网实测。

特别注意：

> **本教学稿给出的 Hybrid、Rerank、Evidence Budget、Cherry / Open WebUI / Agent 分工，是基于公开研究与成熟实现形成的工程设计基线，不代表这些参数组合已经在部门语料上完成最优性验证。**

后续实际测试如果与当前建议冲突：

> **以实测为准，并回改讲义。**


---

# 23. 教学版 v0.2 本轮重构说明

本轮不新增技术路线，主要降低首次学习门槛：

- 增加“开卷考试”统一类比，用于贯穿 Source / Retrieval / Context；
- 将 Embedding 明确解释为“语义索引能力”，避免误解成知识本体；
- 将 RAG 简化为“先查、再给、再答”；
- 将 Parse 与 Chunk 拆开解释，强调“先读对，再切对”；
- 将长上下文论文从主叙事下沉到证据栏，主线只保留三个可理解现象；
- 将 Top-K、Rerank、Evidence Budget 统一解释为“控制最终桌面资料”；
- 将 Agentic Retrieval 解释为“调查员逐步取证”，突出它是检索控制方式而非新搜索算法；
- 新增问题类型 → 优先检索方式速查表；
- 新增讲师节奏分层，避免现场过度展开高级概念。

后续截图验证仍按 KB-01～KB-22 编号补充；实测数据不在本轮虚构。
