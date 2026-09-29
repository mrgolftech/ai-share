# 培训讲义：从 Chat 到 Agent Harness

> 模块二：为什么只有 Chat 不够  
> 核心问题：同一个模型，放进不同的工作环境后，为什么能完成完全不同级别的任务？  
> 资料核实：2026-09-29

## 一、不要先问“哪个 Agent 最好”

这一章不从 ZCode、Codex、OpenCode、DSH、Pi 的菜单开始。

先问一个更稳定的问题：

> **一个模型怎样从“回答问题”，变成“围绕目标持续工作”？**

模型本身主要做两件事：

- 根据上下文判断下一步；
- 生成文本、结构化结果或 Tool Call。

真正让它能够读项目、改文件、跑命令、看结果、继续修复的，是模型外面的执行环境。

因此培训使用下面这个统一视角：

~~~text
Agent = Model + Harness
~~~

这里的 **Harness** 可以理解为“包在模型外面的一整套智能体运行与工程环境”。

DeepSeek Harness 官方当前甚至直接用“Agent = Model + Harness”描述这一关系。

---

## 二、Chat 与 Agent 不是简单的两个物种，而是一条连续谱

过去很容易这样分：

~~~text
OpenWebUI / Cherry Studio = Chat
Codex / OpenCode / ZCode = Agent
~~~

到 2026 年，这种二分已经不够准确。

Open WebUI 已经支持服务端 Tool Loop、MCP、OpenAPI Tool Server 和 Open Terminal；Cherry Studio 也已经提供 Workspace / Agent、文件、命令和 MCP。

因此更准确的区分应该是：

| 维度 | 对话优先工作台 | 工程 Agent / Coding Agent |
|---|---|---|
| 默认入口 | 会话 | Workspace / Repository / Task |
| 默认对象 | 一段上下文 | 一个持续变化的项目环境 |
| 人的角色 | 人不断发起下一轮 | 人给目标、约束和关键判断 |
| 文件 | 附件、知识库为主 | 工作区文件是核心状态 |
| Shell | 可选扩展 | 常见核心能力 |
| Git | 通常不是主线 | 常见工程闭环 |
| 工具调用 | 可以支持 | 通常深度参与循环 |
| 任务循环 | 一轮或少量多轮 | Read → Act → Observe → Verify → Iterate |
| 结果 | 回答、内容 | 修改后的工程状态 + 验证结果 |

所以培训不说“Chat 已经过时”。

更准确的说法是：

> **Chat 适合孤立问题；复杂工程任务需要更完整的 Harness。**

---

## 三、Open WebUI / Cherry Studio 应该怎样讲

### 3.1 Open WebUI

Open WebUI 的默认体验仍然非常适合：

- 多模型聊天；
- 文件和知识库问答；
- Web Search；
- 日常模型入口。

但它现在也可以把工具接入模型，包括：

- Workspace Tools；
- MCP；
- OpenAPI Tool Server；
- Open Terminal；
- 服务端 Tool Calling Loop。

因此它已经不是“纯聊天壳”。

培训中更适合把它定义为：

> **对话优先、逐步扩展 Agent 能力的模型工作台。**

### 3.2 Cherry Studio

Cherry Studio 同样从多模型对话、知识库和桌面助手体验出发，但当前也已经提供：

- Agent；
- Workspace；
- 文件读取；
- 命令执行；
- MCP；
- Skill。

因此它也处在 Chat → Agent 的连续谱上。

培训中可以这样说：

> **Open WebUI / Cherry Studio 更适合从“模型入口”理解；Coding Agent 更适合从“工程执行环境”理解。**

两类产品正在互相靠近，但默认工作方式仍然不同。

---

## 四、八个代表性 Coding Agent：不要只看界面，要看 Harness

本培训至少覆盖：

- ZCode；
- Codex；
- Claude Code；
- OpenCode；
- DeepSeek Harness（DSH）；
- Pi；
- Cline；
- Kilo Code。

