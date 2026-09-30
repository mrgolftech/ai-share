# 第一讲：从模型 API 到 Agent——看懂 AI 应用背后的工作逻辑

> 状态：Final Lecture Draft v2.0（叙事重构版）  
> 日期：2026-09-30  
> 建议时长：100～120 分钟  
> 内容映射：原内容单元 1 + 3  
> 适用对象：部门技术人员及相关技术管理人员  
> 主线：**从一个真实 Chat Request 出发，一层层拆开 Model、API、Context、Tool、Harness，最终解释 Agent 为什么能够“干活”。**

## 讲授层级说明

为了同时保留完整技术内容和现场叙事节奏，本讲从 v2.0 起统一使用三种层级：

- **【主讲】**：现场必须讲清，是理解后续内容的因果主链；
- **【扩展】**：完整讲义保留，现场根据时间、听众基础和提问情况展开；
- **【备用】**：用于答疑、技术人员深入阅读或 Demo 失败时补充，不占用正常主线时间。

> 原则：**不因为现场时间有限而删掉已经形成的技术资产；通过讲授层级控制“现场讲什么”，通过完整讲义保留“以后还能查什么”。**

### 第一讲现场只讲一条故事线

```text
在 Cherry 输入一句话
        ↓
应用怎样找到并调用模型？
        ↓
API Request 到底长什么样？
        ↓
API 为什么不只是 Chat？
        ↓
第二轮为什么“记得”第一轮？
        ↓
Context 里到底有什么？
        ↓
文本怎样 Tokenize？
        ↓
Prefill / Decode 怎样发生？
        ↓
Thinking、长 Context、Tokens/s 为什么都有成本？
        ↓
图片、SSE 等产品体验怎样建立在协议和模型能力之上？
        ↓
模型怎样产生 Tool Call？
        ↓
谁真正执行工具？
        ↓
Harness 是什么？
        ↓
为什么复杂任务最终走向 Agent？
```

现场组织为七幕：

| 幕 | 核心问题 | 现场层级 |
|---|---|---|
| 第一幕：拆开聊天框 | Cherry 背后到底怎样调用模型？ | 主讲 |
| 第二幕：理解“记忆” | 第二轮为什么知道第一轮？ | 主讲 |
| 第三幕：走进一次推理 | Text → Token → Prefill → Decode → Text | 主讲 |
| 第四幕：应用怎样组织信息 | System Prompt、附件、Knowledge、Cherry/Open WebUI | 主讲 + 扩展 |
| 第五幕：模型调用不是免费的 | Thinking、TTFT、Tokens/s、长 Context、共享服务 | 主讲 |
| 第六幕：从回答走向行动 | Tool Calling → Tool Result → Harness | 主讲 |
| 第七幕：为什么最终需要 Agent | Read / Act / Observe / Verify / Iterate | 主讲 |

---

### 讲师节奏原则

如果现场时间不足，优先压缩：

1. 三种协议的 Schema 逐字段比较；
2. Prompt 社区框架；
3. Open WebUI Knowledge 的深入细节；
4. 自动测试全部 29 项的逐项说明；
5. Vision 的编码机制细节。

不要压缩：

1. Cherry Network 看见真实 API；
2. API 不等于 Chat；
3. 多轮 Context；
4. Tokenize → Prefill → Decode → Detokenize；
5. 60k / 100 万 Token 直觉；
6. TTFT / Tokens/s；
7. Tool Call 不等于 Tool Execution；
8. Harness；
9. 最小 Agent 闭环。

---

# 0. 开场：本讲不是“API 编程课”【主讲】

这一讲先解决一个最基础、也最容易被各种产品界面遮住的问题：

> **我们每天看到的 Chat、Agent、AI IDE，到底是什么？**

很多人对 AI 的第一印象来自一个聊天框。

打开 Cherry Studio、Open WebUI 或 ChatGPT，输入一句话，几秒以后得到答案。再打开 Codex、ZCode、Hermes、OpenCode，又会发现这些工具似乎突然多了很多能力：

- 能读文件；
- 能修改代码；
- 能运行命令；
- 能打开浏览器；
- 能提交 Git；
- 甚至能登录服务器。

如果只看界面，很容易产生两个误解：

第一：

> Chat 软件就是模型本身。

第二：

> Agent 是一种比 Chat 更神秘、更高级的新模型。

这一讲要把这层“神秘感”拆掉。

我们不从术语开始，而从一个真实问题开始：

> **当我在 Cherry Studio 里输入“你好”并按下发送以后，究竟是谁做了什么？**

【截图占位 API-NET-01｜Cherry Studio 对话界面与模型选择】

【录屏占位 API-R01｜刷新模型列表，在 Network 中看到 /v1/models 请求】

讲师此处只提出问题，不立即给完整架构图。

---

# 第一幕：拆开聊天框——从 Cherry Studio 看见真实 API【主讲】

第一讲不先把三套 API 格式摆在 PPT 上让大家背。

更自然的做法是：

> **先配置一个大家正在使用的 Chat 客户端，在真实界面里看到“为什么这里会有不同接口类型”，再打开 Network 看它到底发了什么。**

这样 API 不是抽象名词，而是从实际使用中长出来的。

---

## 1.1 配置内网模型：先认识 Provider、Base URL、API Key、Model【主讲】

在 Cherry Studio 中新增/编辑内网模型服务。

现场只解释四个最基本概念：

```text
Provider
= 我准备通过哪一类服务/协议去访问模型

Base URL
= 模型服务在哪里

API Key
= 客户端怎样证明自己有调用权限

Model ID
= 这次真正要调用哪个模型
```

【截图占位 CH-API-00｜Cherry 内网 Provider：Base URL / API Key / Model】

配置完成后刷新模型列表，同时打开 DevTools Network。

可以看到类似：

`GET /v1/models`

【截图占位 API-NET-02｜Cherry GET /v1/models Request / Response】

【录屏占位 API-R01｜配置/刷新模型 → Network 中看到 GET /v1/models】

这里第一次把 UI 和 API 对上：

> Cherry Studio 自己并不知道服务器有哪些模型，它也是通过 API 向模型服务查询。

当前内网正式 r4 测试中，该接口已经验证：

- HTTP 200；
- 找到 `qwen3.6`；
- `max_model_len=131072`。

---

## 1.2 配置时为什么会看到 OpenAI Chat、OpenAI Responses、Anthropic Messages？【主讲简述】

这是非常适合现场停下来问大家的问题：

> **明明后面都是同一个 qwen3.6，为什么客户端还要让我选择不同 API / Endpoint Type？**

答案是：

> **模型能力和接口协议是两层。**

今天的大模型 API 并不是一开始就有一个全球统一标准，而是随着不同厂商、不同产品形态逐步演进出来的几套主流接口生态。

可以用一条很简单的演进线理解。

### OpenAI Chat Completions：先解决“多轮聊天怎样表达”

早期文本 Completion 更接近：

```text
prompt → completion
```

Chat 应用普及以后，需要明确：

- system；
- user；
- assistant；
- 多轮 history；
- tool call。

于是形成以：

`messages[]`

为核心的 Chat Completions 形态。

典型 Endpoint：

```text
POST /v1/chat/completions
```

它后来被大量第三方服务采用，形成非常广泛的 **OpenAI-compatible** 生态。

### OpenAI Responses：从“聊天消息”继续走向统一的模型能力入口

随着模型输入输出不再只有纯文本聊天，而开始包含：

- reasoning；
- multimodal input；
- function/tool；
- file/search 等 Agent 能力；

OpenAI 又发展出以 `input / output items / events` 为中心的 Responses 形态。

典型 Endpoint：

```text
POST /v1/responses
```

培训中不要简单说：

> “Responses 就是 Chat Completions v2，旧接口马上淘汰。”

更准确的是：

> **它是 OpenAI 体系更偏统一输入输出、工具与 Agent 工作负载的新接口形态；现实工程中 Chat Completions 仍然大量存在，因此客户端需要同时兼容。**

### Anthropic Messages：另一套独立演进的模型 API 生态

Anthropic 的 Claude 体系独立发展出了 Messages API。

它同样表达：

- user / assistant；
- streaming；
- vision；
- tool use；
- thinking；

但使用自己的 Content Block 结构，例如：

- `content[]`；
- `tool_use`；
- `tool_result`。

典型 Endpoint：

```text
POST /v1/messages
```

因此我们今天看到的三套接口，不是因为：

> 有三个 qwen3.6。

而是因为：

> **客户端和推理服务为了兼容不同模型生态，需要做 Protocol Adapter。**

可以画：

```text
                    qwen3.6
                       ↑
                  vLLM / Gateway
              ┌────────┼────────┐
              ↑        ↑        ↑
       OpenAI Chat  Responses  Anthropic
              ↑        ↑        ↑
          Chat App   Codex类   Claude类
```

【图示占位 API-PROTO-00｜同一模型服务兼容三套 API 生态】

这也是为什么第三讲讲 Agent 时还会遇到：

- Provider Adapter；
- Model Adapter；
- Protocol Compatibility。

---

## 1.3 先不要讲 JSON：直接用 Cherry 同一个 Prompt 切三种协议【主讲 / 演示】

建议在 Cherry 中准备三个容易辨认的配置/模型项，例如：

```text
Qwen - OpenAI Chat
Qwen - OpenAI Responses
Qwen - Anthropic Messages
```

具体名称和配置入口以当前安装版本为准。

【截图占位 CH-API-01｜Cherry 当前实际的三种协议/Endpoint Type 配置】

固定同一句：

> 请只回答：PROTOCOL_OK

然后依次选择三种配置，同时保持 DevTools Network 打开。

观众会直接看到：

```text
/v1/chat/completions

/v1/responses

/v1/messages
```

【截图占位 CH-API-02A｜Cherry → /v1/chat/completions】

【截图占位 CH-API-02B｜Cherry → /v1/responses】

【截图占位 CH-API-02C｜Cherry → /v1/messages】

【录屏占位 CH-R03｜同 Prompt 切三种 API → Network 显示三个 Endpoint】

到这里再打开 Request Body。

学员会看到：

> **做的是同一件事，但 POST Body 长得不一样。**

---

## 1.4 三种 POST Request 到底有什么不同？【扩展】

### OpenAI Chat Completions

```http
POST /v1/chat/completions
```

核心输入：

```json
{
  "model": "qwen3.6",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ]
}
```

重点看：

- `messages[]`；
- `role`；
- `choices[].message`；
- `tool_calls`；
- Chat SSE delta。

【截图占位 API-PROTO-01｜OpenAI Chat 真实 Request / Response】

### OpenAI Responses

```http
POST /v1/responses
```

当前内网实测输入可以看到：

```json
{
  "model": "qwen3.6",
  "input": "请只回答：RESPONSES_OK",
  "reasoning": {
    "effort": "none"
  }
}
```

重点看：

- `input`；
- `output[]`；
- `function_call`；
- `response.created`；
- `response.completed`。

【截图占位 API-PROTO-02｜Responses 真实 Request / Response / Event】

### Anthropic Messages

```http
POST /v1/messages
```

典型输入：

```json
{
  "model": "qwen3.6",
  "max_tokens": 256,
  "messages": [
    {
      "role": "user",
      "content": "请只回答：CLAUDE_OK"
    }
  ]
}
```

重点看：

- `messages[]`；
- `content[]` blocks；
- `tool_use`；
- `tool_result`；
- Anthropic streaming events。

【截图占位 API-PROTO-03｜Anthropic Messages 真实 Request / Response】

### 用一张表结束，不要求学员背 Schema

| 对比项 | OpenAI Chat | OpenAI Responses | Anthropic Messages |
|---|---|---|---|
| Endpoint | `/v1/chat/completions` | `/v1/responses` | `/v1/messages` |
| 核心输入 | `messages[]` | `input` / items | `messages[]` + content blocks |
| 普通输出 | `choices[].message` | `output[]` | `content[]` |
| Tool Call | `tool_calls` | `function_call` | `tool_use` |
| Tool Result | tool message | function output item | `tool_result` |
| 当前内网基础闭环 | 已实测 | 已实测 | 已实测 |

【图示占位 API-PROTO-04｜三种 POST Schema 对照】

这部分最后只留下一个结论：

> **不要把接口格式和模型能力混为一谈。**

同一个模型可以被多个 Adapter 暴露成不同兼容协议；同一个客户端也可以根据 Endpoint Type 用不同方式组织 Request。

