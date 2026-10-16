# Cherry Studio 知识库召回质量对比实验 V1.0

> 状态：已有初稿 / 待实测（2026-10-16）。**未执行任何本地 Cherry 实验，不得引用本文件中的指标目标作为实测数据。**
>
> 目的：在普通办公 CPU、100–1000 个 Chunk 范围，比较 A（仅 BM25）与 B（BM25 + 本地 Qwen3 Embedding 0.6B）的证据检索质量。
>
> 所属 Demo：`demos/knowledge-retrieval/README.md`，作为第二讲“Cherry 文档解析、Chunk、BM25、Embedding、RAG 评测”的实操证据补充，不另起知识源。
>
> 官方功能依据：
> - https://cherryai.com.cn/docs/zh-cn/knowledge-base/create/
> - https://cherryai.com.cn/docs/zh-cn/knowledge-base/emb-models-info/
> - https://cherryai.com.cn/docs/zh-cn/knowledge-base/recall-test/

## 0. 先明确能测什么，不能测什么

- 官方文档指出：**不配置 Embedding 时仍使用 BM25；选择 Embedding 后使用 BM25 + 向量检索并合并结果**。因此这是 **BM25 vs Hybrid**，不是“BM25 vs 纯向量”。
- Cherry 的“召回测试”检验搜索证据，不涉及 LLM 回答质量。召回到无关片段不等于模型已经幻觉；无答案题的拒答需要另外测试完整 RAG 流程。
- 评价对象是 **Retriever 在固定语料与固定分块下的质量**。CPU 延迟是次要监测项，不以用户看到聊天回答为依据。
- 不能仅依据返回文档名称“正确”就算命中；需要对照**完整支撑答案的原文证据**。

## 1. 语料与规模

沿用 `demos/knowledge-retrieval/README.md` 的同源资料原则。优先选取本仓库中有事实基线、允许共享的 Qwen API/实测资料：

- `api/qwen/reports/qwen36_api_test_report_20260930.md`
- `api/qwen/results/20260930_095033/evidence.md`
- `api/qwen/README.md`
- `docs/chapters/01-intranet-qwen-api.md`
- 如需扩充，加入已授权、去敏后的硬件、软件、测试技术资料；保持真实、异质和版本标记。不强制纳入无关文档凑数量。

第一阶段 100–300 Chunk / 30 题做流程与调试；第二阶段 500–1000 Chunk / 60 题形成冻结后的正式评价集。两阶段均记录**实际** Chunk 数量，若规模不达标调整材料后重新冻结，不根据文件数估计。

每个源文件登记路径、SHA-256、版本、许可/密级、解析器/OCR 配置；只在仓库中提交允许公开的资料、脱敏证据和汇总，禁止上传内部敏感信息。

## 2. 实验环境记录表（每次测试填写）

| 项目 | 值 |
|---|---|
| 测试日期与实验操作者 | 待填写 |
| Cherry Studio 精确版本号 | 待填写 |
| Windows 版本 / CPU 型号 / 内存 | 待填写 |
| 离线状态、代理及网络环境 | 待填写 |
| DirectML/CoreML 设置 | **关闭或确认未启用 GPU**，以保证 CPU 条件；记录实际状态 |
| 本地 Embedding 模型名称、文件/量化版本 | Qwen3 Embedding 0.6B（实际安装版本待确认） |
| 文档解析器 / OCR 模型与选项 | 待填写 |
| Chunk 大小 / 重叠 / 分隔规则 | 待填写（两个组相同） |
| 文件数 / Chunk 数 / 原始语料 SHA-256 清单 | 待填写 |
| Top K | **5**（两组固定） |
| Rerank / 相似度阈值 | **均不配置 Rerank**；阈值不适用 |
| 每种配置的索引建成时间 | 待填写 |
| 两组可比性（Chunk 数、文本抽样、分块边界） | 待核验 |

> Cherry 官方文档所述默认 Top K 为 6；本实验**主动固定为 5**，便于 Hit@1/3/5 分层评估。不能误写为产品默认配置。切分/模型变更后要完成重建索引或重建知识库，等待全部就绪再开始测试。

## 3. 控制变量

| 变量 | A：BM25 基线 | B：本地 Hybrid |
|---|---|---|
| 资料文件与版本 | 相同 | 相同 |
| 解析器/OCR/Chunk 设置 | 相同 | 相同 |
| Embedding | 不使用 | 本地 Qwen3 Embedding 0.6B |
| 向量 | 无 | 有 |
| BM25 | 有 | 有 |
| Rerank | 不启用 | 不启用 |
| Top K | 5 | 5 |
| CPU 条件 | 相同机器与后台负载 | 相同机器与后台负载 |

