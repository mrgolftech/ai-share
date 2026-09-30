# 培训讲义：Open WebUI、Cherry Studio 与 RAG —— 从“聊天界面”走向知识与工具

> 模块二补充：Chat 工作台的设置方式与应用模式  
> 核实日期：2026-09-29  
> 目标：用 Open WebUI / Cherry Studio 说明“模型客户端 → Assistant → Knowledge/RAG → Agent”的能力递进。

---

# 一、先给两款工具一个准确定位

Open WebUI 和 Cherry Studio 都不能再简单叫“聊天壳”。

更准确地说，它们都是：

> **以对话为主要入口的 AI 工作台。**

用户可以从最简单的：

~~~text
选择模型 → 输入 Prompt → 得到回答
~~~

逐步增加：

~~~text
System Prompt / Assistant
→ 文件
→ 知识库
→ RAG
→ Web Search
→ MCP / Tools
→ Agent
~~~

因此培训中不要画成：

~~~text
Open WebUI / Cherry Studio = Chat
~~~

而应该画成：

~~~text
Raw Model
   ↓
Chat
   ↓
Assistant / Model Preset
   ↓
Files / Knowledge / RAG
   ↓
Tools / Web / MCP
   ↓
Agentic Retrieval / Agent
~~~

---

# 二、Open WebUI：更适合“集中式模型入口 + 管理 + Workspace”

【截图占位 OW-01｜P0】Open WebUI 首页 / 模型选择界面，能看出“统一 Web 入口 + 多模型”的产品定位。


## 2.1 接入模型

【截图占位 OW-02｜P0】Open WebUI Provider / Connection 配置页，展示 Base URL、模型来源；API Key 必须脱敏。

【录屏占位 WB-R01｜P1｜30–45 秒】新增/选择 Provider → 拉取模型 → 发起一次 Chat。用于说明“统一入口背后仍然是模型 API”。


对于部门内网这种 OpenAI-compatible API，推荐路径：

~~~text
Settings
→ Admin
→ Connections
→ Add OpenAI API Connection
~~~

配置：

- URL / Base URL；
- API Key；
- Model IDs（如果 /v1/models 无法自动发现）；
- 保存并启用连接。

Open WebUI 当前核心仍以 OpenAI Chat Completions 协议为主，同时对 Open Responses 提供实验支持。

一个完整兼容服务通常至少提供：

- GET /v1/models；
- POST /v1/chat/completions；
- 如果要做向量 RAG，再提供 POST /v1/embeddings；
- 如果要图像生成，可提供 POST /v1/images/generations。

对于部门内网 qwen3.6：

> Chat Completions 和 /v1/models 已有实测证据，因此作为普通 Chat Provider 接入是最直接的。

---

# 三、Open WebUI 的几种典型应用模式

【截图占位 OW-03｜P1】同一 Open WebUI 中“裸模型 Chat / Workspace Model / Knowledge / Tool”四种入口或配置的拼图，展示能力递进。


## 3.1 模式 A：裸模型聊天

直接选择一个 Base Model。

适合：

- 临时问答；
- 翻译；
- 文本生成；
- 快速测试模型。

优点：

> 配置最少，最接近模型原始能力。

## 3.2 模式 B：Workspace Model / 专用助手

Open WebUI 的 Workspace → Models 并不是训练一个新模型，而是在 Base Model 上叠加配置：

~~~text
Base Model
+ System Prompt
+ Parameters
+ Knowledge
+ Tools
+ Skills
+ Capabilities
= Workspace Model
~~~

例如同一个 qwen3.6 可以包装成：

- 硬件设计评审助手；
- API 测试助手；
- 部门制度问答助手。

这正好说明：

> **很多所谓“专用助手”不是新模型，而是“模型 + 固定指令 + 参数 + 知识 + 工具”的组合。**

## 3.3 模式 C：文件 / 知识库问答

临时文件：

> 直接在 Chat 上传。

反复使用的资料：

> Workspace → Knowledge 建立 Knowledge Base。

再把 Knowledge：

- 临时挂到 Chat；
- 或永久绑定到一个 Workspace Model。

## 3.4 模式 D：工具增强 / Agentic Chat

开启 Native Function Calling 后，可以让模型主动调用：

- Knowledge；
- Web Search；
- URL Fetch；
- Memory；
- Code Interpreter；
- Terminal；
- 自定义 Tools。

此时工作方式从：

~~~text
Prompt → Answer
~~~

开始转向：

~~~text
Prompt
→ 判断是否需要工具
→ Tool Call
→ Tool Result
→ 继续判断
→ Answer
~~~

---

# 四、Open WebUI：System Prompt 与模型参数

【截图占位 OW-04｜P0】Workspace Model 的 System Prompt 与 Advanced Parameters 配置页。截图时突出“模型 + Prompt + 参数 = 可复用助手配置”。


## 4.1 System Prompt

Open WebUI 当前支持：

- Per-Chat；
- Per-Account；
- Per-Model；

