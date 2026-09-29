# 培训讲义：把 Agent 拆开看——从不同工具看到共同的 Harness 结构

> 状态：已有初稿
> 日期：2026-09-30
> 定位：连接“为什么 Chat 不够”与“Agent 如何操作真实世界”的桥梁章节。
> 核心目标：不把 Codex、Hermes、OpenCode、Claude Code、Cline、Pi 等当成彼此孤立的软件，而是建立一套可以迁移到不同 Agent 的统一认知模型。

---

# 一、先给出结论：不要先记工具名，先认清 Agent 的共同骨架

不同 Agent 的界面、配置文件和命令不同，但底层都在解决相似的问题：

1. 模型是谁；
2. 模型当前知道什么；
3. 项目规则是什么；
4. 工作目录在哪里；
5. 当前任务如何计划和推进；
6. 能使用哪些工具；
7. 如何访问外部系统；
8. 如何保存跨会话信息；
9. 如何控制权限和风险；
10. 如何观察执行结果并继续迭代；
11. 最终通过什么界面让人使用。

培训建议统一采用下面这个抽象：

~~~text
                         ┌─────────────────────┐
                         │        User         │
                         └──────────┬──────────┘
                                    │ Goal
                                    ▼
┌──────────────────────────────────────────────────────────┐
│                    Agent Harness                         │
│                                                          │
│  Instructions / Identity / Project Rules                 │
│  Context Management / Planning / Memory                  │
│  Tool Selection / Permission / Sandbox / Verification    │
│                                                          │
│          ┌──────────────┐      ┌──────────────┐           │
│          │    Model     │◄────►│ Agent Loop   │           │
│          └──────────────┘      └──────┬───────┘           │
└───────────────────────────────────────┼───────────────────┘
                                        │
              ┌─────────────────────────┼───────────────────────┐
              ▼                         ▼                       ▼
        Workspace Tools            External Tools          UI Control
      File/Shell/Git/Test       API / MCP / DB / SaaS   Browser / Computer
              │                         │                       │
              └─────────────────────────┴───────────────────────┘
                                        │
                                        ▼
                                  Observe / Verify
                                        │
                                        └────→ Iterate
~~~

核心观点：

> **Agent 不是“一个更会聊天的模型”，而是模型外面的一整套执行与上下文管理系统。**

也就是：

> **Model 决定推理和生成能力，Harness 决定模型能够看到什么、调用什么、如何行动、如何验证、如何持续工作。**

---

# 二、什么是 Harness

Harness 可以理解为“把模型变成可工作的 Agent 的运行框架”。

它通常负责：

- 组装 System / Developer / Project Instructions；
- 读取 Workspace；
- 管理上下文；
- 定义工具 Schema；
- 让模型选择和调用工具；
- 接收 Tool Result；
- 决定是否继续下一轮；
- 维护任务状态；
- 管理权限与 Sandbox；
- 处理 Memory；
- 记录日志和执行轨迹；
- 组织 Sub-agent；
- 最终交付结果。

因此即使使用完全相同的模型：

~~~text
Same Model
  +
Different Harness
  ↓
Different Context
Different Tools
Different Permissions
Different Agent Loop
Different Verification
  ↓
Different Result
~~~

这就是为什么培训不应该把“模型能力”和“Agent 产品能力”混为一谈。

---

# 三、先看一个受控实验：模型不变，只换 Harness

在拆解 Harness 之前，先回答一个问题：

> **如果模型完全相同，只换 Agent 工具，结果会不会变？**

FrontierHarness Eval v1.0 很适合作为这一章的开场证据。

它固定：

- 同一个模型：Kimi K3；
- 同一批软件工程任务；
- 同一运行环境；
- 只改变 Harness。

冻结测试规模：

- 30 个软件工程任务；
- 12 个 Harness 配置；
- 360 次 Evaluation；
- 其中 21 个 Terminal-Bench Tasks；
- 9 个 DeepSWE Tasks。

与本培训最相关的冻结结果：

