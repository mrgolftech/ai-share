# 模块五：如何形成可复用资产——把一次成功任务变成团队能力

> 状态：已有初稿 / 待案例与素材补充  
> 更新日期：2026-09-30  
> 上一章：`06-api-mcp-skill-plugin-command-hook.md`  
> 对应培训主线：**如何让 Agent 掌握工具 → 如何形成可复用资产 → 用真实项目证明 Agent 能完成什么**

---

## 0. 这一章先回答一个最现实的问题

前面已经讲了：

- 模型怎么调用；
- Chat 为什么不够；
- Agent 怎样操作文件、Shell、Git、浏览器和服务器；
- API、MCP、Skill 等能力怎样接入。

但如果每次新任务都从零开始：

```text
重新解释项目
→ 重新告诉模型规则
→ 重新描述测试流程
→ 重新找资料
→ 重新写脚本
→ 重新踩一遍坑
```

那么 Agent 只是：

> **把一次任务做快了。**

真正形成团队能力，需要继续问：

> **这次任务中，哪些东西值得留下来，让下一次不用重新发明？**

这一章的核心不是“存得越多越好”，而是：

> **把稳定、可复用、可验证的知识放到正确的载体里。**

---

# 1. 先看本仓库：其实我们已经在做资产沉淀

本培训仓库本身就是最好的案例。

当前已经存在：

```text
AGENTS.md
docs/outline/training-outline.md
docs/chapters/
docs/references/
docs/cases/
demos/
api/qwen/
.github/workflows/
```

它们分别在解决不同问题：

| 资产 | 解决的问题 |
|---|---|
| AGENTS.md | 这个项目长期应该怎样工作 |
| training-outline.md | 培训内容当前基线是什么 |
| chapters | 完整知识如何被讲清 |
| references | 事实依据从哪里来 |
| cases | 真实项目证据是什么 |
| demos | 如何可重复演示 |
| api/qwen | 如何可重复测试 |
| GitHub Actions | 如何自动验证 |

如果这些内容只留在聊天记录里：

- 新会话很难恢复；
- 其他 Agent 很难复用；
- 团队成员无法 Review；
- Git 无法追踪变化；
- 无法独立测试；
- 无法形成培训材料。

所以：

> **聊天是工作现场，仓库才是长期资产库。**

**截图占位：ASSET-01 ai-share 仓库资产地图**

---

# 2. 先不要背资产类型，先理解“生命周期”

一次成功任务通常经历：

```text
临时上下文
    ↓
发现有效经验
    ↓
判断是否稳定
    ↓
选择合适载体
    ↓
版本化
    ↓
测试 / Review
    ↓
下次自动或按需复用
```

这里最关键的动作是：

> **判断“它到底是什么性质的经验”。**

例如：

“今天这个服务临时跑在 8765 端口”

可能只是：

> 临时上下文。

“这个仓库测试统一执行 pytest -q”

可能应该进入：

> Project Rules / AGENTS.md。

“每次发布都要执行 12 个步骤”

更适合：

> Skill / Script / CI。

“Qwen Thinking 开关在当前部署的实测行为”

更适合：

> Evidence / Test Result / Report。

---

# 3. 本培训建议使用一个“资产路由表”

> 下面是本培训用于教学的工程分类，不是行业强制标准。

| 信息 / 能力 | 优先载体 |
|---|---|
| 当前任务临时信息 | Conversation / Session Context |
| 项目长期规则 | AGENTS.md / Project Instructions |
| 一类任务的方法 | Skill / Workflow |
| 确定性重复操作 | Script / CLI |
| 结果正确性的检查 | Test / Eval |
| 每次提交都要执行的检查 | CI / Hook |
| 可重复输出结构 | Template |
| 大量可检索事实资料 | Knowledge Base / Docs / Index |
| 小而稳定的跨会话事实 | Memory（产品支持时） |
| 设计决策与事实依据 | Docs / ADR / Reference |
| 可复现实验 | Test Script + Data + Report |
| 一次修改的状态历史 | Git Commit / PR / Release |

一句话：

> **不同资产解决不同问题，不要用一个“万能记忆文件”装下所有东西。**

