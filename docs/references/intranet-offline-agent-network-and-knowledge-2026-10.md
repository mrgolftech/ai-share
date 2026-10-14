# 内网 Agent 的联网边界与知识供给：第二讲补充证据（2026-10-14）

> 类型：培训参考资料 / 工程决策依据  
> 范围：部门内网运行的本地模型和 Agent；Codex CLI、Claude Code 的联网机制仅依据官方公开资料，不代表本部门已启用或完成实测。  
> 事实分层：官方文档 / 当前内网已知事实 / 推荐设计 / 待验证项。

## 一、核心结论

- 无法访问公网，使内部可更新、可追溯、可授权的知识源更重要；但“知识库”不能代替软件包仓库、源码托管、在线 API、搜索服务和执行工具。应建设**内部知识与工具供给体系**。
- 必须拆分：**模型 API 连接**、**Web Search/Fetch 连接**、**Shell/Git/Browser/MCP 执行环境连接**。三者可以位于不同计算位置，并有各自的网络与权限策略。
- 不联网不代表模型不能推理：模型已有参数知识、内网 API、文件和工具可使用；缺失的是**新知识更新、外部资料获取、外部依赖分发和部分托管工具**。
- Vector/RAG 是检索策略，不是唯一入口：短资料 Full Context，规范/文章全文/BM25/Hybrid，代码 Git 搜索，结构化数据 SQL/Python，最新状态调用内网 API。
- “Codex/Claude Code 自带 WebSearch”**不能推出**内网部署的任意兼容模型已经拥有该功能。托管搜索依赖原厂后端或可实际访问的另行实现。
- 绝不为了让 Agent 上网而直接打通涉密/敏感内网和互联网。只有经审批的资料才进入受控同步、镜像或隔离的交换流程。

## 二、Codex：搜索网络与命令执行网络是两条不同链路

依据 OpenAI Codex 当前基础配置文档（2026-10-14 访问）：
- 本地 Codex 的 `web_search` 支持 `cached`（当前默认：OpenAI 网页搜索缓存）、`indexed`（受索引准入控制）、`live`（实时网页）、`disabled`。
- `--search` 相当于选择 live。**cached 仍依赖可到达 OpenAI 托管搜索服务，并非在本机自动拥有离线互联网索引**。
- 本地 CLI/IDE 的 `workspace-write` 沙盒通常默认不允许命令直接访问网络；要区分命令沙盒网络与 Web Search 工具网络。示意配置：
  ```toml
  sandbox_mode = "workspace-write"
  web_search = "cached"
  [sandbox_workspace_write]
  network_access = false
  ```
- `network_access=true` 也不等于机器具备真实外网路由，更不能代替单位审批和网络隔离。
- OpenAI Agents API 则提供另一个形态：OpenAI-hosted sandbox 与 self-hosted sandbox；云端沙盒的 `network.access` 可以设置 enabled/disabled/restricted；自托管执行器在用户基础设施运行，需与云端控制平面建立连接。这与完全自主、全内网的 Agent 不是同一种架构。
- OpenAI Responses API 的 hosted `web_search` 也是由 API 提供方托管的工具；不是当前内网任意 Responses 兼容服务天然具备的工具。

官方依据：
1. Codex Config Basics（网页搜索默认及模式、Sandbox）：https://developers.openai.com/codex/config-basic （页面可能重定向至 ChatGPT Learn）
2. https://developers.openai.com/zh-Hans/docs/config-file/config-basic
3. OpenAI 安全机制：https://openai.com/index/running-codex-safely/
4. Agents API OpenAI-hosted Sandbox：https://developers.openai.com/api/docs/guides/agents-api/environments/openai-hosted
5. Agents API Self-hosted Sandbox：https://developers.openai.com/api/docs/guides/agents-api/environments/self-hosted
6. Responses API Web Search：https://developers.openai.com/api/docs/guides/tools-web-search

## 三、Claude Code：内置 WebSearch / WebFetch 与本地 Shell 访问

依据 Anthropic Claude Code 工具参考（2026-10-14 访问）：
- `WebSearch` 请求 Anthropic 的搜索后端，返回标题和 URL；若需读取页面，接着使用 `WebFetch`。WebSearch 的搜索后端**不能通过一个普通配置项替换**；要接入其他搜索服务，可增加 MCP 搜索工具。
- `WebFetch` 获取指定 URL，HTML 会转 Markdown，并可能再调用模型提取相关内容，结果可能有损；可用 `Bash + curl` 在**执行环境具有网络权限时**读取原始内容。
- `WebFetch` 对内网无点短主机名（如 `http://intranet`）有限制，官方建议对本地服务器用 Bash/curl；这不表示 Bash 自动有网络能力。
- WebFetch、WebSearch 受工具可用性、组织策略和权限规则约束。Claude Code 支持 `HTTPS_PROXY`、`HTTP_PROXY`、`NO_PROXY`，需要公司批准的网络环境和网关；**代理设置不等于绕过隔离**。
- 走 Anthropic 托管模型的 Claude Code 通常还需连接认证/模型 API；采用第三方 LLM gateway 或其他支持的提供方时，模型连接可改变，但内置搜索能否使用仍要按实际实现、权限和后端支持验证。
- Anthropic Messages API 的服务端 `web_search` 与客户端工具是不同执行位置；后者由客户端执行工具并回传结果。

