# 教学版讲义：从“把资料给 AI”到“真正可用的部门知识库”

> 模块：Chat → Knowledge → RAG → Agent  
> 版本：Teaching Draft v0.1  
> 日期：2026-09-30  
> 面向对象：部门技术人员、知识库建设人员、AI 应用开发人员  
> 定位：**用于培训讲解的教学版，不替代完整研究稿。**  
> 完整技术稿：`docs/chapters/03-department-knowledge-base.md`  
> 证据基线：`docs/references/knowledge-base-rag-evidence-2026-09.md`  
> 架构稿：`docs/architecture/department-knowledge-architecture.md`

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

# 4. RAG 到底是什么？先不要急着讲向量

RAG 可以先用一个最简单的公式理解：

> **RAG = Retrieval → Context Augmentation → Generation**

也就是：

```text
先找资料
→ 把找到的资料放进上下文
→ 再让模型回答
```

注意：

> **Retrieval 不等于 Vector Search。**

搜索资料可以使用：

- BM25；
- 全文搜索；
- Vector Search；
- Hybrid Search；
- grep；
- SQL；
- API；
- Search Engine。

所以这些都是“外部知识进入模型上下文”的不同方式。

---

# 5. BM25、Embedding、Hybrid 到底有什么区别？

这里不要先讲公式，先看问题。

假设文档写的是：

```text
当前模型 max_model_len 为 131072。
```

用户问：

> max_model_len 是多少？

这是典型的**精确词匹配**。

BM25 / Full-text 很适合。

---

另一个文档写：

```text
长上下文会导致首 Token 延迟明显增加。
```

用户问：

> 为什么我一次塞很多材料以后，模型很久才开始出字？

这里用户和文档几乎没有使用相同的关键词，但意思相近。

Embedding / Dense Retrieval 的价值就体现出来了。

## 5.1 可以先这样理解

BM25 更像问：

> **字面上像不像？**

Embedding 更像问：

> **语义上像不像？**

Rerank 则是在已经找到一批候选以后再问：

> **这些候选里，到底谁最值得交给 LLM？**

## 5.2 为什么常见 Hybrid？

工程技术资料里往往同时存在：

```text
自然语言
+
型号
+
API Path
+
错误码
+
标准编号
+
缩写
```

因此一种常见候选方案是：

```text
        Query
       /     \
    BM25    Vector
       \     /
     Candidates
         ↓
       Rerank
         ↓
 Selected Evidence
```

这就是 Hybrid Retrieval 的基本思路。

公开检索研究给我们的结论不是：

> Vector 一定比 BM25 好。

BEIR 等跨域检索研究反而说明：

> **BM25 仍然是很强、很稳健的基线；Dense / Rerank 的效果与任务和语料有关。**

因此培训统一采用：

> **不要讨论“谁更高级”，讨论“当前问题需要什么检索能力”。**

【截图占位 KB-04：Cherry Studio Embedding=None / BM25 配置界面】

【截图占位 KB-05：同一问题 BM25 与 Embedding Retrieval Test 对比】

---

# 6. 文档为什么还要 Parse 和 Chunk？

假设有一本 300 页技术手册。

用户只问：

> 某接口超时时间是多少？

如果每次都把 300 页完整发给模型：

- Token 多；
- Prefill 慢；
- 成本高；
- 无关内容多；
- 模型还要自己重新在 300 页里找证据。

所以传统 RAG 会先把文档拆成更适合检索的单位。

这就是 Chunk。

## 6.1 Chunk 不是“每 500 字切一刀”

机械固定长度虽然简单，但可能把逻辑关系切坏。

例如：

```text
3.2 API 调用限制
前置条件……
参数……
超时时间……
异常处理……
```

如果正好从“超时时间”前面切断：

Retriever 虽然找到一句话，但模型可能不知道：

- 它属于哪个接口；
- 前置条件是什么；
- 哪个版本适用。

因此工程上更优先考虑：

```text
Document
→ Chapter
→ Section
→ Paragraph / Logical Block
```

并保留：

- Heading Path；
- Document ID；
- Version；
- Parent Section；
- 前后 Chunk 关系。

## 6.2 Chunk 太小和太大都会有问题

Chunk 太小：

- 上下文断裂；
- 表头和数据分开；
- 条件与结论分开。

Chunk 太大：

