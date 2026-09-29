# 培训讲义：从 Chat 到 Agent——为什么只有聊天还不够

> 模块二：为什么只有 Chat 不够  
> 核心问题：同一个模型，放进不同的工作环境后，为什么能完成完全不同级别的任务？  
> 资料核实：2026-09-29

## 一、不要先问“哪个 Agent 最好”

这一章不从 ZCode、Codex、OpenCode、DSH、Pi 的菜单开始。

先问一个更稳定的问题：

> **一个模型怎样从“回答问题”，变成“围绕目标持续工作”？**

模型本身主要做两件事：

- 根据上下文判断下一步；
- 生成文本、结构化结果或 Tool Call。

真正让它能够读项目、改文件、跑命令、看结果、继续修复的，是模型外面的执行环境。

因此培训使用下面这个统一视角：

~~~text
Agent = Model + Harness
~~~

这里的 **Harness** 可以理解为“包在模型外面的一整套智能体运行与工程环境”。

DeepSeek Harness 官方当前甚至直接用“Agent = Model + Harness”描述这一关系。

---

## 二、Chat 与 Agent 不是简单的两个物种，而是一条连续谱

过去很容易这样分：

~~~text
OpenWebUI / Cherry Studio = Chat
Codex / OpenCode / ZCode = Agent
~~~

到 2026 年，这种二分已经不够准确。

Open WebUI 已经支持服务端 Tool Loop、MCP、OpenAPI Tool Server 和 Open Terminal；Cherry Studio 也已经提供 Workspace / Agent、文件、命令和 MCP。

因此更准确的区分应该是：

| 维度 | 对话优先工作台 | 工程 Agent / Coding Agent |
|---|---|---|
| 默认入口 | 会话 | Workspace / Repository / Task |
| 默认对象 | 一段上下文 | 一个持续变化的项目环境 |
| 人的角色 | 人不断发起下一轮 | 人给目标、约束和关键判断 |
| 文件 | 附件、知识库为主 | 工作区文件是核心状态 |
| Shell | 可选扩展 | 常见核心能力 |
| Git | 通常不是主线 | 常见工程闭环 |
| 工具调用 | 可以支持 | 通常深度参与循环 |
| 任务循环 | 一轮或少量多轮 | Read → Act → Observe → Verify → Iterate |
| 结果 | 回答、内容 | 修改后的工程状态 + 验证结果 |

所以培训不说“Chat 已经过时”。

更准确的说法是：

> **Chat 适合孤立问题；复杂工程任务需要更完整的 Harness。**

---

## 三、Open WebUI / Cherry Studio：从 Chat 工作台走向 Knowledge、RAG 与 Agent

这一部分不再只介绍两个产品，而是用它们解释能力如何逐层叠加：

~~~text
Raw Model
→ Chat
→ Assistant / Model Preset
→ Files / Knowledge
→ RAG
→ Web / MCP / Tools
→ Agentic Retrieval / Agent
~~~

### 3.1 Open WebUI

更适合作为：

> **部门统一 AI 门户 / 集中式模型工作台。**

重点演示：

- OpenAI-compatible Provider 接入；
- Workspace Model；
- System Prompt 与参数；
- Vision / Image Generation 的区别；
- Thinking UI 与真实后端 Thinking 参数的区别；
- Knowledge Base；
- Vector RAG；
- BM25 + Vector + Rerank Hybrid RAG；
- Native Knowledge Tools / kb_exec Agentic Retrieval。

### 3.2 Cherry Studio

更适合作为：

> **工程师个人桌面多模型 AI 工作台。**

重点演示：

- Custom Provider；
- Assistant 与 Topic；
- Assistant Prompt / 默认模型 / 参数；
- Thinking Depth；
- Vision / Drawing；
- Knowledge Base；
- Embedding Model；
- Rerank Model；
- Embedding=None 时的 BM25 Knowledge Retrieval；
- Knowledge 绑定 Agent；
- MCP / Web Search / Work。

### 3.3 用 Cherry Studio 纠正“RAG = 向量数据库”

当前 Cherry Studio 官方知识库允许：

> **Embedding Model = None。**

此时主要使用 BM25 关键词索引与检索。

所以：

> **RAG 的本质是 Retrieval → Context Augmentation → Generation；向量检索只是 Retrieval 的一种方法。**

培训进一步区分：

~~~text
检索算法：
BM25 / Vector / Hybrid / grep / Search Engine

检索控制：
Pipeline RAG / Agentic Retrieval
~~~

因此 Agentic RAG 与 Vector RAG 不是互斥概念。

详细讲义：

~~~text
docs/chapters/02-chat-workbenches-and-rag.md
~~~

---

## 四、从“为什么需要 Agent”过渡到“Agent 到底由什么组成”

到这里先不展开逐个 Agent 产品比较。

本章只需要建立：

> **Chat 更擅长 Prompt → Answer；工程 Agent 更强调 Goal → Plan → Read → Act → Observe → Verify → Iterate → Deliver。**

至于：

