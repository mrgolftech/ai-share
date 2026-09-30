# AI 大模型与 Agent 工程实践培训——4 次讲座组织方案（13 / 2 / 45 / 678）

> 状态：Review Draft v0.1  
> 日期：2026-09-30  
> 组织原则：保留 1～8 作为内容单元，现场授课按 **13 / 2 / 45 / 678** 合并为 4 次。  
> 目标：从底层认知 → 知识库 → Agent 共性机制 → 完整工程实操，形成连续课程。

---

# 0. 为什么保留“8 个内容单元 + 4 次现场讲座”

建议不要把现有 1～8 内容重新改成 4 个大文件。

更合理的是：

```text
内容组织：1 2 3 4 5 6 7 8
现场授课：13 / 2 / 45 / 678
```

原因：

- 1～8 适合维护知识边界、案例、证据、截图和后续迭代；
- 4 次讲座适合真实授课节奏；
- 同一个内容单元未来可以被不同培训组合复用；
- 不会因为讲座合并而把知识库、Agent、案例文档重新混在一起。

---

# 第一次讲座：从 API 到 Agent——撕破 Chat 与 Agent 的神秘面纱

> 内容映射：**1 + 3**

## 1.1 这场真正要解决什么

这一场不是教大家“怎么写 API”，也不是介绍一堆 AI 产品。

核心目标是：

> **让大家真正看懂 Chat、Agent、模型、API、工具之间到底是什么关系。**

最终形成一张底层图：

```text
用户
↓
Chat / Agent UI
↓
Harness / Application
↓
Model API
↓
LLM
        ↕
Tools / External World
```

让学员明白：

- 模型不是 ChatGPT 页面；
- Chat 不是模型；
- Agent 也不是另一种“神秘模型”；
- Agent 的很多能力来自 Harness、Tools、Runtime；
- 不同 AI 工具底层最终都要解决“怎样调用模型、怎样管理 Context、怎样把工具结果交还模型”这些问题。

---

## 1.2 第一部分：从一个真实 Chat 请求开始

现场直接打开 Cherry Studio DevTools / Network。

展示：

### 模型列表

`GET /v1/models`

回答：

> 应用怎么知道有哪些模型？

### 第一轮 Chat

`POST /v1/chat/completions`

看：

- URL；
- Header；
- API Key；
- JSON；
- model；
- messages；
- stream。

### 多轮 Chat

让学员直接看到：

> 第二轮为什么能“记住”第一轮？

重点解释：

- 历史消息；
- Context；
- Application / Harness 怎样组织请求；
- 模型不是无限长期记忆。

### 多模态

看图片怎样进入 Request。

### SSE

看 `stream=true` 后 Token 怎样持续返回。

---

## 1.3 第二部分：模型能力到底来自哪里

从 API 请求进入模型能力：

- Token；
- Context Window；
- Thinking / Reasoning；
- Tool Calling；
- Vision；
- MoE；
- Quantization；
- Prefill / Decode；
- TTFT；
- TPS；
- KV Cache；
- 并发。

使用内网 Qwen 当前实测。

强调：

> **模型能力不是一个“总分”，而是多项工程能力的组合。**

例如：

- 会不会 Vision；
- Tool Calling 稳不稳；
- 长上下文是否有效；
- 推理能力；
- 速度；
- 并发；
- 成本。

---

## 1.4 第三部分：不同工具其实在做什么

用真实工具做横向说明：

- Cherry Studio；
- Open WebUI；
- ChatGPT / WorkBuddy 类 Chat Surface；
- Codex；
- ZCode；
- OpenCode；
- Hermes。

不讲功能列表。

统一拆成：

```text
UI
↓
Harness
↓
Model Adapter / API
↓
Context
↓
Tool Loop
↓
Result
```

---

## 1.5 第四部分：为什么 Chat 到了复杂任务会不够

先承认 Chat 很适合：

- 问题解释；
- 改写；
- 总结；
- 一次性分析；
- 小段代码。

然后展示复杂任务：

> “把这个仓库里的 Bug 修掉并验证。”

