# 2026 Agent 横向对比：ZCode / Codex / Claude Code / OpenCode / DSH / Pi / Cline / Kilo / Hermes / Hermes

> 用途：AI 大模型与 Agent 工程实践培训参考资料
> 核实日期：2026-09-29
> 原则：产品变化很快；“特点”以当前官方文档和官方仓库为准，“能力强弱”不根据单一 Benchmark 下绝对结论。

## 1. 为什么需要单独比较 Agent，而不能只比较模型

同一个模型放进不同 Agent Harness 后，结果可能明显不同。

差异来自：

- System Prompt / 项目规则；
- 文件编辑工具；
- Shell / Git / Browser；
- Context 管理和 Compaction；
- Prompt Cache；
- Tool Schema；
- Permission / Sandbox；
- Sub-agent；
- Retry / Recovery；
- Verification Loop。

所以：

> **Model Benchmark 回答“模型本身有多强”；Harness Benchmark 回答“同一个模型放进不同 Agent 后，谁更能把能力释放出来”。**

---

## 2. 一张表先看懂九个 Agent

> “自有 API 接入”主要指企业自建或第三方模型服务，而不是产品自带账号订阅。

| Agent | 当前主要定位 | 开源状态 | 自有 API 接入 | 典型特点 | 当前主要注意点 |
|---|---|---|---|---|---|
| **ZCode** | ADE / Workspace-first Agent | **是，Apache-2.0** | **很容易** | Desktop + Browser + Terminal；Goal Mode；AGENTS.md；长任务；与 GLM 深度联调 | 产品默认体验明显偏 GLM，但第三方 OpenAI / Anthropic 协议可接 |
| **Codex** | Terminal / IDE / App / Cloud Coding Agent | **CLI/Harness 是，Apache-2.0** | **中等** | 强 Shell/Git/文件闭环；Sandbox/Approval；AGENTS.md；MCP/Skill/Plugin；OpenAI 生态 | 当前自定义 provider 的 wire API 重点是 Responses；Chat-Completions-only 服务不如 OpenCode/Cline 直接 |
| **Claude Code** | Terminal-first Coding Agent | **否，专有软件** | **一般** | CLAUDE.md；Skills；MCP；Hooks；Subagents；模型与 Harness 深度协同 | 原生围绕 Anthropic 协议；接 OpenAI-compatible 服务通常要网关/协议转换 |
| **OpenCode** | Provider-neutral open Coding Agent | **是，MIT** | **非常容易** | 75+ providers；本地模型；OpenAI-compatible；MCP/Skill/Agent；高度可配置 | 官方安全说明明确：permission 不是安全隔离，默认没有真正 sandbox |
| **DeepSeek Harness (DSH)** | 可组合 Agent Harness / Developer Platform | **是，MIT** | **非常容易** | “Everything is a Plugin”；Model/Tool/Skill/Session/Sandbox/Loop/UI 都可插件化 | 仍是 developer preview，官方明确提醒可能发生 breaking changes，且尚未安全审计 |
| **Pi** | Minimal terminal coding harness | **是，MIT** | **容易** | 极简核心；默认只有 read/write/edit/bash；Extension / Skill / Prompt / SDK；适合研究 Harness | 有意不内置复杂 Plan/Subagent；高级能力靠扩展，开箱即用程度低于大而全产品 |
| **Cline** | IDE-first Agent | **是，Apache-2.0** | **非常容易** | VS Code / CLI；Plan/Act；文件/命令/Browser；MCP；BYOK；人机确认感强 | IDE 中交互较重；大任务自主循环风格与 terminal-first Harness 不完全相同 |
| **Kilo Code** | Multi-surface Agentic Engineering Platform | **是，MIT** | **非常容易** | VS Code / JetBrains / CLI；Code/Plan/Debug/Ask；Subagents；Browser；Marketplace；大量模型 | 2026 年重构后当前架构与早期 Roo/Cline 派生版本不同，培训需以当前版本为准 |
| **Hermes Agent** | 通用自主 Agent / Coding + Automation + Personal Agent | **是，MIT** | **非常容易** | TUI/Desktop/Web/Gateway；Memory；Skills；MCP；Subagents；Cron；Browser；多种 Terminal Backend；Provider-neutral | 能力面比纯 Coding Agent 更宽，做编码 Benchmark 时要区分“通用 Agent 能力”和“Coding Harness 优化程度” |

