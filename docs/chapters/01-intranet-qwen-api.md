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

## 二、Qwen3.6-35B-A3B 的特点：先讲清 MoE

官方 Qwen3.6-35B-A3B 是一个稀疏 Mixture-of-Experts（MoE）模型：

- 总参数约 35B；
- 每 Token 激活约 3B 参数；
- 官方模型卡给出 256 个 Experts；
- 每 Token 路由到 8 个 Routed Experts，并使用 1 个 Shared Expert。

因此名称里的：

~~~text
35B = Total Parameters
A3B = Activated Parameters（约 3B）
~~~

核心过程可以简化为：

~~~text
Token
  ↓
Router / Gate
  ↓
从很多 Experts 中选择少数专家
  ↓
只让被选中的专家参与当前 Token 的计算
  ↓
合并结果
~~~

### 2.1 MoE 为什么有价值

MoE 的关键不是“模型变小”，而是：

> **把总参数容量做大，同时避免每个 Token 都执行全部参数对应的计算。**

早期 Mixture of Experts 思想可以追溯到 1991 年的 Adaptive Mixtures of Local Experts；2017 年 Sparsely-Gated MoE 把稀疏专家机制扩展到超大神经网络；Switch Transformer 等工作进一步推动了稀疏 Transformer MoE。

### 2.2 “只激活 3B，所以只占 3B 显存”是错误理解

少激活专家，主要减少的是 **每 Token 的有效计算量 / FLOPs**。

但整套模型的专家权重仍然必须在系统中可用，通常需要：

- 驻留在一张或多张卡的 HBM / 显存；
- 或分布到多个设备；
- 或采用 Offload / Streaming 等更复杂方案。

所以：

> **A3B 不等于只需要 3B Dense 模型的权重内存。**

MoE 还会引入额外工程问题：

- Router；
- Expert Load Balance；
- 跨卡 All-to-All / 通信；
- 热门专家拥塞；
- Batch 调度；
- 专家并行。

KV Cache、长 Context 和并发也不会因为“A3B”就自动按 3/35 比例下降。

### 2.3 与当前内网部署必须分开

官方模型原生 Context 与当前服务配置不是一回事：

~~~text
官方 Qwen3.6-35B-A3B：262,144 native context
当前内网服务：131072 ≈ 128K
~~~

当前内网还是 W8A8 Ascend 部署，因此培训最终以现网实测的：

- Context；
- 并发；
- TTFT；
- Tokens/s；
- KV Cache；
- 稳定性；

为准，而不是只看官方参数。

参考：

- Qwen3.6-35B-A3B 官方模型卡：https://huggingface.co/Qwen/Qwen3.6-35B-A3B
- Shazeer et al., Sparsely-Gated Mixture-of-Experts：https://arxiv.org/abs/1701.06538
- Switch Transformers：https://www.jmlr.org/papers/v23/21-0998.html

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


### 3.1 现场 Demo：用 Cherry Studio Network 把“聊天框”拆成 API 请求

这一段不先给学员看 Python，而是先打开 **Cherry Studio + Chromium DevTools / Network**。

目标是让大家直观看到：

> **聊天界面不是模型本身。它首先是一个 API Client：负责组织 Context、文件/图片和参数，再把请求发给模型服务。**

建议现场固定使用部门内网 qwen3.6，按下面顺序演示。

#### Demo A：模型列表是怎么来的

打开 Cherry Studio 的模型选择 / Provider 页面，清空 Network 后触发模型列表刷新。

重点观察：

- Request URL；
- Method；
- Status；
- Response；
- 是否请求 `/v1/models`；
- Response 中的 model id 如何最终出现在 UI。

这里要让学员建立第一层直觉：

~~~text
模型下拉框
   ↓
GET /v1/models
   ↓
JSON Response
   ↓
应用把模型列表渲染出来
~~~

也就是说：

> **UI 中“有哪些模型”这件事，本身也可以来自 API。**

截图占位：

- `API-NET-01`：Cherry Studio 模型列表；
- `API-NET-02`：Network 中的 models Request / Response。

#### Demo B：发送第一条普通文本消息

使用一个非常短、容易识别的固定问题，例如：

~~~text
请记住测试编号 A17，只回复“已记住”。
~~~

在 Network 中找到实际 Chat Request，展开 Payload / Request Body。

重点观察：

- Endpoint；
- model；
- messages / input；
- role；
- content；
- stream；
- Thinking / reasoning 相关参数（如果实际请求存在）；
- Header 中的鉴权信息只说明作用，不在培训截图中暴露真实 API Key。