**图示占位：ASSET-02 资产路由决策图**

---

# 4. Prompt：最轻量的可复用资产，但不是最终形态

Prompt 当然可以复用。

例如：

- 代码 Review Prompt；
- 技术调研 Prompt；
- 测试报告 Prompt；
- 文档改写 Prompt。

但 Prompt 有一个天然限制：

> 它经常只描述“怎么说”，没有绑定项目文件、工具、测试、脚本和验收。

例如：

```text
请帮我测试这个 Web 项目，发现问题后修复。
```

这可以是 Prompt。

但如果真实流程要求：

```text
读取 AGENTS.md
→ 记录 SHA
→ 后端单测
→ 前端构建
→ 启动服务
→ Browser QA
→ Screenshot
→ 修复
→ 回归
→ Git Diff
→ CI
→ 验收报告
```

继续靠一大段 Prompt 手工粘贴就开始不合适。

所以：

> **Prompt 是经验沉淀的起点，不一定是终点。**

---

# 5. Project Rules / AGENTS.md：放“这个项目长期都成立”的约束

## 5.1 什么适合放进去

例如：

- 项目目标；
- 目录职责；
- 编码规范；
- 必须执行的测试；
- 事实来源优先级；
- 禁止事项；
- 提交要求；
- 特殊安全边界。

本仓库根目录 `AGENTS.md` 就是现成案例。

---

## 5.2 什么不应该塞进去

不适合：

- 一次任务的临时背景；
- 一次 Bug 的全部聊天记录；
- 几百行 API 返回；
- 每个文件的全文说明；
- 已经能从代码明显看出来的细节；
- 只对极少数任务相关的超长操作手册。

原因：

> Project Instructions 往往会频繁进入 Agent Context。

2026-09 OpenAI Codex 最新实践建议也专门提醒：

- 不要要求每次编辑前都阅读一整套无关文档；
- 应按任务指向相关文档；
- 应定期清理已经不再需要的 AGENTS.md 规则。

因此：

> **项目规则要长期有效、短而明确、能改变行为。**

**截图占位：ASSET-03 本仓库 AGENTS.md + 关键规则高亮**

---

# 6. AGENTS.md 不等于“项目百科全书”

一个常见错误：

> 把所有架构、API、测试、历史、FAQ 全部复制到 AGENTS.md。

更合理的结构：

```text
AGENTS.md
├─ 核心规则
├─ 什么时候读哪些文档
└─ 验证/交付要求

docs/
├─ architecture/
├─ references/
├─ operations/
└─ ...
```

例如：

```markdown
涉及数据库 Schema 变更时，先阅读 docs/architecture/database.md。
发布任务遵循 docs/release/release-process.md。
```

这就是：

> **规则文件负责路由，详细文档负责承载知识。**

---

# 7. Plan / ExecPlan：复杂任务的中间工作资产

不是所有 Plan 都值得长期保存。

但复杂任务中，Plan 有两个重要作用：

1. 把目标拆成可检查阶段；
2. 让长任务跨多轮仍有明确状态。

OpenAI Cookbook 也给出了 `PLANS.md` / ExecPlan 形式，用于多小时复杂任务。

适合：

- 大型重构；
- 数据迁移；
- 多阶段应用开发；
- 复杂验收。

不适合：

- 改一个拼写错误；
- 运行一次简单测试。

所以：

> **Plan 是任务状态资产，不要为了流程感给每个小任务都制造计划文档。**

---

# 8. Skill：把“做事方法”沉淀下来

上一章已经讲过 Skill。

在资产视角看，Skill 的价值是：

> **把一次成功工作流从聊天记录升级为可发现、可按需加载、可版本化的程序化操作手册。**

例如：

```text
project-acceptance/
├── SKILL.md
├── references/
├── scripts/
└── assets/
```

Skill 适合沉淀：

- 什么时候使用；
- 任务流程；
- Tool 顺序；
- 判断分支；
- 验证标准；
- 输出模板。

---

## 8.1 为什么 Skill 通常比“超长系统 Prompt”更好

当前 Agent Skills 的常见机制是：