- 检索不精确；
- 无关内容更多；
- Token 增加；
- 后面 LLM 的 Context 负担增加。

所以：

> **Chunk 的目标不是“切得越细越好”，而是保持一个可以独立理解的知识单元。**

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

# 8. 第二个关键问题：Retriever 找到了，为什么还不算结束？

这是本章最重要的认知之一。

传统 RAG 图经常画成：

```text
Question
→ Retrieval
→ Top-K
→ LLM
→ Answer
```

看起来只要 Retrieval 找到正确 Chunk，后面就没问题了。

其实至少有两道关。

## 8.1 第一关：External Retrieval Recall

问题是：

> Retriever 有没有把真正需要的资料找出来？

例如答案明明在 `qwen-api.md`，结果 Top-5 一个都没命中。

这是典型的检索失败。

## 8.2 第二关：In-context Retrieval / Context Utilization

假设正确资料已经进入 Prompt。

模型仍然要：

- 在这些 Context 中找到证据；
- 理解证据；
- 关联多个证据；
- 排除干扰内容；
- 判断新旧版本；
- 最终用于回答。

这一层同样可能失败。

所以：

> **外部 Retriever 找到了 ≠ LLM 一定能用好。**

---

# 9. Context Window 很长，为什么还不能把资料全塞进去？

模型可能标称：

```text
128K
256K
1M
```

这首先表示：

> **接口能够接受这么长的输入。**

但不能直接等同于：

> **模型能在整个窗口内，对所有位置、所有复杂任务都保持同样可靠的利用能力。**

这个问题已经有多项公开研究。

## 9.1 Lost in the Middle

TACL 2024 的 *Lost in the Middle* 观察到：

- 相关信息在 Context 中的位置会影响模型使用效果；
- 在论文测试的模型中，信息位于中间时可能比开头/末尾更难利用；
- 在开放域 QA case study 中，继续增加检索文档虽然提高了 Retriever Recall，但最终 Reader 收益很快趋于饱和。

它说明：

> **检索更多资料，不等于模型可以同比例利用更多资料。**

## 9.2 RULER

RULER 把简单 Needle-in-a-Haystack 扩展到：

- 多 needle；
- multi-hop；
- aggregation；
- 更复杂的长上下文任务。

论文指出：

> **标称 Context Size 不应直接当成 Effective Context Size。**

## 9.3 NoLiMa

NoLiMa 进一步去掉明显的字面匹配。

也就是问题和正确证据不是复制同一组关键词，而需要语义关联。

这其实比“在 10 万字里找一个完全相同的密码串”更接近真实知识库问答。

## 9.4 更直接的证据：Perfect Retrieval 之后仍会掉性能

Findings of EMNLP 2025 的：

> *Context Length Alone Hurts LLM Performance Despite Perfect Retrieval*

专门控制：

> 正确证据已经提供给模型，不存在 Retriever 漏召回。

但随着输入 Context 变长，论文测试的多个模型和任务仍出现明显性能下降。

因此知识库设计必须同时优化：

```text
Retriever 能不能找到
+
最终 Context 是否干净、足够、可利用
```

完整论文和证据等级见：

`docs/references/knowledge-base-rag-evidence-2026-09.md`

【图示占位 KB-08：External Retrieval Recall 与 In-context Context Utilization 两道关】

---

# 10. 所以，Top-K 为什么不是越大越好？

假设 Hybrid Search 一次搜到 30 个候选 Chunk。

最简单的做法：

```text
30 个全部塞给模型
```

但这些 30 个里面可能有：

- 真正关键证据；
- 内容重复；
- 只沾一点边的段落；
- 旧版本；
- 相互冲突的内容；
- 其他项目的同名资料。

于是会出现：

> **Context Pollution。**

同时还会增加：

- 输入 Token；
- Prefill 时间；
- TTFT；
- 成本；
- LLM 定位和综合信息的负担。

所以 Top-K 本质上是：

> **Recall 和 Context Pollution 之间的权衡。**

更合理的流程是：

```text
Hybrid Search
→ 先召回较多 Candidate
→ Rerank
→ ACL / Version Filter
→ Deduplicate
→ 合并必要相邻 Chunk
→ 选择有限 Evidence
→ LLM
```

这就引出一个很重要的工程概念：

> **Context Budget / Evidence Budget**

不是：

> 检索到多少就给多少。

而是：

