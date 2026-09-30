# 培训截图与录屏总清单

> 日期：2026-09-30  
> 适用范围：当前仓库已有讲义 `01-intranet-qwen-api.md`、`02-chat-to-agent-harness.md`、`02-chat-workbenches-and-rag.md`、`03-department-knowledge-base*.md`、`04-agent-common-mechanisms.md`、`05-agent-tools-real-world.md`、`06-api-mcp-skill-plugin-command-hook.md`、`07-reusable-agent-assets.md`。  
> 目的：把“讲什么”转成“需要提前准备什么证据和演示素材”，避免制作 PPT 时临时补截图。

---

# 1. 优先级与状态

优先级：

- **P0**：培训必须准备。没有现场 Demo，也应该有截图/预录作为备用。
- **P1**：强烈建议。明显提升理解，但可根据培训时长裁剪。
- **P2**：可选。主要用于补充说明或深入讨论。

状态：

- ⬜ 未准备
- 🟨 已截图/录制，待裁剪、标注或脱敏
- ✅ 可直接用于培训/PPT

---

# 2. 截图与录屏统一规范

## 2.1 截图

建议：

- 优先 16:9 桌面环境，方便后续进入 PPT；
- 浏览器/客户端缩放保持一致，文字必须在投影环境下可读；
- 截图前关闭无关窗口、通知和个人信息；
- API Key、Token、账号、Cookie、SSH Key、真实内网地址、真实敏感业务数据按培训范围脱敏；
- 尽量截“真实界面 + 真实结果”，概念图只用于真实界面无法直接表达的机制；
- 同一组对比截图必须固定模型、问题、资料和条件；
- 不把官方文档截图写成“我们的实测”，官方材料必须注明来源。

建议文件名：

~~~text
<编号>-<简短说明>.png

例如：
API-NET-04C-context-diff.png
AGENT-WB-02-workspace.png
KB-05-bm25-vs-embedding.png
~~~

## 2.2 录屏

建议：

- 原始录屏优先 1920×1080；
- 鼠标指针保留，关键点击不要太快；
- 每段录屏尽量只回答一个问题；
- 优先录“动态过程”，静态配置不要为了录屏而录屏；
- 长时间 Thinking / Build / Install 等等待过程后期剪掉，但原始视频保留；
- 现场 Demo 有失败风险的内容必须提前准备预录；
- 涉及对比时，固定输入、模型和数据，不通过后期剪辑制造不真实差异；
- Agent 录屏应尽量保留 Tool Call、Terminal、Diff、Test、Browser 等证据，不只录最终回答。

建议文件名：

~~~text
<编号>-<简短说明>.mp4

例如：
API-R02-multiturn-context.mp4
KB-R05-agent-multisource-retrieval.mp4
AGENT-R05-tool-loop.mp4
~~~

---

# 3. P0：优先一次性准备的素材

如果时间有限，先完成下面这一批。

