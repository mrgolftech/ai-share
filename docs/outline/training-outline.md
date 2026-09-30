# AI 大模型与 Agent 工程实践培训大纲（基线）

> 状态：Baseline v0.1  
> 日期：2026-09-29  
> 仓库：`mrgolftech/ai-share`  
> 适用范围：培训讲义、Demo、案例素材、截图/图表、PPT 设计与最终交付  
> 总体约束：以根目录 `AGENTS.md` 为最高层项目规则；涉及内网模型能力，以本仓库实测证据为准。

---

# 0. 基线治理规则

本文件是 **培训内容的唯一大纲基线**。

详细章节、案例映射、Demo 需求、当前建设状态均在此维护；`AGENTS.md` 只维护稳定的项目规则，不重复维护详细大纲。

发生冲突时，优先级为：

1. 当前代码、实际测试数据和可复现实验结果；
2. 本文件；
3. `AGENTS.md`；
4. 当前章节/案例文档；
5. 官方资料；
6. 高质量社区资料；
7. 历史聊天、历史记忆和推测。

如果新的实测结果与本大纲冲突，应更新本大纲。

## 0.1 材料成熟度

章节、案例、Demo 和重要素材使用以下状态：

- **规划中**
- **已有素材**
- **已有初稿**
- **已有实测证据**
- **可用于培训**
- **可用于 PPT**

后续每完成一个模块，应同步更新第 13 节“当前仓库状态与缺口”。

## 0.2 人与 Agent 的统一分工

培训统一采用：

> **模型负责判断和生成，工具负责执行，自动化测试负责验证，人负责目标、约束和最终判断。**

这一原则应贯穿 API、Agent、应用开发、测试、运维、数据分析和内容生产案例。

---

# 1. 培训定位

本培训面向部门内部技术人员，目标不是做一次“AI 工具介绍”，而是通过部门内网大模型和真实工程案例，让学员建立一套可以迁移到日常工作的 AI Agent 工程方法。

培训从一个最基础的问题开始：

> **模型到底是怎么被调用的？**

然后逐步推进到：

> **为什么只有 Chat 不够？Agent 为什么能够做真正的工程工作？Agent 如何连接工具？如何把一次成功经验沉淀为长期可复用资产？最后，它到底能完成哪些真实任务？**

因此，整场培训采用以下主线：

> **模型怎么调用 → 为什么 Chat 不够 → Agent 如何操作真实世界 → 如何让 Agent 掌握工具 → 如何形成可复用资产 → 用真实项目证明 Agent 能完成什么**

这条主线是后续所有讲义、Demo 和 PPT 的组织基线。

---

# 2. 培训希望最终建立的四个认知

## 2.1 大模型不是传统 SaaS

需要让学员建立“模型调用存在实时计算成本”的意识。

重点不是背 Token 定义，而是理解：

- 输入上下文需要 Prefill；
- 输出需要逐 Token Decode；
- 长上下文会增加计算和 KV Cache 压力；
- Thinking 会增加推理 Token、时间和资源消耗；
- Agent 会反复读取上下文、调用工具并继续推理，因此通常比一次 Chat 消耗更多资源；
- 模型能力、响应速度、上下文长度和成本之间需要权衡。

培训中优先使用内网模型的真实 API、metrics 和 model-metric 测试结果说明这些问题。

核心观点：

> **大模型的每一次输入、推理和输出都不是免费的。**

---

## 2.2 从 Chat 走向 Agent

不简单宣称“Chat 已经过时”。

更准确的表达是：

> **Chat 适合孤立问题；真实工程任务往往需要工作区、文件、Shell、Git、浏览器、测试、项目规则和持续上下文，因此更适合 Agent 工作方式。**

学员需要理解从：

`Prompt → Answer`

到：

`Goal → Plan → Read → Act → Observe → Verify → Iterate → Deliver`

的变化。

---

## 2.3 旗舰模型和开源模型各有位置

培训不形成两个极端：

- “开源模型不行”；
- “所有任务都应该使用最强旗舰模型”。

重点建立“任务路由”意识。

旗舰模型更适合：

- 疑难问题定位；
- 复杂系统设计；
- 多文件代码理解；
- 难以复现或难以解释的 Bug；
- 新技术预研；
- 复杂数据关系发现；
- 高质量方案 Review。

内网开源模型已经可以承担大量：

- 日常编码；
- 文档整理；
- API 调用；
- 信息提取；
- 数据清洗；
- 脚本编写；
- 自动化；
- 常规 Agent 工作。

核心观点：

> **不是所有任务都需要最强模型，模型应该根据任务难度和成本分级使用。**

---

## 2.4 Agent 工具大同小异，可复用资产更重要

培训会涉及 ZCode、Codex、OpenCode、DSH、Pi 等 Agent，但不做“软件功能大全”。

重点让学员理解：

> **工具会变，工作方法和工程资产可以留下来。**

真正值得长期积累的是：

- Prompt；
- 项目说明；
- `AGENTS.md` / `CLAUDE.md`；
- Skill；
- MCP；
- 脚本；
- 测试工具；
- Git 工作流；
- CI；
- 模板；
- 架构规范；
- UI 规范；
- 验收标准；
- 知识库；
- 团队工作方法。

---

# 3. 整体内容结构

内容逻辑继续保留 **1～8 个内容单元**，用于维护知识边界、讲义、证据、截图和 Demo；现场授课正式按 **4 次专题讲座**组织。

截至 2026-09-30，当前正式授课基线为：

1. **第一讲：从模型 API 到 Agent——看懂 AI 应用背后的工作逻辑**  
   内容映射：1 + 3。解决模型、API、Chat、Agent、工具之间的底层关系问题。
2. **第二讲：部门知识库建设——让 AI 可靠使用我们的知识**  
   内容映射：2。围绕部门知识资产、检索、治理、权限、评测和使用方案单独展开。
3. **第三讲：深入 Agent——掌握共性，而不是记住不同界面**  
   内容映射：4 + 5。深入 Harness、Context、Workspace、Runtime、Tools、MCP、Skill 与多 Agent 共性。
4. **第四讲：Agent 工程实战——用真实项目走通开发、测试、发布和部署**  
   内容映射：6 + 7 + 8。以 BMQuiz、FileCheck 等真实项目为主线，用多个专题案例扩展 Agent 的应用边界。

正式领导审核稿及当前授课组织基线：

`docs/outline/training-4-session-leadership-proposal.md`

辅助材料：

- 8 个内容单元：`docs/outline/training-series-plan.md`（仅作为内容组织，不再作为现场场次数）
- 4 次授课详细评审稿：`docs/outline/training-4-session-review-draft.md`

当前统一采用：

`13 / 2 / 45 / 678`

原则：

> **1～8 管“内容怎么维护”，4 次讲座管“现场怎么讲”。后续 PPT、截图、录屏、讲课脚本和案例准备一律按四场讲座组织。**

原则：

> **章节结构负责“知识怎样组织”，四场讲座负责“现场怎样讲”。两者不要求一一对应。**

素材管理原则：

> **一讲一稿、一讲一清单。**

每场讲义对应独立素材清单：

- 第一讲：`docs/lectures/01-api-to-agent-media-checklist.md`
- 第二讲：`docs/lectures/02-department-knowledge-base-media-checklist.md`
- 第三讲：`docs/lectures/03-agent-common-runtime-tools-media-checklist.md`
- 第四讲：`docs/lectures/04-agent-engineering-practice-media-checklist.md`

总控文件 `docs/outline/media-capture-checklist.md` 只维护统一规范、四讲入口和跨讲复用素材，不再重复维护所有明细。

当前四场最终讲义正文：

- 第一讲：`docs/lectures/01-api-to-agent.md`
- 第二讲：`docs/lectures/02-department-knowledge-base.md`
- 第三讲：`docs/lectures/03-agent-common-runtime-tools.md`
- 第四讲：`docs/lectures/04-agent-engineering-practice.md`
- 总索引：`docs/lectures/README.md`

---

# 模块一：模型怎么调用

## 3.1 要回答的核心问题

> **我们在 WebUI 里输入一句话之后，背后到底发生了什么？**

本模块从内网 Qwen 模型的实际服务出发，把“大模型”从抽象概念还原为一个可以被 HTTP 请求调用的计算服务。

---

## 3.2 内网模型环境

当前培训基线：

- 模型：`Qwen3.6-35B-A3B-W8A8-Ascend`；
- Context Window：131072；
- 支持工具调用；
- 支持 Thinking 开关；
- 当前部署描述：两个华为昇腾节点；
- 当前多模态实测：OpenAI Chat 单图、SSE、多图、Vision + Tool Calling 均通过；
- Anthropic Base64 Image 已通过；
- Responses Vision 旧测试请求曾因漏 `detail` 必填字段返回 400；r4 已按当前 OpenAPI Schema 修正并正式验证 PASS。

注意：

> 上述模型服务的具体接口兼容性、部署实例、协议行为和功能状态，必须以后续仓库实测证据为准，不根据模型名称推断。

---

## 3.3 从 HTTP 开始理解模型 API

需要讲清：

- HTTP 是什么；
- URL / Endpoint；
- GET / POST；
- Header；
- API Key；
- JSON；
- Request；
- Response；
- HTTP Status Code。

建议直接使用真实请求，而不是先讲大量网络协议理论。

### 示例

`GET /v1/models`

用于说明：

