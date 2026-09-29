# Qwen3.6 内网模型服务 API 实测报告

> 测试日期：2026-09-29  
> 测试对象：部门内网 Qwen3.6 模型服务  
> 测试脚本：`api/qwen/qwen_api_training_test.py`  
> 原始实测证据：`api/qwen/results/20260929_105316/`

## 1. 测试目的

本次测试不是只确认“模型能不能聊天”，而是从工程使用角度验证当前内网大模型服务是否具备作为 WebUI、脚本、业务系统和 Agent 后端的基础条件。

重点回答以下问题：

1. 当前内网实际部署的模型是什么，服务端实际暴露的上下文长度是多少？
2. HTTP API 的 GET、POST、JSON Request/Response 是否正常？
3. Chat Completions 的非流式和 SSE 流式是否可用？
4. Tokenize / Detokenize 是否可用，能否用于解释 Token 与 Context Window？
5. Thinking 是否可以按请求打开和关闭？
6. Tool Calling 是否能够返回真正的结构化工具调用，而不是在文本中“模拟调用”？
7. OpenAI Chat、OpenAI Responses（Codex 所需核心协议）、Anthropic Messages 三类协议分别兼容到什么程度？
8. `/metrics` 和 `/openapi.json` 能否为监控、自动测试和接口学习提供基础？

本报告坚持区分三类信息：

- **官方模型能力**：来自 Qwen 官方模型卡或官方配置；
- **当前部署配置**：来自内网服务实际返回和现场部署信息；
- **本次实测结果**：来自 2026-09-29 的测试脚本与请求/响应记录。

不能用官方模型参数替代现网实测，也不能因为某个 Endpoint 返回 HTTP 200 就直接判断“协议完全兼容”。

---

## 2. 内网模型与部署概况

### 2.1 当前内网服务

| 项目 | 当前信息 | 证据 |
|---|---|---|
| 对外模型 ID | `qwen3.6` | `GET /v1/models` |
| 模型目录标识 | `Qwen3.6-35B-A3B-w8a8-ascend` | `GET /v1/models` |
| 当前最大上下文 | **131072 tokens** | `max_model_len` |
| 服务框架版本 | **vLLM 0.23.0** | `GET /version` |
| System Fingerprint | `vllm-0.23.0-tp2-78580a24` | Chat 实测响应 |
| 计算平台 | 两个华为昇腾节点 | 现场部署信息 |
| OpenAI Chat | 已通过 | 非流式、SSE、Thinking、Tool Calling |
| OpenAI Responses | 已通过核心协议 | 非流式、SSE、Function Calling |
| Anthropic Messages | 部分通过 | 文本/SSE 通过，Tool Use 未通过 |
| Tokenizer API | 已通过 | Tokenize / Detokenize 闭环 |
| 监控接口 | 已通过 | `/metrics` |
| OpenAPI | 已通过 | `/openapi.json` |

模型路径中的 `w8a8` 是当前部署版本名称的一部分。本次测试只验证了 API 行为，没有对底层量化实现独立做数值校验，因此本报告不进一步推断具体量化算法实现。

### 2.2 官方模型与当前部署不能混为一谈

Qwen3.6-35B-A3B 官方模型卡显示，该模型是带视觉编码器的 MoE 模型，语言模型部分约为 **35B 总参数、3B 激活参数**，包含 256 个专家，每个 Token 路由到 8 个 Routed Experts，并有 Shared Expert；官方原生上下文长度为 **262,144 tokens**。

而我们的实际服务返回：

```json
{
  "id": "qwen3.6",
  "root": "/models/Qwen3.6-35B-A3B-w8a8-ascend",
  "max_model_len": 131072
}
```

因此培训中应统一说：

> **Qwen3.6-35B-A3B 官方模型原生上下文为 262K；部门当前内网部署实际对外提供的是 131072 tokens，即约 128K。**

同理，官方模型带 Vision Encoder，不代表当前内网多模态 API 已经通过验收。本轮只测试了文本 API，因此当前培训材料不把图像输入列为“现网已验证能力”。

### 2.3 35B 与 A3B 分别是什么意思

可以把模型名称中的两个数字理解为：

- `35B`：总参数量级；
- `A3B`：一次前向计算中大约激活 3B 参数。

这是 MoE（Mixture of Experts，混合专家）架构的核心特征之一。

简化理解：

