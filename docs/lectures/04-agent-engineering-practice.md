# 第四讲：Agent 工程实战——用真实项目走通开发、测试、发布和部署

> 状态：Final Lecture Draft v1.0  
> 日期：2026-09-30  
> 建议时长：110～130 分钟  
> 内容映射：原内容单元 6 + 7 + 8  
> 主案例：BMQuiz V2、FileCheck  
> 对照/短案例：model-metric、IPsec VPN、HyperFrames、授权范围内的接口兼容性与安全验证  
> 主线：**不再介绍更多 Agent 名词，而是用真实项目证明“需求 → 架构 → Agent 开发 → 自动验证 → Git → CI/CD → 发布/部署”如何形成完整闭环。**

---

# 0. 这一讲不做“AI 一分钟写网站”的表演

AI 编程最容易做成一个很有视觉冲击力、但工程价值不高的演示：

> 输入一句话：“给我做一个网站。”

几分钟以后页面出来。

这个演示可以证明：

> 模型会生成代码。

但实际工作真正困难的部分往往发生在后面：

- 需求到底是什么；
- 哪些东西明确不做；
- 旧数据能不能改；
- 技术栈为什么这么选；
- 多文件应该怎么组织；
- UI 做出来以后到底好不好用；
- 修改有没有破坏别的功能；
- Windows 7 能不能跑；
- 服务启动以后业务语义是不是正确；
- 怎么自动打包；
- 怎么发布；
- 怎么部署；
- 怎么回滚；
- 下一个 Agent 怎么接着干。

所以第四讲不再证明：

> AI 会写代码。

而是证明：

> **Agent 可以进入一个真实工程过程，但只有当需求、规则、工具、验证和 Git 都准备好以后，这种能力才真正可用。**

---

# 1. 先给出全讲统一工程链

真实复杂任务不建议：

`Prompt → Code`

