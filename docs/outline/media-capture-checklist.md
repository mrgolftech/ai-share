# 培训截图与录屏总控

> 日期：2026-09-30  
> 状态：Master Media Index v2.0  
> 作用：统一规范、四讲入口、跨讲复用素材索引。  
> 说明：**每场讲座的具体截图、录屏、Demo、优先级和状态，统一在对应讲义的独立素材清单中维护。**

---

# 1. 四讲素材清单入口

| 场次 | 讲义 | 对应素材清单 |
|---|---|---|
| 第一讲 | `docs/lectures/01-api-to-agent.md` | `docs/lectures/01-api-to-agent-media-checklist.md` |
| 第二讲 | `docs/lectures/02-department-knowledge-base.md` | `docs/lectures/02-department-knowledge-base-media-checklist.md` |
| 第三讲 | `docs/lectures/03-agent-common-runtime-tools.md` | `docs/lectures/03-agent-common-runtime-tools-media-checklist.md` |
| 第四讲 | `docs/lectures/04-agent-engineering-practice.md` | `docs/lectures/04-agent-engineering-practice-media-checklist.md` |

原则：

> **一讲一稿、一讲一清单。**

正文：

> 决定“为什么需要这份素材、应该插在哪里”。

独立素材清单：

> 决定“具体拍什么、怎么拍、优先级、状态和备用方案”。

---

# 2. 优先级与状态

优先级：

- **P0**：培训必须准备；实时 Demo 失败时也必须有截图或预录兜底。
- **P1**：强烈建议；明显提升理解，可根据时长裁剪。
- **P2**：可选；用于扩展讨论或深入案例。

状态统一使用：

- ⬜ 未准备
- 🟨 已采集，待裁剪 / 标注 / 脱敏
- ✅ 可直接用于培训 / PPT

状态只在各场独立素材清单中更新，本文件不重复维护明细状态。

---

# 3. 截图统一规范

- 优先 16:9 桌面环境；
- 原始截图尽量保留 1920×1080 或更高；
- 浏览器 / 客户端缩放保持一致；
- 投影环境下必须能读清关键字段；
- 关闭通知、个人账号、无关窗口；
- API Key、Token、Cookie、SSH Key、真实敏感地址和业务数据必须脱敏；
- 同组对比固定模型、问题、资料和条件；
- 真实界面优先于概念图；
- 概念图只能用于真实界面无法表达的机制；
- 官方资料必须标注“官方资料”，不得写成“我们的实测”。

命名：

```text
<素材编号>-<简短说明>.png
```

例如：

```text
API-NET-04C-context-diff.png
WB-COMP-04C-openwebui-workspace-model.png
FC-08-danger-confirm.png
```

---

# 4. 录屏统一规范

- 原始录屏优先 1920×1080；
- 鼠标指针保留；
- 一个录屏尽量只回答一个教学问题；
- Tool Call、Terminal、Diff、Test、Browser、Logs 等过程证据优先保留；
- 长时间 Thinking / Build / Install 等等待后期剪掉，但原始录像保留；
- 不通过剪辑制造不存在的性能差异；
- 对比 Demo 固定模型、Prompt、Corpus、环境；
- 网络、模型排队、Browser、SSH、Build、GitHub Actions、生产环境等高不确定 Demo 必须有预录；
- 高风险操作优先使用受控测试环境和预录。

命名：

```text
<素材编号>-<简短说明>.mp4
```

---

# 5. 跨讲复用素材

有些素材会在两场承担不同教学目的，不重复拍摄原始素材。

| 素材 | 主要场次 | 复用方式 |
|---|---|---|
| Cherry Knowledge | 第一讲 / 第二讲 | 第一讲讲“如何进入 Context”；第二讲讲 Retrieval 设计 |
| Open WebUI Note / Workspace | 第一讲 / 第二讲 | 第一讲讲应用封装；第二讲讲个人知识、Full Context、Focused Retrieval 和治理 |
| Qwen API 测试报告 | 第一讲 / 第二讲 | 第一讲做 API 实测；第二讲做知识库同源 Corpus |
| model-metric | 第一讲 / 第四讲 | 第一讲讲服务观测；第四讲讲语义验证 |
| AGENTS.md | 第三讲 / 第四讲 | 第三讲讲 Project Rules；第四讲讲真实工程约束 |
| BMQuiz Browser / Server | 第三讲 / 第四讲 | 第三讲讲 Tool；第四讲讲工程闭环 |
| API → MCP → Skill | 第三讲 / 第四讲 | 第三讲讲机制；第四讲作为工程资产化方法补充 |

原则：

> **一个原始素材文件可以多场复用，但每场素材清单分别说明它承担的教学任务。**

---

# 6. 素材目录建议

后续实际文件建议按场次落盘：

```text
media/
├─ lecture-01/
│  ├─ screenshots/
│  ├─ recordings/
│  └─ diagrams/
├─ lecture-02/
│  ├─ screenshots/
│  ├─ recordings/
│  └─ diagrams/
├─ lecture-03/
│  ├─ screenshots/
│  ├─ recordings/
│  └─ diagrams/
└─ lecture-04/
   ├─ screenshots/
   ├─ recordings/
   └─ diagrams/
```

跨讲复用素材保留一个原始文件，不复制多份；在需要的场次清单中引用同一个素材编号。

---

# 7. 每场素材生产流程

```text
读本场讲义
↓
打开本场素材清单
↓
先完成 P0 静态截图
↓
再录 P0 动态闭环
↓
脱敏 / 裁剪 / 标注
↓
更新状态
↓
检查 Demo 备用
↓
进入 PPT 页级设计
```

不要先把所有截图都拍完再想 PPT。

更合理的是：

> **每完成一场 P0 素材，就可以开始这一场的 PPT 故事线。**

---

# 8. 当前生产重点

当前建议顺序：

1. 第一讲：Cherry 三协议、GET/POST、Qwen r4 自动测试、model-metric、Cherry/Open WebUI 工作台；
2. 第二讲：同源 Knowledge Demo、Full Context / Focused Retrieval、BM25/Vector/Hybrid、版本冲突、ACL；
3. 第三讲：多 Agent 共性、Runtime、Browser、API→MCP→Skill；
4. 第四讲：BMQuiz、FileCheck 两个纵向案例，其后再补 model-metric / IPsec / HyperFrames。

最终原则：

> **真实证据优先；完整故事优先；两个扎实 Demo 胜过十个浅演示。**