Chat 只能给建议时：

```text
Prompt → Answer
```

Agent 需要：

```text
Goal
→ Plan
→ Read
→ Act
→ Observe
→ Verify
→ Iterate
→ Deliver
```

---

## 1.6 第五部分：Agent 的神秘能力从哪里来

先只建立最简单模型：

```text
Agent
=
Model
+ Harness
+ Workspace
+ Context
+ Tools
+ Runtime
```

暂时不深入每一个工具。

展示一个极简案例：

```text
Read file
→ Search
→ Edit
→ Run test
→ Read error
→ Fix
→ Test pass
```

让大家第一次看到：

> 模型不是直接改电脑，而是 Harness 给模型提供工具，模型不断根据工具反馈继续决策。

---

## 1.7 建议 Demo / 素材

P0：

1. Cherry `/models`；
2. 第一轮 Chat Request；
3. 多轮消息 Request；
4. Vision Request；
5. SSE；
6. Qwen Tool Calling；
7. Chat vs Agent 同任务；
8. Agent 一次完整 Read/Edit/Test Loop；
9. model-metric 性能页。

可大量使用录屏。

---

## 1.8 第一场最后留下什么

三句话：

> **Chat、Agent 都是模型之上的应用。**

> **模型负责生成和判断，Harness 负责组织上下文和工具调用。**

> **Agent 的能力既取决于模型，也取决于它能获得什么工具和运行环境。**

过渡到第二场：

> 如果模型和 Agent 都依赖外部 Context，那么部门自己的知识到底应该怎样建设？

---

# 第二次讲座：部门知识库——从需求出发建设可复用知识体系

> 内容映射：**2**

## 2.1 这场为什么必须单独讲

部门当前明确要建设知识库。

因此不能只讲：

> RAG 是什么。

而要回答：

> **我们到底有什么知识、不同工具需要什么知识、不同资产应该怎么处理、部门应该建设成什么样。**

---

## 2.2 第一部分：先从部门需求出发

不是先讲 Embedding。

先问：

- 想让 AI 回答哪些问题？
- 谁在用？
- 哪些内容必须权威？
- 哪些内容有权限？
- 哪些内容变化快？
- 哪些需要引用原文？
- 哪些实际上不是“文档”？

列出典型资产：

- 制度；
- 标准；
- 产品资料；
- 设计文档；
- 测试报告；
- Git 仓库；
- API 文档；
- 配置；
- DB；
- 日志；
- 运行指标。

---

## 2.3 第二部分：知识资产不是一种东西

建立分类：

### 文档知识

适合：

`Parse → Chunk → Search / BM25 / Vector / Hybrid`

### 代码 / 配置

优先：

`Tree → Search → Read → Git History`

### 结构化数据

优先：

`SQL / Query`

### 实时系统

优先：

`API / MCP`

### 日志 / 指标

优先：

`Search / Query / Monitoring API`

核心观点：

> **不是所有知识都应该转成 PDF 再向量化。**

---

## 2.4 第三部分：传统 RAG 的工程机制

讲清：

- Parse；
- OCR；
- Chunk；
- Metadata；
- BM25；
- Embedding；
- Vector；
- Hybrid；
- Filter；
- Query Rewrite；
- Top-K；
- Rerank。

但始终围绕问题：

> **为什么需要它？什么时候用？**

---

## 2.5 第四部分：长上下文为什么不能取代知识库

结合论文和已有证据讲：

- Context Window；
- Lost in the Middle；
- Retrieval Recall；
- Context Utilization；
- Context Budget；
- Evidence Budget。

结论：

> **Context 很长，不等于把所有部门资料一次性塞进去就能可靠回答。**

---

## 2.6 第五部分：不同工具怎样使用知识

这是这场的重点之一。

### Cherry Studio

偏：

- 个人；
- 本地；
- 轻量；
- 文档知识。

### Open WebUI

偏：

- 共享；
- 管理员维护；
- 多用户；
- 集中式 RAG。

### Agent

可以同时使用：

