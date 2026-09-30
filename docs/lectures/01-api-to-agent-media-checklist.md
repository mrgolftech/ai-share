# 第一讲素材清单：从模型 API 到 Agent

> 日期：2026-09-30  
> 对应讲义：`docs/lectures/01-api-to-agent.md`  
> 状态：Working Checklist v1.0  
> 使用原则：**正文决定“为什么需要这份素材、插在哪里”；本清单决定“具体拍什么、怎么拍、优先级、状态和备用方案”。**

---

## 0. 使用方式

- 正文中的 `【截图占位 ...】` / `【录屏占位 ...】` 是素材引用位置；
- 本文件是本讲唯一执行清单；
- P0：必须准备；P1：强烈建议；P2：可选；
- 每项完成后把状态改为：`⬜ 未准备` / `🟨 已采集待处理` / `✅ 可直接用于培训`；
- 同一素材如果跨讲复用，只保留一个原始文件，但在两个讲义清单中分别注明用途；
- 现场 Demo 涉及网络、模型排队、Browser、SSH、Build、GitHub Actions 时必须准备预录或静态备用。

---

## 1. 本讲素材总控表

| 素材组 | 优先级 | 主要内容 | 状态 |
|---|---:|---|---|
| API-NET-* | P0 | Cherry models / Chat / Context / Vision / SSE 抓包 | ⬜ |
| API-PROTO-* | P0 | OpenAI Chat / Responses / Anthropic 三协议 | ⬜ |
| API-SYS-* | P0 | System Prompt 在三种 API 中的实际位置 | ⬜ |
| FILE-* | P0 | 临时附件 / 原生 File Input / Vision / Knowledge 四条路径 | ⬜ |
| PROMPT-* | P1 | Prompt 骨架、社区框架、Prompt/Rules/Skill/Test 边界 | ⬜ |
| API-POST-* | P0 | Postman / curl GET + POST | ⬜ |
| API-APP-* | P0 | 同一 Model API → 翻译 / JSON / Vision OCR / Visual QA / 分类 | ⬜ |
| API-TEST-* | P0 | qwen_api_training_test.py + r4 28 PASS / 1 SKIP | ⬜ |
| CH-API-* | P0 | Cherry 三种 Endpoint Type / Network 对照 | ⬜ |
| CH-ASSIST-* | P0 | Assistant / Instructions / 模型 / 参数 | ⬜ |
| CH-KB-* | P0 | Cherry 知识库创建、召回、对话勾选 | ⬜ |
| CH-WEB-* | P0 | Cherry 联网检索 | ⬜ |
| WB-COMP-* | P0 | Cherry vs Open WebUI；Assistant vs Workspace Model | ⬜ |
| OW-* | P0 | Open WebUI v0.11.0 Note / Knowledge / Workspace | ⬜ |
| API-03~05 | P0 | Thinking / Tool Call / Tool Result | ⬜ |
| MM-* | P0 | /metrics + model-metric 总览 / Benchmark | ⬜ |
| CHAT-* / ZCODE-* | P0 | Chat vs Agent 最小闭环 | ⬜ |
| API-R* / CH-R* / OW-R* / WB-R* / MM-R* | P0/P1 | 第一讲动态演示与备用录屏 | ⬜ |

> 第一讲优先拍摄顺序：**Cherry 三协议 → GET/POST → API 非 Chat 小应用 → 自动测试 → model-metric → Cherry/Open WebUI 工作台 → Context → Tool Loop → Chat vs Agent**。

---

# 14. 第一讲截图执行清单

## 14.1 P0 必拍截图

### API-NET-01：Cherry 对话界面

拍摄内容：

- 当前选择的内网模型；
- 输入框；
- 一条普通文本问题；
- 不显示任何 API Key 或敏感地址。

用途：

> 作为“从大家熟悉的 Chat 开始”的第一张真实界面。

### API-NET-02：/v1/models

拍摄内容：

- Network Request；
- Method；
- Endpoint；
- Response 中模型 id。

画面要求：