| Harness | Frozen Version | Pass Rate | Effective Cost / Pass | Median Runtime |
|---|---:|---:|---:|---:|
| Codex | 0.148.0 | **66.7%** | $3.47 | 6m43s |
| DSH Creator | 0.1.0-rc.8 | **63.3%** | $3.28 | 6m44s |
| Claude Code | 2.1.237 | **63.3%** | $18.34 | 9m38s |
| Pi | 0.84.2 | **60.0%** | $2.43 | 7m33s |
| DSH Standard | 0.1.0-rc.8 | **60.0%** | $3.46 | 6m17s |
| DSH Minimal | 0.1.0-rc.8 | **56.7%** | $4.72 | 5m41s |
| OpenCode | 1.18.19 | **50.0%** | $3.24 | 6m27s |
| Hermes | 0.20.4 | **50.0%** | $2.90 | 6m58s |

注意：

- 这是冻结历史实验，不是今天各产品最新版的实时排行榜；
- Cline、Kilo、ZCode 没进入这组冻结测试，不人为补分；
- 单一 Kimi K3 + 软件工程任务不能外推成所有场景的综合能力排名。

它真正支持的结论是：

> **同一个模型，只换 Harness，任务完成率、成本和运行时间都可能明显变化。**

因此更准确的工程表达是：

~~~text
Agent Effectiveness
= Model
× Harness
× Task
× Configuration
× Runtime
~~~

这组结果回答“为什么 Harness 值得研究”，后面的章节再回答：

> **Harness 到底哪些机制导致差异。**

---

# 四、九个代表性 Agent：不要按产品背功能，要按设计路线观察

培训中涉及：

- ZCode；
- Codex；
- Claude Code；
- OpenCode；
- DeepSeek Harness（DSH）；
- Pi；
- Cline；
- Kilo Code；
- Hermes Agent。

| Agent | 主要定位 | 开源状态 | 自有 / 内网 API 接入 | 最值得观察的机制 |
|---|---|---|---|---|
| ZCode | ADE / Workspace-first | Apache-2.0 | 容易 | Desktop / Browser / Terminal、Goal Mode、AGENTS.md、长任务 |
| Codex | Terminal / IDE / App / Cloud | CLI/Harness Apache-2.0 | 中等 | AGENTS.md、Sandbox/Approval、Shell/Git、MCP、Skill |
| Claude Code | Terminal-first | 专有 | 一般 | CLAUDE.md、Hooks、Skills、MCP、Subagents、权限 |
| OpenCode | Provider-neutral open agent | MIT | 很容易 | Provider 抽象、本地模型、Permissions、MCP、Skills |
| DSH | 可组合 Harness | MIT | 很容易 | Everything is a Plugin，适合解释 Harness 组件化 |
| Pi | Minimal terminal harness | MIT | 容易 | 极简 Tool Core、Extension / Skill / SDK |
| Cline | IDE-first | Apache-2.0 | 很容易 | Plan/Act、Browser、Terminal、MCP、BYOK、人机确认 |
| Kilo Code | Multi-surface platform | MIT | 很容易 | VS Code / JetBrains / CLI、Subagents、Browser、Marketplace |
| Hermes Agent | Persistent general-purpose agent | MIT | 很容易 | Memory、Skills、Cron、Gateway、Browser、Subagents、多 Runtime |

“接入难易”只表示当前企业自建 / 第三方模型 API 的配置便利度，不是综合能力评分。

## 4.1 用四种路线讲，而不是连续讲九款软件

**厂商旗舰 Harness：**

- Codex；
- Claude Code；
- ZCode。

观察模型厂商如何把模型、Prompt、Tool、Sandbox、Context 和产品体验联调。

**Provider-neutral 开源 Harness：**

- OpenCode；
- Cline；
- Kilo。

观察 BYOK、自定义 Provider、本地 / 内网模型接入。

**Harness 架构实验路线：**

- DSH；
- Pi。

DSH 展示“Everything is a Plugin”，Pi 展示 Minimal Harness。