> 客户端向模型服务发送请求，服务返回 JSON 数据。

再进入：

`POST Chat API`

解释消息如何被提交给模型。


### Cherry Studio Network 现场抓包

模块一增加一组主 Demo：

> **从 Cherry Studio 聊天界面直接打开 DevTools / Network，观察模型应用到底怎样调用 API。**

现场依次观察：

1. 刷新模型列表时的 `GET /v1/models`；
2. 第一轮普通文本 Chat Request；
3. 第二轮连续追问时，历史消息 / 会话状态如何进入下一次模型调用；
4. 多模态图片在 Request Body 中采用什么实际结构；
5. `stream=true` 后 SSE / EventStream 怎样持续返回。

原则：

> **不预设 Cherry Studio 当前版本一定怎样组织上下文或图片，而是以实际 Network Request / Response 为准。**

这一 Demo 用来建立：

~~~text
Chat UI
→ Client / Harness
→ HTTP Request
→ Model API
→ Streaming Response
→ UI Render
~~~

的第一层工程直觉，并为 Context、Vision、SSE 和后续 Agent Harness 铺路。

对应截图占位：`API-NET-01` ～ `API-NET-07`。

---

## 3.4 流式与非流式

需要通过真实请求对比：

### 非流式

请求发出  
→ 服务推理  
→ 完整结果一次返回。

### 流式

请求发出  
→ 服务开始产生结果  
→ 通过 SSE 持续返回事件。

重点讲：

- SSE；
- event / data；
- 为什么聊天界面能够“一个字一个字”显示；
- 为什么 TTFT 对体验非常重要；
- 用离线 HTML Demo 直观看不同 Tokens/s 的主观体验。

### Demo：Token 输出速率体感

文件：

`demos/token-output-speed/index.html`

来源：

`aaravchour/token-speed-visualiser`（Apache-2.0），培训仓库只做中文化、离线化和通用速率预设改造。

现场建议：

`5 → 20 → 50 → 100 tok/s`

然后使用 Race Mode 对比：

`5 / 30 / 120 tok/s`

重点不是把演示值当成真实模型 Benchmark，而是建立：

`TTFT → Tokens/s → Total Latency`

三者的区别。

---

## 3.5 内网接口实测

重点覆盖：

- `/v1/models`
- Chat API
- `/tokenize`
- `/detokenize`
- `/version`
- `/metrics`
- `/openapi.json`
- `/v1/messages/count_tokens`

并验证：

- 非流式；
- 流式；
- Thinking On / Off；
- Tool Calling；
- Tool Result 回灌闭环；
- 单图 / 多图 / Vision SSE / Vision + Tool Calling。

---

## 3.6 OpenAI / Codex / Anthropic 接口兼容

不是只讲“兼容 OpenAI”。

需要展示目前实测涉及的三种接口风格：

### OpenAI Chat Completions

关注：

- messages；
- 非流式 / 流式；
- tool_calls。

### OpenAI Responses / Codex 风格

关注：

- input / response；
- 流式事件；
- function_call。

### Anthropic Messages / Claude 风格

关注：

- Messages；
- content blocks；
- tool_use；
- 流式事件。

培训目标不是记住三套 JSON，而是理解：

> **同一个模型服务可以通过不同兼容协议接入不同客户端和 Agent。**

当前实测基线：
- OpenAI Chat：文本 / SSE / Thinking / Tool Loop / Vision PASS；
- Responses：文本 / SSE / Tool Loop PASS，Vision 待按 OpenAPI Schema 修正复测；
- Anthropic：文本 / SSE / count_tokens / Tool Loop / Vision PASS，但 thinking.type=disabled 未观察到生效。

---

### System Prompt、附件与 Prompt Engineering

第一讲增加三个基础问题：

1. **System Prompt 是什么？**
   - OpenAI Chat：`system/developer message`；
   - OpenAI Responses：`instructions`；
   - Anthropic Messages：顶层 `system`；
   - Cherry Assistant / Open WebUI Workspace Model 负责把这类长期指令持续注入模型调用。

2. **文件附件怎样进入模型？**
   - Client Parse → Text → Context；
   - Native File / Document Input；
   - Vision Image Input；
   - Full Context；
   - Knowledge / RAG。
   - 统一强调：UI 上“上传文件”不等于底层一定“转成文本全部塞进 Context”。

3. **Prompt Engineering 怎么讲？**
   - 官方稳定原则优先：Task / Context / Constraints / Output / Examples / Verification；
   - RTF、CO-STAR、CRISPE 只做社区记忆框架简介，不作为标准；
   - 工程任务优先 Goal / Current State / Constraints / Acceptance / Verification，而不是只强调“角色扮演”。

证据：

`docs/references/system-prompt-file-input-prompt-engineering-2026-09.md`

## 3.7 Token：为什么模型调用有成本

结合：

- `/tokenize`
- `/detokenize`

实际演示：

文本  
→ Token IDs  
→ Token 数量  
→ 再解码回文本。

重点解释：

- Token 不等于汉字；
- Token 不等于英文单词；
- 上下文长度通常以 Token 计；
- System Prompt、历史消息、代码、文档和工具返回值都要进入上下文；
- Agent 工作时 Token 消耗为什么增长很快。

---

## 3.8 Context Window

围绕内网模型宣称的 131072 上下文解释：

- 上下文是什么；
- 131072 表示什么；
- 长上下文不等于“可以无限塞资料”；
- 输入越长，Prefill 成本越高；
- Agent 为什么需要控制上下文；
- 为什么要做检索、摘要、项目规则和上下文管理。

后续可结合 model-metric 长上下文测试结果进一步说明。

---

## 3.9 Thinking / CoT

重点回答：

1. CoT（Chain-of-Thought）是什么；
2. 2022 年 CoT Prompting / Zero-shot CoT 已系统提出，CoT 不是从 DeepSeek-R1 才出现；
3. 2024 年 o1、2025 年 DeepSeek-R1 为什么让“长推理 / reasoning model”成为大众显著感知的产品形态；
4. Qwen 的 Thinking / Non-Thinking 与 CoT 是什么关系；
5. 为什么复杂任务可能受益于更多 test-time compute；
6. 为什么 Thinking 会增加 Token、TTFT、总耗时和尾延迟；
7. 哪些任务应该开 Thinking，哪些任务应优先快速回答；
8. 为什么可见 reasoning 文本不能等同于绝对可信的“模型内部执行日志”。

培训中结合内网 Thinking On / Off 实测，建立：

> **Thinking 是一种推理预算；不是所有任务都应该默认把预算拉满。**

工程建议：

> **简单任务优先快速模型 / Non-Thinking；复杂分析、疑难 Debug、系统设计等节点再升级推理预算。**

---

## 3.10 MoE

需要回答：

- MoE 是什么；
- Router / Gate 如何为 Token 选择 Experts；
- Total Parameters 与 Activated Parameters 的区别；
- 为什么总参数可以很大，但每 Token 只执行部分专家；
- MoE 主要节省的是每 Token 的有效计算量，而不是简单把模型权重显存降到 Active Parameters 的规模；
- 为什么仍然需要考虑总权重驻留 / 分布、Expert Parallel、All-to-All 通信和 Load Balance；
- 为什么 KV Cache、长 Context 和并发不会因为“A3B”自动按 3/35 比例下降。

结合 Qwen3.6-35B-A3B：

> **35B 是总参数容量，A3B 是约 3B 激活参数；官方模型卡当前给出 256 Experts，每 Token 8 Routed + 1 Shared。**

与本培训核心关联：

> **模型名称中的参数量不能直接等价为每 Token 都执行相同规模的计算；Active Parameters 也不能直接等价为部署所需权重内存。**

---

## 3.11 推理性能基础

讲清：

- Prefill；
- Decode；
- TTFT；
- Tokens/s；
- KV Cache；
- 并发；
- 排队；
- 长上下文。

结合 model-metric 案例预埋后续内容。

---

## 3.12 统一能力 Demo：鹈鹕骑自行车

统一使用：

> **创建一个单文件 HTML，用 SVG、CSS 和 JavaScript 生成一只鹈鹕骑自行车的循环动画。**

为什么选它：

- 任务短，适合现场；
- “鹈鹕 + 自行车”属于非典型组合，不只是套常见网页模板；
- 同时涉及自然语言理解、SVG 几何、CSS / JS、空间组合和动画；
- 结果高度可视化，学员无需阅读大量代码也能发现问题；
- 生成后必须真正运行，非常适合引出 Agent 的执行与验证闭环。

Demo 分两轮：

### A. 不同模型，同一种 Chat 工作方式

固定 Prompt 和运行条件，观察指令遵循、可执行性、构图、动画逻辑和一次完成度，用于展示 Model Capability。

### B. 同一个模型，Chat vs Agent

Chat：Prompt → 代码 → 人复制/运行/发现问题/再提问。

Agent：Goal → 写文件 → 运行 → Browser 观察 → 修改 → 再验证 → Deliver。

用于展示 Harness Capability。

注意：

> **这是教学演示题，不是严肃模型 Benchmark。单题结果不得外推成模型综合排名。**

完整规范：demos/pelican-bicycle/README.md

---

## 3.13 本模块结论

> **大模型不是一个神秘的聊天框，而是一个可以通过协议调用、存在上下文和实时计算成本的模型服务。**

---

## 3.14 当前已有材料

已存在：

