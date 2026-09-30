# AI 大模型与 Agent 工程实践培训——8 次讲座完整划分（评审稿）

> 状态：Review Draft v0.1  
> 日期：2026-09-30  
> 用途：用于评审 8 次讲座的边界、顺序与整合方式；评审后再固化为正式授课基线。

---

# 0. 总体主线

8 次培训不是 8 个孤立专题，而是一条连续主线：

```text
1 模型是什么、怎么调用
        ↓
2 模型怎样获得部门外部知识
        ↓
3 为什么知道知识还不够，需要 Agent
        ↓
4 Agent 怎样真正操作文件、浏览器、服务器和代码
        ↓
5 怎样把企业能力接给 Agent，并沉淀为可复用资产
        ↓
6 用 Web 项目完整走一遍工程闭环
        ↓
7 用本地客户端再验证同一套工程方法
        ↓
8 看 Agent 如何扩展到分析、安全研究和内容生产
        ↓
最终收束：形成统一 Agent 工程方法
```

总体观点保持：

> **模型负责判断和生成，工具负责执行，自动化测试负责验证，人负责目标、约束和最终判断。**

---

# 1. 第一次：模型到底怎么被调用——从 Chat UI 到模型 API

## 1.1 目标

让学员先把“大模型”从一个聊天网页还原成：

> **可以通过 API 调用、有上下文、有推理成本、有延迟和吞吐约束的计算服务。**

这是后面理解 Chat、RAG、Agent、Tool Calling 的基础。

## 1.2 内容边界

### A. 从真实 Chat 请求开始

- Cherry Studio / Open WebUI 只是客户端；
- HTTP；
- URL / Endpoint；
- GET / POST；
- Header / API Key；
- JSON；
- Request / Response；
- Status Code；
- SSE 流式返回。

### B. 模型 API 的三套常见接口形态

- OpenAI Chat Completions；
- OpenAI Responses；
- Anthropic Messages；
- models / tokenize / detokenize 等辅助接口。

重点不是背协议，而是理解：

> 应用和模型服务之间就是结构化请求与响应。

### C. 一轮对话和多轮对话到底发生了什么

- system / user / assistant；
- 历史消息怎样重新进入请求；
- Context 是怎么累积的；
- 图片怎样作为多模态输入附加；
- Tool Calling 请求怎样出现在模型输出中。

### D. Token 与 Context

- Token 是什么；
- 输入 / 输出 Token；
- Context Window；
- 长上下文不是免费；
- Context 越长，成本、延迟和可用性都会变化。

### E. Thinking / Reasoning

- 普通生成 vs reasoning；
- Thinking 开关；
- reasoning budget；
- 为什么复杂任务更需要推理；
- 为什么不是所有任务都应该开最大 Thinking。

### F. 模型架构只讲和工程使用直接相关的部分

- Dense / MoE；
- Active Parameters；
- 参数量不能直接等价于速度；
- 模型大小、量化、硬件和并发共同影响服务能力。

### G. 推理性能

- Prefill；
- Decode；
- TTFT；
- TPOT / ITL；
- TPS；
- KV Cache；
- running / waiting；
- 并发；
- 为什么“单人很快”不等于“共享服务好用”。

## 1.3 Demo / 证据

主线：

```text
Postman / curl
→ Cherry Studio Network
→ Python API 自动测试
→ /metrics
→ model-metric
```

使用内网 Qwen 实测作为最高优先级证据。

## 1.4 本次不讲

- RAG 细节；
- Agent 工具；
- MCP / Skill；
- 软件工程方法。

## 1.5 本次结论

> **模型是计算服务，Chat 是客户端；Token、Context、Thinking、并发都是真实工程资源。**

## 1.6 与下一次的过渡

提出问题：

> **模型本身不知道部门内部资料，而且内部资料一直变化，怎么办？**

---

# 2. 第二次：部门知识库怎么建——从资料堆到可治理的 AI 知识基础设施

## 2.1 目标