**长期运行的通用 Agent：**

- Hermes Agent。

它把 Coding Agent 进一步扩展到 Persistent Memory、Skills、Cron、Messaging Gateway、Browser、Subagent 和多种执行后端。

## 4.2 对部门内网 Qwen，真正值得测的是 Harness，而不是“能不能接”

部门内网模型已经有 OpenAI Chat、Responses、Anthropic Messages、Streaming、Tool Loop 等实测，因此多数 Harness 已经存在接入路径。

下一阶段内部对比应该固定：

- 同一个内网 qwen3.6；
- 同一个任务集；
- 同一个 AGENTS.md；
- 同一个 Workspace；
- 尽量一致的权限；
- 一致的验收条件。

记录：

- 完成率；
- Tool Call 成功率；
- 人工介入次数；
- 是否主动测试；
- 错误恢复次数；
- Context / Compaction 行为；
- Token；
- TTFT；
- 总耗时。

公网 FrontierHarness 用来证明“Harness 有影响”；部门内部同模型实验才回答：

> **哪一种 Harness 更适合我们的内网模型和工程环境。**

完整产品与来源资料继续维护在：

~~~text
docs/references/coding-agent-comparison-2026-09.md
~~~

---

# 五、第一层：Identity / System Instructions——“你是谁”

每个 Agent 都需要某种最高层行为约束。

它可能来自：

- 产品内置 System Prompt；
- 用户级全局规则；
- Persona；
- Personality；
- SOUL；
- Organization Policy。

Hermes 是一个非常清晰的例子：

- SOUL.md：Agent 身份、语气、风格；
- USER.md：用户画像和偏好；
- MEMORY.md：Agent 跨会话保存的经验和事实；
- AGENTS.md / .hermes.md：项目规则。

因此要特别强调：

> **SOUL.md 不是 Agent 的普遍标准，它只是 Hermes 对“Agent Identity”这一通用问题的一种实现。**

培训不要让学员记住“所有 Agent 都应该有 SOUL.md”，而应理解：

> **任何 Agent Harness 都需要解决 Identity / Behavior Policy，只是保存方式不同。**

---

# 六、第二层：Project Instructions——“在这个项目里应该怎么工作”

这是 Coding Agent 最值得沉淀的机制之一。

Codex 原生使用：

~~~text
AGENTS.md
~~~

它可以包含：

- 项目目标；
- 目录结构；
- 架构约束；
- 编码规范；
- 构建命令；
- 测试要求；
- Git 工作流；
- 禁止修改的区域；
- 验收标准。

并且可以按目录形成层级作用域。

其他 Agent 使用的文件名可能不同，例如：

- Claude Code：CLAUDE.md
- Gemini / Qwen Code：各自项目上下文文件
- Cursor / Cline / Windsurf：Rules 类文件
- Hermes：可以读取 AGENTS.md、CLAUDE.md、自身项目文件等

因此推荐培训统一使用：

> **Project Context / Project Instructions**

作为上位概念。

AGENTS.md 是当前非常值得推广的可移植实现之一，但不要把“文件名”误讲成 Agent 的底层原理。

核心区分：

~~~text
README.md
→ 主要告诉人：项目是什么、怎么使用

AGENTS.md / CLAUDE.md / Rules
→ 主要告诉 Agent：在这个项目里应该怎么工作
~~~

---

# 七、第三层：Workspace——“Agent 在哪里工作”

Workspace 是 Chat 与工程 Agent 的关键分界之一。

一个典型 Workspace 通常至少包括：

~~~text
Working Directory
├── Source Code
├── Documents
├── Config
├── Tests
├── Git Repository
├── Build Environment
└── Generated Artifacts
~~~

Agent 不再只接收用户粘贴的一小段文本，而是能够：

~~~text
Read
→ Search
→ Edit
→ Run
→ Observe
→ Re-edit
~~~

因此：

> **Workspace 不只是“一个文件夹”，而是 Agent 执行任务的世界状态。**

需要让学员理解：