---

## 1.4A System Prompt 到底是什么？三种 API 里放的位置还不一样【主讲】

前面已经看到三种 API 的 POST Body 不一样。

这时正好解释大家在 Cherry Assistant、Open WebUI Workspace Model 中都会看到的一个词：

> **System Prompt / Instructions。**

它不是“神秘咒语”，也不是模型训练。

可以先把它理解成：

> **由应用提供、希望在当前助手/工作空间中长期生效的一组高层指令。**

例如：

```text
你是部门内网模型 API 培训助手。
优先依据已绑定的实测资料回答。
没有证据时明确说明，不要猜测。
输出先给结论，再给证据。
```

它通常用来规定：

- 角色 / 职责；
- 目标；
- 行为边界；
- 事实来源优先级；
- 输出格式；
- 工具使用原则；
- 风格。

但要明确：

> **System Prompt 不是绝对安全边界，也不能替代权限、ACL、Sandbox 和程序校验。**

---

### OpenAI Chat Completions：作为高优先级 Message

OpenAI Chat 采用 Message Roles。

现代 OpenAI 模型更强调 `developer` role；大量 OpenAI-compatible 服务和现有客户端仍广泛使用 `system` role。

典型结构可以先看成：

```json
{
  "model": "qwen3.6",
  "messages": [
    {
      "role": "system",
      "content": "你是部门内网模型 API 培训助手……"
    },
    {
      "role": "user",
      "content": "Responses Vision 当前实测结论是什么？"
    }
  ]
}
```

【截图占位 API-SYS-01｜Cherry OpenAI Chat Request：system/developer + user】

培训时必须以当前 Cherry + 内网 qwen3.6 的真实 Request 为准：

> **当前客户端究竟发送 `system` 还是 `developer`，现场看 Network，不根据 OpenAI 官方新接口直接推断内网兼容行为。**

---

### OpenAI Responses：更直接的 `instructions`

Responses API 可以把高层指令放在顶层：

```json
{
  "model": "qwen3.6",
  "instructions": "你是部门内网模型 API 培训助手……",
  "input": "Responses Vision 当前实测结论是什么？"
}
```

【截图占位 API-SYS-02｜Cherry Responses Request：instructions + input】

这里有一个工程细节值得点一下：

> `instructions` 是当前 Response Request 的指令。应用如果管理多轮状态，仍然要明确自己如何在后续请求中继续提供这些长期规则。

所以 Cherry Assistant / Open WebUI Workspace Model 的价值之一，就是：

> **替用户持续管理这些长期 Instructions，而不是让用户每轮重新粘贴。**

---

### Anthropic Messages：顶层 `system`

Anthropic Messages 不是在 `messages[]` 中加入一个 `role=system`。

典型方式是：

```json
{
  "model": "qwen3.6",
  "system": "你是部门内网模型 API 培训助手……",
  "messages": [
    {
      "role": "user",
      "content": "Responses Vision 当前实测结论是什么？"
    }
  ]
}
```

【截图占位 API-SYS-03｜Cherry Anthropic Request：top-level system + messages】

于是同一句长期指令，在三套协议里可能对应：

| 协议 | 长期指令典型位置 |
|---|---|
| OpenAI Chat | `system/developer message` |
| OpenAI Responses | `instructions` |
| Anthropic Messages | 顶层 `system` |

【图示占位 API-SYS-04｜同一个 System Prompt → 三种 API Schema】

这一页非常适合和前面的“三协议”演示连起来：

> **Prompt 的语义可以相同，但协议表达形式不同。**

---

## 1.4B System Prompt、User Prompt、Context 到底什么关系？【主讲】

可以用一个很简单的分层理解：

```text
System / Developer Instructions
= 长期规则、角色、边界

User Prompt
= 这一次具体要做什么

Context
= 本轮模型真正能看到的全部输入材料
```

Context 可能同时包含：

- System / Developer Instructions；
- 当前 User Prompt；
- 历史对话；
- 文件内容；
- 图片；
- Knowledge Retrieval Result；
- Web Search Result；
- Tool Result。

因此：

> **System Prompt 是 Context 的一部分，但 Context 不等于 System Prompt。**

【图示占位 PROMPT-01｜System Prompt / User Prompt / Context 三层关系】

这张图后面会继续连接：

> Cherry Assistant Instructions  
> Open WebUI Workspace System Prompt  
> AGENTS.md / Project Instructions

它们作用范围不同，但都在解决：

> **“哪些规则应该稳定、重复地进入模型当前工作上下文？”**

---

## 1.4C 脱离 Cherry 再手工发一次 GET / POST：证明 UI 只是客户端【主讲】

现在再使用 Postman 或 curl。

### GET

```http
GET <BASE_URL>/v1/models
Authorization: Bearer <API_KEY>
```

【截图占位 API-POST-01｜Postman / curl GET /v1/models】

### POST

选择最容易看懂的 OpenAI Chat：

```http
POST <BASE_URL>/v1/chat/completions
```

Body：

```json
{
  "model": "qwen3.6",
  "messages": [
    {
      "role": "user",
      "content": "请只回答：CHAT_OK"
    }
  ],
  "temperature": 0,
  "max_tokens": 128
}
```

【截图占位 API-POST-02｜Postman POST Chat：Body + Response】

【录屏占位 API-R09｜Cherry Request → Postman 构造同类 GET/POST】

于是关系就非常清楚：

```text
Cherry Studio
Open WebUI
Postman
Python
Agent
业务应用
      │
      ↓
  API Protocol
      ↓
  Model Service
      ↓
    qwen3.6
```

【图示占位 API-POST-03｜不同客户端 → Protocol Adapter → 同一模型服务】


## 1.4D API 不等于 Chat：一旦脱离聊天框，模型就是一种可编程能力【主讲】

到这里学员很容易形成另一个误区：

> “既然模型是通过 API 调用，那 API 的主要用途是不是就是自己做一个聊天机器人？”

不是。

Chat 只是最容易被普通用户感知的一种应用形态。

从程序视角看，一次模型调用更接近：

```text
Input
+ Instructions
+ Parameters / Output Contract
→ Model API
→ Output
```

只要改变输入、固定指令和输出约束，同一个模型服务就可以被嵌入很多完全没有“聊天窗口”的业务流程。

【图示占位 API-APP-01｜同一个 Model API → Chat / Translation / Vision / JSON / Classification / Agent】

### 例子一：文本翻译

程序直接把一段英文送入模型：

```text
The device entered thermal protection mode after 30 seconds.
```

固定指令：

```text
翻译为简洁、准确的技术中文。只返回译文。
```

最终应用可能只有：

```text
原文输入框
→ 翻译按钮
→ 中文结果
```

用户甚至不需要知道背后是一个大模型。

【截图占位 API-APP-02｜同一 qwen3.6：Translation Request / Response】

---

### 例子二：非结构化文本 → 结构化 JSON

例如测试日志：

```text
SN=A102，温度 86.3°C，电压 3.28V，
测试结果 FAIL，错误码 TEMP_HIGH。
```

可以要求模型整理为：

```json
{
  "sn": "A102",
  "temperature_c": 86.3,
  "voltage_v": 3.28,
  "result": "FAIL",
  "error_code": "TEMP_HIGH"
}
```

然后程序继续：

```text
Model Output
→ JSON Parse
→ Schema / Type Validation
→ Database / Workflow
```

【截图占位 API-APP-03｜文本 → JSON → Parse / Validate】

这里必须讲一个工程边界：

> **“Prompt 里写只返回 JSON”不等于协议层 Structured Output。**

OpenAI 当前 API 已经有 JSON Mode / Structured Outputs / JSON Schema 等机制，但部门内网 qwen3.6 当前 r4 正式验收还没有把 `response_format/json_schema` 纳入能力矩阵。

因此第一讲的严谨说法是：

> **当前可以演示 Prompt 约束 JSON + 程序端校验；协议级 Structured Outputs 是否兼容，需要后续单独实测后再下结论。**

不能因为服务“OpenAI-compatible”就自动推断所有 OpenAI 参数都兼容。

---

### 例子三：图片文字识别 / 标签识别

既然当前内网 qwen3.6 的 Vision 已经正式实测通过，那么程序可以直接把图片送进 Vision Request。

例如准备一张我们自己生成的字符图片：

```text
BLUE-7319
```

让模型只返回：

```text
BLUE-7319
```

【截图占位 API-APP-04｜自制字符图片 → Vision Request → 识别文本】

这就已经是一个最小 OCR / 标签识别应用，不需要任何聊天历史。

如果想借“验证码”帮助大家理解，也只使用：

> **自制的验证码样式测试图片。**

不把培训演示做成第三方网站 CAPTCHA 绕过。

---

### 例子四：网页截图 / UI 视觉检查

把我们自己的网页截图作为图片输入，让模型检查：

- 按钮是否重叠；
- 文本是否溢出；
- 间距是否异常；
- 移动端布局是否错位；
- 哪个区域最值得人工复核。

甚至可以要求返回：

```json
{
  "issues": [
    {
      "type": "layout",
      "region": "右上角",
      "description": "按钮与标题发生重叠",
      "suggestion": "检查响应式断点和容器高度"
    }
  ]
}
```

【截图占位 API-APP-05｜网页截图 → Visual QA → 问题列表】

这正好为后面 Agent + Browser + Playwright 埋伏笔：

> **Vision 可以先“看出问题”；Agent 再进一步操作浏览器、修改代码并重新验证。**

---

### 例子五：分类、抽取和流程路由

模型还可以作为业务流程里的一个节点。

例如：

```text
一条测试记录
↓
Model API
↓
NORMAL / REVIEW / INVALID
↓
程序决定后续流程
```

【截图占位 API-APP-06｜测试记录 → 分类 / 路由结果】

或者：

- 邮件 → 分类；
- 文档 → 字段提取；
- 测试日志 → 异常摘要；
- 用户反馈 → 标签；
- 设备描述 → 标准字段；
- 自然语言 → SQL/查询参数候选（仍需程序验证）。

这时候模型不再是：

> “一个等着人来聊天的页面。”

而是：

> **业务系统里的一个可调用智能能力。**

---

### 这一段现场只需要做一个 60～90 秒串联 Demo

【录屏占位 API-APP-R01｜同一 qwen3.6 API 连续完成：翻译 → JSON → Vision OCR → 网页截图检查】

重点固定：

- 同一个 Base URL；
- 同一个模型；
- 同一套 API 调用方式；
- 只改变 Input / Prompt / Output Contract。

不要做成六个产品功能介绍。

最后收束成：

```text
Model API
   │
   ├─ Chat
   ├─ Translation
   ├─ Extraction / JSON
   ├─ Vision / OCR
   ├─ Visual QA
   ├─ Classification
   ├─ Tool Calling
   └─ Agent
```

真正的业务应用更常见的是：

```text
业务输入
→ Preprocess
→ Prompt / Instructions
→ Model API
→ Parse / Validate
→ Business Logic
→ UI / DB / Workflow
```

这也是第一讲必须建立的一个核心认知：

> **大模型的价值不等于“会聊天”。API 的意义，是把模型能力嵌入程序、流程和系统。**

对应可运行代码：

```text
demos/api-applications/
├─ translate.py
├─ json_extract.py
├─ vision_ocr.py
├─ visual_qa.py
├─ run_all.py
└─ token-output-speed/
```

其中 `run_all.py` 会显示同一个 Base URL 和 Model，并连续运行四个真实 API 应用；Token Speed 页面负责离线体感演示。

对应 Demo 总入口：

`demos/api-applications/README.md`

证据边界：

`docs/references/chat-workbench-api-application-evidence-2026-09.md`


## 1.5 为什么“我手工调通一次”还不够？【扩展】

手工 GET / POST 非常适合学习和调试。

但如果我们要回答：

> **这个内网模型到底支持哪些接口和能力？**

只手工点几次就不够了。

因为至少要重复验证：

- 基础 Endpoint；
- 非流式；
- SSE；
- Thinking；
- Tool Calling；
- Tool Result；
- Responses；
- Anthropic Messages；
- tokenize / detokenize；
- Vision；
- Vision + Tool Calling；
- /metrics；
- OpenAPI。

所以我们在仓库里不是只保留了一张“测试成功”截图，而是建立了正式自动验收脚本：

```text
api/qwen/qwen_api_training_test.py
```