- Knowledge / RAG；
- Workspace；
- File Search；
- Git；
- DB；
- API；
- MCP。

因此：

> Agent 能承接更复杂的多源知识获取，但不意味着传统共享知识库没有价值。

---

## 2.7 第六部分：统一部门知识架构

最终建议不是：

```text
Cherry 建一套
Open WebUI 建一套
Agent 再建一套
```

而是：

```text
Source of Truth
        ↓
Knowledge Processing / Access
        ↓
┌────────┬─────────┬────────┐
Cherry  OpenWebUI   Agent   App
```

---

## 2.8 第七部分：治理和验收

必须讲：

- Source Owner；
- ACL；
- Version；
- Stale；
- Duplicate；
- Conflict；
- Citation；
- Index Refresh。

以及测试集：

- answerable；
- no-answer；
- exact ID；
- version conflict；
- cross-document；
- ACL；
- stale data；
- citation。

---

## 2.9 建议 Demo / 素材

最重要的是“同源三层”：

```text
同一套资料
→ Cherry
→ Open WebUI
→ Agent
```

并增加：

- 一个 BM25 更合适的问题；
- 一个 Vector 更合适的问题；
- 一个 Hybrid 问题；
- 一个 no-answer；
- 一个冲突版本；
- 一个代码问题让 Agent 直接 Search/Read，而不是 RAG。

---

## 2.10 第二场最后留下什么

> **部门知识库不是一个软件功能，而是一套知识资产治理和访问体系。**

---

# 第三次讲座：深入 Agent——抛开 UI，看懂 Harness、工具、环境与共性能力

> 内容映射：**4 + 5**

## 3.1 这场真正要解决什么

前两场之后，大家已经知道：

- 模型怎么被调用；
- Chat / Agent 基本区别；
- Knowledge 怎么进入模型。

第三场开始真正教：

> **怎样放心使用多个不同 Agent。**

目标不是学会某一个 ZCode / Codex。

而是掌握：

> **换一个 Agent 仍然知道该看哪里、配什么、怎么判断它能不能完成任务。**

---

## 3.2 第一部分：把 Agent 拆开

统一结构：

```text
Model Provider / API
        ↓
Harness
        ├─ System / Project Instructions
        ├─ Context Manager
        ├─ Plan / Task State
        ├─ Memory
        ├─ Tool Registry
        ├─ Permission / Sandbox
        ├─ Session / Resume
        └─ Observability
        ↓
Workspace
        ↓
Runtime / External World
```

讲清：

- Model Adapter；
- Context；
- Compaction；
- Memory；
- Project Rules；
- Plan；
- Session；
- Sub-agent；
- Permission；
- Secrets。

---

## 3.3 第二部分：多个 Agent 为什么可以用同一种方法理解

横向使用：

- Codex；
- ZCode；
- OpenCode；
- Hermes；
- WorkBuddy；
- 其他现有 Agent。

不比较“谁最好”。

看：

- 模型怎么接；
- Workspace 在哪；
- 项目规则文件是什么；
- Memory 怎么做；
- Tool 在哪；
- Browser 在哪；
- Shell 在哪；
- Permission 怎么控制；
- Resume / Compaction 怎么做。

最终形成：

> **Agent 能力检查清单。**

---

## 3.4 第三部分：Agent 宿主环境怎么准备

让大家知道为什么经常要准备：

- Git；
- Python；
- pip / uv；
- Node.js；
- npm / npx；
- curl；
- jq；
- Playwright；
- Chromium；
- Docker；
- SSH；
- ffmpeg。

并讲：

- Local；
- WSL；
- Container；
- Cloud Runtime；
- Remote SSH。

---

## 3.5 第四部分：Agent 怎样操作宿主机

### File

Search / Read / Edit。

### Shell

命令执行。

### Git

Diff / Commit / Push / PR。

### Browser

深入讲：

- Playwright；
- CDP；
- Browser Use；
- Computer Use；
- Crawler。

让大家真正理解：

> Agent 并不是“看到网页就神奇地点”，而是可能通过 DOM、CDP、浏览器自动化或视觉 GUI 等不同通道工作。

