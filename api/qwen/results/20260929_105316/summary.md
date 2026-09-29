# Qwen3.6 内网 API 兼容性测试记录

- 生成时间：`2026-09-29T10:54:50+08:00`
- API 根地址：`http://<INTRANET_API_HOST>:<PORT>`
- 模型：`qwen3.6`
- 宣称上下文：`131072` tokens
- 部署说明：两个华为昇腾节点部署 `Qwen3.6-35B-A3B-w8a8-ascend`（以现场部署信息为准）
- 安全说明：日志中的 API Key 已自动打码。

## 一、协议兼容性结论

| 协议 | 结果 | 判定依据 |
|---|---|---|
| OpenAI Chat Completions | **PASS** | models + 非流式 chat + 流式 chat + tool_calls |
| Codex / OpenAI Responses | **PASS** | Responses 非流式 + Responses SSE + function_call |
| Claude / Anthropic Messages | **PARTIAL** | Messages 非流式 + Messages SSE + tool_use |

## 二、逐项测试结果

| # | 分类 | 测试项 | 方法 | Endpoint | 结果 | HTTP | 耗时(ms) | 说明 | 记录文件 |
|---:|---|---|---|---|---|---:|---:|---|---|
| 1 | 基础接口 | models | GET | `/v1/models` | **PASS** | 200 | 34.38 | 找到模型 qwen3.6，max_model_len=131072 | `01_models.json` |
| 2 | 基础接口 | version | GET | `/version` | **PASS** | 200 | 5.86 | version 接口可访问 | `02_version.json` |
| 3 | 基础接口 | metrics | GET | `/metrics` | **PASS** | 200 | 24.75 | Prometheus metrics 可读取 | `03_metrics.json` |
| 4 | 基础接口 | openapi | GET | `/openapi.json` | **PASS** | 200 | 29.14 | OpenAPI 可读取；发现关键路径: /v1/models, /v1/chat/completions, /v1/responses, /v1/messages, /tokenize, /detokenize, /version, /metrics | `04_openapi.json` |
| 5 | Tokenizer | tokenize | POST | `/tokenize` | **PASS** | 200 | 8.27 | tokenize 成功，count=20，max_model_len=131072 | `05_tokenize.json` |
| 6 | Tokenizer | detokenize | POST | `/detokenize` | **PASS** | 200 | 6.50 | detokenize 与原文完全一致 | `06_detokenize.json` |
| 7 | OpenAI Chat | chat_nonstream | POST | `/v1/chat/completions` | **PASS** | 200 | 806.02 | OpenAI Chat Completions 非流式结构正常 | `07_chat_nonstream.json` |
| 8 | OpenAI Chat | chat_stream | POST | `/v1/chat/completions` | **PASS** | 200 | 833.21 | 流式协议与完成事件符合预期 | `08_chat_stream.json` |
| 9 | OpenAI Chat | chat_thinking_off | POST | `/v1/chat/completions` | **PASS** | 200 | 5963.22 | Thinking OFF：直接返回 content，reasoning 为空 | `09_chat_thinking_off.json` |
| 10 | OpenAI Chat | chat_thinking_on | POST | `/v1/chat/completions` | **PASS** | 200 | 48459.36 | Thinking ON：检测到 reasoning/think 内容 | `10_chat_thinking_on.json` |
| 11 | OpenAI Chat | chat_tool_call | POST | `/v1/chat/completions` | **PASS** | 200 | 1443.19 | OpenAI Chat tool_calls 结构正常 | `11_chat_tool_call.json` |
| 12 | Codex / Responses | responses_nonstream | POST | `/v1/responses` | **PASS** | 200 | 915.18 | OpenAI Responses 非流式结构正常 | `12_responses_nonstream.json` |
| 13 | Codex / Responses | responses_stream | POST | `/v1/responses` | **PASS** | 200 | 962.55 | 流式协议与完成事件符合预期 | `13_responses_stream.json` |
| 14 | Codex / Responses | responses_tool_call | POST | `/v1/responses` | **PASS** | 200 | 1618.87 | Responses function_call 结构正常 | `14_responses_tool_call.json` |
| 15 | Claude / Anthropic | anthropic_nonstream | POST | `/v1/messages` | **PASS** | 200 | 6572.18 | Anthropic Messages 非流式结构正常 | `15_anthropic_nonstream.json` |
| 16 | Claude / Anthropic | anthropic_stream | POST | `/v1/messages` | **PASS** | 200 | 7493.60 | 流式协议与完成事件符合预期 | `16_anthropic_stream.json` |
| 17 | Claude / Anthropic | anthropic_tool_use | POST | `/v1/messages` | **FAIL** | 200 | 18434.22 | 未返回 content[].type=tool_use；stop_reason=max_tokens | `17_anthropic_tool_use.json` |

## 三、培训解读

### 1. OpenAI Chat Completions
不能只看 `/v1/chat/completions` 是否返回 200。至少要同时验证普通响应、SSE 流式响应以及 `message.tool_calls[]` 是否能够结构化返回。

### 2. Codex / Responses
Codex 兼容性重点检查 `/v1/responses`。仅端点存在还不够，需要验证 `object=response`、Responses SSE 事件以及 `output[].type=function_call`。

### 3. Claude / Anthropic Messages
Anthropic 兼容性重点检查 `/v1/messages`，包括标准 `type=message`、SSE 的 `message_start/message_stop`，以及工具调用 `content[].type=tool_use`。

### 4. Thinking 开关
`chat_thinking_off` 与 `chat_thinking_on` 用同类推理题进行 A/B 对照。关闭思考时应直接输出答案；开启思考时若服务配置了 reasoning parser，应能观察到独立 reasoning 字段或思考块。

### 5. Tokenizer
`/tokenize` 对应文本编码为 token IDs，`/detokenize` 将 token IDs 还原为文本。两者可用于核实上下文长度声明、输入 token 数以及模型服务端 tokenizer 是否一致。

### 6. Metrics
`/metrics` 是服务级 Prometheus 指标，不等同于单次请求返回的 usage。培训时可重点展示并发、KV Cache、TTFT、生成吞吐、请求完成原因等指标。