【截图占位 API-TEST-00｜qwen_api_training_test.py 文件头 + 覆盖范围】

这里不要把脚本逐行讲解。

只解释它做了三件非常重要的事情。

### 第一：自动构造请求

脚本直接使用 HTTP API，对各类 Endpoint 发出请求。

例如：

```text
GET  /v1/models
GET  /version
GET  /metrics
GET  /openapi.json

POST /tokenize
POST /detokenize

POST /v1/chat/completions
POST /v1/responses
POST /v1/messages
```

### 第二：不是只看 HTTP 200，而是做断言

例如：

`/v1/models`

不仅判断：

> HTTP 200。

还验证：

- 是否真的存在 `qwen3.6`；
- 是否读到 `max_model_len`。

Tool Calling 不只是判断：

> 请求没报错。

还验证：

- 是否真的返回标准 Tool Call；
- Tool Result 回灌后模型能否继续生成最终回答。

Vision 也不是：

> 返回了一段文字就 PASS。

而是使用固定 Ground Truth 检查数量、颜色、位置和文本。

这体现一个工程原则：

> **接口“响应了”和接口“满足我们需要的语义”是两回事。**

### 第三：所有原始证据自动落盘

每一个测试项保存：

- Request；
- Response；
- HTTP Status；
- elapsed time；
- SSE 原始事件；
- attempts；
- analysis；
- PASS / FAIL。

最后再生成：

- `manifest.json`；
- `summary.md`；
- 正式报告。

API Key 在落盘前自动脱敏。

【截图占位 API-TEST-02｜单条测试 record：Request / Response / Analysis】

【截图占位 API-TEST-03｜结果目录树：records / SSE / manifest / summary】

这就把：

> “我今天手工试了一下，好像能用”

升级成：

> **“我们有一套可重复、可留档、以后模型升级还能重新跑的接口验收方法。”**

---

## 1.6 当前内网 Qwen 到底测出了什么？【扩展 / 证据】

当前正式基线：

```text
api/qwen/results/20260930_095033/
```

正式报告：

```text
api/qwen/reports/qwen36_api_test_report_20260930.md
```

脚本版本：

`2026-09-30-r4`

当前模型：

`qwen3.6`

当前服务版本：

`vLLM 0.23.0`

Context 配置：

`131072`

本轮总结果：

> **29 项：28 PASS、1 SKIP、0 FAIL、0 ERROR。**

而且本轮所有实际执行请求都是一次成功，没有触发真实网络重试。

【截图占位 API-TEST-01｜正式 r4 测试总览：28 PASS / 1 SKIP】

建议课堂不要把 29 行全部念一遍，而是整理成能力矩阵：

| 能力 | 当前实测 |
|---|---|
| `/v1/models` / `/version` | PASS |
| `/tokenize` / `/detokenize` | PASS |
| OpenAI Chat 非流式 / SSE | PASS |
| Chat Tool Call / Tool Result Loop | PASS |
| OpenAI Responses 非流式 / SSE | PASS |
| Responses Function Call / Tool Result Loop | PASS |
| Anthropic Messages 非流式 / SSE | PASS |
| Anthropic Tool Use / Tool Result Loop | PASS |
| Chat Vision / Vision SSE | PASS |
| 多图 Vision | PASS |
| Vision + Tool Calling | PASS |
| Responses Vision | PASS |
| Anthropic Vision | PASS |
| `/metrics` / `/openapi.json` | PASS |
| 公网 Remote Image URL | SKIP（默认不测公网 URL） |

【图示占位 API-TEST-04｜Qwen 当前协议 / 能力矩阵】

这里一定要保留几个“有价值的不完美结果”，因为它们比一张全绿表更能体现工程水平。

### Thinking：PASS 不等于回答完整

当前正式记录中：

Thinking OFF：

- 检测到 reasoning 关闭；
- 约 70.82 s；
- `finish_reason=length`。

Thinking ON：

- 检测到 reasoning；
- 约 78.16 s；
- 同样 `finish_reason=length`；
- 最终 `content=null`。

所以这里的 PASS 只表示：

> Thinking 开关行为被检测到。

不表示：

> 这个业务问题已经得到完整高质量回答。

### Anthropic：协议主体可用，但 Thinking 关闭存在兼容差异

Anthropic Messages：

- 文本；
- SSE；
- Tool Use；
- Tool Result；
- Vision；

本轮都已经通过。

但 `thinking.type=disabled` 后仍观察到 thinking。

因此正确表述应该是：

> **Anthropic 协议主体与 Tool Loop 当前实测可用，但关闭 Thinking 的参数仍存在兼容差异。**

### Responses Vision：曾经的 400 不是模型“不支持”

旧测试中 Responses Vision 曾经 HTTP 400。

进一步检查 OpenAPI 后发现：

> 请求漏掉了当前 Schema 要求的 `detail` 字段。

r4 改成：

```json
{
  "type": "input_image",
  "detail": "auto",
  "image_url": "data:image/png;base64,..."
}
```

以后正式 PASS。

这是第一讲非常好的工程案例：

> **看到 400，先查 Error Body、Schema 和 OpenAPI，不要直接下结论“模型不支持”。**

---

## 1.7 建议现场真正运行一次自动测试，但不要把 29 项全等完【备用 / 演示】

【录屏占位 API-R10｜运行 qwen_api_training_test.py → PASS 输出 → 打开 summary / record】

现场建议两种方式。

### 方式 A：完整预录

提前运行完整 r4 测试。

录到：

- Terminal；
- PASS / SKIP；
- 结果目录；
- summary；
- 某一条 record。

课堂剪成 60～90 秒。

### 方式 B：现场只跑一个子集 / 展示已有正式结果

由于 Thinking、多图 Vision 等测试耗时较长，不建议现场等待完整 29 项。

现场只演：

- models；
- chat；
- tool；
- metrics；

其余直接打开正式基线报告。

这样既有：

> “现在真的能跑”

又不会让课堂被模型等待时间拖垮。

---

## 1.8 从测试脚本得到一个很重要的方法论【主讲简述】

这套 Qwen 测试真正应该让大家学会的，不是 Python 语法。

而是一种工程方法：

```text
手工探索
→ 找到正确 Request
→ 明确 Expected Result
→ 写自动断言
→ 保存原始证据
→ 形成 Baseline
→ 后续升级重新 Regression
```

这和第四讲的软件自动测试其实是一件事。

> **AI API 也应该被当成真实工程接口来验收，而不是“聊两句感觉不错”就算通过。**

---

# 第二幕：为什么第二轮对话“记得”第一轮？【主讲】

> **叙事转折：** 第一幕已经证明“聊天框只是客户端、背后是 API”。现在继续追问：如果每次都是一次新的 HTTP 请求，第二轮为什么还能知道第一轮说过什么？

接下来不要急着讲 Context Window。

先现场做两轮对话。

第一轮：

> 我给这个项目起名叫“小明计划”。

第二轮：

> 我刚才给它起了什么名字？

此时大家看到模型能够回答“小明计划”，很自然会产生一种感觉：

> 模型记住了。

但我们再看第二轮 Request。

【截图占位 API-NET-04A｜第一轮 Request】

【截图占位 API-NET-04B｜第二轮 Request】

【截图占位 API-NET-04C｜两轮 Request Diff，高亮历史消息重新进入请求】

【录屏占位 API-R02｜连续两轮对话，展示第二轮 Request 中包含前文】

这时候再解释：

> 对大多数普通 API Chat 来说，所谓“连续对话”，首先是应用把需要保留的历史内容再次放进下一轮请求。

模型当前真正能够利用的是：

> **这一轮请求中进入 Context 的内容。**

因此 Context 不应被理解成一个抽象模型参数。

可以把它理解为：

> **这一次模型真正摆在桌面上能够看的材料。**

它可能包括：

- System Instructions；
- 用户当前问题；
- 历史对话；
- 上传文档；
- Tool Result；
- 图片；
- Agent 搜索得到的文件片段；
- Memory 中被重新取回的内容。

这也自然解释了为什么后面知识库、Agent、Memory 都绕不开 Context。

---

# 第三幕：走进一次推理——Token、Context、Prefill 与 Decode【主讲】

> **叙事转折：** 第二幕已经看到应用会把历史重新放进 Context。接下来终于进入模型内部：这些文字怎样变成模型能计算的数据，又怎样重新变成人能读的文字？

知道了 Context 是“模型当前桌面上的材料”，再讲 Token 就容易得多。

模型并不是按“Word 页数”或者“中文字符数”直接处理文本。对文本输入来说，进入大模型本体之前，首先要经过与模型配套的 Tokenizer，把字符串编码成 Token ID。

这一段不把 Tokenizer 算法讲成 NLP 理论课，而是直接回答四个工程问题：

1. 文本怎样变成模型能够计算的数据？
2. 模型推理时到底输出什么？
3. 为什么 Prefill 和 Decode 是两种不同的计算阶段？
4. 为什么“百万 Token”在真实长上下文工作负载里并没有想象中那么多？

---

## 3.1 从文本到 Token，再从 Token 回到文字：一次文本 LLM 推理的完整链路

可以先给学员看这一条最重要的数据流：

```text
用户输入 / System Prompt / 历史对话 / 检索结果
                    ↓
                Tokenizer
                    ↓
             Token ID 序列
                    ↓
                Embedding
                    ↓
              Transformer
                    ↓
     下一个 Token 的 logits / 概率分布
                    ↓
        Sampling / Decoding Strategy
                    ↓
            选出下一个 Token ID
                    ↓
       追加到序列，继续下一步 Decode
                    ↓
               Detokenize
                    ↓
               人类可读文本
```

【图示占位 TOKEN-01｜Text → Tokenize → Embedding → Transformer → Token → Detokenize】

这里要特别纠正两个常见误解。

第一：

> **LLM 本体并不是直接“读汉字”或“读单词”，而是在 Token ID 映射成的向量上进行计算。**

第二：

> **模型每一步严格来说并不是直接“输出一句文字”，而是计算整个词表中“下一个 Token”的 logits / 概率分布，再由采样策略选出一个 Token。**

因此，自回归文本大模型可以粗略理解为不断重复：

```text
已有 Token 序列
↓
预测下一个 Token
↓
把新 Token 追加回序列
↓
继续预测
```

也就是：

```text
P(t[n+1] | t[1], t[2], ... , t[n])
```

前端看到的“逐字打字”，底层通常更接近“逐 Token 生成并持续解码”。需要提醒：

> **1 Token 不等于 1 个汉字，也不等于 1 个英文单词。**

同一段文字在不同模型家族下，因为 Tokenizer / Vocabulary 不同，Token 切分和 Token 数也可能不同。

当前内网 qwen3.6 正式测试已经验证：

- `POST /tokenize`；
- `POST /detokenize`；
- Context 配置为 `131072`。

课堂上不要只展示接口 PASS，直接做一个往返实验：

```text
"人工智能正在改变软件开发方式"
        ↓ /tokenize
[token_id_1, token_id_2, ...]
        ↓ /detokenize
"人工智能正在改变软件开发方式"
```

【截图占位 TOKEN-02｜内网 qwen3.6 /tokenize：文本 → Token IDs + 数量】

【截图占位 TOKEN-03｜内网 qwen3.6 /detokenize：Token IDs → 文本】

【录屏占位 TOKEN-R01｜同一文本执行 tokenize → detokenize 往返】

这个 Demo 的目的不是让大家背 Token ID，而是建立一个直觉：

> **大模型的输入输出计量单位，首先是 Token，而不是“页”“字”或者“句子”。**

---

## 3.1A 为什么推理还要分 Prefill 和 Decode？

把完整链路再拆成两个阶段就容易理解性能指标。

### Prefill：先把这一次已有的上下文“读进去”

例如本轮请求一共包含 60,000 Token：

```text
System Prompt
+ 历史对话
+ 当前问题
+ 文件/知识库片段
+ Tool Result
= 60,000 input tokens
```

模型首先要处理这些已有 Token，并建立后续生成所需的中间状态 / KV Cache。

这一阶段称为：

> **Prefill / Prompt Processing**

所以输入越长，并不是“反正已经写在请求里了，就没有成本”。

### Decode：再一个 Token、一个 Token 地往后生成

Prefill 完成以后，模型开始：

```text
生成 Token 1
↓
追加
↓
生成 Token 2
↓
追加
↓
生成 Token 3
...
```

这一阶段称为：

