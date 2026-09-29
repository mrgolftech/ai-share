# Qwen3.6 API 实测证据摘录

> 测试时间：2026-09-29。真实内网 API 地址已脱敏；API Key 已打码。完整原始 ZIP 不提交到公开仓库，本文件保留培训最有价值的请求/响应字段与 SSE 事件。

## 1. 模型与部署信息

```json
{
  "id": "qwen3.6",
  "owned_by": "vllm",
  "root": "/models/Qwen3.6-35B-A3B-w8a8-ascend",
  "max_model_len": 131072
}
```

`GET /version`：

```json
{"version":"0.23.0"}
```

Chat 返回的 `system_fingerprint` 为：

```text
vllm-0.23.0-tp2-78580a24
```

## 2. Tokenize / Detokenize

请求：

```json
{
  "model": "qwen3.6",
  "prompt": "你好，Qwen3.6。这是一段用于 tokenizer 接口验证的中文测试文本。",
  "add_special_tokens": false,
  "return_token_strs": true
}
```

关键响应：

```json
{
  "count": 20,
  "max_model_len": 131072,
  "tokens": [109266,3709,48,16451,18,13,21,1710,104749,96460,98618,44424,220,108622,103838,95726,99986,99449,109120,1710]
}
```

将上述 token IDs 提交给 `/detokenize` 后：

```json
{
  "prompt": "你好，Qwen3.6。这是一段用于 tokenizer 接口验证的中文测试文本。"
}
```

结论：Tokenize / Detokenize 闭环通过。

## 3. OpenAI Chat Completions

### 非流式

请求：

```json
{
  "model": "qwen3.6",
  "messages": [{"role":"user","content":"请只回答：CHAT_OK"}],
  "temperature": 0,
  "max_tokens": 128,
  "stream": false,
  "chat_template_kwargs": {"enable_thinking": false}
}
```

关键响应：

```json
{
  "object": "chat.completion",
  "message": {
    "role": "assistant",
    "content": "CHAT_OK",
    "reasoning": null
  },
  "finish_reason": "stop",
  "usage": {
    "prompt_tokens": 18,
    "completion_tokens": 3,
    "total_tokens": 21
  }
}
```

实测耗时：`806.02 ms`。

### SSE 流式

```text
data: {"object":"chat.completion.chunk","choices":[{"delta":{"role":"assistant","content":""},"finish_reason":null}]}

data: {"object":"chat.completion.chunk","choices":[{"delta":{"content":"CHAT"},"finish_reason":null}]}

data: {"object":"chat.completion.chunk","choices":[{"delta":{"content":"_OK"},"finish_reason":"stop"}]}

data: [DONE]
```

结论：OpenAI Chat 非流式与 SSE 均通过。

## 4. Thinking ON / OFF 对照

同类逻辑题实测：

| 模式 | 参数 | 耗时 | completion tokens | reasoning | finish_reason |
|---|---|---:|---:|---|---|
| OFF | `enable_thinking=false` | 5963.22 ms | 178 | `null` | `stop` |
| ON | `enable_thinking=true` | 48459.36 ms | 1024 | 有 | `length` |

Thinking OFF 能完整回答；Thinking ON 产生独立 `reasoning`，但 1024 输出 token 全部耗尽，最终答案被截断。

该数据适合说明 Thinking 会显著增加 Token 与响应时间，但这只是单次行为案例，不能当作严格性能倍数。

## 5. OpenAI Chat Tool Calling

请求核心：

```json
{
  "model": "qwen3.6",
  "messages": [{"role":"user","content":"查询北京天气，必须调用 get_weather 工具，不要自己猜。"}],
  "chat_template_kwargs": {"enable_thinking": false},
  "tools": [{
    "type": "function",
    "function": {
      "name": "get_weather",
      "parameters": {
        "type": "object",
        "properties": {"city":{"type":"string"}},
        "required": ["city"]
      }
    }
  }],
  "tool_choice": "required"
}
```

关键响应：

```json
{
  "message": {
    "role": "assistant",
    "content": "",
    "tool_calls": [{
      "type": "function",
      "function": {
        "name": "get_weather",
        "arguments": "{\"city\": \"北京\"}"
      }
    }],
    "reasoning": null
  },
  "finish_reason": "tool_calls"
}
```

实测耗时：`1443.19 ms`。标准 `message.tool_calls[]` 结构通过。

## 6. OpenAI Responses / Codex

### 非流式

请求：

```json
{
  "model": "qwen3.6",
  "input": "请只回答：RESPONSES_OK",
  "max_output_tokens": 256,
  "reasoning": {"effort":"none"}
}
```

