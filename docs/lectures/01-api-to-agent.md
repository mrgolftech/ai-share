# 第一讲：从模型 API 到 Agent——看懂 AI 应用背后的工作逻辑

> 状态：Final Lecture Draft v1.4  
> 日期：2026-09-30  
> 建议时长：100～120 分钟  
> 内容映射：原内容单元 1 + 3  
> 适用对象：部门技术人员及相关技术管理人员  
> 主线：**从一个真实 Chat Request 出发，一层层拆开 Model、API、Context、Tool、Harness，最终解释 Agent 为什么能够“干活”。**

---

# 0. 本讲不是“API 编程课”

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

# 1. 第一步：先从 Cherry Studio 配置模型——为什么同一个服务会出现三种 API？

第一讲不先把三套 API 格式摆在 PPT 上让大家背。

更自然的做法是：

> **先配置一个大家正在使用的 Chat 客户端，在真实界面里看到“为什么这里会有不同接口类型”，再打开 Network 看它到底发了什么。**

这样 API 不是抽象名词，而是从实际使用中长出来的。

---

## 1.1 配置内网模型：先认识 Provider、Base URL、API Key、Model

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

## 1.2 配置时为什么会看到 OpenAI Chat、OpenAI Responses、Anthropic Messages？

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

## 1.3 先不要讲 JSON：直接用 Cherry 同一个 Prompt 切三种协议

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

## 1.4 三种 POST Request 到底有什么不同？

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

## 1.4A 脱离 Cherry 再手工发一次 GET / POST：证明 UI 只是客户端

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


## 1.5 为什么“我手工调通一次”还不够？

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

## 1.6 当前内网 Qwen 到底测出了什么？

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

## 1.7 建议现场真正运行一次自动测试，但不要把 29 项全等完

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

## 1.8 从测试脚本得到一个很重要的方法论

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

## 1.9 从“接口能不能用”继续追问：共享服务到底好不好用？

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

## 1.10 为什么我们又做了 model-metric？

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

## 1.11 第一讲最值得做的一段录屏：一条请求怎样在 model-metric 上“留下痕迹”

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

# 2. 第二步：为什么第二轮对话“记得”第一轮？

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

# 3. Token 和 Context：为什么“多给资料”不是免费的

知道了 Context 是“模型当前桌面上的材料”，再讲 Token 就容易得多。

模型并不是按“Word 页数”或者“中文字符数”处理输入，而是把输入编码成 Token。

这里不需要花很长时间讲 tokenizer 算法。

只回答三个实际问题：

## 3.1 为什么 Token 值得关心？

因为 Token 直接关系到：

- 输入长度；
- 输出长度；
- Context 占用；
- Prefill 工作量；
- 推理时间；
- 服务吞吐；
- API 成本。

【截图占位 API-01｜/tokenize 或模型接口相关实测】

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

# 3.4 Cherry Studio：一个 Chat 工作台到底替我们做了哪些事？

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

## 3.4.1 助手指令：为什么不需要每轮都重新说“你是谁”

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

## 3.4.2 模型配置：同一个问题为什么可以临时切模型？

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

## 3.4.3 模型参数：UI 里的 Temperature、Top-P、Max Tokens 到底改了什么？

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

## 3.4.4 知识库：勾一下之后，模型真的“学会”这些资料了吗？

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

## 3.4.5 联网搜索：为什么这和知识库不是一回事？

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

## 3.4.6 MCP / 工具调用：勾选工具以后发生了什么？

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

## 3.4.7 一个 Cherry 对话到底可能包含哪些东西？

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

# 3.5 Open WebUI v0.11.0：另一个“Chat 工作台”，但更适合作为共享知识入口

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

## 3.5.1 个人笔记：知识不一定来自“上传 PDF”

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

## 3.5.2 同一个 Markdown 文档为什么可以选“完整文档”和“聚焦检索”？

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

## 3.5.3 没有配置 Embedding，为什么仍然能用知识回答？

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

## 3.5.4 Workspace：为什么它比“临时上传一个附件”更进一步？

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

## 3.5.5 Cherry Studio 与 Open WebUI：功能越来越像，但“数据边界”和“组织方式”不同

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

## 3.5.6 Open WebUI Workspace Model 和 Cherry Assistant：其实在解决同一个问题

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

