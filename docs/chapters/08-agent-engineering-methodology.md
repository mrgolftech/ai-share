# 方法论收束：从会用 Agent 到工程化使用——任务路由、执行闭环与资产沉淀

> 状态：可用于培训 / 案例与截图后补  
> 更新日期：2026-09-30  
> 前置章节：`01-intranet-qwen-api.md` ～ `07-reusable-agent-assets.md`  
> 对应培训主线：**模型怎么调用 → 为什么 Chat 不够 → Agent 如何操作真实世界 → 如何让 Agent 掌握工具 → 如何形成可复用资产 → 用工程方法把它们串起来**

---

## 0. 这一章不是再增加新概念

前面已经讲了很多东西：

- API、Token、Context、Thinking；
- Chat、Knowledge、RAG；
- Agent Harness、Workspace、Memory、Plan；
- File、Shell、Git、Browser、SSH；
- Tool、MCP、Skill、Plugin、Command、Hook；
- AGENTS.md、Script、Test、CI、Knowledge Base、Evidence。

如果培训到这里就结束，学员仍然可能遇到一个最现实的问题：

> **明天回到自己的工作岗位，拿到一个真实任务，到底应该从哪里开始？**

所以这一章不再引入一套新的术语。

它只做一件事：

> **把前面的知识收束成一套可以重复使用的工程方法。**

---

# 1. 第一步不是选模型，而是判断任务属于哪一类

很多低效使用方式都从一句话开始：

> “这个任务我应该用哪个模型？”

更好的第一个问题是：

> **这个任务到底需要“回答”、需要“查资料”，还是需要“真正执行”？**

本培训建议先做四类判断。

| 任务类型 | 典型特征 | 优先工作方式 |
|---|---|---|
| 问答型 | 问题清楚，不需要改外部状态 | Chat |
| 知识型 | 依赖文档、规范、历史资料 | Chat + Search / Knowledge / RAG |
| 执行型 | 要读写文件、跑命令、操作 Git、浏览器或服务器 | Agent |
| 工程型 | 多步骤、长周期、要测试、Review、交付 | Agent + Workspace + Rules + Tools + Verification |

这里最重要的不是给工具贴标签。

而是避免两个极端：

- 所有问题都扔给 Agent；
- 所有工程任务都停留在 Chat 里复制粘贴。

核心原则：

> **工作方式由任务决定，不由“哪个工具最近最火”决定。**

**图示占位：METHOD-01｜四类任务 → Chat / Knowledge / Agent 路由图**

---

# 2. Chat 什么时候其实已经够了

如果任务是：

- 解释一个概念；
- 改写一段文字；
- 分析一个已经完整贴进上下文的问题；
- 给出几个方案；
- 写一段独立代码；
- 快速讨论思路；

那么：

> **Chat 往往是成本最低、最快的方式。**

这也意味着：

> 不要为了“Agent 化”而 Agent 化。

Agent 的优势来自：

- 能读取工作区；
- 能操作工具；
- 能持续执行；
- 能观察结果；
- 能再次修改；
- 能验证；
- 能交付。

如果任务本身不需要这些能力，Agent 反而可能增加：

- Token；
- 延迟；
- 工具调用；
- 环境复杂度；
- 权限风险。

---

# 3. 什么时候应该从 Chat 升级到 Agent

一个任务出现下面任意几种信号时，就应该考虑切到 Agent：

- 需要读取多个项目文件；
- 需要修改代码或文档；
- 需要运行 Shell；
- 需要浏览器验收；
- 需要 Git Diff；
- 需要 SSH / Docker；
- 需要多轮“修改 → 运行 → 观察 → 再修改”；
- 需要维护任务状态；
- 需要跨较长时间保持项目上下文；
- 最终结果必须可验证，而不是只生成一段答案。

因此：

```text
Prompt → Answer
```

开始升级为：

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

这就是本培训所说的：

> **从 Chat 工作方式走向 Agent 工作方式。**

---

# 4. 第二步：先定义问题，再让 AI 工作

