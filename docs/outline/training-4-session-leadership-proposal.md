# AI 大模型与 Agent 工程实践系列培训方案（领导审核稿）

> 日期：2026-09-30
> 建议安排：4 次专题讲座，每次约 1.5～2 小时
> 面向对象：部门技术人员及相关技术管理人员

## 一、总体目标

本次培训不以介绍具体 AI 产品为主，而是围绕部门实际工作，帮助技术人员建立从模型调用、知识使用、Agent 工具链到完整工程实践的统一认识。

总体思路：

1. 从真实模型调用入手，理解模型、API、Chat 和 Agent 的关系；
2. 围绕部门知识库建设需求，建立知识资产分类、检索、治理和使用方法；
3. 抛开不同 Agent 的界面差异，理解 Harness、Workspace、上下文、工具和运行环境等共性机制；
4. 结合 BMQuiz、FileCheck、model-metric、IPsec、HyperFrames 等真实项目，展示 Agent 如何参与需求分析、技术调研、开发、测试、发布和部署。

培训统一强调：

> 模型负责判断和生成，工具负责执行，自动化测试负责验证，人负责目标、约束和最终判断。

## 二、第一讲：从模型 API 到 Agent——看懂 AI 应用背后的工作逻辑

### 要解决的问题

- 聊天界面背后到底发生了什么？
- 同一个模型为什么可以被不同工具调用？
- 模型能力和应用能力有什么区别？
- Chat 与 Agent 的边界在哪里？

### 知识点

- HTTP、JSON、Request、Response、流式输出；
- OpenAI Chat / Responses / Anthropic Messages 等常见接口形态；
- Token、Context、Thinking、Tool Calling、Vision；
- Prefill、Decode、TTFT、TPS、并发等工程指标；
- Chat 的 Prompt → Answer；
- Agent 的 Goal → Plan → Read → Act → Observe → Verify → Iterate → Deliver；
- Model、Harness、Context、Workspace、Tools、Runtime 的关系。

### 案例演示

- Cherry Studio Network：模型列表、普通对话、多轮对话、图片输入、流式返回；
- 内网 Qwen API 自动测试；
- model-metric 性能观测；
- Chat 与 Agent 完成同一个代码修改任务的对照。

### 预期效果

让学员不再把 AI 理解成一个聊天网页，而是理解为“模型能力 + 应用编排 + 工具环境”的组合。

## 三、第二讲：部门知识库建设——让 AI 可靠使用我们的知识

### 要解决的问题

- 部门到底有哪些知识资产？
- 哪份资料是权威版本？
- 文档、代码、数据库、日志和实时数据是否应该采用同一种处理方式？
- 为什么资料已经进入知识库，模型仍可能回答不可靠？
- Cherry Studio、Open WebUI 和 Agent 怎样共用部门知识？

### 知识点

- Source of Truth 与知识资产分类；
- Parse、OCR、Chunk、Metadata；
- 全文检索、BM25、Embedding、Vector、Hybrid、Rerank；
- Context Window、长上下文召回、Context Budget、Evidence Budget；
- 文档、代码、数据库、API、日志、指标的不同访问机制；
- 权限、版本、重复、冲突、过期、引用与更新；
- 知识库评测与验收方法。

### 案例演示

- 同一套真实资料分别在 Cherry Studio、Open WebUI、Agent 中使用；
- 精确编号查询与语义查询的不同检索方式；
- 新旧版本冲突案例；
- 代码资料直接通过 Search / Read / Git 使用，而不是全部向量化。

### 预期效果

推动部门形成知识资产分类、入库规范、检索策略、权限与版本治理、验收测试集及统一知识架构。

## 四、第三讲：深入 Agent——掌握共性，而不是记住不同界面

### 要解决的问题

- 为什么 Codex、ZCode、OpenCode、Hermes、WorkBuddy 看起来不同，却可以用同一套方法理解？
- 一个 Agent 真正由哪些部分组成？
- 为什么有些 Agent 能操作浏览器、终端和服务器，有些不能？
- Agent 怎样接入部门已有系统能力？
- 换一个 Agent 时应该检查和配置什么？

### 知识点

- Harness、Workspace、Context、Memory、Plan、Project Rules；
- Session、Context Compaction、Permission、Observability；
- Git、Python、Node.js、Browser、Docker、SSH 等运行环境；
- File、Shell、Git、Browser、Server 的操作机制；
- Playwright、CDP、Browser Use、Computer Use 的区别；
- API、Tool、MCP、Skill、Plugin、Command、Hook 的关系；
- 权限边界和结果验证。

### 案例演示

- 同一个代码任务在不同 Agent 中的执行过程；
- Browser 操作：页面交互、控制台、截图与结果验证；
- BMQuiz / model-metric 的服务器操作；
- Raw API → Tool → MCP → Skill 的逐层封装；
- WorkBuddy 等 Chat 界面背后的可执行 Workspace。

### 预期效果

让技术人员面对新的 Agent 产品时，能够从模型、上下文、Workspace、工具、运行环境和权限等底层要素快速判断其能力，而不是重新学习一套界面。

## 五、第四讲：Agent 工程实战——从需求到开发、测试、发布和部署

### 要解决的问题

- 为什么“让 AI 写代码”不等于完成工程任务？
- 怎样从需求和约束开始使用 Agent？
- 怎样管理多文件修改和版本变更？
- 怎样证明 Agent 的修改真的正确？
- 怎样把开发、测试、打包、发布和部署串成完整闭环？
- 一次成功实践怎样沉淀为团队资产？

### 知识点

统一工程流程：

Problem → Requirement → Constraint → Research → Architecture → Plan → Implement → Test → Visual / Runtime QA → Review → Release → Deploy → Verify

重点讲解：

- 需求、约束与验收标准；
- 技术调研与架构；
- Git、Diff、Review、回滚；
- 单元测试、集成测试、Browser QA、运行状态验证；
- CI/CD、制品、发布和部署；
- AGENTS.md、Skill、脚本、测试、CI、知识和文档等可复用资产。

### 案例演示

- BMQuiz：Web 应用从需求、架构、Agent 开发、Playwright Visual QA、GitHub Actions、Docker 到部署；
- FileCheck：Windows 本地工具从技术选型、Core/CLI/GUI、兼容性测试、PyInstaller 到 GitHub Release；
- model-metric：指标语义、服务运行和部署验证；
- IPsec VPN：从测试数据到假设、分析和工程验证；
- HyperFrames：从文案、分镜、HTML 动画、预览到自动渲染；
- 授权环境下的接口兼容性和安全验证：从范围、证据、修复到回归。

### 预期效果

让学员理解 Agent 的价值不只是“生成代码”，而是参与一个有目标、有约束、有证据、有验证、有交付的完整工程过程。

## 六、整体培训价值

四次培训分别解决四个问题：

| 讲座 | 核心问题 | 形成的能力 |
|---|---|---|
| 第一讲 | AI 应用背后到底怎么工作？ | 看懂模型、API、Chat、Agent 与工具关系 |
| 第二讲 | 部门知识怎样可靠给 AI 使用？ | 参与知识资产建设、治理和验收 |
| 第三讲 | 怎样真正使用不同 Agent？ | 掌握 Agent 共性机制和环境配置方法 |
| 第四讲 | 怎样让 Agent 参与真实工程？ | 建立需求—开发—测试—发布—部署闭环 |

最终目标不是让大家熟练某一个 AI 产品，而是：

> 面对新的模型、新的 Agent 和新的业务任务，能够判断应该使用什么模型、准备什么知识、提供什么工具、建立什么验证机制，并将有效做法沉淀为可复用的工程资产。
