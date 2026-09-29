# 培训讲义：从一个 HTTP 请求理解内网大模型服务

> 章节定位：内网大模型服务介绍及 API 实测  
> 核心模型：qwen3.6  
> 讲解目标：不是背接口，而是通过真实 API 理解 Token、Context、Thinking、Streaming、Tool Calling，以及 Chat 到 Agent 的技术基础。

---

# 一、本章要解决的问题

很多人第一次接触大模型，是从网页聊天框开始的。

输入一句话，模型返回一句话，看起来和普通网站没有本质区别。

但如果我们希望把大模型真正接入自己写的程序、Web 系统、自动化脚本、RAG、数据分析平台，甚至 Codex、Claude Code 一类 Agent，就必须把“网页里的模型”拆开看。

本章从我们内网真实部署的 Qwen3.6 服务出发，回答几个工程问题：

1. 我们内网实际部署的模型是什么？
2. 程序到底怎样调用模型？
3. GET、POST、JSON、Header、Status Code 分别是什么？
4. 为什么同一个回答既可以一次返回，也可以一个字一个字出现？
5. Token 是什么？128K Context 到底是什么意思？
6. Thinking 开关改变了什么？
7. 模型为什么能“调用工具”？
8. OpenAI、Codex、Claude 的 API 为什么不完全一样？
9. 一个接口“存在”，为什么还不代表真正兼容？

本章所有“当前内网支持情况”的判断，都来自 2026-09-29 的真实 API 测试。

---

# 二、先认识我们现在的内网模型

## 2.1 当前服务实际返回了什么

调用：

~~~http
GET /v1/models
~~~

服务返回：

~~~json
{
  "object": "list",
  "data": [
    {
      "id": "qwen3.6",
      "owned_by": "vllm",
      "root": "/models/Qwen3.6-35B-A3B-w8a8-ascend",
      "max_model_len": 131072
    }
  ]
}
~~~

从这里能读出四个重要信息：

| 信息 | 含义 |
|---|---|
| qwen3.6 | 调 API 时真正使用的模型 ID |
| Qwen3.6-35B-A3B-w8a8-ascend | 当前部署模型目录/版本标识 |
| owned_by: vllm | 当前 API 服务由 vLLM 提供 |
| max_model_len: 131072 | 当前服务实际对外配置约 128K Context |

现场部署情况是：**两个华为昇腾节点**。

第一个培训结论：

> **不要根据产品宣传或模型卡猜现网能力，要先问服务本身。**

官方模型可以支持更长上下文，但现网服务到底开放多少，应该看 /v1/models 和实际压测。

---

# 三、Qwen3.6-35B-A3B 是什么模型

## 3.1 35B 与 A3B

Qwen 官方模型卡显示，Qwen3.6-35B-A3B 的语言模型部分大约是：

~~~text
总参数：35B
激活参数：3B
~~~

这里最关键的不是数字大小，而是它采用 MoE —— Mixture of Experts，混合专家模型。

传统 Dense 模型可以粗略理解为：

~~~text
每来一个 Token
      ↓
大部分模型参数都参与计算
~~~

MoE 则更像：

~~~text
输入 Token
    ↓
  Router
    ↓
从大量 Expert 中选择部分专家
    ↓
完成当前 Token 的计算
~~~

Qwen3.6-35B-A3B 官方配置中有 256 个专家，每个 Token 激活 8 个 Routed Experts，并有 Shared Expert。

因此：

> **35B 表示模型总容量很大，但单个 Token 并不是把全部 35B 参数都完整计算一遍。**

这也是很多新模型采用 MoE 的重要原因：在模型容量和单 Token 推理成本之间做平衡。

但必须避免另一个误区：

> **A3B 不等于“资源消耗就和普通 3B 模型一样”。**

模型权重仍然需要存储；专家需要部署；长 Context 需要 KV Cache；多节点之间可能还有通信；并发时还有调度与排队。

所以模型结构只是第一层，最后仍要回到真实服务的性能测试。

---

# 四、官方模型能力和现网能力要分开

官方 Qwen3.6-35B-A3B 模型卡给出的原生 Context Length 是：

~~~text
262,144 tokens
~~~

而我们的内网服务实际返回：

~~~text
131,072 tokens
~~~