- `docs/chapters/01-intranet-qwen-api.md`
- `docs/chapters/02-chat-to-agent-harness.md`
- `demos/pelican-bicycle/README.md`
- `api/qwen/qwen_api_training_test.py`
- `api/qwen/reports/`
- `api/qwen/results/`
- `docs/references/`

状态：

> **模块一已达到“可用于培训”：文本 API、三协议 Tool Loop、多模态 Vision、Thinking 专项复测均有实测证据；后续主要补 Responses Vision 修正版、长上下文/性能专项数据、截图和 PPT 视觉化。**

---

# 模块二：为什么只有 Chat 不够

## 4.1 要回答的核心问题

> **既然模型已经能回答问题，为什么还需要 Agent？**

---

## 4.2 Chat 的典型工作方式

`User Prompt → Model → Answer`

适合：

- 问答；
- 翻译；
- 改写；
- 概念解释；
- 短文本生成；
- 简单分析。

问题是：

回答完成之后，真正的工程工作通常才刚刚开始。

例如模型告诉你：

> 修改配置文件，然后运行 Docker Compose。

但 Chat 本身不一定：

- 打开你的配置文件；
- 修改它；
- 登录服务器；
- 执行 Docker；
- 查看日志；
- 发现错误；
- 修复错误；
- 再次验证。

---

## 4.3 Open WebUI / Cherry Studio：从 Chat 工作台走向 Knowledge、RAG 与 Agent

到 2026 年，Open WebUI 和 Cherry Studio 都不能再简单等同于“纯 Chat”。

培训用它们展示能力递进：

~~~text
Raw Model
→ Chat
→ Assistant / Model Preset
→ File / Knowledge
→ RAG
→ Web / MCP / Tools
→ Agentic Retrieval / Agent
~~~

### Open WebUI

当前内网部署：`v0.11.0`。

定位更新为：

> **既可以作为个人 Note / Knowledge 工作台，也适合作为部门统一 AI 门户、Workspace 与共享 Knowledge 入口。**

当前内网已实际走通：

- 个人 Note / Markdown；
- 上传文档；
- Full Context / Focused Retrieval；
- 当前未配置 Embedding，因此存在“未向量化”提示；
- Knowledge 绑定 Workspace / Model；
- 选择对应 Workspace 后基于资料回答。

需要演示：

- Workspace / Model；
- System Prompt 与参数；
- 个人 Note / Document；
- Knowledge Base；
- Full Context vs Focused Retrieval；
- “未配置 Embedding但仍能使用知识”与“Vector Retrieval 已生效”之间的区别；
- Shared Knowledge / Group / ACL；
- 后续再根据当前实例实测补 Hybrid / Native Knowledge Tools / Agentic Retrieval。

### Cherry Studio

定位：

> **更适合作为工程师个人桌面多模型 AI 工作台。**

需要演示：

- Custom Provider；
- Assistant / Topic；
- Assistant Prompt；
- 模型参数与 Thinking；
- Vision / Drawing；
- Knowledge Base；
- Embedding；
- Rerank；
- Embedding=None 时的 BM25 检索；
- Knowledge 绑定 Agent；
- MCP / Web Search / Work。

### Cherry Assistant ↔ Open WebUI Workspace Model

第一讲增加显式一一对应：

```text
Cherry Assistant
↔ Open WebUI Workspace Model

Assistant Instructions
↔ System Prompt

Cherry Knowledge Base
↔ Open WebUI Knowledge / Note

Assistant 绑定 Knowledge
↔ Workspace Model 绑定 Knowledge
```

统一抽象：

```text
Base Model
+ System Prompt / Instructions
+ Knowledge
+ Parameters
+ Tools
→ Reusable Assistant / Application Preset
```

并用同一 `qwen3.6`、同一 System Prompt、同一份 Qwen API 测试资料、同一问题做双端演示。

关键教学边界：

> **Assistant / Workspace Model 是应用层封装，不是重新训练模型；只有再加入 Runtime、连续 Tool Loop、Observe、Verify、Iterate，才进入完整 Agent。**

### Cherry Studio 与 Open WebUI 的数据边界

第一讲增加一组工作台对照，不做“谁更好”的产品排名，而是比较：

```text
Cherry Studio
→ Desktop / Local-first
→ 本机管理个人配置、Knowledge、Assistant
→ 通过 API 调模型

Open WebUI v0.11.0
→ Browser / Server-side
→ 服务端集中管理 Chat、Note、Knowledge、Workspace、ACL
→ 服务端调模型
```

当前内网 Open WebUI 已实测：

- 个人 Note / Markdown；
- Note 场景直接对话；
- 上传文档；
- Full Context / Focused Retrieval；
- 未配置 Embedding / 未向量化提示；
- Workspace / Model 设置 System Prompt；
- Workspace 绑定已有 Note / Knowledge；
- 选择 Workspace 后基于知识问答。

Cherry Assistant 与 Open WebUI Workspace Model 都可以理解为：

```text
Base Model
+ System Prompt / Instructions
+ Parameters
+ Knowledge
+ Tools
→ Reusable Application Preset
```

二者都不是重新训练模型，也不应仅因为 UI 中叫 Assistant/Model 就等同于完整 Agent。

数据边界必须讲清：

> **Local / Server-side Storage 与 Model Provider 是两个独立维度。资料存在本机或内网服务器，不代表进入模型 Context 的内容不会通过 API 发送给配置的 Model Provider。**

### 用 Cherry Studio 解释“RAG 不等于向量数据库”

Cherry Studio 当前官方知识库支持：

> **Embedding Model = None → 使用 BM25 关键词检索。**

因此培训统一采用：

> **RAG = Retrieval → Context Augmentation → Generation。**

进一步区分两个独立维度：

1. Retrieval Algorithm：BM25 / Vector / Hybrid / grep / Search Engine；
2. Retrieval Control：Pipeline RAG / Agentic Retrieval。

所以：

> **Agentic Retrieval 与 Vector Retrieval 不是二选一；Agent 可以主动调用 BM25、向量、Hybrid 或全文搜索。**

完整讲义：

`docs/chapters/02-chat-workbenches-and-rag.md`

部门级知识架构进一步采用：

> **Source of Truth 与 Retrieval Index 分离。**

知识原文保留在 Git / Wiki / 文件库 / DB / API 等权威来源；BM25、Vector、Rerank 作为可重建检索层；Open WebUI、Cherry Studio 和 Agent 作为不同消费入口。

推荐定位：

- Open WebUI：个人 Note/Knowledge + Workspace，同时承担部门共享 Knowledge Service / AI Portal；
- Cherry Studio：个人 Knowledge Workspace；
- Coding / General Agent：跨 Repo、文件、API、DB、共享 KB 的 Agentic Retrieval 与任务执行层。

详细架构：

`docs/architecture/department-knowledge-architecture.md`

---

## 4.3.1 专题：部门知识库怎么设计、怎么建、怎么用

由于部门知识库即将进入实际建设和使用阶段，本专题不只介绍 RAG 概念，而要回答实际建设问题：

1. 部门有哪些知识资产类型；
2. 哪些资产应该保留在 Git / Wiki / DMS / DB / API；
3. 哪些文档优先使用 Markdown，哪些需要保留 PDF / DOCX / PPTX / XLSX 原件；
4. 扫描 PDF、表格、图片、音视频如何进入知识体系；
5. Metadata、版本、Owner、有效期和数据分级怎样设计；
6. RAG 与向量化是什么关系，哪些资料需要向量化、哪些不需要；
7. BM25、Embedding、Rerank 分别解决什么问题；
8. Chunk 应怎样按文档逻辑结构设计；
9. Cherry Studio、Open WebUI、Coding/General Agent 的 Retrieval 方式有什么差异；
10. Pipeline RAG 与 Agentic Retrieval 分别适合什么任务；
11. Full Context 什么时候反而比 RAG 更合适；
12. 知识如何同步、更新、失效和重新索引；
13. ACL 为什么必须发生在 Retrieval 之前；
14. 如何提供文件、章节、页码、Commit、Version 等可追溯引用；
15. 如何处理重复、冲突和过期知识；
16. 如何建立 Retrieval Test Set 和知识库回归测试；
17. 如何测试“无答案时不编”；
18. 为什么“检索到了”不等于 LLM 一定能在长 Context 中使用好；
19. 标称 Context Window 与 Effective Context 有什么区别；
20. 为什么 Top-K 不是越大越好，如何用 Rerank / Metadata / 去重 / Evidence Budget 控制最终 Context；
21. Full Context、Pipeline RAG 和 Agentic Retrieval 应该怎样按资料规模与问题类型路由；
22. 部门近期应该怎样从一个可控专题开始试点。

统一架构原则：

> **Source 是长期知识资产；Index 是可重建派生资产；Retrieval Tool 是访问方式；Client / Agent 是可替换入口。**

同时新增一条 Context 原则：

> **Retriever 找到正确资料只是第一关；检索结果进入 Prompt 后，还存在 LLM 的 In-context Retrieval / Context Utilization 问题。Context Window 是容量上限，不是有效知识容量保证。**

因此知识库链路应包含：

`Candidate Recall → Rerank / Filter → Evidence Budget → Context Packing → LLM`

而不是简单：

`Top-K 越大 → 塞得越多 → 回答越好`。

推荐工具定位：

- Open WebUI：部门共享 Knowledge Service / AI Portal；
- Cherry Studio：个人 Knowledge Workspace；
- Coding / General Agent：跨 Git、Workspace、文件、API、DB、共享 KB 的 Agentic Retrieval 与任务执行层。

