# Qwen3.6 当前实测证据基线（2026-09-30）

> 当前培训能力结论只引用本目录。2026-09-29 结果已归档到 `../archive/`，只用于历史回归与排障教学。

## 1. 证据来源

- Run ID：`20260930_095033`
- 脚本：`2026-09-30-r4`
- 实际执行脚本 SHA256：`106727cae3e73dd7f5947e439a68b1be88b2d79c41f62413e5baa6b05ecb303b`
- 原始 ZIP SHA256：`89c1fe652cc8ac3a59967e1a7d0bde1d3fe4b019dcaa0a8551d6d62bef1c508e`
- 模型：`qwen3.6`；`max_model_len=131072`；`/version=0.23.0`
- 结果：**28 PASS / 1 SKIP / 0 FAIL / 0 ERROR**
- 所有实际请求 `attempts=1`，本轮没有依靠 retry 恢复。

## 2. 当前能力矩阵

| 能力 | 当前结论 | 证据边界 |
|---|---|---|
| OpenAI Chat / SSE | PASS | `CHAT_OK`、SSE TTFT 718.59 ms |
| Thinking OFF | PASS（开关） | `reasoning=null`；512 completion tokens 后 `length` |
| Thinking ON | PASS（开关） | reasoning 存在；1536 completion tokens 后 `length`，最终 `content=null` |
| Chat Tool Loop | PASS | `tool_calls` → Tool Result → grounded final answer |
| Responses / SSE | PASS | 标准 `object=response` 与 `response.*` SSE |
| Responses Tool Loop | PASS | `function_call` → `function_call_output` |
| Anthropic Messages / SSE | PASS | 标准 Message / SSE |
| Anthropic Tool Loop | PASS | 本轮标准 `tool_use` 与 `tool_result` 完整 |
| Anthropic `thinking.type=disabled` | **兼容异常** | 仍出现 thinking block / delta |
| Chat Vision 单图 / SSE / 多图 | PASS | Ground Truth 全匹配 |
| Vision + Tool Calling | PASS | 视觉结果进入结构化 `tool_calls` |
| **Responses Vision** | **PASS** | `input_image + detail:"auto"`，HTTP 200，Ground Truth 全匹配 |
| Anthropic Vision | PASS | Base64 image Ground Truth 全匹配 |
| 公网 image_url | 未测 | 主动 SKIP |
| 128K 长上下文稳定性 | 未测 | 当前只确认服务声明 131072 |

## 3. 关键原始事实

### 普通 Chat
```json
{"object":"chat.completion","choices":[{"message":{"content":"CHAT_OK","reasoning":null},"finish_reason":"stop"}],"usage":{"prompt_tokens":18,"completion_tokens":3,"total_tokens":21}}
```
本轮耗时 `819.59 ms`。

### Streaming
- Chat SSE：总耗时 `795.45 ms`，TTFT `718.59 ms`。
- Responses SSE：总耗时 `1368.25 ms`，TTFT `1084.39 ms`。
- Vision SSE：总耗时 `1986.13 ms`，TTFT `1670.69 ms`。

### Thinking：PASS 不等于回答完整
OFF：`reasoning=false`，512 completion tokens，`finish_reason=length`。
ON：`reasoning=true`，1536 completion tokens，`finish_reason=length`，最终 `content=null`。
因此 PASS 只说明开关断言成立。

### Tool Loop
Chat、Responses、Anthropic 三套协议均完成 `Tool Call → Tool Result → Final Answer`。

### 多模态
Ground Truth：`AI TEST 2026`、3 红圆、2 蓝方块、绿色三角形右下。Chat、Responses、Anthropic 均正确；Chat 还通过多图与 Vision + Tool Calling。

Responses Vision 正确请求核心：
```json
{"type":"input_image","detail":"auto","image_url":"data:image/png;base64,..."}
```
历史 HTTP 400 来自旧测试缺少必填 `detail`，不是模型不支持 Vision。

## 4. 测试原则

`Endpoint → HTTP → Schema → 行为断言 → Ground Truth → Tool Loop`。

- SSE 必须重建 delta 并出现完成标记；
- Thinking 验证开关行为，不替代业务质量验收；
- Tool 必须有结构化函数名和 JSON 参数；
- Vision 必须对 Ground Truth，而不是只看 HTTP 200；
- 不同协议分别按 Chat / Responses / Anthropic Schema 验证。

## 5. 历史归档的教学价值

历史结果记录了 Thinking 判定器 bug、Vision Tool Schema 语义不清、Responses Vision 缺 `detail`、Anthropic 曾出现一次 Tool Use 结构不一致。这些不再描述当前能力，但非常适合讲“测试程序与协议也需要 Review”。