# Agent 操作真实世界：证据基线（2026-09）

> 用途：支撑 `docs/chapters/05-agent-tools-real-world.md`。  
> 原则：区分稳定工程机制、官方当前实现、仓库实测和待验证内容。

## 1. 本章可以稳定讲的机制

### 1.1 Tool Call 是“模型请求动作，Harness/Runtime 执行动作”

培训中采用：

```text
Model → Tool Request → Harness/Runtime → External System → Tool Result → Model
```

这是工具调用的教学抽象，不绑定某一款 Agent UI。

### 1.2 File / Shell / Git / Browser / API 是不同执行通道

- File：操作 Workspace 中的文件和目录；
- Shell：执行现有 CLI / Script / Compiler / Test 工具；
- Git：记录和比较工程状态；
- Browser：交互网页和 UI；
- API：结构化调用外部系统。

不要把它们全部简化为“模型会操作电脑”。

---

## 2. Playwright：可重复浏览器自动化的官方证据

官方文档：

- https://playwright.dev/docs/actionability
- https://playwright.dev/docs/test-assertions
- https://playwright.dev/

当前官方文档明确说明：

- Playwright 在执行动作前进行 actionability checks；
- 具备 auto-waiting；
- Web assertions 可以自动重试直到满足条件或超时；
- 官方首页把 Playwright 同时定位到 testing、scripting 和 AI agent workflows。

培训可以据此讲：

> **Playwright 的核心价值不只是“会点击网页”，而是能够把 UI 操作变成可重复、可断言的自动化。**

---

## 3. Computer Use：GUI 操作循环的官方证据

官方文档：

- https://developers.openai.com/api/docs/guides/tools-computer-use

当前文档说明 Computer Use 用于 browser / desktop interface，并描述通过：

- screenshot / observation；
- mouse / keyboard 或 code actions；
- environment execution；
- 新 observation；

形成循环。

培训可据此区分：

> **Computer Use 更偏通用 GUI 操作；Playwright 更偏程序化 Web 自动化与测试。**

注意：

- 不把 OpenAI 当前实现写成所有 Computer Use 产品都完全相同；
- 培训使用机制对比，不做产品绝对能力排名。

---

## 4. Codex Sandbox / Approval：执行能力与权限边界

官方资料：

- https://developers.openai.com/docs/config-file/config-basic

当前文档明确区分：

- approval policy；
- sandbox mode；
- workspace write；
- network / filesystem permission。

培训可以据此强调：

> **“Agent 能执行命令”不等于“Agent 被授权无限制执行命令”。**

这一点应与 Shell、SSH、生产运维内容绑定讲解。

---

## 5. Git：状态、Diff、Commit 的官方定义

官方资料：

- https://git-scm.com/docs/git-status
- https://git-scm.com/docs/git-diff
- https://git-scm.com/docs/git-commit.html

当前官方文档：

- `git status` 展示 Working Tree / Index / HEAD 之间的状态；
- `git diff` 比较 Working Tree、Index、Tree/Commit 等差异；
- `git commit` 形成可追踪提交。

培训结论：

> **Git 既是协作工具，也是 Agent 任务中的状态、审计和回退基础。**

---

## 6. Docker：Logs / Healthcheck 的官方证据

官方资料：

- https://docs.docker.com/reference/cli/docker/container/logs/
- https://docs.docker.com/engine/containers/run/

官方文档明确：

- `docker logs` 可以读取容器日志；
- Docker 支持 Healthcheck 配置和状态。

因此 SSH / Docker 教学 Demo 应至少包含：

```text
container state
+ logs
+ health / real request
```

不要只以“docker compose up 没报错”作为部署成功证据。

---

## 7. GitHub Actions：独立验证层

官方资料：

- https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows

官方定义中，Workflow：

- 存在仓库 YAML；
- 可以由 repository event / manual / schedule 触发；
- 包含 Jobs / Steps；
- 可用于 build / test / deploy。

培训可以据此讲：

> **CI 把验证规则写进仓库，使验证不依赖某次 Agent 会话。**

---

## 8. 与仓库已有证据的连接

### 8.1 内网 API

已有：

- `docs/chapters/01-intranet-qwen-api.md`
- `api/qwen/`

可支撑“Shell/curl/API 自动测试/metrics”部分。

### 8.2 model-metric

已有：

- `docs/cases/model-metric-api-observability.md`

可支撑：

> API 调通后还要观察运行状态，而不是只看单次返回。

### 8.3 Agent Harness

已有：

- `docs/chapters/04-agent-common-mechanisms.md`
- `docs/references/coding-agent-comparison-2026-09.md`

可支撑：

- Tool；
- Sandbox；
- Browser；
- Runtime Backend；
- WorkBuddy Workspace；
- Codex/OpenCode/Hermes 等 Harness 差异。

---

## 9. 当前仍需实测，不应写成既成事实的部分

以下是“教学方案”，不是当前 `ai-share` 已有实测证据：

1. SSH → Docker → Logs → Health Check 的完整录屏；
2. 浏览器 Visual QA 完整录屏；
3. 同一任务 API Tool vs GUI 操作对比；
4. Agent 自动 Commit / Push → CI 的完整训练案例；
5. 内网 qwen3.6 在具体 Harness 中完成上述任务的稳定性。

后续补证据后，应把对应项从：

> 待实测

改为：

> 已有实测证据 / 可用于培训。


---

## Playwright：Python / Node.js 与 Agent Browser Tooling

### 官方事实

Playwright 官方 Supported Languages 文档说明：

- JavaScript / TypeScript、Python、Java、.NET 共用同一底层实现；
- 核心浏览器自动化能力在各语言都支持；
- 差异主要体现在测试框架生态；
- Node.js 版本配套 Playwright Test；
- Python 官方推荐 pytest plugin。

来源：
- https://playwright.dev/docs/languages
- https://playwright.dev/python/docs/languages

Playwright 当前面向 Coding Agent 的 playwright-cli 官方文档：

- 定位为 coding agents 的 token-efficient browser automation；
- prerequisite 为 Node.js 20+。

来源：
- https://playwright.dev/docs/getting-started-cli

Playwright MCP 当前通过 npx 运行，因此 Node/npm 是其直接运行依赖。

Playwright Python 官方提供：

- browser.new_browser_cdp_session()
- browser_type.connect_over_cdp()

说明 Python 同样可以直接访问 CDP。

来源：
- https://playwright.dev/python/docs/api/class-browser
- https://playwright.dev/python/docs/api/class-browsertype

### CDP 官方事实

Chrome DevTools Protocol 是由命令和事件组成的结构化 JSON 协议，官方生态列出了 JavaScript / TypeScript、Python、Java、Go 等多种 client。

来源：
- https://chromedevtools.github.io/devtools-protocol/

### Puppeteer

Puppeteer 当前官方定义为 JavaScript browser automation library；Chrome 默认通过 CDP 自动化。

来源：
- https://pptr.dev/guides/what-is-puppeteer
- https://pptr.dev/faq

### 培训结论

> 浏览器/CDP 不是只能 Node.js；Python 同样能够完整自动化 Chromium。

但：

> 当前 coding-agent 浏览器工具链里，Playwright CLI/MCP、Puppeteer 等工具使 Node.js 成为很有价值的标准运行时。

因此内网 Agent 标准环境建议同时预置 Python 与 Node.js，而不是二选一。
