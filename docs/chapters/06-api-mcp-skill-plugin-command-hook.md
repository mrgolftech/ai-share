# 模块四：如何让 Agent 掌握工具——API、Tool、MCP、Skill、Plugin、Command、Hook

> 状态：已有初稿 / 待统一 Demo 与实测  
> 更新日期：2026-09-30  
> 上一章：`05-agent-tools-real-world.md`  
> 对应培训主线：**Agent 如何操作真实世界 → 如何让 Agent 掌握工具 → 如何形成可复用资产**

---

## 0. 这一章要解决的不是“背名词”

上一章已经说明：

> Agent 通过工具读取和改变真实世界。

但工程人员很快会遇到一堆术语：

- API；
- Tool / Function Calling；
- MCP；
- Skill；
- Plugin；
- Command；
- Hook。

如果只背定义，很容易出现：

> “既然有 API，为什么还需要 MCP？”  
> “既然 MCP 已经能调用工具，为什么还要 Skill？”  
> “Skill 是不是把 API 包一层？”  
> “Plugin 和 MCP 是不是一回事？”  
> “Command 和 Skill 为什么都能触发一段流程？”  
> “Hook 又放在哪里？”

这一章采用一个统一问题来拆：

> **一个外部能力，怎样从“系统本身能做”一步步变成“Agent 能稳定使用，并能被团队复用”？**



## 0.1 第一套连续案例仍然使用 ZCode

模块三已经用 ZCode 建立了：

```text
Workspace → File → Terminal → Browser → Test → Review
```

本章不立即更换 Agent，而是继续用同一个 ZCode Workspace 回答：

> **这些外部能力怎样从“系统接口”一步步变成“Agent 可调用、可复用、可分发的能力”？**

统一演示链：

```text
Training Service
→ curl / Raw API
→ ZCode MCP Tool
→ ZCode Skill + MCP
→ ZCode Command
→ ZCode Plugin（扩展）
→ Hook（扩展）
```

这样课堂控制变量更清楚：

> **后端能力不变，只改变 Agent 的接入层和复用层。**

详细实施方案：

`demos/agent-tool-integration/zcode-implementation-plan.md`

当前 ZCode 官方已经支持：

- User / Workspace MCP；
- stdio / HTTP / SSE MCP；
- `SKILL.md` Skills；
- `/` Commands；
- Plugin 打包 Skills / Commands / Subagents / MCP / Hooks。

这些是当前 ZCode 产品事实；本章要抽象的仍然是 API / Tool / MCP / Skill / Plugin / Trigger 的通用关系。


---

# 1. 先用一张分层图建立直觉

建议课堂第一张图：

```text
┌──────────────────────────────────────────────┐
│  用户目标 / 工程任务                          │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│ Skill / Workflow                             │
│ 什么时候用？按什么顺序？失败怎么办？          │
│ 输出格式是什么？怎样验证？                    │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│ Agent-visible Tools                          │
│ search_repo / get_file / create_issue ...    │
└──────────────────────────────────────────────┘
          ↓                         ↓
┌───────────────────┐      ┌───────────────────┐
│ MCP Server        │      │ Local Tool/Shell  │
│ expose/discover   │      │ script / CLI      │
└───────────────────┘      └───────────────────┘
          ↓
┌──────────────────────────────────────────────┐
│ API / Service / Database / Existing System   │
└──────────────────────────────────────────────┘
```

Plugin 可以横向看：

```text
Plugin
├─ Skills
├─ MCP configuration/server
├─ optional UI
└─ optional lifecycle hooks
```

Command / Hook 则属于“怎样触发”：

```text
Command：用户主动触发
Hook：生命周期事件触发
```

**图示占位：CONNECT-01 七个概念分层总图**

---

# 2. API：系统本身暴露的程序接口

## 2.1 API 先解决“程序怎么调用系统”

第一章已经用模型 API 讲过：

```http
POST /v1/chat/completions
```

API 的核心是约定：

- Endpoint；
- Method；
- Authentication；
- Input；
- Output；
- Error；
- Version。