> **Decode / Generation**

所以我们后面讲性能时要区分：

- 输入有多少 Token；
- Prefill 多快；
- 首 Token 要等多久（TTFT）；
- 后续 Decode 每秒能生成多少 Token；
- 最终一共输出多少 Token。

【图示占位 TOKEN-04｜一次请求：60k Input → Prefill → First Token → Decode → Output】

这也正好连接第五节的 TTFT / Tokens/s / Total Latency。

---

## 3.1B “百万 Token 很多”是一个很容易产生的错觉

这里建议现场直接算一笔账。

假设某种额度、计费统计或吞吐预算按 **1,000,000 input tokens** 计算。

如果一次真实工程请求已经带入：

```text
60,000 input tokens
```

那么即使完全不算输出：

```text
1,000,000 / 60,000 ≈ 16.7
```

也就是说，大约十几次这样的请求，就已经接近 100 万输入 Token。

【图示占位 TOKEN-05｜1,000,000 Token ÷ 60,000 Token/次 ≈ 16.7 次】

但这里必须把三个概念分开，避免讲错：

| 概念 | 含义 |
|---|---|
| Context Window | **单次推理最多能容纳多少 Token** |
| 本次 Input Tokens | **这一轮请求实际送进去多少 Token** |
| Token 额度 / 计费 / 吞吐统计 | **一段时间或一个账户累计处理了多少 Token** |

因此：

> **“模型支持 131K Context”不等于“我有 131K Token 的总额度”；“百万 Token 额度”也不等于“模型拥有百万 Token Context Window”。**

而在普通多轮 Chat 中，如果应用每一轮都重新把历史消息带回请求，累计 Token 消耗还可能比直觉更快。

例如每轮新增约 10k 内容，简单示意：

```text
第 1 轮：10k
第 2 轮：20k
第 3 轮：30k
第 4 轮：40k
...
```

累计消耗并不是只算最后一轮的 40k，而是这些请求分别都发生了 Prefill 和 Token 处理。

这个例子后面可以继续连接到：

- 长对话为什么越来越重；
- 为什么 Agent 要做 Context Compaction；
- 为什么 RAG 不应该把检索到的所有资料都无限塞进上下文；
- 为什么“上下文很长”不等于“可以不做知识检索和上下文管理”。

---

## 3.1C 为什么 Token 值得关心？

因为 Token 直接关系到：

- 输入长度；
- 输出长度；
- Context 占用；
- Prefill 工作量；
- KV Cache；
- 推理时间；
- 服务吞吐；
- API 成本或额度。

这一节最后只留一句话：

> **Token 不是一个计费术语，而是理解模型输入、推理、性能、上下文和成本的共同尺度。**

## 3.2 Context Window 是什么？

它可以先粗略理解为：

> **一次推理最多允许摆到模型桌面上的 Token 数量。**

但这里马上提醒：

> **Context Window 是容量上限，不等于有效知识容量。**

这个问题第二讲知识库会专门展开。

本讲只需要埋下伏笔：

> 能塞进去，和模型能不能稳定找到、正确利用，是两件事。

## 3.3 为什么长对话会越来越“重”？

因为随着越来越多历史被带入请求：

- Prefill 增加；
- KV Cache 占用增加；
- 服务端资源增加；
- 应用可能需要做截断、摘要或者 Compaction。

所以长上下文不是一个“免费无限记忆”。

这为第三讲理解 Agent Context Management 做准备。

---

# 第四幕：应用怎样替模型组织信息——Prompt、附件、Knowledge 与工作台【主讲】

> **叙事转折：** 模型每次真正能处理的是有限 Context。于是应用层的关键职责就出现了：哪些规则长期放进去？文件怎么放？知识怎么选？谁替用户管理这些上下文？

## 4.1 文件作为附件时，到底怎样进入模型？【主讲】

这里要专门纠正一个很常见的说法：

> “上传文件以后，应用就是把文件转成文本塞进上下文。”

**有时候是，但不能一概而论。**

文件进入模型大致有四种典型路径。

---

### 4.1.1 路径一：客户端先解析成文本，再放进 Prompt / Message

一些 Chat 客户端会先在本地或服务端做：

```text
DOCX / TXT / Markdown
↓
Parse
↓
Extracted Text
↓
Message / Context
↓
Model
```

【图示占位 FILE-01｜Client Parse → Text → Context】

这时模型最终看到的确实主要是：

> **提取后的文本。**

但问题也很明显：

- 表格结构可能丢失；
- 图片和图表可能丢失；
- 页码 / 标题层级可能变化；
- 文件越大，占用 Context 越多。

因此不能只问：

> “支持不支持上传 Word？”

还要问：

> **它是怎样解析 Word 的？**

---

### 4.1.2 路径二：API 原生支持 File / Document Input

现在一些模型 API 已经可以直接表达：

> “这一项输入是一个文件。”

例如 OpenAI Responses 支持 `input_file`，可以使用：

- uploaded `file_id`；
- Base64；
- File URL。

服务端再根据文件类型处理。

当前 OpenAI 官方行为包括：

- PDF：可同时提取文本和页面图像；
- DOCX / PPTX / TXT / Code 等非 PDF 文档：主要提取文本；
- Spreadsheet：走专门的表格处理流程。

【图示占位 FILE-02｜Responses input_file → Server-side File Processing → Model】

Anthropic Messages 对 PDF 也支持：

- URL；
- Base64 `document` block；
- Files API `file_id`。

【图示占位 FILE-03｜Anthropic document block / file_id】

因此：

> **API 中出现 file_id / input_file / document，不等于文件二进制原封不动地“塞进 Token”。**

平台仍然会执行某种文件解析、视觉处理或文档处理。

---

### 4.1.3 路径三：图片直接作为多模态输入

图片附件又不同。

它可能作为：

- image URL；
- Base64 image；
- image content block；

交给 Vision Model。

【截图占位 FILE-04｜Cherry 图片附件对应的 Vision Payload】

这时不应该简单理解成：

> “先 OCR 成文字再给模型。”

多模态模型可以直接处理图像表示。

OCR 可能是任务的一部分，但不是所有 Vision 输入的唯一机制。

---

### 4.1.4 路径四：文件进入 Knowledge Base，再按需检索

如果文件不是临时附件，而是反复使用的知识：

```text
File
↓
Parse
↓
Chunk
↓
Index
↓
Question
↓
Retrieve
↓
Relevant Chunks
↓
Context
↓
Model
```

【图示占位 FILE-05｜Attachment vs Knowledge/RAG】

Open WebUI 的 Full Context 则是另一个特例：

```text
File / Note
↓
Whole Content
↓
Context
↓
Model
```

因此“上传文件”至少要先问：

> **这是临时附件、原生 File Input、Vision Input、Full Context，还是 Knowledge/RAG？**

这五个词对用户看起来都像：

> “我上传了一个文件。”

但底层机制完全不同。

---

### 4.1.5 用 Cherry / Open WebUI 做一个附件路径实测

建议第一讲准备同一个很短的 Markdown 文件：

```text
attachment-demo.md
```

里面放一个非常容易验证的唯一字符串，例如：

```text
TRAINING_ATTACHMENT_CODE = BLUE-7319
```

分别做三次：

1. Cherry 直接作为临时附件；
2. Cherry 放入 Knowledge 后再问；
3. Open WebUI 使用 Full Context / Workspace Knowledge。

固定问题：

> 文档中的 TRAINING_ATTACHMENT_CODE 是什么？

然后观察：

- Network Request；
- Context / Retrieval Trace；
- 是否出现全文；
- 是否只出现 Chunk；
- 是否出现 file/document 类型。

【录屏占位 FILE-R01｜同一文件三种进入 Context 的方式】

这个 Demo 的价值非常大：

> **不要根据 UI 上“回形针”图标猜底层机制，直接看 Request / Trace。**

---

## 4.2 Prompt Engineering：提示词需要“框架”吗？【扩展】

> **现场处理：** 主讲只保留一个工程 Prompt 骨架：`Goal / Context / Constraints / Output / Examples / Verification`。RTF、CO-STAR、CRISPE 只作为“社区记忆法”快速带过或留作答疑，避免把第一讲重新讲成“提示词技巧课”。

在大家理解 System Prompt、User Prompt、Context 以后，再简单介绍 Prompt Engineering。

先给一个结论：

> **提示词框架有用，但不要把框架当成模型的魔法口诀。**

OpenAI 和 Anthropic 当前官方 Prompt Guidance 的共同点，其实非常朴素：

- 任务要明确；
- 给必要 Context；
- 约束要明确；
- 指定输出格式；
- 必要时给 Examples；
- 复杂任务进行结构化组织。

所以培训不要求大家背十套缩写。

我们统一推荐一个工程化 Prompt 骨架：

```text
Goal / Task
Context
Constraints
Expected Output
Examples（必要时）
Verification / Success Criteria（工程任务）
```

【图示占位 PROMPT-02｜推荐 Prompt 骨架】

对于普通办公问答，再加 Role 即可：

```text
Role
Task
Context
Constraints
Format
Examples
```

---

### 4.2.1 可以认识几个社区常见框架，但不要迷信【备用】

### RTF

```text
Role
Task
Format
```

适合：

> 很短、输出要求明确的日常任务。

### CO-STAR

社区常见表达：

```text
Context
Objective
Style
Tone
Audience
Response
```

适合：

> 文案、沟通、面向特定受众的内容生产。

### CRISPE

常见版本强调：

- Capacity / Role；
- Insight / Context；
- Statement / Task；
- Personality；
- Experiment / Variants。

适合：

> 需要角色、背景、风格和多个候选版本的任务。

【图示占位 PROMPT-03｜RTF / CO-STAR / CRISPE 一页速览】

但这里要明确：

> **这些大多是社区记忆法，不是 API 标准，也不是模型厂商规定的必填字段。**

真正重要的是：

> 有没有把模型完成任务所需的信息说清楚。

---

### 4.2.2 工程任务里，比“给模型一个专家角色”更重要的是什么？【主讲简述】

例如：

> “你是一名资深软件工程师，请帮我修 Bug。”

看起来像 Prompt Engineering。

但缺了：

- 哪个仓库；
- 当前现象；
- 不能改什么；
- 怎么验证；
- 什么算完成。

更工程化的表达应该是：

```text
Goal
修复 85°C 边界判断错误。

Context
代码位于 src/sensor_guard/。
当前测试 test_high_temperature_boundary 失败。

Constraints
不改变其他温度阈值。
遵守 AGENTS.md。
不新增依赖。

Verification
pytest 必须全部通过。
最后给出 git diff 摘要。
```

所以这里提前埋下第四讲最重要的一句话：

> **对于复杂工程任务，Problem / Requirement / Constraint / Verification 往往比“你扮演什么专家”更重要。**

---

### 4.2.3 Prompt、System Prompt、Project Rules 不要混成一个东西【扩展】

最后做一张范围对比：

| 类型 | 典型作用范围 | 示例 |
|---|---|---|
| User Prompt | 当前任务 | “总结这份报告” |
| System Prompt | 一个 Assistant / Workspace | “优先依据内网资料回答” |
| Project Rules | 一个项目 / Workspace | AGENTS.md / CLAUDE.md |
| Skill | 一类重复工作 | “如何做服务健康检查” |
| Test / Eval | 判断是否做对 | pytest / Benchmark |

【图示占位 PROMPT-04｜Prompt → System Prompt → Project Rules → Skill → Test】

这张图非常重要，因为它把第一讲和第三、第四讲接起来：

> **不要把所有长期知识、项目规则和工作方法都塞进一个越来越长的 Prompt。**

---

## 4.3 Cherry Studio：一个 Chat 工作台到底替我们做了哪些事？【主讲】

在第一讲前面，我们已经从 Network 里看到：

> Chat UI 背后是 API Request。

现在可以反过来再看一次 Cherry Studio 的界面。

你会发现一个成熟的 Chat 工作台并不只是：

> 文本框 + 发送按钮。

它实际上正在帮用户组织：

- 模型；
- System Prompt / Instructions；
- 模型参数；
- 对话历史；
- 知识库；
- 联网搜索；
- 文件 / 图片；
- MCP / Tool；
- Context 管理。

这些东西最后都会以不同方式影响：

```text
Model
Context
Tools
Request Parameters
```

所以这一段的目的不是教“Cherry Studio 全功能使用手册”，而是让学员理解：

