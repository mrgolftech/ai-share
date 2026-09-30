# 案例：内网 Agent 运行环境——有 Terminal，不等于有工具链

> 状态：可用于培训 / 待内网标准环境实测  
> 日期：2026-09-30  
> 关联讲义：docs/chapters/05-agent-tools-real-world.md

---

# 1. 先回答一个容易被忽略的问题

安装 ZCode、Codex、OpenCode 等 Agent 以后：

> **是不是就自动拥有 Git、Python、npm、Docker、编译器和所有项目依赖？**

不是。

需要明确区分：

~~~text
Model
  ↓
Agent Harness
  ↓
Tool / Terminal
  ↓
Execution Environment
  ↓
Git / Python / Node / npm / Docker / Compiler
  ↓
Project Dependencies
  ↓
Network / Package Registry / Internal Services
~~~

Agent Harness 提供的是行动通道；真正执行命令的是当前 Workspace 所在的本机、WSL、容器或远端服务器。

---

# 2. ZCode 当前事实：Git 集成 ≠ 明确承诺内置 Git CLI

ZCode 当前官方明确提供 Git 状态、Branch、Commit、Review、Changed Files 等 Git 工作流能力，FAQ 也使用“built-in Git commit”描述产品能力。

但当前安装文档同时说明：

- Windows Terminal 可选 Auto、CMD、Git Bash；
- Git Bash 只有检测到已安装时才出现；
- Auto 优先 Git Bash，找不到则回退到 CMD。

远程开发文档又明确说明：

> 连接 WSL / SSH / Docker 后，文件、Terminal、Git 操作和 Agent 都运行在目标环境。

因此，培训和内网部署都不应把：

> “ZCode 有 Git UI”

推导成：

> “ZCode 一定自带可供 Terminal 使用的完整 Git CLI”。

更稳妥的工程要求是把下面命令作为环境验收项：

~~~bash
git --version
~~~

---

# 3. Python / Node / npm 更应视为外部工具链

ZCode 官方 Terminal 用来运行 build、test、development server、logs 等命令，本质上是调用当前执行环境里的程序。

ZCode 官方 Hook 文档还明确举例：某 Hook 依赖 node 存在于系统 PATH。

因此培训统一表述：

> **Agent 有 Terminal，只说明它有“执行入口”；具体 Toolchain 是否存在，必须由执行环境提供。**

不要假设：

- ZCode 自带项目可用的 Python；
- ZCode 自带项目可用的 Node.js；
- 桌面应用内部可能使用某种 Runtime，就等价于 Terminal 中存在 node；
- npm / pip 一定能够联网下载依赖。

---

# 4. Local / WSL / Docker / SSH：工具链到底装在哪里

## 本地 Workspace

~~~text
ZCode Desktop
→ Local Workspace
→ Local Shell / PATH
→ Local Git / Python / Node / npm
~~~

工具链应安装在本机。

## WSL Workspace

~~~text
ZCode Desktop
→ WSL
→ Linux Shell / PATH
→ WSL 内 Git / Python / Node
~~~

Windows 宿主机装了 Python，不代表 WSL 中有 Python。

## Docker Workspace

~~~text
ZCode Desktop
→ Running Container
→ Container filesystem
→ Container toolchain
~~~

ZCode 当前官方明确要求目标容器已经启动，并且容器内已经具备项目需要的 shell、Git、Node.js 或其他工具链。

## SSH Remote Workspace

~~~text
ZCode Desktop
→ SSH Host
→ Remote Shell / PATH
→ Remote Git / Python / Node / Docker
~~~

本机装了 npm，不代表远端有 npm。

---

# 5. 为什么内网环境问题会被放大

公网环境中，Agent 遇到缺少工具时可能尝试：

~~~text
pip install ...
npm install ...
apt install ...
curl ...
git clone ...
~~~

但在受限内网中，这些动作可能全部失败：

- 无 Internet；
- 无 GitHub；
- 无 PyPI；
- 无 npm registry；
- 无 apt/yum 外网源；
- HTTPS 被内网网关替换证书；
- Proxy / DNS 不同；
- 软件安装需要管理员权限；
- 安全策略禁止运行未知安装脚本。

因此：

> **不能把“环境自举”默认交给 Agent。**

正确思路是：

> **先由人和平台团队构建标准 Agent Execution Environment，再让 Agent 在可控环境里工作。**

---

# 6. 建议的部门通用 Agent 工作站基线

> 这是培训建议的通用基线，不是所有项目必须安装全部工具。

## P0：基础执行层

