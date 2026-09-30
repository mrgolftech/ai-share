# ZCode Agent 培训证据基线（2026-09）

> 用途：支撑模块三 ZCode 贯穿案例。  
> 核实日期：2026-09-30。  
> 原则：区分 ZCode 当前官方实现与可迁移的 Agent Harness 抽象。

---

## 1. ZCode 当前定位

官方资料：

- https://zcode.z.ai/en/docs/welcome
- https://zcode.z.ai/en/docs/agents
- https://zcode.z.ai/en/docs/agent-framework

当前官方将 ZCode 描述为 Agentic Development Environment（ADE）。

ZCode Agent 当前可以在同一 Workspace 中结合：

- files；
- terminal；
- browser；
- Git state / Review；
- execution modes；
- task context。

官方强调从 planning / implementation 到 verification 的连续工程工作流。

培训中据此使用 ZCode 作为：

> **“Agent 如何进入真实工程环境”的第一套可视化案例。**

不能据此推出：

> “ZCode 是综合能力最强的 Agent”。

---

## 2. AGENTS.md 当前行为

来源：

- https://zcode.z.ai/en/docs/agents

ZCode 当前读取两类项目指令来源：

1. 用户全局：`~/.zcode/AGENTS.md`
2. 当前 Workspace：`AGENTS.md`

当两者都存在时：

- 先追加用户全局规则；
- Workspace AGENTS.md 作为当前项目主要来源。

当前官方同时明确：

- 不会像某些 Harness 那样递归合并多层目录 AGENTS.md；
- 不扫描子目录选择不同规则；
- CLAUDE.md 主要用于 onboarding migration，而不是运行时持续读取来源。

这点在培训做跨 Agent 对照时非常重要：

> **“支持 AGENTS.md”不代表每个 Harness 的发现、合并和优先级完全相同。**

---

## 3. Project Memory

来源：

- https://zcode.z.ai/en/docs/agents

当前 ZCode 区分：

- 手工维护的 AGENTS.md；
- Agent 在成功任务后后台提炼的 Project Memory。

官方描述中 Project Memory 用于自动带回可复用项目事实，例如包管理器、测试命令等。

培训可据此说明：

> **显式 Project Rules 与 Agent 自动积累的 Memory 是两个不同机制。**

实际培训仍应强调：

> 关键工程规则应进入可审计项目文件，不应只依赖隐式 Memory。

---

## 4. Built-in Browser / Browser Automation

来源：

- https://zcode.z.ai/en/docs/browser-use
- https://zcode.z.ai/en/docs/agents

当前官方说明 ZCode Agent 可以直接驱动内置 Browser：

- open URL；
- click；
- fill form；
- scroll；
- screenshot；
- 根据页面实际状态决定下一步。

本地 Workspace 中 HTML 文件也可直接在 Built-in Browser 打开。

培训可据此设计：

```text
Create HTML
→ Open Browser
→ Observe
→ Edit
→ Verify again
```

即鹈鹕骑自行车案例。

---

## 5. Terminal / ADE Tools

来源：

- https://zcode.z.ai/en/docs/ADE-tools

官方当前说明 Terminal 可在同一 Workspace 中用于：

- build；
- test；
- development server；
- logs。

长命令可以转入 background execution。

培训可据此将 Terminal 映射为：

> **Agent 连接现有工程工具链的通用执行通道。**

---

## 6. Execution Modes / Safety Confirmation

来源：

- https://zcode.z.ai/en/docs/agents
- https://zcode.z.ai/en/docs/safety-confirm

当前 ZCode Agent 有四种执行模式：

- Ask before changes；
- Edit automatically；
- Plan mode；
- Full access。

官方将模式选择与任务风险、复杂度和人工参与程度绑定。

培训结论：

> **“Agent 拥有某个 Tool”与“当前任务允许它自动执行到什么程度”是两个问题。**

Sensor Guard 主案例建议首次录制使用：

- Ask before changes；或
- Plan mode → 确认方案后进入执行。

然后展示 Full access 作为权限差异，而不是一开始就全自动。

---

## 7. Goal Mode

来源：

- https://zcode.z.ai/en/docs/goal

当前 ZCode 使用 `/goal` 设置长任务目标。

官方描述的行为：

- 每轮结束后检查目标是否完成；
- 未完成则自动进入下一轮；
- 完成后才收束。

官方示例包括：

- 重构整个模块并保持测试通过；
- 修复全部 TypeScript compile errors；
- 将 Lighthouse performance 提升到目标值。

培训中应抽象为：

> **Long-Horizon Task = Goal + State + Iteration + Completion Check。**

不要把 `/goal` 本身讲成通用 Agent 标准。

---

## 8. Commands

来源：

- https://zcode.z.ai/en/docs/commands

当前 ZCode 支持通过 `/` 调用：

- built-in commands；
- 保存的可复用 prompts；
- Skills 分组。

官方当前内置包括：

- `/goal`
- `/compact`

这一事实可以在模块四 Command / Skill 中作为具体产品案例。

---

## 9. Subagents

来源：

- https://zcode.z.ai/en/docs/subagents

当前官方文档说明 ZCode 支持 Subagents，并区分 foreground / background execution。

自 v3.7.1 起，多数 Subagent 默认注入用户级和 Workspace AGENTS.md；内置 Explore 有特殊行为和只读边界。

培训当前不把 Subagent 放进模块三主案例，避免一次引入过多机制。

后续模块五/复杂任务再引用。

---

## 10. 为什么 Sensor Guard 案例适合当前培训

训练项目：

`demos/zcode-real-world/project/`

它刻意只保留：

- 1 个项目规则文件；
- 1 个实现文件；
- 1 个测试文件；
- 1 个明确边界 Bug。

本地等价环境已验证初始状态：

```text
Ran 5 tests
FAILED (failures=1)
```

失败项：

`test_critical_boundary`

其教学意义不是考算法能力，而是能够稳定观察：

```text
Rules
→ Read
→ Test
→ Observe
→ Locate
→ Edit
→ Re-test
→ Diff
```

---

## 11. 当前待形成的 ZCode 实测证据

仍需用户在实际 ZCode 环境中补：

1. ZCODE-01～05：鹈鹕 Browser 闭环；
2. ZCODE-06～12：Sensor Guard 工程闭环；
3. ZCODE-13：Goal Mode；
4. ZCODE-R01～03：完整录屏；
5. ZCode 版本；
6. 使用模型；
7. Execution Mode；
8. 是否启用 Browser Control；
9. Tool Trace / Terminal Output；
10. 最终 Diff。

完成后本文件应新增“我们的实测”章节，并把官方能力与实测结果分开记录。
