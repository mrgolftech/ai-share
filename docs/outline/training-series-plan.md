# AI 大模型与 Agent 工程实践培训——8 个内容单元

> 状态：Content Structure v1.0  
> 日期：2026-09-30  
> 依据：`docs/outline/training-outline.md` 当前完整讲义基线  
> 用途：维护 1～8 个内容单元，不再代表现场授课次数。  
> 正式现场授课按 `13 / 2 / 45 / 678` 组织为 4 次，见 `docs/outline/training-4-session-leadership-proposal.md`。

---

# 1. 为什么拆成系列培训

当前讲义已经覆盖：

- 模型 API、Token、Context、Thinking、MoE、推理性能；
- Chat、Knowledge、RAG；
- Agent Harness、Workspace、Context、Memory、Plan；
- File / Shell / Git / Browser / SSH / Docker / API / CI；
- MCP / Skill / Plugin / Command / Hook；
- 可复用工程资产；
- Agent 工程方法论；
- 多个真实项目案例。

如果强行压缩成一次讲座，会出现两个问题：

1. 概念密度过高，学员只能“听过”，无法形成可操作心智模型；
2. 真实工程案例没有时间展开，最终又会退化成工具和概念介绍。

因此调整为：

> **系列培训 + 同一工程主线 + 多个真实项目案例。**

每次培训仍然遵守：

> **一个问题 → 一个真实案例 → 一个方法 → 一个结论。**

---

# 2. 八个内容单元

以下 1～8 用于保持知识边界、案例和素材的可维护性。它们不是现场授课次数；现场授课已经正式合并为四场。

---

# 第 1 次：模型到底怎么被调用——从 Chat UI 到模型 API

## 核心问题

> 我们在聊天框里输入一句话，背后到底发生了什么？

## 内容

- HTTP / JSON / Request / Response；
- OpenAI Chat / Responses / Anthropic Messages；
- SSE；
- Token；
- Context Window；
- Thinking / reasoning budget；
- MoE；
- Prefill / Decode / TTFT / TPS / KV Cache / 并发；
- 内网 Qwen API 当前实测。

## 主证据

- Cherry Studio Network；
- Qwen API 自动测试；
- `/metrics`；
- model-metric。

## 学完应该带走

> 大模型不是“聊天软件”，而是有协议、上下文、算力、延迟与成本的计算服务。

---

# 第 2 次：部门知识库怎么建——从资料堆到可治理的 AI 知识基础设施

## 核心问题

> 部门有大量文档、代码、规范、测试数据和系统数据，怎样把它们建设成 Chat、应用和 Agent 都能可靠使用的知识体系？

## 这次培训单独成场的原因

知识库不是 Chat 软件里的一个“上传文件”功能，而是部门后续 AI 应用的公共基础能力。

这场培训重点不是让学员记住 RAG 名词，而是建立一套能够直接指导部门知识库建设的工程方法。

## 内容

### A. 先定义“知识资产”

- 什么是 Source of Truth；
- 原始资料、索引、缓存、生成答案的区别；
- 文档、代码、配置、数据库、API、日志、实时指标为什么不能统一当 PDF 处理；
- 哪些资产应该进入部门知识体系，哪些不应该。

### B. 文档进入知识库之前发生什么

- Parse；
- OCR 边界；
- Chunk；
- Metadata；
- 标题层级；
- 表格、图片、代码块；
- 文档格式规范；
- 版本与来源标识。

### C. Retrieval 到底怎么做

- 全文搜索 / BM25；
- Embedding / Vector；
- Hybrid；
- Rerank；
- Top-K；
- Query Rewrite；
- Metadata Filter；
- 不同问题为什么需要不同 Retrieval。

### D. Context 不是无限知识容量

- Context Window；
- Lost in the Middle；
- 长上下文召回；
- External Retrieval Recall vs In-context Utilization；
- Context Budget；
- Evidence Budget；
- 为什么“检索越多”不一定越好。

### E. 部门知识治理

- ACL / 权限；
- 版本；
- 过期资料；
- 重复资料；
- 冲突资料；
- 引用与溯源；
- 更新和重建索引；
- 谁负责维护 Source of Truth。

### F. 三类工具怎样使用同一套知识

- Cherry Studio：个人/轻量知识工作台；
- Open WebUI：共享知识库与多人访问；
- Agent：Workspace + Search + Read + RAG + DB/API/MCP 的多源取证。

重点说明：

> Agent 可以承接前两类知识资产，但不应该把所有知识都强行向量化。

### G. 怎样评测知识库是否真的可用

至少设计：

- answerable；
- no-answer；
- 版本冲突；
- 权限；
- 精确编号/型号；
- 跨文档组合；
- 长文档定位；
- 引用准确性；
- Retrieval Recall；
- Context Utilization。

## 主 Demo

使用**同一套真实部门资料**，分别演示：

```text
Cherry Studio
→ Open WebUI Shared Knowledge
→ Agent 多源逐步取证
```

