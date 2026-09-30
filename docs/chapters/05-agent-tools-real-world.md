# 模块三：Agent 如何操作真实世界——从 Tool Call 到可验证的工程闭环

> 状态：已有初稿 / 可进入教学打磨  
> 更新日期：2026-09-30  
> 对应培训主线：**模型怎么调用 → 为什么 Chat 不够 → Agent 如何操作真实世界 → 如何让 Agent 掌握工具**  
> 上一章：`04-agent-common-mechanisms.md`  
> 下一章：API / MCP / Skill / Plugin / Command / Hook

---

## 0. 这一章不讲“工具列表”，而讲一件事

前一章已经建立了一个统一认识：

> **Agent = Model + Harness。**

但学员很容易留下第二个疑问：

> **模型本身明明只能生成 Token，它为什么能够改文件、执行命令、开浏览器、登录服务器，甚至完成部署？**

答案不是“模型突然会操作电脑了”，而是：

> **Harness 把模型连接到一组外部工具；模型负责选择动作和生成参数，工具负责真实执行，执行结果再回到模型，形成连续闭环。**

这一章只围绕一个统一工作循环展开：

```text
Goal
  ↓
Read / Observe
  ↓
Choose Tool
  ↓
Act
  ↓
Get Tool Result
  ↓
Verify
  ↓
Need more work?
  ├─ Yes → Iterate
  └─ No  → Deliver
```

对工程任务，可以进一步压缩为：

> **读 → 做 → 看结果 → 验证 → 留痕 → 交付。**



## 0.1 本章采用 ZCode 作为第一套贯穿案例

为了避免把 File / Shell / Git / Browser / Permission 讲成一串抽象名词，本章第一套完整案例固定使用 **ZCode Agent**。

选择它不是为了得出“ZCode 最好”的结论，而是因为当前 ZCode 把 Workspace、文件树、Terminal、Built-in Browser、Git / Review、Execution Modes、AGENTS.md 和 Goal Mode 集中在同一套 ADE 中，适合让学员在一个连续画面里看到 Agent Harness 的执行闭环。

本章统一采用：

```text
一个问题
→ 一个 ZCode 真实画面
→ 一个底层 Agent 机制
→ 一个可迁移到其他 Agent 的结论
```

例如：

| 先问的问题 | ZCode 案例 | 底层机制 |
|---|---|---|
| Agent 怎么知道项目规则？ | 读取 Workspace `AGENTS.md` | Project Instructions |
| Agent 怎么知道 Bug 真的存在？ | Terminal 运行失败测试 | Tool Execution / Observation |
| Agent 怎么找到相关代码？ | File Tree / Search / Read | Selective Context |
| 改完怎么知道修好了？ | 重跑测试 | Verification Loop |
| 人怎么知道改了什么？ | Review / Git Diff | State / Audit |
| 为什么不能一直 Full Access？ | Execution Modes | Permission / Human-in-the-loop |
| 长任务为什么能持续？ | Goal Mode | Task State / Completion Loop |

贯穿案例分两层：

1. **视觉闭环：鹈鹕骑自行车**  
   用 Browser 快速展示“生成 → 执行 → 看结果 → 修改 → 再验证”。

2. **工程闭环：Sensor Guard 边界 Bug**  
   使用 `demos/zcode-real-world/project/`，展示“读规则 → 跑测试 → 定位 → 最小修复 → 重测 → Diff”。

详细案例设计：

- `demos/zcode-real-world/README.md`
- `docs/cases/zcode-agent-real-world.md`

需要始终强调：

> **ZCode 是案例载体，真正要带走的是 Workspace + Tools + State + Permission + Verification。**


---

# 1. 问题：Chat 给了代码以后，谁来真正执行？

假设任务不是“告诉我怎么改”，而是：

> 在一个现有 Web 项目中修改一个按钮文案，并确认页面真的显示正确。

普通 Chat 最多能做到：

1. 猜测项目结构；
2. 给出一段代码；
3. 告诉用户“请自行修改和测试”。

Agent 需要真正完成：

```text
读取仓库
→ 找到目标文件
→ 修改文件
→ 运行测试/构建
→ 启动服务
→ 打开浏览器
→ 检查页面
→ 如果异常继续修复
→ 查看 Diff
→ 输出结果
```

这里至少已经出现了：

- File System；
- Search；
- Shell；
- Git；
- Browser；
- Test；
- Verification。

这正是 Agent 与“只会对话”的关键区别。

> **Agent 的价值不是一次 Tool Call，而是能够围绕目标连续组织多个 Tool Call。**