教学主讲义：

docs/chapters/03-department-knowledge-base-teaching.md

完整技术稿 / 深入阅读：

docs/chapters/03-department-knowledge-base.md

架构文档：

docs/architecture/department-knowledge-architecture.md

知识库专项 Demo 统一采用同一批真实 Qwen 资料，按三层递进：

~~~text
Cherry Studio
→ 演示知识怎么建：Parse / Chunk / BM25 / Embedding / Rerank

Open WebUI
→ 先演示个人 Note/Document → Full Context/Focused → Workspace，再演示 Shared KB / Group / ACL

Agent
→ 演示知识怎么被编排：Shared RAG KB + Git / File + API / Metrics
~~~

这里 Agent 不是第三套互斥知识库，而是更上层的 Knowledge Orchestrator：

> **Agent 可以把 RAG 知识库、全文搜索、Git、API 和数据库都作为 Retrieval Tools 统一调用。**

统一 Demo 规范：

demos/knowledge-retrieval/README.md

同时使用固定问题集对 BM25 Only / Vector / Hybrid + Rerank / Agentic Retrieval 做可比验证。

---

## 4.4 Agent 的核心变化

Agent 的基本组成：

`Model + Context + Workspace + Tools + Loop`

工作方式变成：

目标  
→ 规划  
→ 阅读环境  
→ 执行动作  
→ 获取结果  
→ 判断  
→ 继续执行  
→ 验证  
→ 交付。

---

## 4.5 Workspace 为什么重要

Workspace 让模型面对的不再只是一段 Prompt，而是一个真实项目。

例如：

- 源代码；
- Markdown 文档；
- 测试数据；
- 配置文件；
- Git 历史；
- 项目规范；
- 构建脚本。

因此可以从：

> “帮我写一个登录页面”

提升到：

> “阅读现有项目设计规范，在现有架构中增加管理员登录，完成自动化测试和浏览器验收，再提交代码。”

---

## 4.6 Agent 工具不等于 Agent 能力

一个关键认知：

> **Agent 的价值不在于有多少工具，而在于能否围绕目标连续使用工具并验证结果。**

需要避免把 Agent 培训变成：

“这个软件有 Terminal、那个软件有 Browser、另一个软件有 MCP。”

---

## 4.7 十个代表性 Agent：先横向比较，再收束到 Harness 共性

培训至少覆盖：

- ZCode；
- Codex；
- Claude Code；
- OpenCode；
- DeepSeek Harness（DSH）；
- Pi；
- Cline；
- Kilo Code；
- Hermes Agent。
- WorkBuddy。

不逐个介绍菜单，也不做简单“谁最好”的排名。

统一从以下维度理解：

- 产品定位：Terminal / IDE / Desktop / Workspace / Cloud；
- 是否开源以及开源范围；
- Model / Provider；
- 接企业自有 API 的难易程度；
- 是否支持 OpenAI Chat / Responses / Anthropic 等协议；
- System Prompt / 项目规则；
- Workspace；
- Context / Session / Compaction；
- Agent Loop；
- Shell / File / Git；
- Browser / Computer；
- Tool Registry / Tool Schema；
- MCP / Plugin / Skill；
- Sub-agent / Task Delegation；
- Permission / Approval / Sandbox；
- Test / Verification / Trace；
- Windows / Linux / Remote 使用方式。

详细资料统一维护在：

`docs/references/coding-agent-comparison-2026-09.md`

### 4.7.1 五种代表路线

**厂商旗舰 Harness：**

- Codex；
- Claude Code；
- ZCode。

观察模型厂商如何围绕自家模型做深度 Harness 联调。

**模型中立的开源 Harness：**

- OpenCode；
- Cline；
- Kilo Code。

观察 Provider 抽象、BYOK、本地模型和企业内网 API 接入。

**Harness 架构路线：**

- DeepSeek Harness；
- Pi。

DSH 体现“Everything is a Plugin”，Pi 体现 Minimal Harness，一繁一简，用于解释 Harness 本身。

**长期运行的通用自主 Agent：**

- Hermes Agent。

Hermes 用于展示 Agent 从“完成一次编码任务”继续扩展到持久 Memory、Skills、自学习循环、Cron、多平台 Gateway、Subagent 和多运行后端。

### 4.7.2 用公开实验说明 Harness 真的影响结果

引入 FrontierHarness Eval v1.0：

> **固定同一个 Kimi K3、相同任务和运行环境，只替换 Harness。**

该实验覆盖 30 个软件工程任务、12 个 Harness 配置、360 次 Evaluation。

与培训相关的冻结结果中，Codex、DSH Creator、Claude Code、Pi、OpenCode、Hermes 等在 Pass Rate、成本、缓存和运行时间上存在明显差异；Hermes v0.20.4 在该实验中 Pass Rate 为 50.0%。

必须同时说明边界：

- 它是特定模型、特定任务和特定版本下的受控实验；
- 不是“Agent 永久排行榜”；
- ZCode、Cline、Kilo Code 没有进入该 v1.0 冻结测试，不能自行补分数；
- 不同模型、任务、配置下，排序可能改变。

因此真正要传递的是：

> **Agent Effectiveness = Model × Harness × Task × Configuration × Runtime**

### 4.7.3 对部门内网模型再做一次我们自己的固定模型实验

公网 Benchmark 只作为证据和方法参考。

后续应固定：

- 同一个内网 qwen3.6；
- 同一个 Git 仓库；
- 同一个任务；
- 同一个 AGENTS.md；
- 同一时间限制；
- 同一权限范围；

分别接入 ZCode / Codex / Claude Code / OpenCode / DSH / Pi / Cline / Kilo / Hermes。

记录：

- 任务完成情况；
- 人工介入次数；
- Tool Call 数；
- 输入 / 输出 Token；
- TTFT 和总耗时；
- 是否主动运行测试；
- 是否主动修复；
- 最终 Git Diff；
- 是否错误声称“已完成”。

这样可以把“公网 Harness Benchmark”转换成与部门实际部署直接相关的证据。

### 4.7.3A WorkBuddy：Chat Surface 背后的 Workspace 与 Runtime

WorkBuddy 作为补充案例，重点不做 Coding Agent 排名，而是解释三个机制：

- Skill Marketplace / 社区 Skill；
- Chat / Task Surface 背后的 Workspace、文件、终端、Browser 和产物；
- 企业智能体的云端 Runtime / Sandbox。

它适合用来说明：

> **界面像 Chat，不代表后端只是 Prompt → Answer；当会话绑定 Workspace、Tools 和 Runtime 后，同一个对话入口已经可以成为完整 Agent 工作台。**

同时必须明确：

> **并非所有 Chat 产品或所有会话都天然拥有完整虚拟容器。是否存在 Sandbox、是否持久化、能执行什么，需要按具体产品和模式验证。**

建议截图编号：`AGENT-WB-01` ～ `AGENT-WB-04`。

### 4.7.4 最后收束到 Agent Harness

培训引入统一概念：

> **Agent Harness**

可以把它理解为模型外面的运行与工程环境：

Instructions + Context + Loop + Tools + State + Permission + Verification + UI

DeepSeek Harness 官方当前直接使用“Agent = Model + Harness”，Pi 官方定位为 minimal agent harness。

因此重点不是记住八个产品，而是理解：

> **界面和实现会变化，Harness 要解决的问题高度相似。**

---

## 4.8 本模块短案例

优先复用“鹈鹕骑自行车”统一 Demo，使用同一个模型对比：

### Chat

Prompt → 返回 HTML → 人负责保存、运行、观察和继续提问。

### Agent

Goal → 创建文件 → 启动页面 → 浏览器验证 → 修复 → 再验证 → Git Diff。

这样可以把变量拆开：

- 不同模型，同一 Chat 流程 → 看 Model Capability；
- 同一模型，Chat vs Agent → 看 Harness Capability。

另外可补一个真实仓库小任务：

“读取项目 → 找到文件 → 修改 → 启动 → 浏览器验证 → 修复 → Git Diff。”

通过两种任务链说明差异。

---

## 4.9 本模块结论

> **Chat 给答案；Agent 更接近围绕目标连续完成工作。**

---

# 专题桥梁：把 Agent 拆开看——Agent 的共同结构

在进入 File、Shell、Git、Browser、SSH 等具体工具之前，先建立一个跨产品的统一 Agent 心智模型。

核心不是继续介绍 Codex、Hermes、OpenCode、Claude Code、Cline、Pi 等产品，而是回答：

- Agent Harness 到底是什么；
- System / Identity / Persona 与项目规则是什么关系；
- AGENTS.md / CLAUDE.md / SOUL.md / MEMORY.md 分别在解决什么问题；
- Workspace、Context、Plan、Memory 分别是什么；
- Tool、API、MCP、Skill 的边界；
- Browser Use、Computer Use、Playwright 的区别；
- Permission / Sandbox / Verification 为什么是 Agent 的核心机制；
- Sub-agent 如何隔离任务与上下文；
- CLI / GUI / IDE / Web 为什么只是不同 Surface，应该如何选择。

统一抽象：

> **Agent = Model + Harness；Harness = Instructions + Context + Workspace + State + Tools + Permission + Verification + Interface。**

强调：

> **不同产品的文件名和 UI 会变化，但它们解决的是同一组底层问题。**

例如：

