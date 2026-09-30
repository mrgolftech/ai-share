# 四次讲座最终讲义索引

> 当前授课基线：`docs/outline/training-4-session-leadership-proposal.md`
> 更新日期：2026-09-30
> 状态：四场 Final Lecture Draft v1.0 已建立，进入截图 / 录屏 / Demo / PPT 生产阶段。

## 第一讲：从模型 API 到 Agent——看懂 AI 应用背后的工作逻辑

讲义：

`docs/lectures/01-api-to-agent.md`

核心问题：

> Chat、模型、API、Tool、Harness、Agent 到底是什么关系？

主要真实案例：

- Cherry Studio Network；
- 内网 Qwen API 自动测试；
- model-metric；
- Tool Calling；
- Chat vs Agent；
- Sensor Guard 最小 Agent Loop。

主要素材编号：

- API-*；
- MM-*；
- CHAT-*；
- ZCODE-*。

---

## 第二讲：部门知识库建设——让 AI 可靠使用我们的知识

讲义：

`docs/lectures/02-department-knowledge-base.md`

核心问题：

> 部门有哪些知识、怎样处理、怎样检索、怎样治理、怎样让 Cherry / Open WebUI / Agent 共用？

主要真实案例：

- Qwen API 同源 Corpus；
- Cherry Knowledge；
- Open WebUI Shared Knowledge；
- Agent Shared KB → Git → API/Metrics 多源取证；
- 版本冲突 / no-answer / ACL。

主要素材编号：

- KB-*；
- KB-R*。

---

## 第三讲：深入 Agent——掌握共性，而不是记住不同界面

讲义：

`docs/lectures/03-agent-common-runtime-tools.md`

核心问题：

> 换一个 Agent 时，怎样从 Harness、Context、Workspace、Runtime、Tools 和 Permission 快速理解它？

主要案例：

- Codex / ZCode / OpenCode / Hermes / WorkBuddy 共性；
- AGENTS.md；
- Sensor Guard；
- Browser / Playwright / CDP / Computer Use；
- BMQuiz / model-metric Server；
- Raw API → MCP → Skill；
- 资产路由。

主要素材编号：

- AGENT-*；
- ENV-*；
- TOOL-*；
- CONNECT-*；
- ASSET-*；
- ZCODE-*。

---

## 第四讲：Agent 工程实战——用真实项目走通开发、测试、发布和部署

讲义：

`docs/lectures/04-agent-engineering-practice.md`

纵向案例：

- `docs/cases/bmquiz-end-to-end-agent-development.md`
- `docs/cases/filecheck-end-to-end-agent-development.md`

辅助案例：

- `docs/cases/model-metric-api-observability.md`
- `docs/cases/agent-server-operations.md`
- IPsec VPN 性能分析；
- HyperFrames 内容生产；
- 授权范围内接口兼容性 / 安全验证。

主要素材编号：

- BM-*；
- SERVER-*；
- FC-*；
- MM-CASE-*；
- IPSEC-*；
- HF-*；
- SEC-*；
- METHOD-*。

---

# 当前生产顺序

1. 四讲讲义内容 Review；
2. 按 `docs/outline/media-capture-checklist.md` 完成 P0 素材；
3. 优先录制每场 2～4 个最关键动态闭环；
4. 补 BMQuiz / FileCheck 历史证据；
5. 完成知识库同源三层 Demo；
6. 完成 API → MCP → Skill 统一 Demo；
7. 四场分别抽象 PPT 页级故事线；
8. PPT + 备用截图/录屏；
9. 现场预演。

# 现场 Demo 总原则

> **实时 Demo 用来证明“现在可以做”；预录和截图用来保证“现场即使失败也能讲清”。**

任何涉及：

- 网络；
- 模型排队；
- Browser 状态；
- SSH；
- Build；
- GitHub Actions；
- 生产环境；

的 Demo，都应准备预录。