> **我们在 UI 里勾选的每一个能力，背后都对应某种上下文、参数或工具变化。**

---

### 4.3.1 助手指令：为什么不需要每轮都重新说“你是谁”

Cherry Studio 的“助手”可以保存：

- 默认模型；
- 模型参数；
- 提示词 / Instructions；
- 关联知识库；
- MCP 工具。

例如创建一个：

> “内网 Qwen API 培训助手”。

在提示词中写：

```text
你是部门内网模型 API 培训助手。
回答必须优先依据已关联的内网 API 测试资料。
如果资料中没有证据，应明确说明。
```

【截图占位 CH-ASSIST-01｜Cherry 新建/编辑助手：基础 + 默认模型】

【截图占位 CH-ASSIST-02｜Cherry 助手“提示词/Instructions”页】

然后新建两个对话。

让大家看到：

> 对话变了，但助手的系统指令仍然保留。

这可以直观对应：

```text
Assistant
≈ 一组可复用的角色 / Prompt / Model / Knowledge / Tool 预设

Conversation
≈ 在这个预设下的一段独立对话
```

这一点也为第三讲的 Project Instructions / AGENTS.md 做铺垫：

> 都是在解决“长期规则不要每轮重新说”的问题，只是作用范围不同。

---

### 4.3.2 模型配置：同一个问题为什么可以临时切模型？

Cherry 的助手可以指定默认模型，对话中也可以临时切换模型。

这里建议现场演示：

1. 助手默认使用内网 qwen3.6；
2. 打开对话；
3. 从顶部模型选择器切换另一个已配置模型；
4. 再切回内网模型。

【截图占位 CH-ASSIST-03｜助手默认模型 + 对话顶部模型切换】

教学点：

> **Model 是应用可以路由和替换的一层，不等于整个 Chat 应用。**

这与第一讲的“模型 ≠ Chat”形成呼应。

---

### 4.3.3 模型参数：UI 里的 Temperature、Top-P、Max Tokens 到底改了什么？

在 Cherry 的助手模型设置中，可以展示：

- Temperature；
- Top-P；
- Max Tokens；
- Streaming；
- Context 管理；
- Reasoning / Thinking（若当前模型/Endpoint 支持）；
- 自定义参数。

【截图占位 CH-ASSIST-04｜Cherry 助手模型参数】

不要讲成：

> Temperature=0.7 最好。

而要讲：

> **这些都是 Request Parameters。**

例如：

- Temperature：影响随机性；
- Max Tokens：限制本轮最大输出预算；
- Streaming：决定是否边生成边返回；
- Thinking / Reasoning：是否给模型更多推理预算；
- Context 管理：应用怎样处理越来越长的历史。

然后打开 Network 对比一次参数前后的 Request。

【录屏占位 CH-R04｜修改 Max Tokens / Thinking / Stream → Network Request 对比】

这样“模型参数”不再是 UI 黑盒。

---

### 4.3.4 知识库：勾一下之后，模型真的“学会”这些资料了吗？

Cherry 对话输入区可以选择已经创建的知识库，助手也可以预先关联知识库。

建议第一讲只做一个最小演示。

### 创建一个训练知识库

资料只放：

- 当前 Qwen API 正式测试报告；
- 一份 API 说明。

创建时展示：

- 知识库名称；
- Embedding 模型，或选择不使用 Embedding；
- 添加文件 / 笔记 / 目录 / 链接；
- 资料处理；
- 召回测试。

【截图占位 CH-KB-01｜Cherry 新建知识库】

【截图占位 CH-KB-02｜添加资料 + Chunk/处理结果】

【截图占位 CH-KB-03｜召回测试】

然后进入普通对话，在输入框工具栏勾选这个知识库。

固定问题：

> 当前内网 Qwen 的 Responses Vision 正式测试结论是什么？

【截图占位 CH-KB-04｜对话输入区勾选知识库】

【录屏占位 CH-R05｜不选知识库 vs 选择知识库 → 回答与引用变化】

这里第一讲只讲一个现象：

```text
Knowledge Base
↓
先检索相关资料
↓
Relevant Chunks
↓
进入本轮 Context
↓
Model Answer
```

然后明确告诉学员：

> **勾选知识库不是把资料重新训练进模型。它首先是在回答前把相关资料检索出来，再作为 Context 提供给模型。**

至于：

- BM25；
- Embedding；
- Chunk；
- Rerank；
- 长上下文；
- 版本治理；

第二讲再完整展开。

这样第一讲负责“看见机制”，第二讲负责“设计机制”。

---

### 4.3.5 联网搜索：为什么这和知识库不是一回事？

Cherry 对话输入区还可以打开网络搜索。

【截图占位 CH-WEB-01｜Cherry 对话输入区网络搜索按钮】

固定问一个有时间性的公开问题，例如：

> 某个开源项目当前最新 Release 是什么？

打开联网前后对比。

【录屏占位 CH-R06｜普通回答 vs 开启联网搜索 → Search Result / Citation】

这里不要把“联网”讲成模型突然拥有互联网。

更准确：

```text
User Question
↓
Search Tool / Search Provider
↓
Web Results
↓
Context / Tool Result
↓
Model
```

Cherry 当前支持配置搜索服务和 URL 获取服务，并且联网能力可以通过配置的搜索服务或模型自身支持的搜索能力实现；具体走哪条路径取决于当前版本、Provider 和配置。

因此：

> **Knowledge Base 和 Web Search 都是在补外部知识，但一个主要面向受控内部资料，一个主要面向实时公开信息。**

第二讲会继续比较它们的知识边界。

---

### 4.3.6 MCP / 工具调用：勾选工具以后发生了什么？

Cherry 助手可以关联 MCP，模型支持工具调用时，对话中就可以获得外部工具。

【截图占位 CH-TOOL-01｜Cherry 助手 MCP / Tool 配置】

【截图占位 CH-TOOL-02｜对话中的 Tool Call / Tool Result】

这时再回到第一讲已经讲过的 Tool Loop：

```text
User
↓
Model
↓
Tool Call
↓
Cherry / Harness 执行 Tool
↓
Tool Result
↓
Model
↓
Answer
```

因此 Tool Calling 的能力至少需要三层同时成立：

1. 模型支持；
2. API 协议支持；
3. 客户端 / Harness 能提供并执行 Tool。

这句话非常重要：

> **模型会 Tool Calling，不代表任何 Chat 客户端都自动拥有真实工具。**

---

### 4.3.7 一个 Cherry 对话到底可能包含哪些东西？

讲完所有选项以后，可以截一张最终界面。

【截图占位 CH-ASSIST-05｜同一对话：模型 + Knowledge + Web Search + Tool/MCP + 附件入口】

然后把它翻译成模型真正看到/能够调用的结构：

```text
Assistant Instructions
+ Conversation History
+ Current User Message
+ Knowledge Retrieval Results
+ Web Search Results
+ File / Image Content
+ Tool Definitions
+ Tool Results
+ Model Parameters
↓
Model API
```

【图示占位 CH-ASSIST-06｜Cherry UI 开关 → Context / Parameter / Tool 映射】

这一张图可以作为第一讲理解 Chat Application / Harness 的关键过渡图。

最终结论：

> **Cherry Studio 这样的 Chat 工作台，本质上是在帮助普通用户可视化地配置 Model、Context、Parameters 和 Tools。**

而 Agent 进一步做的事情是：

> 把这些能力放进一个能够围绕 Goal 持续执行、观察和验证的循环里。

---

## 4.4 Open WebUI v0.11.0：先和 Cherry 建立一一对应，再看服务端工作台有什么不同【主讲 + 扩展】

> **现场处理：** 第一讲只主讲三件事：① Cherry Assistant 与 Open WebUI Workspace Model 都是在“Base Model + 长期指令 + Knowledge”上做应用封装；② 两者本地/服务端数据边界不同；③ Knowledge 最终仍是在帮助应用组织 Context。Full Context、Focused Retrieval、Embedding、Note→Knowledge 等细节完整保留，但主要留给第二讲复用。

这一段值得先补一个“产品形态”的视角。

很多工程师最先接触的大模型开源工具，是运行在自己电脑上的桌面客户端 / Local-first 工作台。Cherry Studio 就很典型：

```text
Desktop Client
→ Local Conversation / Knowledge / Config
→ Model API
```

Open WebUI 则代表另一种非常重要的形态：

```text
Browser
→ Self-hosted Open WebUI Server
→ Server-side Chat / File / Note / Knowledge / Workspace
→ Model API
```

【图示占位 WB-COMP-00｜Local Desktop Client vs Self-hosted Server Workbench】

培训里不把：

> “Open WebUI 是最早 / 第一个 / 当时仅有的服务端开源项目”

写成硬事实，因为这需要完整的历史项目统计。

更稳妥、也更有教学价值的表述是：

> **在大量面向个人的桌面 / 本地客户端之外，Open WebUI 是一个非常典型的自托管、集中式 Server-side AI 工作台代表。**

为什么这个区别重要？

因为两边今天的功能越来越像，但：

> **数据主要落在哪里、谁来管理、多设备能否共享、能不能做用户/组/ACL，差别很大。**

这也是部门选型时比“哪个按钮更多”更应该先看的问题。

在进入 Open WebUI 之前，先不要把它当成另一个完全不同的产品世界。

先把 Cherry Studio 和 Open WebUI 中几个最常用概念一一对应起来：

| Cherry Studio | Open WebUI v0.11.0 | 本质上解决什么问题 |
|---|---|---|
| Assistant / 助手 | Workspace Model / Model Preset | 把基础模型封装成一个可重复使用的专用入口 |
| Assistant Instructions | System Prompt | 每轮调用模型时持续注入长期指令 |
| Knowledge Base | Knowledge / Note / Document | 给模型补充外部知识 |
| Assistant 关联 Knowledge | Workspace Model 关联 Knowledge | 让某个专用助手长期使用固定资料 |
| Conversation | Chat | 在同一个应用配置下进行一次具体会话 |
| MCP / Tool | Tools / Skills | 给模型提供外部动作或可复用能力 |

【图示占位 WB-COMP-04A｜Cherry Assistant ↔ Open WebUI Workspace Model 对应关系】

这张表的目的不是说：

> 两个产品完全一样。

而是先让大家看到：

> **它们都在做“基础模型之上的应用封装”。**

---

### 4.4.0 用同一套 System Prompt 和同一份知识，分别创建两个“内网 API 培训助手”【主讲】

为了把这个对应关系讲透，建议第一讲做一个非常直观的双端对照 Demo。

固定使用同一个基础模型：

> 内网 `qwen3.6`

固定使用同一段长期指令：

```text
你是部门内网模型 API 培训助手。
回答优先依据已经绑定的内网 API 测试资料。
如果资料中没有实测证据，应明确说明，不要猜测。
```

固定使用同一份知识：

- Qwen API 正式测试报告；
- 或一条包含当前实测结论的 Markdown Note。

### 在 Cherry Studio 中

```text
qwen3.6
+ Assistant Instructions
+ Cherry Knowledge Base
→ “内网 API 培训助手”
```

【截图占位 WB-COMP-04B｜Cherry Assistant：Model + Instructions + Knowledge】

### 在 Open WebUI 中

```text
qwen3.6
+ Workspace Model System Prompt
+ Knowledge / Existing Note
→ “内网 API 培训助手”
```

【截图占位 WB-COMP-04C｜Open WebUI Workspace Model：Base Model + System Prompt + Knowledge】

然后固定问同一个问题：

> 当前内网 Qwen 的 Responses Vision 正式测试结论是什么？如果历史上曾失败，请说明原因。

两边都应该优先基于绑定资料回答。

【录屏占位 WB-R03｜同模型 + 同 System Prompt + 同知识：Cherry Assistant vs Open WebUI Workspace Model】

这个 Demo 最重要的不是比较回答谁更好。

而是让学员看到：

> **当基础模型、长期指令和知识相同时，两个产品都可以形成一个“专用助手”。**

因此：

```text
Cherry Assistant
≈ Model + Instructions + Knowledge + Parameters + Tools

Open WebUI Workspace Model
≈ Base Model + System Prompt + Knowledge + Parameters + Tools/Skills
```

【图示占位 WB-COMP-04D｜两种产品统一抽象为 Application Preset】

这里给出一个非常重要的边界：

> **System Prompt 的作用首先是“每次调用模型时注入长期指令”，不是重新训练模型。**

