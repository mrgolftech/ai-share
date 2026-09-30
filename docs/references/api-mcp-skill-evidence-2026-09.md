# API / Tool / MCP / Skill / Plugin / Command / Hook：证据基线（2026-09）

> 用途：支撑 `docs/chapters/06-api-mcp-skill-plugin-command-hook.md`。  
> 核实日期：2026-09-30。  
> 原则：跨产品概念只保留稳定抽象；涉及具体产品组成、目录结构、Hook/Plugin 行为时，以当前官方文档为准。

---

## 1. MCP 当前官方定义

### 1.1 官方来源

- MCP TypeScript SDK v2  
  https://ts.sdk.modelcontextprotocol.io/v2/
- OpenAI MCP Server 概念  
  https://developers.openai.com/plugins/concepts/mcp-server

当前 MCP TypeScript SDK v2 文档明确：

> MCP 是连接 AI 应用与数据和工具所在系统的开放标准。

Server 可以暴露：

- tools；
- resources；
- prompts。

培训可据此讲：

> **MCP 的核心是标准化 AI Host 与外部能力提供方之间的连接，而不是重新发明业务 API。**

---

## 2. API 与 MCP 的关系

MCP 官方/当前实现并没有要求外部系统必须放弃原 API。

典型工程结构可以是：

```text
Existing REST/GraphQL/SDK
        ↓
MCP Server
        ↓
MCP Host
```

因此培训采用：

> **API 提供系统能力；MCP Server 可以把这些能力转成 Agent 可发现、可调用的 Tool/Resource/Prompt。**

这是一种常见实现关系，不是强制唯一架构。

---

## 3. Tool Design 官方证据

官方来源：

- https://developers.openai.com/plugins/plan/tools

当前官方文档明确建议：

- Tool 应从用户 use case / outcome 出发；
- 不要机械镜像内部 API；
- 不同权限、安全风险或确认要求的操作应拆分。

因此培训中的 Tool 设计原则有官方依据：

> **Agent Tool Surface 应围绕任务设计，而不是把内部 REST Endpoint 一比一暴露给模型。**

---

## 4. Skills 当前官方定义

### 4.1 官方来源

- https://developers.openai.com/plugins/concepts/skills
- https://developers.openai.com/plugins/build/skills
- https://developers.openai.com/api/docs/guides/tools-skills

当前 OpenAI 文档明确：

- Skill 是目录；
- 需要 `SKILL.md`；
- 可带 references、scripts、assets；
- 用于 reusable workflow；
- Skill 可以指导模型如何组合 MCP tools；
- Skill 也可不依赖 MCP。

因此可稳定讲：

> **Skill 是工作流/方法层，不是 API 或 MCP 的替代物。**

---

## 5. MCP 与 Skill 的边界

OpenAI 当前官方 Skills 文档给出非常明确的分工：

MCP Server 负责：

- live data；
- authentication；
- authorization；
- controlled actions。

Skill 负责：

- tool sequence；
- decision points；
- output requirements；
- examples；
- templates；
- reusable guidance。

这直接支撑培训核心结论：

> **MCP 告诉 Agent“能做什么”；Skill 教 Agent“怎样把能力组合成一个可重复任务”。**

---

## 6. Plugin 当前 OpenAI 实现

官方来源：

- https://developers.openai.com/plugins/concepts/plugins
- https://developers.openai.com/plugins/build/plugins
- https://developers.openai.com/plugins

当前官方文档明确，Plugin 可以包含：

- Skills；
- MCP server；
- optional UI；
- lifecycle hooks。

当前 Package 文档进一步给出 portable plugin 目录，如：

```text
plugin.json
skills/
mcp.json
hooks/
assets/
```

因此在培训中只能表述为：

> **在 OpenAI 当前实现中，Plugin 是一个安装/分发包，可以组合 Skills、MCP 和 Hooks 等能力。**

不能外推成：

> “所有 Agent 的 Plugin 都是这个结构”。

---

## 7. Command 的事实边界

Command 并不是跨产品统一标准。

OpenAI 当前“Submit your Claude Code plugin to OpenAI”官方文档明确提到：

- Claude plugin 中的 `commands/`；
- 可复用行为在迁移时建议转换为 Skills。

来源：

- https://developers.openai.com/plugins/guides/submit-claude-plugin

因此培训只保留稳定抽象：

> **Command 通常是用户主动触发的标准行为入口；具体存储格式、发现机制、是否等同 Prompt Template，应按具体 Harness 理解。**

不要设计一张“所有产品统一 Command 目录”的错误图。

---

## 8. Hook 当前证据

官方来源：

- https://developers.openai.com/plugins/concepts/plugins
- https://developers.openai.com/plugins/build/plugins
- https://developers.openai.com/docs/hooks

当前 OpenAI 文档明确支持 lifecycle hooks，并要求：

- hook scripts 在 execution environment 中存在；
- plugin hooks 需要信任/审核；
- Hook 在特定生命周期事件运行命令。

因此可稳定讲：

> **Hook 是事件驱动自动执行机制，不应与用户主动 Command 混为一谈。**

但不同产品 Event Name / Trust / Runtime 不统一。

---

## 9. Function Calling 与 MCP

培训采用如下抽象：

```text
Model
→ function/tool call
Harness / Host
→ MCP protocol
MCP Server
→ external system
```

这里需要明确：

- Function Calling：模型输出结构化 tool request 的机制；
- MCP：Host 与 Server 之间的协议。

这是一种架构分层教学，不声称所有 Host 内部实现都完全相同。

---

## 10. 安全边界

Skill 中的自然语言规则不能代替：

- Tool authorization；
- MCP Server authorization；
- OAuth / credential scope；
- Sandbox；
- Approval；
- Hook policy；
- OS / Container / Network boundary。

原因：

> Skill 主要是模型工作流指导，而授权应由真正执行能力的一侧强制。

该结论应贯穿企业 Agent 培训。

---

## 11. 当前建议 Demo

### Demo 1：Raw API

```text
curl → REST endpoint → JSON
```

证明原系统能力。

### Demo 2：MCP Tool

```text
Agent → MCP tool → same backend → structured result
```

证明 Agent 连接方式。

### Demo 3：Skill + MCP

```text
Skill
→ call status tool
→ inspect result
→ call logs tool
→ verify
→ report
```

证明工作流方法层。

建议三个 Demo 使用同一后端，避免学员误认为是三套不同能力。

---

## 12. 当前待实测

以下目前属于方案，尚未在 `ai-share` 形成正式实测证据：

1. 自建最小 MCP Server；
2. 内网 qwen3.6 + 某 Harness 的 MCP Tool Calling；
3. `project-acceptance` Skill 实际调用；
4. Command 与 Hook 同任务触发对比；
5. Plugin 打包与跨 Surface 安装。

完成后应在本文件追加：

- 环境；
- 版本；
- 请求/响应；
- Screenshot；
- Tool Trace；
- 失败项；
- 结论。
