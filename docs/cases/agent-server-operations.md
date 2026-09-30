# Agent 操作服务器——从“会 SSH”到真实部署、验证与排障闭环

> 状态：案例设计完成 / 待真实录屏与部署证据  
> 日期：2026-09-30  
> 对应模块：Agent 如何操作真实世界、完整 Web 工程案例  
> 原则：服务器操作不是命令展示，而是目标驱动的执行闭环。

---

# 1. 当前培训已经有服务器内容，但缺什么

现有讲义已经覆盖：

- SSH；
- Docker；
- Runtime；
- 日志；
- 健康检查。

已有：

`docs/cases/agent-runtime-environment-intranet.md`

但它主要回答：

> **Agent 运行环境需要什么。**

本案例进一步回答：

> **一个真实应用已经开发并发布后，Agent 怎样把它部署到服务器，并判断部署是否成功。**

---

# 2. 案例 A：BMQuiz Docker 部署

当前真实仓库：

`mrgolftech/BMQuiz-V2`

已经具备：

- Dockerfile；
- GHCR；
- docker-compose.release.yml；
- Deployment 文档；
- health API；
- SQLite volume；
- GitHub Actions Docker Release。

因此可以形成完整任务：

> **把 BMQuiz 的某个明确版本安全更新到服务器，并完成验证。**

---

# 3. 不从 SSH 开始，从 Goal 开始

错误演示：

```text
ssh server
docker ps
docker pull ...
```

正确教学：

```text
Goal:
将 BMQuiz 从当前版本升级到指定 release，
保留 SQLite 数据，
升级失败能够回退，
升级完成后验证服务、认证与题库安全行为。
```

然后 Agent 才开始读取：

- AGENTS.md；
- Deployment；
- Release；
- current server state。

---

# 4. 服务器执行闭环

```text
Goal
→ Read deployment rules
→ SSH
→ Observe current state
→ Backup / protect data
→ Pull artifact
→ Deploy
→ Observe process/container
→ Inspect logs
→ Health check
→ Application smoke
→ Security smoke
→ Record result
```

---

# 5. Step 1：读取项目事实

Agent 首先应该读取：

- 当前 release version；
- Compose；
- 环境变量说明；
- 数据 volume；
- upgrade / rollback 文档。

而不是凭经验直接执行：

`docker compose down -v`

因为 BMQuiz 当前 Deployment 明确：

> 普通重启/升级不能使用 `down -v`，否则可能删除数据库 volume。

这正好说明：

> **服务器 Agent 的第一能力不是敲命令，而是先读取项目规则。**

---

# 6. Step 2：建立 Preflight

至少检查：

- hostname；
- OS；
- disk；
- docker；
- docker compose；
- current container；
- current image；
- volume；
- network；
- free space；
- credentials 是否存在但不回显。

示意：

```text
whoami
hostname
docker version
docker compose version
docker compose ps
docker inspect ...
df -h
```

---

# 7. Step 3：数据保护

BMQuiz 用户状态位于：

`/data/bmquiz.sqlite`

教学重点不是具体备份命令，而是：

> **Agent 必须先识别哪些状态是可重建的，哪些是不可丢的数据。**

例如：

- Docker image：可重新拉取；
- canonical 题库：随 image 发布；
- SQLite：用户数据，不可丢；
- secret：不能写入仓库和日志。

---

# 8. Step 4：部署明确版本

推荐固定：

`vX.Y.Z`

而不是长期依赖：

`latest`

教学原因：

- 可追踪；
- 可回滚；
- 可审计。

Agent 执行：

```text
docker login
→ docker compose pull
→ docker compose up -d
```

但所有 destructive / production 操作应按环境策略要求审批。

---

# 9. Step 5：不是“容器启动”就算成功

至少验证四层。

## Process

`docker compose ps`

## Log

`docker compose logs --tail ...`

## Health

`GET /api/health`

## Product behavior

例如：

- 未登录完整题库返回 401；
- 旧静态题库路径返回 404；
- 登录页面正常；
- 数据 volume 仍存在。

这对应：

```text
Process Healthy
≠
Application Correct
```

---

# 10. Step 6：失败时不要随机试命令

排障路径应该按层：

```text
Container
→ Process
→ App Log
→ Local HTTP
→ Reverse Proxy
→ DNS / TLS
→ External Access
```

例如：

> 本机 `curl 127.0.0.1:3000/api/health` 成功，但公网失败。

此时优先：

- reverse proxy；
- DNS；
- TLS；
- firewall；

而不是先删除数据库、重建整个服务。

---

# 11. Step 7：Rollback

部署前就应该知道：

- 上一个 image tag；
- Compose 配置；
- 数据兼容性；
- DB migration 是否可回退。

Agent 不能等失败以后再问：

> “怎么回滚？”

因此：

> **Rollback 是 Plan 的一部分，不是异常发生后的临时动作。**

---

# 12. 案例 B：model-metric systemd 服务运维

model-metric 当前真实仓库提供：

- `deploy/model-metric.service.example`；
- systemd；
- `journalctl`；
- SQLite；
- `/api/overview`；
- `/api/instances`；
- 多实例采集语义。

适合演示另一种服务器任务：

> **Agent 不通过 Docker，而是维护一个 Python/systemd 服务。**

流程：

```text
SSH
→ systemctl status
→ journalctl
→ inspect config
→ backup DB
→ update
→ pip install
→ restart
→ status
→ logs
→ /api/overview
→ /api/instances
→ verify metric semantics
```

---

# 13. 为什么 model-metric 的 Verify 更有教学价值

监控服务即使 HTTP 200，也可能：

- 实例没采全；
- TPS 算错；
- Gauge 聚合错；
- 数据 coverage 不足。

因此 Verify 不能停在：

> “页面能打开”。

还应该验证业务语义，例如：

- expected_instances；
- observed_instances；
- coverage_ratio；
- aggregate_exact；
- running / waiting；
- TPS。

这非常适合说明：

> **Agent Verification 必须理解领域成功标准。**

---

# 14. Permission / Approval

服务器案例必须明确：

## 可以自动

- read status；
- read logs；
- health check；
- disk check；
- non-destructive query。

## 需要根据环境审批

- restart；
- deploy；
- migrate；
- modify config；
- delete；
- rollback；
- production traffic change。

核心观点：

> **Skill 可以规定流程，但真正的安全边界来自 Permission / Approval / Credential Scope / OS / Container / Network。**

---

# 15. 最终让学员看到的不是 SSH，而是一个 Agent Loop

```text
Goal
↓
Read Project Rules
↓
Observe Server
↓
Plan
↓
Act
↓
Observe
↓
Verify
↓
Iterate / Rollback
↓
Deliver Report
```

这才是：

> **Agent 操作服务器。**

---

# 16. 待补真实素材

## BMQuiz

- [ ] 当前线上版本；
- [ ] SSH 登录后当前状态；
- [ ] Compose；
- [ ] pull/up；
- [ ] logs；
- [ ] health；
- [ ] application smoke；
- [ ] rollback / previous tag；
- [ ] Agent 执行 Trace。

## model-metric

- [ ] systemctl status；
- [ ] journalctl；
- [ ] update / restart；
- [ ] /api/overview；
- [ ] /api/instances；
- [ ] 实际页面；
- [ ] Agent Trace。

建议录屏编号后续加入 `media-capture-checklist.md`。