控制变量：

> **资料不变，只改变检索方式和使用入口。**

## 对应讲义

- `docs/chapters/03-department-knowledge-base-teaching.md`：主讲教学版；
- `docs/chapters/03-department-knowledge-base.md`：完整技术稿；
- `docs/architecture/department-knowledge-architecture.md`：部门架构；
- `docs/references/knowledge-base-rag-evidence-2026-09.md`：证据基线；
- `demos/knowledge-retrieval/README.md`：统一 Demo。

## 学完应该带走

> **知识库首先是知识资产和治理问题，其次才是向量数据库问题。**

以及：

> **知识原文是资产，索引是派生物，Cherry / Open WebUI / Agent 只是不同入口。**

---

# 第 3 次：为什么 Chat 不够——从 Chat 工作台走向 Agent

## 核心问题

> 如果知识已经能查到了，为什么复杂工程任务仍然不能只靠 Chat？

## 内容

- Chat 适合什么；
- Open WebUI / Cherry Studio 作为 Chat / Knowledge 工作台；
- Prompt → Answer 的局限；
- Chat → Workspace；
- Agent Harness；
- Workspace；
- Context / Plan / Memory；
- Tools；
- Permission / Verification；
- CLI / GUI / IDE / Web Surface；
- WorkBuddy 等“Chat Surface 背后已有 Runtime”的例子。

## 主案例

- 同模型 Chat vs Agent；
- 鹈鹕统一案例；
- WorkBuddy Chat → Workspace → Artifact；
- 一个需要修改真实仓库的小任务。

## 学完应该带走

> **知识库解决“模型去哪里找知识”；Agent 进一步解决“模型怎样围绕目标持续行动和验证”。**

---

# 第 4 次：Agent 为什么能真正干活——Workspace、工具、Runtime 与服务器

## 核心问题

> 模型只会生成 Token，为什么 Agent 能改代码、开浏览器、登录服务器？

## 内容

- Model vs Harness；
- Workspace；
- AGENTS.md / Project Rules；
- Plan / Memory / Context；
- File / Search；
- Shell；
- Git；
- Browser Use / Playwright / CDP / Computer Use；
- SSH；
- Docker；
- API；
- Agent Runtime / Environment Engineering；
- Permission / Sandbox / Approval；
- Verification。

## 主案例

### A. ZCode Sensor Guard

展示：

`Read → Test Fail → Search → Edit → Test Pass → Diff`

### B. Agent 操作服务器

使用两个真实项目：

- BMQuiz：SSH → Docker Compose → image pull → up → logs → health → rollback；
- model-metric：SSH → systemd → journalctl → health/API → 配置 → restart → verify。

详见：

`docs/cases/agent-server-operations.md`

## 学完应该带走

> Agent 能力不只取决于模型；Harness、Runtime、工具权限和验证闭环同样重要。

---

# 第 5 次：怎样让 Agent 掌握企业工具——API、MCP、Skill 与可复用资产

## 核心问题

> 有 API 了为什么还要 MCP？有 MCP 为什么还要 Skill？

## 内容

- API；
- Tool / Function Calling；
- MCP；
- Skill；
- Plugin；
- Command；
- Hook；
- Script；
- AGENTS.md；
- Memory；
- Test / Eval；
- CI；
- Knowledge；
- Evidence；
- Git。

## 统一 Demo

同一个后端能力：

`Raw API → MCP Tool → Skill + MCP`

## 主案例

- 本仓库 `ai-share` 本身作为资产沉淀案例；
- project-acceptance Skill。

## 学完应该带走

> 工具会变化，但规则、Skill、脚本、测试、CI 和知识资产可以留下来。

---

# 第 6 次：完整工程案例（一）——Agent 怎样从需求开发一个 Web 应用

## 核心问题

> 如果今天给 Agent 一个真实 Web 产品需求，应该怎样从 0 走到上线？

## 主案例：BMQuiz V2

BMQuiz 当前仓库具备：

- Product Function Spec；
- UI/UX Spec；
- Technical Architecture；
- Data Model；
- Routing / State Design；
- Project Structure；
- Development Roadmap；
- Codex Implementation Guide；
- Acceptance Checklist；
- Deployment；
- Design System；
- Visual QA；
- CI / Server CI；
- Docker / GHCR；
- PWA / Android TWA。

因此非常适合还原完整工程链：

```text
Problem
→ Requirement
→ Constraint
→ Research
→ Architecture
→ Plan
→ Implement
→ Test
→ Visual QA
→ Review
→ Docker
→ CI/CD
→ SSH Deploy
→ Health Check
→ Release
```

## 对照案例：model-metric

用于说明：

- 同样是 Web 应用，但需求性质不同；
- 监控系统需要特别关注数据口径、实时采集、持久化、部署和可观测性；
- “前后端架构”不是只有一种固定模板。

## 学完应该带走