| 编号 | 类型 | 内容 | 主要讲义 | 状态 |
|---|---|---|---|---|
| API-01 | 截图 | /v1/models + /version | 第一章 API | ⬜ |
| API-NET-01~07 | 截图 | Cherry Network：models / Chat / Context / Vision / SSE | 第一章 API | ⬜ |
| API-POST-01~02 | 截图 | 自编 Postman：GET models / POST chat | 第一章 API | ⬜ |
| API-TEST-01~02 | 截图 | v3 自动测试总览 + record 断言 | 第一章 API | ⬜ |
| MM-01~03 | 截图 | model-metric 总览 / Benchmark / Context&Endpoint | 第一章 API / 案例 | ⬜ |
| API-03 | 截图 | Thinking OFF/ON 实测 | 第一章 API | ⬜ |
| API-04~05 | 截图 | Tool Call + Tool Result | 第一章 API | ⬜ |
| API-08 | 截图 | /metrics 原始指标 | 第一章 API | ⬜ |
| API-R01~04 | 录屏 | models / 多轮 Context / Vision / SSE | 第一章 API | ⬜ |
| API-R09 | 录屏 | Postman GET/POST → Cherry Network 对照 | 第一章 API | ⬜ |
| MM-R01~02 | 录屏 | Postman/API Benchmark → model-metric 指标变化 | 第一章 API / 案例 | ⬜ |
| API-R07 | 录屏 | 完整 Tool Loop | 第一章 API | ⬜ |
| API-R08 | 录屏 | 同模型 Chat vs Agent | 第一章 / Chat→Agent | ⬜ |
| CHAT-01~03 | 截图/图示 | Chat vs Agent 核心差异 | Chat→Agent | ⬜ |
| CHAT-R01~03 | 录屏 | 最小闭环 + 鹈鹕 Chat/Agent 对照 | Chat→Agent | ⬜ |
| OW-01~02 | 截图 | Open WebUI 总览与 Provider | 工作台/RAG | ⬜ |
| OW-04 | 截图 | System Prompt / Parameters | 工作台/RAG | ⬜ |
| CH-01~02 | 截图 | Cherry 总览与 Custom Provider | 工作台/RAG | ⬜ |
| WB-R02 | 录屏 | Cherry Provider → 内网模型 | 工作台/RAG | ⬜ |
| KB-01~06 | 截图/图示 | 外部知识、架构、RAG、BM25/Embedding、Parse/Chunk | 知识库 | ⬜ |
| KB-08~11 | 图示/截图 | 两层召回、Evidence Budget、Rerank、三种 Retrieval | 知识库 | ⬜ |
| KB-12~17 | 截图 | Cherry KB + Open WebUI Shared KB | 知识库 | ⬜ |
| KB-18~22 | 截图/图示 | Agent 多源取证、统一架构、ACL、引用 | 知识库 | ⬜ |
| KB-R01~03 | 录屏 | Cherry 建库/检索 + Open WebUI Shared KB/ACL | 知识库 | ⬜ |
| KB-R05 | 录屏 | Agent 跨源逐步取证 | 知识库 | ⬜ |
| AGENT-01~04 | 图示/截图 | Harness、受控评测、AGENTS.md、Workspace | Agent 共性 | ⬜ |
| AGENT-WB-01~03 | 截图 | WorkBuddy Chat / Workspace / Skill | Agent 共性 | ⬜ |
| AGENT-07~09 | 截图 | Tool Trace / MCP / Skill | Agent 共性 | ⬜ |
| AGENT-12~13 | 截图 | Sandbox/Approval + Verification | Agent 共性 | ⬜ |
| AGENT-16 | 截图 | Runtime Backend | Agent 共性 | ⬜ |
| AGENT-R02 | 录屏 | WorkBuddy Chat → Workspace → Artifact | Agent 共性 | ⬜ |
| AGENT-R04~05 | 录屏 | 读取项目规则 + Tool Loop | Agent 共性 | ⬜ |
| AGENT-R07 | 录屏 | Skill 前后流程对比 | Agent 共性 | ⬜ |
| TOOL-01~06 | 图示/截图 | Tool Loop、Workspace、Shell/Git、验证层次、Browser 分类 | Agent 真实世界 | ⬜ |
| TOOL-07~11 | 截图/图示 | Visual QA、SSH/Docker、API、CI、完整工程闭环 | Agent 真实世界 | ⬜ |
| TOOL-R01~04 | 录屏 | Read/Edit/Test/Diff、Visual QA、SSH 部署、CI | Agent 真实世界 | ⬜ |
| ZCODE-01~05 | 截图 | 鹈鹕：Workspace → File → Browser → Iterate → Review | ZCode 主案例 | ⬜ |
| ZCODE-06~12 | 截图 | Sensor Guard：Rules → Test Fail → Search/Edit → Pass → Diff → Permission | ZCode 主案例 | ⬜ |
| ZCODE-R01~02 | 录屏 | 鹈鹕 Browser 闭环 + Sensor Guard 工程闭环 | ZCode 主案例 | ⬜ |
| ENV-01~04 | 图示/截图 | Harness vs Runtime、环境 Preflight、Local/WSL/Docker/SSH、内网依赖源 | Agent 环境 | ⬜ |
| ENV-R01~02 | 录屏 | 缺工具→补环境→成功；公网源失败→内网源成功 | Agent 环境 | ⬜ |
| CONNECT-01~04 | 图示 | API/Tool/MCP/Skill 分层与关系 | Agent 工具接入 | ⬜ |
| CONNECT-06~09 | 图示/截图 | 端到端示例、Skill 目录、权限拆分、决策表 | Agent 工具接入 | ⬜ |
| CONNECT-R01~03 | 录屏 | Raw API → MCP Tool → Skill+MCP | Agent 工具接入 | ⬜ |
| ASSET-01~08 | 图示/截图 | 仓库资产地图、资产路由、规则/Skill/Memory/CI 边界 | 可复用资产 | ⬜ |
| ASSET-R01~02 | 录屏 | 资产路由互动 + 长 Prompt → Skill 对比 | 可复用资产 | ⬜ |
| ASSET-ZC-01~03 | 截图 | ZCode AGENTS.md/Memory、Command/Skill、Plugin 资产边界 | 可复用资产 | ⬜ |