## 3.5.7 Open WebUI Notes：既可以“在笔记旁边问”，也可以成为后续知识

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

## 3.5.8 从个人知识到部门知识：两者的演进路径不同

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

## 3.5.9 第一讲和第二讲如何分工

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

# 4. Thinking：为什么有些问题值得“多想一会儿”

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

# 5. 为什么同一个模型“快不快”不能只凭感觉

很多人评价模型时会说：

> “我感觉这个模型挺快。”

但模型服务是共享计算资源。

真正影响体验的至少包括：

- Prefill；
- Decode；
- TTFT；
- TPS；
- KV Cache；
- running requests；
- waiting requests；
- 并发。

不需要讲复杂推理框架内部实现，只需要把这些指标翻译成人话。

```text
TTFT
≈ 我按下发送以后，多久看到第一个字

TPS
≈ 开始输出以后，每秒吐多少 Token

running
≈ 现在有多少请求正在算

waiting
≈ 有多少请求正在排队

KV Cache
≈ 长上下文和并发正在占用多少推理缓存资源
```

【截图占位 API-08｜原始 /metrics 指标】

【截图占位 MM-01｜model-metric 总览】

【截图占位 MM-02｜API Benchmark】

【录屏占位 MM-R01｜发送请求时 model-metric 指标变化】

【录屏占位 MM-R02｜提高并发后 running/waiting/TPS 的变化】

这里要把第一讲的一个核心观点讲出来：

> **大模型不是传统 SaaS。每一次输入、长 Context、Thinking 和并发都对应真实计算资源。**

---

# 6. Vision：图片并不是“神奇地进入模型”

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

# 7. SSE：为什么 Chat 能一个字一个字地出现？

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

# 8. Tool Calling：模型第一次从“回答”走向“请求行动”

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

# 9. 到底什么是 Harness？

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

# 10. Chat 与 Agent：不是“旧时代”和“新时代”

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

# 11. 一个最小 Agent 闭环：不要先看复杂产品

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

# 12. 同一个模型，换 Chat 和 Agent，会发生什么？

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

# 13. 第一讲最后把所有东西重新拼起来

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

# 14. 第一讲截图执行清单

## 14.1 P0 必拍截图

### API-NET-01：Cherry 对话界面

拍摄内容：

- 当前选择的内网模型；
- 输入框；
- 一条普通文本问题；
- 不显示任何 API Key 或敏感地址。

用途：

> 作为“从大家熟悉的 Chat 开始”的第一张真实界面。

### API-NET-02：/v1/models

拍摄内容：

- Network Request；
- Method；
- Endpoint；
- Response 中模型 id。

画面要求：

> Request 和 Response 至少有一张能在投影上看清关键字段。

### API-NET-03：首轮 Chat Payload

重点框出：

- model；
- messages / input；
- stream。

不要截完整巨大 JSON。

### API-NET-04A～C：多轮 Context

固定两轮问题。

分别截：

1. 第一轮；
2. 第二轮；
3. Diff/标注图。

第三张是最重要的：

> 用箭头明确指出历史消息怎样重新进入下一轮请求。

### API-NET-05～06：Vision

一张界面，一张 Payload。

要求使用无敏感信息、内容明确的固定测试图片。

### API-NET-07：SSE

要求能看到多个连续 event/data chunk。


### API-POST-01～03：直接 GET / POST 与客户端关系

必须准备：

- Postman / curl `GET /v1/models`；
- Postman `POST /v1/chat/completions`；
- “Postman / Python / Cherry / Open WebUI / Agent → 同一个 Model API”图。

### API-PROTO-01～04：三种 API 协议

必须使用当前内网 qwen3.6 的真实请求准备：

1. OpenAI Chat：`messages / choices / tool_calls`；
2. OpenAI Responses：`input / output / function_call / events`；
3. Anthropic Messages：`content blocks / tool_use / tool_result`；
4. 三协议对比图。

### CH-API-01～02C：Cherry 三协议接入

拍当前实际安装版本：

- Provider / Model 的 Endpoint Type 或协议配置；
- `/v1/chat/completions`；
- `/v1/responses`；
- `/v1/messages`。

不要为了讲义强行模拟不存在的 UI；以当前 Cherry 真实配置方式为准。

### API-TEST-00～04：自动验收证据

准备：

