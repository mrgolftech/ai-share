# Open WebUI v0.11.0 内网知识工作流证据记录（2026-09）

> 用途：支撑第一讲 Chat Workbench 和第二讲部门知识库中的 Open WebUI 案例。  
> 当前内网部署版本：`v0.11.0`。  
> 证据优先级：当前内网实际使用 > 当前官方文档。  
> 当前状态：工作流已由实际使用走通，待补截图/录屏留档。

---

# 1. 当前内网已验证行为

当前已实际走通：

1. 用户可以创建自己的 Note / Markdown；
2. 支持上传文档；
3. 这些内容可以作为个人 Knowledge 使用；
4. 对具体 Markdown / 文档可选择：
   - Full Context / 完整文档；
   - Focused Retrieval / 聚焦检索；
5. 当前实例没有配置 Embedding Model，因此会提示：
   - 未向量化；
   - 或同等含义的 Embedding 缺失状态；
6. Knowledge 仍然可以被 Workspace / 模型配置引用；
7. 也可以在 Workspace 创建过程的 Knowledge 选项中上传/关联文档；
8. 选择对应 Workspace 后，问答可以依据其中资料回答；
9. Workspace / Model 可以配置 System Prompt，形成类似 Cherry Assistant 的可复用专用助手；
10. Note 页面可以直接围绕该 Note 进行对话；
11. 创建 Workspace / Model 时可以附加已有 Note / Knowledge，后续持续复用。

当前培训结论：

> **Open WebUI 当前内网版本既可以作为个人知识工作台，也可以进一步承载 Workspace / Shared Knowledge 场景。**

---

# 2.1 数据存储与部署边界

当前内网 Open WebUI 是集中式 Web / Server 部署。

培训中采用如下表述：

> **用户通过浏览器访问，Chat、Note、Knowledge、Workspace、上传文件等主要由 Open WebUI 服务端持久化和管理。**

Open WebUI 官方部署文档显示，默认上传文件保存在服务器 `DATA_DIR`，数据库保存账号、Chat、配置、Knowledge 等记录；规模化后可改用 PostgreSQL、共享文件系统或对象存储。

因此“服务端”不等于“公网云”。

部门内网服务器同样属于：

> **Server-side / Centralized Deployment。**

这与 Cherry Studio 的 Desktop / Local-first 数据管理形成直接对照。

同时提醒：

> 数据存在哪里与模型请求发到哪里是两个问题。即使资料存内网服务器，只要模型 Provider 是外部服务，被选入 Context 的内容仍会发送给对应 Provider。

---

# 2.2 Workspace Model 与 Cherry Assistant 的对应关系

当前 Open WebUI Workspace Model 可以组合：

- Base Model；
- System Prompt；
- Parameters；
- Knowledge；
- Tools / Skills。

这与 Cherry Assistant 的：

- Model；
- Instructions；
- Parameters；
- Knowledge；
- MCP / Tools；

解决的是同一类应用问题：

> **把基础模型包装成可重复使用的专用助手。**

两者本质上都是 Application Preset / Wrapper，不是模型 Fine-tuning。

只有当再叠加：

- Tool Calling；
- Runtime；
- Loop；
- Verification；

才进入第三讲所说的完整 Agent 工作方式。

---

# 2.3 Note 的两个实际用法

当前内网 v0.11.0 已走通：

## Note-centered Chat

```text
Markdown Note
→ Note Chat
→ 围绕当前笔记问答 / 修改
```

从用户体验看，可以理解为：

> **直接围绕自己的持久笔记进行 AI 协作。**

但培训中不直接称为 Vector RAG。

## Note → Workspace

```text
Existing Note / Knowledge
→ Workspace Model
→ System Prompt
→ Chat
```

这样可以把：

> 临时实验笔记

逐步变成：

> 某个长期专用 Workspace 的知识背景。

---

# 2. 当前不能直接下的结论

当前实例“没有 Embedding，但依然能够依据知识回答”，不能直接写成：

