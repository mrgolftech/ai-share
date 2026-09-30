# 完整工程案例：BMQuiz V2——Agent 怎样从需求走到可发布 Web 产品

> 状态：已有真实仓库与 Git 历史证据 / 待补原始对话、截图和录屏  
> 更新日期：2026-09-30  
> 真实仓库：`mrgolftech/BMQuiz-V2`  
> 当前主线：**Problem → Requirement → Constraint → Research → Architecture → Plan → Implement → Test → Visual QA → Review → CI/CD → Deploy → Verify → Assetize**

---

# 0. 为什么把 BMQuiz 选为第一完整案例

这不是因为 BMQuiz 技术栈“最先进”。

而是因为它已经形成了完整的工程证据链：

- 产品功能说明；
- UI/UX 说明；
- 技术架构；
- 数据模型；
- 路由与状态设计；
- 项目结构；
- Development Roadmap；
- Codex Implementation Guide；
- Acceptance Checklist；
- Design System；
- Visual QA；
- 前端 CI；
- Server CI；
- Release QA；
- Docker / GHCR；
- Android TWA / APK；
- 部署文档；
- Git 历史。

因此这个案例能够回答一个培训里非常重要的问题：

> **Agent 开发一个真实产品，究竟和“让 Chat 写一段代码”有什么不同？**

---

# 1. 先给学员看最终结果，但不从代码开始讲

当前 BMQuiz V2 是一个面向固定考试题库的本地优先学习应用。

产品链：

```text
背题
→ 练习
→ 即时反馈
→ 结果
→ 错题强化
→ 多设备学习状态同步
```

当前产品形态：

- Web；
- PWA；
- Android TWA / APK；
- email/password 账号；
- 邀请码；
- 管理员；
- 学习状态同步；
- Docker 单容器部署。

这里不立即展开 React / Fastify。

先问：

> **如果只给 Agent 一句话：“帮我做个刷题网站”，它能稳定得到今天这个结果吗？**

答案显然是否定的。

真正决定结果的是后面逐步形成的：

- 产品定义；
- 数据事实；
- 约束；
- 架构；
- 设计规范；
- 测试；
- 发布规则。

---

# 2. Problem：为什么要做 V2

教学时需要从真实历史资料和旧应用补充完整背景。

当前仓库已经保留：

`oldquiz/`

以及 V2 的产品说明和当前代码。

可以把问题抽象成：

> 已经有真实题库和旧应用，但希望把它升级为一个真正可长期使用、可多端运行、可同步、可测试、可发布的产品。

这里后续应补：

- [ ] V1 / oldquiz 截图；
- [ ] 当时主要痛点；
- [ ] 用户提出的原始需求；
- [ ] 第一版 Prompt / 对话；
- [ ] 最早 V2 commit。

注意：

> 如果没有历史证据，就只讲“从当前仓库可确认的问题”，不补写不存在的需求故事。

**素材占位：BM-01｜oldquiz 与当前 BMQuiz V2 对比**

---

# 3. Requirement：先把“做个网站”变成产品规格

BMQuiz 当前已经有：

`docs/01_PRODUCT_FUNCTION_SPEC.md`

里面明确：

- 53 道 canonical 填空题；
- 52 个 canonical KnowledgePoint；
- 156 道派生测试；
- 背题；
- 练习；
- WrongBook；
- PracticeHistory；
- ActivePractice；
- 本地备份；
- 账号；
- 邀请码；
- 多设备同步；
- Admin。

还明确了“不做什么”：

- 题库编辑平台；
- 教师管理；
- 多人在线考试；
- 排行榜；
- 社交；
- AI 实时出题。

这是一个非常好的教学点：

> **Requirement 不只是“想加哪些功能”，还应该定义产品边界。**

没有这些边界，Agent 很容易为了“看起来更完整”不断扩展功能。

**素材占位：BM-02｜Product Function Spec 关键页面**

---

# 4. Constraint：真正影响架构的是约束

当前仓库可以确认的关键约束包括：

## 数据事实

- 53 道填空题是 canonical；
- 52 个 KnowledgePoint 是 canonical；
- 题号、题干、答案不能因为 UI 重构被改写。

## 产品约束

- Web / PWA / Android 尽量共用业务实现；
- 学习状态 local-first；
- 多设备需要同步；
- 冲突不能静默覆盖。

## 安全约束

- canonical 题库不能继续作为匿名 public JSON；
- 登录后允许授权用户完整取得题库；
- Session 使用 HttpOnly Cookie；
- 管理员权限必须服务端判断。

## 部署约束

- 当前规模优先单机部署；
- SQLite；
- 单容器；
- 数据持久化到 `/data`；
- 需要备份与回滚。