---

# 2. 问题：模型真的在“操作电脑”吗？——先看 Tool Call

## 2.1 模型并不是直接“执行命令”

可以把工具调用理解成三步。

### 第一步：Harness 告诉模型“有哪些工具”

例如：

```text
read_file(path)
write_file(path, content)
run_command(command)
open_browser(url)
git_diff()
```

模型看到的是工具名称、用途、参数 Schema，而不是直接得到操作系统控制权。

### 第二步：模型选择工具并生成参数

例如：

```json
{
  "tool": "run_command",
  "arguments": {
    "command": "pytest -q"
  }
}
```

### 第三步：Harness 真正执行，并把结果返回

例如：

```text
12 passed, 1 failed
FAILED tests/test_api.py::test_health
```

模型再根据这个结果判断下一步。

所以更准确的结构是：

```text
Model
  ↓ tool request
Harness
  ↓ execute
OS / Browser / API / Remote Service
  ↓ result
Harness
  ↓ tool result
Model
```

**截图占位：TOOL-01 Agent Tool Loop 总图**


## 2.2 一个容易漏掉的层：有 Tool，不等于环境里真的有这个命令

前面的 Tool Call 图还缺一层：

~~~text
Model
  ↓
Harness
  ↓
Tool / Terminal
  ↓
Execution Environment
  ↓
Git / Python / Node / npm / Docker / Compiler
  ↓
Project Dependencies / Internal Services
~~~

这对工程 Agent 特别重要。

例如 Harness 给了 Agent 一个 Terminal Tool，只表示：

> **Agent 可以请求执行 Shell 命令。**

它并不自动保证当前环境里存在：

- git；
- python；
- pip；
- node；
- npm；
- docker；
- cmake；
- gcc / MSVC；
- 项目依赖。

所以需要严格区分：

### Harness Capability

Agent 有没有：

- Terminal；
- File；
- Browser；
- Git / Review UI；
- MCP；
- Permission。

### Runtime Capability

Agent 当前所在环境有没有：

- 对应可执行程序；
- 正确 PATH；
- 正确版本；
- 项目依赖；
- 内网证书；
- Package Registry；
- 网络权限。

这也是为什么：

> **同一个模型、同一个 Agent、同一个 Prompt，换一台机器可能完全不同。**

**图示占位：ENV-01｜Model → Harness → Tool → Runtime → Toolchain 分层图**


---

# 3. 问题：Agent 怎么接触一个已有项目？——ZCode Workspace / File

## 3.1 为什么文件能力如此基础

真实工程信息大量存在于文件中：

- 源代码；
- 配置；
- README；
- AGENTS.md；
- 测试；
- 日志；
- CSV / JSON；
- Markdown；
- 构建产物。

如果 Agent 只能接收用户粘贴的一小段文本，它看到的是一个“问题切片”。

如果 Agent 可以读取 Workspace，它面对的是：

> **一个有目录结构、有依赖关系、有历史状态的工程对象。**

---

## 3.2 文件操作不是“把整个仓库塞进上下文”

这是教学中要特别纠正的一点。

合理方式通常是：

```text
先看目录
→ 搜索关键词/符号
→ 读取相关文件
→ 只展开必要片段
→ 修改
→ 再读取/对比结果
```

而不是：

```text
把所有文件全文一次性发给模型
```

原因很现实：

- 上下文有限；
- 长上下文有 Prefill 成本；
- 无关内容增加干扰；
- Agent 往往需要动态决定“下一步再读什么”。

这与知识库章节的结论一致：

> **外部检索解决“先找到什么”，Context Management 解决“最终给模型多少”。**

---

## 3.3 搜索比盲读更重要

常见工具包括：

- 文件名搜索；
- 文本搜索；
- `grep` / `rg`；
- 符号索引；
- AST / Language Server；
- Git 历史。

教学不要把“read file”讲成唯一方式。

真正高效的 Agent 往往是：

> **先定位，再读取；先缩小范围，再展开上下文。**

**截图占位：TOOL-02 Workspace 目录 + 搜索 + 局部读取**

---

# 4. 问题：Agent 怎么使用现成工程工具？——ZCode Terminal / Shell

## 4.1 Shell 的本质不是“黑窗口”

Shell 提供的是一个非常通用的程序执行接口。

但必须先强调：

> **Terminal 是通道，不是工具链本身。**

如果当前执行环境没有 Python，那么 Agent 输入 `python test.py` 仍然只会得到 command not found；如果 npm registry 在内网不可达，Agent 再聪明也无法凭空下载依赖。

