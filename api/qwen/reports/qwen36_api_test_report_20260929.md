# Qwen3.6 内网模型服务 API、Agent 与多模态实测报告

> 日期：2026-09-29  
> 测试对象：部门内网 qwen3.6  
> 证据：基础兼容性测试 + v2 全面测试 + 失败项专项重测

## 1. 结论摘要

当前内网 qwen3.6 服务端配置 Context 为 131072，服务版本 0.23.0。

三轮递进测试确认：

- OpenAI Chat：文本、SSE、Thinking、Tool Calling、Tool Result 闭环通过；
- OpenAI Responses：文本、SSE、Function Call、Function Call Output 闭环通过；
- Anthropic Messages：文本、SSE、count_tokens、Tool Use、Tool Result 闭环通过；
- Vision：OpenAI Chat 单图、Vision SSE、多图、Vision + Tool Calling、Anthropic Base64 图片通过；
- Anthropic thinking.type=disabled 未观察到真正关闭 Thinking；
- Responses Vision 需按服务 OpenAPI 补 detail 字段后再复测；
- Thinking 存在明显长尾，重任务可能短时间拖慢后续推理请求；
- 131072 长上下文稳定性和真实 Codex/Claude Code 客户端仍需专项验证。

因此当前内网服务已经具备较完整的文本、多模态和 Agent 基础协议能力，但“协议能跑通”仍不等于“共享服务体验稳定”。

## 2. 当前部署事实

| 项目 | 当前实测/已知信息 |
|---|---|
| 模型 ID | qwen3.6 |
| 模型目录 | Qwen3.6-35B-A3B-w8a8-ascend |
| 服务 Context | 131072 |
| vLLM version | 0.23.0 |
| OpenAPI paths | 23 |
| 计算平台 | 两个华为昇腾节点 |
| Prefix Cache | 初始快照 enable_prefix_caching=False |

官方模型结构、参数和理论 Context 继续引用 Qwen 官方资料；当前部署能力以本报告实测为准。

## 3. 基础接口

/models、/version、/metrics、/openapi.json、/tokenize、/detokenize 和 /v1/messages/count_tokens 均通过。

OpenAPI 实际还暴露 /health、/ping、/load、Responses get/cancel 等服务接口。

## 4. OpenAI Chat

### 4.1 文本与流式

普通 Chat 与 SSE 均通过。简单 SSE 请求总耗时约 2.37 s，首个文本片段约 1.83 s。

### 4.2 Thinking

专项重测修复了全面测试中的判定器 bug。

Thinking OFF：

- 4.75 s / 105 tokens / stop
- 20.01 s / 512 tokens / length
- 6.35 s / 146 tokens / stop

三次均未出现独立 reasoning。

Thinking ON：

- 43.48 s / 1331 tokens / stop
- 50.90 s / 1536 tokens / length
- 298.59 s / 1536 tokens / length

三次均出现 reasoning。

工程结论：Thinking 是计算预算，不是简单的增强按钮；它增加 Token、时间和尾延迟，而且较容易挤占最终回答空间。

### 4.3 Tool Loop

模型先返回 get_weather(city=北京)，程序回灌 23℃、晴，模型最终基于 Tool Result 完成回答。

结论：Chat Tool Call → Tool Result → Final Answer PASS。

## 5. Responses / Codex 核心协议

普通 Response、SSE、function_call 和 function_call_output 回灌均通过。

因此当前服务具备继续接入 Codex 类 Agent 的核心协议基础，但真实 Codex CLI 的 Shell、File、Git、多轮长任务仍需实机验收。

## 6. Anthropic Messages / Claude

普通 Messages、SSE、count_tokens、Tool Use 和 Tool Result 闭环均通过。

旧测试中 Tool Use 未形成，是因为 Thinking 持续消耗完 512 tokens。提高预算后 Tool Use 和 Tool Result 均通过。