它可以服务于任何程序，不要求调用方一定是 Agent。

例如 GitHub、监控平台、CI、自研业务系统都可以先有自己的 API。

因此：

> **API 是系统能力接口，不是 Agent 专属概念。**

---

## 2.2 API 不是“最底层”的绝对说法

培训中不要把 API 机械说成所有能力的最底层。

因为 Agent Tool 也可能直接调用：

- 本地文件；
- Shell；
- 数据库驱动；
- SDK；
- 系统调用。

更准确的是：

> **当外部系统已经有稳定 API 时，API 往往是最适合被工具层复用的能力接口。**

---

# 3. Tool / Function Calling：模型真正看到的“可调用动作”

这是 API 和 MCP 之间最容易漏掉的一层。

模型通常不会直接读完一份几百页 REST API 文档再自己拼 URL。

Harness 更常给模型一组结构化工具：

```text
get_project(project_id)
search_code(query)
create_issue(title, body)
restart_service(service)
```

每个 Tool 至少需要：

- 名称；
- 描述；
- 输入参数；
- 返回结果。

模型要做的是：

> **判断什么时候调用哪个 Tool，并生成参数。**

---

## 3.1 Tool 和 API 不是同一个东西

例如：

```text
Tool:
create_issue(title, body)
        ↓
Implementation:
POST https://api.github.com/repos/.../issues
```

Agent 看见的是业务动作：

> create_issue

实现内部可以调用 GitHub REST API。

因此：

> **API 是系统接口；Tool 是面向 Agent 暴露的可调用动作。**

一个 Tool 可以：

- 包装一个 API；
- 组合多个 API；
- 调用本地脚本；
- 调数据库；
- 调 CLI。

---

## 3.2 为什么 Tool 不应该机械镜像所有 API

如果一个系统有 500 个 API，就给模型 500 个原样 Tool，未必是好设计。

当前 OpenAI Plugin 工具设计官方文档也明确建议：

> Tool 应围绕用户目标组织，而不是简单镜像内部 API。

比如：

差的设计：

```text
GET /v1/project/{id}
PATCH /v1/project/{id}
POST /v1/project/{id}/status
...
```

更适合 Agent 的 Tool Surface 可能是：

```text
get_project
update_project
publish_project
```

原则：

> **Tool Schema 是给模型使用的“能力界面”，需要围绕任务设计。**

**图示占位：CONNECT-02 REST API → Agent Tool 映射**

---

# 4. Function Calling 与 MCP：不要混为一谈

Function / Tool Calling 解决的是：

> **模型怎样结构化表达“我要调用某个工具”。**

MCP 解决的是：

> **AI Host 怎样以一种开放协议连接外部 Tool / Resource / Prompt Provider。**

可以粗略表示：

```text
Model
  ↓ function/tool call
Agent Harness / MCP Host
  ↓ MCP protocol
MCP Server
  ↓
API / DB / Service
```

所以：

> **Function Calling 是模型—Harness 之间的调用机制；MCP 是 Host—外部能力提供方之间的连接协议。**

二者可以同时存在，不是二选一。

---

# 5. MCP：为什么已有 API 还需要它

## 5.1 没有 MCP 时

假设有 5 个 Agent、10 个企业系统。

每个 Agent 都可能要分别解决：

- 系统怎么连接；
- Tool Schema 怎么定义；
- 怎么发现工具；
- 返回值怎么表达；
- 认证怎么接；
- 生命周期怎么管理。

很容易形成：

```text
Agent A → Integration A1/A2/A3...
Agent B → Integration B1/B2/B3...
Agent C → Integration C1/C2/C3...
```

---

## 5.2 MCP 想标准化的是“AI 应用怎样连接能力”

MCP 官方当前将自己定义为：

> 连接 AI 应用与数据、工具所在系统的开放标准。

MCP Server 可以暴露：

- Tools；
- Resources；
- Prompts。

Agent Host / Client 通过协议连接。

因此：

```text
Existing Service / API
        ↓
     MCP Server
        ↓
   MCP-compatible Host
        ↓
      Model
```