培训不要只展示整理后的 JSON，要让大家看到：

> **刚才在聊天框里输入的一句话，最终就是这样被应用组装成 HTTP Request 发出去的。**

截图占位：

- `API-NET-03`：第一轮文本对话 Request Payload。

#### Demo C：连续追问，Context 到底怎么附加

第二轮直接问：

~~~text
刚才的测试编号是什么？
~~~

然后把第一轮和第二轮 Request 并排比较。

这里不提前假设 Cherry Studio 当前版本一定采用哪一种会话组织方式，而是以现场抓包为准，重点验证：

1. 第二次请求是否重新带上前面的 user / assistant 消息；
2. System Prompt 是否每轮重复发送；
3. 当前问题位于哪里；
4. 如果实际使用的 Endpoint 支持服务端会话状态，是否出现 response id / conversation id / previous response 等引用；
5. 两轮请求体大小怎样变化。

如果当前 OpenAI Chat Compatible 路径表现为完整 messages 历史回传，可以画成：

~~~text
第 1 轮
System
+ User #1
        ↓
      Model

第 2 轮
System
+ User #1
+ Assistant #1
+ User #2
        ↓
      Model
~~~

这一段要纠正一个常见误解：

> **通常不是“模型自己记住了上一句话”，而是应用 / Harness 在下一次模型调用时重新组织并提供相关历史；如果采用服务端有状态协议，则可能通过会话标识引用之前状态。具体以实际协议和抓包为准。**

这正好为后面的 Context Window、Context Management 和 Agent Harness 铺路。

截图占位：

- `API-NET-04A`：第一轮 Request；
- `API-NET-04B`：第二轮 Request；
- `API-NET-04C`：两轮 Payload Diff / 标注图。

#### Demo D：多模态图片是怎么进入请求的

再发送一张非常简单、答案确定的测试图片。

现场不要只看模型“看懂了图片没有”，而要在 Network 中查看：

- Request Body 中图片对应的 content block；
- 图片是 Base64 / data URL、远程 URL、上传后的文件引用，还是由客户端 / Provider Adapter 转换成其他结构；
- 文本和图片在同一个 message / input 中怎样组合；
- 一张图和多张图的结构有什么变化。

这一段要传递的是：

> **“支持图片”不是聊天框的魔法，本质上仍然是客户端按照模型 API 的多模态 Schema，把文本和图像输入编码进请求。**

最终以 Cherry Studio 当前版本 + 当前 Provider 的真实 Request 为准，不把某一种图片传输形式写成所有客户端的统一标准。

截图占位：

- `API-NET-05`：Vision Request Payload；
- `API-NET-06`：文本 content 与 image content 的结构标注。

#### Demo E：流式输出在 Network 里是什么样

最后观察一次流式请求：

~~~text
stream = true
       ↓
HTTP Response 保持连接
       ↓
SSE event / data 持续到达
       ↓
Cherry Studio 一边接收，一边渲染到聊天框
~~~

这样可以直接把下一节“SSE”从抽象协议变成刚刚看过的真实现象。

截图占位：

- `API-NET-07`：流式 Response / EventStream。

### 3.2 这一组抓包 Demo 最终只留下四个结论

1. **Chat UI 是模型 API 的客户端，而不是模型本身。**
2. **多轮对话需要某种会话状态管理：历史可以被重新组装进请求，也可以由有状态协议引用；必须看真实 Request，不能凭 UI 猜。**
3. **图片、文件、Thinking、Tool Schema 都最终要以某种协议结构进入模型调用。**
4. **从 UI → Network → Request / Response，是理解任何 AI 应用工作机制的一种通用调试方法。**

这也是后续分析 Cherry Studio、Open WebUI、Agent 和各种第三方客户端时建议学员掌握的第一种工程方法。

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

## 五、Tokens/s：先让大家直接感受“吐字速度”

这一段不先讲公式，先现场打开：

`demos/token-output-speed/index.html`

这是基于 GitHub 开源项目 `aaravchour/token-speed-visualiser`（Apache-2.0）做的培训版，不从零重复实现。保留了上游的单速率模拟和 Race Mode，只做中文化、离线化和培训场景调整。

建议现场先点：

~~~text
5 tok/s
→ 明显能跟着它一个片段一个片段地读

20 tok/s
→ 已经比较流畅

50 tok/s
→ 文本快速铺开

100 tok/s
→ 对聊天阅读来说已经非常快
~~~

再切到“并排对比”，同时观察：