只要环境里安装了对应工具，Agent 就可能通过 Shell 调用：

- `git`
- `python`
- `pytest`
- `node`
- `npm`
- `docker`
- `curl`
- `ssh`
- 编译器
- 格式化器
- 静态检查器
- 自研 CLI

因此可以把 Shell 理解成：

> **Agent 连接已有工程工具链的通用入口。**

---

## 4.2 为什么不应该让模型重新实现所有能力

例如要检查 HTTP 接口：

差的方法：

> 让模型“凭知识”猜接口是否正常。

更好的方法：

```bash
curl -sS http://127.0.0.1:8000/health
```

要运行测试：

```bash
pytest -q
```

要看容器：

```bash
docker ps
docker logs --tail 100 app
```

这里传递的工程原则是：

> **模型负责不确定性判断；成熟工具负责确定性执行。**

---

## 4.3 Shell 也带来最大的风险面之一

因为 Shell 可能影响：

- 文件；
- 网络；
- 凭据；
- 进程；
- 容器；
- 远端服务器。

所以必须和前一章的 Permission / Sandbox 一起理解。

例如可以区分：

```text
只读命令
→ 工作区内写入
→ 安装依赖
→ 网络访问
→ Docker / 系统操作
→ SSH / 生产环境操作
```

风险越高，越应该：

- 限制环境；
- 明确审批；
- 保留日志；
- 建立回滚；
- 用测试和健康检查验证。

OpenAI Codex 当前官方配置就明确区分审批策略和 Sandbox Mode，这说明“Agent 能执行”与“Agent 被允许执行什么”是两回事。

**截图占位：TOOL-03 Terminal Tool Call + Approval / Sandbox**

---

# 5. 问题：人怎么知道 Agent 实际改了什么？——ZCode Review / Git

## 5.1 为什么 Agent 特别需要 Git

Agent 会频繁修改文件。

如果没有 Git，最危险的问题是：

> **到底改了什么？哪些是原来的？失败后怎么回退？**

Git 提供了一套天然的工程状态机制：

```text
Current Commit
   ↓
Working Tree
   ↓ edit
git status
   ↓
git diff
   ↓ test
commit
   ↓
push / PR
   ↓
CI
```

Git 官方文档把 `git status` 定义为查看 Working Tree / Index 与 HEAD 的差异，`git diff` 用于比较工作区、索引和提交之间的变化。

对 Agent 来说，这些不是“额外功能”，而是验证链的一部分。

---

## 5.2 教学重点：先 Diff，再相信“我已经改好了”

Agent 的自然语言总结可能遗漏内容。

Diff 是更可靠的事实。

建议建立固定动作：

```text
修改前：确认当前 branch / SHA / working tree
修改后：git status
       → git diff
       → test
       → 必要时 build / browser
       → commit
```

一句话：

> **不要只检查 Agent 说了什么，要检查仓库实际发生了什么。**

**截图占位：TOOL-04 git status + git diff + test 三联图**

---

## 5.3 Git 还是多 Agent / 长任务的边界工具

长任务常见风险：

- 改动越来越多；
- 中间方案失败；
- 多个 Agent 修改同一文件；
- 用户中途切换方向。

合理做法可以包括：

- 小步提交；
- 独立 Branch；
- Worktree；
- PR；
- Commit SHA；
- Tag / Release。

因此 Git 不只是“保存代码”。

更准确地说：

> **Git 为 Agent 提供可比较、可回退、可审计的状态边界。**

---

# 6. 问题：Agent 说“修好了”，凭什么相信？——Test / Verification

## 6.1 三种常见误判

### 误判一：命令退出码是 0，所以功能一定正确

不一定。

Build 成功只能证明：

> 构建过程没有按当前规则失败。

### 误判二：单元测试通过，所以用户界面一定正常

不一定。

前端可能：

- 按钮被遮挡；
- 字体异常；
- 页面溢出；
- 请求失败但测试没有覆盖；
- Console 报错。

### 误判三：页面能打开，所以业务流程一定正确

也不一定。

需要进一步：

- 点击；
- 输入；
- 提交；
- 检查状态；
- 验证返回结果。

---

## 6.2 Verification 要分层

建议培训使用四层验证：

```text
L1 静态检查
   lint / typecheck / compile

L2 自动化测试
   unit / integration / API test

L3 运行态验证
   health check / logs / real request

L4 用户界面验证
   browser / visual QA / end-to-end
```

注意：

> 这不是固定行业等级，而是本培训为了帮助工程师理解验证层次而使用的教学分层。

**图示占位：TOOL-05 Verification Ladder**

