# ZCode：Agent 如何接入真实世界——贯穿案例设计

> 状态：案例设计完成，训练项目已建立，待 ZCode 实测与录屏  
> 日期：2026-09-30  
> 对应讲义：`docs/chapters/05-agent-tools-real-world.md`  
> 主 Agent：ZCode Agent  
> 原则：用具体 ZCode 界面讲清底层机制，但不把培训做成 ZCode 功能说明书。

---

# 1. 为什么先用 ZCode

模块三要回答：

> **模型只能生成 Token，为什么 Agent 能读项目、执行命令、改代码、开浏览器并验证结果？**

ZCode 适合作为第一套贯穿案例，因为当前官方产品把这些环节集中在一个 Workspace 中：

- Workspace / File Tree；
- Agent Task；
- Terminal；
- Built-in Browser；
- Git / Review；
- Execution Modes；
- AGENTS.md；
- Goal Mode。

因此可以在一个 Surface 中连续看到：

```text
Goal
→ Read
→ Edit
→ Run
→ Observe
→ Verify
→ Review
```

但培训必须强调：

> **ZCode 是案例载体，File / Shell / Git / Browser / Permission / Verification 才是要迁移的底层机制。**

官方参考：

- https://zcode.z.ai/en/docs/agents
- https://zcode.z.ai/en/docs/agent-framework
- https://zcode.z.ai/en/docs/ADE-tools
- https://zcode.z.ai/en/docs/browser-use
- https://zcode.z.ai/en/docs/safety-confirm
- https://zcode.z.ai/en/docs/goal

---

# 2. 两层案例，不用一个案例硬讲所有问题

## Case A：视觉闭环——鹈鹕骑自行车

复用：

`demos/pelican-bicycle/README.md`

它回答：

> **Agent 为什么和 Chat 不一样？**

流程：

```text
自然语言目标
→ 创建 index.html
→ Built-in Browser 打开
→ 观察真实结果
→ 发现视觉问题
→ 修改
→ 再验证
```

重点机制：

- File；
- Browser；
- Observe；
- Iterate；
- Verification。

---

## Case B：工程闭环——传感器状态边界 Bug

训练项目：

`demos/zcode-real-world/project/`

它回答：

> **Agent 如何进入一个已有工程，而不是只生成一段新代码？**

初始仓库故意包含一个边界条件错误：

- 温度达到 **85.0°C** 时，需求规定应为 `critical`；
- 当前实现使用 `temp_c > 85.0`；
- 因此 85.0°C 被错误分类成 `warning`；
- 测试集中已有一条失败测试暴露该问题。

预期 ZCode 自己完成：

```text
Read AGENTS.md
→ Inspect repository
→ Run tests
→ Observe one failure
→ Locate implementation
→ Make minimal fix
→ Run tests again
→ Review diff
→ Report evidence
```

重点机制：

- Project Instructions；
- Workspace；
- Search / Selective Read；
- Shell；
- Edit；
- Verification；
- Git / Review；
- Permission。

---

# 3. Case A：ZCode + 鹈鹕骑自行车

## 3.1 固定 Prompt

沿用已有 Prompt，不为 ZCode 特别优化：

> 创建一个单文件 HTML，用 SVG、CSS 和 JavaScript 生成一只鹈鹕骑自行车的循环动画。不得使用外部图片或第三方库。自行车轮子要转动，腿要踩踏板，鹈鹕身体有轻微起伏，画面比例协调、背景简洁，页面保存后可直接在浏览器打开。

---

## 3.2 现场先问问题，不先讲功能

### 问题一

> **如果只用 Chat，模型完成到哪里？**

```text
Chat
→ 输出 HTML 代码
→ 停止
```

### 问题二

> **如果用 ZCode Agent，它多了什么？**

现场观察：

1. Workspace 中真实出现 `index.html`；
2. Built-in Browser 真正打开页面；
3. Agent 能观察页面状态；
4. 发现问题后继续改文件；
5. 再次打开/刷新确认结果；
6. Review 最终变更。

---

## 3.3 ZCode 画面与底层机制映射

