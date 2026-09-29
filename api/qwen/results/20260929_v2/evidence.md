# Qwen3.6 API v2 与专项重测证据摘录（2026-09-29）

> 公开仓库脱敏版。真实内网地址、API Key 和大体量原始响应不公开上传。结论来自基础测试、全面 v2 测试和失败项专项重测。

## 1. 当前部署

- 模型 ID：qwen3.6
- 模型目录：Qwen3.6-35B-A3B-w8a8-ascend
- 服务端 max_model_len：131072
- /version：0.23.0
- OpenAPI：23 paths
- 现场部署：两个华为昇腾节点

## 2. 基础接口

/models、/version、/metrics、/openapi.json、/tokenize、/detokenize、/v1/messages/count_tokens 均通过。

Tokenize 测试文本返回 20 tokens，Detokenize 可完整还原原文。

## 3. 三套 Agent Tool Loop

OpenAI Chat、OpenAI Responses、Anthropic Messages 三套协议均已验证到：

~~~text
Tool Call
→ 模拟真实工具执行
→ Tool Result 回灌
→ Final Answer
~~~

天气测试中，模型调用 get_weather(city=北京)，回灌 23℃、晴 后，三套协议均能基于工具结果完成最终回答。

因此当前不是“只支持函数调用”，而是三套基础 Agent Tool Loop 均 PASS。

## 4. Anthropic 结论修正

旧测试 max_tokens=512 时，Thinking 持续消耗输出预算，最终 stop_reason=max_tokens，没有来得及形成 tool_use。

v2 提高预算后：

- Tool Use：PASS
- Tool Result：PASS
- Final Answer：PASS

但请求 thinking.type=disabled 后仍观察到 thinking block / thinking_delta。

最终结论：Anthropic Tool Loop PASS；thinking.type=disabled 当前存在兼容异常。

## 5. Vision / 多模态

测试图由脚本自动生成，有明确 Ground Truth。

第一张：

- AI TEST 2026
- 3 个红色圆形
- 2 个蓝色方块
- 绿色三角形位于右下

第二张：

- SECOND IMAGE
- 4 个紫色方块
- 1 个橙色圆形

已通过：

- OpenAI Chat Base64 单图
- Vision SSE
- OpenAI Chat 多图
- OCR、数量、颜色、空间位置
- Anthropic Base64 Image
- Vision + Tool Calling

单图关键结果：

~~~json
{
  "red_circles": 3,
  "blue_squares": 2,
  "green_triangle_position": "bottom-right",
  "text": "AI TEST 2026"
}
~~~

## 6. Vision + Tool Calling 的假失败

第一次工具字段名 text 含义模糊，模型把它填成图片描述，因此自动判定 FAIL；但数量和位置实际上正确。

专项重测把字段改为 top_text，并明确要求逐字 OCR 顶部英文。

3 次重测全部 PASS，约 4.18 s、3.73 s、6.75 s：

~~~json
{
  "red_circles": 3,
  "blue_squares": 2,
  "green_triangle_position": "bottom-right",
  "top_text": "AI TEST 2026"
}
~~~

这说明 Tool Schema 本身也是 Prompt 的一部分。

## 7. Responses Vision 当前状态

全面测试和专项重测都得到 HTTP 400，但不是网络超时。

进一步对照服务自身 /openapi.json，ResponseInputImageParam 要求：

~~~json
{
  "type": "input_image",
  "detail": "auto",
  "image_url": "data:image/png;base64,..."
}
~~~

detail 是必填字段，image_url 应是字符串。前两版测试请求漏掉 detail，错误 Body 也出现：

~~~text
ResponseInputImageParam / detail
Field required
~~~

因此不能写成“Responses 不支持图片”。

当前状态：待使用符合当前 OpenAPI Schema、带 detail:"auto" 的请求重新验证。

## 8. Thinking 专项重测

Thinking OFF：3/3 PASS。

| # | 耗时 | Completion Tokens | Finish |
|---:|---:|---:|---|
| 1 | 4.75 s | 105 | stop |
| 2 | 20.01 s | 512 | length |
| 3 | 6.35 s | 146 | stop |

Thinking ON：3/3 检测到 reasoning。

| # | 耗时 | Completion Tokens | Finish |
|---:|---:|---:|---|
| 1 | 43.48 s | 1331 | stop |
| 2 | 50.90 s | 1536 | length |
| 3 | 298.59 s | 1536 | length |

结论：Thinking 开关有效，但 ON 模式存在明显长尾，而且容易耗尽较高输出预算。

## 9. 网络还是推理资源？

三轮开始前简单 PING Chat：

- 846.71 ms
- 814.63 ms
- 790.96 ms

第三轮 Thinking ON 约 298.6 s。紧接着：

- /version 仍约 4.5 ms
- 简单 PING Chat 却约 70.18 s

再经过一段时间，简单 Chat 恢复约 0.81 s。

这个现象更符合推理队列、计算资源持续占用或任务清理滞后，而不是普通网络断线。它不是根因证明，但可以确认：

> 服务可达 ≠ 推理资源空闲 ≠ 请求会立即获得模型计算。

## 10. 性能数据使用边界

全面 v2 后半段曾出现 Responses、Anthropic 60～140 s 的耗时，这些请求发生在重 Thinking 请求附近。

因此这些数据可以证明能力存在，但不能直接当作协议固有性能。稳定性能需要单独低负载、重复、随机化顺序并统计 P50/P95/P99。

## 11. 当前能力矩阵

| 能力 | 当前结论 |
|---|---|
| OpenAI Chat Text / SSE | PASS |
| Chat Thinking OFF / ON | PASS，ON 有明显长尾 |
| Chat Tool Loop | PASS |
| Responses Text / SSE | PASS |
| Responses Tool Loop | PASS |
| Anthropic Messages / SSE / count_tokens | PASS |
| Anthropic Tool Loop | PASS |
| Anthropic thinking disabled | 兼容异常 |
| Chat Vision 单图 / SSE / 多图 | PASS |
| Vision + Tool Calling | PASS，专项重测 3/3 |
| Anthropic Vision | PASS |
| Responses Vision | 待按 OpenAPI Schema 修正复测 |
| 公网 image_url | 未测 |
| 128K 长上下文稳定性 | 未专项验证 |

## 12. 工程结论

1. 当前内网服务已经是文本 + 多模态 + Tool Calling 的模型服务。
2. OpenAI Chat、Responses、Anthropic 三套协议均已验证 Tool Result 基础闭环。
3. Anthropic 的主要异常是 Thinking disabled 未生效，而不是 Tool Use 不支持。
4. Thinking 不只增加平均时间，还可能放大尾延迟并影响随后请求。
5. 自动化测试本身也会出错；测试 Schema、判定器和 Ground Truth 需要人工 Review。
6. Endpoint、HTTP、Schema、模型行为、Ground Truth、Tool Loop 必须分层验证。