| 能力 | 建议组件 | 为什么 |
|---|---|---|
| Shell | PowerShell / CMD / Git Bash；Linux Bash | Agent 命令执行入口 |
| Git | Git CLI | Repo / Diff / Commit / Branch |
| Python | Python 3 + pip + venv | API、数据、脚本、自动化 |
| Node | Node.js + npm | Web、Playwright、部分 MCP / Hook |
| HTTP | curl | API / Health Check |
| SSH | OpenSSH Client（条件项） | CLI 远端操作；ZCode Remote Development 自身使用内置 SSH client |
| CA | 部门内部根证书 | HTTPS / Internal Registry |
| PATH | 标准化 PATH | 让 Agent 找到工具 |

## 6.1 Python、Node.js、系统 CLI 怎么分工

部门标准环境建议三者共存，而不是用一个替掉另外两个。

| 层 | 主要用途 | 典型工具 |
|---|---|---|
| 系统/专用 CLI | 最直接、确定性执行 | git、curl、rg、docker、ssh、编译器 |
| Python | API、数据、文档、脚本、复杂编排 | pytest、pandas、Playwright Python |
| Node.js/npm | Web、JS/TS、浏览器 Agent 工具链 | Playwright Test/CLI/MCP、Puppeteer、前端构建 |

推荐选择顺序：

1. 项目已经有现成命令/脚本：直接复用。
2. 有成熟专用 CLI：优先 CLI。
3. 需要复杂编排、数据处理或状态机：Python。
4. Web / JS / Browser tooling：优先考虑 Node.js。
5. 最后才直接实现底层协议。

这避免两个常见误区：

- “Python 什么都能做，所以只装 Python”；
- “Web Agent 都必须 Node.js”。

Playwright 的核心浏览器自动化能力同时支持 Python 与 JavaScript/TypeScript；但当前 Playwright CLI / MCP 与 Puppeteer 等 Agent/浏览器工具链对 Node.js 更直接。

---

## P1：工程增强层

| 能力 | 建议组件 |
|---|---|
| Container | Docker / Podman（按部门策略） |
| Linux 环境 | WSL2 或受控 Linux VM |
| Browser Test | Chromium / Playwright browsers |
| Python env | uv / pip-tools 等，部门选定一种 |
| Node package manager | npm；项目需要时再统一 pnpm/yarn |
| Build | CMake / Ninja / GCC / MSVC / JDK 等按项目 Profile 预置 |

## 项目 Profile

不要所有机器都装所有工具，可以定义：

~~~text
python-api
web-node
embedded-c
docker-service
document-processing
data-analysis
~~~

每个 Profile 指定工具、版本、环境变量、内部依赖源和验收脚本。

---

# 7. 内网真正要建设的是软件供应链

## 7.1 离线安装包

提前保存并审批：

- Git；
- Python；
- Node.js；
- Docker / WSL 相关组件；
- 浏览器；
- ZCode；
- 必要编辑器和 CLI。

## 7.2 Python 包来源

优先建设内部 PyPI Mirror，或准备经过审核的 wheelhouse。

项目保留 requirements.txt、pyproject.toml 和 Lock 文件，避免 Agent 临时选择未知依赖。

## 7.3 npm 包来源

优先建设内部 npm Registry / Proxy，或准备经过审核的离线缓存。

项目保留 package.json 和 Lock 文件。

## 7.4 OS 软件源

Linux / WSL 应准备内部 apt/yum 镜像或标准基础镜像。

---

# 8. Proxy / Certificate / DNS 是 Agent 环境的一部分

ZCode 当前官方安装文档特别说明：

- ZCode 的 HTTP Proxy 需要在 Settings 中显式设置；
- 空白并不代表继承系统 HTTP_PROXY；
- 配置后会作用于模型请求、MCP Server、Agent 运行的命令行工具和应用请求；
- 企业 HTTPS 解密网关可配置 PEM 根证书；
- No Proxy 应加入 localhost 和内网地址。

内网标准环境建议统一管理：

~~~text
HTTP/HTTPS Proxy
NO_PROXY
Internal DNS
Internal CA
Model Base URL
Git Server
PyPI Mirror
npm Registry
Container Registry
~~~

---

## 8.1 一个非常关键的“半离线”能力

ZCode 当前 Remote Development 文档明确提供两种首次远端 Runtime 准备方式：

- Download on remote server：远端自己访问 ZCode CDN；
- Download locally then upload：桌面端下载组件，再通过 SFTP 上传到远端的 ~/.zcode/server。

因此：

> **远端开发机本身可以不访问公网。**

这对“内网开发服务器”很有价值。

但还需要进一步区分：

### 远端无公网，桌面端可访问外网

当前官方的 “Download locally then upload” 可以工作。

### 桌面端和远端都完全隔离公网

当前官方文档没有给出一个明确的、完全 air-gapped 的远端 Runtime 离线包流程。

因此在真正的全隔离内网部署前，需要单独验证：