三层 System Prompt / 参数设置。

培训中不需要把覆盖规则讲得过细，只要建立：

> **长期稳定规则放 Workspace Model；一次性要求放当前 Chat。**

例如：

~~~text
你是一名硬件设计评审助手。

规则：
1. 先给结论，再说明依据；
2. 对器件规格必须引用提供的资料；
3. 证据不足时明确写“资料不足”；
4. 不根据型号名称猜测未提供参数。
~~~

这比每轮都重新输入同一段 Prompt 更稳定。

## 4.2 Advanced Parameters

常见参数：

- temperature；
- top_p；
- max_tokens / max_completion_tokens；
- seed；
- stop；
- Function Calling。

培训不建议讲“万能参数”。

工程上更实用：

- 事实型任务：Temperature 偏低；
- 创意任务：适当提高；
- 没有明确问题：优先保留模型默认值；
- Max Tokens 只是上限，不是“越大越聪明”。

---

# 五、Open WebUI：Thinking / Reasoning 设置

【截图占位 OW-05｜P1】Open WebUI Thinking/Reasoning 显示设置 + 同一模型真实请求参数/响应的对照，避免误解“UI 有开关 = 后端一定生效”。


这里必须分清两件事。

## 5.1 “显示 Thinking”不等于“开启 Thinking”

Open WebUI 可以识别：

- <think>...</think>；
- <thought>...</thought>；
- 自定义 Reasoning Tags；

然后把推理文本折叠显示。

这属于：

> **显示 / 解析层。**

它本身不一定改变模型是否执行推理。

## 5.2 真正推理预算取决于模型协议

Open WebUI 还支持部分 Provider 的：

- reasoning_effort；
- Ollama 的 think=true / false；
- low / medium / high 等推理层级。

但自建 Qwen 服务是否可以通过 UI 正确传递 Thinking 开关，取决于：

- 服务端实际参数；
- Open WebUI 是否把该字段发出去；
- Provider Adapter 如何处理请求。

因此对于部门 qwen3.6：

> **Thinking UI 是否真的对应服务端 Thinking On / Off，必须抓真实 Request 验证，不能只看界面。**

这本身就是一个很好的培训案例：

> **UI 有开关 ≠ 后端真的执行了开关。**

---

# 六、Open WebUI：图片能力要拆成两类

【截图占位 OW-06｜P1】同一页面中 Vision 输入与 Image Generation 入口/结果的对照图，强调“看图”和“生图”是两类能力。


## 6.1 Vision：理解图片

Workspace → Models 中可以打开 Vision Capability。

但：

> **勾选 Vision 不会把纯文本模型变成视觉模型。**

后端模型必须真的支持 Image Input。

当前内网 qwen3.6 已经实测：

- 单图；
- 多图；
- Vision SSE；
- Vision + Tool Calling。

所以很适合做 Open WebUI Vision Demo。

## 6.2 Image Generation：生成图片

生成图片是另一条链路。

典型路径：

~~~text
Settings
→ Admin
→ Experience
→ Images
~~~

可以配置：

- OpenAI Images；
- ComfyUI；
- Automatic1111 等。

因此培训要明确：

~~~text
Vision Model
= 看图 / 理解图片

Image Generation Model
= 画图 / 生成图片
~~~

二者不是一种模型能力。

---

# 七、先讲清楚 RAG 到底是什么

RAG：

> **Retrieval-Augmented Generation，检索增强生成。**

真正核心是：

~~~text
从外部资料检索相关信息
        ↓
把相关内容放进模型 Context
        ↓
模型基于资料生成回答
~~~

因此：

> **RAG 不等于向量数据库。**

向量检索只是 Retrieval 的一种实现。

只要流程是：

~~~text
Retrieve
→ Augment Context
→ Generate
~~~

就属于 RAG 思路。

---

# 八、Embedding 模型到底做什么

Embedding Model 不负责回答问题。

它负责把文本变成向量：

~~~text
“模型为什么响应很慢？”
          ↓
   Embedding Model
          ↓
[0.12, -0.38, 0.91, ...]
~~~

文档 Chunk 也会转换成向量。

检索时比较：

> Query Vector 与 Document Vector 的相似度。

因此即使文字不一样：

~~~text
用户：
模型为什么响应很慢？

文档：
长上下文会显著提高首 Token 延迟
~~~

向量检索仍可能认为两者语义相关。

## Embedding 的优势

- 同义表达；
- 自然语言提问；
- 问题措辞和文档措辞不一致；
- 大规模非结构化文本语义匹配。

## Embedding 的弱点

下面这类精确实体，关键词搜索常常更可靠：

- 型号；
- 错误码；
- API 名称；
- Endpoint；
- 函数名；
- IP；
- 标准编号。

例如：

~~~text
E12345
/v1/messages/count_tokens
RK3588
~~~

BM25 / grep 通常很直接。

---

# 九、Rerank 模型到底做什么

Rerank 不负责建知识库，也不负责最终生成答案。

它通常工作在第一次召回之后：

