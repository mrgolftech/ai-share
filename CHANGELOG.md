# CHANGELOG

## 2026-09-29

- 初始化 AI 应用培训仓库。
- 增加 Qwen3.6 内网 API 培训测试脚本。
- 增加 2026-09-29 API 实测记录（公开脱敏版）。
- 记录 OpenAI Chat、OpenAI Responses/Codex、Anthropic Messages 的协议兼容性结论。
- 明确记录 Anthropic Tool Use 当前未通过，以及 Thinking ON 被输出长度截断的问题。
- 新增《Qwen3.6 内网模型服务 API 实测报告》。
- 新增《培训讲义：从一个 HTTP 请求理解内网大模型服务》。
- 新增 Qwen3.6 与 vLLM 官方参考资料索引。
- 在讲义中明确区分官方模型能力、当前服务配置与本地实测结果。
- 新增 `AGENTS.md`，明确仓库协作规则、证据优先级、工程方法与人机职责边界。
- 新增 `docs/outline/training-outline.md`，确立六段式培训主线及案例穿插原则。
- 增加材料成熟度状态：规划中 → 已有素材 → 已有初稿 → 已有实测证据 → 可用于培训 → 可用于 PPT。
- 明确培训内容 Source of Truth：实测/代码事实 > 培训大纲 > AGENTS.md > 章节文档 > 外部资料 > 历史聊天。
- 新增 `docs/project-instructions-v2.md`，用于 ChatGPT Project Instructions 的稳定协作规则。

- 增加 Qwen3.6 v2 全面 API / Agent / Vision 实测与失败项专项复测。
- OpenAI Chat、Responses、Anthropic 三套 Tool Result 基础闭环均确认通过。
- 多模态单图、Vision SSE、多图、Anthropic Image、Vision + Tool Calling 形成实测证据。
- 修正旧结论：Anthropic Tool Use 实际可用，主要兼容异常为 thinking.type=disabled 未生效。
- 修正两类测试假失败：Thinking 判定器 bug、Vision Tool Schema 语义不清。
- Responses Vision 改为“待按 OpenAPI 必填 detail 字段修正后复测”，不再误判为不支持。
- 记录 Thinking ON 43～299 秒长尾及重任务后简单推理暂时变慢现象。
- 模块一材料成熟度提升为“可用于培训”。

- 集成开源 Token 输出速率体感 Demo：基于 `aaravchour/token-speed-visualiser`（Apache-2.0）进行培训版改造。
- Demo 去除外部 CDN/字体依赖，改为离线可运行；去掉容易过时的固定模型速度标签，保留单速率和 Race Mode。
- 模块一讲义新增 TTFT / Tokens/s / Total Latency 的现场体感演示环节。

## 2026-09-30

- 将 `20260930_095033` r4 全面测试确立为当前 Qwen 能力基线：28 PASS / 1 SKIP / 0 FAIL / 0 ERROR。
- Responses Vision 使用 `detail:"auto"` 后正式 PASS；旧 HTTP 400 归档为历史 Schema 问题。
- 明确 Thinking 开关 PASS 与回答完成度不同：本轮 OFF/ON 均触发 `finish_reason=length`。
- Anthropic Tool Loop 本轮完整 PASS；`thinking.type=disabled` 兼容异常仍保留。
- 旧 2026-09-29 测试和报告迁入 `archive/`。
- 新增 v3 测试脚本公共脱敏版及 CI 编译检查。
- 第一章新增 Postman → Cherry Network → Python Test → `/metrics` → model-metric 教学链。
- 新增 `docs/cases/model-metric-api-observability.md`。
- 截图/录屏清单新增 Postman、自动测试与 model-metric 素材。

- 新增模块三主讲稿 `docs/chapters/05-agent-tools-real-world.md`，将 File/Search、Shell、Git、Browser/Playwright/Computer Use、SSH、Docker、API、CI/CD 收束为“Read → Act → Observe → Verify → Iterate → Deliver”工程闭环。
- 新增模块三官方证据基线 `docs/references/agent-tools-real-world-evidence-2026-09.md`，区分稳定机制、官方当前实现与待实测内容。
- 模块三新增 TOOL-01～11、TOOL-R01～05 截图/录屏占位并同步总素材清单。
- 新增模块四主讲稿 `docs/chapters/06-api-mcp-skill-plugin-command-hook.md`，明确 API、Tool、Function Calling、MCP、Skill、Plugin、Command、Hook 的分层关系。
- 明确关键教学结论：MCP 不替代 API；Skill 不等于 API 封装；Plugin 定义需按具体产品理解；Command 偏主动触发，Hook 偏事件触发。
- 新增 `docs/references/api-mcp-skill-evidence-2026-09.md`，基于 MCP 与 OpenAI 当前 Skills/Plugins/Tool Design/Hooks 官方资料建立证据基线。
- 新增 `demos/agent-tool-integration/README.md`，规划同一 Training Service 的 Raw API → MCP Tool → Skill+MCP 统一教学 Demo。
- 模块四新增 CONNECT-01～09、CONNECT-R01～05 素材占位；下一讲义建设重点转向模块五“可复用资产与知识体系”。

- 新增模块五主讲稿 `docs/chapters/07-reusable-agent-assets.md`，从“资产路由”而非工具名词出发，统一 Prompt、Project Rules、Plan、Skill、Script、Test/Eval、CI、Template、Memory、Knowledge Base、Evidence、Git 的沉淀边界。
- 新增反过度沉淀原则：AGENTS.md 不作为项目百科全书；专项流程按需加载为 Skill；确定性步骤逐步下沉为 Script/Test/CI；关键项目事实不只依赖产品 Memory。
- 新增 `docs/references/reusable-agent-assets-evidence-2026-09.md`，核验 AGENTS.md 开放格式、Codex 当前 Context/AGENTS 指引、OpenAI Skills/ExecPlan、Hermes Memory/Context/Skills 等资料。
- 模块五新增 ASSET-01～09、ASSET-R01～04 素材占位；培训讲义下一阶段转入真实案例、统一 Demo 实现和实测证据补齐。