---

# 7. 问题：Agent 怎么“看到”网页？——Browser / Playwright / Computer Use / Crawler

这是这一章最容易讲乱的地方。

---

## 7.1 Browser Use：目标导向的网页理解与交互

典型过程：

```text
打开页面
→ 观察页面结构
→ 找到元素
→ 点击/输入
→ 读取变化
→ 决定下一步
```

它强调的是：

> **Agent 围绕目标理解网页并交互。**

实现可以基于：

- DOM / Accessibility Tree；
- 浏览器控制协议；
- 截图 + 视觉；
- Playwright；
- 专用 Browser Agent。

因此 Browser Use 是一个能力概念，不等于某一个固定库。

---

## 7.2 Playwright：程序化、可重复、可断言的 Web 自动化

Playwright 的教学重点不是“它也能点击网页”，而是：

> **它能够把浏览器过程写成可重复执行和可断言的测试。**

官方文档强调：

- Actionability checks；
- Auto-waiting；
- Web-first assertions；
- 自动重试直到满足条件或超时。

例如：

```javascript
await page.getByRole('button', { name: '保存' }).click();
await expect(page.getByText('保存成功')).toBeVisible();
```

这比：

> “我看了一眼，应该保存成功了。”

更适合回归测试。

---

## 7.3 Computer Use：更通用的 GUI 操作

Computer Use 面向的范围更广：

- Browser；
- Desktop App；
- 远程桌面；
- 没有结构化 API 的 GUI。

OpenAI 当前官方 Computer Use 文档描述的基本循环是：

```text
Model observes screenshot/tool result
→ requests mouse/keyboard/code actions
→ environment executes
→ returns new observation
→ model continues
```

它解决的是：

> **当任务必须通过 GUI 完成时，如何让 Agent 看见并操作界面。**

---

## 7.4 Crawler：目标通常是“获取数据”，不是“完成 UI 任务”

爬虫更强调：

- 下载网页；
- 提取正文；
- 遍历链接；
- 结构化数据；
- 批量采集。

它不一定需要像人一样：

- 点击按钮；
- 拖拽；
- 操作菜单；
- 完成业务流程。

---

## 7.5 四者怎么选

| 需求 | 优先方式 |
|---|---|
| 有稳定 API | API / Structured Tool |
| 要做网页 E2E 验证 | Playwright |
| 要探索式操作网页 | Browser Use |
| 只有 GUI，没有可用 API/DOM | Computer Use |
| 要大规模抓取公开网页内容 | Crawler / HTTP Fetch |

核心原则：

> **结构化接口通常优先于视觉模拟操作；可重复自动化通常优先于一次性人工式点击。**

这不是说 Computer Use “不高级”，而是：

> **工具越结构化，输入输出通常越明确，也越容易测试和审计。**

**图示占位：TOOL-06 Browser / Playwright / Computer Use / Crawler 对比**

---

# 8. 问题：代码测试通过，页面就一定能用吗？——ZCode Browser Visual QA

真实 Web 项目经常出现：

```text
代码检查通过
测试通过
构建通过
但页面不好用
```

因此对 UI 任务推荐：

```text
Implement
→ Run App
→ Browser Open
→ Interact
→ Screenshot
→ Console / Network
→ Visual Check
→ Fix
→ Re-test
```

需要检查的不只是“页面出现了”：

- 首屏布局；
- 文本是否被截断；
- 移动/桌面尺寸；
- Button 是否可点击；
- Form 状态；
- Loading / Empty / Error；
- Console Error；
- API Request；
- 页面跳转；
- 关键截图。

本培训后续真实项目案例会继续使用：

> **自动化测试 + Browser Visual QA**

而不是二选一。

**截图占位：TOOL-07 浏览器页面 + Console + Screenshot + 修复后结果**

---

# 9. 问题：Agent 怎么从本地跨到真实服务器？——SSH

## 9.1 SSH 本身不是“AI 能力”

SSH 是成熟的远程连接工具。

Agent 的变化在于：

> 模型可以围绕目标连续决定要执行哪些远程命令，并根据结果继续行动。

例如：

```text
目标：部署新版本并验证服务

Agent
→ ssh server
→ cd /srv/app
→ 查看当前版本
→ docker compose pull
→ docker compose up -d
→ docker ps
→ docker logs
→ curl /health
→ 发现错误
→ 查看配置
→ 修复
→ restart
→ 再验证
```

从“给你几条命令”变成：

> **观察—执行—再观察—再执行。**

---

## 9.2 远端操作一定要区分环境

至少区分：

