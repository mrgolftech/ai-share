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

## 4.3 Python、Node.js 还是系统 CLI？

先纠正术语：

> **真正应该比较的是 Python 与 Node.js；npm 是 Node.js 的包管理器，角色更接近 Python 的 pip。**

Agent 环境不应该二选一地只留 Python 或 Node.js。

更合理的工具选择规则是：

~~~text
已经有成熟、稳定、可审计的专用 CLI？
        ↓ Yes
优先直接调用 CLI
        ↓ No / 需要复杂逻辑
Python / Node.js 编排
        ↓
需要特殊协议能力时
直接 API / SDK / CDP
~~~

### 为什么系统 CLI 仍然重要

虽然 Python 能：

- 调进程；
- 操作文件；
- 发 HTTP；
- 解析 JSON；
- 建立 SSH；
- 调 Docker API；

但如果任务已经有成熟 CLI，通常没必要让 Agent 重新实现一层。

例如：

~~~text
Git 状态       → git status / git diff
HTTP 探测      → curl
文本搜索       → rg / grep
容器状态       → docker ps / docker logs
远端命令       → ssh
文件打包       → tar / zip
进程/端口      → 系统原生命令
~~~

原因是：

- CLI 已经经过大量工程验证；
- 输入输出明确；
- Agent 调用成本低；
- 容易复现；
- 容易人工复核；
- 通常能复用现有配置、认证、Context。

所以：

> **Python 不是替代所有 CLI 的“万能命令”，而是更适合把多个步骤组合成稳定程序。**

### Python 更擅长什么

优先 Python 的典型情况：

- API 测试和数据处理；
- CSV / JSON / Excel / 文档处理；
- 统计分析、机器学习；
- 批量文件处理；
- 复杂条件、重试、状态机；
- 调用多个 CLI / API 后汇总结果；
- 自定义测试脚本；
- 需要将临时 Agent 操作沉淀成可维护程序。

可以把它理解成：

> **Python 更像通用自动化和数据处理胶水。**

### Node.js 更擅长什么

优先 Node.js / TypeScript 的典型情况：

- 前端项目本身就是 JS / TS；
- npm 生态依赖；
- Web 构建工具链；
- Playwright Test；
- Playwright CLI / Playwright MCP；
- Puppeteer；
- 与浏览器、DOM、Web 前端代码强耦合的自动化；
- 现成 MCP / Agent 工具本身是 Node 包。

Playwright 当前官方同时支持 JavaScript/TypeScript 和 Python，核心浏览器自动化能力两边都有；但 Playwright 面向 Coding Agent 的 `playwright-cli` 当前要求 Node.js 20+，Playwright MCP 也直接通过 `npx` 使用。

因此：

> **“浏览器自动化必须 Node”不成立，但当前 Agent 浏览器工具链中 Node.js 往往更方便。**

### CDP 应该用哪一个

Chrome DevTools Protocol 本身是语言无关的 JSON 协议。

Python 和 Node.js 都可以：

~~~text
connect CDP
→ DOM
→ Network
→ Runtime
→ Performance
→ Debugger
~~~

Playwright Python 官方提供 `CDPSession` 和 `connect_over_cdp()`；Node 端 Playwright 同样支持，而 Puppeteer 本身就是 Node.js 浏览器自动化库，并以 CDP 作为 Chrome 自动化的重要底层协议。

因此按任务选：

| 场景 | 优先选择 |
|---|---|
| 一次性查看页面/点击/截图，Agent 已有 Browser Tool | Agent Browser Tool |
| Coding Agent 做轻量浏览器自动化 | Playwright CLI（Node） |
| 需要结构化长期 Browser Agent | Playwright MCP / Browser Tool |
| JS/TS Web 项目 E2E | Node.js + Playwright Test |
| Python API/数据项目顺便做浏览器验证 | Python + Playwright |
| 深入 Chrome 专有 CDP / DevTools 自动化 | Node + Puppeteer 或任一成熟 CDP client |
| 只需 HTTP，不需要渲染页面 | curl / HTTP client，不要启动浏览器 |

### 一个更重要的原则：优先沿用项目原生技术栈

如果仓库本来是：

~~~text
Python Project
→ 优先 pytest / Python scripts

TypeScript Project
→ 优先 npm scripts / Playwright Test