MCP 的价值重点不在“把 HTTP 发明一遍”，而是：

> **给 AI Host 与外部能力之间建立统一的发现、描述和调用约定。**

---

## 5.3 MCP 不是 API 的替代品

常见情况：

```text
企业业务系统
     ↓ REST API
MCP Server
     ↓ MCP
Agent / IDE / Chat
```

MCP Server 内部仍然可能调用原来的：

- REST；
- GraphQL；
- SDK；
- Database；
- CLI。

所以一句话：

> **API 负责系统能力；MCP 负责把能力以 Agent 友好的标准接口暴露出去。**

**图示占位：CONNECT-03 API 与 MCP 非替代关系**

---

# 6. MCP 的 Tools / Resources / Prompts 怎么理解

## 6.1 Tools

Tools 更接近：

> **模型可以发起的动作。**

例如：

- search_issues；
- create_ticket；
- restart_service。

一般涉及参数和执行结果。

---

## 6.2 Resources

Resources 更接近：

> **Host / Model 可以读取的内容。**

例如：

- 文档；
- Schema；
- 配置；
- 数据对象。

它不一定对应一次“动作”。

---

## 6.3 Prompts

Prompts 是：

> **Server 暴露的可复用 Prompt 模板。**

培训中不需要让学员背 MCP Spec，而是建立：

```text
Tool = 做事
Resource = 读东西
Prompt = 复用交互模板
```

并明确：

> 具体 Host 对三类能力的支持范围可能不同，现场要以当前产品实现为准。

---

# 7. Skill：不是“另一个 API”，而是可复用工作方法

这是本章最重要的区分之一。

当前 OpenAI 官方 Skills 文档给出的定义非常适合教学：

> Skill 是带有 `SKILL.md` 的目录，可以包含 instructions、references、scripts、assets，用于教 Agent 完成可重复工作流。

典型结构：

```text
review-release/
├── SKILL.md
├── references/
│   └── release-policy.md
├── scripts/
│   └── check_version.py
└── assets/
    └── report-template.md
```

---

## 7.1 一个 Skill 应该回答什么

不是：

> “系统有哪些接口？”

而是：

- 什么情况下使用；
- 输入是什么；
- 第一步做什么；
- 下一步怎么判断；
- 需要哪些工具；
- 失败怎么办；
- 哪些事实不能猜；
- 验证标准；
- 输出格式。

所以：

> **Tool 更像“手”；Skill 更像“做事的方法”。**

---

# 8. 为什么有 MCP 还需要 Skill

假设 GitHub MCP 已经提供：

- get_file；
- list_commits；
- create_issue；
- create_pr；
- get_workflow_run。

这说明 Agent **能做什么**。

但“如何完成一次规范项目验收”仍然没有定义。

Skill 可以规定：

```text
1. 读取 AGENTS.md
2. 确认 main / SHA / clean tree
3. 安装依赖
4. 运行 unit test
5. 启动服务
6. Browser Visual QA
7. 修复
8. 再测试
9. git diff review
10. commit / push
11. 检查 CI
12. 生成验收报告
```

所以最适合课堂的一句话是：

> **MCP 告诉 Agent“有哪些受控能力”；Skill 教 Agent“怎样把能力组合成可靠流程”。**

OpenAI 当前官方文档也明确写出这个边界：

- MCP Server：live data、authentication、authorization、controlled actions；
- Skill：tool sequence、decision points、output requirements、templates 等 workflow guidance。 

**图示占位：CONNECT-04 MCP Tools vs Skill Workflow**

---

# 9. Skill 里为什么还可以放 Script

这点很容易误解：

> Skill 不是只有 Prompt。

当前 Skill 结构允许：

- references；
- scripts；
- assets。

原因是：

> **确定性的工作不应该每次让模型重新“想一遍”。**

例如：

```text
模型判断：需要检查版本号
    ↓
Skill 规定：运行 check_version.py
    ↓
脚本稳定计算
    ↓
结果回给模型做后续判断
```

这与整个培训的工程原则一致：

