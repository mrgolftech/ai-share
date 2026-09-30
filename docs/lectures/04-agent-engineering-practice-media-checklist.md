# 第四讲素材清单：Agent 工程实战

> 日期：2026-09-30  
> 对应讲义：`docs/lectures/04-agent-engineering-practice.md`  
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

# 39. 第四讲截图执行清单

## 39.1 BMQuiz P0

### BM-01：旧版 vs 当前

需要：

- oldquiz 可运行界面；
- 当前 BMQuiz 首页 / 练习页。

尽量同样窗口比例。

### BM-02：Product Spec

不要截整页小字。

框出：

- 核心产品链；
- canonical 数量；
- non-goals。

### BM-03：Constraint → Architecture

建议根据真实文档自绘，标注“基于当前仓库事实整理”。

### BM-04：总体架构

使用仓库架构图重绘为 PPT 友好版本。

### BM-06：AGENTS.md

截关键规则 + Agent 实际读取画面。

### BM-07：Docs Tree

把 Product / UI / Architecture / Data / Roadmap / Acceptance / Deployment 目录一次展示。

### BM-08：Server CI

GitHub Actions run：

- typecheck；
- tests；
- migration；
- health。

### BM-09：Visual QA

需要：

- workflow；
- screenshot artifact；
- 最好有一次修改前后。

### BM-10 / 12：Git 时间线

建议自己根据真实 commits 制作时间线，不直接截长 Git log。

### BM-11：CI/CD

Workflow 列表 + 一次成功 Release。

### SERVER-01～02

测试/生产环境先脱敏：

- container；
- image tag；
- logs；
- health。

---

## 39.2 FileCheck P0

### FC-01：GUI + CLI

GUI：

> 首页或扫描页。

CLI：

> 主菜单或 help。

目的：

> 一眼看出同一 Core 的两个入口。

### FC-02：Requirements

截：

- 正式工作流；
- Non-goals。

### FC-03：约束图

自绘：

```text
Offline
Win7
Unicode
Large File Set
Safety
↓
Architecture / Packaging / Test
```

### FC-04：Core → CLI / GUI

根据 Architecture + GUI Design 绘图。

### FC-05：CLI + selftest

截：

- selftest PASS；
- 受控测试目录。

### FC-06：Safety Flow

根据真实架构绘制 Backup/Delete/Restore。

### FC-07：GUI

至少：

- Scan；
- Results；
- Backup；
- Delete；
- Restore。

不需要每页单独放 PPT，但素材提前拍齐。

### FC-08：Danger Confirm

必须使用测试数据。

画面要看到：

- 文件数量；
- 高风险颜色；
- 明确确认。

### FC-09：CI

GitHub Actions Matrix。

### FC-10：v0.2.3 Release

截三个正式包。

### FC-11：Package Tree

解压后的真实目录：

- GUI exe；
- advanced CLI；
- tools；
- config；
- runtime；
- SHA256SUMS。

### FC-12：Release Pipeline

根据真实 Workflow 制作图，不猜不存在的步骤。

---

## 39.3 短案例 P0/P1

### MM-CASE-01

model-metric：

- UI；
- /api/overview；
- /api/instances。

### IPSEC-01～03

只使用脱敏数据：

- 原始现象；
- 分析；
- 工程证据。

### HF-01～03

- Storyboard；
- Preview；
- Action；
- Final Video frame。

### SEC-01

建议使用流程图，不必使用敏感测试界面。

---

# 40. 第四讲录屏执行脚本

## BM-R01：BMQuiz Visual QA

原始 3～5 分钟。

步骤：

1. 给 Agent 一个小 UI 修改；
2. 修改；
3. test/build；
4. Browser；
5. Screenshot；
6. 发现一个视觉/交互问题；
7. 修改；
8. 再 Screenshot。

课堂剪辑重点：

> “代码完成”和“用户界面完成”之间还有一个反馈循环。

## BM-R02：Deploy

优先预录。

步骤：

1. 查看当前 version；
2. SSH；
3. current container；
4. data volume；
5. pull / deploy；
6. logs；
7. health；
8. 产品 smoke。

不要在正式课堂临时执行高风险生产操作。

## BM-R03：小需求完整闭环

固定真实小需求。

完整保留：

- Requirement；
- Rules；
- Plan；
- Edit；
- Test；
- Browser；
- Diff。

这是第四讲最重要的录屏。

## FC-R01：FileCheck 小需求

固定受控分支和测试数据。

1. 读 Requirement；
2. 读 GUI Design；
3. Plan；
4. 改；
5. pytest；
6. GUI smoke；
7. Launch；
8. Diff。

## FC-R02：Build / Release

优先使用 GitHub Actions 录屏：

1. Workflow；
2. Jobs；
3. Artifact；
4. Release Assets；
5. SHA256。

等待时间剪掉。

## FC-R03：Backup / Verify / Restore

只用测试目录。

不要使用真实重要文件。

清楚展示：

```text
Source
→ Backup
→ Manifest
→ Verify
→ Remove only if planned
→ Restore
→ Hash Match
```

若演示删除，使用专门临时目录并预录。

## IPSEC-R01

录数据分析过程时不要录完整长对话。

只保留：

- 输入问题；
- 第一个假设；
- 数据图；
- 反证/补充；
- 最终工程验证。

## HF-R01

步骤：

1. 修改一个 scene；
2. 本地 Preview；
3. 时间轴；
4. Commit；
5. GitHub Action；
6. Artifact / Final video。

---

# 41. 第四讲案例准备优先级

如果时间不足，不要平均准备六个案例。

## P0：必须做扎实

### BMQuiz

至少：

- BM-01～12 核心截图；
- BM-R01；
- BM-R03；
- Deploy 可用截图或预录。

### FileCheck

至少：

- FC-01～12；
- FC-R01；
- FC-R02。

## P1：至少一套完整证据

- model-metric；
- IPsec；
- HyperFrames。

## P2：时间允许再加入

- 授权范围内的接口兼容性 / 安全验证。

原则：

> **两个纵向案例证明方法，多种横向案例证明适用范围。**

---

# 42. 第四讲现场节奏建议

建议不要一口气现场演 6 个工具。

## 第一段：方法论 10～15 min

一张完整工程链。

## 第二段：BMQuiz 40～45 min

历史证据 + 一个真实增量 Demo。

## 第三段：FileCheck 30～35 min

架构 / 安全 / Packaging + 一个小 Demo。

## 第四段：短案例 15～20 min

model-metric / IPsec / HyperFrames 快速切换。

## 第五段：收束 5～10 min

METHOD-06 + METHOD-07。

这一讲应该是四场里截图和录屏比例最高的一场。

---