不是教大家“上传 PDF 建 RAG”，而是让部门建立：

> **知识资产 → 检索 → Context → 权限 → 版本 → 评测 → 多入口复用**

的统一知识工程方法。

## 2.2 内容边界

### A. 为什么模型需要外部知识

- 参数知识；
- 私有知识；
- 新知识；
- 动态知识；
- 可追溯知识。

### B. 知识库到底是什么

从：

```text
PDF → Embedding → Vector DB
```

升级为：

```text
Source
→ Parse / Normalize
→ Index
→ Retrieval
→ Context Control
→ Chat / Agent / App
```

强调：

> 原文是资产，索引是派生物，客户端只是入口。

### C. 部门知识资产分类

至少区分：

- Word / PDF / Markdown / Wiki；
- 标准规范；
- 测试报告；
- 代码；
- 配置；
- Git；
- API；
- 数据库；
- 日志；
- 实时指标。

核心原则：

> **不同知识，不要用同一种检索方法。**

### D. 文档怎样进入知识库

- Parse；
- OCR；
- Heading；
- Chunk；
- Chunk overlap；
- Metadata；
- Table；
- Image；
- Code block；
- 文档格式与版本规范。

### E. Retrieval

- Full-text / BM25；
- Embedding；
- Vector Search；
- Hybrid；
- Metadata Filter；
- Query Rewrite；
- Top-K；
- Rerank。

重点回答：

> 哪类问题适合哪种检索方式。

### F. Context 与长上下文限制

- Context Window；
- Lost in the Middle；
- Retrieval Recall；
- Context Utilization；
- Rerank；
- Context Budget；
- Evidence Budget。

结论：

> **检索更多 ≠ 回答更可靠。**

### G. 知识治理

- Source of Truth；
- 文档 owner；
- ACL；
- 版本；
- 重复；
- 冲突；
- 过期；
- 引用；
- 更新；
- 索引重建。

### H. 三种实际入口

同一知识资产分别被：

- Cherry Studio；
- Open WebUI；
- Agent；

使用。

这里重点讲区别：

- Chat Knowledge：一次问答式检索；
- Shared RAG：多人共享知识入口；
- Agent：Search / Read / DB / API / MCP 多源逐步取证。

### I. 评测与验收

测试集至少包含：

- answerable；
- no-answer；
- exact ID / 型号；
- long document；
- cross-document；
- version conflict；
- ACL；
- citation；
- stale data。

## 2.3 Demo

固定采用同一份部门资料：

```text
Cherry Studio
→ Open WebUI
→ Agent
```

只改变入口和检索方式。

## 2.4 本次不讲

- Agent 文件修改；
- Shell；
- Git；
- MCP / Skill 的实现细节。

## 2.5 本次结论

> **部门知识库首先是知识资产和治理问题，其次才是向量数据库问题。**

## 2.6 与下一次的过渡

提出问题：

> **即使模型现在“知道”资料了，如果任务是修改项目、运行程序、部署系统，Chat 仍然做不了什么？**

---

# 3. 第三次：为什么 Chat 不够——从对话界面走向 Agent Harness

## 3.1 目标

建立 Agent 的统一心智模型，避免把 Codex、ZCode、Hermes、OpenCode、WorkBuddy 看成完全不同的东西。

## 3.2 内容边界

### A. Chat 擅长什么

- 独立问题；
- 解释；
- 改写；
- 资料总结；
- 轻量分析；
- 小段代码。

不要讲：

> Chat 已经过时。

### B. Chat 为什么在复杂工程任务中不够

典型信号：

- 多文件；
- 持续修改；
- Shell；
- Git；
- Browser；
- Server；
- Build；
- Test；
- 状态持续；
- 长任务。

从：

`Prompt → Answer`

走向：

`Goal → Plan → Read → Act → Observe → Verify → Iterate → Deliver`

### C. Agent Harness

讲清：

```text
Model
+
Harness
+
Workspace
+
Context
+
Tools
+
Runtime
+
Permission
+
Verification
```

模型本身不等于 Agent。