- Codex 原生支持层级 AGENTS.md；
- Hermes 把 Identity、User、Persistent Memory、Project Context 分别映射为 SOUL.md、USER.md、MEMORY.md、AGENTS.md / .hermes.md；
- Claude Code 使用 CLAUDE.md 等机制承载项目 / 用户上下文；
- 其他 Agent 也可能使用 Rules、Memory Store、Plan Mode、Task State 等不同实现。

完整讲义：

docs/chapters/04-agent-common-mechanisms.md

本专题结束后再进入模块三，让学员带着同一套框架理解 File / Shell / Git / Browser / SSH / API，而不是把后续内容看成一堆孤立工具。

---

## 4.3 第一套连续案例：ZCode 贯穿模块三～五

为了降低教学时频繁切换 Agent UI 带来的认知负担，模块三～五的第一套连续案例统一使用 **ZCode**：

```text
模块三
Workspace / File / Terminal / Browser / Git / Permission
        ↓
模块四
Raw API → MCP → Skill → Command / Plugin
        ↓
模块五
AGENTS.md → Memory → Command → Skill → Script/Test/CI → Team Assets
```

目的不是把 ZCode 变成培训主角，而是保持一个稳定 Surface，把注意力放到底层机制。

后续 Codex、Hermes、OpenCode、WorkBuddy 等用于说明：

> **相同问题在不同 Harness 中如何实现，以及哪些资产可以迁移。**

ZCode 当前案例资产：

- `demos/zcode-real-world/`
- `docs/cases/zcode-agent-real-world.md`
- `docs/references/zcode-agent-evidence-2026-09.md`
- `demos/agent-tool-integration/zcode-implementation-plan.md`

---

# 模块三：Agent 如何操作真实世界

## 5.1 要回答的核心问题

> **模型本身只能生成 Token，它为什么能够改代码、开浏览器、SSH 服务器？**

答案：

> **因为 Agent 把模型和外部工具连接起来。**

---

## 5.2 File System

Agent 可以：

- 读取文件；
- 搜索代码；
- 修改文件；
- 创建文件；
- 对比 Diff。

需要强调：

> 文件是 Agent 与真实工程项目连接的第一层。

---

## 5.3 Shell

通过 Shell 可以操作：

- Git；
- Python；
- npm；
- Docker；
- SSH；
- curl；
- 编译器；
- 测试框架；
- 系统日志。

Shell 是工程 Agent 最重要的通用工具之一。

---

## 5.4 Git

Agent 与 Git 配合形成：

读取仓库  
→ 修改  
→ Diff  
→ Test  
→ Commit  
→ Push  
→ CI。

重点讲：

> Git 不只是代码托管，也是 Agent 操作工程项目时非常重要的状态管理和审计机制。

---

## 5.5 浏览器

分清：

### Browser Use

让 Agent 理解页面并进行交互。

### Playwright

程序化、可重复、可断言的浏览器自动化。

### Computer Use

针对 GUI 环境进行视觉观察与鼠标键盘操作。

### 爬虫

主要目标是结构化获取网页数据。

不要把四者混为一谈。

---

## 5.6 SSH 与服务器

真实任务链：

Agent  
→ SSH  
→ 查看目录  
→ 查看日志  
→ 修改配置  
→ Docker 部署  
→ 检查服务  
→ 发请求验证  
→ 根据结果继续修复。

这是从“告诉工程师命令”到“协助执行完整运维任务”的关键变化。

---

## 5.7 API

Agent 不只能调用 LLM API。

还可以连接：

- GitHub；
- 企业内部系统；
- 数据服务；
- 搜索；
- 监控；
- CI/CD；
- 自研服务。

这为下一模块 MCP / Skill 铺垫。

---

## 5.8 Agent Runtime / Environment Engineering

模块三新增一个必须单独讲清的层：

```text
Model
→ Harness
→ Tool
→ Execution Environment
→ Git / Python / Node/npm / Docker / Compiler
→ Dependencies / Internal Services
```

重点强调：

- Terminal 是执行通道，不等于工具链已经存在；
- ZCode 有 Git 工作流集成，但内网标准环境仍应显式安装并验证 Git CLI；
- Python、Node/npm、Docker、编译器属于宿主机 / WSL / Container / Remote Host 的 Toolchain；
- 增加 CLI / Python / Node.js 选择规则：成熟专用 CLI 优先；复杂编排/数据处理优先 Python；Web/JS/浏览器工具链优先考虑 Node.js；最终沿用项目原生技术栈；
- Remote Workspace 中 Agent Runtime 和命令都在目标环境执行；
- 内网不能依赖 Agent 临时访问公网安装依赖；
- 需要离线安装包、内部 PyPI/npm/OS/Container Registry、CA、Proxy、DNS、版本与 Lock 文件；
- Agent 配置同步与 Runtime 环境构建是两个独立问题。

完整案例：

`docs/cases/agent-runtime-environment-intranet.md`

环境 Preflight：

- `demos/zcode-real-world/check-agent-env.ps1`
- `demos/zcode-real-world/check-agent-env.sh`

### 5.8.1 环境配置

给工程人员一套最低可用 Agent 工作环境概念：

- Git；
- Python；
- pip / uv 等 Python 环境管理；
- Node.js / npm；
- Docker；
- 浏览器；
- SSH；
- 常用 CLI；
- 编辑器 / Agent。

重点不是安装教程本身，而是理解：

> **Agent 能力上限很大程度取决于它所在工作环境中有哪些可靠工具。**

---

## 5.9 本模块案例

优先结合真实项目：

- 服务器远程部署；
- 浏览器 UI Visual QA；
- API 自动化测试；
- GitHub Actions。

---

## 5.10 本模块结论

> **模型负责判断和生成，工具负责真正读取、执行和改变外部世界。**

---

# 模块四：如何让 Agent 掌握工具

## 6.1 要回答的核心问题

> **API、MCP、Skill、Plugin、Command、Hook 到底是什么关系？**

---

## 6.2 API：最底层的能力接口

API 面向程序。

例如：

`POST /v1/chat/completions`

本质是明确约定：

- 请求到哪里；
- 输入什么；
- 返回什么。

API 的优势：

- 明确；
- 稳定；
- 容易自动化；
- 与具体 Agent 无关。

---

## 6.3 为什么已有 API 还需要 MCP

如果每个 Agent 都为每个系统单独：

- 阅读 API 文档；
- 自己构造参数；
- 自己管理接口描述；

连接成本会很高。

MCP 更关注：

> **如何把外部 Tools / Resources / Prompts 以统一方式暴露给 Agent。**

因此可以理解为：

`现有系统 / API → MCP Server → Agent`

API 和 MCP 不是替代关系。

---

## 6.4 Skill 是什么

Skill 重点不是“提供一个接口”，而是：

> **教 Agent 怎样完成一类任务。**

Skill 可以包含：

- 使用说明；
- Prompt；
- 工作步骤；
- 约束；
- 脚本；
- API / MCP 调用；
- 验证方式；
- 输出模板。

因此：

API 更像“能力接口”；  
MCP 更像“Agent 访问外部能力的一种标准化协议”；  
Skill 更像“可复用的任务方法”。

---

## 6.5 为什么有 MCP 还需要 Skill

示例：

MCP 提供 GitHub 的：

- 读文件；
- 创建 Issue；
- Commit；
- PR。

但“如何完成一次规范的软件验收”不是一个单独工具。

Skill 可以规定：

读取 AGENTS.md  
→ 拉取 main  
→ 记录 SHA  
→ 安装依赖  
→ 单元测试  
→ 浏览器 Visual QA  
→ 修复  
→ 再测试  
→ Commit  
→ Push  
→ CI  
→ 验收报告。

因此：

> **MCP 告诉 Agent 能做什么；Skill 可以告诉 Agent 怎样把这些能力组合成一个可靠流程。**

---

## 6.6 Plugin

不同产品中的 Plugin 定义可能不同。

培训必须基于具体产品最新官方实现说明，不能假设所有 Agent 的 Plugin 含义完全相同。

教学重点：

> Plugin 通常用于打包或扩展 Agent 的外部能力，但必须结合具体工具定义理解。

---

## 6.7 Command

Command 适合把高频工作入口化。

例如：

- `/test`
- `/review`
- `/release`

它更像用户主动触发的标准动作。

---

## 6.8 Hook

Hook 适合事件触发。

例如：

- 修改后自动格式化；
- Commit 前运行测试；
- 工具调用前做权限检查。

Command 与 Hook 的区别：

> Command 更偏“主动调用”，Hook 更偏“事件触发”。

---

## 6.9 Skill 安装和创建

后续需要准备一个真正可演示的 Skill：

安装现有 Skill  
→ 查看 `SKILL.md`  
→ 理解目录结构  
→ 修改规则  
→ 创建自己的 Skill  
→ 在真实任务调用。

建议最终制作一个与部门工作有关的小型 Skill，而不是 Hello World。

---

## 6.10 本模块结论

可以用一张图收束：

`API / Service`  
↓  
`MCP / Tool Integration`  
↓  
`Agent Tools`  
↓  
`Skill / Workflow`  
↓  
`完成真实任务`

---

# 模块五：如何形成可复用资产

## 7.1 要回答的核心问题

> **如果明年我们不用今天这款 Agent，现在学的东西是不是都浪费了？**

答案应该是：

> **如果只学软件按钮，会；如果沉淀的是工程资产，就不会。**

