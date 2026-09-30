# 完整工程案例：FileCheck——Agent 怎样从 Windows 需求走到 GUI、兼容性、打包与发布

> 状态：Current Case Draft v1.0  
> 日期：2026-09-30  
> 真实仓库：`mrgolftech/filecheck`  
> 当前正式版本：v0.2.3（以当前 main / README / pyproject.toml 为准）  
> 教学主线：**Problem → Requirement → Constraint → Research → Architecture → Core → CLI → GUI → Test → Package → CI → Release → Verify → Assetize**

---

# 0. 为什么 FileCheck 适合作为第二个纵向案例

BMQuiz 证明了 Agent 可以参与 Web / PWA / Server 工程。

FileCheck 则完全不同：

- Windows 本地运行；
- 离线；
- GUI + CLI；
- 文件系统；
- Everything / ES；
- 高风险删除；
- SHA-256；
- Win7 / Win10 / Win11；
- x64 / x86；
- PyInstaller；
- portable package；
- GitHub Actions / Release。

因此它适合证明：

> **Agent 工程方法不依赖 Web 技术栈。**

---

# 1. 当前事实基线

当前 `README.md` 与 `pyproject.toml` 均表明正式版本为 **v0.2.3**。

当前产品定位：

> Windows 终端离线文件自查、备份与恢复工具。

正式流程：

```text
快速索引
→ 关键词扫描
→ 人工核对
→ 批量目录备份
→ 完整性验证
→ 源文件安全删除
→ 按原路径恢复
```

当前提供：

- GUI x64；
- CLI x64；
- CLI x86；
- portable Everything / ES；
- SHA256SUMS。

注意：

> `docs/REQUIREMENTS.md`、`docs/ARCHITECTURE.md` 当前仍以 V0.1.1 为标题，主要保存早期核心架构和可靠性设计。讲当前发布状态时，以 main 当前代码、README、pyproject 和 workflow 为优先；旧文档用于说明架构演进，不把旧版本号当当前发布版本。

---

# 2. Problem：真正的问题不是“做一个文件搜索 GUI”

真实目标包含：

- 大量文件快速候选发现；
- 离线工作；
- 人工核对；
- 批量备份；
- 完整性验证；
- 高风险删除；
- 原路径恢复。

关键词命中只意味着：

> 候选。

不意味着：

> 最终分类或违规判断。

这个边界非常适合培训：

> **AI/自动化负责筛选和执行，人仍负责关键业务判断。**

【截图占位 FC-01｜当前 GUI 首页 + CLI 主入口】

---

# 3. Requirement：功能与 Non-goals 同时定义

核心需求：

- 专用 Everything 索引；
- scan；
- review；
- backup；
- verify；
- remove sources；
- resume；
- restore。

Non-goals：

- 不做系统痕迹清理；
- 不自动清浏览器历史；
- 不自动清注册表；
- 不强制杀进程；
- 不递归删除父目录；
- scan/backup 不自动触发源文件删除。

【截图占位 FC-02｜Requirements：Goals / Non-goals】

结论：

> **对于涉及数据安全的工具，明确“不做什么”与实现功能同样重要。**

---

# 4. Constraint：平台和安全约束怎样决定架构

当前主要约束：

- Windows；
- 便携、离线；
- Win7 SP1 兼容；
- x86 / x64；
- Unicode 路径；
- 大量文件；
- 不干扰用户自己的 Everything；
- 删除必须有明确门禁；
- 中断后能够恢复状态；
- GUI 不能在主线程执行长任务。

【图示占位 FC-03｜Constraint → Architecture】

---

# 5. Research：技术选型如何讲得严谨

当前事实：

- Python Core；
- CustomTkinter GUI；
- Everything / ES；
- PyInstaller；
- pytest；
- GitHub Actions。

课堂可以做：

> Python vs Go、CustomTkinter vs PyQt/PySide/WebView 的 Architecture Review。