- 本地开发环境；
- 测试环境；
- 预生产；
- 生产。

对高风险环境必须明确：

- 哪些命令允许自动执行；
- 哪些需要人工批准；
- 是否允许删除；
- 是否允许改数据库；
- 凭据如何提供；
- 如何回滚；
- 是否有维护窗口。

培训中必须持续强调：

> **Agent 自动化不取消生产变更纪律。**

---

# 10. 问题：容器启动了，就能证明部署成功吗？——Docker / Health

Docker 很适合 Agent 的一个原因，是很多操作天然结构化：

```text
image
container
port
environment
volume
log
health
```

常见闭环：

```bash
docker ps
docker inspect ...
docker logs --tail 100 ...
docker compose pull
docker compose up -d
curl /health
```

Docker 官方文档明确提供 `docker logs` 查看容器输出，也支持 Healthcheck 机制。

这使 Agent 不必只依赖“进程好像启动了”，而可以结合：

- Container State；
- Logs；
- Health；
- Real Request；

做更可靠判断。

**截图占位：TOOL-08 SSH + Docker + logs + health request**

---

# 11. 问题：Agent 操作系统一定要模拟人点界面吗？——API / Structured Tool

Agent 可以通过 API 连接：

- GitHub；
- CI/CD；
- 企业内部系统；
- 搜索服务；
- 监控；
- 数据平台；
- 自研业务系统；
- 设备管理平台；
- 模型服务。

如果系统已经有 API，一般应该优先考虑结构化调用。

例如：

```text
Create Issue
Get Metrics
Start Job
Query Device
Upload Artifact
Trigger Workflow
```

而不是打开浏览器模拟点击。

这正好为下一章铺路：

> **API 解决“系统提供什么能力”；MCP 等机制解决“如何更标准地把这些能力暴露给 Agent”；Skill 解决“怎样把能力组合成可靠工作方法”。**

**图示占位：TOOL-09 UI 操作 vs API Tool 的两条路径**

---

# 12. 问题：怎样让验证不依赖 Agent 每次“记得测试”？——CI/CD

Agent 在本地跑完测试并不代表结束。

更可靠的闭环是：

```text
Agent local test
→ commit
→ push
→ CI
→ independent runner
→ build/test/check
→ pass/fail
→ if fail, return to fix
```

GitHub Actions 官方将 Workflow 定义为仓库中的可配置自动化流程，可由事件、手动或计划触发，并由 Job / Step 执行构建、测试、部署等任务。

教学重点不是 GitHub Actions YAML 语法，而是：

> **把验证规则写进仓库，让它不依赖某次对话里的“记得测试”。**

因此 CI 是可复用工程资产，也是 Agent 可靠性基础设施。

**截图占位：TOOL-10 Commit → Actions → Failed/Passed**

---

# 13. 问题：这些工具怎样连成一个完整工程闭环？

把前面所有工具收束成一个真实模板：

```text
1. Read rules
   AGENTS.md / README / requirements

2. Inspect state
   branch / SHA / git status / environment

3. Locate
   search / grep / read relevant files

4. Plan
   decide minimal changes + verification

5. Modify
   edit files / generate code

6. Local verify
   lint / typecheck / unit test / API test

7. Runtime verify
   start service / logs / health request

8. UI verify (if needed)
   browser / Playwright / screenshot / console

9. Review changes
   git diff

10. Deliver
   commit / push / PR

11. Independent verify
   CI

12. Report
   changed files + test evidence + limitations
```

这比“写一个 Prompt 让模型生成代码”更接近真实工程。

**图示占位：TOOL-11 工程 Agent 12 步闭环**

---

# 14. 问题：Agent 都能执行了，人还负责什么？

工具越强，越不能把人的职责讲没。

推荐统一分工：

> **模型负责判断和生成，工具负责执行，自动化测试负责验证，人负责目标、约束和最终判断。**

人尤其要负责：

- 目标是否正确；
- 是否允许改这些文件；
- 是否可以访问外网；
- 是否可以执行 Docker；
- 是否可以 SSH；
- 是否可以操作生产；
- 是否允许提交/推送；
- 验收标准是什么；
- 最终结果是否接受。

Agent 适合承担：

- 搜索；
- 重复命令；
- 文件修改；
- 测试；
- 浏览器检查；
- 日志收集；
- Diff；
- 证据整理。

---

# 15. 问题：是不是给 Agent 越多工具越好？

常见误区：

> 工具越多，Agent 越强。

实际还要考虑：

