# ZCode 模块三现场演示 Runbook

> 目标：让现场 Demo 服务于“Agent 如何接入真实世界”的教学问题，而不是展示 ZCode 功能菜单。

---

# 1. 演示前准备

记录：

- 日期；
- ZCode 版本；
- 模型；
- Thinking / Effort；
- Execution Mode；
- Browser Control 是否启用；
- 操作系统；
- Workspace 路径。

准备两套 Workspace：

1. 鹈鹕 Demo 空目录；
2. Sensor Guard 训练项目的独立副本。

不要直接在培训仓库 main 的故意错误源文件上做现场修改。

建议复制：

```text
demos/zcode-real-world/project/
→ 临时工作目录
```

并在临时目录初始化 Git，以便演示 Review / Diff。

---

# 2. 开场：先问，不先解释

投影只显示一句：

> **模型只能生成 Token，为什么 ZCode 能改文件、跑测试、开浏览器？**

让学员先回答。

然后说：

> 我们不从功能列表解释，直接看两次任务执行。

---

# 3. Demo 1：鹈鹕 Browser 闭环

## 固定 Prompt

> 创建一个单文件 HTML，用 SVG、CSS 和 JavaScript 生成一只鹈鹕骑自行车的循环动画。不得使用外部图片或第三方库。自行车轮子要转动，腿要踩踏板，鹈鹕身体有轻微起伏，画面比例协调、背景简洁，页面保存后可直接在浏览器打开。

## 讲师不要做

- 不告诉它文件名应该是什么；
- 不自己手工修 HTML；
- 不跳过第一次效果；
- 不只截最终页面。

## 重点停顿画面

### 停顿 1：文件出现

问：

> **这一步和 Chat 最大的区别是什么？**

结论：

真实 Workspace / File System。

### 停顿 2：Browser 第一次打开

问：

> **现在模型看到的是代码，还是代码运行后的结果？**

结论：

External Observation。

### 停顿 3：发现视觉问题后继续改

问：

> **为什么它还能继续工作？**

结论：

Tool Result / Browser State 回到 Agent Context，进入下一轮推理。

### 停顿 4：最终 Review

结论：

> **Agent 不是“写完了”，而是“执行—观察—迭代—验证”。**

建议控制在 3～5 分钟。

---

# 4. Demo 2：Sensor Guard 工程闭环

## 固定 Prompt

> 当前仓库有一个已知失败。请先读取项目规则和现有测试，复现问题，定位原因并用最小改动修复；运行必要测试确认结果，最后检查 Git Diff，并说明修改了什么、验证了什么、还有什么没有验证。不要跳过已有测试，也不要做无关重构。

## 初始状态

训练项目应保持：

```python
if temp_c > 85.0:
    return "critical"
```

预期：

```text
5 tests
1 failure
```

失败：

`test_critical_boundary`

## 推荐 Execution Mode

第一次录制优先：

- Ask before changes；或
- Plan mode。

目的不是追求最快，而是让学员看到：

> Permission / Human-in-the-loop。

---

# 5. Demo 2 的六次停顿

## 停顿 1：AGENTS.md

如果 Agent 主动读取，停下来。

问：

> **为什么用户 Prompt 没告诉测试命令，它还是能知道？**

结论：

Project Instructions。

如果 Agent 没读：

- 不替它圆；
- 记录为真实结果；
- 后续分析 Harness 行为。

---

## 停顿 2：首次 Test Fail

Terminal 出现失败时停。

问：

> **在运行测试前，“Bug 存在”是谁说的？运行以后呢？**

结论：

从 User Claim 变成 Runtime Evidence。

---

## 停顿 3：定位文件

观察它读：

- tests；
- implementation。

问：

> **为什么不需要把整个仓库全塞给模型？**

结论：

Search + Selective Context Acquisition。

---

## 停顿 4：修改

看修改范围。

问：

> **模型生成了一段代码，任务完成了吗？**

答案：

没有。

---

## 停顿 5：Test Pass

问：

> **现在能证明什么？不能证明什么？**

能证明：

- 当前测试集覆盖的行为通过。

不能无限外推：

- 所有业务都正确；
- 所有未覆盖场景都正确。

---

## 停顿 6：Review / Diff

问：

> **最终验收时更应该相信 Agent 的总结，还是 Diff + Test？**

结论：

Evidence > Narrative。

建议控制在 5～8 分钟。

---

# 6. Execution Modes 补充演示

不用重跑任务。

打开模式菜单，说明：

```text
Ask before changes
Edit automatically
Plan mode
Full access
```

只问：

> **同一个 Agent，为什么要有四种执行方式？**

答案：

> 风险、任务复杂度和人工参与程度不同。

不要把 Full Access 描述为“高级模式”。

---

# 7. Goal Mode 补充演示

放在最后，P1。

先问：

> **如果不是一次修改，而是连续十几轮才能完成的目标，谁来决定什么时候停止？**

再展示 `/goal`。

核心不是按钮，而是：

```text
Goal
+ Persistent Task State
+ Iterate
+ Completion Check
```

---

# 8. 现场失败怎么办

## Browser 没有自动打开

不要掩盖。

说明：

> 这是 Harness 当前一次行为；我们可以手动打开页面，但这一步应记录为“Agent 未主动完成 Browser Verify”。

## Agent 没读取 AGENTS.md

记录事实。

课后检查：

- Workspace 是否正确；
- 文件位置；
- 当前版本；
- Agent 行为。

不要为了演示效果临时说“它其实读了”。

## Agent 一次就直接猜中 Bug

仍然要求：

- 跑测试；
- 修改；
- 重跑测试；
- Review Diff。

因为培训重点是闭环，不是 Debug 难度。

## 网络/模型现场不稳定

使用预录 ZCODE-R01 / ZCODE-R02。

PPT 必须保留关键静态证据。

---

# 9. 录屏完成后的落盘

每次正式录制建立：

```text
demos/zcode-real-world/results/
  YYYYMMDD-HHMM/
    environment.md
    prompt.md
    agent-notes.md
    initial-test.txt
    final-test.txt
    final-diff.patch
    verification.md
    screenshots/
```

原始视频可放 assets/recordings/agent/，结果文本和关键证据进入仓库。

---

# 10. 讲师最后只说三句话

> **第一，模型本身没有直接改电脑，是 Harness 把模型连接到了工具。**

> **第二，Agent 的价值不是 Tool Call 数量，而是能否形成执行—观察—验证—迭代闭环。**

> **第三，ZCode 只是今天用来观察这个闭环的一个具体载体，换成 Codex、OpenCode 或其他 Agent，仍然应该寻找 Workspace、Tools、State、Permission 和 Verification。**