~~~text
5 tok/s
30 tok/s
120 tok/s
~~~

这个 Demo 的目的不是测模型，而是先建立一个直觉：

> **Tokens/s 描述的是模型开始生成以后，内容往外输出有多快。**

一定要和 TTFT 分开：

~~~text
TTFT
= 多久开始出第一个 Token

Tokens/s
= 开始生成以后，每秒能输出多少 Token

Total Latency
= 整个请求多久结束
~~~

因此一个模型即使有 100 tok/s，如果 TTFT 要等 30 秒，用户依然会觉得慢；Agent 又会多轮调用模型和工具，这些等待还会连续叠加。

演示页中的“Token”只是视觉近似片段，不是真实 Qwen tokenizer，也不是性能 Benchmark。真实性能数据仍然来自 API 实测和 model-metric。

## 六、Token 和 Context

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

## 六、Thinking / CoT：不是 DeepSeek 才出现的

这里需要先区分两个经常混用的词。

### 6.1 CoT 是什么

Chain-of-Thought（CoT，思维链）通常指模型在得到最终答案前生成一系列中间推理步骤，或通过 Prompt 引导模型产生这类中间步骤。

在 LLM 语境中，CoT Prompting 被系统性提出并广泛传播，通常追溯到 Wei 等人在 2022 年 1 月提交的论文《Chain-of-Thought Prompting Elicits Reasoning in Large Language Models》。

同年 5 月，Zero-shot CoT 论文进一步展示了类似：

~~~text
Let's think step by step.
~~~

这种简单提示也能显著触发多步推理。

所以：

> **CoT 不是从 DeepSeek-R1 才出现。**

### 6.2 为什么很多人会觉得“从 DeepSeek 开始”

时间线更准确地说是：

~~~text
2022：CoT Prompting / Zero-shot CoT 成为 LLM 推理的重要方法
   ↓
2024-09：OpenAI o1 把“更多 test-time compute + 长推理”做成显著的 reasoning model 产品形态
   ↓
2025-01：DeepSeek-R1 / R1-Zero 让长 CoT、RL 推理和开放模型快速普及
   ↓
2025-2026：Qwen 等模型普遍出现 Thinking / Non-Thinking、Thinking Budget 等模式
~~~

DeepSeek-R1 的重要性不在于“发明 CoT”。

更准确的是：

> **DeepSeek-R1-Zero 公开展示了：可以直接在 Base Model 上用大规模 RL 激励出自验证、反思和长 CoT 等行为；DeepSeek-R1 又把这种能力做得更可用。**

这也是为什么 2025 年之后“模型先想一会儿再回答”开始成为大众非常直观的体验。

### 6.3 Qwen 的 Thinking 与 CoT 是什么关系

Qwen3 已公开采用 Thinking / Non-Thinking 双模式，并在训练中使用长 CoT、Reasoning RL 等方法；Qwen3.6 又增加了 Thinking Preservation 等能力。

但培训不要简单讲成：

~~~text
Thinking = 把模型真实脑内过程打印出来
~~~

更稳妥的理解是：

> **Thinking 是一种推理工作模式 / 推理预算机制；可见的 reasoning 文本只是模型生成过程的一种外显结果，不能把它当作绝对可信的内部执行日志。**

工程上真正应该验证的是：

- 最终答案；
- Tool Call；
- Tool Result；
- 代码；
- 测试；
- 外部证据。

### 6.4 什么任务值得开 Thinking

优先考虑：

- 数学和逻辑推理；
- 疑难 Bug；
- 多约束方案设计；
- 系统故障定位；
- 复杂代码理解；
- 需要权衡多个候选方案的任务。

通常没必要：

- 简单问答；
- 格式转换；
- 信息抽取；
- 翻译；
- 固定模板生成；
- 很明确的简单工具调用。

最实用的工程策略不是“永远开 Thinking”，而是：

> **简单任务快速模型 / 非 Thinking；复杂节点再升级推理预算。**

这就是模型路由意识。

### 6.5 内网专项实测：Thinking 的代价不是抽象概念

Thinking OFF：

- 4.75 s / 105 tokens
- 20.01 s / 512 tokens
- 6.35 s / 146 tokens

Thinking ON：

- 43.48 s / 1331 tokens
- 50.90 s / 1536 tokens
- 298.59 s / 1536 tokens

所以真正结论是：

> **Thinking 是计算预算；它会增加 Token、时间和尾延迟，而且可能挤占最终回答空间。**

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

> **服务可达 ≠ 推理资源空闲。**