> “Open WebUI 没有 Embedding 也可以正常做 Vector RAG。”

更准确：

## Full Context

整篇文档直接进入模型 Context。

因此：

> **不需要 Embedding。**

## Focused Retrieval

Focused Retrieval 的目标是只找到当前问题相关部分。

当前未配置 Embedding 时：

- Vector Retrieval 本身没有完整建立；
- 当前实际走的是 BM25、Knowledge Tool、其他关键词方式还是其他 fallback，仍需要进一步通过当前实例的 Retrieval / Tool Trace 验证。

所以目前只能确认：

> **Knowledge 能够被引用并最终为回答提供依据。**

不能仅凭最终答案反推：

> 底层一定采用了某种特定 Retrieval。

---

# 3. 当前 Open WebUI 官方机制参考

当前官方文档确认：

## Knowledge

Knowledge Base 支持：

- 文档上传；
- Focused Retrieval；
- Full Context；
- Hybrid Search；
- Agentic Knowledge Tools。

官方说明：

- Focused Retrieval：从大型资料集中检索相关 chunks；
- Full Context：整篇内容直接进入每一轮 Context，不进行 chunk-based semantic retrieval。

参考：

- https://docs.openwebui.com/features/workspace/knowledge/

## Notes

当前官方 Notes：

- 是持久内容；
- 支持 Markdown；
- 可以附加到 Chat；
- 作为 Context 时按完整内容注入；
- 不是普通 Document RAG 的同一种机制。

参考：

- https://docs.openwebui.com/features/notes/

## Workspace / Models

当前官方 Workspace 支持将：

- Base Model；
- Prompt；
- Knowledge；
- Tools；
- Skills；

组合成可重复使用的配置。

参考：

- https://docs.openwebui.com/features/workspace/
- https://docs.openwebui.com/features/workspace/models/

---

# 4. 推荐培训 Demo

固定资料：

- Qwen API 当前测试报告 Markdown；
- 一条个人 Qwen 测试 Note。

## Demo 1：个人 Note

```text
Create Note
→ 写入一条当前测试结论
→ Attach / Knowledge
→ Chat
```

## Demo 2：Document

```text
Upload Markdown
→ Full Context
→ Ask
→ Focused Retrieval
→ Ask
```

## Demo 3：Embedding 缺失

展示：

> 当前没有 Embedding / 未向量化。

然后强调：

> 能回答 ≠ Vector RAG 已经建立。

## Demo 4：Workspace

```text
Knowledge
→ Bind Workspace / Model
→ Select Workspace
→ Ask
→ Grounded Answer
```

## Demo 5：后续补测

如果能够看到 Tool / Retrieval Trace：

- 记录 Focused Retrieval 当前实际采用的检索路径；
- 判断是否有 BM25；
- 判断是否调用 Knowledge Tool；
- 记录引用来源。

---

# 5. 素材编号

第一讲：

- OW-07：个人 Note；
- OW-08：上传文档；
- OW-09：Full Context / Focused Retrieval；
- OW-10：未配置 Embedding / 未向量化；
- OW-11：Workspace 绑定 Knowledge；
- OW-12：Workspace 基于知识问答；
- OW-13：Note/Document → Knowledge → Workspace → Chat 图；
- OW-R03：个人知识完整工作流。

第二讲：

- KB-15 / 15A；
- KB-16 / 16A / 16B / 16C；
- KB-R03A / B / C。

---

# 6. 培训中的一句话

> **知识能被模型用到，和知识通过什么 Retrieval 被找到，是两个问题。先观察证据，再判断机制。**


# 7. 数据与 Workspace 官方参考

- https://docs.openwebui.com/features/workspace/
- https://docs.openwebui.com/features/workspace/models/
- https://docs.openwebui.com/features/workspace/knowledge/
- https://docs.openwebui.com/features/notes/
- https://docs.openwebui.com/tutorials/maintenance/backups/
- https://docs.openwebui.com/getting-started/advanced-topics/scaling/