- CWD 为什么重要；
- Repo Root 为什么重要；
- Agent 为什么需要知道文件树；
- 为什么不能把整个 Repo 一次性塞进 Context；
- Agent 为什么需要 grep / glob / index / semantic search；
- 为什么目录级 Project Instructions 有价值。

---

# 八、第四层：Context Management——“当前这一轮模型到底看到了什么”

Agent 并不是拥有无限记忆。

每一轮真正送入模型的是一个受限 Context。

可能包括：

~~~text
System Instructions
+ User Request
+ Project Instructions
+ Relevant Files
+ Conversation History
+ Tool Results
+ Memory
+ Plan / Task State
~~~

因此 Agent Harness 必须不断解决：

- 哪些内容需要保留；
- 哪些内容可以摘要；
- 哪些文件按需读取；
- 哪些 Tool Result 太大需要截断；
- 哪些历史已经失效；
- 什么应该重新检索。

这与前面知识库章节形成直接联系：

> **Agentic Retrieval 本质上也是 Context Management 的一部分。**

---

# 九、第五层：Plan / Task State——“下一步做什么”

复杂 Agent 通常不会只做一次：

~~~text
Prompt → Answer
~~~

而需要维护某种任务状态：

~~~text
Goal
→ Decompose
→ Plan
→ Execute Step
→ Observe
→ Update State
→ Continue
~~~

不同 Harness 的实现方式不同：

- Plan Mode；
- Todo List；
- Task List；
- Scratchpad；
- Checkpoint；
- Workflow State；
- Issue / Build Plan 文件；
- Sub-agent Task。

因此培训中不建议把“Plan 文件”讲成固定标准。

真正需要建立的是：

> **复杂任务需要显式或隐式的 Task State，Agent 才能跨多个步骤保持方向。**

---

# 十、第六层：Memory——“哪些东西需要跨会话留下”

这里要把三个概念分开：

## 10.1 Context

当前模型调用正在看到的内容。

## 10.2 Session History

本次会话过去发生过什么。

## 10.3 Persistent Memory

跨 Session 仍然保留的信息。

典型 Memory 内容：

- 用户偏好；
- 环境信息；
- 常用路径；
- 项目长期事实；
- 已验证经验；
- 工具使用习惯。

但需要强调：

> **Memory 不是越多越好。**

Memory 会占 Context，也可能过期、冲突、污染后续判断。

所以成熟 Harness 会尝试解决：

- Memory 写入条件；
- 容量限制；
- 更新 / 删除；
- 作用域；
- 冲突；
- 检索。

Hermes 的 MEMORY.md / USER.md 很适合作为教学案例，但它代表的是“Persistent Memory”这一类机制，而不是所有 Agent 都使用同样文件名。

---

# 十一、第七层：Tools——“Agent 能做什么”

模型自己不能直接：

- 写文件；
- 执行 Shell；
- 提交 Git；
- 查询数据库；
- 登录服务器；
- 操作浏览器；
- 发 HTTP Request。

这些都需要 Tool。

Agent 常见原生 Tool：

~~~text
Filesystem
Shell / Terminal
Search / Grep
Git
Patch / Edit
Test Runner
Browser
Computer
Web Search
~~~

一个典型 Tool Loop：

~~~text
Model
  ↓ tool_call
Harness
  ↓ execute
Tool
  ↓ result
Harness
  ↓
Model
~~~

这和模块一中的 Function Calling / Tool Calling 正好连接起来。

---

# 十二、第八层：API / MCP——“外部能力如何接进 Agent”

API 和 MCP 都可以把外部系统接给 Agent，但层次不同。

## API

API 是具体系统能力的接口：

~~~text
GET /devices
POST /deploy
SQL Query
GitHub REST API
~~~

## MCP

MCP 提供的是 Agent Client 与外部能力之间的一套标准化连接协议。

MCP Server 可以暴露：

- Tools；
- Resources；
- Prompts。

因此可以把关系先简化为：

~~~text
Business System
      │
      ├── Native API
      │
      ▼
   MCP Server
      │
      ▼
 Agent / MCP Client
