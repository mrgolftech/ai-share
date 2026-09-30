# System Prompt、File Input 与 Prompt Engineering 证据摘要（2026-09）

> 用途：支撑第一讲中 System Prompt、附件进入 Context、Prompt Engineering 的讲解。  
> 原则：协议事实优先使用厂商官方文档；Cherry / Open WebUI 的实际 Request 仍以培训现场当前版本抓包为最高优先级。

---

# 1. System Prompt / Instructions

## OpenAI Chat Completions

OpenAI Chat 使用 message roles 表达不同层级输入。

当前官方 API 中包含：

- developer；
- system；
- user；
- assistant；
- tool。

当前官方说明：新一代 OpenAI 模型更推荐使用 `developer` message 表达应用开发者的高层指令；大量 OpenAI-compatible 服务仍广泛支持 `system`。

参考：

- https://developers.openai.com/api/reference/cli/resources/chat
- https://developers.openai.com/api/docs/guides/prompt-engineering

培训边界：

> 内网 qwen3.6 通过 Cherry 实际发送 `system` 还是 `developer`，必须以 Network Request 为准。

## OpenAI Responses

Responses API 支持顶层：

`instructions`

用于提供高层行为指令。

官方特别说明：

> `instructions` 只作用于当前 response generation request；使用 `previous_response_id` 管理状态时，上一个请求的 instructions 不会自动作为下一轮 instructions 保留。

参考：

- https://developers.openai.com/api/docs/guides/text
- https://developers.openai.com/api/docs/guides/migrate-to-responses

这也是为什么应用层 Assistant / Workspace 仍需要负责持续管理长期指令。

## Anthropic Messages

Anthropic Messages 使用顶层：

`system`

而不是在 `messages[]` 中增加一个 `role=system` 的消息。

官方当前 Prompting Guide 也直接给出：

`system="You are ..."`

的 Messages API 示例。

参考：

- https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables
- https://docs.anthropic.com/

---

# 2. System Prompt 不是安全边界

System Prompt 可以规定：

- Role；
- Goal；
- Constraints；
- Output；
- Tool policy；
- Tone。

但它仍然属于模型输入。

真正的权限与安全边界仍然需要：

- ACL；
- Tool Permission；
- Sandbox；
- Credential Scope；
- Program Validation；
- Human Approval。

因此培训中不使用：

> “System Prompt 可以防止模型做任何不该做的事情”

这种表述。

---

# 3. 文件附件不只有“转文本”一条路径

## 3.1 Client-side Parse → Text

某些 Chat Client 会先解析文件，然后把提取文本拼入 Message / Context。

这一路径确实可以概括为：

`File → Parse → Text → Context`

但不同 Parser 会影响：

- 表格；
- 标题；
- 图片；
- 顺序；
- OCR；
- Metadata。

## 3.2 OpenAI Native File Input

当前 OpenAI Responses 支持：

- `input_file`；
- uploaded `file_id`；
- Base64；
- external file URL。

当前官方处理行为：

- PDF：对于支持视觉的模型，提取文本 + 页面图像；
- DOC/DOCX/PPT/PPTX/TXT/Code 等非 PDF：主要提取文本；
- Spreadsheet：专门的表格增强流程；
- 大文件检索场景更推荐 File Search，而不是每轮直接输入整份文件。

Chat Completions 当前官方 File Input 支持范围比 Responses 更窄；非 PDF 文档通常需要应用自己提取文本后再作为 text content 传入。

参考：

- https://developers.openai.com/api/docs/guides/file-inputs

## 3.3 Anthropic PDF / Document

Anthropic 当前 PDF 支持可以通过：

- URL；
- Base64 document block；
- Files API `file_id`；

进入 Messages API。

参考：

- https://docs.anthropic.com/en/docs/build-with-claude/pdf-support

## 3.4 Vision Input

图片可以直接作为多模态 Image Content 进入模型，不应简单等同于 OCR 文本。

## 3.5 Knowledge / RAG

长期资料通常采用：

`Parse → Chunk → Index → Retrieve → Relevant Chunks → Context`

Open WebUI Full Context 则可整篇直接进入 Context。

因此培训中统一使用：

> **“上传文件”描述 UI 行为；“文件怎样进入 Context”必须继续观察 Client、API 和 Retrieval 机制。**

---

# 4. Prompt Engineering：不把社区框架当标准

OpenAI 当前 Prompt Guidance 强调：

- clear instructions；
- relevant context；
- output format；
- examples；
- evaluation。

Anthropic 当前 Prompting Guide 强调：

- clear/direct instructions；
- context；
- examples；
- structured sections / XML；
- role；
- long-context organization。

参考：

- https://developers.openai.com/api/docs/guides/prompt-engineering
- https://developers.openai.com/api/docs/guides/prompting
- https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-templates-and-variables

两家的共同点可以抽象成：

```text
Task / Goal
Context
Constraints
Expected Output
Examples（必要时）
Verification（工程任务）
```

这比要求所有员工记住某个缩写更稳定。

---

# 5. 社区 Prompt Framework

培训只做“一页认识”，不当成标准。

## RTF

`Role / Task / Format`

适合短任务。

## CO-STAR

常见社区表达：

`Context / Objective / Style / Tone / Audience / Response`

适合文案和受众导向任务。

## CRISPE

常见原始表达围绕：

- Capacity and Role；
- Insight；
- Statement；
- Personality；
- Experiment。

这些框架的价值主要是：

> **帮助用户不遗漏重要 Prompt 元素。**

不是：

> **模型内部要求的固定语法。**

---

# 6. 培训推荐骨架

对于一般知识工作：

```text
Role（可选）
Task
Context
Constraints
Output Format
Examples（可选）
```

对于工程任务：

```text
Goal
Current State / Evidence
Constraints
Allowed Actions
Acceptance / Verification
Deliverable
```

工程培训中后者优先。

原因：

> 对 Agent 来说，目标、边界、工具权限和验收标准通常比“扮演资深专家”更决定最终质量。