> **模型负责不确定性判断，代码负责可重复执行。**

---

# 10. Plugin：这是“打包与分发边界”，而且强产品相关

培训中不能把 Plugin 讲成一个行业唯一标准定义。

不同产品历史上对 Plugin 的含义不同。

因此分两层讲。

---

## 10.1 通用直觉

Plugin 通常解决：

> **怎样把一组扩展能力打包、安装、启用和分发。**

它可能包含：

- Tools；
- MCP；
- Skills；
- UI；
- Hooks；
- 配置；
- 资源。

---

## 10.2 2026 年 OpenAI 当前实现

当前 OpenAI 官方 Plugin Architecture 明确：

```text
Plugin
├── Skills
└── MCP server (optional)
    ├── Tools / structured results
    └── UI resources (optional)
```

并支持 lifecycle hooks。

也就是说，在当前 OpenAI 体系里：

> **Plugin 是安装/发布包；Skill 和 MCP 是 Plugin 可以包含的能力组成。**

这非常适合拿来说明：

> Plugin ≠ MCP，Plugin ≠ Skill。

但必须在 PPT 上标注：

> **“以下是 OpenAI 当前实现，不代表所有产品都使用同一 Plugin 定义。”**

**图示占位：CONNECT-05 OpenAI 当前 Plugin Package 结构**

---

# 11. Command：把高频行为变成“用户主动入口”

不同 Harness 对 Command 的实现差异很大。

教学只保留稳定抽象：

> **Command 通常是用户主动触发的一段预定义行为或 Prompt/Workflow 入口。**

例如：

```text
/review
/test
/release
```

它解决的是：

> “我怎样快速启动一个标准动作？”

---

## 11.1 Command 和 Skill 的区别

可以用：

```text
Command 更偏入口
Skill 更偏能力/方法
```

例如：

```text
/release
   ↓
触发 release Skill
   ↓
读取版本规则
→ 测试
→ 构建
→ Tag
→ Release
```

但不同产品可能：

- Command 本身就是一段 Markdown Prompt；
- Command 被转换为 Skill；
- Skill 可以自动触发而不需要 slash command。

OpenAI 当前“迁移 Claude Code plugin”官方文档甚至建议把可复用的 `commands/` 行为转换为 Skills。

这说明：

> **Command 不是一个跨产品稳定的核心能力层；它更多是 Surface / Trigger 设计。**

---

# 12. Hook：不是“让用户点一下”，而是事件发生时自动执行

Hook 的核心是：

> **事件驱动。**

例如：

```text
SessionStart
→ 加载项目上下文

BeforeToolUse
→ 检查命令是否允许

AfterToolUse
→ 记录日志

BeforeCommit
→ 运行格式化/测试
```

当前 OpenAI Plugin / Codex 文档也已经支持 lifecycle hooks，并要求执行环境中实际存在对应脚本，同时强调信任/审批。

---

## 12.1 Hook 和 Command 的区别

最简洁的教学对比：

| 概念 | 谁触发 | 典型用途 |
|---|---|---|
| Command | 用户主动 | /review、/release |
| Hook | 生命周期事件 | 工具前检查、SessionStart、自动格式化 |

所以：

> **Command 是“我要做”；Hook 是“发生某事时自动做”。**

---

# 13. API、MCP、Skill、Plugin、Command、Hook 放在一个例子里

假设部门有一个“设备管理平台”。

---

## 13.1 系统已有 API

```http
GET /devices/{id}
POST /devices/{id}/restart
GET /devices/{id}/logs
```

这是平台自身程序接口。

---

## 13.2 封装成 Agent Tools

```text
get_device
restart_device
get_device_logs
```

Tool 命名和参数围绕 Agent 任务设计。

---

## 13.3 用 MCP 暴露

```text
Device Platform API
       ↓
Device MCP Server
       ↓
Tools:
get_device
restart_device
get_device_logs
```

这样多个支持 MCP 的 Agent Host 可以连接。

---

## 13.4 做一个故障排查 Skill

`device-troubleshoot/SKILL.md`：