---

## 7.2 AGENTS.md / 项目规则

直接使用本仓库根目录：

`AGENTS.md`

作为真实案例。

解释：

- 项目目标；
- 工作原则；
- 目录约束；
- 验证方式；
- 内容规则；
- 交付方式。

让学员理解：

> **项目规则是把“每次都重新提醒 Agent”变成“长期项目约束”的一种方法。**

---

## 7.3 Prompt

Prompt 不应该只理解为一句“魔法咒语”。

可沉淀：

- 分析模板；
- Review 模板；
- 测试模板；
- 调研模板；
- 文档生成模板。

重点从 Prompt Engineering 过渡到：

> **Context Engineering / Workflow Engineering。**

---

## 7.4 Skill

把成熟流程打包为可复用 Skill。

示例方向：

- API 验收 Skill；
- Web UI QA Skill；
- 项目 Release Skill；
- 文档转换 Skill。

---

## 7.5 脚本和工具

很多稳定、确定性的任务，不应该一直让模型重新生成。

应该沉淀成：

- Python 脚本；
- Shell；
- Playwright；
- 测试代码；
- CI Workflow。

核心原则：

> **模型负责不确定性判断，代码负责可重复执行。**

---

## 7.6 Memory

需要区分：

- 当前对话上下文；
- 项目文件中的显式规则；
- Agent / 产品提供的长期记忆。

重点讨论：

> 哪些内容应该依赖 Memory，哪些关键约束必须写回项目文件。

重要项目规则不应只依赖不可审计的隐式记忆。

---

## 7.7 全文搜索、语义检索与 RAG

### 全文搜索

按关键词匹配。

### Embedding / 语义检索

按语义相似度寻找内容。

### RAG

检索只是其中一步：

Query  
→ Retrieve  
→ 将相关内容加入 Context  
→ Model 生成答案。

核心结论：

> **语义检索是一种 Retrieval 方法；RAG 是“检索 + 上下文增强 + 生成”的完整模式。**

---

## 7.8 索引库 / 知识库

不要把“上传文件”直接等同于知识库能力。

需要讲清：

原始文档  
→ 解析  
→ Chunk  
→ Index  
→ Retrieval  
→ Context  
→ Generation。

---

## 7.9 Sub-agent

适合：

- 并行研究；
- 分模块分析；
- 独立 Review；
- 大任务拆分；
- 隔离上下文。

不要为了“多智能体”而多智能体。

判断标准：

> **任务是否真的可以拆分，并且拆分后收益是否大于协调成本。**

---

## 7.10 Git / CI 也是可复用资产

强调：

- Git 历史；
- Actions；
- Release；
- Docker；
- PyInstaller；
- 测试集；

本身都是让 Agent 更可靠的工程基础设施。

---

## 7.11 本模块结论

> **Agent 软件只是入口，真正形成长期竞争力的是 Prompt、规则、Skill、MCP、脚本、测试、CI、模板和知识资产。**

---

# 模块六：用真实项目证明 Agent 能完成什么

本模块不是单纯“案例展示”，也不再把所有案例视为同等粒度。

案例分为两类：

### A. 贯穿式完整工程案例

必须从需求讲到交付：

- **BMQuiz V2**：Web / Full-stack / Visual QA / Docker / Server / CI/CD；
- **FileCheck**：本地客户端 / CLI / GUI / 兼容性 / PyInstaller / GitHub Release。

完整案例统一回答：

`Problem → Requirement → Constraint → Research → Architecture → Plan → Implement → Test → QA → Review → Build → Release → Deploy → Verify → Assetize`

详细框架：

`docs/cases/end-to-end-agent-engineering-cases.md`

### B. 专题案例

只重点证明某类 Agent 能力：

- model-metric；
- Agent 服务器运维；
- IPsec VPN 数据分析；
- HyperFrames；
- 文档处理；
- Knowledge / RAG；
- 授权机制 / 协议行为研究；
- 网站安全测试。

每个案例需要尽量回答：

1. 原来工作是怎么做的；
2. AI / Agent 参与了哪一部分；
3. 使用了哪些工具；
4. 中间遇到了什么问题；
5. 人做了哪些关键判断；
6. 最终形成了什么可复用资产。

---

## 8.1 案例一：服务器运维

现有服务器案例从“SSH / Docker 功能展示”升级为真实工程交付案例，固定使用：

- **BMQuiz**：Docker / GHCR / Compose / health / application smoke / rollback；
- **model-metric**：systemd / journalctl / SQLite / API 语义验证。

完整案例设计：

`docs/cases/agent-server-operations.md`

### 展示内容

- SSH；
- 查看日志；
- Docker；
- 拉取镜像；
- 修改配置；
- 服务重启；
- 健康检查；
- 异常排查。

### 要传递的观点

> AI 不只是把命令写给工程师，而是可以围绕目标连续执行、观察和验证。

### 演示形式

优先：

- 现场 Demo；
- Terminal 录屏；
- PPT 保留关键截图作为备用。

---

## 8.2 案例二：浏览器 UI 自动测试

### 展示内容

- Chromium；
- Playwright；
- 页面导航；
- 点击；
- 表单；
- Console；
- Screenshot；
- Visual QA；
- 回归验证。

### 要传递的观点

> “代码测试通过”不等于“产品界面真的可用”。

Agent 可以把功能测试、浏览器操作和视觉检查结合起来。

---

## 8.3 案例三：API 开发与自动测试

- 自编 Postman：GET / POST 手工请求；
- Cherry Studio Network：真实应用请求；
- `qwen_api_training_test_v3.py`：自动化断言与回归；
- 当前基线：`20260930_095033`，28 PASS / 1 SKIP；
- model-metric：从单请求继续延伸到服务运行状态。

```text
Postman → Cherry Network → Python Test → Tool/Vision Ground Truth → /metrics → model-metric
```

> **从“手工调通一次”到“自动回归 + 持续观测”，才是 API 工程化。**
---

## 8.4 案例四：model-metric

项目已在内网部署上线。当前仓库可展示 `/metrics` 多实例采集、running/waiting、service TPS、KV、TTFT/Queue/Prefill/Decode/TPOT/ITL、覆盖率，以及 API Benchmark、Context Window、Endpoint Compatibility。

> **模型“能调用”不等于共享服务“好用”；要把单请求、服务遥测和主动压测放在一起看。**

详细教学案例：`docs/cases/model-metric-api-observability.md`。
---

## 8.5 案例五：Web 应用开发

优先使用：

- bmquiz；
- model-metric；
- wafer / map-test。

重点展示完整工程方法：

需求  
→ GitHub 调研  
→ 技术选型  
→ 架构  
→ UI 规范  
→ 文档先行  
→ Plan  
→ 分阶段开发  
→ Test  
→ Browser QA  
→ CI  
→ Docker  
→ Release。

### 核心观点

> **不要一上来就让 AI 写代码。**

AI 编码质量很大程度取决于：

- 需求是否清楚；
- 架构是否确定；
- 约束是否明确；
- 验收标准是否可测试。

---

## 8.6 案例六：客户端 / GUI 应用

使用 filecheck 等案例讨论技术预研。

问题包括：

- Python 还是 Go；
- PyInstaller；
- CustomTkinter；
- PyQt / PySide；
- WebView；
- 原生 GUI。

重点展示：

> **AI 不只是帮忙写代码，也可以用于技术路线预研和方案比较。**

但最终技术选择需要工程约束和验证，而不是直接接受模型第一答案。

---

## 8.7 案例七：GitHub + CI/CD

展示：

- Branch；
- Commit；
- PR；
- CI；
- GitHub Actions；
- Docker Image；
- Release；
- PyInstaller 自动打包；
- HyperFrames 视频自动渲染。

### 核心观点

> **Agent 与 Git/CI 结合以后，开发过程才能真正形成可追踪、可验证、可重复的工程闭环。**

---

## 8.8 案例八：IPsec VPN 性能测试数据分析

展示如何从：

- 测试数据；
- 报文长度；
- RTT；
- 网络设备配置；
- 异常曲线；

逐步发现十兆以太网链路成为性能瓶颈。

### 核心观点

用于说明旗舰模型的价值不只是“写得更漂亮”，而在于：

- 复杂关系；
- 异常关联；
- 多因素分析；
- 疑难问题定位。

同时强调：

> 模型提出线索后仍然需要工程实验验证，不能把相关性直接当因果。

---

## 8.9 案例九：文档处理

展示：

- Markdown；
- Word；
- PDF；
- md2docx；
- 文档解析；
- 文档生成；
- 格式约束。

进一步连接到：

- 全文搜索；
- Embedding；
- RAG；
- 知识库。

---

## 8.10 案例十：浏览器控制与信息采集

对比：

- Browser Use；
- Computer Use；
- Playwright；
- 爬虫。

通过任务选择工具，而不是追求“全部让视觉 Agent 做”。

---

## 8.11 案例十一：HyperFrames 视频制作

流程：

文案  
→ 分镜  
→ HTML / SVG 动画  
→ 音频  
→ 字幕  
→ 时间轴  
→ GitHub Actions  
→ 视频渲染。

### 核心观点

> Agent 的应用并不局限于代码开发，它可以参与复杂内容生产流水线。

---

## 8.12 特殊案例：协议和接口研究

对于软件协议、接口行为、Web API、激活机制等研究案例，只保留合法、可迁移的工程知识：