---

## 3.6 第五部分：Agent 怎样接企业能力

从第一场讲过的 API 再往前一步。

### Tool Calling

模型怎样请求工具。

### MCP

AI Host 怎样标准连接外部能力。

### Skill

怎样把工作方法交给 Agent。

### Command / Hook / Plugin

它们分别解决什么。

重点：

```text
API = 系统能力接口
Tool = 模型可调用动作
MCP = Host 与能力提供方的标准连接
Skill = 可复用工作方法
```

---

## 3.7 第六部分：Agent 与外部世界的三个完整小案例

### 案例 A：代码仓库

`Read → Edit → Test → Diff`

### 案例 B：Browser

`Open → Interact → Inspect → Screenshot → Verify`

### 案例 C：Server

`SSH → Observe → Act → Logs → Health → Verify`

这里不做大型项目。

目标只是：

> **把 Agent 与宿主机 / 外界互动的机制讲透。**

---

## 3.8 第七部分：Permission 与安全

- read-only；
- edit；
- shell；
- network；
- credentials；
- production；
- approval；
- sandbox。

强调：

> **Skill 不是安全边界。**

---

## 3.9 第八部分：使用多个 Agent 的统一方法

给学员一张检查表：

1. 模型从哪接？
2. Context 怎么管理？
3. Workspace 在哪？
4. Project Rules 怎么写？
5. Shell 有没有？
6. Browser 是什么机制？
7. 能不能接 MCP / Tool？
8. Runtime 缺什么？
9. Permission 在哪控？
10. 怎样 Test / Verify？

掌握这 10 个问题以后，换 Agent 不需要重新学习整套世界观。

---

## 3.10 建议 Demo / 素材

大量截图非常适合本场：

- Codex Workspace；
- ZCode；
- Hermes；
- OpenCode；
- WorkBuddy；
- AGENTS.md；
- Memory；
- Tool / MCP；
- Shell；
- Browser；
- Permission；
- Terminal；
- Diff。

录屏：

- 同任务不同 Agent；
- Host Browser；
- Built-in Browser；
- Server；
- Tool Calling。

---

## 3.11 第三场最后留下什么

> **不要记某一个 Agent 的按钮，要理解它的 Harness、Workspace、Runtime、Tool 和 Permission。**

---

# 第四次讲座：Agent 工程实战——从需求到开发、测试、CI/CD 与部署

> 内容映射：**6 + 7 + 8**

## 4.1 这场真正要解决什么

前三场主要解决：

> 知道。

第四场解决：

> **怎么做。**

整场尽量减少新概念，以真实项目、截图、Git 历史和录屏为主。

---

## 4.2 统一工程方法

先只给出一张图：

```text
Problem
→ Requirement
→ Constraint
→ Research
→ Architecture
→ Plan
→ Implement
→ Test
→ Visual / Runtime QA
→ Review
→ Release
→ Deploy
```

然后所有案例都套这套方法。

---

## 4.3 主案例一：BMQuiz——Web 应用完整工程闭环

完整讲：

### Problem

旧应用和真实需求。

### Requirement

Product Spec。

### Constraint

数据、认证、多端、部署。

### Research

技术路线 / GitHub 参考 / library。

### Architecture

React / Fastify / SQLite / Auth / PWA / TWA。

### Plan

文档先行。

### Implement

只选几个关键实现。

### Test

Unit / Integration / Migration。

### Visual QA

Playwright / Screenshot。

### Git

Branch / Diff / PR。

### CI/CD

Actions / Docker / GHCR。

### Deploy

SSH / Compose。

### Verify

Health / Product Smoke / Security Smoke。

### Assetize

AGENTS / Docs / Test / CI / Deployment。

---

## 4.4 主案例二：FileCheck——本地客户端完整闭环

重点体现：

> 同一方法换到完全不同技术栈仍然成立。

从：

- Windows / Offline / Win7；
- Python vs Go 预研；
- Core / CLI；
- GUI；
- Reliability；
- Test；
- CustomTkinter；
- PyInstaller；
- x86/x64；
- GitHub Action；
- Release。