同样：

> **Knowledge 的作用首先是把外部资料通过 Full Context 或 Retrieval 提供给模型，也不是把知识永久写入模型参数。**

所以两个产品的“智能体/工作空间模型”在这一层都可以理解成：

> **Application Preset / 专用应用配置。**

只有当进一步加入：

- Tool Calling；
- Runtime；
- 连续行动；
- Observe；
- Verify；
- Iterate；

才进入第三讲所说的完整 Agent 工作方式。

---

### 4.4.0A 为什么这组对应关系对后面理解 Agent 很重要？【主讲】

因为从这里开始，学员会看到一个连续演进：

```text
Base Model
↓
System Prompt
↓
Knowledge
↓
Parameters
↓
Tools
↓
Reusable Assistant
↓
再加 Runtime / Loop / Verification
↓
Agent
```

【图示占位 WB-COMP-04E｜从 Base Model → Assistant → Agent 的能力叠加】

也就是说：

> Cherry Assistant 和 Open WebUI Workspace Model 已经不是“裸模型”，但也还不等于完整工程 Agent。

它们正好处于：

```text
Model
→ Chat Application
→ Specialized Assistant
→ Agent
```

这条演进链的中间层。

这会让后面“为什么 Chat 不够、Agent 多了什么”变得非常自然。

---

Cherry Studio 更适合用来观察：

- Provider；
- API；
- Network；
- Assistant；
- 模型参数；
- 个人知识和工具。

部门当前内网还部署了 **Open WebUI v0.11.0**。

这正好可以用来说明：

> **Chat Workbench 不只有一种形态。**

Open WebUI 更适合展示另一类需求：

- 多用户入口；
- Workspace；
- 个人笔记；
- 文档上传；
- Knowledge；
- 可复用的模型/工作空间配置；
- 后续共享与权限治理。

【截图占位 OW-01｜当前内网 Open WebUI v0.11.0 首页 / Workspace 总览】

第一讲不要在这里展开完整 RAG 原理。

只让大家看见一个事实：

> **除了对话历史以外，Chat 工作台还可以把用户自己持续维护的笔记和文档变成可复用 Context / Knowledge。**

---

### 4.4.1 个人笔记：知识不一定来自“上传 PDF”【扩展 / 第二讲复用】

当前内网 v0.11.0 已实际走通：

- 用户可以创建自己的笔记；
- 笔记可以作为持续维护的 Markdown 内容；
- 可以上传文档；
- 后续在问答中把这些内容作为知识使用。

【截图占位 OW-07｜Open WebUI Notes：个人 Markdown 笔记】

【截图占位 OW-08｜Note / Knowledge 中上传文档】

这里可以用一个非常接地气的例子：

> 我今天测试了内网 qwen3.6，发现 Anthropic 的 Thinking 关闭参数还有兼容差异。

不一定先写一份正式 PDF。

完全可以先记成一条个人 Markdown Note。

这让大家理解：

> **知识资产不只有“正式文件”，个人工作笔记也可以逐步成为 AI 可复用上下文。**

但第二讲会继续强调：

> 个人笔记不等于部门 Source of Truth。什么时候应该升级成正式知识，需要治理。

---

### 4.4.2 同一个 Markdown 文档为什么可以选“完整文档”和“聚焦检索”？【扩展 / 第二讲复用】

这是当前内网 Open WebUI v0.11.0 很适合现场演示的一点。

对具体 Markdown / 文档，可以选择类似两种模式：

```text
Full Context / 完整文档
vs
Focused Retrieval / 聚焦检索
```

【截图占位 OW-09｜同一 Markdown：Full Context / Focused Retrieval 切换】

先不讲算法，只讲直觉。

### 完整文档

```text
Document
↓
整篇内容进入本轮 Context
↓
Model
```

适合：

- 短文档；
- 风格指南；
- 规则说明；
- 每次都应该完整看到的材料。

优点：

> 简单直接，不依赖向量召回。

代价：

> 文档越长，占用 Context 越多。

### 聚焦检索

```text
Question
↓
Retrieval
↓
Relevant Parts
↓
Context
↓
Model
```

适合：

- 长文档；
- 多份资料；
- 每次只需要其中局部内容。

优点：

> 不需要每轮把整篇文档都塞进去。

代价：

> 系统必须先“找对”。

这里先埋一个伏笔：

> **第二讲真正要解决的，就是“Focused Retrieval 到底怎样找、怎样验证找对没有”。**

---

### 4.4.3 没有配置 Embedding，为什么仍然能用知识回答？【扩展 / 第二讲复用】

这是当前内网 v0.11.0 特别值得讲的真实现象。

当前实例没有配置 Embedding Model，因此在相关知识内容上会提示：

> **没有向量化 / 未建立向量索引。**

【截图占位 OW-10｜当前内网提示：未配置 Embedding / 未向量化】

但实际已经走通：

1. 创建自己的知识 / 笔记；
2. 上传文档；
3. 在 Workspace 中引用该知识库；
4. 或直接在 Workspace 创建时的 Knowledge 选项中上传/关联文档；
5. 选择这个 Workspace / 对应模型配置进行问答；
6. 模型能够依据其中资料回答。

【截图占位 OW-11｜Workspace 绑定 Knowledge】

【截图占位 OW-12｜选择该 Workspace 后依据文档问答】

【录屏占位 OW-R03｜个人 Note/Document → Workspace Knowledge → 问答】

这时必须把结论讲严谨：

> **“能依据知识回答”不等于“向量检索已经生效”。**

如果使用的是 Full Context：

> 整篇内容直接进入 Context，不需要 Embedding。

如果选择的是 Focused Retrieval：

> Vector Retrieval 通常需要向量化；当前没有 Embedding 时，究竟走了关键词/BM25、Knowledge Tool、其他检索路径还是某种回退，需要结合当前实例配置和 Tool Trace 再验证。

因此培训现场不要说：

> “Open WebUI 没 Embedding 也能正常做向量 RAG。”

正确说法：

> **当前内网未配置 Embedding，但知识仍可被 Workspace 引用并用于回答；Full Context 明确不依赖向量检索，Focused Retrieval 的实际检索路径需要进一步实测确认。**

这个案例非常适合说明：

> **看到回答正确，不要反推底层机制；工程判断要看配置、请求和 Trace。**

---

### 4.4.4 Workspace：为什么它比“临时上传一个附件”更进一步？【扩展 / 第二讲复用】

一次聊天临时上传文件解决的是：

> 这次对话需要这份资料。

Workspace / 可复用模型配置解决的是：

> 这一类工作长期都需要这批资料和设置。

当前内网 v0.11.0 已经走通：

```text
个人 Note / Document
        ↓
Knowledge
        ↓
Workspace / 模型配置绑定
        ↓
选择该 Workspace
        ↓
持续问答
```

【图示占位 OW-13｜Note/Document → Knowledge → Workspace → Chat】

这与 Cherry Assistant 很相似：

```text
Cherry Assistant
= Model + Instructions + Knowledge + Tools

Open WebUI Workspace / Model
= Base Model + Prompt + Knowledge + Capabilities
```

具体产品结构不同，但解决的是同一类问题：

> **把一次性的 Chat 配置沉淀成可重复使用的工作上下文。**

---

### 4.4.5 Cherry Studio 与 Open WebUI：功能越来越像，但“数据边界”和“组织方式”不同【主讲】

如果只看今天的功能，两者其实越来越像：

- 都能选择模型；
- 都能设置 System Prompt / Instructions；
- 都能管理知识；
- 都能上传文件；
- 都能配置参数；
- 都可以把知识、Prompt 和工具组合成一个可复用入口。

所以培训不应该简单说：

> “Cherry 是聊天软件，Open WebUI 是知识库软件。”

更准确的区别首先来自：

> **它们运行在哪里，数据主要落在哪里，谁负责管理，以及面向个人还是面向集中共享。**

### Cherry Studio：桌面客户端，本机持久化为主

Cherry Studio 是桌面应用。

当前官方知识库说明明确：

> 加入 Cherry Knowledge Base 的数据保存在本地，文档副本进入 Cherry Studio 本地数据目录。

因此可以把它理解为：

```text
我的电脑
├─ Cherry Desktop
├─ Conversation / Settings
├─ Knowledge / Local Index
└─ Provider Config
          │
          ↓ API
   内网模型 / 云模型
```

【图示占位 WB-COMP-01｜Cherry：Local Desktop → Model API】

这类形态的优势：

- 个人配置灵活；
- 本地资料容易管理；
- 每个人可以有自己的 Assistant / Knowledge；
- 适合工程师个人桌面工作流；
- 不需要依赖一个统一 Web 门户才能管理自己的资料。

但这里要讲清一个非常重要的隐私边界：

> **“知识库文件存在本机”不等于“内容永远不离开本机”。**

如果实际调用的是远程模型 API：

```text
本地知识
↓
Retriever 选出相关内容
↓
进入 Prompt / Context
↓
通过 API 发给模型服务
```

所以真正的数据边界取决于：

- Knowledge 存在哪里；
- Embedding 在哪里算；
- Model API 在哪里；
- 哪些内容最终进入 Request。

---

### Open WebUI：服务端部署，浏览器只是入口

部门当前内网部署的是：

> **Open WebUI v0.11.0**

它更典型的形态是：

```text
浏览器 A ─┐
浏览器 B ─┼→ Open WebUI Server
浏览器 C ─┘      ├─ Accounts
                  ├─ Chats
                  ├─ Notes
                  ├─ Knowledge
                  ├─ Uploaded Files
                  ├─ Workspace Models
                  └─ Permissions
                           │
                           ↓
                     Model API
```

【图示占位 WB-COMP-02｜Open WebUI：Browser → Central Server → Model API】

Open WebUI 官方部署文档也把聊天、配置、上传文件、Knowledge 记录等作为服务端持久化数据管理；单机部署通常落在服务端 Data Directory / Database，规模化时还可以使用 PostgreSQL、共享文件系统或对象存储。

这里建议课堂上用：

> **“集中式服务端部署”**

而不是简单说：

> “一定上公网云。”

因为我们的场景是部门内网服务器，同样属于集中式 Server-side 模式。

这种形态的价值：

- 用户从浏览器即可访问；
- 多终端共享同一个账号和工作空间；
- 用户/Group/ACL 可以集中管理；
- Knowledge / Workspace 可以共享；
- 部门可以统一配置模型和能力。

相应地：

> **个人上传的文档、Note、Chat 等主要由这台 Open WebUI 服务器持久化管理，而不是只留在当前浏览器所在电脑。**

---

### 两个产品的数据边界，一张表讲清

| 维度 | Cherry Studio | 内网 Open WebUI v0.11.0 |
|---|---|---|
| 产品形态 | Desktop Client | Web / Server |
| 主要访问方式 | 本机桌面应用 | 浏览器访问集中服务器 |
| 配置/知识主要管理位置 | 本机 | Open WebUI 服务端 |
| 多终端一致性 | 取决于同步/迁移方式 | 同一账号访问服务器即可 |
| 多用户 / Group | 不是主要定位 | 原生更适合 |
| 个人知识 | 很适合 | Note / Personal Knowledge 已实测 |
| 部门共享知识 | 可做，但更偏个人端 | 更自然 |
| 数据治理 | 个人侧为主 | 服务端集中治理 |
| 模型调用 | Local/Remote Provider | Server → Model Provider |
| 典型定位 | 个人 AI 桌面工作台 | 部门 AI Portal / Workspace |

【截图/图示占位 WB-COMP-03｜Cherry vs Open WebUI 数据与应用边界对照】

结论不是：

> 谁替代谁。

而是：

> **Cherry 更接近“我的 AI 工作台”，Open WebUI 更接近“我们共同使用的 AI 门户”。**

---

### 4.4.6 Open WebUI Workspace Model 和 Cherry Assistant：其实在解决同一个问题【主讲】

现在把两边最容易混淆的功能放到一起。

### Cherry Assistant

可以预先保存：

- Model；
- System Prompt / Instructions；
- Parameters；
- Knowledge；
- MCP / Tools。

### Open WebUI Workspace / Model

当前 Open WebUI 官方定义也允许把：

- Base Model；
- System Prompt；
- Parameters；
- Knowledge；
- Tools / Skills；

组合成一个可重复选择的 Model Preset。

所以可以把两者都理解为：

> **在基础模型上加一层可复用的“应用配置”。**