> 不要从 Prompt 直接跳到 Code；需求、约束、架构、验收标准会直接决定 Agent 编码质量。

---

# 第 7 次：完整工程案例（二）——本地客户端 / GUI / 打包发布

## 核心问题

> Agent 怎样开发一个不是网页的真实 Windows 工具？

## 主案例：FileCheck

当前真实仓库已经包含：

- REQUIREMENTS；
- ARCHITECTURE；
- TEST_PLAN；
- GUI Design System；
- Python core；
- CLI；
- CustomTkinter GUI；
- Win7 / Win10 / Win11 兼容约束；
- PyInstaller；
- Windows/Linux CI matrix；
- Win7 x86/x64 build；
- GUI build；
- GitHub Release。

教学链：

```text
用户需求
→ 平台/兼容性约束
→ 技术路线预研
→ Python vs Go 等候选
→ GUI 框架候选
→ 核心业务层先行
→ CLI 验证
→ GUI 只包装核心能力
→ 自动测试
→ GUI smoke
→ PyInstaller
→ Actions
→ Release
```

注意：

> 当前仓库事实是 Python + CustomTkinter；如果培训要讲“Python vs Go / CustomTkinter vs PyQt/PySide”的选择过程，需要根据历史提交、文档或重新做技术调研来重建证据，不能把后验解释伪装成当时真实决策。

## 学完应该带走

> Agent 不只是写 UI；它可以参与技术预研、架构边界、兼容性验证、打包和发布。

---

# 第 8 次：跨领域案例——数据分析、安全研究与内容生产

## 核心问题

> 除了开发软件，Agent 还能把哪些知识工作重新组织成“可执行闭环”？

## 案例 A：IPsec VPN 测试数据分析

展示：

- 读取测试数据；
- 建立假设；
- 发现异常；
- 关联链路、报文、RTT 等因素；
- 找到十兆以太网瓶颈线索；
- 再通过工程事实验证。

重点：

> 模型提出线索，实验负责验证；不能把相关性直接当因果。

## 案例 B：HyperFrames 视频生产

真实资产位于 `mrgolftech/ai-use`，已有 Kids / Metric / Wafer 多套工程：

```text
文案
→ 分镜
→ HTML/SVG/GSAP
→ Timeline
→ 音频/字幕
→ Preview
→ Review
→ GitHub Actions
→ Render
```

用于说明：

> Agent 可以参与复杂内容生产流水线，而不只是代码开发。

## 案例 C：授权机制 / 协议行为研究

使用 `eda365skill` 只讲：

- 程序行为观察；
- 静态/动态证据；
- 接口与数据格式；
- 兼容性研究；
- 自动化验证；
- 如何把研究过程沉淀为脚本、数据集和文档。

边界：

> 只用于已授权系统、兼容性与安全研究；培训不讲绕过授权、生成未授权许可、绕过付费或扩大第三方访问权限的方法。

## 案例 D：网站安全测试

优先使用：

- 自己控制的开发/测试环境；
- BMQuiz staging；
- 或专门的授权靶场。

完整闭环：

```text
Scope
→ Threat / Test Plan
→ Automated Scan
→ Manual Verification
→ Evidence
→ Fix
→ Regression Test
→ Report
```

重点不是“攻击技巧”，而是：

> **授权范围、证据链、修复与回归。**

## 最终收束

回到：

`docs/chapters/08-agent-engineering-methodology.md`

---

# 3. 两类案例必须区分

## 3.1 贯穿式完整案例

要把完整工程链讲全：

- BMQuiz；
- FileCheck。

这两个是系列培训中的“纵向主案例”。

## 3.2 专题案例

只证明某一类 Agent 能力：

- model-metric；
- Agent 服务器运维；
- IPsec VPN 数据分析；
- HyperFrames；
- 授权协议研究；
- 网站安全测试；
- 文档处理；
- Knowledge / RAG。

不要要求每个专题案例都重新讲一遍需求、架构、CI/CD。

---

# 4. 一个重要教学原则：同一案例在多次培训中重复出现

不是：

> 第一次讲 API 用案例 A，第二次讲 Agent 再换案例 B，第三次讲 CI 又换案例 C。

而是让 BMQuiz / FileCheck 在不同阶段重复出现。

例如 BMQuiz：

```text
第 3 次：为什么 Chat 不足以完成这个项目
第 4 次：Workspace / Browser / Git / Server
第 5 次：AGENTS.md / Skill / CI 作为资产
第 6 次：完整工程闭环
```

这样学员最终看到的是：

> 同一个真实项目中的不同 Agent 机制。

---

# 5. 当前优先级

在案例证据还未集中补录前，先完成：

1. 8 次培训的章节映射；
2. BMQuiz 完整工程案例讲义；
3. FileCheck 完整工程案例讲义；
4. Agent 服务器运维案例讲义；
5. 将其他专题案例只建立结构和证据清单；
6. 最后再集中补截图、录屏和 Git 历史证据。

