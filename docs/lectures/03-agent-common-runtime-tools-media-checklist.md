# 第三讲素材清单：Agent 共性、Runtime 与工具

> 日期：2026-09-30  
> 对应讲义：`docs/lectures/03-agent-common-runtime-tools.md`  
> 状态：Working Checklist v1.0  
> 使用原则：**正文决定“为什么需要这份素材、插在哪里”；本清单决定“具体拍什么、怎么拍、优先级、状态和备用方案”。**

---

## 0. 使用方式

- 正文中的 `【截图占位 ...】` / `【录屏占位 ...】` 是素材引用位置；
- 本文件是本讲唯一执行清单；
- P0：必须准备；P1：强烈建议；P2：可选；
- 每项完成后把状态改为：`⬜ 未准备` / `🟨 已采集待处理` / `✅ 可直接用于培训`；
- 同一素材如果跨讲复用，只保留一个原始文件，但在两个讲义清单中分别注明用途；
- 现场 Demo 涉及网络、模型排队、Browser、SSH、Build、GitHub Actions 时必须准备预录或静态备用。

---

# 31. 第三讲截图执行清单

## 31.1 多 Agent 共性

### AGENT-01：Harness 总图

建议用统一自绘图，不用某产品官方营销图。

### AGENT-WB-01～04：WorkBuddy

分别拍：

1. Chat / Task；
2. Workspace / Files / Artifact；
3. Skill Marketplace / Community Skill；
4. 如可见，Runtime / Environment。

目的：

> 证明“Chat Surface 后面也可以有完整 Agent Runtime”。

### AGENT-03：Project Rules

至少选择两个真实例子：

- ai-share AGENTS.md；
- BMQuiz AGENTS.md。

拍：

- 文件本身；
- Agent 读取；
- Agent 行为体现规则。

### AGENT-04～06

拍一个 Agent：

- Workspace；
- Plan；
- Memory。

不要为了凑图把每个 Agent 都拍一遍。

## 31.2 Runtime

### ENV-02：Preflight

Windows 和 Linux 各一张即可。

关键字段：

- git；
- python；
- node；
- npm；
- browser；
- docker；
- ssh。

### ENV-03：Runtime 类型

可用图示，结合实际：

- Local；
- WSL；
- Docker；
- SSH；
- Cloud。

## 31.3 File / Shell / Git

### TOOL-02

同一张最好能看到：

- File Tree；
- Search；
- Read。

### TOOL-03

Terminal Tool Call + Permission。

### TOOL-04

git diff + test pass。

## 31.4 Browser

### TOOL-06A～D

这是第三讲重要图组。

A：

> Built-in Browser / Host Chrome / Computer Use。

B：

> Playwright / CDP 技术层。

C：

> Host Chrome 接入方式。

D：

> Structured Browser vs Vision Browser vs Computer Use 对模型要求。

## 31.5 Tool / MCP / Skill

### CONNECT-01～04

建议统一自绘一套，不要四种风格。

### AGENT-08

某 Agent 当前 MCP Tool 列表。

### AGENT-09

真实 Skill 目录 + SKILL.md。

### CONNECT-06

同一能力：

> API → MCP → Skill。

## 31.6 Permission / Verification

### AGENT-12

Approval / Sandbox。

### AGENT-13

Diff + Test + Browser QA。

---

# 32. 第三讲录屏执行脚本

## AGENT-R01：同任务跨 Agent

不要做“谁更快”。

固定一个简单任务：

> 读取仓库规则，找到某配置项并说明它的来源，不修改文件。

选择 2～3 个 Agent。

目的是：

> 展示 Workspace / Search / Tool Trace 的共性。

## AGENT-R02：WorkBuddy Chat → Workspace

步骤：

1. 从 Chat Surface 提任务；
2. 进入 Workspace；
3. 生成/修改一个 Artifact；
4. 展示结果。

## AGENT-R04：读取 Project Rules

步骤：

1. 新会话；
2. 提一个会触发项目约束的任务；
3. Agent 先读 AGENTS.md；
4. 最终方案体现规则。

## AGENT-R05 / ZCODE-R02：Tool Loop

Sensor Guard：

`Test Fail → Search → Edit → Test Pass → Diff`

必须保留工具动作，不要只保留文字总结。

## TOOL-R02：Browser Visual QA

选择一个本地 Web 页面：

1. Agent 改 UI；
2. 启动；
3. Playwright / Browser；
4. Screenshot；
5. 发现问题；
6. 修改；
7. 再截图。

## TOOL-R03：Server

建议使用测试/受控环境。

BMQuiz 或 model-metric：

1. SSH；
2. status；
3. logs；
4. health；
5. 如需更新则执行受控更新；
6. verify。

涉及真实生产变更时，不建议现场临时执行高风险动作；使用预录。

## CONNECT-R01～03：API → MCP → Skill

一定使用同一个训练后端。

录成三个短片：

- 直接 API；
- Agent 自动 MCP Tool；
- Skill 指导完整流程。

## AGENT-R09：Approval

选择可安全演示的写操作。

让观众看到：

> Model 想做动作，不代表系统立即允许。

---

# 33. 第三讲现场 Demo 建议

现场实时操作建议控制在四个：

1. Agent 读取 AGENTS.md + Search/Read；
2. Sensor Guard Read/Edit/Test/Diff；
3. Browser Visual QA；
4. MCP Tool 调用。

服务器、高风险 Permission、跨 Agent 比较、Runtime 切换优先使用预录。

原因：

> 第三讲概念很多，现场 Demo 如果频繁切工具，会让主线碎掉。

所以现场建议：

> **ZCode 或 Codex 作为主要演示面，其他 Agent 用截图/短录屏做机制对照。**

---