复杂工程任务最常见的错误不是“Prompt 不够好”。

而是：

> **问题本身没有定义清楚。**

培训中建议统一使用：

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
→ Release
```

中文：

```text
问题
→ 需求
→ 约束
→ 调研
→ 架构
→ 计划
→ 开发
→ 测试
→ 浏览器/视觉验收
→ Review
→ 发布
```

这条链的意义是：

> **不要从 Prompt 直接跳到 Code。**

**图示占位：METHOD-02｜Prompt→Code 错误路径 vs 工程闭环**

---

# 5. Problem：先说清楚“为什么做”

一个任务如果只写：

> “帮我做一个系统。”

模型只能自己补大量假设。

更好的 Problem 至少回答：

- 当前痛点是什么；
- 谁在使用；
- 原来怎么做；
- 哪一步最耗时间；
- 哪一步最容易错；
- 为什么现在值得解决。

问题定义越清楚，后面的方案空间越稳定。

---

# 6. Requirement：把“想要”变成“要做到什么”

Requirement 不只是功能列表。

至少应该包含：

- 输入；
- 输出；
- 核心流程；
- 用户操作；
- 异常情况；
- 数据来源；
- 成功标准。

例如不要只写：

> “做一个 API 测试工具。”

而应该明确：

- 测哪些 Endpoint；
- 是否支持 SSE；
- 是否测试 Tool Calling；
- 结果保存在哪里；
- 怎样判断 PASS；
- 是否自动脱敏；
- 是否生成报告。

这时 Agent 才能围绕目标工作，而不是围绕猜测工作。

---

# 7. Constraint：约束往往比 Prompt 更重要

真实项目不会在无限资源里运行。

常见约束包括：

- 内网；
- Windows / Linux；
- 指定 Python / Node 版本；
- 不能访问公网；
- 不能上传数据；
- 只能使用某个模型；
- CPU / GPU / NPU 资源；
- 权限；
- 依赖安装方式；
- 输出文件格式；
- 时间；
- 安全要求。

因此：

> **高质量 Agent 任务不是只有目标，还应该有边界。**

对于企业工程任务尤其如此。

---

# 8. Research：新问题不要直接让模型凭记忆写

只要涉及：

- 新框架；
- 新 API；
- 当前版本；
- 第三方 Agent；
- MCP；
- Skill；
- 模型能力；
- 浏览器工具；
- 开源项目；

都应该优先：

```text
当前仓库 / 当前代码
→ 官方文档
→ 官方 GitHub / Release Notes
→ 高质量资料
→ 再形成方案
```

不能把：

> 模型训练时见过的知识

当成：

> 当前工程事实。

这也是为什么本培训一直强调：

> **官方宣称 / 当前部署 / 我们实测 / 社区观点 / 推测，要分开。**

---

# 9. Architecture：让 Agent 先理解系统，而不是先生成文件

当任务跨多个模块时，先确认：

- 系统边界；
- 模块；
- 数据流；
- 接口；
- 状态；
- Runtime；
- 权限；
- 验证点。

这一步的价值不只是“画架构图”。

而是提前发现：

- 需求冲突；
- 责任边界不清；
- 接口重复；
- 工具选型错误；
- 无法测试的设计。

对于复杂 Agent 应用，还需要额外确认：

```text
Model
+ Harness
+ Workspace
+ Tools
+ Runtime
+ Permission
+ Verification
```

分别由谁提供。

---

# 10. Plan：计划不是为了好看，而是降低长任务失控概率

简单任务不需要复杂 Plan。

但复杂任务如果包含：

- 多文件修改；
- 多模块；
- 多阶段；
- 环境配置；
- 数据迁移；
- UI；
- 测试；
- 发布；

就需要显式计划。

好的 Plan 至少包含：

- 当前状态；
- 目标；
- 步骤；
- 依赖；
- 风险；
- 验收标准。

并且允许执行过程中更新。

因此：

> **Plan 是工作状态，不是一次性作文。**

---

# 11. 第三步：为 Agent 准备 Runtime，而不是只准备 Prompt

模型本身只能生成 Token。

它能否真正完成任务，很大程度取决于 Harness 和 Runtime。

需要检查：

- Workspace 是否正确；
- Git 是否可用；
- Python / Node / npm 是否可用；
- 浏览器是否可用；
- Playwright / CDP 是否可用；
- Docker 是否可用；
- SSH 是否可用；
- 网络是否允许；
- API Key 是否存在；
- 权限是否足够；
- 测试命令是否能跑。

因此，本培训把：

> **Agent Runtime / Environment Engineering**

视为 Agent 工程的一部分。

**图示占位：METHOD-03｜Model / Harness / Runtime 三层图**

---

# 12. 第四步：让项目规则进入工作区，而不是每次重新说

稳定规则不应该每次都靠 Prompt 重复。

应该进入：

- AGENTS.md；
- CLAUDE.md；
- README；
- Architecture Docs；
- ADR；
- Test Guide；
- Skill；
- CI。

例如：

- 怎么安装依赖；
- 怎么运行测试；
- 哪些目录不能改；
- 哪些接口不能破坏；
- Commit 前必须做什么；
- 什么叫完成。

这样 Agent 每次进入项目时，都能重新读取事实。

核心原则：

> **聊天负责当前任务，仓库负责长期事实。**

---

# 13. 第五步：给 Agent 合适的工具，而不是工具越多越好

Tool Surface 应该围绕任务设计。

一个 Agent 不需要“世界上所有工具”。

它需要的是：

> **完成当前任务所需的最小能力集合。**

例如代码验收任务可能需要：

- File/Search；
- Shell；
- Git；
- Browser；
- CI。

而不是再加十几个完全无关的 MCP Server。

工具过多会带来：

- 选择成本；
- Tool Routing 干扰；
- 更大的 Context；
- 更多权限；
- 更复杂的失败模式。

所以：

> **Tool Access 也应该最小化。**

---

# 14. 第六步：执行时采用 Observe → Verify，而不是“生成完就算完成”

Agent 工程和普通内容生成最大的区别之一是：

> **结果可以被真实环境反馈。**

例如：

写代码  
→ 运行测试；

改页面  
→ 打开浏览器；

改 API  
→ 发请求；

改 Docker  
→ 启动容器；

改 GitHub Workflow  
→ 看 CI；

改配置  
→ 读取实际状态。

统一循环：

```text
Act
→ Observe
→ Compare with expectation
→ Fix
→ Verify again
```

因此：

> **工具让 Agent 能行动，验证工具让 Agent 知道自己是否做对。**

**图示占位：METHOD-04｜Act → Observe → Verify → Iterate 闭环**

---

# 15. Test：自动化测试负责“确定性验证”

自动化测试特别适合验证：

- 计算；
- 数据转换；
- API 返回；
- Schema；
- 边界条件；
- Regression。

这里继续使用本培训统一分工：

> **模型负责判断和生成，工具负责执行，自动化测试负责验证，人负责目标、约束和最终判断。**

模型不应该替代测试。

它应该：

- 写测试；
- 运行测试；
- 解释失败；
- 修复；
- 再运行。

---

# 16. Visual QA：能运行不等于用户看到的是对的

Web / GUI 项目常见问题：

- Build PASS；
- Unit Test PASS；
- 页面却错位；
- 按钮不可见；
- 中文字体错误；
- 移动端溢出；
- 图表显示异常。

因此：

> **视觉产品必须进入浏览器或真实界面验收。**

这也是 Playwright、Browser Use、Computer Use 在工程任务中的真正意义之一：

> 不只是“帮你点网页”，而是把真实界面重新纳入验证闭环。

---

# 17. Review：Agent 自己改的代码也要重新读

完成实现后至少需要：

- Git Diff；
- 关键文件复读；
- 错误处理；
- 是否改坏无关功能；
- 是否引入临时代码；
- 是否漏更新文档；
- 是否误删测试；
- 是否暴露凭据。

不能只因为：

> “测试绿了”

就直接交付。

Review 负责回答：

> **改动是不是合理，而不只是能不能跑。**

---

# 18. Release：真正完成意味着交付状态明确

工程任务的结束不应该是：

> “代码已经写好了。”

而应该是明确：

- 文件改了什么；
- 测试结果；
- Branch / Commit；
- 是否 Push；
- CI 状态；
- 版本；
- 已知限制；
- 后续事项。

也就是说：

> **Deliver 是 Agent Loop 的最后一步。**

---

# 19. 第七步：模型不是越强越好，要做任务路由

本培训不采用：

> 所有任务都给旗舰模型。

也不采用：

> 内网模型只能做简单任务。

更合理的是按任务复杂度路由。

## 日常任务

例如：

- 文档整理；
- 普通脚本；
- 数据提取；
- 常规 API；
- 格式转换；
- 简单代码修改；

优先考虑：

> 内网模型 / 成本更低的模型。

## 高难任务

例如：

- 系统架构；
- 疑难 Bug；
- 多文件复杂理解；
- 新技术预研；
- 高质量 Review；
- 模糊异常分析；

可以升级：

> 更强模型 / 更高 Thinking Budget。

所以：

> **模型本身也是工程资源。**

**图示占位：METHOD-05｜任务难度 × 模型能力 × 成本路由**

---

# 20. Thinking 也应该按任务分配

Thinking 的本质不是：

> “打开以后答案一定更好。”

而是：

> **给模型更多推理预算。**

因此可以建立简单习惯：

```text
简单任务
→ 快速 / Non-Thinking