```text
输入 Token
   │
   ▼
 Router
   │
   ├── Expert 1
   ├── Expert 2
   ├── ...
   └── Expert N
        │
        ▼
只选择部分专家参与当前 Token 的计算
```

Dense 模型的大部分参数每次都会参与计算；MoE 则拥有更大的总参数容量，但每个 Token 只激活部分专家。

这不等于“35B 模型只需要 3B 模型的全部资源”。模型权重存储、专家分布、通信、KV Cache、长上下文 Prefill、Decode、并发请求等仍然会占用大量计算和内存资源。实际服务体验必须看部署和压测，而不能只看参数名。

---

## 3. API 服务整体结构

当前内网服务可以抽象为：

```text
Postman / Python / WebUI / Agent / 业务系统
                    │
                    │ HTTP + JSON / SSE
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
```

几个概念必须分开：

- **Qwen3.6** 是模型；
- **vLLM** 是推理与 API 服务框架；
- **HTTP API** 是客户端访问模型服务的方式；
- **OpenAI Chat / Responses / Anthropic Messages** 是不同的 API 协议格式；
- **Postman、Python、WebUI、Agent** 是 API 的客户端；
- Agent 并不是直接“操作模型权重”，而是在多轮调用模型 API，并执行模型产生的工具请求。

---

## 4. HTTP API 基础：GET、POST、JSON、Header、状态码

### 4.1 GET：读取资源

典型接口：

```http
GET /v1/models
```

GET 通常用于读取已有资源或服务状态，本次还包括：

```text
GET /version
GET /metrics
GET /openapi.json
```

`/v1/models` 关键返回：

```json
{
  "object": "list",
  "data": [
    {
      "id": "qwen3.6",
      "owned_by": "vllm",
      "max_model_len": 131072
    }
  ]
}
```

### 4.2 POST：提交任务

典型接口：

```http
POST /v1/chat/completions
```

请求体使用 JSON：

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
  "max_tokens": 128,
  "stream": false,
  "chat_template_kwargs": {
    "enable_thinking": false
  }
}
```

典型 Header：

```http
Content-Type: application/json
Authorization: Bearer <API_KEY>
```

API Key 用于身份认证，培训截图、脚本日志、Git 仓库都不应保存真实密钥。

### 4.3 Request 与 Response

一次 API 调用可以抽象为：

```text
Request
├─ URL
├─ Method
├─ Headers
└─ Body
       │
       ▼
   API Server
       │
       ▼
Response
├─ HTTP Status Code
├─ Headers
└─ Body
```

常见状态码可用以下方式解释：

| 状态码 | 工程含义 |
|---|---|
| 200 | 请求成功 |
| 400 | 请求格式、参数或协议不满足要求 |
| 401/403 | 鉴权或权限问题 |
| 404 | Endpoint 不存在 |
| 422 | 请求结构可以解析，但字段校验不通过 |
| 429 | 限流或服务忙 |
| 500 | 服务端内部异常 |
| 503 | 服务暂时不可用或资源不足 |

本轮 17 个核心测试请求均成功到达服务端；其中 Anthropic Tool Use 虽然 HTTP 状态码为 200，但协议层未产生预期的 `tool_use`。这正好说明：

> **HTTP 200 只代表请求成功处理，不等于业务或协议能力一定通过。**

---

## 5. OpenAI Chat Completions：非流式与流式

### 5.1 非流式请求

本次实测：

```http
POST /v1/chat/completions
```

请求：

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
  "max_tokens": 128,
  "stream": false,
  "chat_template_kwargs": {
    "enable_thinking": false
  }
}
```

关键响应：

```json
{
  "object": "chat.completion",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "CHAT_OK",
        "reasoning": null
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 18,
    "completion_tokens": 3,
    "total_tokens": 21
  }
}
```

实测耗时约 **806 ms**。

非流式工作方式：

```text
发送请求
   ↓
模型生成完整结果
   ↓
服务器一次性返回完整 JSON
```

适合：

- 后台任务；
- 结构化结果；
- 批处理；
- 简单脚本；
- 希望一次拿到完整 JSON 的场景。

### 5.2 SSE 流式请求

将：

```json
"stream": true
```

服务端开始使用 SSE（Server-Sent Events）逐步返回增量数据。

本次 Chat 实测：

```text
data: {"object":"chat.completion.chunk","choices":[{"delta":{"content":"CHAT"}}]}

data: {"object":"chat.completion.chunk","choices":[{"delta":{"content":"_OK"},"finish_reason":"stop"}]}

data: [DONE]
```