所以培训里不能说：

> “我们现在支持 262K。”

更准确的说法是：

> **Qwen3.6-35B-A3B 官方模型原生 262K；当前部门内网服务配置为 131072，也就是约 128K。**

同样，官方模型本体带 Vision Encoder，但本轮没有测试图片输入，因此不能直接说：

> “我们内网模型已经验证支持多模态。”

正确表达是：

> **模型本体具备视觉架构，但当前内网多模态 API 尚未纳入本轮验收。**

这套区分以后都应该保留：

~~~text
官方能力
  ≠
当前部署配置
  ≠
我们的实测结果
~~~

---

# 五、程序到底是怎么调用大模型的

网页聊天容易让人产生一个错觉：浏览器是不是直接在和“大模型”说话？

实际上，中间至少还有 API 服务。

~~~text
Postman / Python / WebUI / Agent / 业务系统
                    │
                    │ HTTP
                    ▼
              vLLM API Server
                    │
          ┌─────────┴─────────┐
          │                   │
    Chat Template          Tokenizer
          │                   │
          └─────────┬─────────┘
                    ▼
          Qwen3.6-35B-A3B
                    │
                    ▼
              华为昇腾节点

旁路接口：
/metrics       → 运行状态与性能指标
/openapi.json  → API 结构定义
/version       → 服务版本
~~~

因此：

- Qwen3.6 是模型；
- vLLM 是推理与 API 服务框架；
- HTTP API 是客户端访问模型的接口；
- OpenAI Chat、Responses、Anthropic Messages 是不同的协议格式；
- Postman、Python、WebUI、Agent 都是客户端。

理解这一点以后，后面讲 WebUI、Cherry Studio、Agent、MCP 会容易很多。

---

# 六、先用最简单的 GET 理解 API

## 6.1 GET /v1/models

在 Postman 里访问：

~~~http
GET /v1/models
~~~

GET 可以先简单理解为：

> **我要读取一个已有资源。**

我们不是让模型生成内容，只是在问服务：

> “你现在有哪些模型？”

返回的是 JSON。

JSON 可以理解为：

> **程序之间交换结构化数据的一种通用文本格式。**

例如：

~~~json
{
  "id": "qwen3.6",
  "max_model_len": 131072
}
~~~

程序可以直接读取字段，而不需要再从一段自然语言里提取模型名称和上下文长度。

---

# 七、再用 POST 理解真正的模型调用

真正让模型完成任务，使用：

~~~http
POST /v1/chat/completions
~~~

POST 可以先理解为：

> **我要把一份数据提交给服务器，让它处理。**

请求 Body：

~~~json
{
  "model": "qwen3.6",
  "messages": [
    {
      "role": "user",
      "content": "请只回答：CHAT_OK"
    }
  ],
  "temperature": 0,
  "max_tokens": 128,
  "stream": false,
  "chat_template_kwargs": {
    "enable_thinking": false
  }
}
~~~

这里已经包含了大模型 API 最核心的几个概念。

### model

告诉服务调用哪个模型。

### messages

这是对话 Context。多轮对话本质上就是不断把历史消息也放进上下文。

### temperature

控制生成随机性。接口测试通常希望输出稳定，因此本次设为 0 或较低值。

### max_tokens

限制本次最大输出长度。

注意：

> **max_tokens 不是 Context Window。**

Context Window 是输入和输出共同使用的总上下文范围；max_tokens 只限制这次最大生成量。

---

# 八、Header 和 API Key 是干什么的

典型 Header：

~~~http
Content-Type: application/json
Authorization: Bearer <API_KEY>
~~~

Content-Type 告诉服务器：

> “我发过来的 Body 是 JSON。”

Authorization 用来证明：

> “这个请求是谁发的，有没有调用权限。”

所以 API Key 和密码一样：

- 不要写进公开代码；
- 不要上传 GitHub；
- 不要放在培训截图中；
- 不要长期硬编码在脚本里。

推荐使用环境变量。

---

# 九、Response 和 HTTP Status Code

服务器处理完成后返回：

~~~text
HTTP Status
Headers
Body
~~~

这次 Chat 返回：

~~~json
{
  "object": "chat.completion",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "CHAT_OK"
      },
      "finish_reason": "stop"
    }
  ]
}
~~~