这些约束共同决定：

> 不能简单拿一个“通用 SaaS 模板”套进去。

**素材占位：BM-03｜Constraint → Architecture 映射图**

---

# 5. Research：技术选型不能写成“模型推荐了 React”

当前技术栈：

## Frontend

- React；
- TypeScript strict；
- Vite；
- Tailwind CSS；
- TanStack Router；
- Zustand；
- Motion；
- PWA；
- Vitest；
- Playwright。

## Backend

- Node.js 22+；
- Fastify；
- Better Auth；
- SQLite；
- Drizzle；
- Vitest。

## Delivery

- Docker；
- GitHub Actions；
- GHCR；
- Android TWA。

但培训不能后验宣称：

> “这是最优技术栈。”

更严谨的讲法是：

> **这是当前项目在既定规模与约束下形成的实际方案。**

后续需要回查：

- [ ] 最初技术选型 Prompt；
- [ ] 是否比较过其他框架；
- [ ] GitHub 参考项目；
- [ ] 为什么没有 Next.js / NestJS / PostgreSQL 等；
- [ ] Android 为什么选择 TWA 而不是维护第二套原生 UI。

如果找不到历史证据，就把这一段表述为：

> **对当前技术路线做一次事后 Architecture Review。**

而不是伪造“当时 Agent 就是这么选的”。

---

# 6. Architecture：在写大量代码之前先固定系统边界

当前：

`docs/03_TECHNICAL_ARCHITECTURE.md`

已经形成清晰架构：

```text
Browser / PWA / Android TWA
            ↓ HTTPS
Reverse Proxy / TLS
            ↓
     Fastify
      ├─ React/PWA static
      ├─ /api/*
      └─ Better Auth
            ↓
     SQLite / content
```

更重要的是它还规定了内部边界：

```text
Presentation
→ Feature / Use Case
→ Domain
→ State / Persistence
→ API / Services
```

这能说明：

> **架构文档的价值不是“给领导看图”，而是让 Agent 知道代码应该放在哪里、哪些边界不能破坏。**

**素材占位：BM-04｜BMQuiz 当前系统架构**
**素材占位：BM-05｜前端分层与数据流**

---

# 7. Project Rules：AGENTS.md 把隐性经验变成项目约束

BMQuiz 当前 `AGENTS.md` 已经明确规定：

- 事实优先级；
- 技术基线；
- canonical 数据规则；
- UI 规则；
- Auth 规则；
- DB / migration 规则；
- 开工前检查；
- 分支 / PR；
- 前端完成条件；
- 后端完成条件；
- QA 同步规则；
- Release / Deploy；
- Android；
- 完成状态。

例如它明确规定：

> 未经架构决策，不主动替换为 Next.js、NestJS、PostgreSQL、Redis、Firebase、Supabase。

这个例子特别适合讲：

> **AGENTS.md 不是“提示词合集”，它用于把已经做出的长期工程决策从每次对话中拿出来。**

**素材占位：BM-06｜BMQuiz AGENTS.md**

---

# 8. Plan：文档先行，不等于写很多无用文档

BMQuiz 的文档层次可以直接用来回答：

> 什么叫“文档先行 Plan”？

当前包括：

```text
01 Product Function Spec
02 UI/UX Interaction Spec
03 Technical Architecture
04 Data Model
05 Routing / State
06 Project Structure
07 Development Roadmap
08 Codex Implementation Guide
09 Acceptance Checklist
10 Deployment
```

这些文档不是互相重复。

它们分别回答：

- 做什么；
- 怎么交互；
- 系统怎么分；
- 数据怎么定义；
- 状态怎么流；
- 代码放哪里；
- 按什么顺序做；
- Agent 怎么工作；
- 怎样算完成；
- 最后怎么上线。

核心结论：

> **好的 Plan 是减少 Agent 的歧义，而不是增加文档数量。**

**素材占位：BM-07｜Document-first 工程地图**

---

# 9. Implement：不要把完整案例讲成代码导览

课堂上不需要逐文件讲 BMQuiz。

只选 4 类代表性实现。

## 9.1 Canonical 数据

说明：

> AI 可以改代码，但不能“顺便优化”业务事实。

## 9.2 Local-first + Sync

展示：

```text
local snapshot
→ revision / CAS
→ stale write = 409 conflict
```

说明：

> 需求里的“多设备同步”最终必须落成具体一致性语义。

## 9.3 Authenticated Content

展示：

- 未登录完整题库 401；
- 登录后完整下发；
- `private, no-store`；
- 旧 static path 404。

说明：

> “安全需求”必须变成可以验证的行为。

## 9.4 Mobile / Desktop 共用 Domain

说明：