### D. Agent 的共同机制

- Workspace；
- Project Instructions；
- AGENTS.md / CLAUDE.md；
- Context；
- Plan；
- Memory；
- Tools；
- Permission / Sandbox；
- Session / Resume；
- Context Compaction；
- Sub-agent；
- Hooks / Automation；
- Secrets；
- Observability。

### E. CLI / GUI / IDE / Cloud Workspace

讲清选择逻辑：

- CLI；
- IDE；
- Desktop GUI；
- Cloud Workspace；
- Chat Surface + Runtime。

WorkBuddy 用来说明：

> 看起来像 Chat，后端也可以是可执行 Workspace。

### F. Agent 工具横向对比

ZCode / Codex / Hermes / OpenCode / WorkBuddy 等只用于说明：

> **界面不同，底层共同机制高度重合。**

不做功能说明书。

## 3.3 Demo

- 同一个任务：Chat 只能给步骤，Agent 直接进入仓库；
- Agent 读取 AGENTS.md；
- Search / Read；
- 生成 Plan；
- 执行一个小改动；
- Test；
- Diff。

可用 Sensor Guard 小案例或其他极小仓库任务。

## 3.4 本次不深讲

- Playwright / CDP；
- SSH / Docker；
- MCP；
- Skill。

这些放后面。

## 3.5 本次结论

> **Agent 不是“更会聊天的模型”，而是模型进入 Workspace、获得工具和反馈环境以后形成的执行系统。**

## 3.6 与下一次的过渡

提出：

> **Agent 有了 Harness，但到底怎么操作浏览器、Terminal、Git 和服务器？**

---

# 4. 第四次：Agent 怎样操作真实世界——File、Shell、Git、Browser、Server 与 Runtime

## 4.1 目标

让学员理解：

> **模型负责决策，真正改变外部世界的是工具和运行环境。**

## 4.2 内容边界

### A. File / Search / Read / Edit

- tree / glob；
- grep / rg；
- precise read；
- patch / edit；
- 为什么先 Search 再 Read；
- 为什么不要把整个仓库塞进 Context。

### B. Shell

- Python；
- Node.js / npm；
- CLI 工具；
- build；
- test；
- script；
- 环境变量；
- exit code；
- stdout / stderr。

### C. Git

- status；
- branch；
- diff；
- log；
- commit；
- push；
- PR；
- Git 既是版本控制，也是 Agent 的证据系统。

### D. Browser 三套机制

必须讲清：

#### Browser Automation

- Playwright；
- DOM；
- selector；
- network；
- console；
- screenshot。

#### CDP

- Chromium DevTools Protocol；
- 浏览器底层控制接口；
- Playwright 是更高层抽象；
- Agent 可以通过 Node/Python/CLI 与这些能力交互。

#### Computer Use

- screenshot；
- vision；
- mouse / keyboard；
- GUI；
- 对模型视觉和交互推理能力要求更高。

并区分：

- Browser Use；
- Computer Use；
- Crawler / HTTP Fetch。

### E. Agent Runtime

为什么 Agent 环境经常需要：

- Git；
- Python；
- Node/npm；
- Playwright/Chromium；
- Docker；
- SSH；
- curl；
- jq；
- ffmpeg；
- 内网包源。

### F. SSH / Server

- read-only observe；
- logs；
- Docker；
- systemd；
- config；
- restart；
- health；
- permission；
- approval。

### G. Verification

- Test；
- Build；
- Browser QA；
- Health；
- Logs；
- Diff；
- Domain-specific verification。

## 4.3 Demo

### Demo A：ZCode Sensor Guard

`Read → Failing Test → Edit → Test → Diff`

### Demo B：Browser

页面：

`Open → Interact → Console → Screenshot → Verify`

### Demo C：Server

BMQuiz：

`SSH → Docker Compose → logs → health`

model-metric：

`systemctl → journalctl → API semantic verification`

## 4.4 本次不讲

- MCP protocol 细节；
- Skill 设计；
- 完整应用架构。