~~~text
Query
 ↓
BM25 / Vector Search
 ↓
先找 20 个 Candidate Chunks
 ↓
Rerank Model
 ↓
重新判断 Query 与 Candidate 的相关性
 ↓
选前 5 个
 ↓
LLM
~~~

所以可以用一句话：

> **Embedding 是海选，Rerank 是精排。**

Reranker 通常直接同时看：

~~~text
Query + Candidate Document
~~~

所以判断可以比单纯向量距离更精细。

代价：

- 多一次模型调用；
- 增加延迟；
- 增加算力或 API 成本。

工程建议：

> **如果候选内容根本召回不到，先修 Retrieval；如果能找到但顺序不好，再考虑 Rerank。**

---

# 十、Open WebUI 的知识库与 RAG

【复用截图 KB-15～17｜P0】Shared Knowledge、ACL、Focused/Agentic Retrieval。知识库章节为这些素材的唯一编号来源，本章直接复用。


## 10.1 Focused Retrieval

默认 Knowledge 模式会检索最相关的 Chunks 再送入模型。

基础流程：

~~~text
Document
 ↓
Parse
 ↓
Chunk
 ↓
Embedding
 ↓
Vector DB

User Query
 ↓
Query Embedding
 ↓
Vector Search
 ↓
Top-K
 ↓
LLM
~~~

Embedding Engine 可以配置：

- 本地 SentenceTransformers；
- Ollama；
- OpenAI；
- Azure OpenAI。

设置位置：

~~~text
Settings
→ Admin
→ Documents
~~~

## 10.2 更换 Embedding Model 为什么要 Reindex

不同 Embedding Model 产生的是不同向量空间。

所以：

> **更换 Embedding Model 后，已有知识库必须重新生成向量索引。**

不能拿新 Query Vector 去和旧模型生成的 Document Vector 直接比较。

---

# 十一、Open WebUI 的 Hybrid RAG

Open WebUI 当前可以启用：

~~~text
ENABLE_RAG_HYBRID_SEARCH=True
~~~

形成：

~~~text
                Query
               /     \
              /       \
        BM25 Search   Vector Search
              \       /
               \     /
             Candidates
                 ↓
              Rerank
                 ↓
               Top-K
                 ↓
                LLM
~~~

这里三层作用分别是：

### BM25

更擅长：

- 精确关键词；
- API；
- 型号；
- 标准号；
- 错误码。

### Vector

更擅长：

- 语义；
- 同义表达；
- 自然语言问法。

### Rerank

在候选集中进一步判断：

> 哪几段和问题最相关。

所以企业知识库中，很多时候：

> **Hybrid Search 比“只上向量库”更稳妥。**

---

# 十二、Open WebUI 还有 Agentic Knowledge Retrieval

Open WebUI Native Mode 允许模型自己使用知识库工具。

当前工具既包括：

- semantic / RAG query；
- filename search；
- exact grep；
- file read；

也可以开启：

~~~text
ENABLE_KB_EXEC=True
~~~

让模型获得类似文件系统的知识库访问方式：

- ls；
- tree；
- grep；
- cat；
- head；
- tail；
- sed；
- find。

此时模型可以：

~~~text
用户问题
 ↓
模型判断需要查资料
 ↓
query / grep
 ↓
找到相关文件
 ↓
read / cat
 ↓
发现还缺条件
 ↓
再次搜索
 ↓
继续读取
 ↓
回答
~~~

Open WebUI 官方甚至明确建议在 Agentic Flow 中：

~~~text
query_knowledge_files
→ grep_knowledge_files
→ view_file
~~~

一个负责语义定位，一个负责精确定位，一个负责读上下文。

这正好说明：

> **向量搜索与关键词搜索不是二选一，而是可以组合。**

---

# 十三、传统 RAG 与 Agentic Retrieval 的真正区别

不要简单讲成：

> Vector RAG vs Agent RAG。

这会混淆两个维度。

## 维度一：Retriever 怎么找

Retriever 可以是：

- BM25 / Keyword；
- Vector / Dense；
- Hybrid；
- grep / Full-text；
- SQL；
- Search Engine；
- Web Search。

## 维度二：谁控制 Retrieval

### Traditional / Pipeline RAG

~~~text
User Query
 ↓
系统自动 Retrieval
 ↓
固定 Top-K
 ↓
注入 Context
 ↓
LLM
~~~

特点：

- 快；
- 稳定；
- 可预测；
- 适合高频固定问答。

### Agentic Retrieval

~~~text
User Query
 ↓
Model
 ↓
Search
 ↓
Read
 ↓
判断够不够
 ↓
Search Again
 ↓
Read Another Source
 ↓
Answer
~~~

特点：

- 可以多轮搜索；
- 可以换关键词；
- 可以跨多个 Source；
- 适合复杂、多跳问题。

代价：

- 更多 Token；
- 更多 Tool Call；
- 更慢；
- 更依赖模型工具调用能力；
- 行为不如固定 Pipeline 可预测。