> 多端不等于复制两套业务逻辑。

---

# 10. Test：Agent 写完代码以后发生什么

当前项目有明确完成条件。

前端：

```bash
npm ci
npm run typecheck
npm test
npm run build
```

后端：

```bash
npm --prefix server ci
npm --prefix server run typecheck
npm --prefix server test
npm --prefix server run build
```

Server CI 进一步检查：

- dependency audit；
- migration 是否漏提交；
- fresh SQLite migration；
- required tables；
- health smoke。

这非常适合强调：

> **“Agent 说完成了”不是完成条件，机器可验证的门禁才是。**

**素材占位：BM-08｜Server CI 关键步骤**

---

# 11. Visual QA：这是 BMQuiz 最值得展示的 Agent 闭环之一

Git 历史可以看到：

- `8454fb68`：add browser screenshot visual QA harness；
- `9e1f01f0`：add visual QA screenshot workflow；
- 后续连续多次：
  - 修 UI；
  - 更新 QA；
  - 调整 reference；
  - 再验证。

当前 Visual QA workflow：

```text
npm ci
→ Playwright Chromium
→ build
→ start QA preview
→ keyboard/focus QA
→ visual checks
→ screenshots
→ upload artifact
```

这说明：

> **Browser 不是只用来“操作网站”，还可以把 UI 结果重新反馈给 Agent。**

形成：

```text
Implement
→ Browser
→ Observe
→ Screenshot
→ Compare
→ Fix
→ Re-run
```

**素材占位：BM-09｜Git Visual QA 演进时间线**
**录屏占位：BM-R01｜一次 UI 修改 → Visual QA → 修复闭环**

---

# 12. 从前端产品走到 Full-stack

Git 历史显示一个很清楚的阶段变化。

在 2026-08-28，先完成学习体验、PWA、Visual QA 和 Release QA。

随后出现：

- `90ba1f5a` scaffold backend architecture；
- `486da87f` graceful process lifecycle；
- `5422fa30` cover health endpoint；
- `4924f325` bootstrap server verification；
- `532f0205` reproducible server verification；
- `45e055c5` complete B2-B7 authenticated BMQuiz release。

这条历史可以用于说明：

> **复杂工程更适合分阶段扩展，而不是第一次就让 Agent 生成一个“全栈大一统项目”。**

**素材占位：BM-10｜Git 历史：Frontend → Server → Auth/Sync**

---

# 13. CI/CD：从代码完成到制品完成

BMQuiz 当前不仅有普通 CI。

还包括：

- Server CI；
- Visual QA；
- Release QA；
- Docker Image Release；
- Fullstack Release Gate；
- Android APK；
- Version Release。

Docker release 当前会：

```text
checkout
→ Buildx
→ GHCR login
→ metadata
→ build/push
→ inspect published image
→ report image size
```

并启用：

- provenance；
- SBOM。

这说明：

> **Agent 交付的最终对象不只是 Git 里的代码，还包括可验证的发布制品。**

**素材占位：BM-11｜CI/CD Pipeline**

---

# 14. Release：版本本身也是工程资产

当前项目规定：

`release/version.json`

是产品正式版本唯一真值。

它需要与：

- GitHub Release；
- GHCR tag；
- Android versionName；
- Android versionCode；

保持一致。

这解决的是一个经常被忽略的问题：

> **Agent 如果在多个文件随便改版本，很容易造成发布状态不一致。**

因此：

> 单一 Source of Truth 也是 Agent-friendly architecture。

---

# 15. Deploy：Agent 真正进入服务器

当前推荐：

`deploy/docker-compose.release.yml`

服务器流程：

```text
Read Deployment
→ SSH
→ check current state
→ protect SQLite data
→ docker login
→ pull fixed version
→ compose up
→ ps
→ logs
→ /api/health
→ product smoke
```

重要规则：

> 不把 `docker compose down -v` 当普通升级命令。

因为 `-v` 可能删除用户数据库 volume。

这正好体现：

> **Agent 操作服务器时，项目文档和权限边界比“会不会 SSH”更重要。**

完整服务器案例：

`docs/cases/agent-server-operations.md`

**录屏占位：BM-R02｜Release → SSH Deploy → Health → Smoke**

---

# 16. Verify：HTTP 200 不等于产品正确

部署后至少分层验证：

## Service

`/api/health`

## Auth

未登录访问受保护 API：

> 401

## Content Security

旧公开静态题库路径：

> 404

## Product

- 登录；
- 练习；
- 同步；
- 页面。

## Persistence

- SQLite volume；
- restart 后状态仍然存在。

结论：

> **Verification 必须覆盖业务语义，而不是只看进程状态。**

---

