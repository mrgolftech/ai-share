# Model API Protocol Evolution Evidence（2026-09）

> 用途：支撑第一讲“为什么同一个模型服务会出现 OpenAI Chat / OpenAI Responses / Anthropic Messages 三种 API 形态”的讲解。  
> 注意：以下“为什么出现三套接口”的表述是基于当前官方 API 形态和生态演进作出的工程解释，不把它写成任何厂商的统一历史结论。

---

# 1. OpenAI Chat Completions

OpenAI 当前仍保留：

`POST /v1/chat/completions`

其核心抽象围绕：

- messages；
- roles；
- choices；
- tool_calls。

当前 OpenAI API Reference / Batch 仍把 `/v1/chat/completions` 与 `/v1/responses` 同时作为正式 Endpoint 使用。

官方参考：

- https://platform.openai.com/docs/api-reference/
- https://platform.openai.com/docs/api-reference/batch/object

培训解释：

> Chat Completions 代表的是以多轮 Chat Message 为核心的成熟 API 生态。大量第三方推理服务和客户端已经形成 OpenAI-compatible 实现，因此即使出现更新接口，现实工程仍需要兼容。

---

# 2. OpenAI Responses

OpenAI 当前开发者 Quickstart 默认使用 Responses API：

`client.responses.create(...)`

并直接通过 Responses：

- 输入文本/图像/文件；
- Function Calling；
- Web Search；
- File Search；
- Remote MCP；
- Streaming。

官方参考：

- https://platform.openai.com/docs/quickstart/make-your-first-api-request
- https://platform.openai.com/docs/models

培训解释：

> Responses 更适合用“统一的 input/output items + tools/events”理解，能够把文本、视觉、工具和 Agent 工作负载放到更统一的接口形态中。

不要在培训中表述为：

> “Chat Completions 已失效或必须立即迁移。”

当前官方仍同时保留多个 API Endpoint。

---

# 3. Anthropic Messages

Anthropic 当前官方开发者入口明确将 Messages 定义为：

> 直接访问模型，由开发者组织每轮 Conversation、管理状态并实现 Tool Loop。

其核心结构包括：

- messages；
- content blocks；
- tool_use；
- tool_result；
- thinking；
- vision。

官方参考：

- https://docs.anthropic.com/
- https://docs.anthropic.com/en/api/messages

培训解释：

> Anthropic Messages 是 Claude 生态独立形成的一套 API Schema，不使用 OpenAI Chat / Responses 的字段语义。

---

# 4. 为什么同一个 qwen3.6 能同时支持三种接口

当前内网 qwen3.6 实测：

- OpenAI Chat；
- OpenAI Responses；
- Anthropic Messages；

三套基础文本 / Streaming / Tool Loop 均已经验证。

这不意味着：

> qwen3.6 内部有三套模型。

更合理的工程分层：

```text
Client
↓
Protocol / Adapter
↓
Inference Server / Gateway
↓
Model
```

由推理框架 / Gateway / Adapter：

- 解析不同 Request Schema；
- 映射到模型推理输入；
- 再把模型结果映射成对应协议 Response。

---

# 5. Cherry Studio 为什么需要 Endpoint Type / Adapter

当前 Cherry Studio 源码明确存在：

- `openai-chat-completions`；
- `openai-responses`；
- `anthropic-messages`；

并根据 Endpoint Type 解析为不同 Adapter Family。

参考：

- https://github.com/CherryHQ/cherry-studio/blob/main/docs/references/ai/adapter-family.md
- https://github.com/CherryHQ/cherry-studio/blob/main/docs/references/ai/provider-resolution.md

因此第一讲建议：

```text
先看 Cherry 配置
→ 发现三种 Endpoint Type
→ 同 Prompt 切换
→ Network 看到三个 POST Endpoint
→ 再解释 Schema
```

而不是：

```text
先背三套 JSON
→ 再告诉大家 Cherry 可以配置
```

---

# 6. 培训最终只需要学员记住

> **Model Capability、API Protocol、Client/Harness 是三层。**

同一 Model：

- 可以被不同 Protocol Adapter 暴露；
- 可以被不同 Client 使用。

同一 Client：

- 也可以根据 Provider / Endpoint Type 使用不同 Protocol。

因此后续遇到：

- Codex 需要 Responses；
- Claude 类工具使用 Anthropic；
- 普通 OpenAI-compatible 软件使用 Chat Completions；

本质上首先是：

> **协议兼容问题。**

然后才是：

> **模型能力是否支持 Tool / Vision / Thinking。**