结论：

> **Agentic RAG 不是用来淘汰 Traditional RAG，而是解决更复杂的检索任务。**

---

# 十四、Cherry Studio：更适合个人桌面、多模型和知识库工作

【截图占位 CH-01｜P0】Cherry Studio 主界面：Provider / Assistant / Topic / Knowledge / MCP 等入口同屏，体现“个人 AI 工作台”。


Cherry Studio 当前已经包含：

- Chat；
- Work / Agent；
- Drawing；
- Translation；
- Knowledge Base；
- Files；
- Coding Partner；
- Notes。

培训里可以定义为：

> **面向个人与桌面用户的多模型 AI 工作台。**

---

# 十五、Cherry Studio：模型配置

【截图占位 CH-02｜P0】Custom Provider 配置：Base URL、API Key、模型 ID / 拉取模型。API Key 必须脱敏。

【录屏占位 WB-R02｜P0｜30–45 秒】配置内网 Provider → 拉取模型 → 选择 qwen3.6 → 发一次请求。和第一章 Network 抓包可形成前后呼应。


## 15.1 内置 Provider

路径：

~~~text
设置
→ 模型服务
~~~

基本流程：

~~~text
选择 Provider
→ 填 API Key
→ 获取模型列表
→ 添加模型
→ 连通性检查
→ 启用 Provider
~~~

## 15.2 自定义 Provider

部门内网模型可以使用 Custom Provider。

需要配置：

- Provider 名称；
- API Format；
- Base URL；
- API Key；
- Model ID。

Cherry 当前支持多类接口格式，例如：

- OpenAI；
- Anthropic；
- Gemini。

对于 OpenAI-compatible 服务，要特别注意：

> **Base URL 一般填写服务根地址，不要把 /chat/completions 重复写进去。**

Cherry 会根据 Provider 类型拼接请求路径。

### 对部门内网 qwen3.6

最直接路径：

~~~text
Custom Provider
→ OpenAI-compatible
→ Base URL
→ API Key
→ 获取 /v1/models
→ qwen3.6
→ Connectivity Check
~~~

也可以利用我们已经验证过的 Anthropic Messages 做 Cherry Agent 协议兼容测试。

---

# 十六、Cherry Studio 的 Assistant 和 Agent 要分开

【截图占位 CH-03｜P1】Assistant 配置与 Agent/Tools 配置对照，突出“预设 Prompt/参数”与“可主动调用工具”的区别。


Cherry Assistant 可以理解成：

~~~text
Assistant
= Name
+ Prompt
+ Default Model
+ Model Parameters
+ Knowledge
+ MCP
~~~

一个 Assistant 下面可以有多个 Conversation / Topic。

它适合：

- 翻译助手；
- 技术问答助手；
- 制度问答助手；
- 文档总结助手。

它仍然以：

> **持续对话 + 固定角色**

为主。

Agent / Work 更强调：

- 目标；
- 文件；
- 工具；
- 多步骤执行；
- 权限；
- 持续状态。

因此可以借 Cherry 直接解释：

> **Assistant ≠ Agent。**

---

# 十七、Cherry Studio：如何设置长期指令

编辑 Assistant 时当前主要包含：

- 基础；
- 模型；
- 提示词；
- 知识库；
- MCP。

长期规则放在“提示词”。

例如：

~~~text
你是部门技术资料助手。

回答规则：
1. 优先使用绑定知识库中的资料；
2. 如果资料中没有证据，明确说明“当前资料未找到依据”；
3. 回答关键参数时注明来源文件；
4. 不根据常识补写内部制度；
5. 如果问题存在多个解释，先列出可能含义。
~~~

这一页可以传递：

> **Prompt 不只是一次聊天输入，也可以变成可复用的 Assistant 配置。**

---

# 十八、Cherry Studio：模型参数、Thinking 与 Context

【截图占位 CH-04｜P1】模型参数 / Thinking Depth / Context 相关设置。旁边注明“UI 设置是否映射到后端参数必须用 Network/API 验证”。


Assistant 的模型设置可以包括：

- Temperature；
- Top-P；
- Max Tokens；
- Streaming；
- Context 管理；
- 自定义参数。

支持 Reasoning 的模型还可以提供 Thinking Depth。

但是：

> 不同模型支持的档位不同，不是所有模型都有 Off / Low / Medium / High。

所以对于内网 qwen3.6：

> **仍然应该抓真实 API Request，确认 UI 选项到底映射成什么字段。**

Cherry 对长会话还会进行 Context Compaction。

这可以用来解释：

> **长对话不是无限追加原文；随着任务变长，客户端需要管理上下文。**

---

# 十九、Cherry Studio：图片能力

【截图占位 CH-05｜P1】Vision 对话与 Drawing/生图入口的对照，和 OW-06 形成跨产品一致概念。


## 19.1 图片理解

上传图片需要当前模型真的支持 Vision。

Cherry 的 Model Capability 可以记录：

- Image；
- Audio；
- Video；
- Tool Calling 等。