- ZCode Desktop 如何离线安装；
- 首次 Remote Agent Runtime 如何预置；
- Plugin / Marketplace 如何本地分发；
- 模型 Endpoint 是否完全走内网；
- 更新机制是否能关闭或转为人工离线更新。

不要在培训中把“远端无需公网”直接说成：

> “ZCode 支持完全离线部署。”

这是两个不同结论。

---

# 9. Remote Workspace 还要注意配置同步

ZCode 当前官方明确：

- 本地 Skills / MCP / Plugins 不会自动跟随远程 Workspace；
- SSH / WSL 下需要显式 Sync；
- 即使配置同步成功，也不代表远端依赖已经满足；
- 官方特别提醒：ZCode 不会检查远端是否有 npx、正确的 Python dependencies 或其他命令行依赖。

这对内网尤其关键：

> **同步“Agent 配置”与准备“执行环境”是两件事。**

---

# 10. 训练前先做 Environment Preflight

不要一上来就让 Agent 修 Bug。

先检查：

~~~text
git --version
python --version
python -m pip --version
node --version
npm --version
curl --version
ssh -V
docker --version   # 项目需要时
~~~

再检查：

- Git Identity；
- PATH；
- Python venv；
- npm registry；
- pip index；
- CA / Proxy；
- 项目依赖。

仓库提供：

- demos/zcode-real-world/check-agent-env.ps1
- demos/zcode-real-world/check-agent-env.sh

---

# 11. 内网 Agent 推荐环境形态

从“每个人手工装一堆软件”逐步走向：

~~~text
Agent Client
    ↓
Standard Workspace Runtime
    ├─ Approved Git
    ├─ Approved Python
    ├─ Approved Node/npm
    ├─ Approved CLI
    ├─ Internal CA
    ├─ Internal Package Mirrors
    └─ Project Profiles
~~~

可选实现：

1. 标准 Windows 开发机镜像；
2. WSL 标准发行版；
3. 标准 Docker Dev Container；
4. 内部 Linux 开发服务器；
5. 虚拟开发桌面。

最重要的是：

> **让 Agent 的运行环境可预测、可复现、可审计。**

---

# 12. 环境本身也应该成为可复用资产

不要只靠 Wiki 写一句：

> “请安装 Python 和 Node。”

应该沉淀成：

~~~text
environment/
├── versions.md
├── installers/
├── check-agent-env.ps1
├── check-agent-env.sh
├── pip.conf
├── npmrc
├── certificates/
├── Dockerfile / devcontainer
└── README.md
~~~

能代码化的尽量代码化：

- 环境检查；
- 镜像构建；
- Dependency Lock；
- Package Mirror；
- CI 复用。

最终形成：

> **Environment as Code / Environment as Asset。**

---

# 13. 课堂 Demo

## Demo ENV-A：有 Terminal，但 Python 不存在

在隔离环境中模拟：

~~~text
Agent → python ...
→ command not found
~~~

问：

> **是模型不够聪明，还是环境缺能力？**

结论：

> Harness Capability ≠ Runtime Capability。

## Demo ENV-B：环境准备后同一任务成功

补齐 Python / PATH / Dependencies 后，用同一 Prompt 再跑。

结论：

> **很多所谓 Agent 失败，其实是 Runtime / Dependency 问题。**

## Demo ENV-C：公网与内网差异

~~~text
公网：npm install → public registry
内网：npm install → timeout
配置内部 registry → success
~~~

引出：

> **企业 Agent 平台建设必须包含软件供应链和依赖管理。**

---

# 14. 关键结论

1. **Agent Harness 提供“行动通道”，Execution Environment 提供“真正可执行的工具”。**
2. **ZCode 有内置 Git 工作流集成，但内网部署仍应显式安装并验证 Git CLI，不应假设桌面包提供完整 Git Runtime。**
3. **Python、Node/npm、Docker、编译器等应由宿主机、WSL、容器或远端环境提前提供。**
4. **公网 Agent 可以尝试临时下载依赖，内网 Agent 通常不能，因此 Environment Bootstrap 必须前置。**
5. **内网建设要同时解决安装包、版本、PATH、CA、Proxy、DNS、PyPI/npm/Container Registry 和项目依赖。**
6. **环境本身也应该成为版本化、可检查、可复用的工程资产。**

---

# 15. 官方依据

- ZCode Install: https://zcode.z.ai/en/docs/install
- ZCode ADE Tools: https://zcode.z.ai/en/docs/ADE-tools
- ZCode Remote Development: https://zcode.z.ai/en/docs/remote-development
- ZCode FAQ: https://zcode.z.ai/en/docs/qa
- ZCode Hooks: https://zcode.z.ai/en/docs/hooks