## 4.5 本次结论

> **Agent 的能力 = 模型能力 × Harness × Runtime × Tools × Permission × Verification。**

## 4.6 与下一次过渡

提出：

> **如果公司里有大量 API、数据库和内部系统，难道每个 Agent 都重新写调用逻辑吗？**

---

# 5. 第五次：怎样让 Agent 掌握企业能力——API、Tool、MCP、Skill 与可复用资产

## 5.1 目标

回答：

> **怎样把企业已有能力接入 Agent，并把一次成功做法变成团队资产。**

## 5.2 内容边界

### A. API

- REST；
- SDK；
- CLI；
- DB；
- local script；
- API 是系统能力接口，不等于 AI Tool。

### B. Function / Tool Calling

- schema；
- tool request；
- harness executes；
- tool result；
- model continues。

### C. MCP

讲清：

```text
AI Host
↕ MCP
MCP Server
↕
API / DB / Files / Services
```

回答：

> 有 API 为什么还需要 MCP？

因为 MCP 解决的是：

> **AI Host 与外部能力提供方之间的标准连接方式。**

### D. Skill

回答：

> 有 MCP 为什么还需要 Skill？

MCP：

> 有哪些能力可以调用。

Skill：

> 这个任务应该按什么流程做、何时调用、怎样验证。

### E. Plugin / Command / Hook

- Plugin：打包和分发，产品相关；
- Command：用户主动触发入口；
- Hook：生命周期自动触发；
- Script：确定性执行；
- CI：确定性持续验证。

### F. Security

- Skill 不是安全边界；
- Permission；
- Approval；
- Credential Scope；
- Sandbox；
- Network；
- Audit。

### G. 可复用资产地图

从低到高：

```text
Prompt
→ Project Rules
→ Plan
→ Skill
→ Script
→ Test / Eval
→ CI
→ Template
→ Knowledge
→ Evidence
→ Git History
```

### H. Memory 与 Knowledge 再做一次边界回顾

只讲资产治理角度：

- Memory：用户/会话长期偏好或事实；
- Project Rules：项目必须遵守的规则；
- Knowledge：外部事实来源；
- Skill：流程；
- Script/Test：确定性执行/验证。

不重新讲第二次知识库。

## 5.3 Demo

同一个能力连续演示：

```text
Raw API
→ Tool
→ MCP Tool
→ Skill + MCP
```

再用 `ai-share` 自身展示：

- AGENTS.md；
- Skill；
- scripts；
- tests；
- CI；
- docs；
- evidence。

## 5.4 本次结论

> **工具会变，真正应该沉淀的是规则、流程、脚本、测试、知识和验收标准。**

## 5.5 与下一次过渡

提出：

> **这些东西放到一个真实软件项目里，到底是怎样协同工作的？**

---

# 6. 第六次：完整工程案例（一）——Agent 从需求开发 Web 应用

## 6.1 目标

用 BMQuiz 完整证明：

> **Agent 工程不是 Prompt → Code，而是从需求到 Release 的完整工程过程。**

## 6.2 主案例：BMQuiz V2

### A. Problem

- 为什么重构；
- oldquiz；
- 用户真正希望得到什么。

### B. Requirement

- Product Function Spec；
- 做什么；
- 不做什么。

### C. Constraint

- canonical 数据；
- local-first；
- 多设备；
- Auth；
- SQLite；
- 单容器；
- PWA / Android；
- Security。

### D. Research

- GitHub / 官方文档；
- 技术候选；
- 依赖评估；
- 不后验伪造历史。

### E. Architecture

- React / Fastify；
- Auth；
- SQLite；
- Data Flow；
- Domain；
- State；
- Sync；
- Deployment。

### F. Project Rules

- AGENTS.md；
- Design System；
- Coding / Testing / Release rules。

### G. Plan

文档体系：

- Product Spec；
- UI/UX；
- Architecture；
- Data Model；
- Roadmap；
- Codex Guide；
- Acceptance Checklist。