> 先向模型暴露 Skill 的 name / description，需要时再读取完整 SKILL.md 和支持文件。

这意味着 Skill 可以做到：

> **按需加载，而不是所有规则永久占用 Context。**

这也解释了：

- 小而稳定的项目约束 → AGENTS.md；
- 较长的专项流程 → Skill。

Hermes 当前文档也用类似思路区分：

- Memory 保存小而持久的事实；
- Skill 保存更长的程序性方法，需要时加载。

**图示占位：ASSET-04 Always-on Rules vs On-demand Skill**

---

# 9. Script：当步骤已经确定，就不要每次让模型重新生成

例如：

- 批量重命名；
- CSV 格式转换；
- 版本号解析；
- JSON Schema 校验；
- API 批量测试；
- 图片批处理。

如果每次都让模型：

> “请重新写一段 Python 做这件事”

会产生：

- 输出不一致；
- 新 Bug；
- 重复 Token；
- 难以 Review；
- 难以自动测试。

更好的方式：

```text
第一次：
模型帮助设计脚本
→ 人验证
→ 加测试
→ Commit

以后：
Agent 直接调用脚本
```

所以：

> **成熟脚本是把模型的“临时生成能力”转成确定性工程能力。**

---

# 10. Test / Eval：把“我觉得有效”变成可验证资产

一个 Prompt、Skill、Script 或 Agent Workflow 是否真的好用，不能只靠感觉。

需要测试。

根据对象不同：

| 对象 | 可验证方式 |
|---|---|
| Script | Unit Test |
| API | Contract / Integration Test |
| UI | E2E / Visual QA |
| RAG | Retrieval / Answer Eval |
| Agent | Task success / Tool trace / regression set |
| Prompt | 固定案例集 / A-B 对比 |
| Skill | 固定任务 + 成功标准 |

本仓库 Qwen API 测试就是最典型案例：

> 从“手工调用成功”升级为可重复回归。

所以：

> **没有测试的资产，只是“保存下来的经验”；有测试才更接近工程资产。**

**截图占位：ASSET-05 Chat 经验 → Script → Test → CI 的成熟化路径**

---

# 11. CI：让验证脱离“某个 Agent 有没有记得”

如果测试只写在 AGENTS.md：

> “修改后请运行 pytest”

依赖 Agent 每次正确遵守。

如果进入 GitHub Actions：

```text
push
→ runner
→ test
→ pass/fail
```

就变成系统执行。

因此一个成熟过程经常是：

```text
Prompt
→ Rule
→ Skill
→ Script
→ Test
→ CI
```

注意：

> 这不是每个任务都必须经历的固定升级流水线，而是“经验越来越稳定时，可以逐步减少模型自由度”的工程方向。

---

# 12. Template：把输出结构也变成资产

Agent 经常重复生成：

- 测试报告；
- 验收报告；
- 调研报告；
- Release Note；
- Issue；
- PR；
- PPT 页面结构。

如果没有 Template，每次可能：

- 章节变化；
- 字段遗漏；
- 风格不一致。

Template 可以稳定：

- 必填字段；
- 顺序；
- 格式；
- 命名；
- Evidence 区域；
- Risk 区域。

所以：

> **Skill 定义怎么做，Template 定义怎么交付。**

---

# 13. Memory：解决“跨会话记住什么”，但不要承担项目事实库

Memory 最容易被误用。

需要至少区分三层：

```text
Session Context
Project Explicit Files
Persistent Memory
```

### Session Context

当前对话中的临时信息。

### Project Files

团队可读、可审计、可 Git 管理的项目事实与规则。

### Persistent Memory

产品提供的跨会话记忆机制。

---

## 13.1 Memory 适合保存什么

一般适合：

- 小而稳定的偏好；
- 稳定环境事实；
- 经常复用但不适合写进项目仓库的小事实；
- Agent 学到的长期使用习惯。

Hermes 当前把 `MEMORY.md` 定位为环境事实、约定、工具经验等小型持久笔记，并且设置明确字符上限，就是为了保持“有界、精选”。

---

## 13.2 什么不要只放在 Memory

