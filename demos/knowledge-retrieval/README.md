# Knowledge Retrieval Demo：同一知识源，三种使用方式

> 培训目标：用同一批真实资料，连续演示 Cherry Studio、Open WebUI 与 Agent 对知识的不同处理方式。
> 核心观点：知识源可以相同，索引和 Retrieval 可以不同；Agent 还可以把 RAG 知识库当作一个 Tool 继续向上编排。

## 1. 统一资料集

全部来自当前仓库真实材料：

- docs/chapters/01-intranet-qwen-api.md
- api/qwen/README.md
- api/qwen/reports/qwen36_api_test_report_20260929.md
- api/qwen/results/20260929_v2/evidence.md
- api/qwen/results/20260929_105316/evidence.md

不要为三个工具准备三套事实资料。

这样可以固定：

> Source of Truth 不变，只改变 Retrieval 与 Orchestration。

## 2. 统一问题集

建议固定三类问题。

### Q1：精确事实

> qwen3.6 当前服务配置的 max_model_len 是多少？

用途：

- BM25 / grep 很容易命中；
- 说明精确术语不一定需要 Vector Search。

### Q2：语义改写

> 为什么一个复杂推理任务跑完以后，后面的简单请求有时也会突然变得很慢？

资料中的原始表述包括：

- Thinking 存在明显长尾；
- 重任务可能短时间拖慢后续推理；
- Thinking ON 约 298.6 s 后，简单 PING Chat 一度约 70.18 s。

用途：

- 对比 BM25 与 Embedding；
- 观察 Query 与原文措辞不同后的召回效果。

### Q3：综合判断

> 当前内网 qwen3.6 是否已经适合用于部门 Agent 连续任务？请区分：已验证能力、已观察风险、尚未验证项，并给出证据来源。

用途：

- 需要跨多份资料；
- 适合 Agentic Retrieval；
- 可以验证是否会把“未测试”说成“不支持”。

---

## 3. Demo A：Cherry Studio —— 知识怎么建

定位：

> Personal Knowledge Workspace。

### 演示步骤

1. 建立知识库“内网 Qwen 使用与测试”；
2. 导入统一资料集；
3. 检查 Parsed Text；
4. 检查 Chunk；
5. Embedding Model 先选 None；
6. 用 Q1 做 BM25 Retrieval Test；
7. 用 Q2 测 BM25；
8. 配置 Embedding 后重新索引；
9. 再用 Q2 比较语义召回；
10. 如果正确资料已召回但排序不理想，再配置 Rerank；
11. 保存 Q1/Q2/Q3 作为回归问题；
12. 将 KB 绑定到 Cherry Agent，再用 Q3 做综合问答。

### 要讲清的概念

- BM25 = 字面匹配；
- Embedding = 语义召回；
- Rerank = 候选精排；
- RAG 不等于 Vector DB；
- Cherry Agent 可以在自己的工作流中绑定并使用该 KB。

---

## 4. Demo B：Open WebUI —— 知识怎么共享与治理

定位：

> Shared Knowledge Service / Department AI Portal。

这里不再完整重复 Cherry 的建库教学。

### 预先配置

由平台管理员统一设置：

- Document Extraction；
- Embedding；
- Rerank；
- Hybrid Search；
- Knowledge Access 权限。

创建：

- Shared KB：内网 AI 模型使用知识库；
- Group：AI-Engineering；
- Workspace Model：部门 AI 技术助手。

把统一资料集导入或同步到 Shared KB，并把 Read 权限授予 AI-Engineering。

### System Prompt 示例

~~~text
你是部门 AI 技术助手。

回答内部模型能力、接口和性能问题时：
1. 优先使用已绑定知识库；
2. 关键结论注明来源；
3. 资料没有证据时明确说明；
4. 不把“未测试”说成“不支持”。
~~~

### 演示 1：共享使用

有权限用户通过共享 Model 提问 Q1/Q3。

目标：

> 用户不需要各自重建 KB，也能使用统一部门知识。

### 演示 2：ACL

使用没有 KB Read 权限的账号提问同样问题。

目标：

> Model 共享不等于 Knowledge 自动共享；权限必须发生在 Retrieval 前。

### 演示 3：Pipeline 与 Agentic Knowledge

若当前部署启用 Native Knowledge Tools：

- 先展示 Focused / Hybrid Retrieval；
- 再让模型主动 query / grep / view_file。

目标：

> 同一个 Shared KB 既可以作为 Pipeline RAG，也可以作为 Agentic Retrieval Tool。