---

# 4. 第一章：模型怎么调用

完整占位位于：

`docs/chapters/01-intranet-qwen-api.md`

## 4.1 静态

| 编号 | 优先级 | 拍什么 | 关键要求 | 状态 |
|---|---:|---|---|---|
| API-01 | P0 | /v1/models + /version | model id、context、version | ⬜ |
| API-NET-01 | P0 | Cherry 模型列表 | 与下一张 models Request 对应 | ⬜ |
| API-NET-02 | P0 | GET /v1/models Request/Response | URL/Method/Response 清晰 | ⬜ |
| API-NET-03 | P0 | 第一轮 Chat Payload | model/messages/input/stream | ⬜ |
| API-NET-04A~C | P0 | 第一/第二轮 Request + Diff | 明确上下文如何附加 | ⬜ |
| API-NET-05~06 | P0 | Vision Payload | 文本+图像实际结构 | ⬜ |
| API-NET-07 | P0 | SSE/EventStream | 能看到流式事件 | ⬜ |
| API-POST-01 | P0 | 自编 Postman GET /v1/models | Method/URL/Status/Response | ⬜ |
| API-POST-02 | P0 | 自编 Postman POST /v1/chat/completions | Body/messages/stream/usage | ⬜ |
| API-TEST-01 | P0 | v3 终端结果 | 28 PASS / 1 SKIP | ⬜ |
| API-TEST-02 | P0 | 单条 record JSON | Request/Response/attempts/analysis | ⬜ |
| API-02 | P1 | Token speed Race Mode | 5/30/120 tok/s | ⬜ |
| API-03 | P0 | Thinking OFF/ON | 来自真实测试 | ⬜ |
| API-04~05 | P0 | Tool Call / Tool Result | 完整闭环两张图 | ⬜ |
| API-06~07 | P1 | Vision / Vision Tool | 固定 Ground Truth | ⬜ |
| API-08~09 | P0/P1 | metrics + model-metric | 原始指标与 UI 对照 | ⬜ |
| MM-01 | P0 | model-metric 总览 | running/waiting/TPS/KV/coverage | ⬜ |
| MM-02 | P0 | API Benchmark | 并发/TTFT/吞吐/Token | ⬜ |
| MM-03 | P1 | Context Window + Endpoint Compatibility | 与 API 章节对应 | ⬜ |
| API-10~11 | P1 | 鹈鹕 Chat / Agent | 同模型同 Prompt | ⬜ |

## 4.2 录屏