但官方明确强调：

> **勾选能力标记不会凭空增加模型能力。**

所以仍然要以 API 实测为准。

## 19.2 图片生成

Cherry 有独立 Drawing 应用。

也可以：

- 直接选择 Image Generation Model；
- 或让文本 Agent 调用 Image Generation Tool。

默认绘图模型可在：

~~~text
Settings
→ Default Model
~~~

中配置。

培训中建议画一张“模型角色图”：

~~~text
Chat Model        → 回答问题
Vision Model      → 理解图片
Embedding Model   → 文本转向量
Rerank Model      → 候选精排
Image Model       → 生成图片
~~~

---

# 二十、Cherry Studio 当前知识库可以完全不配置 Embedding

【复用截图 KB-04｜P0】Embedding=None / BM25 配置界面。

【复用截图 KB-05｜P0】同一问题的 BM25 vs Embedding Retrieval Test。


这是这部分最值得现场演示的点。

Cherry Studio 当前官方知识库允许：

> **Embedding Model = None。**

此时主要依靠：

> **BM25 Keyword Retrieval。**

流程：

~~~text
Document
 ↓
Parse
 ↓
Chunk
 ↓
BM25 Index
 ↓
Query
 ↓
Keyword / Statistical Matching
 ↓
Top-K
 ↓
LLM
~~~

因此：

> **不用向量模型，照样可以建立知识库，也照样属于 RAG。**

Cherry 当前知识库会维护：

- Parsed Text；
- Chunks；
- BM25 Keyword Index；
- 如果配置 Embedding，再增加 Vector Index。

---

# 二十一、Cherry Studio：什么时候需要 Embedding

BM25 的典型强项：

~~~text
RK3588
E12345
/v1/models
CFG_LDO1
ISO 26262
~~~

因为字面匹配明确。

但是如果：

文档写：

~~~text
长上下文会显著增加首 Token 延迟。
~~~

用户问：

~~~text
为什么一次输入很多材料以后，要等很久才开始出字？
~~~

BM25 可能因为词不同而表现不好。

这时 Embedding 的语义匹配就有价值。

因此可以给学员一个判断：

> **资料和问题词汇高度一致 → BM25 可以先用。**

> **用户会用口语、同义词、不同表述提问 → 增加 Embedding。**

---

# 二十二、Cherry Studio：Embedding 与 Rerank 怎么配置

## 22.1 Embedding

先在：

~~~text
设置 → 模型服务
~~~

添加真正支持 Embedding 的模型。

常见模型类别包括：

- BGE；
- text-embedding；
- Jina Embeddings；
- Qwen Embedding。

创建 / 编辑 Knowledge Base 时选择：

> Embedding Model。

如果不需要：

> 选择 None。

重要注意：

> **更换 Embedding 后需要重新索引，旧向量不能和新向量空间直接混用。**

## 22.2 Rerank

同样需要在 Provider / Model Service 中加入真正支持 Rerank 接口的模型。

然后在 Knowledge Base 的检索设置中选择 Rerank Model。

它是：

> **可选项。**

推荐调试顺序：

~~~text
Parser / Chunk 正常
        ↓
BM25 或 Vector 能召回
        ↓
Retrieval Test
        ↓
能找到正确内容，但排序不好
        ↓
再加 Rerank
~~~

不要一开始就同时打开：

- OCR；
- 高级 Parser；
- Embedding；
- Rerank；
- Agent；

否则失败时无法定位是哪一层出了问题。

---

# 二十三、能否借助 Agent 搜索，不使用向量实现知识库？

答案：

> **可以，而且至少有三种模式。**

## 23.1 BM25 RAG

~~~text
Query
 ↓
BM25
 ↓
Top-K
 ↓
LLM
~~~

没有 Embedding，也没有 Vector DB。

这是：

> **Non-vector RAG。**

Cherry Studio 当前官方明确支持。

## 23.2 Agent + Knowledge Search

将 Knowledge Base 绑定给 Agent。

模型可以在任务中决定：

~~~text
要不要查？
 ↓
搜什么？
 ↓
结果够不够？
 ↓
换关键词再搜？
 ↓
读取结果
 ↓
继续任务
~~~

底层 Retriever 可以是：

- BM25；
- Vector；
- Hybrid。

因此：

> **Agentic Retrieval 与 Vector Retrieval 不是互斥关系。**

它们回答的是两个不同问题：

~~~text
Agentic：
谁决定什么时候搜、怎么搜？

Vector / BM25：
底层用什么算法找？
~~~

## 23.3 Agent 直接搜索原始文件

有 Shell / File Tool 的 Agent 甚至可以：

~~~text
grep
ripgrep
find
全文搜索
文件读取
~~~

直接在原始文件里搜索。

例如：

~~~text
grep "131072"
→ 找到 API 文档
→ read

grep "KV Cache"
→ 找到性能测试
→ read

综合答案
~~~

完全不需要向量数据库。

这种方式特别适合：

