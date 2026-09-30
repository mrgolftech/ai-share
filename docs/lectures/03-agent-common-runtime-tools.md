# 第三讲：深入 Agent——掌握共性，而不是记住不同界面

> 状态：Final Lecture Draft v1.0  
> 日期：2026-09-30  
> 建议时长：100～120 分钟  
> 内容映射：原内容单元 4 + 5，并吸收“可复用资产”核心内容  
> 主线：**把不同 Agent 的 UI 拿掉，只看 Model、Harness、Context、Workspace、Tools、Runtime、Permission、Verification；然后回答怎样配置、怎样扩展、怎样放心使用多个 Agent。**

---

# 0. 为什么这一讲不叫“Codex 使用教程”或“ZCode 使用教程”

今天的 Agent 工具变化很快。

一个月前大家可能在讨论：

- Codex；
- Claude Code；
- OpenCode；
- Cline。

现在又可能出现：

- ZCode；
- Hermes；
- WorkBuddy；
- 新的 Desktop / Cloud Agent。

如果培训按照：

> 第 1 节 Codex 有哪些按钮  
> 第 2 节 ZCode 有哪些按钮  
> 第 3 节 Hermes 怎么设置

来组织，最大的问题不是内容太多，而是：

> **知识很快过期，而且换一个 Agent 又要重新学。**

所以这一讲换一个方法。

先不看产品名字。

先问：

> **一个 Agent 想真正完成任务，最少需要哪些东西？**

然后再拿不同产品去看：

> 它们分别把这些东西放在哪里、用什么方式实现。

本讲最终目标不是让大家记住某个工具，而是能够拿到一个没用过的 Agent，先问十个问题，就大致知道它能不能干活、缺什么、怎么配置。

---

# 1. 先把 Agent 拆开：真正稳定的是这套骨架

先给出统一结构：

```text
              User Goal
                 ↓
              Harness
     ┌───────────┼────────────┐
     ↓           ↓            ↓
Instructions   Context     Task / Plan
     │           │            │
     └───────────┼────────────┘
                 ↓
               Model
                 ↓
             Tool Request
                 ↓
        Tool Registry / Policy
        ┌────────┼─────────┐
        ↓        ↓         ↓
      File     Shell     Browser
        │        │         │
        └────────┼─────────┘
                 ↓
              Runtime
                 ↓
       Host / Repo / Server / Web
                 ↓
             Observation
                 ↓
             Verification
                 ↓
               Model
```

【图示占位 AGENT-01｜Agent Harness 总图】

这张图是第三讲最重要的一张图。

后面所有产品和概念都回到这张图。

可以先用一句接地气的话解释：

> **模型像“大脑”，Harness 像项目经理和调度员，Workspace 是工作台，Tools 是手和眼睛，Runtime 是实际工作环境，Test/Browser/Logs 是反馈。**

但要马上提醒：

> 这个类比只是帮助理解，实际系统中各层可能由同一个应用实现。

---

# 2. 什么是 Harness：为什么同一个模型放进不同 Agent，效果会不同

第一讲已经看到 Harness 会：

- 组织 Context；
- 调用模型；
- 提供 Tool；
- 执行 Tool；
- 把结果返回模型。

现在进一步看：

一个工程 Agent 的 Harness 往往还负责：

- System Instructions；
- Project Instructions；
- Workspace；
- Context Management；
- Plan / Task State；
- Memory；
- Tool Registry；
- Permission；
- Sandbox；
- Session / Resume；
- Context Compaction；
- Sub-agent；
- Observability；
- Runtime Backend。

这就解释了一个很重要的现象：

> **固定同一个模型，换 Harness，最终任务表现仍然可能变化。**

原因不一定是“哪个 Harness 更聪明”。

而可能是：

- 给模型的上下文不同；
- 搜索策略不同；
- 工具不同；
- Tool Schema 不同；
- 权限不同；
- Runtime 不同；
- 验证闭环不同。

【截图/图示占位 AGENT-02｜固定模型、不同 Harness 的受控对比】

这里不要做“排行榜”。

只说明：

> **模型是 Agent 能力的一部分，不是全部。**

---

# 3. 不同 Agent 先按“路线”看，不按产品表格背功能

可以选择当前实际会接触的几个工具：

- Codex；
- ZCode；
- OpenCode；
- Hermes；
- WorkBuddy。

课堂上不需要做几十列功能表。

把它们映射到几种使用形态：

## 3.1 CLI / Terminal-first

典型特点：

