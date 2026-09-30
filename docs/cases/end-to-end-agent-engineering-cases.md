# 完整工程案例设计——从具体需求到 Agent 闭环交付

> 状态：案例框架已建立 / 待按真实 Git 历史与素材补证据  
> 日期：2026-09-30  
> 目的：解决现有培训“机制讲清了，但缺少一个从需求到交付的完整工程故事”的问题。

---

# 1. 完整工程案例必须回答什么

每个“完整案例”不能只展示：

> Agent 写了哪些代码。

至少需要完整回答：

1. 原始问题是什么；
2. 用户真正需要什么；
3. 有哪些平台、业务、安全、兼容性约束；
4. Agent 做了哪些调研；
5. 为什么选择当前架构；
6. 为什么没有选其他候选方案；
7. 怎样形成 Plan；
8. Agent 如何分阶段实现；
9. 怎样测试；
10. 怎样进行 Browser / GUI QA；
11. 怎样 Review Git Diff；
12. 怎样构建；
13. 怎样发布；
14. 怎样部署；
15. 怎样验证线上状态；
16. 人在哪些关键节点做决定；
17. 最终留下哪些可复用资产。

统一结构：

```text
Problem
→ Requirement
→ Constraint
→ Research
→ Architecture
→ Plan
→ Implement
→ Test
→ Visual / Runtime QA
→ Review
→ Build
→ Release
→ Deploy
→ Verify
→ Assetize
```

---

# 2. 主案例一：BMQuiz V2——完整 Web / Full-stack 工程

## 2.1 为什么选 BMQuiz

当前真实仓库 `mrgolftech/BMQuiz-V2` 已经存在非常完整的工程资产：

- `AGENTS.md`；
- Product Function Spec；
- UI/UX Interaction Spec；
- Technical Architecture；
- Data Model；
- Routing / State Design；
- Project Structure；
- Development Roadmap；
- Codex Implementation Guide；
- Acceptance Test Checklist；
- Deployment；
- Design System / Design Tokens；
- Visual QA；
- Docker；
- Docker Compose；
- GitHub Actions；
- GHCR；
- Android TWA / APK。

这使它特别适合回答：

> **“文档先行 + Agent 开发”到底是什么样子。**

---

## 2.2 当前真实技术栈

当前仓库事实：

### Frontend

- React；
- TypeScript strict；
- Vite；
- Tailwind CSS；
- TanStack Router；
- Zustand；
- Motion；
- PWA；
- Vitest / Playwright。

### Backend

- Node.js 22+；
- Fastify；
- Better Auth；
- SQLite；
- Drizzle；
- TypeScript；
- Vitest。

### Runtime / Delivery

- Docker；
- GitHub Actions；
- GHCR；
- Android TWA / Bubblewrap / Gradle。

培训不能把这些技术选型解释成“唯一正确方案”。

真正要讲的是：

> **这些选择怎样与当前规模、部署方式、local-first、多设备同步、认证和交付约束匹配。**

---

## 2.3 课堂故事线

### Step 1：从旧题库 / 旧应用问题开始

回答：

- 当前产品是什么；
- 为什么需要重构；
- 哪些数据必须保持 canonical；
- 用户真正要什么。

证据：

- README；
- oldquiz；
- Product Spec；
- Git 历史。

### Step 2：Requirement

展示 Product Function Spec。

重点：

> Agent 开工前已经知道“产品应该做成什么”。

### Step 3：Constraint

例如：

- 固定小规模题库；
- local-first；
- 多设备状态；
- 登录认证；
- 题库不能匿名公开；
- 单机 SQLite；
- Web/PWA/Android 尽量共享实现。

### Step 4：Research

需要根据仓库和历史资料还原：

- 为什么采用当前前后端技术；
- 是否参考已有 GitHub 项目；
- 哪些库被评估过；
- 哪些方案最终没有采用。

> 这一部分不得后验编造，后续必须补 Git / 文档证据。

### Step 5：Architecture

使用：

`docs/03_TECHNICAL_ARCHITECTURE.md`

讲：

- Browser / PWA / TWA；
- Fastify；
- API；
- Auth；
- SQLite；
- local-first；
- sync；
- deployment。

### Step 6：Plan / Documentation First

展示：

- Development Roadmap；
- Codex Implementation Guide；
- Acceptance Checklist。