关键项目规则：

> 不要只依赖隐式 Memory。

例如：

- 部署命令；
- 安全约束；
- 数据格式；
- 测试要求；
- 架构原则；
- 接口 Contract。

这些更适合：

> **写回项目文件并进入 Git。**

原因：

- 团队成员需要看到；
- Agent 可能更换；
- 产品 Memory 实现可能变化；
- 需要 Review；
- 需要版本历史。

一句话：

> **Memory 是个人/Agent 级辅助上下文，Project Files 才是团队项目的可审计事实源。**

**图示占位：ASSET-06 Session / Memory / Project Rules / Knowledge Base 四层边界**

---

# 14. Knowledge Base：它不是 Memory 的“大号版本”

知识库解决的是：

> **大量事实资料如何被检索并送入 Context。**

Memory 更偏：

> 小而稳定、经常需要的跨会话事实。

知识库更偏：

- 文档；
- 规范；
- 手册；
- 历史报告；
- 大规模资料；
- 可检索 Evidence。

因此：

```text
Memory：少量、精选、经常用
Knowledge Base：大量、按需检索
Project Rules：必须遵守
Skill：流程方法
```

知识库的 Parse / Chunk / Index / Retrieval / Evidence Budget 已经在：

- `03-department-knowledge-base-teaching.md`
- `03-department-knowledge-base.md`

详细讲过。

本章只讲“它在资产体系中的位置”，不重复 RAG 理论。

---

# 15. Documentation / ADR / Reference：把“为什么这样设计”留下来

代码只能告诉你：

> 现在是什么样。

很多时候不能告诉你：

> 为什么这样选。

例如：

- 为什么选 SQLite 而不是 PostgreSQL；
- 为什么当前接口保留三种兼容协议；
- 为什么 Knowledge Demo 要使用同源资料；
- 为什么某个测试阈值这样设。

这些适合进入：

- Architecture Document；
- ADR（Architecture Decision Record）；
- Reference / Evidence；
- Design Note。

这样 Agent 下一次修改时能知道：

> **这是故意这样设计，还是历史遗留？**

---

# 16. Evidence：事实与结论也应该成为资产

本项目一个很重要的实践是：

```text
docs/references/
api/qwen/results/
api/qwen/reports/
```

它们让我们可以区分：

- 官方宣称；
- 当前配置；
- 我们实测；
- 推测。

如果没有 Evidence，团队知识很容易变成：

> “我记得以前好像测过。”

因此：

> **实验结果、原始数据、测试环境和结论应该尽可能一起保存。**

推荐：

```text
Test Script
+ Raw Result
+ Environment
+ Summary
+ Report
```

---

# 17. Git：把所有显式资产串起来

只要资产是文件，就应该尽量考虑 Git 管理。

Git 提供：

- Version；
- Diff；
- Author；
- Review；
- Branch；
- History；
- Rollback；
- Release。

对于 Agent 资产尤其重要，因为：

> **Prompt、AGENTS.md、Skill、Template、Workflow 本身都会变化。**

它们也需要：

> 修改 → Diff → Review → Test → Commit。

---

# 18. Sub-agent：它是执行模式，不是“资产类型”

模块五不应该把所有 Agent 概念都硬塞进“资产”。

Sub-agent 更准确地说是：

> **任务组织与执行模式。**

适合：

- 并行研究；
- 模块化分析；
- 独立 Review；
- 上下文隔离。

可沉淀的是：

- Sub-agent 的 Role；
- Prompt；
- Tool 权限；
- 验收标准；
- Routing Rule。

也就是：

> **Sub-agent 本身不是资产，定义和编排它的方法可以成为资产。**

---

# 19. 不要走向另一个极端：资产越多越好

Agent 项目很容易出现新的“文档债务”：

```text
AGENTS.md 500 行
SKILL 100 个
Memory 一堆过期事实
docs/ 多份互相冲突
Prompt 模板没人知道哪个最新
脚本没有测试
CI 已经失效
```

这时候资产反而变成 Context Noise。

所以资产必须有：

- Owner；
- Source of Truth；
- Version；
- 适用范围；
- 更新条件；
- 淘汰机制。