建议建立两个**独立知识库** A/B，避免在同一个库中反复切模型引入索引状态混乱。
两组需核对正文、Chunk 数与抽样分块边界；如果不一致，必须先标记为不可严格归因，排查重建/解析差异后再继续。
每组先执行 3–5 个**不计入正式成绩**的预热查询；再以相同问题清单和顺序测试。为记录延迟，可将每道查询重复 3 次（不把重复次数当成新的统计样本）；保存每次耗时。模型计算加速是否生效以进程/资源监控为证据。

## 4. 问题集与人工标准（Gold Set）

正式集 60 道（此配额是工程建议，不是统计学保证）：

| 类型编码 | 题型 | 数量 | 观察点 |
|---|---|---:|---|
| EXACT | 专业术语、器件型号 | 12 | 确切字符串 / 标识符 |
| ID | 标准、接口、寄存器编号 | 8 | 中英混排、数字、特殊字符 |
| PARA | 同义词、口语改写 | 12 | 与原文词汇差异 |
| WHY | 原理、因果与技术机理 | 12 | 自然语言长句检索 |
| MULTI | 多条件、相近概念易混淆 | 10 | 证据是否完整而非仅同主题 |
| NONE | 语料中不存在可用答案 | 6 | 检索噪声；**不**推断系统拒答能力 |

逐题填写 `benchmark/queries.csv` 与 `benchmark/gold_evidence.csv`。证据由人工从**原文**独立标注：证据 ID、文档来源、SHA-256、章节、关键原文、支持的事实。若答案要求两个独立事实，在 `gold_evidence_ids` 字段以分号列出两项；检索结果只有覆盖全部必要事实才算完整证据命中。

标注时应注意：答案若不在当前语料中，标为 NONE；不得使用旧版本或非授权来源充当正确证据。正式集冻结后不再针对 A/B 结果改题；第一阶段可用于修复标注流程，不能用其调出的参数反过来夸大效果。建议另一位熟悉业务的工程师抽检至少 20% 标注，分歧记录并仲裁。

## 5. Cherry 操作 Runbook

1. 创建 A（Embedding=不使用），导入冻结资料，等待文档/索引就绪。
2. 打开每份资料的 Parsed Text / Chunk，抽查内容、标题、表格、证据跨块、版权脚注、OCR 错字；记录失败。**正文缺失时先修语料，不要调检索模型。**
3. 创建 B（Embedding=本地 Qwen3 Embedding 0.6B，提前完成本地下载），相同文件、解析与分块设置；完成索引后对照 A 的片段。
4. 两组 Top K=5、无 Rerank。正式对照时不改同义词词典、Chunk 大小和检索参数。
5. `知识库 → 召回测试` 逐题执行同一份 `queries.csv`（固定问题顺序）。每次记下前 5 名的实际来源、排名、文本片段、检索时延；无结果以 rank=0 行记录。
6. 先比对人工证据，再把每条 Chunk 标记为 `adequate_evidence=1/0`：只有片段能支持该 required_fact 时才标 1；标题接近但缺少关键事实标 0；支持多项证据可分号分隔 IDs。
7. 结果进入 `benchmark/retrieval_results.csv`，保存必要截图；每个问题都要有 A/B 结果，缺项视为“未执行”而非失败。
8. 输出总表、分题型结果、A-only/B-only/both-miss 三类案例，标明版本、样本数与方法局限。

## 6. 数据记录格式

### benchmark/queries.csv（题级标准）
`query_id,category,question,answerable,gold_evidence_ids,expected_source,expected_fact,notes`

- `answerable` 为 `yes` / `no`；no 时证据 ID 为空。
- `gold_evidence_ids` 中多个 ID 使用 `;` 分隔，代表回答必需的**全部**证据单元。
- `category` 仅使用上面六个类型编码。

### benchmark/gold_evidence.csv（独立于检索结果的证据）
`evidence_id,doc_path,doc_sha256,section,required_fact,anchor_quote,notes`

- `anchor_quote` 不应包含受限原文进入公开仓库；有权限限制时仅存储授权位置引用与脱敏标注。

### benchmark/retrieval_results.csv（每个返回 Chunk 一行）
`run_id,query_id,rank,returned_source,returned_chunk_excerpt,matched_gold_ids,adequate_evidence,latency_ms,notes`