- Tool Description 是否清晰；
- 参数是否容易生成正确；
- 返回结果是否过长；
- 是否存在功能重叠；
- 权限是否过大；
- 错误是否可恢复；
- 是否有验证工具；
- Tool Result 是否污染 Context。

因此工具设计的目标不是：

> “能接的都接上。”

而是：

> **给任务提供足够、明确、可验证的行动空间。**

这也是下一章 MCP / Skill 设计要继续回答的问题。

---

# 16. 问题：要让 Agent 真正工作，环境最少要准备什么？

这一段在内网培训中需要重点讲，不只是“安装教程”，而是 **Agent Runtime Engineering**。

完整案例：

`docs/cases/agent-runtime-environment-intranet.md`

环境检查脚本：

- `demos/zcode-real-world/check-agent-env.ps1`
- `demos/zcode-real-world/check-agent-env.sh`

先建立一个判断：

> **Agent Harness 提供执行能力的入口；宿主机 / WSL / 容器 / 远端服务器提供真正的 Toolchain。**

建议工程人员至少理解这些组件：

| 类别 | 典型工具 | Agent 用途 |
|---|---|---|
| 版本管理 | Git | 状态、Diff、Commit、协作 |
| 脚本 | Python | 数据、API、自动化 |
| 前端/工具链 | Node.js / npm | Web、Playwright、构建 |
| 容器 | Docker | 可复现运行与部署 |
| 网络 | curl | API/Health 验证 |
| 远程 | SSH | 服务器运维 |
| 浏览器自动化 | Playwright | UI/E2E/Visual QA |
| 编辑/Agent | CLI / IDE / Desktop / Web Agent | Harness Surface |

## 16.1 ZCode 的 Git 到底算不算“内置”

当前 ZCode 官方明确提供 Git 状态、Branch、Commit、Review 等内置工作流；但 Windows 安装文档又说明 Git Bash 只有检测到已安装时才出现，远程开发文档则明确 Git 操作运行在目标环境。

因此本培训采用更谨慎的说法：

> **ZCode 内置了 Git 工作流集成，但不要据此假设它提供一个可供所有 Terminal / Script 使用的独立 Git CLI Runtime。**

内网标准环境仍然要求：

~~~bash
git --version
~~~

通过验收。

## 16.2 Python / npm 要不要提前装

要。

对本地 Workspace：

> 安装在宿主机。

对 WSL：

> 安装在 WSL 发行版中。

对 Docker：

> 写入标准镜像。

对 SSH Remote：

> 安装在远端开发机。

尤其是内网环境，不应该依赖 Agent 现场联网执行 `pip install`、`npm install`、`apt install` 来“自举”。

## 16.3 内网环境还要多准备一层

除了 Toolchain，还要准备：

- 离线安装包；
- 内部 PyPI；
- 内部 npm Registry；
- apt/yum 内部源或基础镜像；
- Container Registry；
- Git Server；
- Internal CA；
- Proxy / NO_PROXY；
- DNS；
- 软件白名单；
- 固定版本和 Lock 文件。

因此内网 Agent 的实际基础设施更接近：

~~~text
Agent
→ Standard Runtime
→ Approved Toolchain
→ Internal Package Supply Chain
→ Internal Services
~~~

## 16.4 Remote Development 更能说明这个问题

ZCode 当前官方明确说明：

> Remote Workspace 中 File、Terminal、Git 和 Agent Runtime 都在目标环境运行。

而且官方进一步提醒：

> Sync Skill / MCP / Plugin 成功，不代表远端已经有 npx、Python dependencies 或它们依赖的 CLI。

所以：

> **同步 Agent 配置 ≠ 构建执行环境。**

这是企业内网推广时必须单独治理的两件事。

核心结论：

> **Agent 的能力上限不仅取决于模型和 Harness，也取决于它所在环境是否预先提供稳定、可复现的 Toolchain 与依赖供应链。**

---

# 17. 课堂案例：先 ZCode 闭环，再扩展到服务器与 CI

## Demo A：ZCode 工程闭环——Sensor Guard

### 目的

证明 Agent 不是只给代码，而是进入已有项目完成“读规则 → 复现 → 修改 → 验证 → Review”。

训练项目：

`demos/zcode-real-world/project/`

固定 Prompt：

> 当前仓库有一个已知失败。请先读取项目规则和现有测试，复现问题，定位原因并用最小改动修复；运行必要测试确认结果，最后检查 Git Diff，并说明修改了什么、验证了什么、还有什么没有验证。不要跳过已有测试，也不要做无关重构。

初始基线：