工作方式变成：

```text
发送请求
   ↓
模型开始生成
   ↓
Token / 文本片段不断产生
   ↓
SSE 持续推送
   ↓
客户端边接收边显示
```

流式并不会让模型“少算”，它主要改变结果返回方式。对 Chat UI 来说，它显著改善用户感知；对 Agent 来说，还可以提前暴露 reasoning、工具调用、阶段状态等事件。

---

## 6. Tokenize / Detokenize

### 6.1 模型不是直接按“字”理解文本

大语言模型接收的是 Token ID，而不是原始字符串。

简化流程：

```text
"你好，Qwen3.6"
       │
       ▼
   Tokenizer
       │
       ▼
[109266, 3709, ...]
       │
       ▼
      LLM
```

### 6.2 本次实测

输入：

```text
你好，Qwen3.6。这是一段用于 tokenizer 接口验证的中文测试文本。
```

请求：

```http
POST /tokenize
```

关键响应：

```json
{
  "count": 20,
  "max_model_len": 131072,
  "tokens": [
    109266,
    3709,
    48,
    16451,
    18,
    13,
    21,
    1710,
    104749,
    96460,
    98618,
    44424,
    220,
    108622,
    103838,
    95726,
    99986,
    99449,
    109120,
    1710
  ]
}
```

再将这些 Token ID 提交到：

```http
POST /detokenize
```

返回：

```json
{
  "prompt": "你好，Qwen3.6。这是一段用于 tokenizer 接口验证的中文测试文本。"
}
```

本轮结论：

> **Tokenize → Token IDs → Detokenize → 原文，闭环通过。**

### 6.3 Token 为什么是培训重点

即使是内网私有模型，没有公网按 Token 计费，Token 仍然代表真实资源成本。

输入越长：

- Prefill 计算量越大；
- TTFT 往往越长；
- KV Cache 占用越高；
- 并发容量越容易下降。

输出越长：

- Decode 时间越长；
- 输出 Token 越多；
- 请求占用计算资源越久。

所以：

> **“上下文越大越好”不是工程结论。能放进去，不代表值得放进去。**

---

## 7. Context Window：131072 代表什么

当前服务返回：

```text
max_model_len = 131072
```

它表示单次模型请求的 Token 序列存在约 128K 的服务端上限。

Context 中不只有用户最新一句话，还可能包含：

```text
System Prompt
+ 历史对话
+ 当前问题
+ RAG 检索内容
+ 文件内容
+ 工具定义
+ 工具返回
+ Agent 中间状态
+ 输出预留空间
```

因此 Agent 比简单 Chat 更容易快速消耗 Context。

还要特别注意：

> `/v1/models` 返回 131072 只能证明当前服务“声明”的最大长度。本轮尚未完成从短上下文逐级增长到 131072 的完整成功率、TTFT、吞吐和内存压力验证。

所以当前正确说法是：

- **配置/声明：131072；**
- **是否在各种并发下都能稳定跑到 131072：仍需压测验证。**

---

## 8. Thinking 开关实测

### 8.1 什么是 Thinking

Thinking 模式可以简单理解为：模型在最终回答之前生成额外的推理过程或 reasoning token。

在当前 OpenAI Chat 风格接口中，实测可以通过：

```json
"chat_template_kwargs": {
  "enable_thinking": true
}
```

开启，以及：

```json
"chat_template_kwargs": {
  "enable_thinking": false
}
```

关闭。

### 8.2 A/B 实测结果

针对同类逻辑题：

| 模式 | 耗时 | Completion Tokens | Reasoning | Finish Reason |
|---|---:|---:|---|---|
| Thinking OFF | 5963.22 ms | 178 | 无 | `stop` |
| Thinking ON | 48459.36 ms | 1024 | 有 | `length` |

Thinking OFF 能完整回答。

Thinking ON 检测到独立 reasoning，但 1024 个输出 Token 被全部消耗，最终答案因达到长度上限而被截断。

### 8.3 这个结果能说明什么

可以说明：

- Thinking 会消耗额外 Token；
- Thinking 会增加整个请求的持续时间；
- 如果 `max_tokens` 设置太小，推理过程可能挤占最终答案空间；
- Agent 中如果每一轮工具选择都进行长 Thinking，端到端时延会被多轮放大。

但不能说：

> “Thinking 一定慢 8 倍。”