常见状态码：

| 状态码 | 可以怎么理解 |
|---|---|
| 200 | 请求正常完成 |
| 400 | 请求格式或参数有问题 |
| 401 / 403 | 鉴权或权限问题 |
| 404 | Endpoint 不存在 |
| 422 | JSON 能解析，但字段校验不通过 |
| 429 | 请求过多、限流或服务忙 |
| 500 | 服务端内部异常 |
| 503 | 服务暂时无法处理 |

本轮最适合用来教学的反例是 Anthropic Tool Use：

~~~text
HTTP = 200
~~~

但是：

~~~text
没有得到标准 tool_use
~~~

所以：

> **HTTP 200 只代表服务成功处理了这个请求，不代表目标功能一定通过。**

---

# 十、非流式：一次性拿到完整回答

最普通的方式：

~~~json
"stream": false
~~~

流程：

~~~text
发送请求
   ↓
模型完整生成
   ↓
一次返回完整 Response
~~~

本次简单 Chat 实测约 806 ms 完成。

非流式适合：

- 后台接口；
- 批量处理；
- 结构化数据生成；
- 自动化测试；
- 不需要实时显示的任务。

---

# 十一、流式 SSE：为什么聊天界面能边生成边显示

把参数改为：

~~~json
"stream": true
~~~

服务端不会等整段答案完成，而是不断向客户端推送：

~~~text
data: ...
data: ...
data: ...
data: [DONE]
~~~

本次 Chat 实测可以看到：

~~~text
CHAT
_OK
[DONE]
~~~

这就是 SSE：

> **Server-Sent Events，服务器向客户端持续推送事件。**

流式不会让模型少计算，它主要改变结果返回方式。

因此：

~~~text
总生成时间
~~~

和：

~~~text
用户第一次看到内容的时间
~~~

是两个不同指标。

后者就是后面经常讲到的 TTFT：

> **Time To First Token，首 Token 延迟。**

---

# 十二、Token：大模型世界里的“工作量单位”

## 12.1 Token 不是字符，也不一定是单词

本轮测试文本：

~~~text
你好，Qwen3.6。这是一段用于 tokenizer 接口验证的中文测试文本。
~~~

调用：

~~~http
POST /tokenize
~~~

得到：

~~~text
20 tokens
~~~

同时返回实际 Token IDs。

再把 IDs 送到：

~~~http
POST /detokenize
~~~

能够完整还原原文。

所以模型真正处理的是：

~~~text
文本
 ↓
Tokenizer
 ↓
Token IDs
 ↓
模型
~~~

---

# 十三、为什么 Token 不只是“计费问题”

很多人会觉得：

> 我们是内网模型，又不按 OpenAI API 付钱，Token 不重要。

这是一个关键误区。

即使没有公网账单：

~~~text
Token
  ↓
算力
  ↓
内存 / 显存
  ↓
时间
  ↓
并发容量
~~~

输入 Token 越多：

- Prefill 越重；
- TTFT 往往越长；
- KV Cache 占用越高。

输出 Token 越多：

- Decode 越久；
- 一条请求占用计算资源越久。

所以 Agent 通常比普通 Chat 更“贵”。

Agent 会不断叠加：

- System Prompt；
- 项目规则；
- 文件；
- Tool Schema；
- Shell 输出；
- 浏览器内容；
- Git Diff；
- 历史 Tool Result；
- 多轮推理。

这就是为什么培训一开始就必须把 Token 讲清楚。

---

# 十四、128K Context 到底是什么意思

当前服务：

~~~text
max_model_len = 131072
~~~

大约就是我们通常说的：

~~~text
128K Context
~~~

但 Context 不是“用户可以独占输入 128K”。

真正共享这一预算的包括：

~~~text
System Prompt
+ 历史消息
+ 当前问题
+ 文件
+ RAG 检索内容
+ Tool Definitions
+ Tool Results
+ Agent 中间状态
+ 输出预留空间
~~~

因此：

> **Context Window 是一个共享预算。**

不是越大越好，也不是有 128K 就应该每次塞 128K。

长 Context 会影响：

- Prefill；
- TTFT；
- KV Cache；
- 并发；
- Agent 连续调用体验。

而且当前 131072 是服务声明值。