| 编号 | 优先级 | 动态过程 | 状态 |
|---|---:|---|---|
| API-R01 | P0 | 刷新模型 → /v1/models | ⬜ |
| API-R02 | P0 | 连续两轮对话 → Context 变化 | ⬜ |
| API-R03 | P0 | 图片输入 → Payload | ⬜ |
| API-R04 | P0 | SSE → 聊天窗口逐步显示 | ⬜ |
| API-R05 | P1 | Tokens/s Race Mode | ⬜ |
| API-R06 | P1 | Thinking OFF/ON 体感 | ⬜ |
| API-R07 | P0 | 完整 Tool Loop | ⬜ |
| API-R08 | P0 | Chat vs Agent | ⬜ |
| API-R09 | P0 | Postman GET/POST → Cherry Network 对照 | ⬜ |
| MM-R01 | P0 | Postman 请求 → model-metric 实时变化 | ⬜ |
| MM-R02 | P1 | API Benchmark → 总览并发/吞吐变化 | ⬜ |

---

# 5. Chat → Agent 过渡章

完整占位：

`docs/chapters/02-chat-to-agent-harness.md`

| 编号 | 类型 | 优先级 | 内容 | 状态 |
|---|---|---:|---|---|
| CHAT-01 | 截图 | P0 | Chat 只给答案/代码 | ⬜ |
| CHAT-02 | 截图 | P0 | Agent 文件/命令/验证 | ⬜ |
| CHAT-03 | 图示 | P0 | Prompt→Answer vs Goal→Deliver | ⬜ |
| CHAT-04 | 截图 | P1 | 同模型最终结果对照 | ⬜ |
| CHAT-R01 | 录屏 | P0 | Read/Edit/Run/Verify 最小闭环 | ⬜ |
| CHAT-R02 | 录屏 | P0 | 鹈鹕 Chat 人工接力 | ⬜ |
| CHAT-R03 | 录屏 | P0 | 鹈鹕 Agent 自动闭环 | ⬜ |

---

# 6. Open WebUI / Cherry Studio / RAG

完整占位：

`docs/chapters/02-chat-workbenches-and-rag.md`

| 编号 | 类型 | 优先级 | 内容 | 状态 |
|---|---|---:|---|---|
| OW-01 | 截图 | P0 | Open WebUI 总览 | ⬜ |
| OW-02 | 截图 | P0 | Provider/Connection | ⬜ |
| OW-03 | 截图 | P1 | Chat→Model→Knowledge→Tool | ⬜ |
| OW-04 | 截图 | P0 | System Prompt + Parameters | ⬜ |
| OW-05 | 截图 | P1 | Thinking UI vs 后端协议 | ⬜ |
| OW-06 | 截图 | P1 | Vision vs Image Generation | ⬜ |
| CH-01 | 截图 | P0 | Cherry 总览 | ⬜ |
| CH-02 | 截图 | P0 | Custom Provider | ⬜ |
| CH-03 | 截图 | P1 | Assistant vs Agent | ⬜ |
| CH-04 | 截图 | P1 | Thinking / Context | ⬜ |
| CH-05 | 截图 | P1 | Vision vs Drawing | ⬜ |
| WB-R01 | 录屏 | P1 | Open WebUI Provider→Chat | ⬜ |
| WB-R02 | 录屏 | P0 | Cherry Provider→内网模型 | ⬜ |

知识库操作统一复用下一节 `KB-xx`。

---

# 7. 部门知识库

教学版：

`docs/chapters/03-department-knowledge-base-teaching.md`

技术版：

`docs/chapters/03-department-knowledge-base.md`

两份讲义共用同一套素材编号。

## 7.1 截图/图示

当前已有 `KB-01～KB-22`，详见教学版第 21 节。重点：

- KB-01：无资料 vs 带资料；
- KB-04 / 05：BM25 / Embedding；
- KB-06A / 06：PDF → Parsed Text → Chunk；
- KB-08 / 08B / 09：External Retrieval / Context Utilization / Evidence Budget；
- KB-12～14：Cherry；
- KB-15～17：Open WebUI；
- KB-18：Agent Tool Trace；
- KB-19：同源三工具；
- KB-21：ACL；
- KB-22：引用与可追溯。