> **在覆盖回答需要的证据前提下，尽量只给最相关、最可靠、最有信息量的内容。**

【图示占位 KB-09：30 Candidates → Rerank → 5 Evidence Chunks → LLM】

---

# 11. Rerank 为什么值得单独理解？

Rerank 不是第二个“更高级的向量数据库”。

它工作在：

```text
Candidate Retrieval
之后
        ↓
真正送进 LLM
之前
```

例如：

```text
BM25 + Vector
→ 召回 30 个 Candidate
→ Reranker 重新判断相关性
→ 留下 5 个
→ LLM
```

所以 Rerank 有两个作用：

1. 提高候选排序质量；
2. **帮助压缩最终 Evidence Set。**

第二点和长 Context 问题直接相关。

成熟 RAG 系统普遍会暴露：

- Top-K；
- Relevance Threshold；
- Rerank；
- Context Limit；

这说明知识库不是简单追求：

> “召回越多越好”。

【截图占位 KB-10：Rerank 配置与 Top-K 参数界面】

---

# 12. Full Context、Pipeline RAG、Agentic Retrieval 怎么选？

到这里就可以把三种方式放在一起看。

## 12.1 Full Context

例如：

- 一页编码规范；
- 很短的系统规则；
- 小型术语表。

可以直接：

```text
完整资料
+
问题
→ LLM
```

优点：

- 简单；
- 不会发生 Retriever 漏召回。

缺点：

- 每次都消耗全部 Context；
- 资料大以后延迟和成本增加；
- “放得下”不代表“一定能利用好”。

所以更准确的判断不是：

> 能不能塞进 Context？

而是：

> **资料是否短、是否每次都必须完整看到、证据密度是否高。**

---

## 12.2 Pipeline RAG

典型流程：

```text
Question
→ 固定 Retrieval
→ Rerank
→ Top-K Evidence
→ LLM
```

适合：

- 制度问答；
- FAQ；
- 产品手册；
- 高并发；
- 问题边界稳定；
- 通常一两次检索即可找到证据。

特点：

- 快；
- 稳定；
- 易测试；
- 行为相对可预测。

---

## 12.3 Agentic Retrieval

复杂问题可能是：

> 最近 API 为什么变慢？和部署配置、代码修改、模型运行状态有没有关系？

这时资料可能分布在：

- 部署文档；
- Git；
- metrics；
- 测试报告；
- API；
- Issue。

Agent 可以：

```text
Search
→ Read
→ 判断还缺什么
→ Search Again
→ Read Another Source
→ Query API
→ Compare
→ Answer
```

它不是一次性把大量资料全部塞进 Context。

更像：

> **逐步取证。**

因此 Agentic Retrieval 的一个重要价值是：

> **动态决定“下一步需要什么 Context”。**

代价：

- Tool Call 多；
- Token 多；
- 更慢；
- 更依赖模型工具调用能力；
- 更难复现。

所以：

> **Agentic Retrieval 不会淘汰 Pipeline RAG。**

【图示占位 KB-11：Full Context / Pipeline RAG / Agentic Retrieval 三路对比】

---

# 13. Cherry Studio、Open WebUI、Agent 应该怎么理解？

这里不要把它们讲成三个互相竞争的“知识库产品”。

更容易理解的方式是：

> **同一套知识，不同使用层次。**

---

## 13.1 Cherry Studio：个人知识工作台

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

# 20. 本章最后让学员带走七个认知

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

---

# 21. 后续截图与验证清单

| 编号 | 待补素材 | 建议来源 | 目的 |
|---|---|---|---|
| KB-01 | 无内部资料 vs 带资料回答 | 内网 qwen3.6 / Chat | 引出“外部知识” |
| KB-02 | 部门知识五层架构 | 后续绘图 | 建立全局框架 |
| KB-03 | 不同知识不同处理方式 | 后续绘图 | 防止“全部向量化” |
| KB-04 | Embedding=None / BM25 | Cherry Studio | 证明 RAG ≠ Vector |
| KB-05 | BM25 vs Embedding Retrieval | Cherry Studio | 展示精确词 vs 语义 |
| KB-06 | Parsed Text / Chunk | Cherry / Open WebUI | 解释 Parse / Chunk |
| KB-07 | v1/v2 Metadata | 自制示例 | 解释版本治理 |
| KB-08 | 两层召回 | 后续绘图 | External vs In-context |
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