是否从 1K、10K、30K、60K 一直到 128K，在不同并发下都稳定，是另一类性能测试。

---

# 十五、Thinking 到底是什么

普通模式可以粗略理解为：

~~~text
问题
 ↓
模型
 ↓
回答
~~~

Thinking 模式则增加了推理预算：

~~~text
问题
 ↓
Reasoning / Thinking
 ↓
最终回答
~~~

当前 Chat 接口实测支持：

~~~json
"chat_template_kwargs": {
  "enable_thinking": true
}
~~~

以及：

~~~json
"chat_template_kwargs": {
  "enable_thinking": false
}
~~~

---

# 十六、Thinking 开关的真实 A/B 数据

同类逻辑题：

| | Thinking OFF | Thinking ON |
|---|---:|---:|
| 耗时 | 5.96 s | 48.46 s |
| Completion Tokens | 178 | 1024 |
| Reasoning | 无 | 有 |
| Finish Reason | stop | length |
| 最终答案 | 完整 | 被截断 |

这个 Demo 很值得现场展示。

但培训时不要把结论讲成：

> “开 Thinking 一定慢 8 倍。”

更准确的是：

> **同一个模型开启 Thinking 后，会额外消耗推理 Token、计算时间和输出预算；复杂任务可能值得，简单任务未必值得。**

这直接引出任务路由：

~~~text
简单任务
→ Non-Thinking

复杂推理
→ Thinking
~~~

再进一步可以变成：

~~~text
普通文档 / 简单代码
→ 内网模型 + Non-Thinking

普通 Agent
→ 内网模型 + Tool Calling

疑难分析 / 复杂设计
→ 更强模型 + 更高推理预算
~~~

---

# 十七、Tool Calling：Chat 走向 Agent 的关键基础能力

如果问模型：

> 北京天气怎么样？

模型本身并不知道今天北京真实天气。

普通 Chat 只能根据已有 Context 生成文本。

Agent 可以给模型一个工具：

~~~text
get_weather(city)
~~~

模型输出：

~~~json
{
  "name": "get_weather",
  "arguments": {
    "city": "北京"
  }
}
~~~

注意：

> **模型只是决定“调用哪个工具、传什么参数”。**

真正执行 HTTP、Shell、浏览器、文件系统、数据库、Git 或 MCP 的，是 Agent Runtime。

因此 Agent 的基本闭环是：

~~~text
用户
 ↓
模型
 ↓
Tool Call
 ↓
Runtime 执行工具
 ↓
Tool Result
 ↓
模型
 ↓
下一步
~~~

---

# 十八、什么叫“真的支持工具调用”

不合格的情况：

~~~json
{
  "content": "我将调用 get_weather(city='北京')"
}
~~~

这只是一句话。

真正 Tool Calling：

~~~json
{
  "tool_calls": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{"city":"北京"}"
      }
    }
  ]
}
~~~

程序可以直接解析函数名和参数并执行。

本次实测：

> **OpenAI Chat Tool Calling：PASS。**

---

# 十九、为什么已经有 Chat API，还要 Responses API

OpenAI Chat Completions 以 messages 为中心。

Responses API 更接近一系列有类型的输出 Item：

~~~text
reasoning
message
function_call
...
~~~

Streaming 也会变成：

~~~text
response.created
response.output_item.added
response.output_text.delta
response.completed
~~~

这对 Agent 更友好，因为客户端能明确知道：

> “现在返回的是文字、推理，还是 Tool Call？”

这也是为什么 Codex 一类 Agent 更重视 Responses 风格协议。

---

# 二十、我们内网的 Responses 实测

基础请求：

~~~http
POST /v1/responses
~~~

请求：

~~~json
{
  "model": "qwen3.6",
  "input": "请只回答：RESPONSES_OK",
  "max_output_tokens": 256,
  "reasoning": {
    "effort": "none"
  }
}
~~~

实测得到：

~~~text
object = response
status = completed
RESPONSES_OK
~~~

SSE 也能够完整看到：

~~~text
response.created
response.in_progress
...
response.completed
~~~

工具调用返回：

~~~json
{
  "type": "function_call",
  "name": "get_weather",
  "arguments": "{"city":"北京"}"
}
~~~

所以目前可以说：