- 代码仓库；
- Markdown；
- 配置文件；
- 日志；
- API 文档；
- 型号明确的工程资料。

---

# 二十四、Coding Agent 里的 Agentic Retrieval 到底是什么

对 Coding Agent 来说，Agentic Retrieval 通常不是“先建一个向量知识库再问答”，而是：

~~~text
任务目标
  ↓
模型判断当前缺什么上下文
  ↓
glob / tree / list
  ↓
grep / search
  ↓
read file
  ↓
根据结果调整下一次搜索
  ↓
找到足够证据
  ↓
edit / shell / test
~~~

例如用户说：

~~~text
把 API 超时时间默认改成 30 秒，并运行相关测试。
~~~

Agent 不一定预先知道配置在哪。

它可能：

~~~text
1. grep "timeout"
2. 发现多个命中
3. read config 文件
4. read 对应测试
5. 判断真正配置入口
6. edit
7. run tests
~~~

这里前 1～5 步就是典型的 Agentic Retrieval。

## 24.1 为什么这和传统 RAG 很像

两者都在解决：

> **模型当前缺少哪些外部上下文，应该怎样找到？**

传统 Pipeline RAG 通常是：

~~~text
Query
→ Retrieval System 自动 Top-K
→ 把结果塞给模型
→ 模型回答
~~~

Coding Agent 则更常见：

~~~text
Goal
→ Model
→ Search Tool
→ Observe
→ 改写搜索策略
→ Read
→ 再 Search
→ 足够以后执行
~~~

因此：

> **Agentic Retrieval 可以看成“把 Retrieval 本身纳入 Agent Loop”。**

## 24.2 但不是所有 Agent 工具都叫 Retrieval

要分清两类工具。

### Retrieval / Context Tools

目的是：

> 找到模型下一步判断所需要的信息。

例如：

- glob；
- grep；
- ripgrep；
- search_files；
- read_file；
- semantic code search；
- file search；
- web search；
- knowledge search；
- session search；
- memory search。

### Action / Execution Tools

目的是：

> 改变外部世界或者验证结果。

例如：

- edit / patch；
- shell；
- git commit；
- npm test；
- docker；
- browser click；
- SSH；
- API POST；
- deploy。

真实 Agent Loop 通常是：

~~~text
Retrieve
→ Reason
→ Act
→ Observe
→ Retrieve More
→ Act Again
→ Verify
~~~

所以更准确的说法不是：

> “Agent 工具都是 Agentic Retrieval。”

而是：

> **现代 Agent Harness 通常包含 Agentic Retrieval，再配合 Action Tools 完成闭环。**

## 24.3 前面那些 Coding Agent 是否都采用这种思路

整体上：

> **是，主流 Coding Agent 大多采用“模型主动搜索 / 读取 Workspace 上下文”的 Agentic Retrieval 思路。**

但实现方式并不完全一样。

例如 OpenCode 官方工具中就有：

- glob；
- grep；
- read；
- shell；
- edit。

官方示例任务明确是让模型自己选择 grep / glob → read → edit → shell。

Codex 的官方 Prompt Guidance 同样明确建议使用：

- rg；
- read_file；
- list_dir；
- glob_file_search；

来搜索文件和文本，再执行修改。

Hermes 也把：

- search_files；
- read_file；
- web_search；
- web_extract；
- session_search；

作为模型可主动调用的核心工具。

因此它们都体现了 Agentic Retrieval。

但要注意：

> **一个 Agent 内部可以同时存在多种上下文注入方式。**

例如：

~~~text
AGENTS.md / CLAUDE.md
→ 启动时自动注入

当前打开文件
→ UI 自动提供

Embedding Top-K
→ Pipeline Retrieval

grep / read / web_search
→ Agentic Retrieval
~~~

所以“用了 Agent”并不意味着：

> 所有 Context 都必须由 Agent 自己搜。

最好的 Harness 往往是：

> **固定上下文 + 自动 Retrieval + Agentic Retrieval 混合使用。**

---

# 二十四、Coding Agent 其实大量使用 Agentic Retrieval

对于 ZCode、Codex、Claude Code、OpenCode、DSH、Pi、Cline、Kilo、Hermes 这类 Agent，要理解一个关键点：

> **它们在理解代码库和工作区时，通常都会采用“模型主动检索 → 读取 → 判断 → 再检索”的 Agentic Retrieval 思路。**

但这不意味着它们都依赖“向量知识库”。

典型 Coding Agent 更常见的是：

~~~text
用户：
修复请求超时问题

Agent：
1. 先搜索 timeout / request timeout
2. grep / rg / glob 找到候选文件
3. read 关键代码
4. 根据 import / 调用关系继续查
5. 需要时查 Git / LSP / 文档
6. 修改代码
7. 运行测试
8. 根据错误再次搜索和读取
~~~

所以 Coding Agent 中常见的 Retrieval 工具有：

- grep / ripgrep；
- glob / find；
- 文件读取；
- Git Search / Diff / History；
- LSP definition / references；
- 文档搜索；
- Web Search；
- MCP Search；
- 有些产品还会叠加 Semantic Code Search / Vector Index。