但必须明确：

> 如果缺少当时真实选择记录，这属于基于当前需求的“事后技术评审”，不是伪造历史决策过程。

当前选择继续使用 Python 的重要现实因素包括：

- 已有 Core 和测试资产；
- CLI/GUI 共用；
- 当前 packaging 已经形成；
- 迁移会带来真实重写和回归成本。

---

# 6. Architecture：Core → CLI / GUI

当前 GUI 代码直接复用：

- backup service；
- migration service；
- restore service；
- scan service；
- task runner。

架构可以归纳为：

```text
               Core
     ┌──────────┼───────────┐
     ↓          ↓           ↓
   Index      Backup      Restore
     │          │           │
     └──────────┼───────────┘
                ↓
          Service Layer
          ┌─────┴─────┐
          ↓           ↓
         CLI         GUI
```

【图示占位 FC-04｜Core → CLI / GUI】

原则：

> **GUI 不重新实现业务逻辑。**

---

# 7. 为什么先稳定 CLI 有价值

CLI 当前可以覆盖：

- doctor；
- index；
- scan；
- backup；
- verify；
- remove-sources；
- resume；
- restore；
- selftest。

它的价值：

- Core 可先独立测试；
- GUI 不是唯一入口；
- CI 可以直接验证业务能力；
- 问题容易定位在 Core 还是 Presentation。

【截图占位 FC-05｜CLI / selftest】

---

# 8. Reliability：这是案例最值得讲的部分

## 8.1 备份

真实 Core 包含：

- staging；
- temp file；
- fsync；
- SHA-256；
- source stability check；
- manifest；
- full verify；
- atomic publish。

## 8.2 历史备份保护

当前 v0.2.3 已强化：

> 历史 FileCheck 备份即使移动或改名，仍根据有效 manifest + files 结构识别和保护，而不是依赖外层目录名。

当前 `backup.py` 中已有专门结构识别和保护逻辑。

这很适合讲：

> **安全约束应该落进 Core，而不是只靠 UI 提示。**

## 8.3 删除

`migration.py` 当前可确认：

- 先完整 verify；
- 批次预检；
- SHA-256；
- stat 稳定性；
- 任一整批预检失败则不进入删除；
- 每文件即时再检查；
- source-removal.json；
- not-deleted.txt；
- resume；
- reappeared 保护。

【图示占位 FC-06｜Backup / Remove / Restore Safety Flow】

---

# 9. GUI：交互层同样需要工程规则

当前 GUI Design System 已定义：

- 浅色专业工具风格；
- 统一 Palette / Typography / Spacing；
- 固定页面结构；
- 公共组件；
- 危险按钮；
- DangerConfirmDialog；
- Worker Thread；
- queue；
- after；
- 1024×640 最小窗口；
- 不使用依赖浏览器内核的 WebView。

当前一级导航：

- 首页；
- 扫描；
- 扫描结果；
- 备份；
- 源文件删除；
- 恢复；
- 设置。

【截图占位 FC-07｜各主要 GUI 页面】

【截图占位 FC-08｜危险操作二次确认】

结论：

> **GUI 工程不是把 CLI 命令做成按钮，而是增加状态、用户路径、风险表达和并发交互。**

---

# 10. Compatibility：自动测试也有边界

当前普通 CI Matrix：

- Windows latest / Python 3.10；
- Windows latest / Python 3.12；
- Ubuntu latest / Python 3.10；
- Ubuntu latest / Python 3.12。

Windows 还执行：

- GUI construction smoke。

另有 Python 3.8 Win7 GUI compatibility job：

- compile source；
- import GUI services；
- construct GUI。

【截图占位 FC-09｜CI Matrix】

必须明确：

> **在 Windows runner 上用 Python 3.8 构建通过，不等价于真实 Windows 7 SP1 已经完成运行验收。**

真实老系统仍需要实机验证。

---

