# Qwen3.6 内网 API / Agent / Vision 实测材料

## 当前入口

- 最终实测报告：reports/qwen36_api_test_report_20260929.md
- 培训讲义：../../docs/chapters/01-intranet-qwen-api.md
- v2 与专项重测证据：results/20260929_v2/evidence.md
- 第一轮基础证据：results/20260929_105316/evidence.md
- 官方参考资料：../../docs/references/qwen36-api-sources.md
- 第一版脚本：qwen_api_training_test.py
- 全面测试脚本：qwen_api_training_test_v2.py
- 失败项专项重测：qwen_failed_retest.py

## 当前部署

- 模型 ID：qwen3.6
- 模型目录：Qwen3.6-35B-A3B-w8a8-ascend
- Context：131072
- vLLM：0.23.0
- 两个华为昇腾节点
- OpenAPI：23 paths

## 当前能力矩阵

| 能力 | 结论 |
|---|---|
| Models / Version / Metrics / OpenAPI | PASS |
| Tokenize / Detokenize | PASS |
| Anthropic count_tokens | PASS |
| OpenAI Chat Text / SSE | PASS |
| Chat Thinking OFF / ON | PASS，ON 尾延迟明显 |
| Chat Tool Call + Result | PASS |
| Responses Text / SSE | PASS |
| Responses Function Call + Output | PASS |
| Anthropic Messages / SSE | PASS |
| Anthropic Tool Use + Result | PASS |
| Anthropic thinking.type=disabled | 兼容异常 |
| Chat Vision 单图 / SSE / 多图 | PASS |
| Vision + Tool Calling | PASS，专项重测 3/3 |
| Anthropic Vision | PASS |
| Responses Vision | 待按 OpenAPI Schema 修正复测 |
| 128K 长上下文稳定性 | 未专项验证 |

## 本轮最重要的修正

1. Anthropic Tool Use 实际支持；旧失败来自 Thinking 消耗完输出预算。
2. Vision 已是现网实测能力，不再标记为“未验证”。
3. Vision + Tool Calling 修正 Schema 后 3/3 PASS。
4. Responses Vision 的 HTTP 400 暂不能解释为“不支持”，因为旧请求漏了必填 detail 字段。
5. Thinking 专项复测显示 43～299 s 的明显长尾，并可能短时间拖慢后续简单推理。

## 材料状态

模块一已达到：**可用于培训**。

后续主要补 Responses Vision 正确请求、长上下文与性能专项基准、Codex CLI / Claude Code 实机和 PPT 视觉化。


## 测试脚本版本识别

全面测试脚本自 `2026-09-30-r3` 起，会在启动时打印：

```text
Script   : 2026-09-30-r3 sha256=...
```

同时将脚本版本和 SHA256 写入 `environment.json`，用于避免本地旧脚本与仓库最新版混淆。

本次还增强了 Anthropic Tool Use 诊断：

- 若 `stop_reason=tool_use`；
- 但 `content[]` 中没有标准 `type=tool_use` block；

仍判 FAIL，并明确记录为“协议结构不一致”，不会因为 `stop_reason` 看起来正确就误判 PASS。

注意：`SKIP` 表示按设计未执行，不等于 FAIL。