### 4.1 一张表先建立认识

| Agent | 主要定位 | 开源 | 自有 API 接入 | 最值得观察的特点 |
|---|---|---|---|---|
| ZCode | ADE / Workspace-first | Apache-2.0 | 很容易 | Desktop / Browser / Terminal、Goal Mode、AGENTS.md、长任务 |
| Codex | Terminal / IDE / App / Cloud | CLI/Harness Apache-2.0 | 中等 | Sandbox/Approval、Shell/Git、AGENTS.md、MCP/Skill/Plugin |
| Claude Code | Terminal-first | 否，专有 | 一般 | CLAUDE.md、Hooks、Skills、MCP、Subagents、成熟模型-Harness 联调 |
| OpenCode | Provider-neutral open agent | MIT | 非常容易 | 75+ Provider、本地模型、自定义 OpenAI-compatible、高度可配置 |
| DSH | 可组合 Agent Harness | MIT | 非常容易 | Everything is a Plugin，适合解释 Harness 架构本身 |
| Pi | Minimal terminal harness | MIT | 容易 | 默认 read/write/edit/bash，Extension / Skill / SDK，核心极简 |
| Cline | IDE-first Agent | Apache-2.0 | 非常容易 | Plan/Act、Browser、Terminal、MCP、BYOK、人机批准 |
| Kilo Code | Multi-surface agentic platform | MIT | 非常容易 | VS Code / JetBrains / CLI、多模式、Subagents、Marketplace、多 Provider |

“自有 API 接入难易”不是综合能力评分，只看企业自建 / 第三方模型服务接入门槛。

完整对比、开源许可、Provider 配置和资料来源见：

~~~text
docs/references/coding-agent-comparison-2026-09.md
~~~

### 4.2 对部门内网 Qwen，最值得比较的不是“能不能接”，而是“接上以后 Harness 表现如何”

我们当前内网模型已经实测：

- OpenAI Chat；
- OpenAI Responses；
- Anthropic Messages；
- Streaming；
- Tool Loop。

因此八个 Agent 中，多数已经具备可行的接入路径。

更值得实测：

- Tool Schema 兼容；
- Thinking 行为；
- Context 管理；
- Compaction；
- Prompt Cache；
- 文件修改策略；
- 是否主动 Test；
- 错误恢复；
- Token / TTFT / 总耗时；
- 人工介入次数。

其中：

- Codex 当前自定义 Provider 更偏 Responses；
- Claude Code 更偏 Anthropic-compatible API；
- OpenCode / DSH / Cline / Kilo 对自定义 Provider 更直接；
- ZCode 支持第三方 OpenAI / Anthropic 协议；
- Pi 对标准协议配置简单，特殊协议可通过 Extension 扩展。

### 4.3 公开 Harness Benchmark：FrontierHarness Eval

2026 年的 FrontierHarness Eval 很适合本培训引用，因为它控制了关键变量：

> **Same Model + Same Tasks + Same Runtime，只改变 Harness。**

v1.0 使用同一个 Kimi K3，覆盖 30 个软件工程任务、12 个 Harness 配置、360 次 Evaluation。

与本培训相关的冻结结果：

| Harness | Frozen Version | Pass Rate |
|---|---:|---:|
| Codex | 0.148.0 | 66.7% |
| DSH Creator | 0.1.0-rc.8 | 63.3% |
| Claude Code | 2.1.237 | 63.3% |
| Pi | 0.84.2 | 60.0% |
| DSH Standard | 0.1.0-rc.8 | 60.0% |
| DSH Minimal | 0.1.0-rc.8 | 56.7% |
| OpenCode | 1.18.19 | 50.0% |

ZCode、Cline、Kilo 没有进入 v1.0 这组冻结测试，不人为补分数。

这一页真正要讲的不是：

> “Codex 永远第一。”

而是：

> **同一个模型，只换 Harness，任务完成率、Token 成本、Cache 和耗时都会变。**