核心观点：

> **不是 Prompt → Code，而是文档把 Agent 的搜索空间压缩下来。**

### Step 7：Implementation

不要逐文件讲。

只选几个能代表 Agent 工程的问题：

- canonical dataset；
- authenticated content；
- shared DTO；
- state / sync；
- 关键 UI；
- auth / admin。

### Step 8：Test

展示：

- frontend test；
- server test；
- typecheck；
- migration check；
- health smoke。

### Step 9：Visual QA

展示真实 Playwright Visual QA：

```text
Build
→ Start QA Preview
→ Browser
→ Screenshot
→ Visual Check
→ Artifact
```

### Step 10：Review

展示：

- Git Diff；
- 关键代码复读；
- 文档同步；
- 迁移/安全影响。

### Step 11：CI/CD

展示：

- CI；
- Server CI；
- Visual QA；
- Docker Image Release；
- Fullstack Release Gate。

### Step 12：服务器部署

```text
SSH
→ docker login
→ docker compose pull
→ docker compose up -d
→ ps
→ logs
→ health
→ smoke
```

### Step 13：线上验证

至少：

- `/api/health`；
- 未登录内容 401；
- 旧静态题库路径 404；
- 登录流程；
- 数据 volume。

### Step 14：Assetize

最后回头看 BMQuiz 留下了：

- AGENTS.md；
- Requirements；
- Architecture；
- Design System；
- Test；
- Visual QA；
- CI；
- Docker；
- Deployment；
- Release 流程。

因此：

> **项目本身就是一套可复用 Agent 工程上下文。**

---

# 3. 对照案例：model-metric——监控类 Web 应用

BMQuiz 用于“完整从需求到产品”。

model-metric 更适合强调另一组问题：

- 指标语义；
- 多实例采集；
- Gauge / Counter；
- 数据口径；
- 实时与历史；
- SQLite；
- API；
- WebSocket；
- 服务部署；
- systemd；
- 日志；
- 升级；
- 数据兼容。

当前真实仓库包含：

- backend / frontend；
- tests；
- DEPLOY；
- systemd example；
- Windows build workflow。

它适合作为对照说明：

> **Agent 工程流程可以复用，但架构方案必须服从问题本身。**

---

# 4. 主案例二：FileCheck——本地客户端 / GUI / 打包发布

## 4.1 为什么选 FileCheck

当前 `mrgolftech/filecheck` 已经有：

- REQUIREMENTS；
- ARCHITECTURE；
- TEST_PLAN；
- GUI design system；
- Python core；
- CLI；
- GUI；
- CI；
- 多 Windows 版本构建；
- GitHub Release。

而且它的约束很“工程化”：

- Windows；
- 离线；
- Everything / ES；
- Unicode 路径；
- 大量文件；
- SHA-256；
- 恢复；
- 数据安全；
- Win7 SP1；
- x86 / x64。

这是一个非常适合说明：

> **约束怎样影响技术选择。**

---

## 4.2 不把“客户端”和“GUI”拆成两个案例

教学上统一为：

```text
Core / Domain
→ CLI
→ GUI
→ Packaging
→ Release
```

GUI 是客户端的一层 Surface，不应该重新实现业务逻辑。

当前架构也已经明确：

> GUI 应包装已有生命周期能力，CLI / GUI 共用同一 Python core。

这是非常好的工程教学点。

---

## 4.3 技术预研怎么讲

可以设置候选：

### 语言

- Python；
- Go。

### GUI

- CustomTkinter；
- PyQt / PySide；
- WebView；
- 其他原生框架。

但培训必须区分：

### 当前项目事实

当前实现：

- Python；
- CustomTkinter；
- PyInstaller。

### 教学重建

“当时为什么不是 Go / PyQt”只有在找到：

- Git 历史；
- issue；
- Plan；
- 调研文档；
- 实测数据；

后才能作为“真实历史决策”来讲。

如果没有历史证据，就表述为：

> **站在当前需求约束下，重新做一次技术路线 Review。**

---

## 4.4 完整故事线

```text
敏感文件自查需求
→ 离线 / Windows / Unicode / 批量 / 安全恢复约束
→ Everything / ES 能力调研
→ Requirements
→ Architecture
→ Core
→ CLI
→ Selftest / pytest
→ GUI
→ GUI smoke
→ Win7 compatibility
→ PyInstaller
→ GitHub Actions
→ Artifact validation
→ Checksum
→ GitHub Release
```