| ZCode 画面 | 底层机制 | 教学结论 |
|---|---|---|
| Workspace / File Tree | File System | Agent 接触的是实际项目，不只是 Prompt |
| 创建/修改 HTML | Write / Edit Tool | 模型请求动作，Harness 真正写文件 |
| Built-in Browser | Browser Tool | 生成结果进入真实运行环境 |
| Browser → 再修改 | Observe → Iterate | Agent 可以基于外部结果继续推理 |
| Review / Changed Files | State / Git | 结果可以检查和审计 |
| 最终确认 | Verification | “生成了”不等于“完成了” |

一句话收束：

> **Chat 给出候选答案；Agent 可以把候选答案放进真实环境执行、观察并继续迭代。**

---

# 4. Case B：工程闭环——为什么选“已有 Bug”而不是从零写项目

从零生成项目很容易让学员形成：

> Agent = 自动写代码。

真实工程更常见的是：

```text
已有代码
+ 已有规则
+ 已有测试
+ 已有历史
+ 一个具体问题
```

因此 Case B 故意设计成：

> **已有仓库 + 已有规则 + 已有失败测试 + 一个很小的 Bug。**

目标不是考模型算法能力，而是观察 Harness 是否形成完整工程闭环。

---

# 5. Case B 固定任务

建议原样输入，不提前告诉 Bug 在哪：

> 当前仓库有一个已知失败。请先读取项目规则和现有测试，复现问题，定位原因并用最小改动修复；运行必要测试确认结果，最后检查 Git Diff，并说明修改了什么、验证了什么、还有什么没有验证。不要跳过已有测试，也不要做无关重构。

为什么不告诉：

- 文件路径；
- 具体边界条件；
- 应改哪一行；
- 测试命令。

因为课堂需要观察：

> **Agent 是否主动读取 Context、定位、执行和验证。**

---

# 6. Case B：一个问题对应一个机制

## 问题 1：Agent 怎么知道这个项目应该怎样工作？

观察 ZCode 是否读取：

```text
AGENTS.md
README.md
```

机制：

> Project Instructions + Workspace Context

结论：

> **工程 Agent 不只依赖当前 Prompt，还需要显式项目规则。**

---

## 问题 2：Agent 怎么知道问题真的存在？

观察：

```text
Terminal
→ python -m unittest discover -s tests -v
→ 1 failure
```

机制：

> Shell / Tool Execution

结论：

> **工具把“模型猜测”变成“运行证据”。**

---

## 问题 3：Agent 怎么找到相关代码？

观察：

```text
Search / File Tree
→ tests/test_sensor_guard.py
→ src/sensor_guard.py
```

机制：

> Search → Selective Read

结论：

> **Agent 不应该把整个仓库一次性塞进上下文，而是边定位边读取。**

---

## 问题 4：Agent 改完怎么知道真的修好了？

观察：

```text
Edit
→ rerun unit tests
→ all pass
```

机制：

> Verification Loop

结论：

> **生成代码不是结束，验证成功才接近完成。**

---

## 问题 5：我们怎么知道 Agent 实际改了什么？

观察：

```text
Review
Git Diff
Changed Files
```

机制：

> State + Audit

结论：

> **不要只读 Agent 的自然语言总结，要检查仓库事实。**

---

## 问题 6：为什么不能总用 Full Access？

同一案例展示 ZCode 当前四种 Execution Modes：

- Ask before changes；
- Edit automatically；
- Plan mode；
- Full access。

先用 **Ask before changes** 或 **Plan mode** 展示一次确认，再解释：

> **Agent 能做什么，与我们允许它自动做什么，是两个不同问题。**

高风险生产配置、远程操作、删除和凭据相关任务不应为了演示“自动化”而直接 Full Access。

---

# 7. Case C：Browser Verification

课堂问题：

> **Unit Test 和 Build 都 PASS，是否说明前端任务已经完成？**

使用 Case A 或后续真实 Web 项目演示：

```text
Run Dev Server
→ Open Built-in Browser
→ Inspect Actual Page
→ Click / Fill / Scroll
→ Screenshot
→ Find UI Problem
→ Edit
→ Re-check
```