这比简单说“网络不稳定”更接近当前证据。

参考：

- Wei et al., Chain-of-Thought Prompting：https://arxiv.org/abs/2201.11903
- Kojima et al., Zero-shot CoT：https://arxiv.org/abs/2205.11916
- OpenAI o1（2024-09-12）：https://openai.com/index/learning-to-reason-with-llms/
- DeepSeek-R1：https://github.com/deepseek-ai/DeepSeek-R1
- Qwen3 Thinking / Non-Thinking：https://qwenlm.github.io/blog/qwen3/

## 八、Tool Calling：从 Chat 走向 Agent

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

## 九、三套协议是一张能力矩阵

| 能力 | OpenAI Chat | Responses | Anthropic |
|---|---|---|---|
| 文本 | ✅ | ✅ | ✅ |
| SSE | ✅ | ✅ | ✅ |
| Tool Call | ✅ | ✅ | ✅ |
| Tool Result | ✅ | ✅ | ✅ |
| Vision | ✅ | 待修正复测 | ✅ |
| Thinking 关闭 | ✅ | — | ⚠️ |

兼容不是 Yes / No，而是 Endpoint、Schema、Streaming、Thinking、Tool Calling、Tool Result 等逐项验证。

## 十、Anthropic 真正的问题

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

## 十一、多模态现在已经是现网实测能力

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

## 十二、Vision + Tool Calling 的假失败

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

## 十三、Responses Vision 为什么还不能下结论

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

## 十四、自动化测试本身也会错

本轮有两个典型假失败：

1. Thinking OFF 判定器 tuple 写错；
2. Vision Tool 字段语义不清。

因此：

> 自动化测试不是最终真理，测试代码、测试数据、Ground Truth 和验收标准也需要 Review。

这正好对应培训中的人机分工：

> 模型负责判断和生成，工具负责执行，自动测试负责验证，人负责目标、约束和最终判断。

## 十五、/metrics：从“能用”走向“好用”

初始 Metrics 快照可看到 running、waiting、KV Cache、Prompt Tokens 等指标，并显示 Prefix Cache 未启用。

API 测试回答：

> 能不能调？

Metrics + 压测回答：

> 多人连续用的时候还能不能好用？

这就是后续 Model-Metric 案例的入口。

## 十六、当前内网模型的统一表述

推荐培训中这样说：

> 部门当前内网部署 qwen3.6，服务端配置约 128K Context。实测已支持 OpenAI Chat、Responses 和 Anthropic Messages 三套文本协议，并验证了三套 Tool Call → Tool Result 基础闭环；OpenAI Chat 与 Anthropic 已实测支持图片，Chat 侧支持单图、多图、Vision Streaming 和 Vision + Tool Calling。Thinking 可开关，但 Anthropic 风格关闭 Thinking 存在兼容异常，重 Thinking 任务还表现出明显尾延迟。

## 十六、统一模型能力 Demo：鹈鹕骑自行车

统一使用：

> **创建一个单文件 HTML，用 SVG、CSS 和 JavaScript 生成一只鹈鹕骑自行车的循环动画。**

为什么不是简单问一道数学题？

因为这个任务同时需要：

- 理解自然语言要求；
- 把鹈鹕与自行车做空间组合；
- 生成 SVG 几何结构；
- 处理 CSS / JavaScript 动画；
- 保证轮子、踏板、腿和身体动作基本协调；
- 最终生成一个真正可执行的网页。

而且结果一眼就能看出来：

~~~text
“代码看起来像对的”
        ≠
“浏览器里真的对”
~~~

这正好为下一章 Agent 铺垫。

### 16.1 第一轮：模型能力对比

固定同一 Prompt、相近参数和运行条件，只比较第一次输出。

观察：

- 指令遵循；
- HTML/SVG 是否可运行；
- 构图；
- 动画逻辑；
- 一次完成度。

这主要观察：

> **Model Capability**

### 16.2 第二轮：同模型 Chat vs Agent

必须使用同一个模型。

Chat：

~~~text
Prompt → 代码 → 人保存 → 人打开 → 人发现问题 → 人再提问
~~~

Agent：

~~~text
Goal → 写文件 → 打开浏览器 → 观察 → 修改 → 再验证 → 交付
~~~

这一轮主要观察：

> **Harness Capability**

因此“鹈鹕骑自行车”不是正式 Benchmark，而是一个非常适合教学的统一能力演示题。

完整 Demo 规范：

~~~text
demos/pelican-bicycle/README.md
~~~

---

## 十七、与下一章 Agent 的衔接

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