因为本轮只是单次行为对比，两次请求最大输出长度不同，也没有进行多次重复统计。

正确培训结论是：

> **Thinking 是一种需要按任务选择的计算预算，而不是一个应该永远打开的“增强按钮”。**

---

## 9. Tool Calling：模型如何从“回答问题”走向“执行任务”

### 9.1 普通 Chat

普通对话：

```text
用户问题
   ↓
模型
   ↓
文本回答
```

模型只能根据已有 Context 生成文本。

### 9.2 Tool Calling

Tool Calling：

```text
用户需求
   ↓
模型判断需要工具
   ↓
返回结构化 Tool Call
   ↓
Agent / 程序执行真实工具
   ↓
Tool Result 回传模型
   ↓
模型继续处理
```

关键点是：

> **模型本身并没有真的执行天气 API、Shell、浏览器或 Git。模型输出“应该调用什么”；真正执行动作的是 Agent Runtime。**

### 9.3 OpenAI Chat Tool Calling 实测

定义工具：

```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "查询指定城市当前天气",
    "parameters": {
      "type": "object",
      "properties": {
        "city": {
          "type": "string"
        }
      },
      "required": ["city"]
    }
  }
}
```

用户要求：

```text
查询北京天气，必须调用 get_weather 工具。
```

关键响应：

```json
{
  "message": {
    "role": "assistant",
    "tool_calls": [
      {
        "type": "function",
        "function": {
          "name": "get_weather",
          "arguments": "{\"city\": \"北京\"}"
        }
      }
    ],
    "reasoning": null
  },
  "finish_reason": "tool_calls"
}
```

这说明模型没有只输出：

```text
“我准备调用 get_weather……”
```

而是返回了应用可以直接解析的标准结构化工具调用。

本项：

> **PASS。**

---

## 10. /v1/models、/version、/metrics、/openapi.json 分别有什么用

### 10.1 /v1/models：不要把模型名称写死在脑子里

```http
GET /v1/models
```

可用于：

- 获取当前服务实际提供的模型；
- 获取模型 ID；
- 获取当前服务暴露的 `max_model_len`；
- 前端动态生成模型下拉列表；
- 自动化测试避免硬编码模型 ID。

本次返回：

```text
model = qwen3.6
max_model_len = 131072
```

### 10.2 /version：确认服务实现版本

```http
GET /version
```

实测：

```json
{
  "version": "0.23.0"
}
```

它对于排查兼容问题非常重要：

> 同一个模型换了 vLLM 版本、Tool Parser、Reasoning Parser 或 Chat Template，API 行为可能发生变化。

### 10.3 /metrics：模型服务的“仪表盘原料”

```http
GET /metrics
```

当前服务返回 Prometheus 格式 metrics。

本次证据中可看到：

```text
vllm:num_requests_running
vllm:num_requests_waiting
vllm:kv_cache_usage_perc
vllm:prefix_cache_queries_total
vllm:prefix_cache_hits_total
vllm:prompt_tokens_total
```

以及本次快照中的部分配置/运行标签：

```text
enable_prefix_caching="False"
gpu_memory_utilization="0.85"
num_gpu_blocks="487"
```

它和单次 Response 里的 `usage` 不同：

- Response usage：解释**这一条请求**用了多少 Token；
- `/metrics`：解释**整个服务**现在有多少请求、缓存占用、吞吐和累计指标。

这正是后续 model-metric 项目的数据基础。

### 10.4 /openapi.json：让服务“自我描述”

```http
GET /openapi.json
```

本次实际发现：

```text
/v1/models
/v1/chat/completions
/v1/responses
/v1/messages
/tokenize
/detokenize
/version
/metrics
```

它的工程价值是：

- 查看服务到底暴露了哪些 Endpoint；
- 查看 Request/Response Schema；
- 自动生成 API 文档；
- 辅助 Postman/客户端开发；
- 编写自动化兼容性测试。

但是：

> **OpenAPI 里存在一个 Endpoint，只能证明服务声明了这个接口；真正是否兼容，还必须实际发请求验证。**

本轮 Anthropic Tool Use 就是反例。

---

## 11. OpenAI、Codex、Claude 三种接口实测

这三种接口不是“换个 URL 而已”，它们的数据结构也不同。

### 11.1 OpenAI Chat Completions

Endpoint：

```text
/v1/chat/completions
```

核心输入：

```json
{
  "messages": [...]
}
```

工具调用核心返回：

```text
choices[].message.tool_calls[]
```