- 更接近 Shell；
- 容易脚本化；
- 与 Git、现有命令行工具结合自然；
- 适合工程师。

## 3.2 IDE / Code Workspace

典型特点：

- 编辑器和代码上下文更直接；
- 文件、Diff、Terminal、Browser 更集中。

## 3.3 Desktop GUI

典型特点：

- 上手门槛低；
- 配置、会话、文件和工具可视化。

## 3.4 Cloud Workspace / Chat Surface

看起来可能仍然像 Chat。

但背后已经可能有：

- Workspace；
- Cloud Runtime；
- Files；
- Skills；
- Browser；
- Artifact。

WorkBuddy 很适合用来说明这一点。

【截图占位 AGENT-WB-01｜WorkBuddy Chat / Task Surface】

【截图占位 AGENT-WB-02｜WorkBuddy Workspace / Artifact】

【截图占位 AGENT-WB-03｜WorkBuddy Skill / Community Ecosystem】

结论：

> **UI 是给人使用的入口，不是 Agent 能力的定义。**

---

# 4. 使用任何 Agent，先看第一件事：模型从哪里来？

一个 Agent 可能：

- 内置模型；
- 接 OpenAI-compatible API；
- 接 Anthropic；
- 接本地模型；
- 通过 Provider Adapter 接多个模型。

所以第一个检查问题是：

> **这个 Agent 怎样接 Model Provider？**

这和第一讲的 API 直接连起来。

例如内网模型如果提供 OpenAI-compatible API：

某些 Agent 可以直接配置：

- Base URL；
- API Key；
- Model ID。

但“能接上”只是第一步。

后面还要验证：

- Tool Calling；
- Streaming；
- Thinking；
- Context；
- Vision；
- Protocol compatibility。

所以：

> **Provider 配置成功 ≠ Agent 能力完整可用。**

【截图占位 AGENT-18｜某 Agent Provider / Model 配置界面】

如果后续对内网 Qwen 做固定模型跨 Harness 测试，这里放结果最合适。

---

# 5. Project Instructions：为什么每次都重新说规则会很累

假设每次进入一个项目都对 Agent 说：

> 不要改 canonical 数据。  
> 修改后一定测试。  
> GUI 不要重写业务逻辑。  
> 不要随便换技术栈。  
> 提交前看 Diff。

一次可以。

几十次以后：

- 容易漏；
- Prompt 越来越长；
- 新会话又要复制；
- 团队成员规则不一致。

因此很多 Agent 支持项目规则文件，例如：

- AGENTS.md；
- CLAUDE.md；
- 产品自己的 Project Instructions。

【截图占位 AGENT-03｜真实 BMQuiz / ai-share AGENTS.md + Agent 读取规则】

【录屏占位 AGENT-R04｜Agent 进入仓库后先读取 AGENTS.md，再执行任务】

用 BMQuiz 的真实规则举例：

> canonical 题库不能因为 UI 重构被改写。

> 未经架构决策不要随便换成另一个完整技术栈。

这比抽象解释“System Prompt”更容易理解。

结论：

> **长期成立的项目规则应该进入 Workspace，而不是每次靠人重新提醒。**

---

# 6. Workspace：Agent 在哪里工作？

Chat 通常处理：

> 用户发来的内容。

工程 Agent 还需要一个真实工作空间。

Workspace 里可能有：

- 代码；
- 文档；
- 配置；
- Git；
- 测试；
- 构建脚本；
- 图片；
- 数据。

【截图占位 AGENT-04｜Agent Workspace 文件树】

但必须纠正一个误解：

> Agent 有一个 Workspace，不等于模型每轮都把整个 Workspace 看了一遍。

实际更常见的是：

```text
Tree
→ Search
→ Read relevant files
→ Put selected content into Context
```

这和第二讲知识库本质上是相通的：

> 都是在大量信息里，选择这次真正需要的内容。

---

# 7. Context Management：Agent 为什么需要主动管理“它现在知道什么”

复杂工程会话越来越长以后，Context 会出现问题。

可能包含：

- 历史对话；
- 已读文件；
- Tool Result；
- Terminal 输出；
- Diff；
- Browser 截图；
- Plan；
- Error Log。

如果无限累积：

- Token 增长；
- 重点变弱；
- 响应变慢。

所以 Agent Harness 常见机制包括：

- selective read；
- summary；
- context compaction；
- cache；
- task state；
- resume。

这里把第二讲知识库的认识迁移过来：

> **Context 很长，不等于所有信息都应该常驻。**