C/C++ Project
→ 优先 CMake / compiler / native tests
~~~

不要为了“Agent 喜欢 Python”给一个 TypeScript 项目额外造一套 Python 自动化层。

一句话：

> **Agent 最好的工具不是它“理论上能用”的工具，而是项目已经验证、团队已经维护、结果最容易复现的工具。**

**图示占位：ENV-05｜Shell / CLI vs Python vs Node.js 决策树**

---

## 4.4 Shell 也带来最大的风险面之一

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

### 7.1.1 内置浏览器、Browser Use 与宿主机 Chrome 是三件事

这一层必须拆开讲：

~~~text
内置浏览器
= Agent 产品内部提供的 Browser Surface / Browser Runtime

Browser Use
= Agent 驱动网页的能力层

宿主机 Chrome
= 用户平时使用的外部浏览器实例
~~~

三者不是同一个概念。

#### ZCode 当前实现

ZCode 当前官方说明：

- 桌面端有独立 Built-in Browser Panel；
- Agent 对它的控制能力来自官方 **Browser Use plugin**；
- Agent 可以打开 URL、点击、填表、滚动、截图，并根据页面当前状态继续执行；
- Built-in Browser 有自己的 Session State，不与日常 Chrome 持续共享；
- 当前可以从 Chrome 一次性导入 cookies / local storage（Windows 暂不支持）；
- Agent 默认只操作自己打开的 tab。

因此更准确的关系是：

~~~text
ZCode Agent
  ↓
Browser Use plugin
  ↓
ZCode Built-in Browser
  ↓
Web page
~~~

对于普通本地前端验证、公开网页访问、表单检查：

> **已经可以直接使用 ZCode 内置浏览器，不需要再去控制宿主机 Chrome。**

只有当任务依赖用户真实 Chrome Profile、已有登录态、浏览器扩展或某个已经打开的外部浏览器上下文时，才需要考虑把宿主机浏览器纳入任务。

ZCode 当前官方文档没有公开说明 Browser Use plugin 内部具体是通过 Playwright、CDP 还是其他浏览器控制实现完成，因此培训中不应把实现细节猜成某一种技术。

#### Codex / ChatGPT Desktop 当前实现

当前 OpenAI 官方将以下能力明确区分：

~~~text
In-app Browser
= ChatGPT / Codex Desktop 内置浏览器

Browser Use
= Codex 操作网页的能力
  ├─ 可以操作 In-app Browser
  └─ 也可以通过 Codex Chrome extension 使用宿主机 Chrome

Computer Use
= 操作 Windows / macOS 桌面应用
~~~

In-app Browser 使用自己的 Browser State，不共享用户日常 Chrome Profile。

因此：

> **如果只是让 Codex 打开网站、测试本地页面、浏览公共网页，直接使用 In-app Browser 即可。**

如果任务需要：

- 已登录的 Chrome Session；
- 用户当前打开的 Chrome tabs；
- Chrome Profile；
- Chrome extensions；

才切换到 **Codex Chrome extension**。

另外，Codex Developer Mode 当前可以给 Browser Use / In-app Browser 提供更深的 CDP 访问，用于：

- Console；
- Network；
- Page State；
- JavaScript Performance；

但这属于更深层调试权限，并不是普通 Browser Use 的前提。

#### 与 Computer Use 的关系

如果任务仍然发生在网页内部：

~~~text
URL
DOM
表单
按钮
网页交互
~~~

优先 Browser Use / Browser Tool。

如果任务已经跨出网页，例如：

~~~text
Windows 文件对话框
桌面软件
系统设置
原生 GUI
其他没有 Browser DOM 的应用
~~~

才进入 Computer Use。

所以不要理解成：

> “内置浏览器只是显示页面，真正操作还得靠 Computer Use。”

更准确的是：

> **Browser Use 已经负责网页内部交互；Computer Use 是网页之外的更通用 GUI 执行层。**

**图示占位：TOOL-06A｜Built-in Browser / Browser Use / Host Chrome / Computer Use 分层图**

### 7.1.2 Agent 操作宿主机浏览器时，到底谁在发 CDP 命令

需要把“浏览器能力”继续拆成几层：

~~~text
Agent
  ↓
Harness / Browser Tool
  ↓