## 7.2 录屏

| 编号 | 优先级 | 内容 | 状态 |
|---|---:|---|---|
| KB-R01 | P0 | Cherry 建库 → Parse/Chunk → BM25 → Retrieval Test → Chat | ⬜ |
| KB-R02 | P0 | 同资料同问题：BM25 vs Embedding/Rerank | ⬜ |
| KB-R03 | P0 | Open WebUI Shared KB + ACL | ⬜ |
| KB-R04 | P1 | Pipeline vs Agentic Retrieval | ⬜ |
| KB-R05 | P0 | Agent：Shared KB → Git → API/Metrics → 引用回答 | ⬜ |
| KB-R06 | P1 | 无答案 / 版本冲突回归 | ⬜ |

---

# 8. Agent 共性机制

完整占位：

`docs/chapters/04-agent-common-mechanisms.md`

## 8.1 静态

| 编号 | 优先级 | 内容 | 状态 |
|---|---:|---|---|
| AGENT-01 | P0 | Harness 总图 | ⬜ |
| AGENT-02 | P0 | 固定模型 Harness 受控实验 | ⬜ |
| AGENT-WB-01 | P0 | WorkBuddy Chat/Task | ⬜ |
| AGENT-WB-02 | P0 | WorkBuddy Workspace/Artifact | ⬜ |
| AGENT-WB-03 | P0 | WorkBuddy Skill Marketplace | ⬜ |
| AGENT-WB-04 | P1 | WorkBuddy Cloud Runtime | ⬜ |
| AGENT-03 | P0 | AGENTS.md + 实际遵守 | ⬜ |
| AGENT-04 | P0 | Workspace | ⬜ |
| AGENT-05 | P1 | Plan/Task State | ⬜ |
| AGENT-06 | P1 | Memory | ⬜ |
| AGENT-07 | P0 | Tool Trace | ⬜ |
| AGENT-08 | P0 | MCP Tools/Resources | ⬜ |
| AGENT-09 | P0 | Skill 目录/SKILL.md | ⬜ |
| AGENT-10 | P1 | Browser Use | ⬜ |
| AGENT-11 | P2 | Computer Use | ⬜ |
| AGENT-12 | P0 | Approval/Sandbox | ⬜ |
| AGENT-13 | P0 | Diff + Test + Visual QA | ⬜ |
| AGENT-14 | P1 | Sub-agent | ⬜ |
| AGENT-15 | P1 | CLI/IDE/Desktop-Web | ⬜ |
| AGENT-16 | P0 | Runtime Backend | ⬜ |
| AGENT-17 | P1 | Trace/Audit | ⬜ |

## 8.2 录屏

| 编号 | 优先级 | 内容 | 状态 |
|---|---:|---|---|
| AGENT-R01 | P0 | 同模型同任务跨 2–3 Harness | ⬜ |
| AGENT-R02 | P0 | WorkBuddy Chat → Workspace → Artifact | ⬜ |
| AGENT-R03 | P1 | WorkBuddy 社区 Skill 安装/调用 | ⬜ |
| AGENT-R04 | P0 | 读取并遵守 AGENTS.md | ⬜ |
| AGENT-R05 | P0 | Read/Edit/Test/Verify Tool Loop | ⬜ |
| AGENT-R06 | P1 | MCP Tool 闭环 | ⬜ |
| AGENT-R07 | P0 | Skill 前后流程对比 | ⬜ |
| AGENT-R08 | P1 | Browser 自动操作 | ⬜ |
| AGENT-R09 | P1 | Approval/Sandbox | ⬜ |
| AGENT-R10 | P1 | Runtime Backend 切换/远程执行 | ⬜ |

---

# 9. Agent 如何操作真实世界