### H. Implement

只选代表性能力：

- canonical data；
- local-first；
- sync；
- auth；
- content security；
- responsive UI。

### I. Test

- typecheck；
- unit；
- integration；
- migration；
- health。

### J. Visual QA

- Playwright；
- screenshot；
- reference；
- Browser loop。

### K. Git / Review

- branch；
- diff；
- PR；
- CI。

### L. CI/CD

- frontend CI；
- Server CI；
- Visual QA；
- Release QA；
- Docker；
- GHCR；
- Android。

### M. Deploy

- SSH；
- Compose；
- SQLite protection；
- logs；
- health；
- smoke；
- rollback。

### N. Assetize

最后展示项目留下的：

- Rules；
- Docs；
- Tests；
- CI；
- Deployment；
- Release process。

## 6.3 对照案例：model-metric

只对照：

> 同样是 Web 应用，因为问题不同，架构和验证重点也不同。

重点：

- metrics semantics；
- collector；
- WebSocket；
- SQLite；
- systemd；
- service verification。

## 6.4 现场 Demo

不要现场从零写 BMQuiz。

做一个小增量需求：

```text
Requirement
→ Read Rules
→ Plan
→ Change
→ Test
→ Browser QA
→ Diff
```

## 6.5 本次结论

> **需求、约束、架构、验收标准决定 Agent 的搜索空间；自动验证决定它能不能持续迭代。**

---

# 7. 第七次：完整工程案例（二）——本地客户端、GUI、兼容性与发布

## 7.1 目标

用 FileCheck 证明：

> 同一套 Agent 工程方法不依赖 Web 技术栈。

## 7.2 主案例：FileCheck

### A. Problem

- Windows 终端文件自查；
- 大量文件；
- 批量备份；
- 恢复；
- 数据安全。

### B. Requirement

- scan；
- backup；
- verify；
- remove；
- resume；
- restore。

### C. Constraint

- Windows；
- Offline；
- Unicode；
- Everything；
- Win7；
- x86/x64；
- 大批量文件；
- SHA-256；
- 数据不能误删。

### D. Research / 技术路线

候选：

- Python vs Go；
- Everything API / CLI；
- CustomTkinter；
- PyQt / PySide；
- WebView；
- packaging。

必须区分：

> 当前项目事实 vs 事后技术 Review。

### E. Architecture

关键思想：

```text
Core
→ CLI
→ GUI
```

GUI 不重新实现业务逻辑。

### F. Reliability

- staging；
- manifest；
- hash；
- atomic replace；
- resumable；
- delete gate；
- restore verification。

### G. Test

- pytest；
- selftest；
- Python matrix；
- Windows/Linux；
- Python 3.8 compatibility；
- GUI construction smoke。

### H. GUI

- CustomTkinter；
- Design System；
- task runner；
- progress；
- error handling。

### I. Packaging

- PyInstaller；
- portable tools；
- x86/x64；
- Win7 package。

### J. CI/CD

- build workflow；
- artifact；
- validation；
- SHA256SUMS；
- GitHub Release。

## 7.3 这次重点对比 Web

Web：

> server runtime + browser.

FileCheck：

> local OS + filesystem + native GUI + packaging.

但工程流程仍然：

`Requirement → Constraint → Architecture → Plan → Implement → Test → Build → Release`

## 7.4 本次结论

> **Agent 工程方法可以跨技术栈复用，但架构必须服从平台和业务约束。**

---

# 8. 第八次：Agent 的跨领域应用——分析、安全研究、内容生产与方法论收束

## 8.1 目标

避免学员形成：

> Agent = AI 编程工具

的狭窄认识。

展示 Agent 的本质：

> **围绕目标组织知识、工具、观察和验证。**

## 8.2 案例一：IPsec VPN 测试数据分析

完整链：

```text
Problem
→ Data Inventory
→ Clean
→ Visualize
→ Hypothesis
→ Correlation
→ Architecture Evidence
→ Candidate Cause
→ Counter-check
→ Engineering Verification
→ Report
```