# 11. Packaging / Release：本地应用最终交付的是 Artifact

当前 v0.2.3 README 定义三个正式包：

- `FileCheck-v0.2.3-gui-x64.zip`；
- `FileCheck-v0.2.3-cli-x64.zip`；
- `FileCheck-v0.2.3-cli-x86.zip`。

GUI 包内还包含高级 CLI，并复用同一个 portable root。

正式包包括：

- EXE；
- config；
- portable Everything / ES；
- runtime；
- scan-results；
- SHA256SUMS；
- THIRD-PARTY-NOTICES。

【截图占位 FC-10｜GitHub Release v0.2.3】

【截图占位 FC-11｜便携包目录树】

---

# 12. CI/CD：不仅是 pytest

案例中要展示：

```text
Commit
→ Regression
→ Compatibility
→ GUI Smoke
→ PyInstaller
→ EXE Smoke
→ Bundle Tools
→ Package Validation
→ Checksum
→ Release
```

【图示占位 FC-12｜Build / Release Pipeline】

核心观点：

> **对本地客户端而言，能够生成代码远远不等于能够交付。**

---

# 13. 课堂现场 Demo

建议选择一个低风险小增量。

例如：

> 给扫描结果增加一个新的显示/过滤行为。

完整走：

```text
Requirement
→ Read Requirements
→ Read GUI Design
→ Inspect Core
→ Plan
→ Implement
→ pytest
→ GUI Smoke
→ Launch
→ Screenshot
→ Diff
```

【录屏占位 FC-R01｜FileCheck 小需求完整 Agent Loop】

第二个预录：

```text
Test Source
→ Backup
→ Manifest
→ Verify
→ Restore
→ Hash Match
```

【录屏占位 FC-R03｜受控测试数据 Backup / Verify / Restore】

如果要演示删除，只使用明确可销毁的测试目录，并优先使用预录。

---

# 14. 人在 FileCheck 中承担什么

- 定义“候选不等于最终判断”；
- 确定扫描范围；
- 核对结果；
- 确定高风险操作边界；
- 选择兼容平台；
- 决定是否接受技术路线；
- 真实 Windows 环境验收；
- 决定 Release。

这再次证明：

> **Agent 可以承担大量工程执行，但不能替代业务、安全和最终发布责任。**

---

# 15. FileCheck 最终沉淀的资产

- README / Requirements；
- Architecture；
- GUI Design System；
- Core；
- CLI；
- GUI；
- tests；
- selftest；
- CI；
- packaging；
- release artifacts；
- checksums；
- compatibility rules。

所以最终案例结论：

> **一个 Agent 工程项目的可复用价值，远大于最终源代码本身。**

---

# 16. 待采集证据

## P0 截图

- [ ] FC-01 GUI + CLI；
- [ ] FC-02 Requirements / Non-goals；
- [ ] FC-03 Constraint 图；
- [ ] FC-04 Core → CLI / GUI；
- [ ] FC-05 selftest；
- [ ] FC-06 Safety Flow；
- [ ] FC-07 主要 GUI 页面；
- [ ] FC-08 Danger Confirm；
- [ ] FC-09 CI；
- [ ] FC-10 Release；
- [ ] FC-11 Package Tree；
- [ ] FC-12 Pipeline。

## P0 录屏

- [ ] FC-R01 小需求 Agent Loop；
- [ ] FC-R02 Actions → Artifact / Release；
- [ ] FC-R03 测试数据 Backup → Verify → Restore。

## 历史材料

- [ ] 最初需求 / 对话；
- [ ] CLI-first 阶段对应 commit；
- [ ] GUI 加入阶段；
- [ ] Win7 compatibility 阶段；
- [ ] v0.2.2 / v0.2.3 历史备份保护演进；
- [ ] Release workflow 实际页面。

找不到历史材料时，不编造决策故事，以当前代码和 Git 可确认事实为准。