本项目已经明确：

```text
实测/代码
> training-outline
> AGENTS.md
> chapter
> external source
> history
```

这就是一种：

> **资产治理。**

---

# 20. 资产应该“按需加载”，而不是全塞进 Context

这是 2026 年 Agent 工程越来越重要的方向。

可以把资产分成：

### Always-on

每次都重要：

- 少量身份/安全边界；
- 核心项目规则；
- 当前任务目标。

### Discoverable / On-demand

需要时加载：

- Skill；
- Architecture Doc；
- Reference；
- Knowledge Base；
- Detailed Runbook。

### Executable

直接运行：

- Script；
- Test；
- CI；
- Tool。

核心原则：

> **让 Agent 知道“有什么、什么时候去哪找”，往往比把所有内容提前塞给模型更好。**

OpenAI 2026-09 最新 Codex 指引也明确强调：

> 不必要的 AGENTS.md / Skill 内容会消耗 Context 并可能过度约束更强模型。

**图示占位：ASSET-07 Always-on / On-demand / Executable 三层资产**

---

# 21. 从一次成功任务到可复用资产：建议复盘五问

每次一个重要任务成功后，问：

1. **这次哪条规则以后都会成立？**  
   → Project Rule / AGENTS.md

2. **哪套方法以后会重复？**  
   → Skill / Workflow

3. **哪一步已经足够确定，不需要模型再判断？**  
   → Script / Test / CI

4. **哪些事实以后还会被查，但不该常驻 Context？**  
   → Docs / Knowledge Base / Reference

5. **哪些只是这次会话的临时信息？**  
   → 不沉淀，任务结束后消失

这五问比：

> “要不要把它存进 Memory？”

更完整。

---

# 22. 本培训最终希望部门积累什么

不是积累：

> “大家都装了某一个 Agent 软件。”

而是逐步形成：

```text
部门 AI 工程资产
├── 项目规则
├── Prompt / Task Templates
├── Skills
├── MCP / Tool Integrations
├── Scripts
├── Test / Eval Sets
├── CI Workflows
├── Architecture / ADR
├── Knowledge Bases
├── Demo / Example Repos
├── Report Templates
└── Evidence / Benchmarks
```

工具可以换：

```text
Codex
Claude Code
OpenCode
Hermes
WorkBuddy
...
```

但只要资产是开放、显式、可版本化的：

> **团队能力不会随着 UI 一起消失。**

---

# 23. 一个真实的“资产升级”案例：Qwen API 培训

这个仓库已经发生了完整升级：

### 最开始

```text
手工请求
```

### 然后

```text
Python Test Script
```

### 再然后

```text
Raw Results
+ Summary
+ Report
```

### 再然后

```text
CI Syntax Check
```

### 再然后

```text
Training Chapter
+ Screenshot Plan
+ Demo Chain
```

最终不再是一段聊天经验，而是：

> **可测试、可审阅、可培训、可继续迭代的一组工程资产。**

**截图占位：ASSET-08 Qwen API 资产升级时间线**

---

# 24. 课堂 Demo：同一个经验，放错位置与放对位置

建议做一个非常短的互动 Demo。

给学员四条信息：

```text
A. 这个仓库运行测试用 pytest -q
B. 今天临时服务端口是 8765
C. 发布流程一共 12 步
D. 有 300 份历史测试报告要按需查询
```

让大家选择：

- Conversation；
- AGENTS.md；
- Skill；
- Script / CI；
- Knowledge Base；
- Memory。

再讨论为什么。

目的：

> **让学员建立“资产路由”意识，而不是记文件名。**

对应：**ASSET-R01**

---

# 25. 课堂 Demo：把一段重复 Prompt 升级成 Skill

### 第一次

使用长 Prompt：

```text
请读取项目规则...
运行测试...
打开浏览器...
检查...
生成报告...
```

### 第二次

把它整理成：

```text
project-acceptance Skill
```

再运行。

比较：

- Prompt 长度；
- 步骤一致性；
- 输出格式；
- 是否自动调用 Script；
- 是否完成验证。