重点：

- 强模型；
- 数据处理工具；
- 图表；
- 多因素分析；
- 不能把相关性当因果。

## 8.3 案例二：HyperFrames 视频生产

```text
Narrative
→ Script
→ Storyboard
→ Design Spec
→ HTML / CSS / SVG / GSAP
→ Timeline
→ Voice / Subtitle
→ Preview
→ Human Review
→ GitHub Action
→ Render
```

展示：

- Kids；
- Metric；
- Wafer。

重点：

> Agent 能把内容生产也工程化。

## 8.4 案例三：授权机制 / 协议行为研究

只讲合法研究方法：

- scope；
- observation；
- trace；
- hypothesis；
- static/dynamic evidence；
- automation；
- version comparison；
- reproducibility；
- report。

不讲：

- 绕过付费；
- 未授权许可；
- 凭据窃取；
- 绕过授权。

## 8.5 案例四：网站安全测试

授权环境：

```text
Scope
→ Asset Inventory
→ Threat Model
→ Test Plan
→ Automated Check
→ Manual Verification
→ Evidence
→ Fix
→ Regression
→ Report
```

重点：

> 安全 Agent 的价值在闭环，不在“自动攻击”。

## 8.6 最终统一工程方法

最后回到：

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
```

同时强调：

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

最终回答五个问题：

1. 只是问问题？→ Chat；
2. 依赖资料？→ Search / Knowledge / RAG；
3. 要操作真实环境？→ Agent；
4. 是复杂工程？→ Workspace + Rules + Plan + Tools + Verification；
5. 会重复？→ Skill / Script / Test / CI / Knowledge。

## 8.7 本次结论

> **AI Agent 的长期价值，不是某一个产品界面，而是把团队工作逐步变成“目标清晰、上下文可控、工具可执行、结果可验证、方法可复用”的工程系统。**

---

# 9. 八次培训的职责边界

| 场次 | 只在这里首次讲透 | 后续只引用 |
|---|---|---|
| 1 模型/API | Token、Context 基础、Thinking、推理性能、API 协议 | 后面只谈 Context Budget 或 Tool Calling 时引用 |
| 2 知识库 | RAG、BM25、Vector、Hybrid、Rerank、知识治理 | 后面只把 Knowledge 当资产或工具 |
| 3 Chat→Agent | Harness、Workspace、Plan、Memory、Agent 共性机制 | 后面直接使用，不重复定义 |
| 4 Tools/Runtime | Shell、Git、Browser、Playwright/CDP、Computer Use、SSH/Docker | 后面案例直接使用 |
| 5 能力接入/资产 | API vs Tool vs MCP vs Skill、Plugin/Hook、资产体系 | 后面只展示实际应用 |
| 6 Web 工程 | 从需求到部署的 Web 完整闭环 | 不再重复讲工具定义 |
| 7 客户端工程 | 本地客户端/GUI/兼容性/打包发布 | 验证方法可跨栈复用 |
| 8 跨领域 | 数据分析、安全研究、内容生产 + 总方法论 | 最终收束 |

---

# 10. 两条贯穿主线

## 知识主线

```text
Model Context
→ External Knowledge
→ Retrieval
→ Agent Context
→ Project Rules
→ Knowledge Asset
```

## 行动主线

```text
Chat
→ Agent Harness
→ Tools / Runtime
→ MCP / Skill
→ Complete Engineering Loop
→ Reusable Team Assets
```

两条主线在第 6、7 次汇合。

---

# 11. 如果需要进一步压缩

如果实际只能安排 6 次，优先考虑：

- 合并第 3 + 第 4 次：Agent 原理 + Tool/Runtime；
- 合并第 7 + 第 8 次：客户端案例 + 跨领域案例精选。

不建议合并：

- 第 1 次模型/API；
- 第 2 次知识库；
- 第 5 次 MCP/Skill/资产；
- 第 6 次完整 Web 工程案例。

因为这四场承担不同的基础认知和实践任务。
