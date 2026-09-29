# Qwen3.6 内网 API 实测材料（2026-09-29）

## 测试对象

- 对外模型 ID：`qwen3.6`
- 模型目录标识：`Qwen3.6-35B-A3B-w8a8-ascend`
- 服务返回的最大上下文：`131072` tokens
- vLLM 版本：`0.23.0`
- 部署背景：两个华为昇腾节点（部署信息来自现场配置；本仓库公开版本已脱敏 API 地址）

## 本次测试结论

本轮共执行 17 个测试项，其中 16 项通过，1 项未通过。

| 能力 | 结论 | 证据 |
|---|---|---|
| `/v1/models` | PASS | 返回 `qwen3.6`，`max_model_len=131072` |
| `/version` | PASS | 返回 `0.23.0` |
| `/metrics` | PASS | 可读取 Prometheus/vLLM metrics |
| `/openapi.json` | PASS | 可发现 Chat、Responses、Messages、tokenize/detokenize 等路径 |
| `/tokenize` | PASS | 测试文本返回 20 tokens，`max_model_len=131072` |
| `/detokenize` | PASS | token IDs 可完整还原原文 |
| OpenAI Chat 非流式 | PASS | 标准 `chat.completion` |
| OpenAI Chat SSE | PASS | 流式完成事件正常 |
| Thinking OFF | PASS | `reasoning=null`，直接输出答案 |
| Thinking ON | PASS（但被长度截断） | 检测到独立 `reasoning`；1024 输出 token 用尽，`finish_reason=length` |
| OpenAI Chat Tool Calling | PASS | 标准 `message.tool_calls[]`，`finish_reason=tool_calls` |
| OpenAI Responses 非流式 | PASS | 标准 `object=response` |
| OpenAI Responses SSE | PASS | `response.created` → delta → `response.completed` |
| Responses Function Calling | PASS | `output[].type=function_call` |
| Anthropic Messages 非流式 | PASS | 标准 `type=message` |
| Anthropic Messages SSE | PASS | `message_start` / `message_stop` 正常 |
| Anthropic Tool Use | **未通过** | HTTP 200，但只输出 `thinking`，512 tokens 用尽，`stop_reason=max_tokens`，未出现 `content[].type=tool_use` |

## 关键工程结论

### 1. OpenAI Chat Completions：可以确认兼容

已经同时验证了普通请求、SSE 流式响应、Thinking 开关和结构化 `tool_calls`，因此不能只说“OpenAI 格式端点存在”，而可以说本轮实测中 **OpenAI Chat Completions 兼容链路通过**。

### 2. OpenAI Responses / Codex：可以确认核心协议通过

本轮同时验证了 `/v1/responses` 的非流式、标准 SSE 和 `function_call`。这比只验证 `/v1/responses` 返回 HTTP 200 更有意义，可作为后续 Codex CLI 实机接入测试的协议基础。

注意：这里的结论是“Responses 协议核心能力通过”，不等同于已经完成完整 Codex CLI 产品级兼容验收；真正接入 Codex 后，还需要继续验证连续多轮工具调用、错误恢复、长任务稳定性等。

### 3. Anthropic / Claude：当前应写为“部分兼容”

`/v1/messages` 的普通响应和 SSE 均通过，但 Tool Use 未通过本轮测试。请求里已经设置 `thinking.type=disabled`，实际响应仍然持续输出 `thinking`，最终在 512 tokens 达到上限，未产生标准 `tool_use`。

因此培训中不能写“Claude/Anthropic 工具调用已支持”，更准确的表述是：

> Anthropic Messages 文本与流式协议已通过实测；Tool Use 在当前服务配置下存在 Thinking 关闭不生效/工具调用未落地的问题，需要进一步验证。

### 4. Thinking 开关差异非常明显

同类逻辑题：

- Thinking OFF：约 `5.96 s`，178 completion tokens，完整回答；
- Thinking ON：约 `48.46 s`，1024 completion tokens，且答案因长度上限被截断。

这个结果非常适合作为培训中“Thinking 会增加时间和 Token 成本”的现场实测证据。需要注意，这不是严格性能基准，因为两次请求的 `max_tokens` 不同，且只执行一次；它只能作为行为差异案例，不宜直接推广成固定倍数。

## 当前材料是否足够用于培训

**足够支撑第一版 API 培训章节。** 当前材料已经覆盖：

1. HTTP GET/POST；
2. JSON Request/Response；
3. 非流式与 SSE；
4. Tokenize/Detokenize；
5. Thinking ON/OFF；
6. Tool Calling；
7. `/models`、`/version`、`/metrics`、`/openapi.json`；
8. OpenAI Chat、OpenAI Responses/Codex、Anthropic Messages 三类协议的实测对比。

后续建议补充，但不阻塞当前培训材料：

- Tool result 回灌后的完整闭环（Chat / Responses / Anthropic）；
- 连续 5～10 轮工具调用稳定性；
- Parallel Tool Calling；
- Claude Tool Use 重测（提高 token 上限，并进一步确认为什么 `thinking.type=disabled` 未生效）；
- Codex CLI 和 Claude Code 的真实客户端接入；
- 长上下文 131072 的宣称验证与 TTFT/吞吐变化；
- 同一测试重复多次，形成平均值/P50/P95，避免把单次时延当作性能结论。

## 文件说明

- `qwen_api_training_test.py`：测试脚本。
- `results/20260929_105316/summary.md`：脚本自动生成的原始汇总。
- `results/20260929_105316/manifest.json`：机器可读测试结果。
- `results/20260929_105316/evidence_records.json`：公开脱敏后的关键请求/响应、SSE、metrics 摘录与 OpenAPI 路径证据。

> 公开仓库版本对真实内网 API 地址做了脱敏；API Key 在测试脚本落盘时已自动打码。