而且不同 Benchmark / 模型下排序可能变化，因此更准确的公式是：

~~~text
Agent Effectiveness
= Model
× Harness
× Task
× Configuration
× Runtime
~~~

### 4.4 八个 Agent 在培训中的分工

不要连续做八段软件介绍。

建议分成三类：

**厂商旗舰 Harness：**

- Codex；
- Claude Code；
- ZCode。

用来观察模型厂商如何把模型和 Harness 联调成完整产品。

**模型中立的开源 Harness：**

- OpenCode；
- Cline；
- Kilo。

用来解释 Provider 抽象、BYOK 和企业内网 API 接入。

**Harness 架构路线：**

- DSH；
- Pi。

DSH 展示“Everything is a Plugin”；Pi 展示“Minimal Harness”。

二者一繁一简，最适合解释 Harness 到底由什么组成。

---

## 五、Harness 到底包含什么

“Harness”不是一个所有厂商都严格统一定义的标准协议，但在 Agent 工程语境里，可以把它理解成以下能力的组合：

~~~text
                         ┌───────────────┐
                         │   User Goal   │
                         └───────┬───────┘
                                 ↓
┌─────────────────────────────────────────────────────┐
│                    Agent Harness                    │
│                                                     │
│  Instructions / Rules                              │
│  Context / Session / Compaction                     │
│  Agent Loop / Planning / Routing                    │
│  Model Adapter / Provider                           │
│  Tool Registry / Tool Schema                        │
│  Workspace / File / Shell / Git / Browser / MCP     │
│  Permission / Approval / Sandbox                    │
│  Memory / State / Checkpoint                        │
│  Verification / Test / Trace / Observability        │
│  UI / TUI / IDE / Web                               │
└──────────────────────────┬──────────────────────────┘
                           ↓
             Files / OS / Git / Browser / APIs
~~~

不是每个 Agent 都具备全部模块。

但只要理解这些共性，就不必把每一种 Agent 当成全新的知识重新学一遍。

---

## 六、为什么“同一个模型”换一个 Agent，效果会明显不同

模型能力只是最终效果的一部分。

同一个模型在不同 Harness 中，结果可能因为以下因素发生明显变化：

### 6.1 System Prompt / 项目规则不同

例如：

- 是否读取 AGENTS.md；
- 是否要求先计划；
- 是否要求测试后才能交付；
- 是否要求检查 Git Diff。

### 6.2 Tool Schema 不同

同一个“修改文件”能力，可以实现为：

- 整文件重写；
- search/replace；
- patch；
- line-based edit。

工具设计会直接影响修改成功率。

### 6.3 Context 管理不同

长任务中需要处理：

- 历史消息；
- 工具返回；
- 文件内容；
- 摘要；
- Compaction；
- 子任务上下文。

上下文管理差，即使模型很强也可能越做越乱。

### 6.4 权限与 Sandbox 不同

Agent 需要知道：

- 什么可以自动执行；
- 什么必须请求批准；
- 哪些目录可写；
- 是否能联网；
- 是否能调用外部 MCP。

安全边界也是 Harness 的一部分。

### 6.5 是否真正形成验证闭环

只会“写代码”的 Agent 与能够：

~~~text
修改
→ 运行
→ 看错误
→ 修复
→ 再运行
→ 浏览器验收
→ Git Diff
~~~

的 Agent，实际完成率会有很大差异。

因此：

> **模型决定“会不会想”，Harness 很大程度决定“能不能把事情做完”。**

---

## 七、从 Prompt → Answer 到 Goal → Deliver

Chat 的典型循环：

~~~text
Prompt
  ↓
Model
  ↓
Answer
~~~

Agent 的典型循环：

~~~text
Goal
 ↓
Plan
 ↓
Read
 ↓
Act
 ↓
Observe
 ↓
Verify
 ↓
Iterate
 ↓
Deliver
~~~

这里最关键的变化不是“可以调用 Shell”。

