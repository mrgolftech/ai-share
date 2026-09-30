# Cherry Studio API / Workbench 证据摘要（2026-09）

> 用途：支撑第一讲中 Cherry Studio 的协议配置、助手、知识库、联网搜索和工具能力说明。  
> 原则：当前产品界面可能继续变化，培训截图以实际安装版本为准；机制表述以官方文档和当前源码为依据。

## 1. Endpoint / Adapter

当前 Cherry Studio 源码将 Endpoint Type 与 Adapter Family 分开处理。

已明确出现：

- `openai-chat-completions`
- `openai-responses`
- `anthropic-messages`

官方源码说明：

- Anthropic Messages 默认映射 Anthropic adapter；
- OpenAI Responses 默认映射 OpenAI adapter；
- 其他常见 Chat endpoint fallback 到 OpenAI-compatible adapter。

参考：

- https://github.com/CherryHQ/cherry-studio/blob/main/docs/references/ai/adapter-family.md
- https://github.com/CherryHQ/cherry-studio/blob/main/docs/references/ai/provider-resolution.md

## 2. 多协议 Provider

Cherry Studio 当前 NewAPI Provider 官方文档明确说明，一个 New API 根地址可以连接：

- OpenAI Chat；
- OpenAI Responses；
- Anthropic Messages；
- Gemini。

源码中的 `endpointType` 也包含：

- `openai`
- `openai-response`
- `anthropic`

参考：

- https://github.com/CherryHQ/cherry-studio-docs/blob/main/pre-basic/providers/newapi.md
- https://github.com/CherryHQ/cherry-studio/blob/main/src/main/ai/provider/custom/newapiProvider.ts

培训注意：

> 不把 NewAPI 的具体 UI 路径泛化成所有 Custom Provider 的统一界面。实际培训使用当前安装版本截图。

## 3. 助手 / 对话

Cherry Studio 当前官方文档将：

- 助手：固定角色与模型配置；
- 对话：该助手下独立会话。

助手可设置：

- 基础信息；
- 默认模型；
- 模型参数；
- Prompt / Instructions；
- Knowledge Base；
- MCP。

参考：

- https://github.com/CherryHQ/cherry-studio-docs/blob/main/cherrystudio/preview/chat.md

## 4. 对话输入区

当前官方文档描述：

- Network Search；
- Knowledge Base；
- 上传附件；
- 更多快捷能力；

均可以从对话输入区启用。

模型参数按助手配置，包括：

- Temperature；
- Top-P；
- Max Tokens；
- Stream；
- Context Management；
- 自定义参数。

参考：

- https://github.com/CherryHQ/cherry-studio-docs/blob/main/cherrystudio/preview/chat.md

## 5. Knowledge Base

当前官方文档说明：

- 可创建 Knowledge Base；
- 可选择不使用 Embedding、以 BM25 为主；
- 可增加 File / Note / Directory / Link；
- 导入后应检查 Parse / Chunk；
- 使用 Retrieval Test 验证召回；
- 然后在 Conversation 中选择 Knowledge Base，或绑定到 Agent。

参考：

- https://github.com/CherryHQ/cherry-studio-docs/blob/main/knowledge-base/knowledge-base.md
- https://github.com/CherryHQ/cherry-studio-docs/blob/main/cherrystudio/preview/knowledge-base.md

## 6. Web Search

当前 Cherry Studio 官方文档说明：

- 对话输入框可直接开启联网模式；
- 搜索服务商与 URL 获取服务商可分别配置；
- 可使用配置的搜索服务，部分模型也可使用模型内置搜索能力；
- 官方当前文档列出 Exa MCP、Tavily、Bocha、Exa、Zhipu 等实现路径。

参考：

- https://github.com/CherryHQ/cherry-studio-docs/blob/main/pre-basic/websearch/README.md

培训注意：

> 具体默认服务商属于当前版本产品事实，培训主线只讲“联网搜索 = 外部搜索工具结果进入 Context / Tool Result”，避免把某个默认 Provider 讲成长期不变机制。

## 7. 设置结构

当前官方设置文档将能力区分为：

模型：

- Model Provider；
- Default Model；
- Local Model；
- API Gateway。

工具：

- MCP；
- Skills；
- Network Search；
- Document Processing。

参考：

- https://github.com/CherryHQ/cherry-studio-docs/blob/main/pre-basic/settings/README.md

## 8. 数据边界：Desktop / Local-first

Cherry Studio 官方知识库文档明确说明：

- 加入知识库的数据保存在本地；
- 添加文档时会在 Cherry Studio 本地数据目录保存副本；
- Knowledge 的索引与检索属于本机知识工作流。

因此培训中可将 Cherry 定位为：

> **Desktop / Local-first Personal AI Workspace。**

但必须同时说明：

> **Local Storage ≠ 所有内容永远不离开本机。**

当调用远程 / 内网模型 API 时，被选入最终 Prompt / Context 的内容仍然会发送到对应 Model Provider。

因此真正的数据边界应该拆成：

1. 原始文件 / Knowledge 存在哪里；
2. Embedding 在哪里计算；
3. Model Provider 在哪里；
4. 哪些证据最终进入 Request。

官方参考：

- https://docs.cherry-ai.com/cherry-studio-wen-dang/en-us/knowledge-base/knowledge-base-data

---

## 8. 培训使用边界

第一讲：

> 通过 Cherry UI 看见 Model / Instructions / Parameters / Knowledge / Search / Tool 怎样影响 Request 和 Context。

第二讲：

> 再深入知识库的 Parse / Chunk / BM25 / Vector / Hybrid / Rerank / Governance。

第三讲：

> 再深入 MCP / Tool / Agent Runtime。

避免同一个概念在三场重复展开。