这里一定要区分：

> **Retrieval Tool 是“找资料”的工具；Edit / Shell / Test / Browser 等是“执行动作”的工具。**

因此不能说“Agent 的所有工具都是 Agentic Retrieval”。

更准确是：

> **Agent Harness 会把 Retrieval Tools 和 Action Tools 都交给模型；其中检索相关工具通常由模型在循环中主动、迭代地调用，这部分就是 Agentic Retrieval。**

对 Coding Agent 来说，很多场景甚至不需要预先做 Embedding：

~~~text
grep / rg
→ read
→ follow references
→ read more
→ act
~~~

就已经能很好地完成代码库检索。

---

# 二十四、两类 RAG 不应该叫“搜索 RAG vs 向量 RAG”这么简单

建议培训做一个二维图。

## 第一维：检索算法

~~~text
Keyword / BM25
Vector / Dense
Hybrid
Full-text / grep
SQL
Search Engine
Web Search
~~~

## 第二维：检索控制方式

~~~text
Pipeline RAG
vs
Agentic Retrieval
~~~

所以可以组合成：

| 控制方式 | BM25 | Vector | Hybrid / 多工具 |
|---|---:|---:|---:|
| Pipeline RAG | 可以 | 可以 | 可以 |
| Agentic Retrieval | 可以 | 可以 | 可以 |

关键结论：

> **Agentic RAG 不是一种新的向量算法，而是一种由模型主动控制检索流程的工作方式。**

---

# 二十五、从“知识库产品”上升到“部门 Knowledge Architecture”

这一部分培训要再往前走一步：

> **部门知识库不应该绑定在 Cherry Studio、Open WebUI 或某一个 Agent 上。**

更合理的架构是：

~~~text
Source of Truth
Git / Wiki / 文件库 / DB / API
        ↓
Parse / Metadata / ACL
        ↓
BM25 / Full-text / Vector Index
        ↓
Rerank / Search / grep / read / SQL / API
        ↓
Open WebUI / Cherry Studio / Agent
~~~

其中：

- Source 是长期资产；
- Index 是可以重建的派生资产；
- Retrieval Tool 是访问方式；
- Client / Agent 是可替换入口。

因此三个工具在部门知识体系中的推荐定位是：

| 工具 | 推荐角色 | 主要知识形态 | 主要 Retrieval |
|---|---|---|---|
| Open WebUI | 部门共享 Knowledge Service / AI Portal | 同步后的共享 Knowledge + ACL | Hybrid RAG、Native Knowledge Tools、grep、kb_exec |
| Cherry Studio | 个人 Knowledge Workspace | 专题文件、Notes、Folder、Link、本地 KB | BM25 起步，按需 Embedding / Rerank，绑定 Agent |
| Coding / General Agent | 工程与研究任务执行层 | Repo、Workspace、Git、API、DB、共享 KB | rg/grep/read/LSP/Git/API/MCP + 可选语义检索 |

因此：

> **部门知识建设的对象应该是“知识源 + 元数据 + 权限 + 检索测试集”，而不是某个客户端生成的 Embedding。**

完整架构文档：

~~~text
docs/architecture/department-knowledge-architecture.md
~~~

---

# 二十五、非常适合现场做的 Cherry RAG Demo

【录屏占位 KB-R01｜P0｜60–90 秒】Cherry：建立知识库 → 添加同源资料 → Embedding=None/BM25 → Retrieval Test → 提问。

【录屏占位 KB-R02｜P0｜60–90 秒】Cherry：同一问题切换 BM25 / Embedding /（如可用）Rerank，展示召回变化。必须使用同一资料、同一问题。


准备三份我们自己的真实材料：

1. qwen3.6 API 说明；
2. Thinking 实测；
3. model-metric 长上下文测试。

## 问题 A：精确词

~~~text
qwen3.6 的 max_model_len 是多少？
~~~

BM25 应该很容易找到：

~~~text
131072
~~~

## 问题 B：换一种说法

资料写：

~~~text
长上下文导致 TTFT 显著增加。
~~~

用户问：

~~~text
为什么我一次性塞很多材料以后，模型很久才开始回答？
~~~

可以对比：

- Embedding=None / BM25；
- Embedding 开启；

看召回结果变化。

## 问题 C：跨文件综合问题

~~~text
当前内网模型有哪些因素会影响 Agent 连续调用体验？
~~~

让 Agent 分别搜索：

- Thinking；
- Long Context；
- TTFT；
- KV Cache；
- 并发；

再综合回答。

这样一套 Demo 可以自然讲出：

~~~text
Keyword Retrieval
→ Vector Retrieval
→ Rerank
→ Agentic Retrieval
~~~

---

# 二十六、Open WebUI 与 Cherry Studio 怎么选

不是简单评价哪个好。