中等任务
→ 普通推理

复杂分析 / 架构 / 疑难 Debug
→ 更高 Thinking Budget
```

这与 CPU、GPU、服务器资源一样：

> **算力应该分配到真正需要它的地方。**

---

# 21. 第八步：Context 也要预算

Agent 做长任务时，容易不断把：

- 文件；
- 日志；
- 搜索结果；
- Tool Result；
- 测试输出；
- 历史消息；

全部塞进 Context。

这会产生：

- Token 增长；
- Prefill 成本；
- 响应变慢；
- 噪声增加；
- 重要信息被淹没。

因此需要：

- Search；
- 精确读取；
- Summary；
- Memory；
- Project Files；
- Knowledge Retrieval；
- Context Compaction；
- Evidence Budget。

核心不是：

> “让模型看到最多。”

而是：

> **让模型在当前决策点看到最相关的证据。**

---

# 22. 第九步：Human in the Loop 要放在关键决策点，而不是每一步

如果每一个 Shell 命令都要人工确认：

> Agent 失去连续执行价值。

如果任何操作都完全自动：

> 风险又会失控。

更合理的是把人工判断放在高价值节点。

例如：

- 目标确认；
- 架构确认；
- 权限升级；
- 删除数据；
- Production 变更；
- 发布；
- 最终验收。

可以理解为：

```text
低风险重复动作
→ 自动执行