本模块第一套贯穿主案例固定使用 **ZCode Agent**：

- `demos/zcode-real-world/README.md`
- `docs/cases/zcode-agent-real-world.md`
- `demos/zcode-real-world/project/`

先用 ZCode 建立完整执行闭环，再用其他 Agent 做机制对照，避免培训频繁切换 UI。

完整占位：

`docs/chapters/05-agent-tools-real-world.md`

## 9.1 静态

| 编号 | 优先级 | 内容 | 状态 |
|---|---:|---|---|
| TOOL-01 | P0 | Model → Tool Request → Harness → Execute → Tool Result 总图 | ⬜ |
| TOOL-02 | P0 | Workspace：目录 + Search + Read | ⬜ |
| TOOL-03 | P0 | Terminal Tool Call + Approval / Sandbox | ⬜ |
| TOOL-04 | P0 | git status + git diff + test | ⬜ |
| TOOL-05 | P0 | 静态检查/自动测试/运行态/UI 四层验证图 | ⬜ |
| TOOL-06 | P0 | Browser Use / Playwright / Computer Use / Crawler 对比图 | ⬜ |
| TOOL-06A | P0 | Built-in Browser / Browser Use / Host Chrome / Computer Use 分层图 | ⬜ |
| TOOL-07 | P0 | Browser + Console + Screenshot + 修复对照 | ⬜ |
| TOOL-08 | P0 | SSH + Docker + logs + health request | ⬜ |
| TOOL-09 | P1 | UI 自动操作 vs Structured API Tool | ⬜ |
| TOOL-10 | P0 | Commit → GitHub Actions → Pass/Fail | ⬜ |
| TOOL-11 | P0 | 12 步工程 Agent 闭环图 | ⬜ |

## 9.2 录屏

| 编号 | 优先级 | 内容 | 状态 |
|---|---:|---|---|
| TOOL-R01 | P0 | Read → Edit → Test → Diff 最小闭环 | ⬜ |
| TOOL-R02 | P0 | Test Pass → Browser Visual QA → Fix | ⬜ |
| TOOL-R03 | P0 | SSH → Docker → Logs → Health Check | ⬜ |
| TOOL-R04 | P0 | Commit → Push → CI | ⬜ |
| TOOL-R05 | P1 | API Tool 与 GUI 操作完成同一任务对比 | ⬜ |
| ZCODE-01 | P0 | ZCode Workspace + 鹈鹕任务 | ⬜ |
| ZCODE-02 | P0 | index.html 出现在 File Tree | ⬜ |
| ZCODE-03 | P0 | Built-in Browser 第一次结果 | ⬜ |
| ZCODE-04 | P0 | Agent 根据 Browser 结果继续修改 | ⬜ |
| ZCODE-05 | P0 | 最终 Browser 验证 + Review | ⬜ |
| ZCODE-06 | P0 | Sensor Guard 初始 Workspace | ⬜ |
| ZCODE-07 | P0 | 读取 AGENTS.md | ⬜ |
| ZCODE-08 | P0 | Terminal 首次测试失败 | ⬜ |
| ZCODE-09 | P0 | Search / Read 定位代码 | ⬜ |
| ZCODE-10 | P0 | 修改后完整测试通过 | ⬜ |
| ZCODE-11 | P0 | Review / Git Diff | ⬜ |
| ZCODE-12 | P0 | Execution Modes / Safety Confirmation | ⬜ |
| ZCODE-13 | P1 | Goal Mode / Summary | ⬜ |
| ZCODE-R01 | P0 | 鹈鹕：生成 → Browser → 看 → 修 → 再验证 | ⬜ |
| ZCODE-R02 | P0 | Sensor Guard：Rules → Fail → Locate → Fix → Pass → Diff | ⬜ |
| ZCODE-R03 | P1 | Goal Mode 多轮长任务 | ⬜ |



## 9.3 Agent 运行环境 / 内网工具链

完整案例：