而是：

> **模型的输出不再天然等于任务结束。**

模型输出可能只是：

- 下一条命令；
- 一次文件修改；
- 一个 Tool Call；
- 一个候选方案。

Harness 会把执行结果重新放回上下文，让模型继续判断。

---

## 八、统一 Demo：同一个“鹈鹕骑自行车”题同时测试模型和 Harness

这道题建议承担两个教学任务。

### 8.1 第一轮：不同模型，同一种 Chat 工作方式

所有模型使用同一 Prompt：

> 创建一个单文件 HTML，用 SVG、CSS 和 JavaScript 生成一只鹈鹕骑自行车的循环动画。不得使用外部图片或第三方库。自行车轮子要转动，腿要踩踏板，鹈鹕身体有轻微起伏，页面可直接在浏览器打开。

观察：

- 是否遵循单文件要求；
- SVG 结构是否完整；
- JS / CSS 是否可运行；
- 鹈鹕和自行车是否能正确组合；
- 动作是否协调；
- 第一次结果是否可直接使用。

这一轮主要观察 **Model Capability**。

### 8.2 第二轮：同一个模型，Chat 与 Agent 对比

Chat：

~~~text
Prompt
→ 返回 HTML 代码
→ 人复制
→ 人保存
→ 人打开浏览器
→ 人发现问题
→ 人重新描述问题
~~~

Agent：

~~~text
Goal
→ 创建文件
→ 启动页面
→ 浏览器观察
→ 发现轮子/腿/构图问题
→ 修改
→ 再验证
→ 交付文件 + Diff
~~~

这一轮主要观察 **Harness Capability**。

这样可以避免一个常见错误：

> 把“Agent 有浏览器、有文件工具带来的优势”，误认为完全是“模型更聪明”。

---

## 九、这道 Demo 为什么适合培训

“鹈鹕骑自行车”不是严谨 Benchmark，但非常适合现场教学。

原因有五个：

1. **任务短**：几分钟内可以看到结果，不需要大型工程环境；
2. **组合不常见**：不是最常见的网页模板，能观察组合生成能力；
3. **跨能力**：同时涉及自然语言理解、SVG 几何、CSS/JS、动画逻辑；
4. **结果可视化**：学员不需要看大量代码就能判断明显问题；
5. **天然适合 Agent 闭环**：生成后必须真正运行，才知道动画是否正确。

它的局限也必须明确：

- 单题不能代表模型总体能力；
- 动画审美有主观性；
- 采样随机性会影响结果；
- 不适合据此做严肃模型排名。

因此统一定位为：

> **能力演示题，不是标准化 Benchmark。**

若需要形成更可靠对比，应固定 Prompt、参数和运行环境，至少重复多次，并配合代码正确性和可执行性指标。

---

## 十、这一章最后只留下三个结论

第一：

> **Chat 和 Agent 不是“旧工具”和“新工具”的关系，而是工作复杂度不同。**

第二：

> **Agent 的共性不是某个按钮，而是 Model 外面的 Harness：Context、Tools、Loop、State、Permission、Verification。**

第三：

> **工具会不断变化，但 Harness 的共性以及项目规则、Skill、MCP、脚本、测试和 CI 等工程资产可以长期复用。**

---

## 十一、参考资料

- DeepSeek Harness：官方将其描述为开源 Agent Harness，并明确提出“Agent = Model + Harness”：https://www.deepseek.com/harness/
- DeepSeek Harness GitHub：https://github.com/deepseek-ai/deepseek-harness
- Pi：官方定位为 minimal agent harness：https://pi.dev/
- OpenCode Agent / Tools / Skills：https://opencode.ai/docs/
- Open WebUI Tools / Server-side Tool Calling：https://docs.openwebui.com/
- Cherry Studio Agent / MCP：https://cherryai.com/docs/
- Codex：项目规则与 Sandbox/Approval 以当前 OpenAI Codex 官方仓库和文档为准。
