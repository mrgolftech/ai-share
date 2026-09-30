# ZCode：API → MCP → Skill → Plugin 连续案例实施方案

> 状态：设计完成，待实现与实测  
> 日期：2026-09-30  
> 对应讲义：`docs/chapters/06-api-mcp-skill-plugin-command-hook.md`  
> 复用 Demo：`demos/agent-tool-integration/README.md`

---

# 1. 为什么模块四继续用 ZCode

模块三刚用 ZCode 看完：

```text
Workspace
→ File
→ Terminal
→ Browser
→ Test
→ Review
```

模块四如果立即换另一个 Agent，学员容易把：

> “API / MCP / Skill 的差异”

误解成：

> “不同软件的差异”。

因此第一套实现继续固定 ZCode，只改变能力接入层：

```text
同一个 Training Service
        ↓
A. curl / Raw API
        ↓
B. ZCode MCP Tool
        ↓
C. ZCode Skill + MCP
        ↓
D. ZCode Command / Plugin（扩展）
```

这样控制变量更清楚。

---

# 2. Case 1：Raw API

先不给 Agent MCP。

在 ZCode Terminal 中直接：

```bash
curl http://127.0.0.1:8766/status
```

课堂问题：

> **这个系统已经能被程序调用了，为什么还需要 MCP？**

先保留这个疑问。

这一阶段展示：

- Endpoint；
- JSON；
- curl；
- Status Code；
- Raw API。

对应：

`CONNECT-R01`

---

# 3. Case 2：同一能力通过 ZCode MCP

ZCode 当前官方支持：

- User / Workspace scope；
- stdio；
- HTTP；
- SSE；
- JSON configuration；
- Plugin MCP servers。

训练 Demo 优先使用 Workspace scope，避免影响其他项目。

MCP Server 暴露：

```text
get_service_status()
get_service_logs(tail)
restart_test_service()
```

MCP Server 内部仍调用：

```text
GET /status
GET /logs
POST /restart-test
```

课堂问题：

> **后端 API 变了吗？**

答案：

没有。

变化的是：

> **Agent 看到的能力界面从 URL/JSON 变成了有名字、有参数 Schema 的 Tool。**

对应：

`CONNECT-R02`

---

# 4. Case 3：Skill 组合 MCP Tools

创建：

```text
service-acceptance/
└── SKILL.md
```

后续可再增加：

```text
references/
scripts/
assets/
```

Skill 规则：

1. 先查状态；
2. unhealthy 才读取日志；
3. 不允许直接重启 production；
4. training 环境可在确认后重启；
5. 重启后再次读取状态；
6. 输出前后证据；
7. 明确未验证项。

课堂问题：

> **MCP 已经有三个 Tool，为什么还要 Skill？**

答案：

> **MCP 提供动作；Skill 提供做事方法。**

对应：

`CONNECT-R03`

---

# 5. Case 4：Command

ZCode 当前官方把 Command 定位为可复用 Prompt / 快捷入口。

因此可以把：

```text
/accept-service
```

设计成一个简单入口。

它的作用不是替代 Skill，而是：

> **让用户快速启动一类固定动作。**

课堂对比：

```text
Command：入口
Skill：方法
MCP：动作
API：系统接口
```

如果只是一个简单固定 Prompt，用 Command 即可。

如果需要：

- scripts；
- templates；
- examples；
- 多步流程；

优先 Skill。

---

# 6. Case 5：Plugin

ZCode 当前 Plugin 可以打包：

```text
plugin
├── commands/
├── skills/
├── agents/
├── hooks/
└── .mcp.json
```

因此培训中可以把前面的训练能力最终打包成：

```text
training-service-plugin/
├── .zcode-plugin/
│   └── plugin.json
├── commands/
│   └── accept-service.md
├── skills/
│   └── service-acceptance/
│       └── SKILL.md
└── .mcp.json
```

如果后续需要再增加 Hook。

课堂问题：

> **Plugin 又解决什么？**

答案：

> **前面解决“能力是什么、流程是什么”，Plugin 解决“怎样把一组扩展能力安装和分发”。**

这里必须标注：

> 这是 ZCode 当前 Plugin 实现，不是所有 Agent 的统一标准。

---

# 7. Case 6：Hook

不建议第一轮就做复杂 Hook。

只设计一个安全教学 Hook：

> 在高风险训练动作前记录/检查环境。

例如：

```text
BeforeToolUse
→ environment == training ?
→ yes: continue
→ no: stop / require approval
```

教学重点：

```text
Command = 用户主动触发
Hook = 事件自动触发
```

具体 Event Name 和 Hook Schema 以实现当天 ZCode 官方文档为准。

---

# 8. 最终课堂一张图

```text
Training Service
       │
       │ REST API
       ▼
   Raw API / curl
       │
       │ wrapped as tools
       ▼
   MCP Server
       │
       │ tools
       ▼
   ZCode Agent
       │
       ├── Command：入口
       │
       ├── Skill：方法
       │
       └── Plugin：安装/分发包
               └── Hook：事件触发
```

---

# 9. 实测时必须记录

- ZCode version；
- Model；
- MCP scope；
- MCP transport；
- Tool list；
- Tool schema；
- Raw API request / response；
- MCP Tool Call / Tool Result；
- Skill trigger；
- Skill 是否按顺序使用 Tools；
- Command；
- Plugin directory；
- Permission / confirmation；
- 失败项。

---

# 10. 事实边界

当前 ZCode 官方资料：

- MCP：https://zcode.z.ai/en/docs/mcp-services
- Skill：https://zcode.z.ai/en/docs/skill
- Command：https://zcode.z.ai/en/docs/commands
- Plugin：https://zcode.z.ai/en/docs/plugin

当前已确认：

- ZCode 支持 User / Workspace MCP；
- 支持 stdio / HTTP / SSE；
- Skill 使用 `SKILL.md`；
- Command 适合保存简单 Prompt；
- ZCode 官方明确建议复杂流程用 Skill；
- Plugin 可打包 Skill / Command / Subagent / MCP / Hook。

以上是当前官方实现，后续实际录制仍以安装版本为准。