```text
Base Model
   +
System Prompt
   +
Knowledge
   +
Parameters
   +
Tools
   ↓
Specialized Assistant / Workspace Model
```

【图示占位 WB-COMP-04｜Cherry Assistant vs Open WebUI Workspace Model】

例如都可以做一个：

> “内网 API 培训助手”

然后写 System Prompt：

```text
你负责回答部门内网模型 API 相关问题。
优先使用已绑定测试资料。
没有实测证据时明确说明。
```

两边最终本质上都是：

> **把 System Prompt 注入到后续模型调用中，并把知识、参数、工具等配置一起复用。**

因此这里要纠正一个容易产生的错觉：

> **创建 Assistant / Workspace Model 并没有重新训练模型。**

也不应因为 UI 上叫“Agent / Assistant”就自动理解成第三讲那种：

`Goal → Plan → Tool → Observe → Verify`

的完整 Autonomous Agent。

它首先是：

> **Model Preset / Application Wrapper。**

是否具备真正 Agent 行为，还取决于：

- Tool；
- Function Calling；
- Runtime；
- Loop；
- Verification。

---

### 4.4.7 Open WebUI Notes：既可以“在笔记旁边问”，也可以成为后续知识【扩展 / 第二讲复用】

当前内网 v0.11.0 已经实际走通两个很有价值的使用方式。

### 方式一：直接围绕 Note 对话

用户创建一份 Markdown Note 后，可以直接在笔记场景中和模型对话。

从用户体验看，它非常像：

> **“把这份笔记作为当前知识背景，直接围绕它问答和修改。”**

【截图占位 OW-14｜Note Editor + Note Chat】

【录屏占位 OW-R04｜创建 Note → 围绕 Note 问答】

这里培训中建议使用“Note-centered Chat / 围绕笔记问答”，不要直接等同于传统 Vector RAG。

因为：

> Note 的目标首先是持久内容和完整上下文协作，而不是一定经过 Embedding → Vector Retrieval。

---

### 方式二：已有 Note 进入 Workspace Knowledge

当前内网也已经实际走通：

```text
Create Note
↓
持续补充内容
↓
创建 Workspace / Model
↓
Knowledge 中选择已有 Note / Knowledge
↓
设置 System Prompt
↓
选择这个 Workspace
↓
后续持续问答
```

【截图占位 OW-15｜创建 Workspace 时选择已有 Note / Knowledge】

【录屏占位 OW-R05｜Note → Workspace Knowledge → 专用问答助手】

这和 Cherry 的：

```text
Knowledge
↓
Bind Assistant
↓
Assistant Prompt
↓
Chat
```

是很好的对照。

最终可以形成：

```text
Cherry
Local Knowledge
→ Assistant
→ System Prompt
→ Chat

Open WebUI
Server Note / Knowledge
→ Workspace Model
→ System Prompt
→ Chat
```

两者都在解决：

> **“不要每次打开新聊天再重新上传资料、重新粘贴角色提示词。”**

---

### 4.4.8 从个人知识到部门知识：两者的演进路径不同【扩展 / 第二讲复用】

Cherry 更自然的起点：

```text
个人文件
→ Local Knowledge
→ Personal Assistant
```

Open WebUI 更自然地可以继续向上走：

```text
个人 Note / Knowledge
→ Personal Workspace
→ Shared Knowledge
→ Group / ACL
→ Department Workspace
```

【图示占位 WB-COMP-05｜个人知识 → 团队知识的两条路径】

这也是为什么部门知识库建设中：

> Open WebUI 很适合作为近期直接可用的“知识消费和共享入口”。

但长期的 Source of Truth 仍然不应该锁死在 Open WebUI 里面。

第二讲会继续解释：

> Git / DMS / Wiki / DB / API 才是长期知识源，Open WebUI 和 Cherry 都是消费入口。

---

### 4.4.9 第一讲和第二讲如何分工【主讲】

第一讲只让学员看到：

```text
Document / Note
↓
Full Context or Retrieval
↓
Assistant / Workspace
↓
Context
↓
Model
```

第二讲再回答：

- 为什么要 Parse；
- 为什么要 Chunk；
- 没有 Embedding 会少什么；
- BM25 / Vector / Hybrid 的区别；
- Focused Retrieval 怎样验收；
- Full Context 什么时候更好；
- Personal Note 怎样升级成部门 Source of Truth；
- Knowledge、Workspace 和部门长期知识架构怎样分层。

所以 Cherry / Open WebUI 会在两场复用：

> **第一讲看“AI 工作台如何组织模型、Prompt、知识和工具”；第二讲看“知识为什么应该这样设计和治理”。**

---

# 第五幕：模型调用不是免费的——Thinking、速度、长 Context 与共享服务【主讲】

> **叙事转折：** 到这里我们已经知道输入会被 Tokenize、Context 要 Prefill、输出要逐 Token Decode。现在再看 Thinking、TTFT、Tokens/s、KV Cache 和共享服务指标，就不再是孤立参数。

### 5.2.1 Thinking：为什么有些问题值得“多想一会儿”？【主讲】

接下来用一个简单任务和一个复杂任务对比。

简单任务：

> 从这段 JSON 里提取 model 字段。

复杂任务：

> 分析一个多文件项目为什么 CI 通过但部署后业务数据不正确。

这两类任务显然不应该采用完全一样的推理预算。

Thinking / Reasoning 可以先这样理解：

> **让模型在给出最终答案前投入更多推理计算。**

结合部门内网模型实际测试展示 Thinking On / Off。

【截图占位 API-03｜Thinking OFF / ON 实测对比】

【录屏占位 API-R06｜相同任务 Thinking OFF/ON 的响应过程和耗时体感】

重点不是告诉大家：

> Thinking 一定更好。

而是建立“任务路由”意识：

- 信息抽取、格式转换、简单脚本：通常不需要最高推理；
- 疑难 Bug、架构、复杂分析、多文件理解：更值得使用更强推理。

结论：

> **模型能力、速度和资源消耗之间需要权衡。**

---

## 5.2 为什么同一个模型“快不快”不能只凭感觉——TTFT、Tokens/s 和总时延怎样影响应用【主讲】

很多人评价模型时会说：

> “我感觉这个模型挺快。”

但“快”至少包含两个完全不同的体验：

```text
多久开始回答？
→ TTFT

开始回答以后吐得多快？
→ Decode Tokens/s
```

最终用户真正等待的是：

> **Total Latency / 整个任务完成时间。**

可以先给一个足够实用的近似关系：

```text
Total Latency
≈ TTFT
+ Output Tokens / Decode Tokens/s
+ Tool / Network / Queue 等额外时间
```

【图示占位 API-SPEED-00｜TTFT + Decode → Total Latency】

这里要强调：

> 这只是建立工程直觉的近似式，不是所有推理服务内部时延组成的精确公式。

---

### 5.2.1 先用现有 Token 输出速率 Demo 建立“人的体感”

仓库里已经有一个离线可运行的 Token 输出速率体感 Demo，现在统一归入第一讲 API 应用体验套件：

```text
demos/api-applications/token-output-speed/index.html
```

原路径：

```text
demos/token-output-speed/index.html
```

保留兼容跳转。

这个页面不调用真实模型，也不是 Benchmark。

它只做一件事：

> **让大家直观看见，同一段内容在不同 Decode Tokens/s 下是什么感觉。**

【截图占位 API-SPEED-01｜Token 输出速率体感 Demo：单速率】

现场建议：

```text
5 tok/s
→ 20 tok/s
→ 50 tok/s
→ 100 tok/s
```

然后切 Race Mode：

```text
5 / 30 / 120 tok/s
```

【录屏占位 API-SPEED-R01｜5 → 20 → 50 → 100 tok/s + Race Mode】

不要把这些数字讲成：

> “某个模型必须达到 50 tok/s 才合格。”

它们只是帮助学员建立速度体感。

---

### 5.2.2 输出速率为什么对不同应用影响完全不同？

前面刚刚跑过四个 Python 小应用：

```text
Translation
→ JSON Extraction
→ Vision OCR
→ Visual QA
```

这正好可以用来说明：

> **模型性能指标必须结合应用形态看。**

| 应用 | 典型输出长度 | 更敏感的指标 | 为什么 |
|---|---:|---|---|
| 分类 / 路由 | 很短 | TTFT、稳定性 | 可能只输出一个标签，Decode 再快也省不了多少时间 |
| JSON 抽取 | 短 | TTFT、结构正确率 | 业务更关心尽快拿到可解析结果 |
| Vision OCR / 标签识别 | 很短 | Vision 前处理、TTFT、正确率 | 只输出几个字符，Tokens/s 通常不是主瓶颈 |
| 短文本翻译 | 短～中 | TTFT + Tokens/s | 第一屏等待和持续输出都会影响交互感受 |
| Visual QA 报告 | 中～长 | TTFT + Tokens/s | 问题列表和建议较长，Decode 会明显影响完成时间 |
| 长文 / 代码生成 | 长 | Tokens/s 很重要 | 输出 Token 越多，Decode 时间占比越高 |
| Agent | 多次短/中输出 | 每步 TTFT + Tool 延迟 + 累计时延 | 一个任务会串联多次模型和工具调用，单步延迟会不断累积 |

【图示占位 API-SPEED-02｜不同应用对 TTFT / Tokens/s / Tool Latency 的敏感度】

所以更准确的判断不是：

> “Tokens/s 越高，这个模型所有应用都一定越快。”

而是：

> **短输出应用通常先看 TTFT；输出越长，Decode Tokens/s 越重要；Agent 还要看多步调用和工具执行的累计时延。**

这个判断对模型选型非常重要。

例如一个只需要返回：

```json
{"category":"REVIEW"}
```

的业务接口，即使模型能从 40 tok/s 提升到 100 tok/s，用户可能也几乎感觉不到。

因为真正花时间的可能是：

- 排队；
- Prefill；
- Vision Encoder；
- TTFT；
- 网络。

但如果要生成：

- 2000 Token 报告；
- 大段代码；
- 长篇分析；

Decode Tokens/s 的差异就会直接进入总等待时间。

---

### 5.2.3 Agent 为什么更容易把“小延迟”放大？

普通 Chat：

```text
User
→ Model
→ Answer
```

Agent 更像：

```text
Model
→ Search
→ Model
→ Read
→ Model
→ Edit
→ Test
→ Model
→ Verify
```

如果每一步模型调用都多等待一点：

> **几十次循环以后，这些延迟会累计。**

而且 Agent 总时延还包括：

- Shell；
- Browser；
- Git；
- Search；
- API；
- Build；
- Test。

因此 Agent 体验不能只盯着单次 Tokens/s。

应该同时看：

```text
Per-step TTFT
+ Decode Tokens/s
+ Tool Latency
+ Number of Steps
+ Queue / Concurrency
```

【图示占位 API-SPEED-03｜Chat 单次时延 vs Agent 多步累计时延】

这也解释了为什么：

> **有些 Agent 任务不一定需要每一步都使用最强、最慢的旗舰模型。**

模型路由、Thinking 预算和工具效率都会影响整个任务速度。

---

### 5.2.4 再回到真实共享服务：速度不能只看一个人的输出

模型服务是共享计算资源。

真正影响体验的还包括：

- Prefill；
- Decode；
- TTFT；
- 单请求 Decode Tokens/s；
- Aggregate Output TPS；
- KV Cache；
- running requests；
- waiting requests；
- 并发。

把指标翻译成人话：

```text
TTFT
≈ 我按下发送以后，多久看到第一个 Token

Decode Tokens/s
≈ 这一条请求开始输出后，每秒产生多少 Token

running
≈ 现在有多少请求正在算

waiting
≈ 有多少请求正在排队

KV Cache
≈ 长上下文和并发正在占用多少推理缓存资源

Aggregate Output TPS
≈ 整个共享服务所有并发请求合起来每秒生成多少 Token
```

这里一定要明确：

> **单请求 Decode Tokens/s ≠ 服务端 Aggregate Output TPS。**

前者回答：

> “我这一条请求输出得快不快？”

后者回答：

> “整个模型服务当前吞吐有多大？”

【截图占位 API-08｜原始 /metrics 指标】

【截图占位 MM-01｜model-metric 总览】

【截图占位 MM-02｜API Benchmark】

【录屏占位 MM-R01｜发送请求时 model-metric 指标变化】

