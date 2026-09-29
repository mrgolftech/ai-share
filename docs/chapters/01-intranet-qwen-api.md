# 培训讲义：从 API 到多模态与 Agent Tool Loop

> 模块一：模型怎么调用  
> 实测对象：部门内网 qwen3.6

## 一、先看现网，而不是先看宣传参数

GET /v1/models 实际返回：

~~~json
{
  "id": "qwen3.6",
  "root": "/models/Qwen3.6-35B-A3B-w8a8-ascend",
  "max_model_len": 131072
}
~~~

GET /version 返回 0.23.0。

培训第一原则：

> 官方资料说明模型本体能做什么；现网 Request / Response、Metrics 和压力测试说明我们部署出来的服务到底能做什么。

## 二、Qwen3.6-35B-A3B 的特点

35B 表示总参数规模，A3B 表示每 Token 只激活约 3B 参数，这是 MoE 的典型特点。

~~~text
Token
  ↓
Router
  ↓
选择部分 Experts
  ↓
当前 Token 计算
~~~

A3B 不等于“整套服务只需要 3B 模型的资源”。权重、专家分布、通信、KV Cache、长 Context 和并发仍然需要真实部署验证。

官方模型原生 Context 和当前部署也要分开：

~~~text
官方模型：262K
当前服务：131072 ≈ 128K
~~~

## 三、API：模型走出聊天框的第一步

~~~text
Postman / Python / WebUI / Agent
               │
          HTTP + JSON / SSE
               ▼
          vLLM API Server
               ▼
        Tokenizer / Parser
               ▼
             Qwen
               ▼
            昇腾节点
~~~

模型不是网页；WebUI 只是 API 的一种客户端。

## 四、非流式与 SSE

非流式：

~~~text
Request → 完整推理 → 完整 JSON
~~~

流式：

~~~text
Request → 生成 → SSE chunk → SSE chunk → DONE
~~~

简单 Chat SSE 实测总耗时约 2.37 s，首个文本约 1.83 s。

因此 TTFT 和总耗时是两个不同指标。

## 五、Token 和 Context

/tokenize 将文本变为 Token IDs，/detokenize 可以还原文本。

即使内网模型不按公网账单计费：

> Token 仍然等于真实算力、内存、时间和并发容量。

128K Context 是共享预算：

~~~text
System Prompt
+ 历史消息
+ 当前问题
+ 文件
+ RAG
+ Tool Schema
+ Tool Result
+ Agent 中间状态
+ 输出空间
~~~

能装进去，不代表值得每次都装满。

## 六、Thinking：重点不是平均慢几倍，而是资源和尾延迟

专项重测：

Thinking OFF：

- 4.75 s / 105 tokens
- 20.01 s / 512 tokens
- 6.35 s / 146 tokens

Thinking ON：

- 43.48 s / 1331 tokens
- 50.90 s / 1536 tokens
- 298.59 s / 1536 tokens

所以真正结论是：

> Thinking 是计算预算；它会增加 Token、时间和尾延迟，而且可能挤占最终回答空间。

第三轮更值得展示：

~~~text
Thinking ON：298.6 s
↓
/version：4.5 ms
↓
简单 PING Chat：70.2 s
↓
稍后恢复：0.81 s
~~~

说明：

> 服务可达 ≠ 推理资源空闲。

这比简单说“网络不稳定”更接近当前证据。

## 七、Tool Calling：从 Chat 走向 Agent

模型并不直接执行天气接口。

模型做的是：

~~~json
{
  "name": "get_weather",
  "arguments": {"city": "北京"}
}
~~~

真正闭环：

~~~text
用户
 ↓
模型
 ↓
Tool Call
 ↓
Agent Runtime 执行真实工具
 ↓
Tool Result
 ↓
模型
 ↓
Final Answer
~~~

现在已经验证：

- OpenAI Chat Tool Loop PASS
- Responses Tool Loop PASS
- Anthropic Tool Loop PASS

所以我们测试的不再只是“会不会输出函数名”，而是完整回灌后能不能继续回答。

## 八、三套协议是一张能力矩阵

| 能力 | OpenAI Chat | Responses | Anthropic |
|---|---|---|---|
| 文本 | ✅ | ✅ | ✅ |
| SSE | ✅ | ✅ | ✅ |
| Tool Call | ✅ | ✅ | ✅ |
| Tool Result | ✅ | ✅ | ✅ |
| Vision | ✅ | 待修正复测 | ✅ |
| Thinking 关闭 | ✅ | — | ⚠️ |