控制客户端
  ├─ 产品内置 Browser Use
  ├─ Playwright CLI
  ├─ Playwright MCP
  ├─ Playwright Library
  ├─ Chrome DevTools MCP
  ├─ Browser Extension
  └─ 自定义 CDP Client
  ↓
Browser
  ├─ Agent Built-in Browser
  └─ Host Chrome / Edge
~~~

CDP 本身不是 Python 或 Node.js 程序，而是 Chromium 暴露的一套调试/控制协议。Chrome 可以通过 Remote Debugging 暴露 WebSocket endpoint；客户端通过该 endpoint 发送 CDP 命令和接收事件。

因此：

> **Agent 使用 CDP 时，不一定“现场写 Python/Node 代码”。**

可能有四种情况：

1. Harness 已经内置浏览器工具，Agent 只调用 Browser Tool；
2. Agent 通过 Playwright CLI / MCP，由 Playwright 代替它和浏览器通信；
3. Agent 通过 Chrome DevTools MCP，由 MCP Server 代替它发 CDP；
4. 没有现成工具时，Agent 才自己写 Python / Node.js 代码，通过 Playwright、Puppeteer 或 WebSocket Client 发 CDP。

所以更准确的链路是：

~~~text
Model
→ Tool Call / Shell Command
→ Browser Automation Client
→ CDP / Browser Protocol
→ Chrome
~~~

而不是：

~~~text
Model
→ 必须自己生成 Python
→ CDP
~~~

### 7.1.3 操作宿主机已有 Chrome，目前常见三种接入方式

#### 方式 A：浏览器扩展

适合：

- 复用当前 Chrome Profile；
- 已登录 Session；
- SSO / 2FA；
- 已打开 Tab；
- 浏览器扩展。

当前例子：

- Codex Chrome extension；
- Playwright MCP Extension mode。

这类方案优势是：

> **直接进入用户已经在用的浏览器上下文。**

#### 方式 B：Remote Debugging / CDP

Chrome/Chromium 自带 CDP，不需要单独安装“CDP”。

但必须：

- 在 Chrome 中启用 Remote Debugging；或
- 以 `--remote-debugging-port` 启动；
- 再提供一个 CDP Client 连接。

Chrome 官方当前还支持通过 `chrome://inspect/#remote-debugging` 显式允许远程调试连接。

典型链路：

~~~text
Agent
→ Playwright / Chrome DevTools MCP / Puppeteer
→ CDP endpoint
→ Existing Chrome
~~~

所以：

> **CDP 协议不需要安装，但“说 CDP 的客户端”仍然需要。**

#### 方式 C：Playwright 自己启动浏览器

最适合：

- E2E；
- 回归测试；
- 隔离环境；
- 不想污染用户日常浏览器状态。

典型链路：

~~~text
Agent
→ Playwright
→ Dedicated Chromium / Chrome / Firefox / WebKit
~~~

此时通常不需要操作用户正在使用的 Chrome。

### 7.1.4 Playwright 到底要不要安装

要，除非当前 Agent 产品已经内置等价浏览器能力，你根本不需要自己搭 Playwright。

当前 Playwright 有三种常见 Agent 接入方式：

| 方式 | 环境要求 | Agent 怎样用 |
|---|---|---|
| Playwright CLI | Node.js 20+ | Agent 直接执行简洁 CLI 命令 |
| Playwright MCP | Node.js 20+ + MCP Client | Agent 调 `browser_navigate` / `browser_click` 等工具 |
| Playwright Library | Node.js / Python / Java / .NET | Agent 写代码调用 API |

当前官方把 Playwright CLI 定位为 coding agents 的 token-efficient browser automation；MCP 更适合需要持续浏览器状态和结构化工具调用的 Agent loop。

因此，对通用 Coding Agent：

> **如果已经有 Node.js，Playwright CLI 是当前非常自然的浏览器自动化入口。**

如果是：

- 长时间探索；
- 希望 Browser Tool 直接出现在 Agent 工具列表；
- 多轮保持 Session；

可以优先考虑 Playwright MCP。

### 7.1.5 没有 Node.js 时怎么办

不是“Browser Automation 就做不了了”。

至少有三条路：

#### 路径 1：Agent 已自带 Browser Use

例如 ZCode Built-in Browser、Codex In-app Browser：

> 不需要额外安装 Playwright，也不要求你自己写 Python。

#### 路径 2：Python + Playwright

安装：

