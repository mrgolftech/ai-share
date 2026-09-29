# Qwen3.6 内网 API 实测材料（2026-09-29）

## 培训成果入口

- [测试报告：Qwen3.6 内网模型服务 API 实测报告](reports/qwen36_api_test_report_20260929.md)
- [培训讲义：从一个 HTTP 请求理解内网大模型服务](../../docs/chapters/01-intranet-qwen-api.md)
- [官方参考资料](../../docs/references/qwen36-api-sources.md)
- [实测证据摘录](results/20260929_105316/evidence.md)
- [测试汇总](results/20260929_105316/summary.md)
- [机器可读结果](results/20260929_105316/manifest.json)
- [可复用测试脚本](qwen_api_training_test.py)

## 测试对象

- 对外模型 ID：qwen3.6
- 模型目录标识：Qwen3.6-35B-A3B-w8a8-ascend
- 服务返回的最大上下文：131072 tokens
- vLLM 版本：0.23.0
- 部署背景：两个华为昇腾节点（部署信息来自现场配置；公开仓库已脱敏真实 API 地址）

## 本次测试结论

本轮共执行 17 个测试项，其中 16 项通过，1 项未通过。

| 能力 | 结论 | 证据 |
|---|---|---|
| /v1/models | PASS | 返回 qwen3.6，max_model_len=131072 |
| /version | PASS | 返回 0.23.0 |
| /metrics | PASS | 可读取 Prometheus/vLLM metrics |
| /openapi.json | PASS | 可发现 Chat、Responses、Messages、tokenize/detokenize 等路径 |
| /tokenize | PASS | 测试文本返回 20 tokens，max_model_len=131072 |
| /detokenize | PASS | Token IDs 可完整还原原文 |
| OpenAI Chat 非流式 | PASS | 标准 chat.completion |
| OpenAI Chat SSE | PASS | 流式完成事件正常 |
| Thinking OFF | PASS | reasoning=null，直接输出答案 |
| Thinking ON | PASS（但被长度截断） | 检测到 reasoning；1024 输出 token 用尽，finish_reason=length |
| OpenAI Chat Tool Calling | PASS | 标准 message.tool_calls[] |
| OpenAI Responses 非流式 | PASS | 标准 object=response |
| OpenAI Responses SSE | PASS | 标准 response.* 事件 |
| Responses Function Calling | PASS | output[].type=function_call |
| Anthropic Messages 非流式 | PASS | 标准 type=message |
| Anthropic Messages SSE | PASS | message_start / message_stop 正常 |
| Anthropic Tool Use | **未通过** | HTTP 200，但未出现 content[].type=tool_use；stop_reason=max_tokens |

## 关键工程结论

### OpenAI Chat Completions

普通请求、SSE、Thinking 开关和结构化 tool_calls 均已通过，本轮可以确认 OpenAI Chat Completions 兼容链路工作。

### OpenAI Responses / Codex

/v1/responses 的非流式、SSE 与 function_call 均已通过，可作为后续 Codex CLI 实机接入的协议基础。

“Responses 核心协议通过”不等于“Codex CLI 全流程已经验收”，还需要继续测试 Shell、文件、Git、多轮工具、错误恢复和长任务稳定性。

### Anthropic / Claude

/v1/messages 的普通响应和 SSE 均通过，但请求 thinking.type=disabled 后仍观察到 thinking / thinking_delta；Tool Use 测试最终达到 max_tokens，未产生标准 tool_use。

因此目前只能判定为：

> **Anthropic Messages 文本与流式协议通过；Thinking 关闭和 Tool Use 当前存在兼容问题，整体 PARTIAL。**

### Thinking A/B

同类逻辑题单次实测：

- Thinking OFF：约 5.96 s，178 completion tokens，完整回答；
- Thinking ON：约 48.46 s，1024 completion tokens，最终被长度上限截断。

这组数据适合作为“Thinking 会增加 Token 与时延预算”的行为案例，但不是严格性能基准，不应推广为固定倍数。

## 当前材料是否足够用于培训

已经足够支撑第一版 API 培训章节，覆盖：

1. HTTP GET / POST、JSON、Header、Request / Response、Status Code；
2. 非流式与 SSE；
3. Tokenize / Detokenize；
4. Token 与 Context Window；
5. Thinking ON / OFF；
6. Tool Calling；
7. models、version、metrics、openapi.json；
8. OpenAI Chat、OpenAI Responses/Codex、Anthropic Messages 三套协议实测。

后续建议补充，但不阻塞当前培训材料：

- Tool Result 回灌后的完整闭环；
- 连续 5～10 轮工具调用稳定性；
- Parallel Tool Calling；
- Anthropic Tool Use 重测；
- Codex CLI 和 Claude Code 实机接入；
- 131072 长上下文逐级验证；
- 重复压测形成平均值、P50、P95；
- Prefix Cache 开启前后对比。

## 安全说明

仓库是公开仓库，因此没有上传原始测试 ZIP。公开材料已对真实内网 API 地址脱敏，API Key 不落盘；完整 OpenAPI Schema 与原始 metrics 快照也未直接公开，只保留了培训需要的关键字段和指标摘录。