- `qwen_api_training_test.py` 文件头与覆盖范围；
- r4 正式结果 28 PASS / 1 SKIP / 0 FAIL / 0 ERROR；
- 单条 record；
- 结果目录；
- 协议/能力矩阵。

### CH-ASSIST-01～06：助手与对话配置

拍：

- 新建 / 编辑助手；
- Instructions；
- 默认模型；
- Temperature / Top-P / Max Tokens / Stream / Context；
- 对话顶部模型切换；
- Knowledge / Web Search / Tool/MCP 等入口；
- “UI 开关 → Context / Parameter / Tool”映射图。

### CH-KB-01～04：Cherry 最小知识库流程

拍：

1. 新建知识库；
2. 添加文件 / 笔记 / 目录 / 链接中的实际可用入口；
3. Parse / Chunk 或资料处理结果；
4. Recall Test；
5. 对话勾选知识库。

第一讲只用于说明知识如何进入 Context；第二讲继续复用并展开 Retrieval 原理。

### CH-WEB-01：联网检索

拍：

- 输入区联网按钮；
- 当前搜索服务配置；
- 一次带 Search Result / Citation 的回答。

### WB-COMP-01～05：Cherry vs Open WebUI 对比

准备：

- WB-COMP-01：Cherry Desktop / Local Data → Model API；
- WB-COMP-02：Browser → Open WebUI Server / Data → Model API；
- WB-COMP-03：两者数据边界/使用场景对照表；
- WB-COMP-04：Cherry Assistant vs Open WebUI Workspace Model；
- WB-COMP-05：个人知识 → 团队知识演进图。

### OW-07～13：Open WebUI v0.11.0 个人知识 / Workspace

按当前内网已经走通的实际流程拍：

- OW-07：个人 Note / Markdown；
- OW-08：上传文档；
- OW-09：Full Context / Focused Retrieval 切换；
- OW-10：未配置 Embedding / 未向量化提示；
- OW-11：Workspace 绑定 Knowledge；
- OW-12：选择 Workspace 后依据知识问答；
- OW-13：Note/Document → Knowledge → Workspace → Chat 图。

### OW-14～15：Note 对话与 Workspace 复用

拍：

- OW-14：Note Editor + 围绕 Note 的 Chat；
- OW-15：创建 Workspace / Model 时附加已有 Note / Knowledge。

### CH-TOOL-01～02：MCP / Tool

拍：

- 助手 MCP / Tool 配置；
- 一次 Tool Call / Tool Result。

### API-TEST-03：结果资产目录

拍摄：

```text
api/qwen/results/20260930_095033/
```

要求能看到：

- 单项 JSON record；
- SSE 原始记录；
- manifest；
- summary。

### API-TEST-04：能力矩阵

根据正式 r4 报告制作一张 PPT 友好矩阵：

- Chat；
- Responses；
- Anthropic；
- Tool Loop；
- Vision；
- Thinking 差异；
- 28 PASS / 1 SKIP。

### API-03：Thinking

固定同一问题，截 OFF 和 ON。

如果协议中能看到 reasoning/thinking 参数，优先把参数也截进去。

### API-04～05：Tool Calling

必须形成成对证据：

1. Tool Call；
2. Tool Result + Final Answer。

### MM-01～02：model-metric

至少拍：

- 总览；
- Benchmark。

重点保证 TTFT/TPS/running/waiting/KV 等关键字段可读。

### CHAT-01 / CHAT-02

同一个任务：

- Chat 只给建议；
- Agent 已经开始操作 Workspace。

---

# 15. 第一讲录屏执行脚本

## API-R01：模型列表

时长建议：20～30 秒。

步骤：

1. 打开 Cherry；
2. 打开 DevTools Network；
3. 刷新 Provider / Model；
4. 点击对应 request；
5. 停在 Response。

目的：

> 证明“模型列表也是 API 获取的”。

## API-R02：多轮 Context

时长建议：40～60 秒。

固定脚本：

1. 新建会话；
2. 输入：“这个项目代号叫蓝鲸”；
3. 输入：“刚才的项目代号是什么？”；
4. 展开两次 Network Request；
5. 对照第二次请求历史。

不要在录屏中临时想问题。

## API-R03：Vision

步骤：

1. 上传固定图片；
2. 输入固定问题；
3. 发送；
4. 查看 Network Payload；
5. 回到回答。