本轮结果：

- 非流式：PASS；
- SSE：PASS；
- Thinking OFF/ON：PASS；
- Tool Calling：PASS。

结论：

> **当前服务 OpenAI Chat Completions 兼容链路已经形成较完整实测证据。**

### 11.2 OpenAI Responses / Codex

Endpoint：

```text
/v1/responses
```

基础输入不再是 `messages`，而可以直接使用：

```json
{
  "model": "qwen3.6",
  "input": "请只回答：RESPONSES_OK"
}
```

普通返回核心：

```text
object = response
output[]
```

Tool Call 核心：

```json
{
  "type": "function_call",
  "name": "get_weather",
  "arguments": "{\"city\": \"北京\"}"
}
```

本轮结果：

- Responses 非流式：PASS；
- Responses SSE：PASS；
- Function Calling：PASS。

因此可以说：

> **当前服务已通过 Codex 所依赖的 OpenAI Responses 核心协议测试。**

但必须保留边界：

> 这不等于已经完成 Codex CLI 的产品级验收。真实 Codex CLI 还需要测试长任务、多轮工具、错误恢复、Shell/File/Git 工作流等。

### 11.3 Anthropic Messages / Claude

Endpoint：

```text
/v1/messages
```

Anthropic 风格工具定义使用：

```text
input_schema
```

而不是 OpenAI Chat 的：

```text
function.parameters
```

也不是 Responses 的：

```text
parameters
```

本轮结果：

- Messages 普通文本：PASS；
- Anthropic SSE：PASS；
- Tool Use：FAIL。

更重要的是：

请求中已经设置：

```json
"thinking": {
  "type": "disabled"
}
```

实际普通响应仍先出现 `thinking` block；流式响应仍出现 `thinking_delta`。

Tool Use 测试中，模型在 Thinking 内容里已经明确推导出应该调用：

```json
{
  "name": "get_weather",
  "parameters": {
    "city": "北京"
  }
}
```

但直到 512 个输出 Token 全部用完，也没有形成标准：

```json
{
  "type": "tool_use"
}
```

最终：

```text
stop_reason = max_tokens
```

因此当前应准确表述为：

> **Anthropic Messages 文本与 SSE 协议已经通过；当前服务的 Anthropic 风格 Thinking 关闭和 Tool Use 存在兼容问题，整体只能判定为 PARTIAL。**

---

## 12. 三套协议对比

| 项目 | OpenAI Chat | OpenAI Responses / Codex | Anthropic Messages |
|---|---|---|---|
| Endpoint | `/v1/chat/completions` | `/v1/responses` | `/v1/messages` |
| 主要输入 | `messages[]` | `input` | `messages[]` |
| 文本输出 | `choices[].message.content` | `output[].content[]` | `content[]` |
| 流式 | chunk + `[DONE]` | `response.*` SSE Events | `message_*` / `content_block_*` |
| 工具 Schema | `function.parameters` | `parameters` | `input_schema` |
| 工具输出 | `tool_calls[]` | `function_call` | `tool_use` |
| 本轮状态 | **PASS** | **PASS（核心协议）** | **PARTIAL** |

培训时可以强调：

> **“OpenAI-compatible”不是一个二元标签。兼容性应该拆成 Endpoint、请求 Schema、流式、Reasoning、Tool Calling、多轮 Tool Result 等能力逐项验证。**

---

## 13. 本轮测试矩阵

本轮共执行 17 项测试：

| # | 测试项 | 结果 |
|---:|---|---|
| 1 | `/v1/models` | PASS |
| 2 | `/version` | PASS |
| 3 | `/metrics` | PASS |
| 4 | `/openapi.json` | PASS |
| 5 | `/tokenize` | PASS |
| 6 | `/detokenize` | PASS |
| 7 | OpenAI Chat 非流式 | PASS |
| 8 | OpenAI Chat SSE | PASS |
| 9 | Thinking OFF | PASS |
| 10 | Thinking ON | PASS，但输出被 max_tokens 截断 |
| 11 | OpenAI Chat Tool Calling | PASS |
| 12 | Responses 非流式 | PASS |
| 13 | Responses SSE | PASS |
| 14 | Responses Function Calling | PASS |
| 15 | Anthropic Messages | PASS |
| 16 | Anthropic SSE | PASS |
| 17 | Anthropic Tool Use | **FAIL** |

总体：

```text
16 PASS
1 FAIL
```

