# 第一讲：从模型 API 到 Agent——看懂 AI 应用背后的工作逻辑

> 状态：Final Lecture Draft v1.1  
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

# 1. 第一步：把聊天框拆开——原来背后就是一次模型调用

先打开 Cherry Studio 的开发者工具，在 Network 中观察模型列表。

我们会看到类似：

`GET /v1/models`

这一步解决第一个问题：

> Cherry Studio 自己并不知道服务器上有哪些模型，它需要向模型服务询问。

接着发送第一条普通消息。

在 Network 中找到实际请求，可以看到：

- Request URL；
- Method；
- Header；
- Authorization；
- Request Body；
- model；
- messages；
- stream。

【截图占位 API-NET-02｜GET /v1/models Request / Response】

【截图占位 API-NET-03｜第一轮 Chat Request Body】

这里不需要把 HTTP 协议完整讲一遍。

只需要建立几个最基本的工程概念：

```text
URL
= 要访问哪个服务

GET / POST
= 这次要读取信息，还是提交信息

Header
= 请求附带的控制信息和身份信息

JSON
= 应用和服务之间交换的结构化数据

Request
= 应用发出去的内容

Response
= 服务返回来的内容
```

这时再回头看 Chat，就可以得到一个很重要的结论：

> **聊天软件并不是模型。聊天软件首先是一个模型 API 的客户端。**

为了进一步把这个关系讲直观，可以现场用 Postman 或 curl 发出同样的请求。

【截图占位 API-POST-01｜Postman GET /v1/models】

【截图占位 API-POST-02｜Postman POST /v1/chat/completions】

【录屏占位 API-R09｜Postman GET/POST 与 Cherry Network 对照】

这组演示最终不要让学员记住一长串 JSON 字段，只留下一个认识：

```text
用户
↓
应用
↓
API Request
↓
模型服务
↓
API Response
↓
应用
```

## 1.1 先不要依赖任何 Chat 软件：直接发一个 GET

为了让“API”彻底从聊天界面里剥离出来，建议现场再做一次最简单的手工请求。

目标：

> **不打开 Cherry Studio，只使用 Postman 或 curl，直接询问模型服务“你有哪些模型”。**

请求：

```http
GET <BASE_URL>/v1/models
Authorization: Bearer <API_KEY>
```

或者使用 curl：

```bash
curl -H "Authorization: Bearer <API_KEY>" \
  <BASE_URL>/v1/models
```

现场重点不是教 curl 参数，而是让大家看到四个东西：

1. Method 是 `GET`；
2. URL 是 `/v1/models`；
3. 服务返回 HTTP Status；
4. Response Body 是 JSON。

当前内网正式测试基线中，这个接口已经自动验证：

- HTTP 200；
- 找到模型 `qwen3.6`；
- `max_model_len=131072`。

【截图占位 API-POST-01｜Postman / curl 直接 GET /v1/models】

【录屏占位 API-R09A｜不经过 Chat UI，直接 GET /v1/models】

这一段讲完以后再问：

> **如果 GET 是“向服务取信息”，那真正让模型回答问题时，为什么需要 POST？**

---

## 1.2 再手工发一个 POST：模型调用就是把输入放进 Request Body

直接调用：

```http
POST <BASE_URL>/v1/chat/completions
Content-Type: application/json
Authorization: Bearer <API_KEY>
```

最小 Body 可以展示成：

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

现场观察：

- Request Body；
- HTTP 200；
- `object=chat.completion`；
- `choices`；
- `usage`。

【截图占位 API-POST-02｜Postman POST /v1/chat/completions：Body + Response】

【录屏占位 API-R09B｜直接 POST Chat → 得到 JSON Response】

这一步的教学意义非常大：

> **模型不是只能通过 Chat 软件使用。任何能够按协议构造 HTTP Request 的程序，都可以调用模型。**

Python、Java、JavaScript、Cherry Studio、Open WebUI、Agent，本质上都可以站在这个位置。

因此可以画：

```text
Postman
Python
Cherry Studio
Open WebUI
Agent
业务应用
    │
    └────→ 同一个 Model API
```

【图示占位 API-POST-03｜不同客户端 → 同一个模型 API】

---

## 1.3 为什么“我手工调通一次”还不够？

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

## 1.4 当前内网 Qwen 到底测出了什么？

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

## 1.5 建议现场真正运行一次自动测试，但不要把 29 项全等完

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

## 1.6 从测试脚本得到一个很重要的方法论

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

## 1.7 从“接口能不能用”继续追问：共享服务到底好不好用？

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

## 1.8 为什么我们又做了 model-metric？

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

## 1.9 第一讲最值得做的一段录屏：一条请求怎样在 model-metric 上“留下痕迹”

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

现场建议真正实时做的只有三项：

1. Cherry 普通 Chat + Network；
2. 多轮 Context；
3. 最小 Agent Read/Edit/Test Loop。

Thinking、Vision、并发、Tool Loop 如果现场稳定，可以实时演示；否则使用预录。

原则：

> **任何依赖网络、模型排队、浏览器状态的 Demo 都必须准备预录和静态截图。**

第一讲结束以后，学员应该已经能够把一个新的 AI 产品先问成一句话：

> “它背后调用什么模型？怎样管理 Context？有哪些 Tool？谁负责执行？”

做到这一点，第一讲就完成了。
