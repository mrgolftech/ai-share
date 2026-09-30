# AI Share

面向部门技术人员的 AI 大模型与 Agent 工程实践培训材料。

## 培训基线

- [AI 大模型与 Agent 工程实践培训大纲（Baseline）](docs/outline/training-outline.md)
- [项目协作规则与内容原则](AGENTS.md)
- [ChatGPT Project Instructions v2](docs/project-instructions-v2.md)

后续培训讲义、案例、Demo、素材和 PPT 均以这份大纲为组织基线，并随实测结果和材料成熟度持续迭代。

## 当前已落盘

### 内网 Qwen3.6 API / Agent / Vision

- [API 实测材料总览](api/qwen/README.md)
- [Qwen3.6 内网模型服务 API 实测报告（当前基线）](api/qwen/reports/qwen36_api_test_report_20260930.md)
- [培训讲义：从一个 HTTP 请求理解内网大模型服务](docs/chapters/01-intranet-qwen-api.md)
- [官方参考资料](docs/references/qwen36-api-sources.md)
- [当前 Qwen r4 实测证据](api/qwen/results/20260930_095033/evidence.md)
- [历史实测归档](api/qwen/results/archive/)
- [第一版 API 测试脚本](api/qwen/qwen_api_training_test.py)
- [全面 API / Agent / Vision 测试脚本 v3](api/qwen/qwen_api_training_test_v3.py)
- [失败项专项重测脚本](api/qwen/qwen_failed_retest.py)
- [model-metric API 观测案例](docs/cases/model-metric-api-observability.md)
- [Token 输出速率体感 Demo](demos/token-output-speed/index.html) — 基于开源项目改造，支持单速率与并排对比

材料原则：以官方资料、源代码和本地实测为证据，明确区分“官方能力”“当前部署配置”“协议存在”和“我们实测”。

后续内容继续围绕“理解原理 → 掌握工具 → 建立方法 → 完成实际工作”组织。