~~~text
pip install playwright
playwright install
~~~

然后 Agent 可以生成和执行 Python 自动化脚本。

如果只是连接已经存在的 Chromium CDP endpoint，而不是让 Playwright 启动自己的 Browser，核心仍然是安装 Python Playwright Library；是否还需要下载 Playwright Browser binaries 取决于是否需要 Playwright 自己启动浏览器。

#### 路径 3：直接使用其他 Browser Tool / MCP

例如：

- 产品自带 Browser Tool；
- Chrome DevTools MCP；
- 其他可用 Browser MCP。

因此：

> **Node.js 不是浏览器自动化的理论前提；但当前 Playwright CLI/MCP 生态明确依赖 Node.js 20+，所以完整 Agent 工作站仍然很值得预装 Node.js。**

### 7.1.7 Browser Use 和 Computer Use 对模型能力的要求

Browser Use 和 Computer Use 对模型的要求并不相同，关键取决于 Harness 给模型的“观察”是什么。

#### Browser Use：不一定需要视觉

如果 Browser Tool 返回的是：

~~~text
heading "Settings"
button "Save" [ref=e12]
textbox "Name" [ref=e15]
~~~

这类 DOM / Accessibility Snapshot，模型主要需要：

- 文字理解；
- 页面语义理解；
- Tool Calling；
- 根据新状态连续决策；
- Context / State Management。

此时并不要求模型必须能看图片。

Playwright MCP 当前默认就是 accessibility snapshot 模式，并明确说明普通交互不需要 vision model。

所以：

> **结构化 Browser Use = 可以由纯文本模型完成。**

但如果网页包含：

- Canvas；
- WebGL；
- 地图；
- 图表；
- 图像编辑器；
- 没有 ARIA/Accessibility 信息的自定义控件；
- 需要判断页面布局、颜色、遮挡、视觉质量；

就需要加入 Screenshot / Vision。

Playwright MCP 当前也把这部分单独定义为 Vision Mode：模型先看 Screenshot，再基于坐标点击、拖拽或滚轮。

因此更准确地说：

~~~text
Browser Use
  ├─ Structured mode
  │    DOM / Accessibility Snapshot
  │    → Vision 非必需
  │
  └─ Vision mode
       Screenshot / coordinates
       → Vision 必需
~~~

#### Computer Use：通常需要视觉 + 空间定位

典型 Computer Use 的 Observation 是：

~~~text
Screenshot
→ Model 看当前桌面
→ 判断哪个区域是目标
→ 输出 x/y 坐标或鼠标键盘动作
→ Environment 执行
→ 返回新 Screenshot
~~~

因此模型不仅要“看懂图片”，还要具备：

- GUI 元素识别；
- 空间关系理解；
- 坐标定位；
- 点击 / 拖拽 / 滚动规划；
- 根据截图变化判断动作是否成功；
- 多步任务规划；
- 错误恢复。

OpenAI 当前 Computer Use 官方流程就是：

~~~text
Screenshot / tool result
→ model decides
→ mouse / keyboard / code action
→ environment executes
→ new screenshot
→ continue
~~~

而 OpenAI Vision 文档也明确把 computer use 列为需要高保真、坐标敏感视觉输入的场景。

所以可以把 Computer Use 的能力要求概括成：

> **Vision + Spatial Grounding + Tool/Action Calling + Planning + Verification。**

#### 但 Computer Use 也不一定“所有信息都只能靠像素”

现代 Computer Use 可以把部分工作转成代码：

- Playwright 操作 Browser；
- PyAutoGUI 操作 Desktop；
- Accessibility API；
- DOM；
- OS automation API。

此时模型可以通过代码获得更多结构化信息，降低“纯视觉点坐标”的负担。

但是，只要任务涉及：

- 桌面 App；
- 视觉布局；
- 无结构化 API 的 GUI；
- 原生对话框；
- Canvas；
- 图像内容；

视觉能力仍然是核心能力。

#### 模型能力要求对比

| 能力 | Structured Browser Use | Vision Browser Use | Computer Use |
|---|---:|---:|---:|
| 文本/语义理解 | 必需 | 必需 | 必需 |
| Tool Calling | 必需 | 必需 | 必需 |
| 多步规划 | 重要 | 重要 | 很重要 |
| 视觉理解 | 非必需 | 必需 | 通常必需 |
| 空间定位 / 坐标 Grounding | 非必需 | 重要 | 核心 |
| DOM / Accessibility 理解 | 核心 | 可选 | 可选 |
| Screenshot 理解 | 可选 | 核心 | 核心 |
| 错误恢复 | 重要 | 很重要 | 很重要 |