高影响决策
→ 人确认
```

因此：

> **Human in the Loop 不是“人盯着 Agent 每一步”，而是把人放在真正需要判断的节点。**

---

# 23. 第十步：任务完成后一定要问“什么值得留下”

如果一个任务完成后：

- Prompt 消失；
- 规则留在聊天里；
- 脚本没保存；
- 测试没提交；
- 经验没人记录；

那么下一次几乎又从零开始。

任务结束后至少复盘：

1. 哪条规则以后还成立？
2. 哪个步骤以后还会重复？
3. 哪个判断可以变成测试？
4. 哪段代码应该变成脚本？
5. 哪个经验应该进入 Skill / Knowledge / Project Rules？

最终可能沉淀为：

- Prompt；
- AGENTS.md；
- Skill；
- Script；
- Test；
- CI；
- Template；
- Knowledge；
- Evidence；
- Git History。

这才完成：

> **一次 AI 帮忙 → 可复用工程资产。**

---

# 24. 一张统一的 Agent 工程闭环

整场培训最终可以压成：

```text
1. Clarify Goal
      ↓
2. Define Requirement / Constraint
      ↓
3. Research Current Facts
      ↓
4. Choose Chat / Knowledge / Agent
      ↓
5. Choose Model / Thinking Budget
      ↓