# 17. Android：Agent 工程为什么需要边界复用

BMQuiz 最终支持 Android，但没有再写一套原生业务 UI。

路线：

```text
Web/PWA
→ TWA
→ Bubblewrap / Gradle
→ APK
```

这也是架构决策案例：

> **不是平台越多，代码就应该越多。**

当前 Git 历史还记录了 signing、assetlinks、release workflow 的连续修复。

可以说明：

> 最终交付链本身也需要 Agent 反复 Observe → Fix → Verify。

---

# 18. Git 历史给出的真正结论：这是迭代工程，不是“一次生成”

当前可见历史呈现大致阶段：

## 阶段 A：产品与 UI

- learning experience；
- memorize / practice；
- design alignment。

## 阶段 B：浏览器验证

- screenshot harness；
- Visual QA workflow；
- 多轮 UI 修正。

## 阶段 C：Release QA

- release browser gate；
- acceptance report。

## 阶段 D：Backend

- scaffold；
- lifecycle；
- health；
- Server CI。

## 阶段 E：Auth / Sync / Production

- B2-B7；
- Docker；
- GHCR；
- Release。

## 阶段 F：Android

- TWA；
- signing；
- APK；
- assetlinks。

## 阶段 G：治理

- security hardening；
- architecture hygiene；
- release governance；
- 后续 bug fix。

这条时间线非常适合作为培训证据：

> **真实 Agent 工程更接近持续迭代的 Loop，而不是“一次 Prompt 生成完整系统”。**

**图示占位：BM-12｜BMQuiz Git 演进时间线**

---

# 19. 人在哪些地方做关键判断

这个案例必须避免讲成：

> AI 自己把系统做完了。

至少这些属于人的关键责任：

- 产品目标；
- canonical 数据边界；
- 功能范围；
- 技术路线接受/拒绝；
- 是否引入后端；
- 安全策略；
- local-first / sync 语义；
- 发布策略；
- 是否接受架构重构；
- UI 最终视觉判断；
- 生产升级和风险判断。

统一表达：

> **模型负责判断和生成，工具负责执行，自动化测试负责验证，人负责目标、约束和最终判断。**

---

# 20. 最后形成了哪些可复用资产

BMQuiz 最终留下的不只是产品代码：

- `AGENTS.md`；
- Product Spec；
- Architecture；
- Data Model；
- Design System；
- Codex Implementation Guide；
- Acceptance Checklist；
- Tests；
- Visual QA；
- CI；
- Docker；
- Deployment；
- Version governance；
- Release workflow。

所以这一案例最后应回扣模块五：

> **一次 Agent 开发如果只留下代码，资产还不完整；规则、测试、部署、验收与知识同样是产品的一部分。**

---

# 21. 课堂建议：不要从头演示开发整个 BMQuiz

不现实，也没有必要。

现场建议采用：

## 讲历史证据

用 Git 时间线说明完整工程过程。

## 做一个“增量需求”现场 Demo

例如选择一个小而完整的真实需求：

```text
提出需求
→ Agent 读取 AGENTS.md / docs
→ Plan
→ 修改
→ Test
→ Browser QA
→ Git Diff
→ CI
```

这样 10～20 分钟就能重新演示完整方法。

完整项目负责证明：

> 这个方法真的在大型实际项目里发生过。

小增量 Demo 负责证明：

> 这套方法现场可以重复。

---

# 22. 待补证据清单

## 历史

- [ ] earliest V2 commit；
- [ ] 原始需求聊天；
- [ ] 早期技术选型讨论；
- [ ] GitHub 参考项目；
- [ ] 关键架构变化的 PR / commit。

## 截图

- [ ] oldquiz；
- [ ] current UI；
- [ ] docs tree；
- [ ] AGENTS.md；
- [ ] architecture；
- [ ] Visual QA artifact；
- [ ] Server CI；
- [ ] Docker Release；
- [ ] GitHub Release；
- [ ] server deployment。

## 录屏

- [ ] BM-R01：UI 改动 → Browser Visual QA → 修复；
- [ ] BM-R02：Release → Server Deploy → Verify；
- [ ] BM-R03：小增量需求完整 Agent Loop。

---

# 23. 本案例最后只留下五句话

1. **真实应用开发不应该从 Prompt 直接跳到 Code。**
2. **需求、约束、架构和验收标准是在给 Agent 缩小错误搜索空间。**
3. **Browser、Test、CI 和 Server 都是 Agent 的反馈环境。**
4. **一个产品不是“代码写完”就完成，而是要经过 Build、Release、Deploy 和 Verify。**
5. **最有价值的结果不仅是代码，而是项目规则、文档、测试、CI 和发布流程都被沉淀下来。**