一句话：

> **Browser Use 可以把网页先结构化再给模型；Computer Use 往往只能把“屏幕”给模型，因此更依赖视觉和空间推理。**

**图示占位：TOOL-06D｜Structured Browser Use vs Vision Browser Use vs Computer Use 模型能力要求**

---

### 7.1.6 课堂推荐的选择顺序

~~~text
Agent 已有可靠 Built-in Browser？
        ↓ Yes
直接 Browser Use
        ↓ No

需要用户现有 Chrome 登录态？
        ↓ Yes
Chrome Extension / Existing Browser Connection
        ↓ No

是 Coding Agent 临时做页面验证？
        ↓
Playwright CLI

是长期、结构化 Browser Agent？
        ↓
Playwright MCP

是 Python 项目并已有 Python Runtime？
        ↓
Python Playwright

需要 Chrome 独有的底层 Network / Runtime / Performance？
        ↓
CDP / Chrome DevTools MCP
~~~

核心原则：

> **优先高层、稳定、可验证的 Browser Tool；只有需要更底层浏览器内部状态时才下沉到 CDP。**

**图示占位：TOOL-06B｜Browser Tool → Playwright CLI/MCP/Library → CDP → Host Chrome 技术栈**




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

### Playwright 不是“CDP 的简单封装”

一个常见误解是：

> Playwright = 把 Chrome DevTools Protocol 再包一层。

更准确的关系是：

~~~text
Chrome / Chromium
  ├─ CDP：Chrome 自己提供的底层调试/控制协议
  └─ Playwright：更高层的浏览器自动化框架
       ├─ Locator / Auto-wait
       ├─ BrowserContext
       ├─ Assertions / Test Runner
       ├─ Trace / Screenshot / Download
       ├─ Chromium
       ├─ Firefox
       └─ WebKit
~~~

CDP 是 Chromium/Chrome 的底层协议，按 DOM、Network、Runtime、Debugger、Performance 等 domain 暴露命令和事件。

Playwright 则提供更稳定、更面向任务的自动化 API，并支持 Chromium、Firefox、WebKit。Playwright 在需要时也允许直接创建 CDP Session，或者通过 `connectOverCDP()` 接入一个已经运行的 Chromium。

Playwright 官方明确指出：

> 通过 CDP 连接现有 Chromium 的方式，能力保真度低于 Playwright 自己的原生连接协议。

因此：

- **普通 Web 自动化 / E2E / Agent Browser：优先 Playwright**
- **需要 Chrome 特有的 Network / Performance / Debugger / Runtime 底层信息：再下沉到 CDP**
- **需要控制已经启动、只暴露 CDP 的 Chrome / Edge / WebView2 / Electron：CDP 很有价值**

一句话：

> **CDP 更像“浏览器底层控制总线”，Playwright 更像“面向自动化任务的浏览器 SDK / Harness”。**



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

## 16.5 内网还要区分“远端无公网”和“完全隔离公网”

ZCode 当前 Remote Development 支持：

~~~text
Desktop 下载 Remote Runtime
→ SFTP 上传到远端
→ 远端不需要访问公网
~~~

所以对于：

> **远端开发服务器无法上公网，但桌面端可以下载所需资源**

这一类场景，官方已有明确路径。

但如果：

> **桌面端与远端都处于完全隔离公网环境**

当前官方文档没有明确给出完整 air-gapped Remote Runtime 预置流程。

因此正式内网部署前必须专项验证：

- Desktop Installer 是否能完全离线；
- Remote Runtime 是否可以预下载并人工导入；
- Plugin / MCP 依赖如何本地分发；
- 软件升级如何离线管理；
- 模型、Git、Package Registry 是否全部可走内网。

不要把“远端无需公网”误讲成“整套 ZCode 已确认支持全离线部署”。

另外，ZCode Remote Development 自身使用内置 SSH client；系统 `ssh` CLI 对 ZCode 连接不是绝对前提，但对通用 CLI 运维工作仍然有价值，因此本培训把 OpenSSH Client 定义为条件项。

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