---

## 3. 自有 API 接入：这部分对我们最重要

### 3.1 ZCode

官方当前支持 Z.ai / BigModel 账号、API Key、第三方 Provider，以及 OpenAI / Anthropic 协议。

因此对于标准企业 API Gateway，接入门槛低。

部门内网 Qwen 已经实测提供 OpenAI Chat / Responses / Anthropic Messages，所以 ZCode 是适合作为内网模型 Agent 客户端的候选之一。

### 3.2 Codex

Codex 支持自定义 Model Provider、Base URL、API Key 环境变量和 Headers。

但当前配置参考中，自定义 provider 的 wire_api 只列 responses。

这意味着：

- 上游真正支持 OpenAI Responses：比较适合；
- 只有 /v1/chat/completions：不如 OpenCode / Cline 这种原生 OpenAI-compatible 路径直接；
- 本地 Ollama / LM Studio 有官方 OSS 路径。

对部门内网 Qwen：

> **因为我们已经实测 Responses 文本、Streaming、Tool Loop 可用，所以 Codex 是可接的。**

但仍应实测 Responses Tool Schema、reasoning/thinking、context、多轮工具回灌，以及 Codex 对模型能力 metadata 的假设。

### 3.3 Claude Code

Claude Code 的原生调用方式围绕 Anthropic API。

官方提供 ANTHROPIC_BASE_URL、Anthropic-compatible Gateway、LiteLLM Gateway 指南、Bedrock 和 Vertex AI。

所以：

> **Anthropic-compatible 企业网关很好接；普通 OpenAI Chat-compatible API 不是它最自然的接入方式。**

如果企业只有 OpenAI-compatible API，通常需要 LiteLLM / Proxy 做协议转换。

对部门内网 Qwen：

- Anthropic Messages 文本：PASS；
- SSE：PASS；
- Tool Loop：PASS；
- Vision：PASS；
- 但我们实测 thinking.type=disabled 没有真正关闭 Thinking。

所以 Claude Code 理论上能接内网服务，但 Thinking 行为必须专项验证。

### 3.4 OpenCode

OpenCode 是这组工具里 Provider 自由度最高的一类。

官方当前使用 AI SDK + Models.dev，支持 75+ Provider、本地模型、任意 Provider 覆盖 baseURL，并可通过 OpenAI-compatible 或 Responses 适配层接企业 API。

对于企业内网 OpenAI-compatible API：

> **非常自然。**

### 3.5 DeepSeek Harness / DSH

DSH 的自定义模型 API 页面直接提供三种 Protocol：

- OpenAI Chat Completions；
- OpenAI Responses；
- Anthropic Messages。

还支持自定义 Base URL、Key、手动 Model ID、从上游发现 Model Catalog。

这与我们的内网 Qwen 三协议实测几乎完全对齐。

因此从“拿部门内网 API 做 Agent 教学”的角度看：

> **DSH 是非常理想的协议展示对象。**

### 3.6 Pi

Pi 内置大量 Provider。

如果服务使用 Pi 已支持的 wire protocol，可以在 ~/.pi/agent/models.json 直接声明自定义模型。

官方支持 OpenAI、Anthropic、Google 等既有协议，以及自定义 Base URL / Header；如果协议本身完全自定义，再通过 Provider Extension 扩展。

因此：

> **标准 OpenAI-compatible 接入容易；非标准协议需要一定开发工作。**

### 3.7 Cline

Cline 对 BYOK / 企业 API 很友好。

OpenAI Compatible Provider 直接配置：

1. Base URL；
2. API Key；
3. Model ID。

并可补 Context Window、Max Output、Vision、Tool / Computer Use 和价格信息。

这类 GUI 配置方式很适合培训现场：

> **三项配置 → 直接把内网模型接进 Coding Agent。**

### 3.8 Kilo Code