> **OpenAI Responses 核心协议已经通过实测，可以继续做 Codex CLI 实际接入。**

但这里特意加“核心协议”。

因为：

~~~text
API 协议通过
≠
整个 Codex 产品工作流已经验证
~~~

后面还需要实际测试 Shell、File、Git、多轮工具调用、长任务和错误恢复。

---

# 二十一、Claude / Anthropic Messages 又是什么

Anthropic Messages 使用：

~~~http
POST /v1/messages
~~~

普通返回不是 choices[]，而是：

~~~json
{
  "type": "message",
  "role": "assistant",
  "content": [...]
}
~~~

工具定义也不同：

~~~text
OpenAI Chat:
function.parameters

Responses:
parameters

Anthropic:
input_schema
~~~

所以：

> **都叫“工具调用”，不代表请求 JSON 一样。**

---

# 二十二、Anthropic 测试为什么是本章最好的失败案例

我们的 /v1/messages 普通文本通过，SSE 也通过。

如果测试到这里就停止，很容易写成：

> “支持 Claude 接口。”

但继续测工具后发现问题。

请求已经明确：

~~~json
"thinking": {
  "type": "disabled"
}
~~~

实际普通响应仍然先出现 Thinking Block。

SSE 也持续出现：

~~~text
thinking_delta
~~~

到 Tool Use 测试时，模型其实已经在 Thinking 里推导出：

~~~json
{
  "name": "get_weather",
  "parameters": {
    "city": "北京"
  }
}
~~~

但一直没有真正生成：

~~~text
type = tool_use
~~~

最后：

~~~text
512 output tokens 用完
stop_reason = max_tokens
~~~

因此当前结论必须是：

> **Anthropic Messages 文本与 Streaming 协议通过，但 Thinking disabled 和 Tool Use 当前存在兼容问题。**

这比简单写“支持/不支持”更有工程价值。

---

# 二十三、三套协议一张图看懂

~~~text
                    qwen3.6
                       │
                 vLLM API Server
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
 OpenAI Chat        Responses       Anthropic
/chat/completions   /responses      /messages
        │              │              │
  messages[]          input         messages[]
        │              │              │
  tool_calls      function_call      tool_use
        │              │              │
   本轮 PASS        本轮 PASS       本轮 PARTIAL
~~~

实测状态：

| 协议 | 非流式 | 流式 | 工具调用 | 当前判断 |
|---|---:|---:|---:|---|
| OpenAI Chat | ✅ | ✅ | ✅ | PASS |
| Responses / Codex | ✅ | ✅ | ✅ | PASS（核心协议） |
| Anthropic Messages | ✅ | ✅ | ❌ | PARTIAL |

培训时可以强调：

> **“OpenAI-compatible”不是一个简单的 Yes/No 标签。兼容性应该拆成 Endpoint、Schema、Streaming、Thinking、Tool Calling、多轮 Tool Result 等能力逐项验证。**

---

# 二十四、/version 有什么用

实测：

~~~http
GET /version
~~~

返回：

~~~json
{
  "version": "0.23.0"
}
~~~

为什么要讲这么一个看起来不起眼的接口？

因为：

> **API 行为不只是由模型决定。**

还受到：

- vLLM 版本；
- Chat Template；
- Reasoning Parser；
- Tool Call Parser；
- 启动参数；
- Ascend 适配版本；

影响。

某个 Agent “以前能用、今天不能用”时，不要只问“模型是不是变笨了”，还要检查服务版本和启动配置。

---

# 二十五、/openapi.json：让服务自己描述接口

调用：

~~~http
GET /openapi.json
~~~

我们实测发现：

~~~text
/v1/models
/v1/chat/completions
/v1/responses
/v1/messages
/tokenize
/detokenize
/version
/metrics
~~~

OpenAPI 描述：

- 有哪些 Endpoint；
- 接收什么字段；
- 字段类型是什么；
- 返回什么 Schema。

对于工程师，它可以用于：

- 自动生成文档；
- 自动生成 Client；
- Postman 导入；
- 自动化接口测试；
- 前后端联调。

但一定要补一句：

> **Schema 存在不代表行为完全正确。**

Anthropic Tool Use 就是这句话的实测证据。

---

# 二十六、/metrics：从“能用”走向“好用”

调用：