~~~

MCP 不会消灭 API。

很多 MCP Server 的内部仍然是在调用：

- REST API；
- SDK；
- Database；
- Filesystem；
- CLI。

核心观点：

> **API 是能力接口；MCP 是让 Agent 标准化发现和调用这些能力的一种协议层。**

---

# 十三、第九层：Skill——“把会做一次变成会重复做”

Skill 不等于 Tool。

Tool 更接近：

> **我能执行什么动作。**

Skill 更接近：

> **遇到某类任务，我应该按照什么方法、顺序和标准去完成。**

例如一个 GitHub Tool 可能提供：

- search；
- read file；
- create branch；
- update file；
- create PR。

而一个“发布版本 Skill”可以规定：

~~~text
Read project rules
→ Check git status
→ Run tests
→ Update version
→ Generate changelog
→ Commit
→ Tag
→ Push
→ Check CI
→ Report result
~~~

因此：

~~~text
Tool = Capability
Skill = Reusable Procedure
~~~

Skill 可能进一步包含：

- SKILL.md；
- Prompt；
- Scripts；
- Templates；
- References；
- Validation Rules。

这正是培训“形成可复用资产”模块的重要桥梁。

---

# 十四、第十层：Browser Use——“专门操作 Web 世界”

这里建议培训把几个容易混淆的概念彻底拆开。

## 14.1 HTTP / Web Search

如果只是获取公开数据：

~~~text
HTTP / Search
~~~

通常更快、更稳定、更便宜。

## 14.2 Browser Automation

当任务需要：

- JavaScript 渲染；
- 登录态；
- 点击；
- 表单；
- 页面流程；
- UI 测试；

就需要真实浏览器。

常见实现：

- Playwright；
- CDP；
- Puppeteer；
- Browser Use / Browser Harness 等 Agent Browser 层。

Browser Use 这一类工具的价值是：

> **把 DOM、页面状态和浏览器操作封装成更适合 Agent 使用的工具。**

因此“Browser Use”既可以泛指 Agent 使用浏览器，也可能特指 Browser Use 这个开源项目，培训中需要明确上下文。

---

# 十五、第十一层：Computer Use——“不只操作浏览器，而是操作 GUI”

Computer Use 的作用范围更宽：

~~~text
Browser Use
→ 主要操作浏览器页面

Computer Use
→ 可以操作浏览器，也可以操作桌面 GUI 应用
~~~

Computer Use 通常依赖：

- Screenshot；
- Mouse；
- Keyboard；
- Window / Screen State。

例如：

~~~text
Screenshot
→ Model Understands UI
→ Click / Type / Scroll
→ New Screenshot
→ Continue
~~~

适合：

- 没有 API 的软件；
- 桌面客户端；
- 老旧系统；
- 跨应用流程；
- 视觉验收。

但它通常：

- 比 API 更慢；
- 比结构化 Tool 更脆弱；
- 更受 UI 变化影响；
- 风险更高。

因此推荐优先级：

~~~text
Structured API / Tool
        ↓
Browser DOM / Playwright
        ↓
Computer Use
~~~

不是因为 Computer Use “能力差”，而是工程系统通常优先选择更稳定、可验证、可复现的接口。

---

# 十六、第十二层：Permission / Sandbox——“Agent 可以做到，不代表应该直接做”

Agent 能执行真实动作之后，权限边界非常重要。

常见机制：

- Read Only；
- Workspace Write；
- Full Access；
- Command Approval；
- Network Approval；
- Secret Isolation；
- Container / Sandbox；
- Human Confirmation。

因此 Harness 不只是“赋予 Agent 能力”，还必须解决：

> **Agent 可以在什么范围内使用这些能力。**

培训统一采用：

> **模型负责判断，工具负责执行，权限系统限制边界，人负责最终授权和判断。**

---

# 十七、第十三层：Verification——“做完不等于做对”

真正成熟的 Agent 工作流必须加入验证：