Kilo 当前 Custom Provider 支持：

- OpenAI Compatible；
- OpenAI Responses；
- Anthropic Messages；
- Base URL；
- API Key；
- Headers；
- 手动 Model；
- 从 /v1/models 自动发现模型。

因此它在自有 API 接入方面也很友好。

### 3.9 Hermes Agent

Hermes Agent 当前官方 Provider 文档支持多种云端和本地模型来源，也明确支持：

- OpenAI API；
- OpenRouter；
- Anthropic；
- DeepSeek；
- Gemini；
- Qwen OAuth；
- LM Studio；
- Ollama / vLLM / llama.cpp 等本地或自托管服务；
- Custom Endpoint；
- OPENAI_BASE_URL + OPENAI_API_KEY。

官方开发文档明确说明：

> 任何 OpenAI-compatible endpoint 都可以直接通过 Custom Provider 路径接入，不需要专门写 Provider 插件。

因此对于部门内网 Qwen：

> **Hermes 是非常自然的接入对象。**

只需配置自定义 OpenAI-compatible Base URL、API Key 和 Model，即可使用；如果需要进一步做 Vision、Compression、Title Generation 等辅助模型，也可以分别配置 Provider / Model / Base URL。

Hermes 的差异点是：

> **它不只把自己定位成 Coding Agent，而是一个可以长期运行、拥有 Memory、Skills、自动化和多平台 Gateway 的通用自主 Agent。**

---

## 4. 如果只针对“部门内网 Qwen”，接入便利度怎么判断

这里不是评价 Agent 综合能力，而只是评价我们当前内网模型 API 的适配成本。

| Agent | 内网 Qwen 接入判断 | 原因 |
|---|---|---|
| **ZCode** | ★★★★★ | OpenAI / Anthropic compatible，GUI/API Key 路径清晰 |
| **Codex** | ★★★★☆ | 内网 Responses 已实测可用；但 Codex 当前自定义 provider 更依赖 Responses 语义 |
| **Claude Code** | ★★★☆☆ | 内网 Anthropic Messages 可跑，但 Thinking disable 已发现兼容异常 |
| **OpenCode** | ★★★★★ | OpenAI-compatible / Responses 均可灵活配置 |
| **DSH** | ★★★★★ | 三套协议直接可选，与我们测试矩阵高度对应 |
| **Pi** | ★★★★☆ | 标准 API 配置简单；极端兼容问题需要 models.json / Extension |
| **Cline** | ★★★★★ | OpenAI Compatible 三字段即可接入 |
| **Kilo Code** | ★★★★★ | Chat / Responses / Anthropic 三种自定义 Provider 路径齐全 |
| **Hermes Agent** | ★★★★★ | 原生支持 Custom OpenAI-compatible Endpoint、OPENAI_BASE_URL，本地 vLLM / Ollama / LM Studio 等路径也完整 |

注意：

> 星级只表示**接我们当前内网 API 的配置便利度**，不表示 Agent 综合能力排名。

---

## 5. 开源状态必须讲清，不要把“GitHub 有仓库”当成开源

### ZCode

Z.ai 当前官方 zai-org/ZCode 仓库已经包含客户端、后端、共享 UI、Agent CLI / Runtime 源码；根 LICENSE 为 Apache-2.0。

### Codex

OpenAI openai/codex 为 Apache-2.0。

准确表述应是：

> **Codex CLI / 本地 Harness 是开源的；OpenAI Hosted Codex / 云端服务不应简单等同为整个产品全部开源。**

### Claude Code

Anthropic 的官方 GitHub 仓库主要用于安装说明、Issue、Changelog 等。

LICENSE 当前为 All rights reserved，并受 Anthropic Commercial Terms of Service 约束。

因此：

> **Claude Code 当前不是开源 Harness。**

### OpenCode

当前主项目为 MIT。

不要和 2025 年归档的旧 opencode-ai/opencode 项目混淆。

### DeepSeek Harness

MIT，源码完整公开。

### Pi

MIT。

### Cline

Apache-2.0。

### Kilo Code

当前主仓库 MIT。

Kilo 的历史比较特殊：

