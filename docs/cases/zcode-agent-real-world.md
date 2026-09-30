# 案例：用 ZCode 看懂 Agent 如何接入真实工程环境

> 状态：案例设计完成 / 训练项目已建立 / 待 ZCode 实测与截图  
> 日期：2026-09-30  
> 关联 Demo：`demos/zcode-real-world/`

## 1. 案例要回答的问题

本案例不用于证明“ZCode 是最好的 Agent”。

它只回答一个培训主问题：

> **模型本身只能生成 Token，一个 Agent 为什么能够进入真实项目并连续完成读取、执行、修改和验证？**

选择 ZCode 是为了让学员在同一个 Workspace 中直观看到：

```text
Project Instructions
+ Files
+ Terminal
+ Browser
+ Git / Review
+ Permission
+ Task State
```

然后把这些 UI 现象映射回通用 Agent Harness 机制。

## 2. 为什么需要两个子案例

### 子案例 A：鹈鹕骑自行车

优点：

- 结果肉眼可见；
- Browser Verification 非常直观；
- 适合在 2～3 分钟内建立“Chat vs Agent”的第一印象。

它回答：

> **Agent 为什么比一次 Chat 多了 Execute → Observe → Iterate？**

### 子案例 B：Sensor Guard 边界 Bug

优点：

- 已有仓库；
- 已有 AGENTS.md；
- 已有测试；
- 初始状态固定失败；
- 修复只有一个很小的边界修改；
- 可以清楚展示 Test / Diff / Review。

它回答：

> **Agent 如何像工程人员一样进入一个已有项目，而不是只从零生成代码？**

## 3. Sensor Guard 初始事实

需求：

- `temp_c < 75.0` → `normal`
- `75.0 <= temp_c < 85.0` → `warning`
- `temp_c >= 85.0` → `critical`

训练代码故意使用：

```python
if temp_c > 85.0:
    return "critical"
```

因此 85.0°C 被错误判断为 `warning`。

本地等价环境已检查该训练代码：

```text
Ran 5 tests
FAILED (failures=1)
test_critical_boundary: warning != critical
```

该结果只表示训练项目初始代码逻辑已校验，不代表已经完成 ZCode 实测。

## 4. 固定 ZCode Prompt

> 当前仓库有一个已知失败。请先读取项目规则和现有测试，复现问题，定位原因并用最小改动修复；运行必要测试确认结果，最后检查 Git Diff，并说明修改了什么、验证了什么、还有什么没有验证。不要跳过已有测试，也不要做无关重构。

## 5. 需要观察什么

不以“最终改对了”作为唯一标准。

记录：

1. 是否主动读取 `AGENTS.md`；
2. 是否先运行测试复现；
3. 是否读取测试理解需求；
4. 是否只读相关代码而非盲目展开整个项目；
5. 是否做最小修改；
6. 是否重跑完整测试；
7. 是否检查 Diff；
8. 是否准确汇报未验证项；
9. 使用什么 Execution Mode；
10. Tool / Terminal / Review 的过程是否可追踪。

## 6. 课堂问题链

### 问题一

> Agent 怎么知道项目规则？

证据：

`AGENTS.md`

机制：

Project Instructions。

### 问题二

> Agent 怎么知道 Bug 真的存在？

证据：

Terminal 中失败测试。

机制：

Tool Execution + Observation。

### 问题三

> Agent 怎么知道读哪几个文件？

证据：

Search / File Read。

机制：

Selective Context Acquisition。

### 问题四

> Agent 怎么知道修改真的有效？

证据：

测试从 Fail → Pass。

机制：

Verification Loop。

### 问题五

> 人怎么知道 Agent 没偷偷改别的？

证据：

Git Diff / Review。

机制：

State + Audit。

### 问题六

> Agent 能执行是不是就应该全部自动执行？

证据：

Execution Modes / Confirmation。

机制：

Permission + Human-in-the-loop。

## 7. 人在案例中的职责

人不是只负责“点击开始”。

人负责：

- 定义需求边界；
- 确认 85°C 的业务要求；
- 决定执行权限；
- 判断是否接受修复；
- 检查最终 Diff；
- 接受或拒绝交付。

Agent 负责：

- 读取；
- 复现；
- 搜索；
- 修改；
- 执行测试；
- 整理证据。

## 8. 最终教学结论

不要收束成：

> “ZCode 很强。”

而应该收束成：

> **ZCode 把 Workspace、File、Terminal、Browser、Git、Permission 和 Task State 组织在一个 Harness 中；这些机制使模型输出能够进入真实工程环境，并形成可观察、可验证的执行闭环。**

## 9. 与其他 Agent 的后续对照

完成 ZCode 主案例后，再用其他产品做单点对照：

- Codex：Sandbox / Approval / AGENTS.md；
- WorkBuddy：Chat Surface 背后的 Workspace / Runtime；
- Hermes：Memory / Skill / Long-running Agent；
- OpenCode：Provider-neutral 与内网模型接入。

对照目标是说明：

> **产品 UI 不同，但很多底层问题相同。**

不再对每个产品重复跑一遍完整模块三。