~~~text
Edit Code
→ Run Test
→ Start App
→ Browser Check
→ Read Logs
→ Compare Expected Result
→ Fix
~~~

也就是：

> **Act 后面必须有 Observe / Verify。**

这是 Chat 与工程 Agent 差距最大的地方之一。

---

# 十八、第十四层：Sub-agent——“一个 Harness 里可以有多个执行角色”

复杂任务可以拆分：

~~~text
Main Agent
├── Research Agent
├── Coding Agent
├── Test Agent
└── Review Agent
~~~

Sub-agent 的价值不只是“并行”。

它还可以：

- 隔离上下文；
- 使用不同模型；
- 使用不同工具权限；
- 将特定任务交给专门 Prompt / Skill；
- 降低主上下文污染。

但不要把多 Agent 当成默认答案。

如果一个 Agent 可以简单完成，就不必人为增加编排复杂度。

---

# 十九、第十五层：CLI、GUI、IDE、Web——只是不同的人机入口

培训中尤其需要避免：

> “CLI Agent 更高级，GUI Agent 更低级。”

这并不准确。

CLI 和 GUI 主要差别在交互入口和工作流集成，不等于模型能力本身。

## CLI 更适合

- 工程师；
- Repo / Shell 重度工作；
- SSH；
- 自动化脚本；
- 管道组合；
- CI；
- 无头环境；
- 快速键盘操作。

优势：

- 离工作目录最近；
- Shell / Git 自然；
- 容易自动化；
- 日志透明；
- 远程服务器好用。

## GUI / Desktop 更适合

- 文件拖拽；
- 多会话管理；
- Diff 可视化；
- Browser / Computer 交互；
- 图片和多模态；
- 不熟悉命令行的用户；
- 日常办公任务。

优势：

- 学习成本低；
- 可视化强；
- 权限确认和 Tool Call 更容易理解；
- 文件、图片、网页操作更直观。

## IDE Agent 更适合

- 代码浏览；
- 行级上下文；
- Diff；
- Diagnostics；
- Debug；
- 编辑器内开发循环。

因此不要问：

> **“CLI 和 GUI 哪个更强？”**

更应该问：

> **“这个任务的执行环境在哪里？”**

推荐判断：

~~~text
Repo / Terminal / Server / Automation
→ CLI 优先

日常文件 / 多模态 / 浏览器 / 可视化操作
→ GUI / Desktop 优先

长期写代码
→ IDE + Agent

跨环境复杂工程任务
→ CLI + IDE + Browser / GUI 组合
~~~

核心观点：

> **CLI、GUI、IDE 是同一个 Agent Harness 能力的不同 Surface，而不是 Agent 原理上的不同物种。**

---

# 二十、还需要补齐的运行时与生命周期机制

前面的十五层已经解释了 Agent 的主要可见能力，但工程实践中还需要补几类经常被忽略的共性机制。

## 20.1 Model / Provider / Protocol Adapter

Agent 不一定绑定一个模型。

Harness 通常还需要处理：

- Provider；
- Base URL；
- OpenAI / Responses / Anthropic 等 wire protocol；
- 模型能力声明；
- Thinking / Reasoning 参数；
- Tool Calling 差异；
- Vision；
- Context Window；
- Fallback / Routing。

因此：

> **“能接某个 API”与“能充分释放这个模型的 Agent 能力”不是一回事。**

这也解释了为什么本培训要同时做模型 API 测试和 Harness 测试。

## 20.2 Session / Checkpoint / Resume

长任务不是一次调用。

需要区分：

- Session：一次持续工作的会话状态；
- Resume：恢复之前的会话；
- Checkpoint：对工作区或任务状态做可回滚快照；
- Rollback：出现错误时回到可靠状态。

这类机制决定 Agent 能否安全执行长任务，而不是失败后全部重来。

## 20.3 Context Compaction / Cache / Budget

Context Window 再大也不是无限资源。

Harness 需要管理：

- 历史压缩；
- Tool Result 截断；
- Summarization；
- Prompt Cache；
- 文件按需加载；
- Token Budget；
- 长任务 Context 污染。