响应核心：

```json
{
  "object": "response",
  "status": "completed",
  "output": [{
    "type": "message",
    "role": "assistant",
    "content": [{
      "type": "output_text",
      "text": "RESPONSES_OK"
    }]
  }],
  "usage": {
    "input_tokens": 20,
    "output_tokens": 5,
    "total_tokens": 25
  }
}
```

实测耗时：`915.18 ms`。

### Responses SSE

关键事件顺序：

```text
event: response.created
event: response.in_progress
event: response.output_item.added
event: response.content_part.added
...
event: response.content_part.done
event: response.output_item.done
event: response.completed
```

实测耗时：`962.55 ms`。

### Function Calling

请求使用 Responses 风格的扁平工具定义：

```json
{
  "type": "function",
  "name": "get_weather",
  "parameters": {
    "type": "object",
    "properties": {"city":{"type":"string"}},
    "required": ["city"]
  }
}
```

关键响应：

```json
{
  "object": "response",
  "status": "completed",
  "output": [{
    "type": "function_call",
    "name": "get_weather",
    "arguments": "{\"city\": \"北京\"}",
    "status": "completed"
  }]
}
```

实测耗时：`1618.87 ms`。

结论：本轮实测中，Responses 的非流式、标准 SSE 与 function_call 全部通过，可作为 Codex 协议接入的基础证据；仍需另做真实 Codex CLI 产品级验证。

## 7. Anthropic / Claude Messages

### 非流式 Messages

请求：

```json
{
  "model": "qwen3.6",
  "max_tokens": 256,
  "thinking": {"type":"disabled"},
  "messages": [{"role":"user","content":"请只回答：CLAUDE_OK"}]
}
```

返回是标准 Anthropic `type=message` 结构，最终文本为 `CLAUDE_OK`，`stop_reason=end_turn`。

但有一个重要兼容性现象：即使请求明确设置 `thinking.type=disabled`，响应仍然先出现 `content[].type=thinking`，之后才出现文本块。该请求输出 201 tokens，耗时 `6572.18 ms`。

### Anthropic SSE

流式事件结构通过：

```text
event: message_start
event: content_block_start
event: content_block_delta
...
event: content_block_stop
event: message_delta
event: message_stop
```

但 `content_block_start` 的首块类型仍为 `thinking`，随后持续输出 `thinking_delta`。因此“协议流式兼容”和“关闭思考参数生效”必须分开判断。

### Tool Use：当前未通过

请求核心：

```json
{
  "model": "qwen3.6",
  "max_tokens": 512,
  "thinking": {"type":"disabled"},
  "messages": [{"role":"user","content":"查询北京天气，必须使用 get_weather 工具。"}],
  "tools": [{
    "name": "get_weather",
    "input_schema": {
      "type": "object",
      "properties": {"city":{"type":"string"}},
      "required": ["city"]
    }
  }],
  "tool_choice": {"type":"any"}
}
```

模型在 thinking 中已经明确推导出：

```json
{"name":"get_weather","parameters":{"city":"北京"}}
```

但一直没有产生标准：

```json
{"type":"tool_use", ...}
```

最终结果：

```json
{
  "stop_reason": "max_tokens",
  "usage": {
    "input_tokens": 283,
    "output_tokens": 512
  }
}
```

实测耗时：`18434.22 ms`。

因此当前应判定：**Anthropic Messages 文本与 SSE 协议通过，但 Tool Use 未通过；同时 `thinking.type=disabled` 在当前服务上未观察到生效。**

## 8. OpenAPI 与 Metrics

`/openapi.json` 实测发现以下关键路径：

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

`/metrics` 返回 Prometheus/vLLM 指标，包括本培训后续可重点讲解的：

```text
vllm:num_requests_running
vllm:num_requests_waiting
vllm:kv_cache_usage_perc
vllm:prefix_cache_queries_total
vllm:prefix_cache_hits_total
vllm:prompt_tokens_total
```

本次快照中还能看到 `enable_prefix_caching="False"`、`gpu_memory_utilization="0.85"`、`num_gpu_blocks="487"` 等服务配置/运行指标。

## 9. 本轮协议结论

| 协议 | 结论 |
|---|---|
| OpenAI Chat Completions | PASS |
| OpenAI Responses / Codex | PASS（核心协议） |
| Anthropic Messages / Claude | PARTIAL |

这里的 PASS 指本测试矩阵覆盖的协议能力通过，不等于已经完成 Codex CLI / Claude Code 的真实客户端全流程验收。