真正的兼容异常是：请求 thinking.type=disabled 后仍出现 thinking block / thinking_delta。

所以当前表述应是：

> Anthropic Tool Loop 支持；Thinking disabled 兼容存在异常。

## 7. Vision / 多模态

测试脚本生成有标准答案的图片，用 OCR、颜色、数量、位置和多图区分作为 Ground Truth。

OpenAI Chat 已通过：

- Base64 单图
- Vision SSE
- 多图
- OCR
- 数量与颜色
- 空间位置

Anthropic Base64 Image 也通过。

### 7.1 Vision + Tool Calling

第一次自动判定 FAIL 的原因是工具字段 text 语义不清，而不是模型没有识别图片。

改为 top_text 并明确“逐字 OCR 顶部英文”后，专项重测 3/3 PASS：

~~~json
{
  "red_circles": 3,
  "blue_squares": 2,
  "green_triangle_position": "bottom-right",
  "top_text": "AI TEST 2026"
}
~~~

这说明工具 Schema 本身也是 Prompt 的一部分。

### 7.2 Responses Vision

连续 HTTP 400 不是网络超时。服务 OpenAPI 明确要求 ResponseInputImageParam 同时包含：

~~~json
{
  "type": "input_image",
  "detail": "auto",
  "image_url": "data:image/png;base64,..."
}
~~~

前两版测试漏了必填 detail，错误 Body 也显示 Field required。因此现在只能标为“请求修正后待复测”，不能写成“不支持图片”。

## 8. 服务稳定性观察

第三轮 Thinking ON 耗时约 298.6 s。其后：

- /version 约 4.5 ms；
- 简单 Chat PING 却约 70.18 s；
- 再稍后又恢复约 0.81 s。

因此 HTTP 服务和网络仍然可达，但推理路径短时间非常慢。

当前更合理的候选解释包括：

- 推理队列；
- 计算资源持续占用；
- 重任务结束/取消后的资源释放滞后；
- 实例调度不均。

这不是根因证明，但明显不能简单归因为普通网络断线。

## 9. 当前最终矩阵

| 能力 | 状态 |
|---|---|
| Models / Version / Metrics / OpenAPI | PASS |
| Tokenize / Detokenize | PASS |
| Anthropic count_tokens | PASS |
| OpenAI Chat Text / SSE | PASS |
| Chat Thinking OFF / ON | PASS，ON 尾延迟明显 |
| Chat Tool Loop | PASS |
| Responses Text / SSE | PASS |
| Responses Tool Loop | PASS |
| Anthropic Messages / SSE | PASS |
| Anthropic Tool Loop | PASS |
| Anthropic Thinking Disabled | 兼容异常 |
| Chat Vision 单图 / SSE / 多图 | PASS |
| Vision + Tool Calling | PASS |
| Anthropic Vision | PASS |
| Responses Vision | 待修正请求后复测 |
| 远程公网 image_url | 未测 |
| 128K 长上下文稳定性 | 未专项验证 |
| Codex CLI / Claude Code 实机 | 未测 |

## 10. 培训应强调的方法

真正的能力验证链应该是：

~~~text
Endpoint
→ HTTP
→ Request / Response Schema
→ 模型行为
→ Ground Truth
→ Tool Call
→ Tool Result
→ Final Answer
~~~

本轮还证明了一点：

> 自动化测试本身也要 Review。

Thinking OFF 的一次假失败来自测试判定器 bug；Vision Tool 的一次假失败来自字段语义不清。工程师仍然需要判断“测试失败是不是一个合理的失败”。

## 11. 后续验证

1. 使用 detail:"auto" 的正确 Responses Vision 请求复测；
2. Codex CLI 实机接入；
3. Claude Code 实机接入；
4. 4K / 16K / 60K / 100K+ 长上下文；
5. 并发 P50/P95/P99；
6. Prefix Cache 开启前后对比；
7. 重 Thinking 请求后的任务取消、队列和资源恢复行为。