> Request 和 Response 至少有一张能在投影上看清关键字段。

### API-NET-03：首轮 Chat Payload

重点框出：

- model；
- messages / input；
- stream。

不要截完整巨大 JSON。

### API-NET-04A～C：多轮 Context

固定两轮问题。

分别截：

1. 第一轮；
2. 第二轮；
3. Diff/标注图。

第三张是最重要的：

> 用箭头明确指出历史消息怎样重新进入下一轮请求。

### API-NET-05～06：Vision

一张界面，一张 Payload。

要求使用无敏感信息、内容明确的固定测试图片。

### API-NET-07：SSE

要求能看到多个连续 event/data chunk。


### API-SYS-01～04：System Prompt 在三套 API 中怎么附加

必须准备同一段“内网 API 培训助手”长期指令的三套真实 Request：

- API-SYS-01：OpenAI Chat 中的 `system/developer message`；
- API-SYS-02：OpenAI Responses 中的 `instructions`；
- API-SYS-03：Anthropic Messages 顶层 `system`；
- API-SYS-04：一张三协议位置对照图。

要求：

> 以当前 Cherry + 内网 qwen3.6 实际 Network Request 为准，不因为官方新接口支持某字段就推断内网一定相同。

### PROMPT-01～04：Prompt 基础

准备：

- PROMPT-01：System Prompt / User Prompt / Context 三层关系；
- PROMPT-02：推荐工程 Prompt 骨架：Goal/Context/Constraints/Output/Examples/Verification；
- PROMPT-03：RTF / CO-STAR / CRISPE 社区框架速览，注明“记忆法，不是标准”；
- PROMPT-04：User Prompt / System Prompt / Project Rules / Skill / Test 作用范围。

### FILE-01～05：文件怎样进入模型

准备统一图组：

- FILE-01：客户端 Parse → Extract Text → Context；
- FILE-02：Responses `input_file` / `file_id`；
- FILE-03：Anthropic `document` / `file_id`；
- FILE-04：图片作为 Vision Content；
- FILE-05：临时附件 vs Full Context vs Knowledge/RAG。

建议所有图都使用同一个短 Markdown / PDF 做示意，避免不同文件造成理解干扰。

### API-POST-01～03：直接 GET / POST 与客户端关系

必须准备：

- Postman / curl `GET /v1/models`；
- Postman `POST /v1/chat/completions`；
- “Postman / Python / Cherry / Open WebUI / Agent → 同一个 Model API”图。

### API-APP-01～06：同一个 API，不只有 Chat

准备一组尽量统一风格的素材：

- API-APP-01：同一个 Model API 分叉到 Chat / Translation / JSON / Vision / Visual QA / Classification / Agent；
- API-APP-02：英文技术句子 → 中文翻译；
- API-APP-03：测试记录 → JSON → Parse / Schema Validation；
- API-APP-04：自制字符图片 → Vision 识别；
- API-APP-05：自有网页截图 → Visual QA 问题列表；
- API-APP-06：测试记录 → NORMAL / REVIEW / INVALID 分类。

要求：

> 所有演示尽量固定同一个 Base URL、同一个 qwen3.6，只改变 Input / Prompt / Output Contract。

工程边界：

- 不用第三方真实 CAPTCHA，使用自制验证码样式图片；
- 当前内网如果未正式验证 `response_format/json_schema`，只演示 Prompt JSON + 本地校验；
- 不能把“能输出 JSON”表述成“Structured Outputs 已兼容”。

对应 Demo 规范：

`demos/api-applications/README.md`

### API-PROTO-01～04：三种 API 协议

必须使用当前内网 qwen3.6 的真实请求准备：

1. OpenAI Chat：`messages / choices / tool_calls`；
2. OpenAI Responses：`input / output / function_call / events`；
3. Anthropic Messages：`content blocks / tool_use / tool_result`；
4. 三协议对比图。

### CH-API-01～02C：Cherry 三协议接入

拍当前实际安装版本：