- 5 条单元测试；
- 其中 85.0°C 临界值测试失败；
- 修复目标应由 Agent 从 README / tests / implementation 中自行确认。

### 必须保留证据

- ZCode 读取 `AGENTS.md`；
- Terminal 第一次测试失败；
- Search / Read 定位相关代码；
- 最小 Edit；
- 第二次完整测试通过；
- Review / Git Diff；
- 当前 Execution Mode。

对应录屏：**ZCODE-R02 / TOOL-R01**

---

## Demo B：ZCode Browser 闭环——鹈鹕骑自行车

### 目的

先用一个肉眼可见的短任务说明：

> **Chat 给出代码；Agent 可以把代码写入文件、打开真实页面、观察结果并继续修改。**

复用：

`demos/pelican-bicycle/README.md`

推荐流程：

```text
同一 Prompt
→ ZCode 创建 index.html
→ Built-in Browser 打开
→ 第一次视觉检查
→ 根据实际页面继续修改
→ 再次 Browser Verify
→ Review 最终变化
```

这一段同时引出：

> **Test != Visual QA。**

对应录屏：**ZCODE-R01 / TOOL-R02**

---

## Demo C：SSH 远端部署闭环

### 目的

展示从“告诉用户命令”到“Agent 连续执行运维任务”。

### 流程

```text
SSH
→ 查看当前容器
→ 拉取/启动
→ 查看 logs
→ health check
→ 返回版本与状态
```

训练环境优先，不建议把第一次现场演示直接放到关键生产环境。

对应录屏：**TOOL-R03**

---

## Demo D：Commit → Push → CI

### 目的

说明：

> **验证规则应该离开聊天窗口，进入仓库。**

### 流程

```text
local test pass
→ commit
→ push
→ Actions
→ show workflow
→ show pass/fail
```

对应录屏：**TOOL-R04**

---

# 18. 本章截图 / 录屏清单

## 18.1 静态素材

| 编号 | 优先级 | 内容 | 状态 |
|---|---:|---|---|
| TOOL-01 | P0 | Model → Tool Request → Harness → Execute → Tool Result 总图 | ⬜ |
| TOOL-02 | P0 | Workspace：目录 + Search + Read | ⬜ |
| TOOL-03 | P0 | Terminal Tool Call + Approval / Sandbox | ⬜ |
| TOOL-04 | P0 | git status + git diff + test | ⬜ |
| TOOL-05 | P0 | 静态检查/自动测试/运行态/UI 四层验证图 | ⬜ |
| TOOL-06 | P0 | Browser Use / Playwright / Computer Use / Crawler 对比图 | ⬜ |
| TOOL-07 | P0 | Browser + Console + Screenshot + 修复对照 | ⬜ |
| TOOL-08 | P0 | SSH + Docker + logs + health | ⬜ |
| TOOL-09 | P1 | UI 自动操作 vs Structured API Tool | ⬜ |
| TOOL-10 | P0 | Commit → GitHub Actions → Pass/Fail | ⬜ |
| TOOL-11 | P0 | 12 步工程 Agent 闭环图 | ⬜ |
| ENV-01 | P0 | Model → Harness → Tool → Runtime → Toolchain 分层图 | ⬜ |
| ENV-02 | P0 | ZCode Terminal 环境检查：git/python/node/npm/curl/ssh | ⬜ |
| ENV-03 | P0 | Local / WSL / Docker / SSH 的执行环境位置对比 | ⬜ |
| ENV-04 | P0 | 公网自动安装 vs 内网内部镜像/离线包 | ⬜ |

## 18.2 录屏

| 编号 | 优先级 | 内容 | 状态 |
|---|---:|---|---|
| TOOL-R01 | P0 | Read → Edit → Test → Diff 最小闭环 | ⬜ |
| TOOL-R02 | P0 | Test Pass → Browser Visual QA → Fix | ⬜ |
| TOOL-R03 | P0 | SSH → Docker → Logs → Health Check | ⬜ |
| TOOL-R04 | P0 | Commit → Push → CI | ⬜ |
| TOOL-R05 | P1 | API Tool 与 GUI 操作完成同一任务对比 | ⬜ |
| ENV-R01 | P0 | 环境 Preflight：工具缺失 → 环境补齐 → 同任务成功 | ⬜ |
| ENV-R02 | P1 | npm/pip 公网源失败 → 内部源成功 | ⬜ |

---

# 19. 讲师节奏建议

这章不要连续讲 30 分钟概念。

建议节奏：

### 第一段：5 分钟

问题：

> 模型只能出 Token，为什么能改电脑？

展示 TOOL-01。

---