【录屏占位 MM-R02｜提高并发后 running/waiting/TPS 的变化】

这一段最后收束：

> **大模型不是传统 SaaS。每一次输入、Prefill、长 Context、Thinking、Decode 和并发都对应真实计算资源；性能指标必须放到具体应用和共享服务环境里理解。**

---

## 5.3 从“单请求速度”继续追问：共享服务到底好不好用？【主讲】

到这里我们已经回答：

> 单个请求能不能正确调用？

但部门实际使用模型，还需要回答另一类问题：

- 现在有多少请求正在算？
- 有没有人在排队？
- 两个实例是不是都在工作？
- KV Cache 使用率怎样？
- 当前 Prompt / Generation TPS 怎样？
- TTFT 是否变长？
- 高并发时服务发生了什么？

这些问题不是一条 Chat Response 能回答的。

所以测试脚本还会读取原始：

`GET /metrics`

当前 r4 在测试前后都验证了 `/metrics`，关键指标读取通过。

【截图占位 API-08｜原始 vLLM /metrics：running / waiting / KV / token counters】

这里要明确区分两个视角：

```text
Request / Response
= 这一条调用发生了什么

/metrics
= 整个模型服务正在发生什么
```

---

## 5.4 为什么我们又做了 model-metric？【主讲】

原始 Prometheus Metrics 对开发和运维有价值，但直接给大部分用户看，会遇到：

- 指标很多；
- Counter / Gauge / Histogram 不直观；
- 多实例聚合容易理解错；
- 单请求速度和服务聚合吞吐容易混淆；
- 不容易连续观察。

所以我们又做了自己的：

`mrgolftech/model-metric`

这不是为了再做一个“漂亮仪表盘”。

它解决的是：

> **把模型 API 从“单请求测试”提升到“共享服务持续观测”。**

当前项目已经覆盖：

- running / waiting；
- Prompt / Generation TPS；
- 每实例状态；
- 实例覆盖率；
- KV Cache max / avg；
- TTFT；
- E2E；
- Queue；
- Prefill；
- Decode；
- TPOT / ITL；
- WebSocket 实时更新；
- API Benchmark；
- Context Window 验证；
- Endpoint Compatibility。

【截图占位 MM-01｜model-metric 总览】

【截图占位 MM-02｜API Benchmark】

【截图占位 MM-03｜Context Window / Endpoint Compatibility】

这里必须讲清一个常见误解：

> **单请求输出 tokens/s ≠ 整个模型服务的 aggregate output TPS。**

一个是：

> 某一个用户这次请求输出得多快。

一个是：

> 整个服务所有实例、所有请求合起来正在处理多少 Token。

---

## 5.5 一条请求怎样在 model-metric 上“留下痕迹”【扩展 / 演示】

【录屏占位 MM-R01｜Postman POST → model-metric 实时指标变化】

建议录法：

1. 左边打开 Postman；
2. 右边打开 model-metric；
3. 先让页面稳定；
4. 发出一个输出稍长的 POST；
5. 观察 running；
6. 观察 TPS / KV / latency；
7. 请求结束；
8. running 回落。

第二段可以使用 Benchmark：

【录屏占位 MM-R02｜提高并发 → waiting / TPS / KV 变化】

这时第一讲就形成了一条非常完整的证据链：

```text
手工 GET
↓
手工 POST
↓
Cherry Studio Network
↓
Python 自动验收
↓
正式测试 Baseline
↓
原始 /metrics
↓
model-metric
```

它分别回答：

```text
协议长什么样？
↓
应用怎样调用？
↓
功能到底支不支持？
↓
结果能否重复验证？
↓
共享服务运行时发生了什么？
```

这应该成为第一讲的核心工程案例，而不是旁支。

---

---

## 5.6 Vision：图片并不是“神奇地进入模型”【扩展】

为了避免多模态继续被当成黑盒，现场给 Cherry 上传一张固定测试图片。

然后打开 Request。

【截图占位 API-NET-05｜Cherry 图片输入界面】

【截图占位 API-NET-06｜Vision Request Payload】

【录屏占位 API-R03｜上传图片 → 发送 → 查看实际 Payload】

不需要展开图像编码细节。

只让大家看到：

> 图片同样需要通过应用和协议进入模型请求。

因此“支持图片”至少涉及两层：

1. 模型本身是否具备 Vision 能力；
2. 当前应用/协议是否正确把图片送进去。

同样一个多模态模型，如果 Harness 没有实现图片输入，用户仍然“用不到”这个能力。

这已经开始触碰：

> **模型能力 ≠ 产品最终能力。**

---

## 5.7 SSE：为什么 Chat 能一个字一个字地出现？【主讲简述】

再观察流式请求。

非流式请求：

> 等模型完整生成，再一次返回。

流式请求：

> 生成一点，返回一点。

【截图占位 API-NET-07｜SSE / EventStream 原始事件】

【录屏占位 API-R04｜Network SSE 与聊天窗口逐步显示同步】

这里解释 SSE 即可，不必讲复杂 WebSocket 对比。

重点是：

> 很多“AI 产品体验”其实来自应用协议和前端实现，而不是模型参数本身。

到这里学员已经能看到：

- Chat UI；
- Request；
- Context；
- Vision；
- Streaming；

是怎样一层层组成最终体验的。

---

# 第六幕：从回答走向行动——Tool Calling 与 Harness【主讲】

> **叙事转折：** 前五幕都还主要是在解释“模型怎样接收信息并输出结果”。下一步是质变：模型能不能不只回答，而是提出一个需要真实世界执行的动作？

## 6.1 Tool Calling：模型第一次从“回答”走向“请求行动”【主讲】

现在进入本讲最关键的转折。

问一个模型本身不知道、但工具能够查询的问题。

例如：

> 当前服务有哪些实例正在运行？

如果只是普通 Chat，模型有三种可能：

- 不知道；
- 根据已有信息猜；
- 告诉用户应该去哪里查。

但如果给模型一个工具：

`get_service_instances()`

模型可以输出结构化 Tool Call。

【截图占位 API-04｜模型产生 Tool Call】

此时必须强调：

> **模型没有真的执行函数。**

完整过程是：

```text
Harness 告诉模型：
“你可以使用这些工具”
        ↓
模型生成：
“我要调用 get_service_instances，参数是……”
        ↓
Harness 真正执行工具
        ↓
得到 Tool Result
        ↓
Harness 把结果重新送给模型
        ↓
模型继续回答
```

【截图占位 API-05｜Tool Result 返回模型后的后续回答】

【录屏占位 API-R07｜完整 Tool Loop】

这就是从 Chat 向 Agent 过渡的关键机制之一。

结论：

> **模型负责决定“要不要调用、调用什么”，真正执行动作的是工具和 Harness。**

---

## 6.2 到底什么是 Harness？【主讲】

这时再引入 Harness，而不是一上来就给抽象定义。

前面已经看到应用在做：

- 组织 messages；
- 管理 Context；
- 调用模型 API；
- 提供 Tool Schema；
- 执行 Tool；
- 把 Tool Result 重新送回模型；
- 管理会话。

这些工作合起来，可以先把 Harness 理解为：

> **把模型组织成一个可工作的 AI 应用的那层“编排系统”。**

此处只给最简结构：

```text
            User
              ↓
        Chat / Agent UI
              ↓
           Harness
      ┌───────┼────────┐
      ↓       ↓        ↓
   Context   Tools   Workspace
      │       │        │
      └───────┼────────┘
              ↓
          Model API
              ↓
             LLM
```

【图示占位 CHAT-03｜Prompt→Answer vs Goal→Deliver】

Harness 的详细结构留到第三讲。

本讲只要求大家记住：

> **同一个模型放进不同 Harness，最终表现可以明显不同。**

---

# 第七幕：为什么复杂任务最终走向 Agent【主讲】

> **叙事转折：** 一旦 Harness 能管理 Context、提供 Tool、执行动作并把结果反馈给模型，复杂任务就不再是一次 Prompt → Answer，而开始形成 Read → Act → Observe → Verify → Iterate。

## 7.1 Chat 与 Agent：不是“旧时代”和“新时代”【主讲】

这里要避免一个错误叙事：

> Chat 已经过时，Agent 才高级。

更准确的说法是：

## Chat 很适合

- 一个独立问题；
- 文案改写；
- 解释概念；
- 总结材料；
- 一次性分析；
- 小段代码。

## 复杂任务开始需要 Agent

当任务包含：

- 多文件；
- 持续修改；
- Shell；
- Git；
- Browser；
- Server；
- Build；
- Test；
- 多轮验证；

工作方式从：

`Prompt → Answer`

变成：

`Goal → Plan → Read → Act → Observe → Verify → Iterate → Deliver`

【截图占位 CHAT-01｜Chat 对代码问题给出答案/步骤】

【截图占位 CHAT-02｜Agent 正在读取文件、运行命令和验证】

---

## 7.2 一个最小 Agent 闭环：不要先看复杂产品【主讲】

现场选择一个极小工程任务。

例如训练项目 Sensor Guard 中有一条故意失败的边界测试。

任务：

> 修复 85°C 边界判断错误，并保证其他测试不受影响。

让 Agent：

```text
Read project rules
→ Run test
→ See failure
→ Search code
→ Edit
→ Run test
→ Test pass
→ git diff
```

【录屏占位 CHAT-R01 / ZCODE-R02｜最小 Read/Edit/Test/Diff 闭环】

【截图占位 ZCODE-06～12｜Rules → Test Fail → Search/Edit → Pass → Diff】

这个案例非常重要，因为它让学员看到：

> Agent 的“智能”不是一口气生成一个完美答案，而是在不断读取外部反馈之后继续判断。

因此 Agent 的实际能力来自一个组合：

```text
Model
+ Harness
+ Workspace
+ Context
+ Tools
+ Runtime
+ Verification
```

---

## 7.3 同一个模型，换 Chat 和 Agent，会发生什么？【扩展 / 演示】

如果条件允许，再使用同模型、同 Prompt 做一次受控对比。

可以继续使用“鹈鹕骑自行车”案例：

第一轮在 Chat 中：

> 让模型给出网页实现代码。

用户需要人工：

- 创建文件；
- 复制代码；
- 打开网页；
- 截图；
- 把问题反馈给模型。

第二轮在 Agent：

- 创建 Workspace；
- 写文件；
- 启动服务；
- 打开 Browser；
- 看截图；
- 修改；
- 再验证。

【截图占位 API-10｜同模型 Chat 结果】

【截图占位 API-11｜同模型 Agent 最终结果】

【录屏占位 API-R08 / CHAT-R02～03｜同模型 Chat 人工接力 vs Agent 闭环】

这组对比的意义不是证明：

> Agent 一定更聪明。

而是证明：

> **Harness 改变了模型能够获得的信息、能够采取的动作以及能够得到的反馈。**

---

## 7.4 第一讲最后把所有东西重新拼起来【主讲】

现在再看最初的聊天框，就不再神秘。

```text
用户目标
   ↓
Chat / Agent Surface
   ↓
Harness / Application
   ├─ Context
   ├─ Session
   ├─ Tools
   ├─ Workspace
   └─ Runtime
   ↓
Model API
   ↓
LLM
   ↓
Tool Call / Text / Reasoning
   ↓
Harness 执行和反馈
```

第一讲最后只需要留下五个认识：

1. **模型不是聊天软件，Chat 是模型的一种应用形态。**
2. **API 是应用与模型服务交互的基本接口。**
3. **Context 是本轮模型真正能够看到的信息，长 Context 有真实资源成本。**
4. **Tool Calling 是模型请求行动，Harness 和工具才真正执行。**
5. **Agent 并不是神秘新物种，而是模型获得 Workspace、Tools、Runtime 和反馈闭环后的工作系统。**

下一讲自然提出一个问题：

> 如果模型真正能用的是 Context，那么部门成千上万份文档、代码、测试数据和实时系统，应该怎样把“这一次真正需要的知识”可靠地交给模型？

这就是部门知识库的问题。

---

# 8. 第一讲素材准备【备用】

本讲所有截图、录屏、现场 Demo 和备用素材统一维护在：

`docs/lectures/01-api-to-agent-media-checklist.md`

正文中的 `【截图占位 ...】` / `【录屏占位 ...】` 继续保留，用于标明素材应该插入哪个知识点。

准备素材时以独立清单为执行入口；制作 PPT 时再按照正文占位把素材归位。