---

# 5. 横向案例：CI/CD 与发布

CI/CD 不应只作为一个抽象章节。

从三个真实项目对照：

## BMQuiz

- frontend；
- server；
- migration；
- Visual QA；
- Docker image；
- GHCR；
- Android APK。

## FileCheck

- Python matrix；
- GUI smoke；
- Win7 compatibility；
- x86/x64；
- PyInstaller；
- artifact validation；
- checksum；
- GitHub Release。

## HyperFrames

- HTML / animation assets；
- timeline；
- render；
- video artifact。

最后抽象：

```text
Source
→ Test
→ Build
→ Artifact
→ Verify
→ Publish
```

---

# 6. 横向案例：Agent 操作服务器

不要做孤立“SSH 演示”。

统一放到真实交付任务中：

### BMQuiz

```text
目标：把已发布的新版本部署到测试/生产服务器

Read deployment doc
→ SSH
→ check current version
→ backup / confirm data volume
→ docker login
→ pull pinned image
→ docker compose up
→ inspect
→ logs
→ health
→ application smoke
→ record deployed version
```

### model-metric

```text
目标：更新服务并验证监控数据正常

SSH
→ check service
→ backup data
→ pull/update code or artifact
→ install deps
→ systemctl restart
→ journalctl
→ /api/overview
→ /api/instances
→ verify data semantics
```

完整设计见：

`docs/cases/agent-server-operations.md`

---

# 7. 专题案例：IPsec VPN 数据分析

重点不是让模型“看表格给结论”。

应该展示：

```text
Problem
→ Data Inventory
→ Clean / Structure
→ Hypothesis
→ Correlation
→ External / Architecture Evidence
→ Candidate Cause
→ Counterfactual Check
→ Engineering Verification
→ Conclusion
```

用来说明：

> 强模型适合复杂关系发现，但最终因果判断必须靠工程证据。

---

# 8. 专题案例：HyperFrames

当前 `mrgolftech/ai-use` 已有：

- Kids；
- Metric；
- Wafer；

三套 HyperFrames 资产。

可以展示 Agent 如何把：

```text
Narrative
→ Storyboard
→ Design Spec
→ HTML/SVG/GSAP
→ Timeline
→ Voice / Subtitle
→ Preview
→ Human Review
→ Render
```

组织为可重复内容生产流水线。

---

# 9. 专题案例：授权机制 / 协议行为研究

`eda365skill` 可以作为：

> **授权系统的行为分析、协议理解、兼容性研究与证据留档**

案例。

培训内容只保留：

- 研究问题如何定义；
- 如何建立实验样本；
- 如何记录 Trace；
- 如何定位代码路径；
- 如何从观察形成假设；
- 如何写自动化验证；
- 如何保存 Evidence；
- 如何做版本对比。

不纳入培训：

- 未授权许可生成；
- 绕过付费；
- 绕过激活；
- 凭据窃取；
- 扩大对第三方系统的未授权访问。

---

# 10. 专题案例：网站安全测试

推荐优先使用：

- 自己控制的 staging；
- BMQuiz 测试环境；
- 或明确授权的本地靶场。

完整 Agent 流程：

```text
Scope
→ Asset / Endpoint Inventory
→ Threat Model
→ Test Plan
→ Automated Checks
→ Manual Verification
→ Evidence
→ Severity / Impact
→ Fix
→ Regression
→ Report
```

培训重点：

- 授权范围；
- 工具编排；
- 证据；
- 修复；
- 回归。

而不是：

> “怎样攻击第三方网站”。

---

# 11. 案例成熟度要求

完整案例进入培训前至少需要：

- [ ] 当前仓库 SHA；
- [ ] 原始需求 / Requirement；
- [ ] 当前架构；
- [ ] 技术选型证据；
- [ ] Plan / Roadmap；
- [ ] 关键 Git Diff 或历史提交；
- [ ] Test 证据；
- [ ] Browser / GUI / Runtime QA；
- [ ] CI 证据；
- [ ] Release / Deploy 证据；
- [ ] 人做的关键判断；
- [ ] 可复用资产总结。

没有证据的部分必须标记：

> **教学重建 / 待核实**

不能把推测写成真实历史。