## API-R04：SSE

步骤：

1. 发送一个输出稍长的问题；
2. Network 保持打开；
3. 让观众同时看到聊天窗口持续输出和 EventStream。

## API-R07：完整 Tool Loop

必须保留：

- 模型提出 Tool Call；
- Harness 执行；
- Tool Result；
- 模型继续生成。

不要只录最终答案。

## CH-R03：Cherry 三协议

固定同一个 Prompt：

> 请只回答：PROTOCOL_OK

依次切换：

- OpenAI Chat；
- OpenAI Responses；
- Anthropic Messages。

录到 Network Endpoint 与 Request Body 差异。

## CH-R04：Cherry 模型参数

修改：

- Max Tokens；
- Stream；
- Thinking / Reasoning（当前配置支持时）。

然后对比 Network Request。

## CH-R05：Cherry Knowledge

步骤：

1. 不勾知识库提问；
2. 勾选 Qwen API 训练知识库；
3. 再问当前内部实测问题；
4. 展示检索/引用差异。

## CH-R06：Cherry Web Search

固定一个时效性公开问题：

1. 普通问；
2. 开启联网；
3. 展示 Search Tool / Result / Citation。

## OW-R03：Open WebUI 个人知识到 Workspace

步骤：

1. 新建个人 Note / Knowledge；
2. 上传固定 Markdown / 文档；
3. 展示 Full Context / Focused Retrieval；
4. 展示当前未配置 Embedding / 未向量化提示；
5. 在 Workspace / Model 中引用 Knowledge；
6. 选择对应 Workspace；
7. 问固定问题；
8. 展示依据资料回答。

建议同一份资料至少保留一次 Full Context 演示，以明确说明全文注入不依赖 Embedding。

## OW-R04～05：Note 对话与复用

### OW-R04：围绕 Note 直接问答

1. 新建一条固定 Markdown Note；
2. 写入一段 Qwen 实测结论；
3. 打开 Note Chat；
4. 问一个答案明确存在于 Note 的问题；
5. 展示回答或对 Note 的修改。

### OW-R05：Note → Workspace Model

1. 使用已有 Note / Knowledge；
2. 创建 Workspace / Model；
3. 设置 System Prompt；
4. 附加已有知识；
5. 选择该 Workspace；
6. 新建 Chat；
7. 固定问题；
8. 观察系统提示词和知识共同影响回答。

## API-R10：自动测试脚本

建议使用预录 + 现场打开正式结果。

步骤：

1. 显示 `qwen_api_training_test.py`；
2. 运行测试；
3. 展示若干 PASS；
4. 打开结果目录；
5. 打开 `manifest.json` / 正式报告；
6. 展示一条 Tool Loop 或 Vision record。

不要在课堂现场等待全部 Thinking / 多图 Vision 测试跑完。

## MM-R01：请求与指标变化

步骤：

1. model-metric 总览保持可见；
2. 发出一个较长请求；
3. 显示 running/KV/TPS 等变化；
4. 请求完成后观察状态回落。

## API-R08：Chat vs Agent

最好剪成左右或前后两段：

Chat：

> 给一个需要文件修改和验证的小任务。

Agent：

> 同样目标，展示实际 Read/Edit/Test/Diff。

不要比较不同模型；尽量固定模型，突出 Harness 差异。

---

# 16. 第一讲现场 Demo 与备用策略

现场建议真正实时做四项：

1. Cherry 配置内网模型，并用同一 Prompt 切 OpenAI Chat / Responses / Anthropic 三种协议，看 Network Endpoint；
2. Open WebUI v0.11.0：个人 Note / 文档 → Knowledge → Workspace → 基于资料问答；
3. Cherry 多轮 Context；
4. 最小 Agent Read/Edit/Test Loop。

Postman、自动测试、model-metric、Thinking、Vision、Tool Loop 根据现场时长选择实时或预录；其中完整 r4 测试、并发压测和长 Thinking 优先使用预录。

原则：

> **任何依赖网络、模型排队、浏览器状态的 Demo 都必须准备预录和静态截图。**

第一讲结束以后，学员应该已经能够把一个新的 AI 产品先问成一句话：

> “它背后调用什么模型？怎样管理 Context？有哪些 Tool？谁负责执行？”

做到这一点，第一讲就完成了。