```text
1. 读取设备状态
2. 判断是否在线
3. 如果异常先取日志
4. 不允许直接重启关键生产设备
5. 给出候选原因
6. 获得批准后才执行 restart
7. 重启后重新读取状态
8. 输出前后对比和证据
```

这变成可复用工程流程。

---

## 13.5 打包成 Plugin

Plugin 可以把：

- Skill；
- MCP Server 配置；
- 可能的 UI；
- Hooks；

打在一起供安装。

---

## 13.6 Command

用户输入：

```text
/troubleshoot DEVICE-001
```

作为显式入口。

---

## 13.7 Hook

每次调用 `restart_device` 前：

```text
BeforeToolUse
→ 检查设备标签
→ 如果 production 则强制人工审批
```

这样七个概念就不再是孤立定义。

**图示占位：CONNECT-06 设备管理端到端示例**

---

# 14. API vs MCP：什么时候直接用 API 就够了

并不是所有系统都应该先做 MCP。

直接 API / SDK 可能更合适：

- 只有一个固定程序调用；
- 不需要多个 Agent Host 复用；
- 已有成熟内部 SDK；
- 接口数量很少；
- 任务逻辑非常确定；
- 安全边界由现有服务完成。

例如一个确定性脚本：

```text
每天 01:00 调接口拉报表
→ 处理 CSV
→ 写数据库
```

可能根本不需要 Agent，更不需要 MCP。

---

# 15. 什么时候值得做 MCP

更适合考虑 MCP 的场景：

- 同一套能力要给多个 Agent / IDE / Chat Surface 使用；
- 希望标准化 Tool Discovery；
- 需要受控地暴露一部分能力，而不是整个内部 API；
- 希望把认证、授权、Tool Schema 放在 Server 侧；
- 需要独立演进 Tool Provider；
- 外部系统能力经常被 Agent 组合使用。

判断不是：

> “MCP 很火，所以要做。”

而是：

> **是否真的存在多 Host 复用和 Agent Tool Integration 的需求。**

---

# 16. 什么时候值得做 Skill

适合 Skill 的典型任务：

- 有固定步骤但仍需要判断；
- 经常重复；
- 需要组织多个 Tool；
- 有明确验收标准；
- 有团队规则；
- 需要模板化输出；
- 失败处理有经验可沉淀。

例如：

- API 验收；
- Web UI QA；
- Release；
- 服务器部署检查；
- 技术调研；
- 文档审查。

不适合为了形式把：

> “运行 pytest”

单独做成复杂 Skill。

如果一个 Shell Script 已经稳定完成，就保留 Script 即可。

---

# 17. 一个重要边界：Skill 不是安全边界

Skill 里的文字可以规定：

> 不要执行危险命令。

但真正的安全控制应该落在：

- Tool permissions；
- MCP Server authorization；
- Sandbox；
- Approval；
- Credential scopes；
- Hook policy；
- OS / Container / Network boundary。

所以：

> **Skill 可以教模型守规则，但不能替代系统级权限控制。**

这对企业 Agent 非常重要。

---

# 18. MCP Tool 的设计原则

结合官方当前 Tool Design 指引，本培训建议至少检查：

## 18.1 名称围绕任务

好：

```text
get_build_status
restart_test_service
create_release_note
```

差：

```text
api_v2_post_37
do_action
misc
```

---

## 18.2 描述要让模型知道“什么时候用”

Tool Description 是模型路由工具的重要 Context。

需要写：

- 作用；
- 适用条件；
- 输入；
- 风险；
- 返回。

---

## 18.3 Read / Write / Dangerous Action 尽量分开

例如：

```text
get_device_status
restart_device
delete_device
```

不要塞进一个：

```text
device_action(action=...)
```

然后给所有动作同样权限。

工具边界应该帮助：

- 最小授权；
- 审批；
- 审计；
- 错误处理。

---

## 18.4 返回结果不要无限大

Tool Result 会进入 Agent Context。

因此返回：

- 必要字段；
- 摘要；
- Pagination；
- 可继续 fetch 的 ID；