~~~http
GET /metrics
~~~

本轮可以看到：

~~~text
vllm:num_requests_running
vllm:num_requests_waiting
vllm:kv_cache_usage_perc
vllm:prefix_cache_queries_total
vllm:prefix_cache_hits_total
vllm:prompt_tokens_total
~~~

还可以看到部分配置/运行标签：

~~~text
enable_prefix_caching="False"
gpu_memory_utilization="0.85"
num_gpu_blocks="487"
~~~

这里正好把本章与后面的 Model-Metric 案例串起来。

普通 API Response 告诉你：

> “这一条请求用了多少 Token。”

Metrics 告诉你：

> “整个服务现在到底怎么样。”

例如：

~~~text
有多少请求正在运行？
有多少请求正在排队？
KV Cache 用了多少？
Prefix Cache 有没有命中？
整体吞吐怎么样？
~~~

这就从“能不能返回答案”，升级到了“能不能作为共享服务稳定运行”。

---

# 二十七、Prefix Cache 为什么值得关注

本次 metrics 快照中：

~~~text
enable_prefix_caching="False"
~~~

Agent 场景通常有很长、重复度很高的前缀：

~~~text
System Prompt
AGENTS.md
工具定义
项目规则
~~~

然后每轮真正变化的只是后面一小部分。

如果服务能复用相同前缀的计算，就可能降低重复 Prefill。

因此：

> **Prefix Cache 对 Agent 不是一个无关紧要的小优化，而是值得专项评估的服务能力。**

当前只能说快照显示未启用；是否开启，以及开启后的收益与稳定性，需要单独测试。

---

# 二十八、Prefill 和 Decode

理解大模型性能，至少要分清两个阶段。

~~~text
很长的输入
   │
   ▼
Prefill
   │
   │  TTFT 主要受这里影响
   ▼
第一个 Token
   │
   ▼
Decode
   │
   ├→ Token
   ├→ Token
   └→ ...
~~~

Prefill：

> 模型先“读完”输入。

Decode：

> 模型一个 Token 一个 Token 地往后生成。

所以：

- 长 Context 通常首先冲击 TTFT；
- 很长的回答会增加 Decode 总时间。

这也解释了为什么不能只用一个 Tokens/s 描述全部模型性能。

---

# 二十九、KV Cache

模型生成第 100 个 Token 时，不会把前 99 个 Token 的全部 Attention 从零再计算一遍。

推理框架会缓存过去 Token 对应的 Key / Value：

~~~text
KV Cache
~~~

优点：

> 降低连续生成中的重复计算。

代价：

> Context 越长、并发越高，KV Cache 占用越大。

所以会形成典型矛盾：

~~~text
Context 更长
        ↓
每个请求占更多 KV Cache
        ↓
同时能容纳的请求减少
        ↓
更容易出现排队
~~~

这也是后续性能压测的重点。

---

# 三十、这套 API 对我们意味着什么

到这里，可以把当前内网模型服务从：

> “一个网页，可以和大模型聊天。”

升级成：

~~~text
内网模型服务
│
├─ Chat API
├─ Streaming
├─ Thinking
├─ Tool Calling
├─ Responses API
├─ Anthropic Messages
├─ Tokenizer
├─ Metrics
└─ OpenAPI
~~~

这意味着它已经具备成为 AI 基础服务的雏形。

上层可以是：

~~~text
WebUI
Cherry Studio
Python 程序
RAG
数据分析
API 自动化
运维助手
浏览器 Agent
编码 Agent
内部业务系统
~~~

---

# 三十一、但这还不等于“Agent 已经完全可用”

当前实测还缺几个重要闭环：

~~~text
Tool Call
   ↓
真实工具执行
   ↓
Tool Result 回灌
   ↓
模型继续下一步
~~~

以及：

~~~text
连续多轮工具调用
并行工具调用
错误工具参数恢复
长任务稳定性
128K 长上下文稳定性
Codex CLI 实机
Claude Code 实机
~~~

所以当前最准确的定位是：

> **已经具备较完整的模型 API 与 Agent 基础协议能力，但正式 Agent 生产体验仍需要连续工具调用、长上下文和客户端实机测试。**

---

# 三十二、本章最重要的结论

### 结论 1：大模型不是一个网页