`docs/cases/agent-runtime-environment-intranet.md`

环境检查脚本：

- `demos/zcode-real-world/check-agent-env.ps1`
- `demos/zcode-real-world/check-agent-env.sh`

| 编号 | 优先级 | 内容 | 状态 |
|---|---:|---|---|
| ENV-01 | P0 | Model → Harness → Tool → Runtime → Toolchain 分层图 | ⬜ |
| ENV-02 | P0 | ZCode Terminal 环境检查结果 | ⬜ |
| ENV-03 | P0 | Local / WSL / Docker / SSH 工具链位置对比 | ⬜ |
| ENV-04 | P0 | 公网临时安装 vs 内网内部镜像/离线包 | ⬜ |
| ENV-05 | P0 | 系统 CLI vs Python vs Node.js 工具选择决策树 | ⬜ |
| ENV-06 | P1 | CDP / Playwright：Browser Tool、CLI、MCP、Python、Node.js 路径对比 | ⬜ |
| ENV-R01 | P0 | Preflight：工具缺失 → 补齐 → 同任务成功 | ⬜ |
| ENV-R02 | P1 | npm/pip 公网源失败 → 内部源成功 | ⬜ |

---

# 10. Agent 工具接入：API / MCP / Skill / Plugin / Command / Hook

完整占位：

`docs/chapters/06-api-mcp-skill-plugin-command-hook.md`

统一 Demo 设计：

`demos/agent-tool-integration/README.md`

第一套实现使用 **ZCode 作为 MCP Host**：

`demos/agent-tool-integration/zcode-implementation-plan.md`

## 10.1 静态

| 编号 | 优先级 | 内容 | 状态 |
|---|---:|---|---|
| CONNECT-01 | P0 | API / Tool / MCP / Skill / Plugin / Command / Hook 分层总图 | ⬜ |
| CONNECT-02 | P0 | REST API → Agent Tool 映射 | ⬜ |
| CONNECT-03 | P0 | Existing API → MCP Server → Agent | ⬜ |
| CONNECT-04 | P0 | MCP Tools vs Skill Workflow | ⬜ |
| CONNECT-05 | P1 | OpenAI 当前 Plugin Package 结构（注明产品特定） | ⬜ |
| CONNECT-06 | P0 | 设备管理端到端七概念示例 | ⬜ |
| CONNECT-07 | P0 | project-acceptance / service-acceptance Skill 目录 | ⬜ |
| CONNECT-08 | P1 | Read / Write / Dangerous Tool 权限拆分 | ⬜ |
| CONNECT-09 | P0 | API / MCP / Skill / Script 决策表 | ⬜ |

## 10.2 录屏

| 编号 | 优先级 | 内容 | 状态 |
|---|---:|---|---|
| CONNECT-R01 | P0 | 同一训练服务的 curl / Raw API 调用 | ⬜ |
| CONNECT-R02 | P0 | 同一能力通过 MCP Tool 调用 | ⬜ |
| CONNECT-R03 | P0 | Skill 组合 MCP Tools 完成多步验收 | ⬜ |
| CONNECT-R04 | P1 | 安装/查看现有 Skill，打开 SKILL.md | ⬜ |
| CONNECT-R05 | P1 | Command 主动触发 vs Hook 事件触发 | ⬜ |


---

# 11. 如何形成可复用资产

完整占位：

`docs/chapters/07-reusable-agent-assets.md`

## 11.1 静态