~~~text
Cline
  ↓ fork
Roo Code
  ↓ fork
早期 Kilo
  ↓
2026-04 当前 Kilo VS Code 扩展重构到 OpenCode server 架构
~~~

因此不要拿 2025 年的 Kilo/Roo 架构直接描述 2026 年当前 Kilo。

### Hermes Agent

Nous Research 官方 `NousResearch/hermes-agent` 仓库为 MIT License，源码公开。

它同时提供：

- CLI / TUI；
- Hermes Desktop；
- Web / Dashboard；
- Messaging Gateway；
- Native Windows / Linux / macOS / WSL；
- ACP Server 等多种使用界面。

因此它可以作为“同一个 Agent Core 如何服务多种交互 Surface”的案例。

---

## 6. 各自最值得培训讲的“特点”

### ZCode：Agentic Development Environment

用它讲：

> **Coding Agent 不一定只是一个终端程序，也可以围绕 Workspace 做成 ADE。**

适合展示 Desktop / Browser / Terminal、Workspace、AGENTS.md、Goal Mode、Git Branch Context、Long-Horizon Task 和 Model Effort。

### Codex：工程执行与安全边界

适合讲 Terminal-first、IDE、App / Cloud、AGENTS.md、Shell / Git、MCP、Skill / Plugin、Approval、Sandbox、Context Compaction、Subagent / Delegation。

尤其适合讲：

> **Agent 不只要会执行，还必须考虑“允许它执行到什么程度”。**

### Claude Code：成熟 Agent 生态

适合讲 CLAUDE.md、Skills、MCP、Hooks、Subagents、Plugin、Terminal / Git 工作流。

Claude Code 的一个教学价值是：

> **模型与 Harness 可以深度共同设计。**

但它同时也是很好的对照样本：

> 功能强、生态成熟，并不意味着 Harness 一定开源，也不意味着最容易接企业自有模型。

### OpenCode：模型自由与 Provider 抽象

非常适合部门环境，因为它把 Agent Harness 与 Provider 明确解耦。

同时必须讲安全边界：

> OpenCode 官方安全说明明确表示，其 Permission System 是 UX 安全提示，不构成真正 OS Sandbox；需要强隔离时应放到 Container / VM。

### DSH：Harness 架构本身就是产品

最适合讲“Agent Harness 到底是什么”。

DeepSeek 官方直接提出：

> **Agent = Model + Harness**

并将 Models、Tools、Skills、Sessions、Sandboxes、Storage、Loops、Scheduling、UI 都设计为 Plugin。

因此 DSH 更适合作为：

> **Agent 架构教学案例**

而不是单纯作为“另一个代码助手”。

### Pi：把 Harness 拆到最小

Pi 默认只给模型四个工具：

~~~text
read
write
edit
bash
~~~

并刻意不把很多功能焊死在核心中，而通过 Extensions、Skills、Prompt Templates、Pi Packages、RPC、SDK 继续扩展。

它非常适合提出：

> **一个 Coding Agent 最少需要多少东西？**

### Cline：IDE 内的人机协作 Agent

Cline 很适合初次接触 Agent 的开发人员，因为用户能直观看到 Agent 请求执行、文件修改、Terminal、Browser、用户批准、Plan / Act 和 Token / Cost。

而且自定义 API 非常直接。

### Kilo：多模式 + 多 Provider + 多 Surface

Kilo 当前覆盖 VS Code、JetBrains、CLI、Code / Plan / Debug / Ask、Subagents、Browser、Agent Manager、Marketplace 和大量模型 Provider。

适合讲：

> **开源 Coding Agent 正从“VS Code 插件”演变为完整 Agentic Engineering Platform。**

### Hermes：从 Coding Agent 扩展到“长期运行的通用 Agent”

Hermes 最值得培训讲的不是“又一个会改代码的 Agent”，而是它把很多长期 Agent 能力放在同一个核心里：