- Provider / Model 的 Endpoint Type 或协议配置；
- `/v1/chat/completions`；
- `/v1/responses`；
- `/v1/messages`。

不要为了讲义强行模拟不存在的 UI；以当前 Cherry 真实配置方式为准。

### API-TEST-00～04：自动验收证据

准备：

- `qwen_api_training_test.py` 文件头与覆盖范围；
- r4 正式结果 28 PASS / 1 SKIP / 0 FAIL / 0 ERROR；
- 单条 record；
- 结果目录；
- 协议/能力矩阵。

### CH-ASSIST-01～06：助手与对话配置

拍：

- 新建 / 编辑助手；
- Instructions；
- 默认模型；
- Temperature / Top-P / Max Tokens / Stream / Context；
- 对话顶部模型切换；
- Knowledge / Web Search / Tool/MCP 等入口；
- “UI 开关 → Context / Parameter / Tool”映射图。

### CH-KB-01～04：Cherry 最小知识库流程

拍：

1. 新建知识库；
2. 添加文件 / 笔记 / 目录 / 链接中的实际可用入口；
3. Parse / Chunk 或资料处理结果；
4. Recall Test；
5. 对话勾选知识库。

第一讲只用于说明知识如何进入 Context；第二讲继续复用并展开 Retrieval 原理。

### CH-WEB-01：联网检索

拍：

- 输入区联网按钮；
- 当前搜索服务配置；
- 一次带 Search Result / Citation 的回答。

### WB-COMP-01～05：Cherry vs Open WebUI 对比

准备：

- WB-COMP-01：Cherry Desktop / Local Data → Model API；
- WB-COMP-02：Browser → Open WebUI Server / Data → Model API；
- WB-COMP-03：两者数据边界/使用场景对照表；
- WB-COMP-04：Cherry Assistant vs Open WebUI Workspace Model；
- WB-COMP-05：个人知识 → 团队知识演进图。

### WB-COMP-04A～04E：Assistant / Workspace Model 对应关系

必须准备：

- WB-COMP-04A：功能对应表；
- WB-COMP-04B：Cherry Assistant 的 Model + Instructions + Knowledge；
- WB-COMP-04C：Open WebUI Workspace Model 的 Base Model + System Prompt + Knowledge；
- WB-COMP-04D：两边统一抽象为 Application Preset；
- WB-COMP-04E：Base Model → Assistant → Agent 能力叠加图。

### OW-07～13：Open WebUI v0.11.0 个人知识 / Workspace

按当前内网已经走通的实际流程拍：

- OW-07：个人 Note / Markdown；
- OW-08：上传文档；
- OW-09：Full Context / Focused Retrieval 切换；
- OW-10：未配置 Embedding / 未向量化提示；
- OW-11：Workspace 绑定 Knowledge；
- OW-12：选择 Workspace 后依据知识问答；
- OW-13：Note/Document → Knowledge → Workspace → Chat 图。

### OW-14～15：Note 对话与 Workspace 复用

拍：

- OW-14：Note Editor + 围绕 Note 的 Chat；
- OW-15：创建 Workspace / Model 时附加已有 Note / Knowledge。

### CH-TOOL-01～02：MCP / Tool

拍：

- 助手 MCP / Tool 配置；
- 一次 Tool Call / Tool Result。

### API-TEST-03：结果资产目录

拍摄：

```text
api/qwen/results/20260930_095033/
```

要求能看到：

- 单项 JSON record；
- SSE 原始记录；
- manifest；
- summary。

### API-TEST-04：能力矩阵

根据正式 r4 报告制作一张 PPT 友好矩阵：

- Chat；
- Responses；
- Anthropic；
- Tool Loop；
- Vision；
- Thinking 差异；
- 28 PASS / 1 SKIP。

### API-03：Thinking

固定同一问题，截 OFF 和 ON。

如果协议中能看到 reasoning/thinking 参数，优先把参数也截进去。

### API-04～05：Tool Calling

必须形成成对证据：

1. Tool Call；
2. Tool Result + Final Answer。