【图示占位 AGENT-19｜Workspace ≠ Context：Search/Read → Selected Context】

---

# 8. Plan 和 Reasoning：两个概念不要混

Thinking / Reasoning 解决：

> 模型内部为了回答当前问题“想多少”。

Plan 解决：

> 一个长任务下一步准备做什么、哪些步骤已经完成。

例如：

```text
Goal：给 FileCheck 增加一个 GUI 功能
Plan：
1. Read requirements
2. Inspect core API
3. Design UI interaction
4. Implement
5. Unit test
6. GUI smoke
7. Build
```

这和模型内部推理不是一个东西。

【截图占位 AGENT-05｜真实 Agent Plan / Task State】

复杂任务使用 Plan 的价值是：

- 人可以 review；
- Agent 不容易忘记阶段；
- 中断后容易 resume；
- 更容易知道“还没做什么”。

---

# 9. Memory：不是把整个项目塞进“长期记忆”

Memory 很容易被过度神化。

先分三个东西：

## Session Context

当前会话正在看的内容。

## Project Files

项目事实。

例如：

- Architecture；
- AGENTS.md；
- README；
- code。

## Persistent Memory

跨会话希望保留的用户偏好或长期事实。

因此：

> 项目当前架构、测试结果、版本号，不应该只存在 Memory 里。

应该落到：

- Git；
- Docs；
- Test；
- Knowledge Base。

【截图占位 AGENT-06｜某 Agent Memory / Project Rules 对比】

这里直接回扣：

> **Memory 不是 Knowledge Base 的大号版本。**

---

# 10. Tools：模型有“手”，但谁真的在执行？

第一讲已经讲过 Tool Calling。

第三讲进一步看工程工具。

```text
Model
→ Tool Request
→ Harness
→ Execute
→ Tool Result
→ Model
```

【图示占位 TOOL-01｜Tool Loop】

这里引入一个非常重要的二层结构：

## Harness Capability

Agent 有没有 Shell Tool。

## Runtime Capability

Shell 里面有没有这个命令。

例如：

Agent 有 Terminal 工具。

但系统没有：

`git`

那么 Agent 还是不能 Git。

所以：

> **有 Tool 不等于环境里有能力。**

---

# 11. Runtime：为什么装好 Agent 以后还要准备一堆环境

这部分直接回答用户最常见的问题：

> Agent 都装好了，为什么还说缺 npm、Python、Playwright？

因为 Agent 的 Terminal 只是一个“执行入口”。

真正命令来自 Runtime。

典型研发环境需要：

- Git；
- Python；
- pip / uv；
- Node.js；
- npm / npx；
- curl；
- jq；
- Playwright；
- Chromium；
- Docker；
- SSH；
- ffmpeg。

【图示占位 ENV-01｜Harness vs Runtime】

【截图占位 ENV-02｜环境 Preflight 结果】

可以给出简单判断：

## Python 更擅长

- 数据处理；
- 脚本；
- 文件；
- 后端；
- 自动分析。

## Node.js 更擅长

- Web 项目；
- 前端工具链；
- npm CLI；
- Playwright 原生生态。

但核心原则不是：

> Agent 到底统一用 Python 还是 Node。

而是：

> **优先沿用项目原生技术栈和成熟工具。**

---

# 12. Local、WSL、Container、Cloud：Agent 到底运行在哪？

不同 Agent 可能运行在：

- Windows Host；
- WSL；
- Docker；
- Remote Server；
- Cloud Sandbox。

这直接影响：

- 能看到哪些文件；
- 能不能访问宿主机浏览器；
- 网络能到哪里；
- Docker 能不能用；
- 凭据在哪里；
- 安装了什么命令。

【图示占位 ENV-03｜Local / WSL / Docker / SSH / Cloud Runtime】

这时大家会理解：

> “这个 Agent 为什么找不到我的文件？”

很多时候不是模型问题。

而是：

> **Workspace / Runtime Boundary。**

---

# 13. File / Search / Read：Agent 接触项目的第一步通常不是“读全部代码”

真正工程 Agent 更常见的路径：

```text
tree / glob
→ grep / rg
→ read selected file
→ references
→ edit
```

【截图占位 TOOL-02｜Workspace：目录 + Search + Read】

这里可以现场用 ZCode / Codex 搜一个函数。

强调：

> 搜索不是低级能力，而是 Context 管理的重要部分。

Agent 不需要“记住整个仓库”，它需要：

> **会找。**

---

# 14. Shell：Agent 怎样复用已有工程工具

Shell 的意义不是：