- 跨 Session 持久 Memory；
- 从经验中创建和改进 Skills；
- MCP；
- Subagents / Parallel Work；
- Browser / Vision / Web；
- 内置 Cron 自动化；
- Telegram / Discord / Slack / WhatsApp / Signal 等 Gateway；
- Local / Docker / SSH / Modal / Daytona / Vercel Sandbox 等 Terminal Backend；
- CLI / TUI / Desktop / Web / IDE ACP 多种 Surface。

因此 Hermes 很适合用来回答：

> **如果 Agent 不只是“写完一次代码就退出”，而是长期运行、记住经验、定时工作、通过多个入口协作，会变成什么？**

它与 Codex / Claude Code / OpenCode 的对比重点不应只放在编码完成率，而应放在：

> **Coding Harness vs General-purpose Persistent Agent**

---

## 7. 你记得的 Harness Benchmark：FrontierHarness Eval

这是目前非常适合培训引用的一组数据。

FrontierHarness Eval v1.0 做了一个关键控制：

> **固定同一个 Kimi K3 模型，固定任务，固定运行环境，只改变 Harness。**

测试规模：

- 9 个 Harness；
- 12 个 Harness 配置；
- 30 个软件工程任务；
- 360 次 Evaluation；
- 21 个 Terminal-Bench Tasks；
- 9 个 DeepSWE Tasks。

冻结版本在 2026-08-22 左右，因此是：

> **一次受控历史实验，不是 2026-09-29 各产品最新版的实时排行榜。**

### 7.1 与我们相关的结果

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

Cline、Kilo、ZCode **没有进入 FrontierHarness v1.0 的这组冻结测试**，所以不要自己补分数。Hermes 已经在该测试中，冻结版本为 v0.20.4。

### 7.2 这组数据真正说明什么

不是：

> “Codex 永远比 OpenCode 强 16.7%。”

而是：

> **同样的 Kimi K3，在不同 Harness 里完成相同任务，Pass Rate 可以从 50% 到 66.7%，而成本和速度也出现明显差异。**

这正好支持本培训的核心观点：

> **Harness 本身就是 Agent 能力的一部分。**

### 7.3 为什么不能拿这一张表直接做“Agent 总排名”

至少有五个限制：

1. 只有 30 个任务；
2. 只固定了一个模型 Kimi K3；
3. Harness 版本被冻结；
4. 主要是 Terminal / Software Engineering Tasks；
5. Prompt Cache、Provider 实现和模型-Harness 适配都会影响结果。

另一个独立项目 HarnessRank 当前用 GPT-5.5 / medium 测试时，公开页面显示：

~~~text
Pi > Oh My Pi > OpenCode > Codex
~~~

次序与 FrontierHarness 并不相同，而且 HarnessRank 当前明确说明完整 benchmark rows 尚未公开。

因此最值得讲的不是谁排第一，而是：

> **Agent 表现 = Model × Harness × Task × Configuration × Runtime。**

---

## 8. 建议培训中的产品分组

### 第一类：厂商旗舰 Harness

- Codex
- Claude Code
- ZCode

讲：

> 模型厂商如何针对自己的模型设计完整 Agent 体验。

### 第二类：模型中立的开源 Harness

- OpenCode
- Cline
- Kilo

讲：

> 一个 Harness 如何通过 Provider 层支持不同模型和企业自建 API。

### 第三类：Harness 架构实验与极简路线

- DeepSeek Harness
- Pi

讲：

> Agent Harness 到底由什么组成，以及“全部插件化”和“核心极简化”两种设计哲学。

### 第四类：长期运行的通用自主 Agent

- Hermes Agent

讲：

> **Coding Agent 如何进一步扩展为有 Memory、Skills、Cron、Messaging Gateway 和多运行后端的长期 Agent。**

这也能帮助学员理解：Agent 的应用边界并不止于软件开发。

---

## 9. 推荐现场 Demo

### Demo A：同一个内网 Qwen，跑三个 Harness

优先：

~~~text
OpenCode
DSH
Cline / Kilo
~~~

都接同一个 Base URL、API Key、Model ID，然后发相同工程任务。

目的不是排名，而是观察：

- Agent 怎么读取文件；
- Tool Call 长什么样；
- Context 怎么组织；
- Approval 怎么做；
- 修改策略；
- 是否主动测试；
- 失败后怎么恢复。