更稳妥的路径是：

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
→ Release
→ Deploy
→ Verify
→ Assetize
```

【图示占位 METHOD-02｜Prompt→Code vs 完整工程链】

这一串词不要一次解释完。

第四讲后面两个主案例都重复用这张图。

每讲到一个阶段，就把对应节点点亮。

这样学员最后会发现：

> BMQuiz 和 FileCheck 技术栈完全不同，但工程方法高度一致。

---

# 2. 人和 Agent 到底怎么分工？

第四讲必须避免讲成：

> “我给 Agent 一个目标，然后它自动把整个项目做完。”

更准确的是：

## 人负责

- 为什么做；
- 业务目标；
- 产品边界；
- 安全边界；
- 资源约束；
- 架构关键决策；
- 最终视觉判断；
- 是否接受风险；
- 是否发布。

## 模型 / Agent 负责

- 读现有资料；
- 调研候选方案；
- 形成 Plan；
- 修改代码；
- 生成测试；
- 调用工具；
- 运行验证；
- 整理证据；
- 反复执行。

## 自动化系统负责

- Test；
- Build；
- CI；
- Static Check；
- Package validation；
- Health；
- Regression。

统一表达：

> **模型负责判断和生成，工具负责执行，自动化测试负责验证，人负责目标、约束和最终判断。**

---

# 3. 主案例一：BMQuiz——不要从 React 开始，从“问题”开始

BMQuiz 适合作为第一完整案例，不是因为它使用 React、Fastify 或 Docker。

而是因为当前真实仓库已经留下了比较完整的工程链：

- Product Function Spec；
- UI/UX Spec；
- Technical Architecture；
- Data Model；
- Routing / State Design；
- Project Structure；
- Development Roadmap；
- Agent/Codex Implementation Guide；
- Acceptance Checklist；
- Design System；
- Unit / Integration Test；
- Playwright Visual QA；
- Server CI；
- Docker / GHCR；
- Android TWA；
- Deployment；
- AGENTS.md；
- Git History。

也就是说：

> **可以看到的不只是最后代码，还有“怎么逐步把需求变成产品”的证据。**

【截图占位 BM-01｜旧版本 / oldquiz 与当前 BMQuiz 界面对照】

开场先展示最终产品，然后问：

> 如果最开始只给 Agent 一句话——“帮我做个刷题网站”，能稳定得到现在这个结果吗？

显然不能。

---

# 4. BMQuiz / Problem：先说清楚为什么做

当前可以确认：

- 已有旧版应用；
- 有固定真实题库；
- 希望形成可长期使用的学习产品；
- 后续形成了 Web / PWA / Android TWA；
- 有账号、同步、管理员、部署等能力。

课堂上不需要为了故事完整而编造历史。

如果找不到最初的对话，只讲当前仓库能够确认的事实：

> **有真实业务数据和旧应用，需要把一次性小工具逐步变成可维护、可测试、可发布的产品。**

【案例素材待补：BM-H01｜最初需求对话 / 最早 V2 commit；如果找不到则不在正文中引用】

这里让大家看到：

> Problem 描述的是“为什么做”，而不是“用 React 做”。

---

# 5. BMQuiz / Requirement：把“做个网站”变成可验收需求

当前项目有正式 Product Function Spec。

可以展示：

- 53 道 canonical 填空题；
- 52 个 KnowledgePoint；
- 156 个派生测试；
- 背题；
- 练习；
- WrongBook；
- History；
- 多设备同步；
- 账号；
- 邀请码；
- Admin。

同时它还明确了“不做”：

- 不做多人在线考试平台；
- 不做社交；
- 不做排行榜；
- 不为了看起来完整增加无关模块。

【截图占位 BM-02｜Product Function Spec：做什么 / 不做什么】

这很适合讲一个工程经验：

> **Requirement 不只是列功能，还要限制 Agent 不要做什么。**

否则模型很容易把：

> “帮我做一个刷题网站”

理解成：

> “请生成一个互联网教育平台”。

---

# 6. BMQuiz / Constraint：约束往往比 Prompt 更重要

真正影响架构的不是“写得多漂亮的 Prompt”，而是约束。

BMQuiz 当前可确认的重要约束：

## 数据约束

- canonical 题库不能被 UI 重构“顺手优化”；
- KnowledgePoint 数量和业务语义必须保持。

## 产品约束

- Web / PWA / Android 尽量复用业务实现；
- 学习状态 local-first；
- 多设备需要同步；
- 冲突不能静默覆盖。

## 安全约束

- 完整题库不能继续匿名公开；
- Session 使用服务端认证；
- Admin 权限必须由服务端判断。

## 部署约束

- 当前规模优先单机；
- SQLite；
- 单容器；
- 数据持久化；
- 可备份、可回滚。

【图示占位 BM-03｜Constraint → Architecture 映射】

这张图应该把“为什么架构长成现在这样”讲清，而不是只画组件框。

---

# 7. BMQuiz / Research：Agent 可以调研，但不能把“推荐”当事实

遇到新技术问题，Agent 可以帮助：

- 查官方文档；
- 查 GitHub；
- 对比框架；
- 查看维护状态；
- 找参考实现。

但课堂必须区分：

- 当时真实做过的选择；
- 当前仓库已经形成的事实；
- 现在重新做的 Architecture Review。

当前技术路线是：

## Frontend

- React；
- TypeScript strict；
- Vite；
- Tailwind；
- TanStack Router；
- Zustand；
- PWA；
- Vitest / Playwright。

## Backend

- Node.js 22+；
- Fastify；
- Better Auth；
- SQLite；
- Drizzle。

## Delivery

- Docker；
- GitHub Actions；
- GHCR；
- Android TWA。

讲师表述：

> **这些是当前真实方案，不宣称它们是所有项目的最佳答案。**

如果后续找到当时技术选型对话，再作为真实历史加入。

---

# 8. BMQuiz / Architecture：先让 Agent 知道系统边界，再让它写文件

当前架构是：

```text
Browser / PWA / Android TWA
          │
        HTTPS
          ↓
    Reverse Proxy
          ↓
     Fastify
   ┌──────┼────────┐
   ↓      ↓        ↓