6. Prepare Workspace / Rules / Runtime / Tools
      ↓
7. Plan
      ↓
8. Read → Act → Observe → Verify → Iterate
      ↓
9. Test / Visual QA / Review
      ↓
10. Human Decision at Critical Points
      ↓
11. Deliver
      ↓
12. Assetize What Worked
```

**图示占位：METHOD-06｜全培训最终闭环图**

这张图建议成为：

> **整场培训最后一张核心架构图。**

---

# 25. 如果只能记住一个判断框架

拿到任务以后，依次问：

```text
它只是一个问题吗？
→ Chat

它依赖资料吗？
→ Search / Knowledge / RAG

它需要操作真实环境吗？
→ Agent

它是复杂工程任务吗？
→ Workspace + Rules + Plan + Tools + Verification

这套方法以后会重复吗？
→ Skill / Script / Test / CI / Knowledge
```

**图示占位：METHOD-07｜五问决策卡**

---

# 26. Agent 工程最常见的九种失败模式

## 26.1 直接 Prompt → Code

问题：

- 需求不清；
- 架构靠猜；
- 返工大。

替代：

> Requirement / Constraint / Architecture 先行。

## 26.2 把 Chat 当 Agent

问题：

- 手工复制；
- 手工执行；
- 无闭环。

替代：

> 复杂执行任务进入 Workspace。

## 26.3 把 Agent 当“自动 Chat”

问题：

- 只让它生成；
- 不让它运行和验证。

替代：

> 给工具和验证闭环。

## 26.4 工具越多越好

问题：

- Tool Surface 膨胀；
- 权限增大；
- 选择困难。

替代：

> 最小必要工具集。

## 26.5 所有资料都塞进 Context

问题：

- 慢；
- 贵；
- 噪声大。

替代：

> Search / Retrieval / Evidence Budget。

## 26.6 所有规则都写成长 Prompt

问题：

- 每次重复；
- 难版本化；
- 难 Review。

替代：

> Rules / Skill / Script / Test。

## 26.7 Skill 代替安全边界

问题：

- Prompt 规则并不能真正限制权限。

替代：

> Permission / Sandbox / Approval / Server Authorization。

## 26.8 测试通过就直接发布

问题：

- UI、集成、行为逻辑仍可能错误。

替代：

> Test + Visual QA + Review。

## 26.9 每次任务完成后什么都不留下

问题：

- 团队永远停留在“一次性 AI 使用”。

替代：

> 任务结束后资产化。

---

# 27. 对部门内部最值得形成的不是“统一 Agent 软件”，而是统一工作方法

工具一定会变化。

可能今天使用：

- ZCode；
- Codex；
- OpenCode；
- Cline；
- Hermes；
- WorkBuddy。

未来可能又出现新的 Harness。

如果团队只统一：

> “大家都用某个按钮。”

这个经验很容易过期。

更值得统一的是：

- 项目规则格式；
- 任务启动方式；
- 需求模板；
- 验收标准；
- Skill；
- MCP；
- Script；
- Test；
- CI；
- Knowledge；
- Evidence；
- Release 流程。

所以部门级能力建设的方向应该是：

> **统一工程资产与协作方法，而不是绑定单一 Agent UI。**

---

# 28. 对企业内网模型的定位

内网模型真正有价值的前提，不只是：

> “部署了一套 Chat 页面。”

而是逐步接入：

- API；
- Agent Harness；
- Workspace；
- Tool；
- MCP；
- Knowledge；
- CI；
- 内部业务系统。

这样模型才可能从：

> **信息问答能力**

逐步进入：

> **工程执行能力。**

但始终需要：

- 权限；
- 审计；
- 安全边界；
- 数据边界；
- 验证。

因此最终目标不是：

> “让模型能做所有事。”

而是：

> **让模型在受控工具和工程规则中完成合适的事。**

---

# 29. 这套方法最终改变的是工作组织方式

传统软件工具通常是：

```text
人理解任务
→ 人找到软件
→ 人逐步操作
→ 人检查结果
```

Agent 工作方式逐渐变成：

```text
人定义 Goal / Constraint
→ Model 判断和规划
→ Tools 执行
→ Environment 返回证据
→ Tests 自动验证
→ Model 继续修正
→ Human 做关键判断
```

所以真正的变化不是：

> “AI 帮我写代码。”

而是：

> **一部分原来必须由人连续完成的数字化工作流，可以被重新组织为 Agent 执行闭环。**

---

# 30. 本章建议现场只讲三张图

如果培训时间有限，本章不要重新讲一遍所有内容。

只保留：

1. **METHOD-07：五问任务路由卡**
2. **METHOD-02：完整工程开发链**
3. **METHOD-06：Agent 工程闭环**

然后回扣整场培训。

---

# 31. 本章截图 / 图示清单

| 编号 | 优先级 | 内容 | 状态 |
|---|---:|---|---|
| METHOD-01 | P1 | 四类任务 → Chat / Knowledge / Agent 路由 | ⬜ |
| METHOD-02 | P0 | Prompt→Code vs 完整工程链 | ⬜ |
| METHOD-03 | P1 | Model / Harness / Runtime 三层 | ⬜ |
| METHOD-04 | P0 | Act → Observe → Verify → Iterate | ⬜ |
| METHOD-05 | P1 | 模型 / Thinking 分级路由 | ⬜ |
| METHOD-06 | P0 | 全培训最终 Agent 工程闭环 | ⬜ |
| METHOD-07 | P0 | 五问任务决策卡 | ⬜ |

本章原则：

> **不需要再增加大量现场录屏。**

它主要负责：

> **帮助学员把前面的内容“装进一个框架里”。**

---

# 32. 本章最后只留下七句话

1. **先判断任务，再选择 Chat、Knowledge 还是 Agent。**
2. **复杂工程任务不要从 Prompt 直接跳到 Code。**
3. **模型能力只是 Agent 能力的一部分，Harness、Runtime、Tools 和 Verification 同样重要。**
4. **Agent 的核心不是“会生成”，而是能够 Read → Act → Observe → Verify → Iterate。**
5. **模型、Thinking、Context 和 Tool 都是需要预算的工程资源。**
6. **人在目标、约束、高影响操作和最终验收节点保持判断权。**
7. **一次成功任务只有被沉淀为规则、Skill、脚本、测试、CI 或知识资产，才真正变成团队能力。**

---

# 33. 与前序章节的关系

本章不替代前面的章节，而是把它们重新串起来：

| 本章问题 | 回看章节 |
|---|---|
| 模型为什么有成本 | `01-intranet-qwen-api.md` |
| 为什么 Chat 不够 | `02-chat-to-agent-harness.md` |
| Knowledge / RAG 怎么用 | `02-chat-workbenches-and-rag.md`、`03-department-knowledge-base-teaching.md` |
| Agent 的共同机制 | `04-agent-common-mechanisms.md` |
| Agent 如何操作真实世界 | `05-agent-tools-real-world.md` |
| API / MCP / Skill 的关系 | `06-api-mcp-skill-plugin-command-hook.md` |
| 如何沉淀资产 | `07-reusable-agent-assets.md` |

因此，本章适合作为：

> **完整讲义的最后一章，以及 PPT 结尾的方法论收束。**

---

# 34. 事实边界

本章大部分内容属于：

> **基于前述实测、官方资料和本培训工程实践形成的方法论归纳。**

需要区分：

- “MCP 当前规范是什么”“某 Agent 当前支持什么能力”属于产品/协议事实，应回到对应证据文档；
- “应该怎样组织复杂 Agent 工程任务”属于本培训的方法论建议；
- 具体部门项目是否适合 Agent、采用什么权限模型，仍需结合实际系统、安全边界和业务风险判断。

最终原则仍然是：

> **模型负责判断和生成，工具负责执行，自动化测试负责验证，人负责目标、约束和最终判断。**