> AI 会黑窗口。

而是让 Agent 可以调用人类工程师已经在用的工具：

```text
pytest
npm test
git
docker
curl
ffmpeg
build scripts
linters
```

【截图占位 TOOL-03｜Terminal Tool Call + 输出】

如果已经有：

`pytest`

就不要让模型自己写一套“测试解释器”。

如果已经有：

`ffmpeg`

就不要让模型重新实现视频编码。

结论：

> **Agent 的价值之一，是把现有工程工具组织起来。**

---

# 15. Git：为什么 Agent 尤其需要版本控制

人手工改三行代码，还可能记得自己改了什么。

Agent 一次可能改：

- 8 个文件；
- 500 行；
- 配置；
- 测试；
- 文档。

所以 Git 对 Agent 特别重要。

至少要看：

```text
git status
git diff
git log
```

【截图占位 TOOL-04｜git diff + test】

Git 在 Agent 工程中承担：

- 变更边界；
- Review；
- 回滚；
- 历史；
- 多 Agent 协作；
- CI 触发；
- 证据链。

一句话：

> **不要只相信 Agent 说“我改好了”，先看 Diff。**

---

# 16. Verification：Agent 说完成了，凭什么相信？

这是使用 Agent 最重要的习惯之一。

错误判断：

> 命令 exit code = 0，所以功能正确。

> Unit Test 过了，所以网页一定正常。

> 页面打开了，所以业务一定正确。

验证应该分层。

```text
Static Check
↓
Unit / Integration Test
↓
Runtime
↓
Browser / UI
↓
Business Semantics
```

【图示占位 TOOL-05｜四层验证】

BMQuiz：

> /api/health = 200 只证明服务活着。

还需要验证：

- 未登录受保护 API 是否 401；
- 旧 public path 是否 404；
- 登录；
- 练习；
- 同步。

model-metric：

> HTTP 200 也不等于 running/waiting/TPS 聚合语义正确。

所以：

> **验证要和需求对应。**

---

# 17. Browser：这里最容易混淆，必须一次讲清

很多产品都写：

> Browser。

但底层可能完全不同。

## 17.1 HTTP Fetch / Crawler

目标：

> 获取网页内容或数据。

不一定真的启动浏览器。

适合：

- 文档；
- 搜索；
- 数据抓取。

## 17.2 Browser Automation

通过：

- DOM；
- selector；
- accessibility；
- Playwright；
- CDP；

进行程序化操作。

适合：

- Web 测试；
- 表单；
- UI 验收；
- 页面交互。

## 17.3 Computer Use

模型看截图，然后：

- mouse；
- keyboard；
- GUI。

更通用，但通常：

- 更慢；
- 更依赖 Vision；
- 更难稳定断言。

【图示占位 TOOL-06｜Crawler / Browser Automation / Computer Use 对比】

---

# 18. Playwright 和 CDP 到底什么关系？

这部分尽量说人话。

CDP：

> **Chromium 暴露的一套底层调试和控制协议。**

Playwright：

> **面向浏览器自动化任务的更高层工具和 API。**

所以 Playwright 不能简单说成：

> “CDP 套了一层壳”。

因为它还负责：

- browser abstraction；
- locator；
- wait；
- context；
- downloads；
- network；
- assertions；
- cross-browser。

但对于 Chromium：

> 底层确实可能通过浏览器协议完成很多控制。

【图示占位 TOOL-06B｜Browser Tool → Playwright → CDP → Chromium】

---

# 19. 内置 Browser、宿主机 Chrome、Computer Use 不是一回事

一个 Agent 可能有自己的云端 Browser。

此时它操作的是：

> Agent Runtime 里的浏览器。

如果要操作宿主机已经登录的 Chrome：

就需要额外桥接方式，例如：

- Extension；
- Remote Debugging / CDP；
- Host-side Browser Tool。

【图示占位 TOOL-06A｜Built-in Browser vs Host Chrome vs Computer Use】

这能解释一个现实问题：

> Agent 明明“有 Browser”，为什么看不到我宿主机浏览器里已经登录的网站？

因为它们根本不是同一个 Browser Runtime。

---

# 20. 浏览器案例：不要只演示“帮我搜一下”

真正有价值的 Demo：

> 修改页面以后，Agent 自己打开网页验收。

流程：

```text
Implement
→ Start App
→ Browser
→ Interact
→ Console
→ Screenshot
→ Observe
→ Fix
→ Re-run
```

【截图占位 TOOL-07｜修改前 / Browser Console / 修改后 Screenshot】