React   /api/*   Better Auth
          │        │
          ├────────┘
          ↓
      SQLite
```

【截图/图示占位 BM-04｜BMQuiz 当前总体架构】

内部前端也有明确分层：

```text
Presentation
→ Feature / Use Case
→ Domain
→ State / Persistence
→ Application Services
```

【图示占位 BM-05｜前端分层 / 数据流】

这里强调：

> Architecture 文档不是“项目做完以后画给领导看的图”。

它对 Agent 的价值是：

- 新功能放哪；
- 哪层可以依赖哪层；
- 哪些逻辑不能复制；
- 哪些边界不能被“顺手重构”。

---

# 9. BMQuiz / Project Rules：AGENTS.md 把人的经验变成 Agent 的长期约束

当前 BMQuiz 的 AGENTS.md 明确了：

- 当前事实优先级；
- 技术基线；
- canonical 数据；
- UI；
- Auth；
- migration；
- 测试；
- 发布；
- Android；
- 部署。

例如：

> 未经明确架构决策，不主动替换为另一套完整框架或数据基础设施。

【截图占位 BM-06｜BMQuiz AGENTS.md 关键规则】

【录屏占位 BM-R00｜Agent 进入项目后先读取 AGENTS.md / Architecture，再开始计划】

这正好回扣第三讲：

> **Project Rules 是工程资产，不是聊天技巧。**

---

# 10. BMQuiz / Plan：为什么“文档先行”不是形式主义

当前项目文档大致回答了：

```text
Product Spec
= 做什么

UI/UX
= 怎么交互

Architecture
= 系统怎么分

Data Model
= 数据是什么

Routing / State
= 状态怎么流

Project Structure
= 文件放哪里

Roadmap
= 按什么顺序做

Agent Guide
= Agent 怎么实施

Acceptance
= 怎样算完成

Deployment
= 最后怎样上线
```

【截图/图示占位 BM-07｜Document-first 工程地图】

这里强调：

> 文档不是越多越好。

真正有价值的是：

> **每份文档减少一种歧义。**

---

# 11. BMQuiz / Implement：课堂不要变成代码导览

完整工程案例最容易犯一个错误：

> 从 src 目录一路讲代码。

课堂只选几类最能证明工程方法的实现。

## 11.1 Canonical Data

说明：

> AI 可以重构代码，但不能改业务事实。

## 11.2 Local-first + Sync

真实同步语义：

```text
local snapshot
+ revision
↓
server CAS
├─ match → revision + 1
└─ stale → 409 SYNC_CONFLICT
```

这说明：

> “支持多设备同步”不是一句需求，它最终要落成可测试的一致性行为。

## 11.3 Authenticated Content

可以验证：

- 未登录完整题库接口 401；
- 登录后可用；
- private / no-store；
- 旧公开静态路径 404。

这里讲：

> 安全需求必须能变成验证项。

---

# 12. BMQuiz / Test：Agent 说“完成”不是完成

前端完成至少需要：

```text
npm ci
→ typecheck
→ test
→ build
```

后端：

```text
npm ci
→ typecheck
→ test
→ build
→ migration
→ health
```

Server CI 还会检查：

- migration；
- fresh DB；
- required tables；
- health。

【截图占位 BM-08｜GitHub Actions Server CI】

这里可以说：

> **如果完成标准只是“Agent 回答我已经完成”，这个项目实际上没有完成标准。**

---

# 13. BMQuiz / Visual QA：测试通过，页面就一定好用吗？

BMQuiz 是非常适合讲 Visual QA 的真实案例。

流程：

```text
Implement
→ Build
→ Start Preview
→ Playwright
→ Keyboard / Interaction
→ Screenshot
→ Observe
→ Fix
→ Re-run
```

【截图占位 BM-09｜Visual QA Workflow + Screenshot Artifact】

【录屏占位 BM-R01｜一次 UI 修改 → Browser QA → 发现问题 → 修复 → 再验证】

这段 Demo 应该成为第四讲非常强的视觉内容。

因为它让大家看到：

> Agent 不只是“写页面”，还可以把浏览器作为反馈环境。

---

# 14. BMQuiz / Git：用历史证明这是迭代工程

把 Git 历史整理成时间线：

```text
产品/UI
↓
PWA
↓
Visual QA
↓
Backend
↓
Health / Server CI
↓
Auth / Sync
↓
Docker / GHCR
↓
Android TWA
↓
Security / Governance
↓
Bug Fix
```

【图示占位 BM-10 / BM-12｜BMQuiz Git 演进时间线】

关键结论：

> **真实 Agent 工程不是“一次 Prompt 生成完整系统”，而是一个持续 Observe → Verify → Iterate 的过程。**

---

# 15. BMQuiz / CI/CD：代码通过以后，还要形成可以交付的制品

BMQuiz 当前已经有：

- CI；
- Server CI；
- Visual QA；
- Release QA；
- Docker Release；
- Fullstack Release；
- Android 构建。

可以画：

```text
Commit
↓
CI
├─ Typecheck
├─ Test
├─ Server
├─ Visual QA
└─ Release QA
↓
Build
↓
Docker Image / APK
↓
Release
```

【截图占位 BM-11｜GitHub Actions Workflow 列表 / Pipeline】

这里解释：

> CI/CD 不是“运维部门以后再做”。

它是：

> **让 Agent 输出能够重复验证、形成固定制品的一部分。**

---

# 16. BMQuiz / Deploy：Agent 怎样真正进入服务器

服务器任务不要从：

`ssh server`

开始。

从 Goal 开始：

> 把一个明确 Release 安全更新到服务器，保留 SQLite 数据，完成服务、认证和产品验证，必要时能回退。

完整过程：

```text
Read Deployment Rules
→ SSH
→ Observe Current State
→ Protect Data
→ Pull Fixed Version
→ Deploy
→ ps / logs
→ Health
→ Product Smoke
→ Security Smoke
→ Record
```

【截图占位 SERVER-01｜部署前 server state】

【截图占位 SERVER-02｜Docker Compose / logs / health】

【录屏占位 BM-R02 / SERVER-R01｜Release → SSH → Deploy → Health → Smoke】

这里一定要加入真实项目中的危险规则：

> 普通升级不能把删除数据卷的命令当成惯常操作。

目的不是让大家记 Docker 命令。

而是理解：

> **Agent 操作服务器以前，必须先读项目规则。**

---

# 17. BMQuiz / Verify：HTTP 200 不等于业务正确

部署后至少分层验证。

## Service

服务能否响应。

## Auth

未登录保护是否正确。

## Content Security

不该公开的路径是否真的不可访问。

## Product

登录、练习、同步。

## Persistence

重启后数据是否仍在。

这一点可以和 model-metric 做呼应：

> 服务在线和业务正确是两回事。

---

# 18. BMQuiz / Assetize：最终留下的不是代码，而是一套工程系统

BMQuiz 最终留下：

- AGENTS.md；
- Requirements；
- Architecture；
- Data Model；
- Design System；
- Agent Guide；
- Acceptance Checklist；
- Tests；
- Visual QA；
- CI；
- Docker；
- Deployment；
- Version Governance；
- Git History。

所以第一个主案例最后回到一个问题：

> 如果以后换掉 Codex / ZCode，哪些东西还在？

答案：

> **这些显式工程资产都还在。**

---

# 19. BMQuiz 现场不要从头开发：只演一个“小需求完整闭环”

完整历史用截图和 Git 讲。

现场只挑一个小需求。

要求它同时包含：

```text
Requirement
→ Read Rules
→ Plan
→ Edit
→ Test
→ Browser QA
→ Diff
```

【录屏占位 BM-R03｜BMQuiz 小增量需求完整 Agent Loop】

建议选择：

- UI 小功能；
- 一个已有测试可扩展的行为；
- 不涉及高风险 migration。

控制在 10～15 分钟原始过程，现场播放 2～4 分钟精华或现场重演其中部分。

---

# 20. 主案例二：FileCheck——为什么需要第二个完全不同的项目

如果只讲 BMQuiz，学员容易认为：

> Agent 工程就是 Web 开发。

FileCheck 是 Windows 离线客户端。

当前正式版本 README 已是 v0.2.3，产品面向：

> **Windows 终端离线文件自查、备份、完整性验证、安全删除和原路径恢复。**

它有：

- GUI；
- CLI；
- Everything / ES；
- SHA-256；
- 目录备份；
- 恢复；
- Windows 7 / 10 / 11；
- x64 / x86；
- PyInstaller；
- GitHub Actions；
- Release 包。

因此它能证明：

> **同一套 Agent 工程方法与 React、Web 没有绑定关系。**

【截图占位 FC-01｜FileCheck GUI 首页 + CLI 对照】

---

# 21. FileCheck / Problem：这里最重要的不是“做一个 GUI”

真实问题是：

> 在 Windows 终端离线环境中，对大量文件进行快速候选扫描，人工核对以后安全备份，并在明确条件下删除源文件，未来还要能够可靠恢复。

注意关键词：

- 离线；
- 大量文件；
- 候选；
- 人工核对；
- 备份；
- 完整性；
- 删除；
- 恢复。

这不是：

> 写一个搜索文件的小工具。

---

# 22. FileCheck / Requirement：安全产品必须写“不做什么”

项目需求明确：

- 快速索引；
- 关键词扫描；
- 人工核对；
- 批量目录备份；
- 完整验证；
- 显式源文件删除；
- 原路径恢复。

同时明确边界：

- 不是系统痕迹清理工具；
- 不自动清浏览器历史；
- 不清注册表；
- 不强制杀进程解锁；
- 不递归删除父目录；
- 关键词命中只是候选，不是最终性质判定。

【截图占位 FC-02｜Requirements：目标 + Non-goals】

这是第四讲第二次强化：

> **高风险软件里，Non-goals 和功能列表同样重要。**

---

# 23. FileCheck / Constraint：平台约束直接改变技术路线

它面对的约束与 BMQuiz 完全不同：

- Windows；
- 离线；
- 便携；
- Win7 SP1；
- x86 / x64；
- 中文 / Unicode 路径；
- 大批量文件；
- 用户可能已经安装 Everything；
- 高风险删除必须可验证；
- 不能因为 GUI 卡死破坏任务状态。

这些约束决定：

> 不能简单把 Web 应用那一套架构复制过来。

【图示占位 FC-03｜Windows / Offline / Win7 / Safety → Technical Decisions】

---

# 24. FileCheck / Research：技术选型要讲“约束”，不要讲“语言信仰”

可以设计一个课堂 Architecture Review：

> 如果今天从需求重新看，Python、Go 怎么选？

但必须明确：

> 这是课堂基于当前需求进行的 Review，不伪装成历史决策记录。

当前真实事实：

- 核心是 Python；
- GUI 是 CustomTkinter；
- GUI / CLI 复用同一 Core；
- 当前正式 v0.2.3 GUI/x64 CLI 使用 Python 3.8.10 + PyInstaller 5.13.2 的 Win7 兼容构建基线；
- x86 CLI 也有兼容包。

可以讨论候选：

## Python

优势：

- 文件 / 脚本生态成熟；
- 快速开发；
- 测试方便；
- Everything/CLI 调用自然。

约束：

- Packaging；
- Runtime compatibility；
- Win7 Python 版本限制。

## Go

可能优势：

- 单二进制；
- 分发简单；
- 并发和跨平台。

但迁移代价：

- 已有 Python Core；
- GUI 生态和当前实现；
- 大量已有测试需要重构。

因此工程决策不能只问：

> 哪个语言更先进？

而是：

> **在当前约束、已有资产和风险下，哪个方案总代价更合理？**

---

# 25. FileCheck / Architecture：先 Core，再 CLI，再 GUI

当前架构很适合教学：

```text
             Core
    ┌─────────┼─────────┐
    ↓         ↓         ↓
 Index      Backup    Restore
    │         │         │
    └─────────┼─────────┘
              ↓
        Stable Services
         ┌────┴────┐
         ↓         ↓
        CLI       GUI
```

【图示占位 FC-04｜Core → CLI / GUI】

真实设计规范明确：

> GUI 负责交互与状态展示，业务逻辑继续复用现有核心模块。

这就是一个非常好的架构原则：

> **界面层不要重新实现业务规则。**

---

# 26. FileCheck / 为什么先有 CLI 是很有价值的

CLI 让核心能力可以先独立验证：

```text
doctor
index
scan
backup
verify
remove-sources
restore
selftest
```

在 GUI 还没有完成前：

- 业务流程已经可运行；
- 自动测试可以直接调用；
- CI 可以验证；
- 出问题时容易定位 Core 还是 GUI。

【截图占位 FC-05｜CLI 命令 / selftest】

这能让大家理解：

> **先稳定业务内核，再做界面，比“先画页面再往里塞逻辑”更适合 Agent 长期维护。**

---

# 27. FileCheck / Reliability：这是比 GUI 更值得讲的技术内容

FileCheck 最有工程价值的不是界面，而是对高风险文件操作的约束。

备份：

```text
Preflight
→ staging .incomplete
→ copy
→ SHA-256
→ source stability
→ manifest
→ full verify
→ atomic publish
```

删除：

```text
verify backup
→ recheck all source files
→ any failure = do not start
→ explicit confirmation
→ per-file immediate check
→ unlink manifest path only
→ checkpoint
```

恢复：

```text
verify backup
→ copy to temp
→ SHA-256
→ atomic replace
→ final verify
```

【图示占位 FC-06｜Backup / Delete / Restore Safety State Machine】

这里强调：

> AI 写高风险功能时，更需要先把不可破坏的约束写成状态机和测试。

---

# 28. FileCheck / GUI：为什么不是“把 CLI 按钮化”

当前 GUI Design System 已明确：

- 统一视觉 Token；
- 固定导航；
- 危险操作使用 Danger UI；
- 高风险操作二次确认；
- 后台任务不阻塞 GUI 主线程；
- Worker 不直接操作 Tk 控件；
- progress 通过 queue / after 更新；
- 不能伪造百分比；
- GUI 必须能自己完成首次索引。

【截图占位 FC-07｜FileCheck GUI 首页 / Scan / Delete 页面】

【截图占位 FC-08｜Danger Confirm + 影响文件数量】

这说明：

> GUI 不是把 CLI 命令换成几个按钮。

它还承担：

- 状态表达；
- 风险沟通；
- 可取消流程；
- 用户路径。

---

# 29. FileCheck / Test：为什么 CI 里同时跑 Windows 和 Linux

当前 CI：

```text
Windows latest / Python 3.10
Windows latest / Python 3.12
Ubuntu latest  / Python 3.10
Ubuntu latest  / Python 3.12
```

Windows 还会做：

- GUI construction smoke；
- Python 3.8 compatibility；
- GUI import / construction。

【截图占位 FC-09｜GitHub Actions CI Matrix】

这里解释：

> 多平台 CI 的价值不一定是“产品支持 Linux”。

有时是：

- 核心逻辑跨环境验证；
- 尽早发现依赖问题。

同时一定要说：

> **CI 中 Python 3.8 构建通过，不等于真实 Windows 7 机器已经验收通过。**

这体现：

> Automated Verification 也有边界。

---

# 30. FileCheck / Packaging：本地客户端的“Release”到底是什么

Web 项目发布可能是：

> Docker Image。

本地 Windows 工具发布则是：

- EXE；
- portable directory；
- bundled dependency；
- architecture；
- checksum。

当前 v0.2.3 正式 Release 提供：

- GUI x64；
- CLI x64；
- CLI x86。

并内置 Everything / ES，不要求用户安装 Python。

【截图占位 FC-10｜v0.2.3 Release Assets】

【截图占位 FC-11｜GUI portable package tree + SHA256SUMS】

这很好地说明：

> **不同产品最终“交付物”不同，但都必须形成可以验证的 Artifact。**

---

# 31. FileCheck / GitHub Actions：CI 不只是跑 pytest

把流程画出来：

```text
Commit
↓
Regression
↓
Python compatibility
↓
GUI smoke
↓
PyInstaller
↓
EXE smoke
↓
Bundle Everything / ES
↓
ZIP validation
↓
SHA-256
↓
Release
```

【图示占位 FC-12｜FileCheck Build / Release Pipeline】

【录屏占位 FC-R02｜GitHub Actions → Build Artifact → Release】

这比单独上一节“什么是 CI/CD”更直观。

---

# 32. FileCheck 现场 Demo：选一个安全、可回滚的小需求

不要现场演示删除真实文件。

准备独立测试目录。

推荐 Demo：

> 给扫描结果增加一个新的状态显示或过滤条件。

完整流程：

```text
Requirement
→ Read Requirements / GUI Design
→ Inspect Core
→ Plan
→ Implement
→ pytest
→ GUI smoke
→ Launch GUI
→ Screenshot
→ git diff
```

【录屏占位 FC-R01｜FileCheck 小需求 Agent 开发闭环】

另一个预录：

> 测试目录备份 → verify → restore。

【录屏占位 FC-R03｜受控测试数据 Backup → Verify → Restore】

涉及源文件删除的演示只使用明确可丢弃的数据，并优先预录。

---

# 33. 两个主案例放在一起，真正想证明什么？

现在对比：

| | BMQuiz | FileCheck |
|---|---|---|
| 产品 | Web/PWA/Android | Windows GUI/CLI |
| 运行环境 | Browser + Server | Local Windows |
| 核心语言 | TypeScript/Node | Python |
| 持久化 | SQLite + local-first | File/Manifest/Operation State |
| UI 验证 | Playwright Visual QA | GUI Smoke + 实机 |
| 构建 | Vite/Docker | PyInstaller |
| 发布 | GHCR / APK | Portable ZIP / EXE |
| 部署 | Server | User endpoint |
| 共同方法 | Requirement → Constraint → Architecture → Test → Release | Requirement → Constraint → Architecture → Test → Release |

这就是第四讲最重要的比较：

> **Agent 工程方法不是某一技术栈的方法。**

---

# 34. 对照案例：model-metric——“服务活着”不等于“数据是对的”

model-metric 用来补一个非常重要的验证观念。

它的任务不是普通 CRUD。

它采集 vLLM Metrics，并计算：

- running；
- waiting；
- TPS；
- KV usage；
- multi-instance aggregate。

部署后：

`curl /api/overview`

返回 200。

仍然不能直接证明：

> 指标语义正确。

必须验证：

- scrape_mode；
- observed / expected instances；
- coverage ratio；
- aggregate_exact；
- running/waiting 聚合；
- counter gap。

【截图占位 MM-CASE-01｜model-metric overview / instances JSON】

【录屏占位 MM-CASE-R01｜systemd/log → API → 语义核验】

这给第四讲增加一个很好的结论：

> **Verification 应该验证业务语义，不只是验证程序没有报错。**

---

# 35. 快速案例：IPsec VPN——Agent 也可以帮助“找原因”，但不能代替实验

使用真实性能分析案例时，重点不是展示：

> AI 很会分析数据。

而是展示一个调查过程：

```text
现象
→ 数据整理
→ 可视化
→ 候选假设
→ 对比链路 / 报文 / RTT
→ 发现 10 Mbps Ethernet 瓶颈线索
→ 工程验证
```

【截图占位 IPSEC-01｜原始测试数据 / 曲线】

【截图占位 IPSEC-02｜Agent 分析出的候选假设】

【截图占位 IPSEC-03｜最终工程证据】

【录屏占位 IPSEC-R01｜数据 → 假设 → 证据链】

必须强调：

> **相关性不等于因果。**

Agent 负责扩大分析视野、提出候选解释。

最终仍然由：

- 配置；
- 实验；
- 实际链路；

确认因果。

---

# 36. 快速案例：HyperFrames——内容生产也可以工程化

这一案例用来打破：

> Agent = 写代码。

真实流程：

```text
Narrative
→ Script
→ Storyboard
→ Design Spec
→ HTML / CSS / SVG / GSAP
→ Timeline
→ Voice / Subtitle
→ Preview
→ Human Review
→ GitHub Actions
→ Render
```

当前已有 Kids / Metric / Wafer 多套实际工程。

【截图占位 HF-01｜Storyboard / Design Spec】

【截图占位 HF-02｜HTML/GSAP 场景源码 + Preview】

【截图占位 HF-03｜GitHub Actions Render】

【录屏占位 HF-R01｜修改一个场景 → Preview → Commit → Action → Video Artifact】

这里结论：

> **工程化的本质是把复杂工作拆成可描述、可执行、可验证、可重复的阶段，不只适用于软件开发。**

---

# 37. 快速案例：接口兼容性 / 安全验证——Agent 的价值在闭环

这一类案例只使用：

- 自有环境；
- 测试环境；
- 已授权系统。

培训不把重点放在技巧。

讲：

```text
Scope
→ Observe
→ Evidence
→ Hypothesis
→ Test
→ Fix
→ Regression
→ Report
```

【图示占位 SEC-01｜授权测试闭环】

如果使用网站测试 Demo：

> 选择 BMQuiz staging 或专用测试环境。

展示：

- 问题发现；
- 证据；
- 修复；
- Regression。

重点：

> **Agent 的价值不是“自动攻击”，而是帮助组织测试、证据、修复和回归。**

---

# 38. 第四讲最后：把所有案例重新收束成一个方法

不管是：

- BMQuiz；
- FileCheck；
- model-metric；
- IPsec；
- HyperFrames；

其实都可以看成：

```text
Goal
↓
Understand Context
↓
Plan
↓
Use Tools
↓
Observe
↓
Verify
↓
Iterate
↓
Deliver
↓
Assetize
```

【图示占位 METHOD-06｜全培训最终 Agent 工程闭环】

再给学员最后一张任务决策卡：

```text
只是一个问题？
→ Chat

依赖部门资料？
→ Knowledge / Search / RAG

需要修改文件或操作系统？
→ Agent

是复杂工程？
→ Workspace + Rules + Plan + Tools + Verification

以后还会重复？
→ Skill / Script / Test / CI / Knowledge
```

【图示占位 METHOD-07｜五问任务决策卡】

---

# 39. 第四讲素材准备

本讲 BMQuiz、FileCheck、model-metric、IPsec、HyperFrames 等案例的截图、录屏、现场 Demo 和备用素材统一维护在：

`docs/lectures/04-agent-engineering-practice-media-checklist.md`

正文中的素材占位继续保留；第四讲案例准备优先级、现场演示顺序和备用策略也在独立清单中统一维护。

# 43. 第四讲最后只留下七句话

1. **不要从 Prompt 直接跳到 Code。**
2. **Requirement、Constraint、Architecture 是在缩小 Agent 的错误搜索空间。**
3. **Git 不只是存代码，也是 Agent 变更、Review 和回滚的证据系统。**
4. **Test、Browser、CI、Logs、Health 都是反馈环境。**
5. **代码写完不等于产品完成，必须走到 Artifact、Release、Deploy 和 Verify。**
6. **人负责目标、边界和最终判断，不把责任交给 Agent。**
7. **一次成功实践最终应该留下 Rules、Docs、Skill、Scripts、Tests、CI、Knowledge 和 Git，而不是只留一段聊天记录。**