### MM-01～02：model-metric

至少拍：

- 总览；
- Benchmark。

重点保证 TTFT/TPS/running/waiting/KV 等关键字段可读。

### CHAT-01 / CHAT-02

同一个任务：

- Chat 只给建议；
- Agent 已经开始操作 Workspace。

---

# 15. 第一讲录屏执行脚本

## API-R01：模型列表

时长建议：20～30 秒。

步骤：

1. 打开 Cherry；
2. 打开 DevTools Network；
3. 刷新 Provider / Model；
4. 点击对应 request；
5. 停在 Response。

目的：

> 证明“模型列表也是 API 获取的”。

## API-R02：多轮 Context

时长建议：40～60 秒。

固定脚本：

1. 新建会话；
2. 输入：“这个项目代号叫蓝鲸”；
3. 输入：“刚才的项目代号是什么？”；
4. 展开两次 Network Request；
5. 对照第二次请求历史。

不要在录屏中临时想问题。

## API-R03：Vision

步骤：

1. 上传固定图片；
2. 输入固定问题；
3. 发送；
4. 查看 Network Payload；
5. 回到回答。

## API-R04：SSE

步骤：

1. 发送一个输出稍长的问题；
2. Network 保持打开；
3. 让观众同时看到聊天窗口持续输出和 EventStream。

## API-R07：完整 Tool Loop

必须保留：

- 模型提出 Tool Call；
- Harness 执行；
- Tool Result；
- 模型继续生成。

不要只录最终答案。

## CH-R03：Cherry 三协议

固定同一个 Prompt：

> 请只回答：PROTOCOL_OK

依次切换：

- OpenAI Chat；
- OpenAI Responses；
- Anthropic Messages。

录到 Network Endpoint 与 Request Body 差异。

## CH-R04：Cherry 模型参数

修改：

- Max Tokens；
- Stream；
- Thinking / Reasoning（当前配置支持时）。

然后对比 Network Request。

## CH-R05：Cherry Knowledge

步骤：

1. 不勾知识库提问；
2. 勾选 Qwen API 训练知识库；
3. 再问当前内部实测问题；
4. 展示检索/引用差异。

## CH-R06：Cherry Web Search

固定一个时效性公开问题：

1. 普通问；
2. 开启联网；
3. 展示 Search Tool / Result / Citation。

## OW-R03：Open WebUI 个人知识到 Workspace

步骤：

1. 新建个人 Note / Knowledge；
2. 上传固定 Markdown / 文档；
3. 展示 Full Context / Focused Retrieval；
4. 展示当前未配置 Embedding / 未向量化提示；
5. 在 Workspace / Model 中引用 Knowledge；
6. 选择对应 Workspace；
7. 问固定问题；
8. 展示依据资料回答。

建议同一份资料至少保留一次 Full Context 演示，以明确说明全文注入不依赖 Embedding。

## WB-R03：Cherry Assistant vs Open WebUI Workspace Model

固定：

- 同一个 `qwen3.6`；
- 同一段 System Prompt；
- 同一份 Qwen API 测试资料；
- 同一个问题。

步骤：

1. Cherry 创建/打开“内网 API 培训助手”；
2. 展示 Instructions + Knowledge；
3. 提问并看回答；
4. Open WebUI 创建/打开对应 Workspace Model；
5. 展示 System Prompt + Knowledge；
6. 提同一个问题；
7. 对比两边都如何基于“长期指令 + 知识”工作。

不要比较模型谁更聪明，重点只观察“应用封装机制相同”。

## OW-R04～05：Note 对话与复用

### OW-R04：围绕 Note 直接问答

1. 新建一条固定 Markdown Note；
2. 写入一段 Qwen 实测结论；
3. 打开 Note Chat；
4. 问一个答案明确存在于 Note 的问题；
5. 展示回答或对 Note 的修改。

### OW-R05：Note → Workspace Model

1. 使用已有 Note / Knowledge；
2. 创建 Workspace / Model；
3. 设置 System Prompt；
4. 附加已有知识；
5. 选择该 Workspace；
6. 新建 Chat；
7. 固定问题；
8. 观察系统提示词和知识共同影响回答。