### Open WebUI KB 还可以成为 Agent 的上游知识服务

Open WebUI 当前提供 Knowledge API，也支持 server-side tool calling。

因此架构上可以：

~~~text
External Agent
    ↓
Open WebUI Knowledge API / Tool Service
    ↓
Shared KB
    ↓
带 ACL 的 Retrieval Result
~~~

这说明 Open WebUI 不只是最终聊天界面，也可以成为后续 Agent 的共享知识服务层。

---

## 5. Demo C：Agent —— 同时承接原始知识和 RAG 知识

定位：

> Knowledge Orchestrator + Task Executor。

这里不要把 Agent 演示成第三套独立知识库。

应该展示：

> Agent 可以同时调用多个知识源和 Retriever。

### 推荐任务

给 Agent：

> 基于当前仓库和部门共享知识库，分析 qwen3.6 是否已经适合部门 Agent 连续任务。先从共享知识库检索总体能力，再到 Git Repo 中查原始测试报告和证据；如果存在相关实时指标接口，再说明还可以进一步查询哪些实时数据。所有结论必须标明来源，不允许根据模型名称推测。

### 预期流程

~~~text
Goal
 ↓
Shared KB Search
 ↓
得到能力矩阵候选结论
 ↓
Agent 判断仍需原始证据
 ↓
grep / read Git Repo
 ↓
找到 Thinking / Tool Loop / Vision / 未验证项
 ↓
必要时查询 API / Metrics
 ↓
交叉核验
 ↓
Final Answer
~~~

这里 Agent 同时承接：

1. Open WebUI 一类的共享 RAG 知识；
2. Coding Agent 擅长的 Git / 文件原始知识；
3. 后续还可增加 API / SQL / Metrics 等实时知识。

### Cherry 的知识如何进入 Agent

分两种情况：

- 在 Cherry Agent 内：直接绑定 Cherry Knowledge Base；
- 在外部 Codex/OpenCode/Hermes 等 Agent 内：不要默认直接读取 Cherry 本地索引，优先访问同一个原始 Source，或调用有正式 API/MCP 的共享知识服务。

因此：

> Cherry KB 更像个人局部索引；Open WebUI Shared KB 更适合成为跨 Agent 复用的共享 Retrieval Service。

---

## 6. 为什么同一套资料是更好的演示

因为它控制了一个重要变量：

~~~text
Source of Truth = Same
~~~

然后只改变：

~~~text
Cherry:
BM25 / Vector / Rerank

Open WebUI:
Shared Hybrid RAG / ACL / Knowledge Tools

Agent:
Search Router + Shared KB + Git + API
~~~

这样差异更容易归因于：

> Retrieval / Governance / Orchestration。

---

## 7. 但不要所有 Demo 都问完全一样的问题

推荐：

- Q1 在三种工具中都问一次，用来建立可比基线；
- Q2 重点在 Cherry 演示 Retrieval Algorithm；
- Q3 重点在 Open WebUI / Agent 演示 Shared Knowledge 与 Agentic Retrieval。

也就是：

~~~text
同一 Corpus
+ 一组固定 Benchmark Questions
+ 每个工具一个最能体现其特点的任务
~~~

比三个工具全部机械重复同一个问题更有教学价值。

---

## 8. 最后一页对比

| 层次 | Cherry Studio | Open WebUI | Agent |
|---|---|---|---|
| 主要角色 | 个人 KB 工作台 | 部门共享 Knowledge Service | Knowledge Orchestrator |
| Source | 文件/Note/Folder/Link | Shared KB / 同步源 | Repo / File / KB / API / DB |
| Retrieval | BM25 / Vector / Rerank | Hybrid / Full Context / Knowledge Tools | 自主选择 grep / KB / API / Search |
| 权限 | 个人为主 | Group / ACL | 继承各 Tool / Source 权限 |
| 是否必须 Vector | 否 | 否 | 否 |
| 能否使用 RAG KB | 是 | 是 | 是，可作为一个 Tool |
| 能否直接搜原始 Repo | 不作为主要方式 | 可通过 Sync/Knowledge Tool | 是，强项 |
| 适合展示 | 建库与检索算法 | 分享、治理、权限 | 多源检索与任务闭环 |

最终结论：

> **Agent 不是替代 RAG，而是可以把 RAG、全文搜索、Git、API、数据库都作为 Retrieval Tools 统一编排。**

> **同一份知识最好保留稳定 Source，再根据不同工具生成不同索引和访问方式。**