| 场景 | Open WebUI | Cherry Studio |
|---|---|---|
| 部门统一 Web 入口 | 很适合 | 更偏个人终端 |
| 多用户 / 集中部署 | 强项 | 非主要定位 |
| 个人桌面多模型 | 可以 | 很适合 |
| 多 Provider 配置 | 支持 | 很方便 |
| 可复用助手 | Workspace Model | Assistant |
| 知识库 | 成熟 | 成熟，且当前明确支持无 Embedding 的 BM25 |
| Hybrid RAG | BM25 + Vector + Rerank | BM25 与向量索引均存在，组合策略以当前版本设置为准 |
| Agentic Knowledge | Native Knowledge Tools / kb_exec | Agent 绑定 Knowledge |
| MCP / Tools | 支持 | 支持 |
| Drawing | 外部图像 Backend | 独立 Drawing 使用体验明显 |
| 内网 qwen3.6 | 适合作为统一服务入口 | 适合作为工程师个人桌面入口 |

因此培训可以总结：

> **Open WebUI 用来讲“部门统一 AI 门户”；Cherry Studio 用来讲“个人 AI 工作台”。**

但二者都可以从 Chat 逐步增加：

> Knowledge → RAG → Tools → Agent。

---

# 二十七、这部分最后只留下五个认知

第一：

> **Open WebUI 和 Cherry Studio 都不再只是 Chat UI，而是逐步向 Agent 工作台演进。**

第二：

> **Assistant / Workspace Model 本质上是“模型 + Prompt + 参数 + 可选知识和工具”的可复用配置。**

第三：

> **RAG 的本质是 Retrieval → Context → Generation，不等于向量数据库。**

第四：

> **BM25 负责字面匹配，Embedding 负责语义召回，Rerank 负责候选精排。**

第五：

> **Agentic Retrieval 的关键变化不是换了一种搜索算法，而是让模型自己决定什么时候检索、如何检索、是否继续检索。**

---

# 二十八、官方资料

## Open WebUI

- Provider Connection: https://docs.openwebui.com/getting-started/quick-start/connect-a-provider/
- Workspace Models: https://docs.openwebui.com/features/workspace/models/
- Knowledge: https://docs.openwebui.com/features/workspace/knowledge/
- RAG: https://docs.openwebui.com/features/chat-conversations/rag/
- Reasoning Models: https://docs.openwebui.com/features/chat-conversations/chat-features/reasoning-models/
- Chat Parameters: https://docs.openwebui.com/features/chat-conversations/chat-features/chat-params/
- Agentic Search: https://docs.openwebui.com/features/chat-conversations/web-search/agentic-search/

## Cherry Studio

- Official Docs: https://cherryai.com/docs/en/
- Model Service: https://cherryai.com/docs/en/pre-basic/settings/providers/
- Chat / Assistant: https://cherryai.com/docs/en/cherrystudio/preview/chat/
- Knowledge Base: https://cherryai.com/docs/en/knowledge-base/knowledge-base/
- Web Search: https://cherryai.com/docs/en/pre-basic/websearch/
- Agent: https://cherryai.com/docs/en/advanced-basic/agent/


---

# 二十九、截图与录屏准备清单

> 本章知识库相关素材尽量与教学版知识库讲义共用 `KB-xx` / `KB-Rxx` 编号，避免同一画面重复拍摄。

| 编号 | 类型 | 优先级 | 内容 | 状态 |
|---|---|---:|---|---|
| OW-01 | 截图 | P0 | Open WebUI 统一入口 / 模型选择 | ⬜ |
| OW-02 | 截图 | P0 | Provider / Connection | ⬜ |
| OW-03 | 截图 | P1 | Chat → Workspace Model → Knowledge → Tool | ⬜ |
| OW-04 | 截图 | P0 | System Prompt + Advanced Parameters | ⬜ |
| OW-05 | 截图 | P1 | Thinking UI 与实际协议参数对照 | ⬜ |
| OW-06 | 截图 | P1 | Vision vs Image Generation | ⬜ |
| CH-01 | 截图 | P0 | Cherry Studio 个人工作台总览 | ⬜ |
| CH-02 | 截图 | P0 | Custom Provider | ⬜ |
| CH-03 | 截图 | P1 | Assistant vs Agent | ⬜ |
| CH-04 | 截图 | P1 | Thinking / Context 参数 | ⬜ |
| CH-05 | 截图 | P1 | Vision vs Drawing | ⬜ |
| KB-04~05 | 复用截图 | P0 | BM25 / Embedding 对比 | ⬜ |
| KB-12~17 | 复用截图 | P0/P1 | Cherry KB / Open WebUI Shared KB | ⬜ |
| WB-R01 | 录屏 | P1 | Open WebUI Provider → Chat | ⬜ |
| WB-R02 | 录屏 | P0 | Cherry Provider → 内网模型 Chat | ⬜ |
| KB-R01 | 录屏 | P0 | Cherry 从建库到问答 | ⬜ |
| KB-R02 | 录屏 | P0 | BM25 / Embedding / Rerank 对比 | ⬜ |