兼容不是 Yes / No，而是 Endpoint、Schema、Streaming、Thinking、Tool Calling、Tool Result 等逐项验证。

## 九、Anthropic 真正的问题

旧测试里 Tool Use 没有形成，是因为 Thinking 持续消耗输出预算。

提高 max_tokens 后：

~~~text
tool_use ✅
tool_result ✅
final answer ✅
~~~

所以不能再说“Anthropic Tool Use 不支持”。

真正异常是：

> thinking.type=disabled 没有真正关闭 Thinking。

这就是“协议能跑通”和“体验好不好”之间的差别。

## 十、多模态现在已经是现网实测能力

测试图不是随机照片，而是带标准答案：

~~~text
AI TEST 2026
3 个红圆
2 个蓝方块
绿色三角形：右下
~~~

已通过：

- Base64 单图
- Vision SSE
- 多图
- OCR
- 数量、颜色、位置
- Anthropic Image
- Vision + Tool Calling

所以现在可以正式说：

> 当前内网 qwen3.6 已实测具备图片理解和多图输入能力，并能把视觉结果转换为结构化 Tool Call。

## 十一、Vision + Tool Calling 的假失败

第一次工具字段叫 text。

模型正确识别数量和位置，却把 text 理解成“图片描述”，因此脚本判 FAIL。

改成：

~~~text
top_text
description = 必须逐字 OCR 顶部英文
~~~

后，3/3 全部返回：

~~~json
{
  "red_circles": 3,
  "blue_squares": 2,
  "green_triangle_position": "bottom-right",
  "top_text": "AI TEST 2026"
}
~~~

这说明：

> Tool Schema 本身也是 Prompt。字段名和 description 写得差，也会制造“模型失败”。

## 十二、Responses Vision 为什么还不能下结论

专项重测连续 HTTP 400，一开始很容易说“不支持图片”。

但服务自己的 OpenAPI 告诉我们 ResponseInputImageParam 需要：

~~~json
{
  "type": "input_image",
  "detail": "auto",
  "image_url": "data:image/png;base64,..."
}
~~~

测试请求漏掉 detail，错误 Body 也明确出现 Field required。

所以正确结论是：

> 测试请求不符合服务 Schema，修正后复测。

而不是“模型不支持”。

## 十三、自动化测试本身也会错

本轮有两个典型假失败：

1. Thinking OFF 判定器 tuple 写错；
2. Vision Tool 字段语义不清。

因此：

> 自动化测试不是最终真理，测试代码、测试数据、Ground Truth 和验收标准也需要 Review。

这正好对应培训中的人机分工：

> 模型负责判断和生成，工具负责执行，自动测试负责验证，人负责目标、约束和最终判断。

## 十四、/metrics：从“能用”走向“好用”

初始 Metrics 快照可看到 running、waiting、KV Cache、Prompt Tokens 等指标，并显示 Prefix Cache 未启用。

API 测试回答：

> 能不能调？

Metrics + 压测回答：

> 多人连续用的时候还能不能好用？

这就是后续 Model-Metric 案例的入口。

## 十五、当前内网模型的统一表述

推荐培训中这样说：

> 部门当前内网部署 qwen3.6，服务端配置约 128K Context。实测已支持 OpenAI Chat、Responses 和 Anthropic Messages 三套文本协议，并验证了三套 Tool Call → Tool Result 基础闭环；OpenAI Chat 与 Anthropic 已实测支持图片，Chat 侧支持单图、多图、Vision Streaming 和 Vision + Tool Calling。Thinking 可开关，但 Anthropic 风格关闭 Thinking 存在兼容异常，重 Thinking 任务还表现出明显尾延迟。

## 十六、与下一章 Agent 的衔接

我们现在已经证明：

~~~text
文本
图片
Thinking
Tool Call
Tool Result
~~~

都可以进入模型服务。

下一章的问题不再是“模型会不会回答”，而是：

> 谁来给它 File、Shell、Git、Browser、API，并围绕目标连续执行、观察、验证和迭代？

~~~text
Model
+ Context
+ Workspace
+ Tools
+ Loop
= Agent
~~~

API 是模型走出聊天框的第一步，Tool Calling 是 Chat 走向 Agent 的关键桥梁。