| 编号 | 优先级 | 内容 | 状态 |
|---|---:|---|---|
| ASSET-01 | P0 | ai-share 仓库资产地图 | ⬜ |
| ASSET-02 | P0 | 信息/经验 → 资产类型路由图 | ⬜ |
| ASSET-03 | P0 | 本仓库 AGENTS.md 关键规则 | ⬜ |
| ASSET-04 | P0 | Always-on Rules vs On-demand Skill | ⬜ |
| ASSET-05 | P0 | Prompt → Script → Test → CI 成熟化路径 | ⬜ |
| ASSET-06 | P0 | Session / Memory / Project Rules / Knowledge Base 边界 | ⬜ |
| ASSET-07 | P0 | Always-on / On-demand / Executable 三层资产 | ⬜ |
| ASSET-08 | P0 | Qwen API 资产升级时间线 | ⬜ |
| ASSET-09 | P1 | Source of Truth / 资产治理图 | ⬜ |
| ASSET-ZC-01 | P0 | ZCode AGENTS.md vs Project Memory | ⬜ |
| ASSET-ZC-02 | P0 | ZCode Command vs Skill | ⬜ |
| ASSET-ZC-03 | P1 | ZCode Plugin 组成：Skill / Command / MCP / Hook | ⬜ |

## 11.2 录屏

| 编号 | 优先级 | 内容 | 状态 |
|---|---:|---|---|
| ASSET-R01 | P0 | 四条信息应该沉淀到哪里：互动判断 | ⬜ |
| ASSET-R02 | P0 | 长 Prompt → Skill 的前后对比 | ⬜ |
| ASSET-R03 | P1 | 修改 AGENTS.md / Skill → Git Diff → Commit | ⬜ |
| ASSET-R04 | P1 | Script / Test / CI 三层确定性升级 | ⬜ |


---

# 12. 推荐的实际采集顺序

不要严格按讲义章节逐张拍，按“环境”批量采集效率更高：

1. **Cherry Studio 一次录完**：API-NET、API-R01~04、CH-01~05、WB-R02、KB-04/05、KB-12~14、KB-R01/02；
2. **Open WebUI 一次录完**：OW-01~06、WB-R01、KB-15~17、KB-R03/04；
3. **API / Postman / model-metric 一次录完**：API-01、API-POST-01~02、API-TEST-01~02、API-03~09、MM-01~03、API-R06/07/09、MM-R01~02；
4. **统一鹈鹕 Demo 一次录完**：API-10/11、CHAT-01/02/04、CHAT-R01~03、API-R08；
5. **WorkBuddy 一次录完**：AGENT-WB-01~04、AGENT-R02/03；
6. **先录 Agent Runtime 环境**：ENV-01~04、ENV-R01；先证明 Terminal ≠ Toolchain，并记录内网标准环境；
7. **ZCode 主案例再录**：ZCODE-01~13、ZCODE-R01~03；优先完成 ZCODE-R01 鹈鹕 Browser 闭环和 ZCODE-R02 Sensor Guard 工程闭环；
8. **工程 Agent Repo 补充录制**：AGENT-03~17、AGENT-R04~10、TOOL-01~07、TOOL-10~11、TOOL-R01~02、TOOL-R04；
9. **服务器训练环境一次录完**：TOOL-08、TOOL-R03；
10. **API/MCP/Skill 统一训练 Demo 一次录完**：CONNECT-01~09、CONNECT-R01~05；
11. **资产沉淀一次录完**：ASSET-01~09、ASSET-R01~04（优先直接使用 ai-share 仓库与 project-acceptance Skill）；
12. **Knowledge Agent 多源任务最后录**：KB-18/19/22、KB-R05/06。

这样可以减少反复切换环境、账号、模型和测试资料。

---

# 13. 后续落盘约定

实际素材建议逐步落到：

~~~text
assets/
├── screenshots/
│   ├── api/
│   ├── chat-agent/
│   ├── workbenches/
│   ├── knowledge/
│   └── agent/
└── recordings/
    ├── api/
    ├── chat-agent/
    ├── knowledge/
    └── agent/
~~~

每完成一批素材：

1. 回填本清单状态；
2. 在对应讲义中将“占位”替换为真实相对路径；
3. 原始录屏和裁剪后的培训版分开保存；
4. 保留原始证据，不只保存 PPT 中经过裁剪的图片；
5. 如果实测与讲义叙述不一致，以实测为准并同步修改讲义。