通常比把几 MB 原始数据直接回灌更好。

这与前面的 Context Budget 思想一致。

---

# 19. Skill 的设计原则

## 19.1 先写 Trigger，再写步骤

Skill 的 description 决定 Agent 什么时候考虑使用。

要写清：

> 这个 Skill 解决什么用户目标，什么时候应该触发。

---

## 19.2 不要把所有规则塞进一个超级 Skill

更好的拆法：

```text
api-acceptance
web-ui-qa
release
incident-triage
```

而不是：

```text
engineering-everything
```

---

## 19.3 Script 只承接确定性步骤

例如：

- 版本号解析；
- JSON Schema 校验；
- 报表转换；
- 文件批处理。

不要把复杂判断重新硬编码到 Script，然后让 Skill 只是一个壳。

---

## 19.4 写清成功标准

Skill 最容易缺的是：

> 到什么程度才算完成？

例如 API 验收：

```text
- Endpoint list complete
- Happy path pass
- Error path checked
- Streaming checked
- Tool loop checked
- Evidence saved
- Report generated
```

---

# 20. 本培训应该做什么 Skill Demo

不建议 Hello World。

建议直接做：

> **工程项目验收 Skill**

名称暂定：

```text
project-acceptance
```

它至少包含：

```text
skills/project-acceptance/
├── SKILL.md
├── references/
│   └── acceptance-checklist.md
├── scripts/
│   └── collect_git_state.py
└── assets/
    └── acceptance-report-template.md
```

流程：

```text
Read AGENTS.md
→ Capture Branch/SHA
→ Install/Check Environment
→ Unit Test
→ Build
→ Start App
→ Browser QA
→ Git Diff
→ Optional Push
→ CI
→ Acceptance Report
```

这能直接承接上一章全部内容。

**截图占位：CONNECT-07 project-acceptance Skill 目录**

---

# 21. MCP Demo 应该怎么设计

第一套正式实现固定使用 **ZCode 作为 MCP Host**，具体步骤见：

`demos/agent-tool-integration/zcode-implementation-plan.md`

为了让学员真正看懂“API 与 MCP 的关系”，不要只展示一个现成 MCP 列表。

统一 Demo：

```text
同一个“查询服务状态”能力

A. curl / REST API
B. Agent Tool via MCP
C. Skill 调用 MCP Tool 并生成验收结论
```

三次使用同一个后端能力。

学员会直观看到：

```text
API = 原始系统接口
MCP Tool = Agent 可发现/调用的动作
Skill = 多步任务方法
```

对应录屏：

- CONNECT-R01：Raw API；
- CONNECT-R02：MCP Tool；
- CONNECT-R03：Skill + MCP。

---

# 22. 一张最终决策表

| 我现在缺什么 | 优先考虑 |
|---|---|
| 系统还没有程序接口 | API / CLI / SDK |
| 模型需要一个明确动作 | Tool |
| 多个 AI Host 要复用外部 Tool/Data | MCP |
| Agent 经常重复一套多步骤方法 | Skill |
| 要安装/分发一组 Skills/MCP/UI/Hooks | Plugin（按具体产品定义） |
| 用户需要快速主动触发标准行为 | Command |
| 生命周期事件发生时要自动执行 | Hook |
| 完全确定、无需模型判断 | Script / CI / Automation |

最重要的一行是最后一行：

> **不要把本来应该写成程序的确定性任务，强行做成 Agent。**

---

# 23. 课堂节奏建议

## 第一段：概念冲突

先问：

> 有 API 了，为什么还需要 MCP？

用 CONNECT-01 / CONNECT-03。

---

## 第二段：Tool 与 MCP

展示同一个系统：

```text
REST API → Tool → MCP Server → Agent
```

让学员看到“不是替代，是分层”。

---

## 第三段：MCP 与 Skill

直接展示：

```text
GitHub Tools
vs
项目验收 Skill
```

说明“能做什么”与“怎么做”的区别。

---

## 第四段：Plugin / Command / Hook

只讲打包和触发方式，不展开产品大全。