### Demo B：同一个任务，Codex / Claude Code / OpenCode

如果有条件让三个 Harness 使用同一可访问模型，尽量固定模型。

如果无法固定模型，就必须明确：

> 这次差异同时包含 Model 和 Harness 两个变量，不能归因到 Harness。

### Demo C：FrontierHarness Eval 截图

直接展示：

~~~text
Same Model
Same Tasks
Same Runtime
Different Harness
      ↓
Different Pass Rate / Cost / Cache / Runtime
~~~

这一张比罗列 Agent 功能更有说服力。

---

## 10. 对部门内部使用的实际判断

如果目标是快速把内网 Qwen 接起来，优先做实验：

- OpenCode；
- DSH；
- Cline；
- Kilo；
- ZCode；
- Hermes。

如果目标是研究 Harness 设计，重点看：

- DSH；
- Pi；
- Codex；
- OpenCode；
- Hermes。

如果目标是看成熟旗舰 Agent 体验，重点看：

- Codex；
- Claude Code；
- ZCode。

如果目标是给习惯 IDE 的开发人员降低使用门槛，重点看：

- Cline；
- Kilo；
- ZCode。

这里不是最终选型结论。

真正部门选型还需要在**我们的内网模型、我们的代码仓库、我们的网络与安全约束**下做同模型实测。

---

## 11. 后续应做的部门内实测

建议把 FrontierHarness 的思路缩小成内部 Harness Test：

~~~text
同一个内网 qwen3.6
同一个 Git Repo
同一个 Task
同一个 AGENTS.md
同一时间限制
同一权限范围
        ↓
ZCode / Codex / Claude Code / OpenCode / DSH / Pi / Cline / Kilo
~~~

记录：

- 任务是否完成；
- 第一次成功率；
- Tool Calls；
- 输入 / 输出 Token；
- TTFT；
- 总耗时；
- 修改文件数；
- 命令数；
- 是否执行测试；
- 是否主动修复；
- 是否错误声称“已完成”；
- 最终 Git Diff；
- 人工介入次数。

这会比直接照搬公网排行榜更有价值。

---

## 12. 主要资料

### Benchmark

- FrontierHarness Eval: https://github.com/frontier-harness-eval/eval
- FrontierHarness interactive report: https://frontierharness.org/
- HarnessRank: https://harnessrank.net/

### ZCode

- Docs: https://zcode.z.ai/
- GitHub: https://github.com/zai-org/ZCode
- Model configuration: https://zcode.z.ai/en/docs/configuration

### Codex

- Docs: https://developers.openai.com/codex/
- GitHub: https://github.com/openai/codex
- Config reference: https://developers.openai.com/docs/config-file/config-reference

### Claude Code

- Docs: https://code.claude.com/docs/
- GitHub: https://github.com/anthropics/claude-code
- LLM Gateway: https://docs.anthropic.com/en/docs/claude-code/llm-gateway

### OpenCode

- Docs: https://opencode.ai/docs/
- Providers: https://opencode.ai/docs/providers
- GitHub: https://github.com/anomalyco/opencode

### DeepSeek Harness

- Homepage: https://www.deepseek.com/harness/
- GitHub: https://github.com/deepseek-ai/deepseek-harness
- Providers: https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/guide/providers.md

### Pi

- Docs: https://pi.dev/
- Custom Provider: https://pi.dev/docs/latest/custom-provider

### Cline

- GitHub: https://github.com/cline/cline
- OpenAI Compatible: https://github.com/cline/cline/blob/main/docs/provider-config/openai-compatible.mdx

### Kilo Code

- Docs: https://kilo.ai/docs/
- GitHub: https://github.com/Kilo-Org/kilocode
- OpenAI Compatible: https://kilo.ai/docs/ai-providers/openai-compatible

### Hermes Agent

- Docs: https://hermes-agent.nousresearch.com/docs/
- GitHub: https://github.com/NousResearch/hermes-agent
- Providers: https://hermes-agent.nousresearch.com/docs/integrations/providers/
- Configuration: https://hermes-agent.nousresearch.com/docs/user-guide/configuration