---

## 4.5 CI/CD 不单独讲理论，直接放进真实项目

### BMQuiz

`Commit → CI → Visual QA → Docker → GHCR → Deploy`

### FileCheck

`Commit → pytest → Build → PyInstaller → Artifact Verify → Release`

### HyperFrames

`Commit → Render Action → Video Artifact`

让大家看到：

> CI/CD 不是“大公司 DevOps 概念”，而是 Agent 工程闭环的一部分。

---

## 4.6 服务器操作也放进完整工程

不单独做 SSH 教程。

BMQuiz：

`Release → SSH → Docker Pull → Deploy → Logs → Health → Smoke`

model-metric：

`Update → systemd → logs → API semantics`

---

## 4.7 专题实操案例：展示 Agent 不只是编程

主案例讲深，以下案例讲短而精彩。

### IPsec VPN 数据分析

展示：

`Data → Hypothesis → Analysis → Evidence → Verify`

### HyperFrames

展示：

`Narrative → Storyboard → HTML Animation → Timeline → Render`

### 授权机制 / 协议研究

展示：

`Observe → Trace → Hypothesis → Script → Verify → Evidence`

只限授权研究。

### 网站安全测试

展示：

`Scope → Test → Evidence → Fix → Regression`

使用授权环境。

---

## 4.8 建议本场的展示比例

这一场建议与前三场明显不同：

```text
理论        20%
Git/文档    20%
截图        20%
录屏/Demo   40%
```

甚至可以更偏实操。

---

## 4.9 第四场最后收束整个系列

最终让大家带走：

### 使用模型

知道任务该用什么模型和 Thinking。

### 使用知识

知道何时 Search / RAG / Read / DB / API。

### 使用 Agent

知道怎样准备 Workspace / Runtime / Tool / Permission。

### 做工程

知道不能 Prompt → Code。

### 做验证

知道 Test / Browser / CI / Health / Evidence。

### 做资产

知道把成功做法沉淀成：

- AGENTS；
- Skill；
- Script；
- Test；
- CI；
- Knowledge；
- Template；
- Git。

---

# 5. 四次讲座之间的逻辑

```text
第一次
看懂 AI 应用底层
API / Model / Chat / Agent
        ↓
第二次
解决“AI 从哪获得部门知识”
Knowledge / RAG / Governance
        ↓
第三次
解决“Agent 怎么真正工作”
Harness / Runtime / Tools / MCP / Skill
        ↓
第四次
解决“怎么把这些东西用于真实工作”
Git / Development / Test / CI/CD / Deploy / Cases
```

---

# 6. 为什么这个四场结构比八场现场授课更适合当前培训

## 好处一：前两场都能独立成立

第一场解决底层认知。

第二场直接服务部门知识库建设。

## 好处二：Agent 不被拆得太碎

原来的 3 / 4 / 5 分三次容易让学员觉得：

> Agent 怎么讲了三遍？

现在：

- 第一场只揭开 Agent 机制；
- 第三场一次真正讲深。

## 好处三：案例集中以后更有冲击力

前三场建立认知。

第四场直接展示：

> 我们真的已经用 Agent 做出了这些东西。

## 好处四：非常适合截图与录屏

第一场：

> Network / API。

第二场：

> Knowledge Retrieval。

第三场：

> 多 Agent UI / Terminal / Browser / Server。

第四场：

> Git History / Development / QA / CI/CD / Deploy / Final Product。

每场视觉素材类型都不同，不容易疲劳。

---

# 7. 一个需要注意的风险

第四场内容量仍然最大。

因此不要试图把 BMQuiz、FileCheck、IPsec、HyperFrames、安全案例全部“完整讲”。

建议：

### 完整讲

- BMQuiz；
- FileCheck 选择关键链路。

### 快速案例

- IPsec；
- HyperFrames；
- Protocol Research；
- Security Testing。

原则：

> **两个纵向案例证明方法，多个横向案例证明适用范围。**