- `run_id` 使用 `A` 或 `B`，每题若返回 5 个 Chunk 便记录 5 行；返回 0 个时记录 rank=0 的一行。
- `rank` 为 UI 排名 1–5，`adequate_evidence` 为 `1` 或 `0`。
- `matched_gold_ids` 仅在 `adequate_evidence=1` 且确实能支持证据时填写；允许多个 ID 用 `;` 分隔。
- 同一道题的检索时延可在该题各行重复记录相同数值，**计算时每题仅取一个时延样本**。如果需要三次重复延迟测量，另表按 query_id/run_id/repetition 记录；不要把一次的排名复制为三份“质量样本”。

> 对于整个语料“无答案”的题，系统返回任意 5 个 Chunk 并不一定是 Bug：Top K 检索通常会给出最近的候选。人工应把这些 Chunk 标成非有效证据，后续单独测试 LLM 是否拒答。不能将无答案题纳入有答案题的 Hit@K 分母。

## 7. 指标、分母和公式

在 60 道正式题中，54 道 answerable=yes 构成检索质量计算分母；6 道 NONE 单独记录。

- **Hit@1/3/5** = 在 Top K 中至少出现 **1 个完整、有效必需证据单元** 的有答案题数 / 54。
- **MRR@5** = 对 54 道题求平均 `1 / 第一个有效证据单元的排名`，前五无命中记 0；适合排序分析。
- **FullEvidence@5** = 在 Top 5 中全部必需证据单元被有效覆盖的有答案题数 / 54；最能体现 MULTI 题能否得到足够事实。
- **精确题回退**：EXACT、ID 分别给出 A/B Hit@5 的分子/分母与失败列表。
- **语义增益**：PARA、WHY 分别给出 `B Hit@5 − A Hit@5`（百分点）。
- **无答案诊断**：NONE 题前五名中无有效证据是预期的标注结果；逐条报告存在误导性强的候选和相似度（如果可见），**不将“有搜索结果”等同于“系统未拒答”**。
- **次要性能**：查询延迟 P50/P95（同一组热启动条件）、索引耗时、最大进程内存；不合并到质量分数。

建议的**待验证验收目标**（不是实测）：
- B 的整体 Hit@5 候选目标 >=85%，FullEvidence@5 >=75%；
- PARA 题预期改善需逐题展示；EXACT/ID 题若回退，应先保留 A 基线并分析；
- 不以 60 题上的小百分点差距宣称统计显著，也不先假设 B 一定优于 A。

## 8. 判断和失败归因

| 现象 | 优先排查 | 可采取的后续动作 |
|---|---|---|
| A/B 都未命中 | 原文缺失、OCR、分块断裂、Gold 标注错误 | 修资料/分块，建立**新版**基线 |
| A 命中，B 不命中 | Hybrid 合并、候选竞争、术语拆分、Top K | 保留 A；检查混合候选而非假设向量有害 |
| B 命中，A 不命中 | 同义词、自然语言问法与正文词汇错位 | 将该题作为语义召回价值证据 |
| 都命中，但排位很后 | 排序不稳 | 后续可单变量开启 Rerank 单独实验 |
| 同源不同版本相互冲突 | 没做版本去重/元数据筛选 | 先解决 Source of Truth，不归因于模型 |
| NONE 题返回相关话题 | 检索器没有“无答案”判定 | 后续测试阈值、RAG 提示词和拒答 |

## 9. 截图、归档与培训交付

建议素材编号：
- `KB-BENCH-01`：原始 PDF、Parsed Text、Chunk 对照（包含页眉页脚/OCR 典型问题）；
- `KB-BENCH-02`：A 组设置 + BM25 Recall Test；
- `KB-BENCH-03`：B 组本地 Embedding 设置 + Recall Test；
- `KB-BENCH-04`：同一道 PARA 题 A/B 并列对比；
- `KB-BENCH-05`：EXACT 题保持/退化案例；
- `KB-BENCH-06`：完整结果汇总表 + A-only/B-only/both-miss；
- `KB-BENCH-R01`：从添加文件、查看 Chunks、召回测试到两组对比的录屏。

运行后填写报告：设备/版本、数据快照、原始结果文件、指标分子/分母、失败案例截图、可复现实操条件、工程结论。当前状态只能标记 **已有初稿**，待真实测试和截图完成后升级。

## 10. 补充边界

- 纯向量组在 Cherry 当前 GUI 上**没有因设置 Embedding 就天然可用**；需要能关闭 BM25 的其他实现才能做严格三路对照。
- 冷启动和热启动延迟必须分开，CPU 推理量化、DirectML 与 CPU 可能混用，不可凭“本地模型”自动认定纯 CPU。
- 解析质量和召回质量是两个阶段，OCR 误识别/表格被打散会造成上限问题。
- 不推断问答正确率、引用正确率、ACL 有效性，这些需要生成层/权限层专门测。