- 为什么同一个模型放进 Codex、Claude Code、OpenCode、Hermes、Pi 等 Harness 后表现不同；
- AGENTS.md / CLAUDE.md / SOUL.md / MEMORY.md 分别是什么；
- Workspace、Context、Plan、Memory、Tool、Skill、MCP、Permission、Sandbox、Sub-agent 的关系；
- Browser Use / Computer Use；
- CLI / GUI / IDE 如何选择；
- Kimi K3 固定模型的 FrontierHarness 受控评测；

统一放到下一章：

~~~text
docs/chapters/04-agent-common-mechanisms.md
~~~

这样避免把本章变成 Agent 产品功能列表。

---

## 五、从 Prompt → Answer 到 Goal → Deliver

Chat 的典型循环：

~~~text
Prompt
  ↓
Model
  ↓
Answer
~~~

Agent 的典型循环：

~~~text
Goal
 ↓
Plan
 ↓
Read
 ↓
Act
 ↓
Observe
 ↓
Verify
 ↓
Iterate
 ↓
Deliver
~~~

这里最关键的变化不是“可以调用 Shell”。

而是：

> **模型的输出不再天然等于任务结束。**

模型输出可能只是：

- 下一条命令；
- 一次文件修改；
- 一个 Tool Call；
- 一个候选方案。

Harness 会把执行结果重新放回上下文，让模型继续判断。

---

## 六、统一 Demo：同一个“鹈鹕骑自行车”题同时测试模型和 Harness

这道题建议承担两个教学任务。

### 6.1 第一轮：不同模型，同一种 Chat 工作方式

所有模型使用同一 Prompt：

> 创建一个单文件 HTML，用 SVG、CSS 和 JavaScript 生成一只鹈鹕骑自行车的循环动画。不得使用外部图片或第三方库。自行车轮子要转动，腿要踩踏板，鹈鹕身体有轻微起伏，页面可直接在浏览器打开。

观察：

- 是否遵循单文件要求；
- SVG 结构是否完整；
- JS / CSS 是否可运行；
- 鹈鹕和自行车是否能正确组合；
- 动作是否协调；
- 第一次结果是否可直接使用。

这一轮主要观察 **Model Capability**。

### 6.2 第二轮：同一个模型，Chat 与 Agent 对比

Chat：

~~~text
Prompt
→ 返回 HTML 代码
→ 人复制
→ 人保存
→ 人打开浏览器
→ 人发现问题
→ 人重新描述问题
~~~

Agent：

~~~text
Goal
→ 创建文件
→ 启动页面
→ 浏览器观察
→ 发现轮子/腿/构图问题
→ 修改
→ 再验证
→ 交付文件 + Diff
~~~

这一轮主要观察 **Harness Capability**。

这样可以避免一个常见错误：

> 把“Agent 有浏览器、有文件工具带来的优势”，误认为完全是“模型更聪明”。

---

## 七、这道 Demo 为什么适合培训

“鹈鹕骑自行车”不是严谨 Benchmark，但非常适合现场教学。

原因有五个：

1. **任务短**：几分钟内可以看到结果，不需要大型工程环境；
2. **组合不常见**：不是最常见的网页模板，能观察组合生成能力；
3. **跨能力**：同时涉及自然语言理解、SVG 几何、CSS/JS、动画逻辑；
4. **结果可视化**：学员不需要看大量代码就能判断明显问题；
5. **天然适合 Agent 闭环**：生成后必须真正运行，才知道动画是否正确。

它的局限也必须明确：

- 单题不能代表模型总体能力；
- 动画审美有主观性；
- 采样随机性会影响结果；
- 不适合据此做严肃模型排名。

因此统一定位为：

> **能力演示题，不是标准化 Benchmark。**

若需要形成更可靠对比，应固定 Prompt、参数和运行环境，至少重复多次，并配合代码正确性和可执行性指标。

---

## 八、这一章最后只留下三个结论

第一：

> **Chat 和 Agent 不是“旧工具”和“新工具”的关系，而是工作复杂度和执行闭环不同。**

第二：

> **从 Chat 到 Agent，核心变化是从 Prompt → Answer 走向 Goal → Act → Observe → Verify → Deliver。**

第三：

> **下一步不要继续记产品按钮，而要把 Agent 拆开，看清 Model 外面的 Harness 为什么决定它能看到什么、能做什么、能否持续做对。**

---

## 九、参考资料

- DeepSeek Harness：官方将其描述为开源 Agent Harness，并明确提出“Agent = Model + Harness”：https://www.deepseek.com/harness/
- DeepSeek Harness GitHub：https://github.com/deepseek-ai/deepseek-harness
- Pi：官方定位为 minimal agent harness：https://pi.dev/
- OpenCode Agent / Tools / Skills：https://opencode.ai/docs/
- Open WebUI Tools / Server-side Tool Calling：https://docs.openwebui.com/
- Cherry Studio Agent / MCP：https://cherryai.com/docs/
- Codex：项目规则与 Sandbox/Approval 以当前 OpenAI Codex 官方仓库和文档为准。
