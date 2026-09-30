# 第二讲素材清单：部门知识库建设

> 日期：2026-09-30  
> 对应讲义：`docs/lectures/02-department-knowledge-base.md`  
> 状态：Working Checklist v1.0  
> 使用原则：**正文决定“为什么需要这份素材、插在哪里”；本清单决定“具体拍什么、怎么拍、优先级、状态和备用方案”。**

---

## 0. 使用方式

- 正文中的 `【截图占位 ...】` / `【录屏占位 ...】` 是素材引用位置；
- 本文件是本讲唯一执行清单；
- P0：必须准备；P1：强烈建议；P2：可选；
- 每项完成后把状态改为：`⬜ 未准备` / `🟨 已采集待处理` / `✅ 可直接用于培训`；
- 同一素材如果跨讲复用，只保留一个原始文件，但在两个讲义清单中分别注明用途；
- 现场 Demo 涉及网络、模型排队、Browser、SSH、Build、GitHub Actions 时必须准备预录或静态备用。

---

## 1. 本讲素材总控表

| 素材组 | 优先级 | 主要内容 | 状态 |
|---|---:|---|---|
| KB-01~03 | P0 | 裸模型 vs 带资料、知识资产、Source of Truth | ⬜ |
| KB-04~07 | P0 | RAG、BM25/Vector、Parse、Chunk、Metadata | ⬜ |
| KB-08~11 | P0 | 长上下文、Evidence Budget、Rerank、Retrieval 路由 | ⬜ |
| KB-12~13 | P0 | Cherry Knowledge / Retrieval Test | ⬜ |
| KB-15~16C | P0 | Open WebUI Note / Full Context / Focused / Workspace | ⬜ |
| KB-18~22 | P0 | Agent 多源取证、ACL、引用、统一知识架构 | ⬜ |
| KB-R01~02 | P0 | Cherry 建库、BM25 vs Vector/Hybrid | ⬜ |
| KB-R03A~C | P0 | Open WebUI 个人知识、Retrieval 模式、Shared ACL | ⬜ |
| KB-R05 | P0 | Agent：KB → Git → API/Metrics | ⬜ |
| KB-R06 | P1 | 版本冲突 + No-answer | ⬜ |

> 第二讲所有工具尽量使用**同一套 Qwen API / model-metric 真实资料**，避免因语料变化干扰比较。

---

# 24. 第二讲截图执行清单

## 24.1 P0 必拍

### KB-01：裸模型 vs 带资料

固定同一内部问题。

左侧：

> 不提供资料。

右侧：

> 带当前实测报告。

目标：

> 一眼看出外部知识的价值。

### KB-06A：PDF → Parsed Text

选一页有表格或复杂结构的真实非敏感资料。

至少截：

1. 原始 PDF；
2. Parse 后文本/结构。

### KB-06：Chunk

最好使用带标题层级的 Markdown / PDF。

展示：

- 原文；
- Chunk 边界；
- Metadata。

### KB-04A / KB-05：BM25 vs Vector

必须使用同一个 Corpus。

准备：

- 一个精确关键词问题；
- 一个语义改写问题。

### KB-10：Rerank

如果工具能展示候选分数，截：

- 初始候选；
- rerank 后顺序。

如果工具不显示，制作基于实测结果的图示，但注明“示意”。

### KB-12～13：Cherry

拍：

- Knowledge Base；
- Retrieval Config / Test；
- 引用结果。

### KB-15～16C：Open WebUI v0.11.0

按当前内网实测准备：

- KB-15：Workspace / Knowledge 总览；
- KB-15A：个人 Note / Markdown；
- KB-16：Full Context / Focused Retrieval；
- KB-16A：未配置 Embedding / 未向量化提示；
- KB-16B：Workspace 绑定 Knowledge；
- KB-16C：选择 Workspace 后依据资料回答；
- Shared Knowledge / Citation 作为部门共享场景继续补拍。

### KB-21：ACL

拍用户/Group 和知识权限配置，敏感账号名称脱敏。

### KB-18：Agent 多源取证

要求画面中同时能看到：

- KB Search；
- File/Git Search；
- API / Metrics Tool；
- 最终引用。

---

# 25. 第二讲录屏执行脚本

## KB-R01：Cherry 建库完整流程

建议原始录屏 3～5 分钟，后期剪成 60～90 秒。

步骤：

1. 创建知识库；
2. 导入固定资料；
3. 展示 Parse / Chunk 设置；
4. 做 Retrieval Test；
5. 进入 Chat；
6. 查看引用。

目的：

> 让大家看到“上传文件”中间实际还有处理过程。

## KB-R02：BM25 vs Vector / Hybrid

固定两个问题。

过程：

1. 只启用 BM25 或关键词模式；
2. 问精确词问题；
3. 问语义改写问题；
4. 切 Vector / Hybrid；
5. 重复；
6. 对比召回。

不要为了展示效果临时换 Corpus。

## KB-R03A～C：Open WebUI v0.11.0

### KB-R03A：个人知识 → Workspace

步骤：

1. 新建个人 Note；
2. 上传 Markdown / 文档；
3. 展示 Knowledge；
4. 绑定 Workspace；
5. 选择 Workspace；
6. 固定问题；
7. 展示依据资料回答。

### KB-R03B：Full Context vs Focused Retrieval

同一 Markdown、同一问题切两种模式。

必须把当前“未配置 Embedding / 未向量化”状态一起录入，并观察 Retrieval / Tool Trace。

### KB-R03C：Shared Knowledge + ACL

再由共享知识场景展示：

1. Shared Knowledge；
2. Group / User；
3. ACL；
4. 用户可见性；
5. 引用。

## KB-R05：Agent 多源逐步取证

固定任务：

> “判断当前内网 Qwen 哪些 Agent 能力已有实测证据，哪些还没有。必须基于共享资料和仓库证据回答。”

录屏必须保留：

- 先 KB；
- 再 Git；
- 再 API/Metrics（如可用）；
- 最终答案和引用。

这条录屏是第二讲最重要素材之一。

## KB-R06：版本冲突 / No-answer

可以分两段。

版本冲突：

1. 同时放入 v1 / v2；
2. 观察不加 Filter 的结果；
3. 加 Version / current Metadata；
4. 回归。

No-answer：

1. 问 Corpus 中没有的问题；
2. 检查系统是否明确证据不足。

---

# 26. 第二讲现场 Demo 与备用策略

建议真正现场操作：

1. Cherry Retrieval Test；
2. 同一问题 BM25 vs Hybrid；
3. Agent 多源检索。

Open WebUI ACL、Parse、版本冲突等更适合预录，因为配置过程可能较长。

每个 Demo 都准备：

- 最终截图；
- 60～90 秒剪辑版；
- 原始完整录屏。

---
