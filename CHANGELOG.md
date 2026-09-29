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