ZCode 当前官方 Browser Automation 支持打开 URL、点击、填写、滚动、截图，并根据页面状态继续行动。

因此重点不是：

> “ZCode 内置了一个浏览器。”

而是：

> **Browser 为 Agent 增加了运行态观察通道，使 UI 可以进入 Verify → Iterate 闭环。**

---

# 8. Case D：Goal Mode 放在长任务阶段，不要开场就讲

ZCode 当前支持 `/goal`，适用于一个目标需要多轮持续执行的任务。

建议在学员已经理解单轮 Tool Loop 后再问：

> **如果任务不是一轮 Tool Call 能做完，谁来判断“还要不要继续”？**

Goal Mode 的教学抽象：

```text
Goal
→ Round 1
→ Check completion
→ Not done
→ Round 2
→ ...
→ Done
```

演示任务可后续选择：

- 修复所有测试失败；
- 完成一个小模块重构并保持测试通过；
- 完成页面并持续 Browser QA。

这里要明确：

> **Goal Mode 是 ZCode 当前产品实现；底层要学的是 Long-Horizon Task State + Completion Check。**

---

# 9. ZCode 不承担模块三所有案例

模块三仍然有 SSH / Docker / CI 等内容。

建议分工：

### ZCode：主叙事

用于：

- Workspace；
- File；
- AGENTS.md；
- Search；
- Terminal；
- Git / Review；
- Browser；
- Permission；
- Goal / Long task。

### 后续真实项目：补真实世界深度

用于：

- SSH；
- Docker；
- GitHub Actions；
- 远程部署；
- API / metrics；
- 生产与测试环境边界。

这样可以避免为了“所有东西都必须 ZCode 演示”而构造不自然任务。

---

# 10. 现场素材编号

## Case A

- `ZCODE-01`：ZCode Workspace + 鹈鹕任务
- `ZCODE-02`：index.html 出现在 File Tree
- `ZCODE-03`：Built-in Browser 第一次结果
- `ZCODE-04`：Agent 根据 Browser 结果继续修改
- `ZCODE-05`：最终 Browser 验证 + Changed Files
- `ZCODE-R01`：完整“生成 → 打开 → 看 → 修 → 再看”

## Case B

- `ZCODE-06`：训练项目初始 Workspace
- `ZCODE-07`：读取 AGENTS.md
- `ZCODE-08`：Terminal 首次测试失败
- `ZCODE-09`：Search / Read 定位代码
- `ZCODE-10`：修改后测试通过
- `ZCODE-11`：Review / Git Diff
- `ZCODE-12`：Execution Modes
- `ZCODE-R02`：完整“规则 → 测试失败 → 定位 → 修复 → 测试 → Diff”

## Long Horizon

- `ZCODE-13`：Goal Mode / Summary
- `ZCODE-R03`：多轮 Goal Task（P1）

---

# 11. 现场录屏要求

必须尽量保留：

- Prompt；
- Tool Call / Agent Action；
- Terminal 原始输出；
- Browser 第一次错误状态；
- 修改过程；
- Test PASS；
- Diff；
- Execution Mode。

不要只录：

> 输入一句话 → 剪辑 → 最终成品。

否则看不出 Agent 工程闭环。

---

# 12. 最终教学映射

```text
问题：模型怎么碰到项目？
案例：ZCode Workspace
原理：File / Workspace

问题：怎么知道系统真实状态？
案例：ZCode Terminal
原理：Tool Execution / Observation

问题：怎么知道改对了？
案例：Unit Test + Browser
原理：Verification

问题：怎么知道改了什么？
案例：ZCode Review
原理：Git State / Audit

问题：为什么不能无限自动执行？
案例：Execution Modes
原理：Permission / Human-in-the-loop

问题：长任务为什么能持续？
案例：Goal Mode
原理：Task State / Completion Loop
```

最后再把 ZCode Logo 去掉，学员仍然应该记得：

> **Workspace + Tools + State + Permission + Verification。**

这才说明案例设计成功。