对应：**ASSET-R02**

---

# 26. 本章截图 / 录屏清单

## 26.1 静态

| 编号 | 优先级 | 内容 | 状态 |
|---|---:|---|---|
| ASSET-01 | P0 | ai-share 仓库资产地图 | ⬜ |
| ASSET-02 | P0 | 信息/经验 → 资产类型路由图 | ⬜ |
| ASSET-03 | P0 | 本仓库 AGENTS.md 关键规则 | ⬜ |
| ASSET-04 | P0 | Always-on Rules vs On-demand Skill | ⬜ |
| ASSET-05 | P0 | Prompt → Script → Test → CI 成熟化路径 | ⬜ |
| ASSET-06 | P0 | Session / Memory / Project Rules / Knowledge Base 边界 | ⬜ |
| ASSET-07 | P0 | Always-on / On-demand / Executable 三层资产 | ⬜ |
| ASSET-08 | P0 | Qwen API 资产升级时间线 | ⬜ |
| ASSET-09 | P1 | 项目 Source of Truth / 资产治理图 | ⬜ |

## 26.2 录屏

| 编号 | 优先级 | 内容 | 状态 |
|---|---:|---|---|
| ASSET-R01 | P0 | 四条信息应该沉淀到哪里：互动判断 | ⬜ |
| ASSET-R02 | P0 | 长 Prompt → Skill 的前后对比 | ⬜ |
| ASSET-R03 | P1 | 修改 AGENTS.md / Skill → Git Diff → Commit | ⬜ |
| ASSET-R04 | P1 | Script / Test / CI 三层确定性升级 | ⬜ |

---

# 27. 本章最后只留下八句话

1. **聊天记录不是团队资产，显式、可版本化、可验证的内容才更接近工程资产。**
2. **AGENTS.md 放长期项目规则，不要把它写成项目百科全书。**
3. **Skill 沉淀可重复的工作方法，并适合按需加载。**
4. **步骤一旦足够确定，就应该逐步下沉为 Script / Test / CI，而不是每次让模型重新生成。**
5. **Memory 适合少量跨会话事实，不应该成为关键项目事实的唯一存储。**
6. **Knowledge Base 管大量可检索事实，Project Rules 管必须遵守的约束，两者不是一回事。**
7. **资产也会过期，必须有 Source of Truth、版本、Review 和淘汰机制。**
8. **真正长期有价值的是工程资产，而不是今天使用哪一个 Agent UI。**

---

# 28. 参考资料与事实边界

## AGENTS.md

- AGENTS.md open format  
  https://agents.md/
- OpenAI Codex current model guidance / AGENTS.md behavior  
  https://developers.openai.com/api/docs/guides/latest-model
- OpenAI 2026-09: Rethinking skills and prompts for GPT-6 Astra  
  https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra

## Skills / Agents

- OpenAI Skills  
  https://developers.openai.com/api/docs/guides/tools-skills
- OpenAI Agents  
  https://developers.openai.com/api/docs/guides/agents
- OpenAI ExecPlan / PLANS.md  
  https://developers.openai.com/cookbook/articles/codex_exec_plans

## Hermes：用于说明产品实现差异

- Which File Does What  
  https://hermes-agent.nousresearch.com/docs/user-guide/which-file-does-what
- Persistent Memory  
  https://hermes-agent.nousresearch.com/docs/user-guide/features/memory/
- Skills System  
  https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/

## 本仓库

- `AGENTS.md`
- `docs/outline/training-outline.md`
- `docs/references/`
- `api/qwen/`
- `.github/workflows/api-test-script-check.yml`

## 事实边界

- 本章的“资产路由表”“Always-on / On-demand / Executable”是本培训的工程教学框架，不声明为行业标准。
- Memory 的具体载体、容量、写入机制由具体 Agent 产品决定；Hermes 仅作为一个当前实现案例。
- AGENTS.md 的具体发现/优先级行为要按使用的 Harness 当前实现确认；开放格式本身只规定 Markdown 约定。
- Skill 的加载、版本和执行环境也依产品实现而不同，本章强调的是“程序性方法按需复用”的稳定抽象。