官方依据：
1. Claude Code Tools Reference：https://code.claude.com/docs/en/tools-reference
2. Claude Code Enterprise Network：https://code.claude.com/docs/en/network-config
3. Claude Web Search API：https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool
4. Claude Tool Use：https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview

## 四、给本部门推荐的四层架构

```text
[需审批的公网资料/第三方代码/依赖]  ──(隔离、审核、受控导入/同步)──┐
                                                                  ↓
第一层 Source of Truth    内网制度与文控/PDM、技术文档、Git、禅道、测试记录、制品/依赖镜像
第二层 Knowledge Access   Parse/全文/BM25/向量与混合检索、元数据、版本、ACL、原文链接
第三层 Tools & Runtime    内网 API、Search/Read、SQL/Python、Git、Shell、内网 MCP、包管理镜像
第四层 Applications       Cherry Studio、Open WebUI、Agent（模型 API 连接到内网 Qwen）
```

权威资料和派生索引需分离；身份鉴权、版本有效性与许可范围必须先于模型上下文注入。对 Git/禅道/测试数据库仍以原系统为事实来源。对于最新官方 SDK/API：
- 允许受控资料交换：建立批准目录、来源、许可证/供应链检查、更新时间、责任人及 SHA256，保持增量更新。
- 严格隔离：选择**离线版本文档快照 + 内网包镜像 + 本地项目代码/测试 + 基于版本的人工导入**；不能声称具备实时外网事实。
- 内网已批准的实时业务系统优先通过 API/MCP Tool 查询，不通过滞后的文档索引冒充实时状态。

### 运行模式判断表

| 模式 | 模型调用 | 搜索/资料更新 | 主要边界 |
|---|---|---|---|
| 全内网离线 | 内网 Qwen | 内网文档、内网 Git/禅道、离线快照 | 最新公网资料无法自动获取 |
| 受控交换 | 内网 Qwen | 按策略审核导入文档、依赖及版本镜像 | 必须验证审批、来源、授权、审计 |
| 合规受控外连（仅允许时） | 内网或批准的模型服务 | 受限搜索网关/域名白名单和代理 | 外发数据、提示注入、泄漏、恶意依赖风险 |
| 公网云 Agent | 云模型 API | 厂商 Web 工具、MCP、Shell 网络 | 不适合作为内部敏感信息的默认执行环境 |

## 五、第二讲的建议教学 Demo（未实测）

统一问答：`我们部署的 Qwen 的 Responses Vision 当前实际测试状态是什么？其证据在哪？`
1. 裸模型（不提供本部门资料）：观察其能否可靠回答；
2. 引入仓库权威报告（最新 `api/qwen/reports/qwen36_api_test_report_20260930.md` 与 `api/qwen/results/20260930_095033/evidence.md`）：比较事实、版本、引用；
3. 内网 Agent：分别尝试“查公网最新资料”“查内网知识库”“读 Git 实测证据”“访问内网 API（若具备授权）”，记录成功、失败和执行位置。对于联网失败要显示网络原因，不把“无实时公网结果”伪装成“资料里没有”。

追加演示“官方文档更新”场景：使用经过审批的离线版本文档快照，让学员观察引用日期与版本标识。不可声称此快照代表当日实时官网。

### 尚需执行的核验

- 内网出口策略、DNS、代理/镜像可用性（由网络和安全管理人员确认）；
- Agent 运行平台与模型 API/工具 API 的实际可达性；
- `WebSearch` / `WebFetch` / `curl` / `git ls-remote` 在相同执行环境下的差异（不得主动探测未获授权的公网地址）；
- 本地 embedding/rerank 能否调用、离线快照如何更新、权限是否在检索前生效；
- 内网 Qwen 的 Anthropic/Responses **协议兼容**不等于支持官方 hosted web tools，需单项实测。

> 培训结论：**联网是外部知识和服务的访问渠道；知识治理解决准确性、版本、权限、可复用性。缺外网会增加本地知识供给压力，但不应把“联网缺失”简单等价为“只需一套向量库”。**