- HTTP；
- SSE；
- WebSocket；
- OAuth；
- PKCE；
- Token；
- API Gateway；
- Proxy；
- DevTools；
- 协议兼容；
- 自动化测试。

不将培训材料制作成：

- 绕过付费；
- 滥用免费额度；
- 凭据窃取；
- 绕过授权；
- 未授权攻击；

的实操教程。

---

# 9. 案例不应全部放在最后

虽然模块六集中展示真实项目，但实际授课不采用：

> 前面全部理论 → 最后统一讲案例

这种结构。

原则是：

> **每出现一个抽象概念，尽快插入一个真实短案例。**

建议映射如下：

| 概念 | 立即插入的案例 |
|---|---|
| Token | `/tokenize` 实测 |
| SSE | Qwen 流式请求 |
| Thinking | Thinking On / Off API 对比 |
| Context | model-metric 长上下文测试 |
| TTFT / Tokens/s | Token 输出速率体感 HTML Demo + model-metric |
| Chat vs Agent | 修改 Web 项目小任务 |
| Shell / Git | 真实仓库修改闭环 |
| Browser | Playwright Visual QA |
| MCP | GitHub / 外部服务连接 |
| Skill | 项目验收流程 Skill |
| AGENTS.md | 本仓库根目录 `AGENTS.md` |
| RAG | Cherry Studio BM25 vs Embedding 召回对比；Open WebUI Hybrid/Agentic Retrieval |
| CI/CD | GitHub Actions |
| 旗舰模型价值 | IPsec VPN 数据分析 |

---

# 10. 最后的方法论收束

培训最后不再增加大量新概念，而是把前面的内容收束成一套工程方法。

## 10.1 先判断任务

这是：

- 一个问题？
- 一个分析任务？
- 一个工程任务？
- 一个重复流程？
- 一个可以自动化的流程？

---

## 10.2 再选择工作方式

简单问题：

`Chat`

复杂工作：

`Agent + Workspace + Tools`

稳定重复工作：

`Script / Skill / CI / Automation`

---

## 10.3 再选择模型

常规任务：

优先选择成本合理、速度稳定、能力足够的模型。

疑难任务：

升级到更强模型进行分析、设计、Review 或异常定位。

---

## 10.4 把结果沉淀下来

一次成功任务之后，不只保留聊天记录。

需要判断是否应该沉淀成：

- 文档；
- Prompt；
- AGENTS.md；
- Skill；
- MCP；
- Script；
- Test；
- CI；
- Template；
- Knowledge Base。

---

## 10.5 最终形成闭环

> **模型选择 → Agent 工作 → 工具执行 → 人工判断 → 自动验证 → Git 留痕 → 资产沉淀 → 下一次复用**

这是整场培训最终希望学员带走的方法。

## 10.6 工程开发不要从 Prompt 直接跳到 Code

复杂应用建议统一采用：

`Problem → Requirement → Constraint → Research → Architecture → Plan → Implement → Test → Visual QA → Review → Release`

也就是：

> **问题 → 需求 → 约束 → 调研 → 架构 → 计划 → 开发 → 测试 → 视觉/浏览器验收 → Review → 发布**

该流程不是只属于 Web 开发案例，而是本培训贯穿应用开发案例的通用工程方法。

## 10.7 人工判断始终在闭环中

Agent 可以执行大量工作，但不把最终技术判断外包给模型。

人在关键节点负责：

- 定义问题和目标；
- 给出业务、安全和资源约束；
- 确定是否接受技术方案；
- 判断异常线索是否成立；
- 对最终结果负责。


---

# 11. PPT 组织基线

最终 PPT 不应把本文逐条压缩到幻灯片。

每页尽量只回答一个核心问题。

推荐页面节奏：

问题  
→ 真实现象  
→ 原理  
→ Demo / Evidence  
→ 一句话结论。

优先使用：

- 实际 API Request / Response；
- Terminal；
- Postman；
- GitHub；
- Agent Workspace；
- Browser；
- metrics；
- 性能曲线；
- 实际应用截图。

针对每个重点内容标记：

- PPT 静态展示；
- 现场 Demo；
- 录屏；
- 动画；
- 备用截图。

最终要求：

> **即使现场 Demo 失败，PPT 仍然能够独立讲清主要逻辑。**

---

# 12. 后续内容建设顺序

## 12.1 当前编制策略（2026-09-30）

四次讲座方案已经确定，后续工作从“继续扩章节”转入**按四场讲座准备可交付授课材料**。

当前优先级：

1. 按四场分别完成“讲课脚本级目录”：问题、案例、知识点、过渡和结论；
2. 把现有 1～8 内容单元映射进四场，消除重复讲解；
3. 优先补 P0 截图与录屏，并为现场 Demo 准备备用素材；
4. 完成两个纵向工程案例：BMQuiz、FileCheck；
5. 完成知识库同源三层 Demo 与部门知识库建设方案；
6. 完成第三讲多 Agent 共性对照、Browser/Runtime/MCP/Skill 演示；
7. 再从完整讲义和真实证据抽象四套 PPT 故事线；
8. 制作最终 PPT，并执行现场演示预演与备用方案检查。

> 当前原则：**不再为了“内容更全”继续横向扩充概念，优先把已确定内容做深、做实、做成可演示材料。**

> 原有案例建设顺序继续保留，作为后续“证据与演示补全阶段”的执行清单。

本大纲作为后续培训材料建设基线，建议按以下顺序推进：

1. 完成模块一现有 Qwen API 讲义、证据、图表和演示脚本；
2. 编写“为什么 Chat 不够”章节；
3. 打磨 Agent 工作区与工具链章节：`04-agent-common-mechanisms.md` 与 `05-agent-tools-real-world.md` 已有初稿，下一步补统一 Demo、实测证据和截图；
4. API / MCP / Skill / Plugin / Command / Hook：主讲稿、证据基线与统一 Demo 设计已形成；第一套 MCP Host 固定为 ZCode，下一步实现并实测 Raw API → ZCode MCP Tool → ZCode Skill+MCP；
5. “如何形成可复用资产”主讲稿与证据基线已形成，并增加 ZCode AGENTS.md / Project Memory / Command / Skill / Plugin 的连续实例，用于解释资产沉淀边界；
6. **后续证据与演示补全阶段**：完成 Agent Runtime 内网标准环境与 Preflight 实测，再完成 ZCode 两个贯穿案例（鹈鹕 Browser 闭环 + Sensor Guard 工程闭环），之后补 SSH/Docker、CI 与模块四 API→MCP→Skill 统一 Demo；
7. 为每个模块建立截图和 Demo 清单；

   - 当前已有讲义的统一素材清单已建立：`docs/outline/media-capture-checklist.md`；
   - 截图/录屏采用统一编号、P0/P1/P2 优先级和状态管理；

8. 形成培训完整讲义；
9. 将讲义重新抽象为 PPT 逐页故事线；
10. 制作最终 PPT 和备用演示素材。

---

# 13. 当前仓库状态与缺口

截至本基线形成时：

## 已有

- **Qwen 当前正式实测基线**：`api/qwen/results/20260930_095033/`（r4；28 PASS / 1 SKIP；Responses Vision 正式 PASS；旧结果进入 `archive/`）
- **当前 API 实测报告**：`api/qwen/reports/qwen36_api_test_report_20260930.md`
- **API 教学链**：Postman GET/POST → Cherry Studio Network → Python 自动测试 → `/metrics` → 内网已部署 model-metric
- **model-metric 案例**：`docs/cases/model-metric-api-observability.md`（当前仓库 FastAPI 2.3.2）