【录屏占位 TOOL-R02｜一次 Browser Visual QA 闭环】

这才体现 Browser 对工程 Agent 的价值。

---

# 21. SSH：Agent 怎样从本地进入服务器

SSH 本身不是 AI 能力。

它只是已有远程管理工具。

Agent 的优势是：

> 能把 SSH 纳入任务闭环。

例如：

```text
Goal
→ Read deploy docs
→ SSH
→ Observe
→ Act
→ Logs
→ Health
→ Verify
```

【截图占位 TOOL-08｜SSH + Docker / systemd + logs + health】

服务器案例使用：

- BMQuiz Docker；
- model-metric systemd。

【录屏占位 TOOL-R03｜一次远端部署/检查闭环】

重点不是炫命令。

而是：

> **Agent 进入生产/测试环境以前，必须先有目标、规则、权限和验证方法。**

---

# 22. API、Tool、MCP、Skill：用一个问题讲清

现在假设部门有一个内部系统：

`GET /api/service/status`

## 22.1 API

它解决：

> 程序怎么调用这个系统。

API 原本不是为了 AI 发明的。

## 22.2 Tool

Agent Harness 可以把它包装成：

`get_service_status()`

模型看到的是一个“可调用动作”。

所以：

> **Tool 不一定等于一个 API Endpoint。**

一个好的 Tool 可以组合多个底层 API，围绕任务设计。

## 22.3 MCP

如果不同 AI Host 都需要接这个能力：

可以通过 MCP Server 以统一方式提供。

```text
Codex / ZCode / Other Host
         ↕
        MCP
         ↕
      MCP Server
         ↓
   API / DB / System
```

【图示占位 CONNECT-01～03｜API / Tool / MCP 分层】

MCP 解决：

> **AI Host 和外部能力之间怎样形成相对标准的连接方式。**

它不替代底层 API。

## 22.4 Skill

有了 Tool，Agent 知道：

> 能做什么。

但未必知道：

> 一个完整故障排查应该按什么流程做。

这时 Skill 可以写：

```text
Trigger
→ Check status
→ Read metrics
→ Inspect logs
→ Compare threshold
→ Produce evidence
→ Verification
```

Skill 解决：

> **把成功的工作方法变成可重复流程。**

【截图占位 CONNECT-06｜Raw API → Tool → MCP → Skill 完整分层】

---

# 23. Raw API → MCP → Skill：第三讲核心 Demo

同一个训练服务。

不要换三个系统。

## 第一轮：Raw API

手工：

`curl /api/status`

让大家看到底层能力。

## 第二轮：MCP Tool

在 Agent 中出现：

`get_status`

Agent 自动调用。

## 第三轮：Skill + MCP

任务：

> 做一次完整服务健康检查并生成结论。

Skill 指导 Agent：

- 哪些 Tool；
- 什么顺序；
- 成功标准；
- 异常怎么办。

【录屏占位 CONNECT-R01｜Raw API】

【录屏占位 CONNECT-R02｜MCP Tool】

【录屏占位 CONNECT-R03｜Skill + MCP】

这个 Demo 的核心不是：

> MCP 很高级。

而是让大家看出三层各自解决什么问题。

---

# 24. Permission / Sandbox：能做，不等于应该直接做

一个 Agent 有 Shell 后，可以：

- 读文件；
- 改文件；
- 删除文件；
- 网络访问；
- SSH；
- 执行命令。

所以权限应该分层。

例如：

## 通常低风险

- Read；
- Search；
- git diff；
- logs；
- health。

## 更高风险

- Edit；
- install dependency；
- network write；
- restart。

## 需要严格控制

- delete；
- production deploy；
- migration；
- secret；
- destructive command。

【截图占位 AGENT-12｜Approval / Sandbox】

【录屏占位 AGENT-R09｜高风险动作触发 Approval】

重要结论：

> **Skill 不是安全边界。**

Skill 可以写：

> “先确认再删除”。

但真正安全还需要：

- OS 权限；
- Tool Permission；
- Sandbox；
- Credential Scope；
- Approval。

---

# 25. Secrets：不要为了 Agent 方便，把凭据写进 Prompt

需要让 Agent 使用：

- API Key；
- SSH Credential；
- Token；

不意味着应该把这些写进：

- AGENTS.md；
- Skill；
- Git；
- 长 Prompt。

应该使用：

- Environment；
- Secret Store；
- Credential Manager；
- scoped token。

这也是“Agent Runtime 工程”的一部分。

---