### 第二段：10 分钟

直接做 **ZCODE-R02**：

> AGENTS.md → Test Fail → Search → Edit → Test Pass → Diff

边做边解释 Project Instructions / File / Shell / Git / Verification。

---

### 第三段：8 分钟

先做 **ZCODE-R01 鹈鹕 Browser 闭环**，再从 ZCode Built-in Browser 抽象到 Browser Use / Playwright / Computer Use / Crawler 的区别。

---

### 第四段：8 分钟

SSH / Docker / API / CI。

展示 TOOL-R03 / TOOL-R04 的预录或关键截图。

---

### 最后 3 分钟

只收束三句话：

> **模型不是执行器，工具才是。**  
> **工具调用不是终点，验证才是闭环。**  
> **Agent 自动化越深入，权限、留痕和回滚越重要。**

---

# 20. 本章与下一章如何衔接

这一章解决：

> **Agent 怎样动手。**

下一章继续解决：

> **这么多外部能力，应该怎样标准化提供给 Agent，并变成可复用工作方法？**

自然过渡：

```text
Shell / File / Browser / API
          ↓
这些都是“工具能力”
          ↓
工具怎样接入 Agent？
          ↓
API / MCP / Plugin
          ↓
工具怎样组成稳定流程？
          ↓
Skill / Command / Hook
```

---

# 21. 本章最后只留下五个结论

1. **模型本身不直接操作真实世界，Harness 通过 Tool Call 把模型连接到文件、Shell、浏览器、API 和远端系统。**
2. **Shell 是通用执行入口，但 File / Git / Browser / API 等结构化工具往往更容易约束、验证和审计。**
3. **Git 的价值不只是托管代码，它为 Agent 提供状态、Diff、回退和审计边界。**
4. **Browser Use、Playwright、Computer Use、Crawler 解决的问题不同；结构化 API 和可重复自动化通常应优先。**
5. **真正的工程闭环不是“Agent 执行成功”，而是 Read → Act → Observe → Verify → Iterate → Deliver。**

---

# 22. 事实边界与参考资料

本章概念部分优先使用稳定机制；涉及具体产品行为时，以当前官方文档为准。

## ZCode 当前官方资料

- ZCode Agent：https://zcode.z.ai/en/docs/agents
- ZCode Agent Framework：https://zcode.z.ai/en/docs/agent-framework
- ADE Tools：https://zcode.z.ai/en/docs/ADE-tools
- Browser Automation：https://zcode.z.ai/en/docs/browser-use
- Safety Confirmation：https://zcode.z.ai/en/docs/safety-confirm
- Goal Mode：https://zcode.z.ai/en/docs/goal

注意：ZCode 当前官方实现会持续变化；课堂截图和具体菜单名称以录制当天版本为准。

## 其他官方资料

- Playwright Auto-waiting / Actionability  
  https://playwright.dev/docs/actionability
- Playwright Assertions  
  https://playwright.dev/docs/test-assertions
- Playwright 官方首页（Testing / CLI / MCP）  
  https://playwright.dev/
- OpenAI Computer Use  
  https://developers.openai.com/api/docs/guides/tools-computer-use
- OpenAI Codex 配置：Approval / Sandbox  
  https://developers.openai.com/docs/config-file/config-basic
- Git status  
  https://git-scm.com/docs/git-status
- Git diff  
  https://git-scm.com/docs/git-diff
- Docker logs  
  https://docs.docker.com/reference/cli/docker/container/logs/
- Docker Healthcheck / Running Containers  
  https://docs.docker.com/engine/containers/run/
- GitHub Actions Workflows  
  https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows

## 仓库内关联资料

- `docs/chapters/04-agent-common-mechanisms.md`
- `docs/references/coding-agent-comparison-2026-09.md`
- `docs/chapters/01-intranet-qwen-api.md`
- `docs/cases/model-metric-api-observability.md`
- `docs/outline/media-capture-checklist.md`

## 后续实测要求

以下内容不要仅靠讲义结论，需补真实素材：

- ZCODE-R01：ZCode 鹈鹕 Browser 闭环；
- ZCODE-R02：ZCode Sensor Guard 的 AGENTS.md / Test / Edit / Diff 完整闭环；
- TOOL-R01：真实仓库 Read/Edit/Test/Diff；
- TOOL-R02：Playwright / Browser Visual QA；
- TOOL-R03：SSH / Docker 部署；
- TOOL-R04：GitHub Actions；
- TOOL-R05：API Tool vs GUI。

如果后续实测与本章描述不一致：

> **以实测为准，修改讲义。**