要特别区分：

> **Context Compaction 是运行时上下文管理；Persistent Memory 是跨会话知识保存；Knowledge Retrieval 是按需找资料。**

三者不是一个概念。

## 20.4 Runtime / Execution Backend

Workspace 在哪里执行同样重要。

典型 Runtime：

- Local；
- Docker / Container；
- SSH Remote；
- Cloud Sandbox；
- Persistent Remote Workspace。

Hermes 当前就把 terminal backend 显式拆成 local、docker、ssh、Modal、Daytona、Vercel Sandbox、Singularity 等多种后端。

所以：

> **Agent Surface 在本地，不代表执行环境一定在本地。**

这对部门未来内网部署尤其重要。

## 20.5 Hooks / Events / Automation

Agent 除了“用户问一次、执行一次”，还可能被事件触发：

- Pre / Post Tool Hook；
- Git Hook；
- CI Event；
- Schedule / Cron；
- Webhook；
- Message Gateway；
- Background Job。

这类机制解决的是：

> **什么时候启动 Agent，以及执行前后还要触发什么确定性动作。**

不要把 Hook 和 Skill 混淆：

- Skill：任务应该怎么做；
- Hook：某个事件发生时必须触发什么。

## 20.6 Secrets / Credentials / Network Boundary

真实 Agent 会接触：

- API Key；
- SSH Key；
- Git Credential；
- Cloud Token；
- Database Credential。

所以还要讲：

- Secret 不进入 Prompt；
- 最小权限；
- 环境变量 / Secret Store；
- Credential Injection；
- Network Allowlist；
- Tool Scope；
- 审批。

这是企业内网落地不能省略的一层。

## 20.7 Observability / Trace / Audit

Agent 做了什么必须可追踪。

需要关注：

- Model Calls；
- Tool Calls；
- Token / Cost；
- Runtime；
- Error；
- Retry；
- Diff；
- Approval；
- Trajectory；
- Final Result。

因此：

> **Agent 工程不仅需要“会执行”，还需要可观测、可审计、可复现。**

FrontierHarness 这类 Benchmark 能成立，本身也依赖对 Agent trajectory、任务结果、成本和运行时间进行记录。

## 20.8 Thinking / Reasoning 不等于 Plan

这点培训必须主动纠偏。

Thinking / Reasoning 更接近：

> 模型在一次或多次推理过程里投入多少推理预算。

Plan / Todo / Task State 更接近：

> Agent 对外显式维护“任务分成哪些步骤、现在做到哪里”。

因此：

~~~text
Reasoning
≠
Plan
≠
Persistent Memory
~~~

三者分别属于模型推理、任务状态和跨会话状态。

---

# 二十一、最后用一张表建立统一认知

| 机制 | 要解决的问题 | 常见实现 |
|---|---|---|
| Model | 谁来推理 | GPT / Claude / Qwen / Gemini 等 |
| Identity | Agent 是谁、行为风格 | System Prompt / SOUL / Personality |
| Project Instructions | 项目中怎么工作 | AGENTS.md / CLAUDE.md / Rules |
| Workspace | 在哪里工作 | CWD / Repo / Files |
| Context | 当前知道什么 | History / File Read / Retrieval / Summary |
| Planning | 下一步做什么 | Plan / Todo / Task State |
| Memory | 跨会话记住什么 | MEMORY / Auto Memory / Memory Store |
| Native Tools | 如何执行本机任务 | File / Shell / Git / Test |
| MCP / API | 如何接外部能力 | MCP Server / REST / SDK |
| Skill | 如何复用方法 | SKILL.md / Workflow / Script |
| Browser Use | 如何操作 Web | Playwright / CDP / Browser Harness |
| Computer Use | 如何操作 GUI | Screenshot / Mouse / Keyboard |
| Permission | 能操作到什么范围 | Approval / Sandbox / Policy |
| Verification | 如何确认做对了 | Test / Browser QA / Logs / Diff |
| Sub-agent | 如何拆分复杂任务 | Delegation / Worker / Specialist |
| Provider Adapter | 如何接不同模型/协议 | Provider / Base URL / Wire Protocol / Routing |
| Session / Checkpoint | 如何持续与恢复长任务 | Resume / Snapshot / Rollback |
| Compaction | 如何控制长任务上下文 | Summary / Cache / Token Budget |
| Runtime | 在哪里真正执行 | Local / Docker / SSH / Cloud Sandbox |
| Automation | 什么事件触发任务 | Hook / Cron / Webhook / CI |
| Secrets | 如何安全取得凭据 | Env / Secret Store / Scoped Credential |
| Observability | 如何追踪和审计 | Trace / Tool Log / Cost / Diff / Trajectory |
| Surface | 人怎样使用 | CLI / GUI / IDE / Web |