- 根目录项目规则：`AGENTS.md`（可用于培训：可直接作为“项目规则/可复用资产”案例）
- Qwen API 自动测试脚本（已有实测证据）
- Qwen API 实测结果（已有实测证据）
- Qwen API 实测报告（已有实测证据）
- 第一章 API 培训讲义（可用于培训；第一讲正式讲义已更新到 v1.7）
- 第一讲新增“API 不等于 Chat”主桥段：同一 qwen3.6 API 可封装为翻译、结构化抽取/JSON、Vision OCR、网页截图 Visual QA、分类/路由等非 Chat 应用；Demo 规范：`demos/api-applications/README.md`
- 第一讲已明确 Cherry Studio Desktop/Local-first 与 Open WebUI Self-hosted/Server-side 的数据边界差异，并避免把“最早/唯一服务端项目”等未经系统统计的历史判断写成硬事实；证据基线：`docs/references/chat-workbench-api-application-evidence-2026-09.md`
- Cherry Studio Network 抓包主 Demo（已有讲义设计，待现场截图：models / 首轮 Chat / 多轮 Context / Vision / SSE）
- Qwen v2 Agent Tool Loop 与多模态 Vision 实测（已有实测证据）
- Thinking 失败项专项复测（已有实测证据）
- Token 输出速率体感 Demo（可用于培训，基于 Apache-2.0 开源项目改造，可离线运行）
- 现有讲义截图/录屏占位与总清单（已有初稿：`docs/outline/media-capture-checklist.md`；API、Chat→Agent、Open WebUI/Cherry、知识库、Agent 共性机制、Agent 真实世界工具链均已建立编号；当前待用户按 P0 清单补真实截图与录屏）
- 模块三主讲稿：`docs/chapters/05-agent-tools-real-world.md`（已有初稿；覆盖 File/Search、Shell、Git、Verification、Browser Use/Playwright/Computer Use/Crawler、SSH、Docker、API、CI/CD，并设计 TOOL-01～11 与 TOOL-R01～05）
- 模块三证据基线：`docs/references/agent-tools-real-world-evidence-2026-09.md`（已有素材；已核验 Playwright、OpenAI Computer Use/Codex Sandbox、Git、Docker、GitHub Actions 官方资料）
- ZCode 模块三贯穿案例：`demos/zcode-real-world/README.md` + `docs/cases/zcode-agent-real-world.md`（已有案例设计；并已补 `instructor-runbook.md`、`result-template.md`；官方证据基线为 `docs/references/zcode-agent-evidence-2026-09.md`，确认 Workspace/Terminal/Built-in Browser/Review/Execution Modes/AGENTS.md/Project Memory/Goal Mode 等当前实现）
- ZCode Sensor Guard 训练项目：`demos/zcode-real-world/project/`（已有初始项目；5 条测试中设计 1 条 85°C 边界失败，待 ZCode 现场实测修复）
- Agent Runtime / 内网工具链案例：`docs/cases/agent-runtime-environment-intranet.md`（已有初稿；明确 Harness vs Runtime、Git/Python/Node/npm、Local/WSL/Docker/SSH、内网软件供应链边界）；并新增 Windows/Linux Preflight 脚本
- 模块四主讲稿：`docs/chapters/06-api-mcp-skill-plugin-command-hook.md`（可用于培训；明确 API、Tool、Function Calling、MCP、Skill、Plugin、Command、Hook 的分层关系与事实边界；统一 Demo 与实测后补）
- 模块四证据基线：`docs/references/api-mcp-skill-evidence-2026-09.md`（已有素材；基于 MCP、OpenAI Skills/Plugins/Tool Design/Hooks 当前官方资料核验）
- 模块四统一 Demo 设计：`demos/agent-tool-integration/README.md`（规划完成；同一训练服务依次演示 Raw API → MCP Tool → Skill+MCP，避免把三层误解为三套不同能力）
- 模块五主讲稿：`docs/chapters/07-reusable-agent-assets.md`（可用于培训；以“资产路由”组织 Prompt、Project Rules、Plan、Skill、Script、Test/Eval、CI、Template、Memory、Knowledge Base、Evidence、Git，并明确反过度沉淀原则；案例与素材后补）
- 模块五证据基线：`docs/references/reusable-agent-assets-evidence-2026-09.md`（已有素材；核验 AGENTS.md open format、Codex 当前 AGENTS/Context 指引、OpenAI Skills/ExecPlan、Hermes Memory/Context/Skills 等当前资料）
- 方法论收束主讲稿：`docs/chapters/08-agent-engineering-methodology.md`（可用于培训；覆盖任务路由、Problem→Release 工程链、Agent 执行闭环、模型/Thinking/Context 预算、人机分工、交付与资产沉淀；METHOD-01～07 图示后补）
- 正式四讲授课方案：`docs/outline/training-4-session-leadership-proposal.md`（当前授课基线；按 13 / 2 / 45 / 678 组织）
- 8 个内容单元：`docs/outline/training-series-plan.md`（继续保留用于内容维护，不作为现场场次安排）
- 完整工程案例框架：`docs/cases/end-to-end-agent-engineering-cases.md`（已有框架；BMQuiz V2 与 FileCheck 固定为两个纵向主案例）
- BMQuiz V2 完整工程案例：`docs/cases/bmquiz-end-to-end-agent-development.md`（已有第一版主讲底稿；已按真实仓库与 Git 历史串联需求、约束、架构、AGENTS、Plan、实现、测试、Visual QA、Server CI、Docker/GHCR、部署、验证与资产沉淀；待补原始对话与截图/录屏）
- FileCheck 完整工程案例：`docs/cases/filecheck-end-to-end-agent-development.md`（已按当前 v0.2.3 README / pyproject / main 代码与 CI 核验；覆盖 Windows/Offline/Win7 约束、Core→CLI/GUI、可靠性、CustomTkinter、CI、PyInstaller、Release；待补 Git 历史与实操录屏）
- Agent 服务器运维案例：`docs/cases/agent-server-operations.md`（已有案例设计；BMQuiz Docker + model-metric systemd，待真实录屏与执行证据）

- API 官方参考资料（已有素材）

## 待建设

- 模块二：Chat → Knowledge/RAG → Agent（已有初稿：`docs/chapters/02-chat-to-agent-harness.md`、`docs/chapters/02-chat-workbenches-and-rag.md`；知识库现采用“双稿制”：`docs/chapters/03-department-knowledge-base-teaching.md` 为培训主讲教学版，按“问题→例子→原理→结论”重构并预留 KB-01～KB-22 截图/图示占位；`docs/chapters/03-department-knowledge-base.md` 保留为完整技术稿和深入阅读材料；架构文档为 `docs/architecture/department-knowledge-architecture.md`；已形成同源三层 Knowledge Demo 规范 `demos/knowledge-retrieval/README.md`；已完成知识库/RAG 学术论文、官方产品与成熟实现的专项证据核验，证据基线为 `docs/references/knowledge-base-rag-evidence-2026-09.md`，涵盖 Lost in the Middle、RULER、NoLiMa、LongBench v2、2025 “Perfect Retrieval 仍受 Context Length 影响”等长上下文证据，以及 External Retrieval Recall vs In-context Context Utilization、Context Budget / Evidence Budget；教学版已完成 v0.2 第一轮“首次学习者降阶”重构：新增开卷考试统一类比、RAG“先查再给再答”、Embedding/Vector Index 非知识本体解释、Parse 与 Chunk 分拆、长上下文证据下沉、Top-K/Rerank/Evidence Budget 统一直觉、Agentic Retrieval“逐步取证”解释、问题类型→检索方式速查表和讲师节奏分层；当前待补 KB-01～KB-22 及扩展占位截图/图示，并在后续验证阶段补 BM25/Vector/Hybrid/Agentic Retrieval、no-answer/版本冲突/ACL 与内网 qwen3.6 实测）
- Agent 共性机制专题（已有初稿：`docs/chapters/04-agent-common-mechanisms.md`；10 个 Agent（新增 WorkBuddy）横向对比与 FrontierHarness/Kimi K3 受控评测已迁入本章；已覆盖 Harness、Identity、Project Instructions、Workspace、Context、Plan、Memory、Tools、MCP/API、Skill、Browser/Computer Use、Permission/Sandbox、Verification、Sub-agent、CLI/GUI/IDE，以及 Provider/Protocol Adapter、Session/Checkpoint/Resume、Context Compaction、Runtime Backend、Hooks/Automation、Secrets、Observability、Reasoning vs Plan；待补内网 qwen3.6 跨 Harness 实测、截图和统一 Demo；WorkBuddy 的 Chat→Workspace→Skill→Runtime 截图已规划为 AGENT-WB-01～04）
- 模块三：Agent 工具与真实世界（已有初稿；**第一套贯穿主案例已固定为 ZCode**，案例规范为 `demos/zcode-real-world/README.md`，已建立 Sensor Guard 训练项目和 `docs/cases/zcode-agent-real-world.md`；当前缺口为 ZCode 实际录屏/截图，以及 SSH/Docker、Commit→CI 等后续真实案例证据）
- 模块四：API / MCP / Skill 等关系（主讲稿已可用于培训，官方证据基线已形成；后续只补最小 MCP Server、内网 qwen3.6 + Harness Tool Calling、Skill 实际调用、Command/Hook 对比等实测证据与素材）
- 模块五：可复用资产与知识体系（主讲稿已可用于培训，证据基线已形成；后续只补仓库资产地图、长 Prompt→Skill、Skill→Script/Test/CI 等演示素材）
- **四场最终讲义正文已建立**：当前下一建设重点转为 P0 截图/录屏与 Demo 实测。第一讲补 API/Chat/Agent 素材，第二讲完成知识库同源三层 Demo，第三讲补多 Agent 共性/Browser/Runtime/MCP/Skill 演示，第四讲补 BMQuiz 与 FileCheck 历史证据和实操录屏，并准备 model-metric/IPsec/HyperFrames 短案例
- Agent 服务器运维：案例设计已完成，后续补 BMQuiz Docker 与 model-metric systemd 的真实执行证据和录屏
- 四讲串联检查：检查四场之间的重复、术语一致性、案例复用、过渡和节奏；8 个内容单元只作为后台内容维护
- 其他专题案例：IPsec VPN 数据分析、HyperFrames、授权机制/协议研究、网站安全测试后续逐个补证据与讲义
- 各模块架构图 / 流程图
- Demo 脚本
- 截图资产
- PPT 页面设计
- 最终 PPT

后续每完成一个模块，应同步更新本节状态。

---

# 14. 基线变更原则

本文件不是不可修改的“死大纲”。

后续如果：

- 实测结果推翻当前认知；
- 出现更好的真实案例；
- 培训时长变化；
- 某一章节过于理论；
- 某工具或技术发生重大变化；

可以调整章节顺序和内容。

但原则上不应轻易改变以下主线：

> **模型怎么调用 → 为什么 Chat 不够 → Agent 如何操作真实世界 → 如何让 Agent 掌握工具 → 如何形成可复用资产 → 用真实项目证明 Agent 能完成什么**

所有调整优先服务于一个目标：

> **让工程师理解原理、掌握方法，并能在培训结束后真正把 Agent 用到工作中。**