# 26. 可复用资产：为什么一次成功任务不应该只留在聊天记录

使用 Agent 一段时间以后，会出现大量“已经做过一次”的经验。

例如：

> 部署前先备份数据库。

> UI 修改必须跑 Visual QA。

> 这个项目的 canonical 数据不能改。

如果这些只存在历史 Chat 中：

- 新会话找不到；
- 新人不知道；
- 换 Agent 也带不过去。

所以需要资产化。

可以用“生命周期”来判断放哪里。

```text
一次性临时要求
→ Prompt

项目长期规则
→ AGENTS.md / Project Rules

复杂任务阶段计划
→ Plan

重复工作方法
→ Skill

确定性步骤
→ Script

成功标准
→ Test / Eval

持续门禁
→ CI

外部事实
→ Knowledge / Docs

为什么这么设计
→ ADR / Architecture

历史和变更
→ Git
```

【图示占位 ASSET-02｜资产路由表】

---

# 27. 不要走到另一个极端：什么都做成 Skill

资产越多也不一定越好。

如果一个命令：

`npm test`

已经足够清楚。

没有必要再创建：

> “超级测试 Skill”。

如果只有一次任务：

> 临时转换 3 个 CSV。

也未必需要永久资产。

判断五问：

1. 会不会重复？
2. 是否容易忘？
3. 是否有明确成功标准？
4. 是否需要团队共享？
5. 是否值得从 Context 中移出去按需加载？

【录屏占位 ASSET-R01｜一个工作经验应该放 Prompt/Rules/Skill/Script/Test 哪】

---

# 28. 一个最典型的资产升级过程

可以使用本培训自己的 Qwen API 工作作为案例。

最开始：

> 手工 curl。

然后：

> Python 测试脚本。

再然后：

> 每次请求/响应/状态/耗时自动落盘。

再然后：

> manifest + summary + report。

再然后：

> model-metric。

这说明：

```text
一次测试
→ Script
→ Repeatable Test
→ Evidence
→ Report
→ Monitoring
```

资产不是为了“文件更多”。

而是：

> **减少下一次工作的重复判断和重复劳动。**

【截图占位 ASSET-01｜ai-share 当前资产地图】

---

# 29. 到这里，再拿五个 Agent 看一次

第三讲接近结束时，再回到产品。

不要问：

> 哪个最好？

统一问十个问题。

```text
1. Model 怎么接？
2. Context 怎么管？
3. Workspace 在哪？
4. Project Rules 怎么写？
5. Shell 有没有？
6. Browser 什么机制？
7. MCP / Tool 怎么扩？
8. Runtime 缺什么？
9. Permission 怎么控？
10. Verification 怎么做？
```

【图示占位 AGENT-20｜多 Agent 十问检查表】

用 Codex、ZCode、Hermes、OpenCode、WorkBuddy 各选 2～3 张关键截图放在同一页。

学员如果能拿这十个问题去看一个新工具，本讲目标就达到了。

---

# 30. 第三讲最后留下八句话

1. **Agent 的 UI 会变，Harness 的核心问题相对稳定。**
2. **同一个模型放进不同 Harness，能力表现可以不同。**
3. **Workspace 很大，但模型每轮真正使用的是被选入 Context 的内容。**
4. **Tool 是执行入口，Runtime 决定这个入口背后到底有没有能力。**
5. **Browser Automation、Computer Use、Crawler 解决的是不同问题。**
6. **API 是系统接口，MCP 是 AI Host 的连接方式，Skill 是可复用工作方法。**
7. **Permission / Sandbox / Credential 才是安全边界，Skill 不是。**
8. **真正值得团队积累的是 Rules、Skill、Script、Test、CI、Knowledge 和 Git，而不是某个 Agent 的按钮位置。**

下一讲不再继续增加大量 Agent 概念。

而是问：

> **这些机制放进一个真实项目以后，Agent 到底怎样从需求一直走到发布和部署？**

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

# 34. 第三讲给学员的“一页带走卡”

最后可以直接给一张卡：

## 拿到一个新的 Agent，我先问

```text
Model：接什么模型？
Context：模型这一轮能看到什么？
Workspace：在哪工作？
Rules：长期约束放哪？
Tools：能调用什么？
Runtime：环境里真正装了什么？
Browser：是 DOM/CDP/Playwright 还是 Vision？
External：API/MCP 怎么接？
Permission：什么动作需要批准？
Verify：它怎么证明做对了？
```

这张卡比“某 Agent 30 个功能点”更值得保留。