---

# 二十二、培训中建议做的统一演示

不要拿 8 个 Agent 逐个点菜单。

推荐建立同一个最小 Repo：

~~~text
demo-project/
├── AGENTS.md
├── README.md
├── src/
├── tests/
└── docs/
~~~

然后分别让 Codex / Hermes / OpenCode 等做同一个任务：

> 修改一个小功能，运行测试，发现错误后修复，并说明遵守了哪些项目规则。

演示时重点观察：

1. 是否读取 Project Instructions；
2. Workspace 如何被读取；
3. 如何建立 Plan；
4. 调用了什么 Tool；
5. Tool Result 如何重新进入 Context；
6. 有没有验证；
7. 是否保存 Memory；
8. UI 是 CLI / GUI 还是 IDE；
9. 底层模型是否相同。

最终让学员看到：

> **工具名字在变，但 Agent 工作循环非常相似。**

---

# 二十三、这一章最后只留下六个结论

1. **Agent = Model + Harness，而不是只有模型。**
2. **AGENTS.md、CLAUDE.md、SOUL.md、MEMORY.md 是不同 Harness 对 Context / Identity / Memory 的具体实现，不要把文件名当成原理。**
3. **Workspace、Tools、Context Management 和 Verification 才是工程 Agent 真正工作的基础。**
4. **MCP 提供连接能力，Skill 沉淀使用能力的方法，两者解决的问题不同。**
5. **Browser Use 是 Web 交互能力，Computer Use 是更通用的 GUI 操作能力；结构化 Tool/API 通常应优先于视觉操作。**
6. **CLI / GUI / IDE 是不同交互入口，选择应由任务环境决定，而不是争论哪个“更高级”。**

---

# 二十四、参考资料

补充运行时与生命周期参考：

- OpenAI Agents architecture / state / compaction：https://developers.openai.com/api/docs/guides/agents
- Claude Code session resume / permission CLI：https://docs.anthropic.com/en/docs/claude-code/cli-usage
- Claude Code project/user memory：https://docs.anthropic.com/en/docs/claude-code/memory
- OpenCode permissions：https://opencode.ai/v2/docs/permissions
- Hermes Features / Checkpoints / Automation：https://hermes-agent.nousresearch.com/docs/user-guide/features/overview/
- Hermes Runtime / Terminal Backends：https://hermes-agent.nousresearch.com/docs/user-guide/configuration/


- OpenAI Codex AGENTS.md：
  - https://github.com/openai/codex/blob/main/codex-rs/models-manager/prompt.md
  - https://github.com/openai/openai-cookbook/blob/main/examples/codex/iterating-development-workflows-with-codex.md
- AGENTS.md open format：
  - https://agents.md/
- Hermes context / memory / personality：
  - https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/which-file-does-what.md
  - https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/memory.md
  - https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/personality.md
- Model Context Protocol：
  - https://modelcontextprotocol.io/
- OpenAI Skills：
  - https://developers.openai.com/plugins/concepts/skills
- OpenAI Computer Use：
  - https://developers.openai.com/api/docs/guides/tools-computer-use
- Browser Use：
  - https://github.com/browser-use/browser-use
