# Qwen3.6 内网模型服务 API / Agent / Vision 实测报告

> 当前基线：`20260930_095033`（2026-09-30）  
> 脚本：`2026-09-30-r4`  
> 模型：`qwen3.6`；Context 配置：`131072`；vLLM：`0.23.0`

## 1. 结论

本轮 29 项：**28 PASS、1 SKIP、0 FAIL、0 ERROR**。所有实际执行请求一次成功，本轮没有触发真实网络重试。

已确认：OpenAI Chat、Responses、Anthropic Messages 的文本/SSE/Tool Loop；Chat/Responses/Anthropic Vision；Chat 多图、Vision SSE、Vision + Tool Calling；tokenize/detokenize/models/version/metrics/openapi。

仍需强调：Anthropic `thinking.type=disabled` 未观察到生效；128K 长上下文稳定性与 Codex CLI / Claude Code 实机尚未专项验收。

## 2. 当前运行摘要

The requested file reference is not currently visible. Use files.search or files.list to rediscover the file, then retry with a returned ref_id or file_id.

## 3. 重要解释

### Thinking
OFF/ON 都是“开关能力 PASS”，但本轮两条都 `finish_reason=length`；ON 甚至最终 `content=null`。不能把它们写成回答质量或完整性 PASS。

### Responses Vision
旧 HTTP 400 已定位为请求漏掉 OpenAPI 必填 `detail`。r4 使用 `detail:"auto"` 后 HTTP 200 且 Ground Truth 全匹配，因此正式更新为 PASS。

### Anthropic
本轮 Tool Use 与 Tool Result 完整 PASS，但 `thinking.type=disabled` 仍返回 thinking，是当前最明确兼容差异。

### 性能边界
Chat SSE TTFT 约 0.72 s；Responses SSE TTFT 约 1.08 s；多图 Vision 单次 54.21 s。以上只是一轮能力验收伴随观测，不替代 P50/P95/P99 和并发压测。

## 4. 下一步
性能与共享服务体验统一转入 model-metric：并发、waiting、TTFT、输出 TPS、KV Cache、长上下文和实例覆盖。

详细案例：`docs/cases/model-metric-api-observability.md`。