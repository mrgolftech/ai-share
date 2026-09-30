# Chat Workbench 数据边界与“API 不等于 Chat”证据摘要（2026-09）

> 用途：支撑第一讲中 Cherry Studio / Open WebUI 的部署与数据边界对比，以及“同一个模型 API 可以被封装为非 Chat 应用”的讲解。  
> 原则：产品事实以官方文档/官方仓库为主；部门内网 qwen3.6 的具体能力，以本仓库实测为最高优先级。

---

# 1. Cherry Studio：Desktop / Local-first 形态

Cherry Studio 官方知识库文档说明，加入知识库的数据在本地保存，并在 Cherry Studio 数据目录中保存导入资料的托管副本、解析文本、Chunks 与检索索引。

同时必须保留边界：

> “知识文件存在本机”不等于“整个处理链都离线”。

如果解析、OCR、Embedding、Rerank 或最终模型调用使用远程服务，相应文件、片段或查询仍可能离开本机。

参考：

- https://github.com/CherryHQ/cherry-studio-docs/blob/main/knowledge-base/data.md
- https://docs.cherry-ai.com/cherry-studio-wen-dang/en-us/knowledge-base/knowledge-base-data

培训推荐表述：

> **Cherry Studio 是典型桌面客户端 / Local-first AI 工作台；个人配置、知识和会话主要由本机客户端管理，但最终数据边界仍取决于实际 Provider 与处理链。**

---

# 2. Open WebUI：Self-hosted Server-side 形态

Open WebUI 官方文档显示：

- Chat 历史保存在服务端数据库中；
- 上传文件、Knowledge、Notes、用户、模型配置等由服务端持久化管理；
- 默认 SQLite 数据库位于服务端数据目录，也支持 PostgreSQL 等外部数据库；
- 上传文件、vector store 与数据库都属于备份/迁移时需要考虑的服务端持久化资产；
- 同一账号可从多个设备访问已保存 Chat。

参考：

- https://docs.openwebui.com/features/chat-conversations/chat-features/history-search/
- https://docs.openwebui.com/reference/database-schema/
- https://docs.openwebui.com/tutorials/maintenance/backups/
- https://docs.openwebui.com/features/workspace/knowledge/

培训推荐表述：

> **Open WebUI 是典型的自托管 Web / Server AI 工作台：浏览器是入口，Chat、文件、Knowledge、Note、Workspace 配置等主要由集中服务器管理。**

历史表述边界：

> 不在培训中把“Open WebUI 是最早/第一个/当时少数几个服务端开源项目”写成未经系统历史统计的硬事实。更稳妥的说法是：**在大量面向个人的桌面/本地客户端之外，Open WebUI 是一个非常典型、且长期采用集中式自托管架构的开源代表。**

---

# 3. API 不等于 Chat

模型 API 的本质是：

```text
Input
+ Instructions
+ Parameters / Output Contract
→ Model
→ Output
```

Chat 只是其中一种应用封装：

```text
Conversation History
+ User Message
→ Chat UI
→ Model API
```

同一个 API 还可以被封装为：

- 文本翻译；
- 信息抽取；
- 分类与路由；
- 图片文字识别；
- 图片/网页截图检查；
- 文档字段提取；
- 结构化 JSON 生成；
- Tool Calling；
- Agent。

这类应用与 Chat 的差别首先不在“换了一个模型”，而在：

- 输入由程序自动提供；
- Prompt / System Prompt 由应用固定；
- 输出由程序继续消费；
- 需要更严格的格式校验、错误处理和测试。

---

# 4. Structured Output：Prompt JSON 与 Schema 约束不是一回事

OpenAI 官方 Structured Outputs 文档明确区分：

- JSON Mode：保证是合法 JSON，但不保证符合指定 Schema；
- Structured Outputs：使用 JSON Schema 对输出结构进行约束；
- Function Calling：适合模型要调用程序工具的场景；
- response format / text format：适合模型直接返回结构化结果给应用的场景。

参考：

- https://developers.openai.com/api/docs/guides/structured-outputs

培训工程边界：

> **“请只输出 JSON”只是 Prompt 约束，不等于协议层 Structured Output。**

如果当前服务没有正式验证 JSON Schema / Structured Outputs：

1. 先要求模型输出 JSON；
2. 程序端执行 JSON parse；
3. 再做 Schema / 类型校验；
4. 失败则重试或降级；
5. 后续把 `response_format/json_schema` 纳入兼容性测试后，再宣称“协议级结构化输出已支持”。

当前 qwen3.6 r4 正式验收已经覆盖 Chat / Responses / Anthropic、Tool Loop、Vision 等，但第一讲当前能力矩阵未包含 Structured Outputs / JSON Schema，因此不要从“OpenAI-compatible”直接推断该能力已经通过。

---

# 5. Vision 示例的培训安全边界

可以用自制的“验证码样式图片”说明：

> 图片 → Vision Request → 文本/结构化结果

但只作为自有测试图片 / OCR 示例。

不把培训内容做成：

- 绕过第三方 CAPTCHA；
- 绕过网站反自动化；
- 未授权自动化访问。

更推荐的素材：

- 自制 4～6 位字符图片；
- 产品标签 / 仪表读数；
- 自己的网站截图；
- 内部 Demo 网页布局缺陷截图。

这样既能说明 Vision API 的工程用法，也不会把培训主题带偏。
