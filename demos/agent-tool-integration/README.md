# API → MCP → Skill 统一教学 Demo 设计

> 状态：规划完成，待实现/实测  
> 对应讲义：`docs/chapters/06-api-mcp-skill-plugin-command-hook.md`

## 1. 目标

用**同一个后端能力**演示三层差异：

```text
Raw API
→ MCP Tool
→ Skill + MCP
```

避免使用三个不同系统，导致学员把“能力差异”误认为“产品差异”。

---

## 2. 建议后端：Training Service

先实现一个非常小的本地训练服务：

```text
GET /health
GET /status
GET /logs?tail=20
POST /restart-test
```

只作用于训练环境，不连接生产系统。

返回固定、可验证 JSON。

例如：

```json
{
  "service": "training-api",
  "version": "1.0.0",
  "status": "healthy"
}
```

---

## 3. Demo A：Raw API

用 curl / Postman：

```bash
curl http://127.0.0.1:8766/status
```

教学问题：

> 程序已经能调用，为什么 Agent 还需要另一层？

保留截图：

- CONNECT-R01；
- Request；
- JSON Response。

---

## 4. Demo B：MCP Tool

MCP Server 暴露：

```text
get_service_status()
get_service_logs(tail)
restart_test_service()
```

内部仍然调用 Training Service API。

教学重点：

> MCP 没有替代 API，而是给 Agent Host 一个标准 Tool Surface。

必须保留：

- Tool list；
- Tool Schema；
- Agent Tool Call；
- Tool Result；
- 后端 API 日志。

对应：

- CONNECT-R02。

---

## 5. Demo C：Skill + MCP

创建：

```text
skills/service-acceptance/
├── SKILL.md
├── references/
│   └── acceptance-checklist.md
├── scripts/
│   └── summarize_result.py
└── assets/
    └── report-template.md
```

Skill 逻辑：

1. 调用 `get_service_status`；
2. 如果 unhealthy，先读取日志；
3. 不直接重启，先说明依据；
4. 在训练环境获得允许后调用 `restart_test_service`；
5. 再次读取状态；
6. 输出前后证据；
7. 按模板生成验收结论。

教学重点：

> Tool 提供动作；Skill 提供流程。

对应：

- CONNECT-R03；
- CONNECT-07。

---

## 6. Command / Hook 补充 Demo

### Command

如果选定 Harness 支持：

```text
/accept-service
```

作为用户主动入口。

### Hook

在高风险工具前：

```text
BeforeToolUse(restart_test_service)
→ 检查 environment == training
→ production 则拒绝/请求审批
```

对应：

- CONNECT-R05。

注意：

> Command / Hook 的具体格式按最终演示 Harness 当前官方实现编写，不提前硬编码跨产品格式。

---

## 7. 验收标准

Demo 完成必须满足：

- Raw API 独立可调用；
- MCP Tool 返回值与 Raw API 对得上；
- Skill 至少调用两个 Tool；
- Skill 有明确成功/失败判定；
- 重启类动作只允许训练环境；
- 所有请求/Tool Result 可留档；
- README 记录环境和版本；
- 有备用截图/录屏。

---

## 8. 后续实现顺序

```text
Phase 1  Training Service
Phase 2  MCP Server
Phase 3  MCP client/Harness test
Phase 4  service-acceptance Skill
Phase 5  Command/Hook（按演示 Harness）
Phase 6  截图/录屏
Phase 7  回填讲义和 evidence
```