但“16/17”不应被包装成简单的成功率，因为不同测试项的重要性不同。特别是 Anthropic Tool Use 对 Claude Code 类型 Agent 的实际可用性影响较大。

---

## 14. 关键工程判断

### 判断一：当前内网服务已经不仅是“聊天模型”

它已经具备：

- 结构化 API；
- Streaming；
- Thinking；
- Tool Calling；
- Responses；
- Tokenizer；
- Metrics；
- OpenAPI。

这意味着它可以成为：

- Chat UI 后端；
- 内部 Python/Java/Go 服务；
- RAG；
- 自动化脚本；
- Agent Runtime；

的基础模型服务。

### 判断二：Agent 场景中，Tool Calling 比“回答好不好看”更关键

Agent 真正依赖：

```text
稳定输出结构化工具调用
        ↓
工具参数合法
        ↓
工具结果能回灌
        ↓
模型继续下一步
```

因此后续测试重点应该从“单轮问答”转向“连续 Agent Loop”。

### 判断三：Thinking 应该作为任务路由参数

简单问答、RAG 摘要、普通工具选择，不一定值得开启长 Thinking。

复杂故障分析、方案设计、疑难代码问题，可以启用更高推理预算。

这就是：

> **能力、时延和资源成本之间的工程权衡。**

### 判断四：协议兼容需要实测，不要只看文档

本轮最典型的例子是 Anthropic：

- Endpoint 存在；
- 普通 Message 正常；
- Streaming 正常；
- 但 `thinking.type=disabled` 未观察到生效；
- Tool Use 没有落到标准结构。

所以“支持 Anthropic API”必须进一步问：

> 支持到哪一层？

---

## 15. 当前测试还缺什么

本轮已经足够支撑第一版培训，但如果要判断“能否作为部门正式 Agent 模型服务”，建议继续补充：

1. **Tool Result 回灌闭环**：工具调用后，将结果重新交给模型，验证最终回答。
2. **连续多轮工具调用**：5～10 轮 Tool Loop 稳定性、参数错误率。
3. **Parallel Tool Calling**：一次返回多个工具调用的行为。
4. **Anthropic Tool Use 重测**：增加 `max_tokens`，进一步确认 Thinking disabled 映射问题。
5. **Codex CLI 实机接入**：验证 Shell、文件、Git、多轮任务。
6. **Claude Code 实机接入**：验证 Messages + Tool Use 的真实兼容。
7. **128K 上下文宣称验证**：逐步增加输入长度，观察成功率、TTFT、KV Cache 和吞吐。
8. **多次重复测试**：至少统计平均值、P50、P95，而不是用单次时延做性能结论。
9. **并发测试**：1、2、3、4…并发下观察排队、TTFT、Decode 吞吐。
10. **Prefix Cache**：当前 metrics 快照显示未启用前缀缓存，应评估 Agent 长系统提示词下的收益。

---

## 16. 最终结论

截至 2026-09-29，本轮实测可以形成以下结论：

> 部门当前部署的 Qwen3.6-35B-A3B-w8a8-ascend 服务，对外模型 ID 为 `qwen3.6`，服务端声明上下文长度为 131072 tokens，运行于 vLLM 0.23.0。OpenAI Chat Completions 的非流式、SSE、Thinking 开关和 Tool Calling 均已通过；OpenAI Responses 的非流式、SSE 与 Function Calling 均已通过，可作为 Codex 协议接入的基础；Anthropic Messages 的文本与 SSE 已通过，但 Thinking 关闭参数未观察到生效，Tool Use 当前未通过，因此只能判定为部分兼容。

从培训角度，这组测试最大的价值不是证明“这个模型很强”，而是形成一种工程判断方法：

> **不要只问模型支持什么；要把能力拆成协议、参数、流式、工具调用、上下文、性能和稳定性，然后用真实 Request / Response 验证。**

## 参考依据

- Qwen 官方 `Qwen3.6-35B-A3B` 模型卡与配置文件：用于模型结构、参数量、MoE、官方 Context Length、Tool Calling / Reasoning 配置说明。
- vLLM Online Serving 官方文档：用于 OpenAI-compatible、Responses、Anthropic Messages、Tokenize / Detokenize 等接口定义。
- 部门内网 2026-09-29 实际测试记录：用于当前部署能力、兼容性、时延和异常结论。

> 本报告中对“当前内网支持情况”的判断，始终以本地实测数据为最高优先级。