重点强调：

> **这些定义跨产品并不完全统一。**

---

## 最后

用一张决策表收束。

---

# 24. 本章截图 / 录屏清单

## 24.1 静态

| 编号 | 优先级 | 内容 | 状态 |
|---|---:|---|---|
| CONNECT-01 | P0 | API/Tool/MCP/Skill/Plugin/Command/Hook 分层总图 | ⬜ |
| CONNECT-02 | P0 | REST API → Agent Tool 映射 | ⬜ |
| CONNECT-03 | P0 | Existing API → MCP Server → Agent | ⬜ |
| CONNECT-04 | P0 | MCP Tools vs Skill Workflow | ⬜ |
| CONNECT-05 | P1 | OpenAI 当前 Plugin Package 结构 | ⬜ |
| CONNECT-06 | P0 | 设备管理端到端七概念示例 | ⬜ |
| CONNECT-07 | P0 | project-acceptance Skill 目录结构 | ⬜ |
| CONNECT-08 | P1 | Read/Write/Dangerous Tool 权限拆分 | ⬜ |
| CONNECT-09 | P0 | API/MCP/Skill 决策表 | ⬜ |

## 24.2 录屏

| 编号 | 优先级 | 内容 | 状态 |
|---|---:|---|---|
| CONNECT-R01 | P0 | curl / Raw API 调用 | ⬜ |
| CONNECT-R02 | P0 | 同能力通过 MCP Tool 调用 | ⬜ |
| CONNECT-R03 | P0 | Skill 组合 MCP Tool 完成多步验收 | ⬜ |
| CONNECT-R04 | P1 | 安装/查看现有 Skill，打开 SKILL.md | ⬜ |
| CONNECT-R05 | P1 | Command 主动触发 vs Hook 事件触发 | ⬜ |

---

# 25. 本章最后只留下七句话

1. **API 是系统的程序接口，不是 Agent 专属。**
2. **Tool 是模型能够理解和调用的动作界面，它可以包装 API、脚本、数据库或 CLI。**
3. **Function Calling 解决模型如何请求 Tool；MCP 解决 AI Host 如何标准化连接外部 Tool/Data Provider。**
4. **MCP 不替代 API，很多 MCP Server 本身就是现有 API 的 Agent 适配层。**
5. **Skill 不是另一种接口，它沉淀“什么时候做、按什么步骤做、怎样验证”的可复用工作方法。**
6. **Plugin 更像安装与分发包，具体组成必须按产品当前定义理解。**
7. **Command 偏主动触发，Hook 偏事件触发；完全确定的任务仍应优先 Script / CI / Automation。**

---

# 26. 官方参考资料

## MCP

- MCP TypeScript SDK / 当前稳定规范实现  
  https://ts.sdk.modelcontextprotocol.io/v2/
- OpenAI MCP Server 概念  
  https://developers.openai.com/plugins/concepts/mcp-server

## Skills

- OpenAI Skills 概念  
  https://developers.openai.com/plugins/concepts/skills
- Build Skills  
  https://developers.openai.com/plugins/build/skills
- OpenAI API Agent Skills  
  https://developers.openai.com/api/docs/guides/tools-skills

## Plugin / Hooks

- OpenAI Plugin Architecture  
  https://developers.openai.com/plugins/concepts/plugins
- Package Plugin  
  https://developers.openai.com/plugins/build/plugins
- Plugins  
  https://developers.openai.com/plugins

## Tool Design

- Define Tools  
  https://developers.openai.com/plugins/plan/tools

## 事实边界

- OpenAI 当前 Plugin / Skills / Hook 结构是 **当前产品实现**，不是行业中所有 Agent 的统一定义。
- MCP 属于开放协议；具体 Host 对 Tool / Resource / Prompt / UI 的支持应以当前实现为准。
- Command 的文件格式、自动发现方式和与 Skill 的关系差异较大，本章只保留“主动触发入口”这一稳定抽象。
- Hook 的事件名、信任机制和可执行环境差异较大，实际演示必须以选定 Harness 当前版本为准。