真正可以被系统复用的是：

~~~text
模型 + API
~~~

WebUI 只是其中一个客户端。

### 结论 2：Token 是资源，不只是账单

即使模型部署在自己机房：

~~~text
Token = 算力 + 时间 + 内存 + 并发容量
~~~

### 结论 3：Thinking 是预算，不是“越开越强”

应该根据任务难度选择。

### 结论 4：Tool Calling 是 Chat 到 Agent 的关键一步

有了 Tool Calling，模型才能通过 Agent Runtime 使用外部工具。

### 结论 5：兼容不是 Yes / No

真正的兼容矩阵应该拆开：

~~~text
Endpoint
Request Schema
Streaming
Thinking
Tool Calling
Tool Result
Multi-turn
Error Recovery
~~~

### 结论 6：现网结论必须来自实测

官方模型卡回答：

> “这个模型理论上具备什么能力？”

我们自己的 API Test、Metrics、Agent Test 回答：

> **“我们现在部署出来的这一套，到底能做到什么程度？”**

---

# 三十三、推荐的现场 Demo 顺序

## Demo 1：GET /v1/models

展示模型 ID、131072、JSON 和 GET。

结论：

> 我们先问服务器自己，它到底部署了什么。

## Demo 2：POST /v1/chat/completions

先 stream=false，再 stream=true。

让大家直观看到：

> 一次性 Response 和 SSE 是两回事。

## Demo 3：/tokenize

把一段熟悉的中文送进去。

让大家看到：

> 人看到一句话，模型看到一串 Token ID。

## Demo 4：Thinking OFF / ON

直接对比耗时和输出 Token。

这是本章最有冲击力的数据之一。

## Demo 5：Tool Calling

展示：

~~~text
get_weather
city = 北京
~~~

然后问：

> “模型真的访问天气网站了吗？”

答案：

> 没有。模型只产生 Tool Call，真正执行的是 Agent。

这是接入下一章 Agent 的最好过渡。

## Demo 6：OpenAI / Responses / Anthropic

只展示三种关键结构：

~~~text
tool_calls
function_call
tool_use
~~~

再展示 Anthropic Tool Use 的失败记录。

结论：

> **API 兼容不是看名字，而是测出来的。**

---

# 三十四、PPT 静态展示与现场 Demo 的分工

适合 PPT 固化：

- 内网模型卡片：35B / A3B / MoE / 当前 128K；
- API 总体架构；
- GET vs POST；
- 非流式 vs SSE；
- Token → Token ID；
- Thinking OFF/ON 对比数据；
- Tool Calling 流程；
- 三套协议对比表；
- 17 项测试矩阵；
- Anthropic PARTIAL 异常案例；
- Metrics → Model-Metric 的过渡。

适合现场 Demo：

- Postman GET /v1/models；
- Chat 非流式；
- Chat SSE；
- /tokenize；
- Thinking 开关；
- Tool Calling；
- 如果现场服务状态允许，再直接运行 qwen_api_training_test.py。

现场 Demo 应准备备用截图，因为实际服务可能出现排队、网络或资源波动。

---

# 三十五、与下一章 Agent 的衔接

本章最后不要停在：

> “我们测试完了 17 个接口。”

而应该停在一个问题：

> **既然模型已经能够输出 Tool Call，那么谁来真正执行这些工具？**

答案就是下一章：

~~~text
模型
+ Context
+ Workspace
+ File
+ Shell
+ Browser
+ Git
+ API
+ MCP
+ Skill
+ Memory
= Agent
~~~

也就是说：

> **API 是模型走出聊天框的第一步，Tool Calling 是 Chat 走向 Agent 的关键桥梁。**

---

# 参考与证据

本讲义事实来源分三层：

1. Qwen 官方 Qwen3.6-35B-A3B 模型卡和配置：用于模型结构、参数规模、MoE、原生 Context 等模型本体信息。
2. vLLM 官方 Online Serving 文档：用于 Chat Completions、Responses、Anthropic Messages、Tokenize / Detokenize 等服务接口背景。
3. api/qwen/results/20260929_105316/：用于所有“当前内网服务已通过/未通过”的判断。

培训时若官方能力与本地实测不一致，**以本地实测描述当前服务，以官方资料描述模型本体**。