## PROMPT-R01：修改 System Prompt → 看 Request

固定同一个用户问题。

步骤：

1. Cherry Assistant 先不设置长期指令；
2. 发送问题并保存 Network Request；
3. 增加 System Prompt；
4. 再发送同一问题；
5. 对照 Request 中新增的 `system/developer`、`instructions` 或顶层 `system`；
6. 如时间允许切三种 Endpoint Type。

目的：

> 证明 Assistant / Workspace 的“长期指令”最终仍然要进入模型调用。

## FILE-R01：同一文件三种进入 Context

准备一个短文件，包含唯一字符串：

`TRAINING_ATTACHMENT_CODE = BLUE-7319`

依次演示：

1. Cherry 临时附件；
2. Cherry Knowledge；
3. Open WebUI Full Context / Workspace Knowledge。

每次问：

> 文档中的 TRAINING_ATTACHMENT_CODE 是什么？

同时观察：

- Request；
- Retrieval / Tool Trace；
- 是否全文；
- 是否只出现片段；
- 是否出现 file/document content type。

目的：

> 证明“上传文件”只是 UI 动作，底层可能是完全不同的数据路径。

## API-APP-R01：同一 API 串联 4 个非 Chat 小应用

时长建议：60～90 秒。

建议连续展示：

1. 技术英文 → 中文翻译；
2. 测试记录 → JSON；
3. 自制字符图片 → Vision 识别；
4. 自有网页截图 → Visual QA JSON。

要求始终让观众看到：

- Base URL 没变；
- Model 没变；
- API 调用模式没变；
- 变化的是 Input / Prompt / Output Contract。

目的：

> **把“模型 API = 聊天接口”这个认知彻底打破。**

## API-R10：自动测试脚本

建议使用预录 + 现场打开正式结果。

步骤：

1. 显示 `qwen_api_training_test.py`；
2. 运行测试；
3. 展示若干 PASS；
4. 打开结果目录；
5. 打开 `manifest.json` / 正式报告；
6. 展示一条 Tool Loop 或 Vision record。

不要在课堂现场等待全部 Thinking / 多图 Vision 测试跑完。

## MM-R01：请求与指标变化

步骤：

1. model-metric 总览保持可见；
2. 发出一个较长请求；
3. 显示 running/KV/TPS 等变化；
4. 请求完成后观察状态回落。

## API-R08：Chat vs Agent

最好剪成左右或前后两段：

Chat：

> 给一个需要文件修改和验证的小任务。

Agent：

> 同样目标，展示实际 Read/Edit/Test/Diff。

不要比较不同模型；尽量固定模型，突出 Harness 差异。

---

# 16. 第一讲现场 Demo 与备用策略

现场建议真正实时做四项，并准备一条 P0 的 API 小应用串联录屏：

1. Cherry 配置内网模型，并用同一 Prompt 切 OpenAI Chat / Responses / Anthropic 三种协议，看 Network Endpoint；
2. Open WebUI v0.11.0：个人 Note / 文档 → Knowledge → Workspace → 基于资料问答；
3. Cherry 多轮 Context；
4. 最小 Agent Read/Edit/Test Loop。

P0 预录：

- API-APP-R01：同一 qwen3.6 API 连续完成翻译 / JSON / Vision OCR / Visual QA，用 60～90 秒证明“API 不等于 Chat”。

Postman、自动测试、model-metric、Thinking、Vision、Tool Loop 根据现场时长选择实时或预录；其中完整 r4 测试、并发压测和长 Thinking 优先使用预录。

原则：

> **任何依赖网络、模型排队、浏览器状态的 Demo 都必须准备预录和静态截图。**

第一讲结束以后，学员应该已经能够把一个新的 AI 产品先问成一句话：

> “它背后调用什么模型？怎样管理 Context？有哪些 Tool？谁负责执行？”

做到这一点，第一讲就完成了。
