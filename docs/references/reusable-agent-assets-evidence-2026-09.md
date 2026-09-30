# 可复用 Agent 工程资产：证据基线（2026-09）

> 用途：支撑 `docs/chapters/07-reusable-agent-assets.md`。  
> 核实日期：2026-09-30。  
> 原则：区分开放格式、具体 Harness 实现、当前产品行为与本培训教学框架。

---

## 1. AGENTS.md：开放项目指令格式

来源：

- https://agents.md/

当前官网将 AGENTS.md 描述为：

- 面向 coding agents 的开放格式；
- 类似“给 Agent 的 README”；
- 适合放 build steps、tests、conventions 等项目上下文；
- 支持 monorepo 中 nested AGENTS.md；
- 标准 Markdown，不要求固定字段。

培训可据此稳定讲：

> **AGENTS.md 适合承载显式、项目级、可版本管理的 Agent 指令。**

但具体某个 Harness 是否自动发现、怎样合并、优先级如何，应按产品实现确认。

---

## 2. Codex 当前 AGENTS.md 行为

来源：

- https://developers.openai.com/api/docs/guides/latest-model

当前 OpenAI 文档说明 Codex CLI 会：

- 从全局目录和 repo root → CWD 的路径发现 AGENTS.md；
- 以 root-to-leaf 方式合并；
- 更深目录的规则可覆盖更上层规则；
- 注入到对话 Context。

培训可以据此说明：

> **项目规则会占用并影响 Context，因此不应该无限膨胀。**

---

## 3. OpenAI 2026-09 对“过度指令”的最新提醒

来源：

- https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra

该文明确建议重新审视：

- skills；
- AGENTS.md；
- task prompts。

核心方向包括：

- 不要为了每个小任务要求读取全部架构文档；
- 项目规则应指出“什么任务需要读什么资料”；
- 旧模型时代积累的过度 scaffolding 可能对更强模型造成过约束；
- 需要持续清理和更新规则。

这支持本章的核心观点：

> **资产不是越多越好；更重要的是相关、最新、按需加载。**

---

## 4. Skills：按需加载的程序性知识

来源：

- https://developers.openai.com/api/docs/guides/tools-skills

当前 OpenAI 文档明确：

- Skill 是包含 `SKILL.md` 的目录；
- 用于 reusable instructions / process / conventions；
- 可有 supporting files；
- Agent 可先看到 Skill name / description / path；
- 决定使用时再读取完整 Skill。

培训可据此讲：

> **Skill 适合承载比项目常驻规则更长、更专项的流程知识，并按需加载。**

---

## 5. Plan / ExecPlan

来源：

- https://developers.openai.com/cookbook/articles/codex_exec_plans

OpenAI Cookbook 提供：

- 在 AGENTS.md 中定义复杂任务什么时候使用 ExecPlan；
- 用独立 PLANS.md 定义长任务计划格式。

培训中应明确：

> **Plan 是复杂任务状态和执行契约的一种资产形式，不要求所有小任务都使用。**

---

## 6. Hermes：Memory / Project Context / Skill 的清晰实现案例

### 6.1 Which File Does What

来源：

- https://hermes-agent.nousresearch.com/docs/user-guide/which-file-does-what

当前 Hermes 文档区分：

- SOUL.md：Agent identity；
- USER.md：用户资料；
- MEMORY.md：Agent 学到的小型持久事实；
- AGENTS.md / .hermes.md：项目指令。

这证明：

> **Identity、User Profile、Memory、Project Instructions 是不同问题，不应混成一个“记忆文件”。**

### 6.2 Persistent Memory

来源：

- https://hermes-agent.nousresearch.com/docs/user-guide/features/memory/

当前 Hermes 为 MEMORY.md / USER.md 设置明确字符上限，并把它们作为 session-start frozen snapshot 注入。

文档也明确建议跳过：

- 大型原始数据；
- 临时 session 信息；
- 已经存在于 context files 的内容。

这支持：

> **Memory 应小而精选，不适合作为大型事实库。**

### 6.3 Skills System

来源：

- https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/

Hermes 当前把：

- Memory 视作小型持久事实；
- Skills 视作更长、按需加载的 procedural memory。

这是“Memory vs Skill”边界的一个具体产品案例，不外推为所有 Agent 统一实现。

---

## 7. 本仓库已有的资产证据

当前 `ai-share` 已有：

- `AGENTS.md`：工作规则；
- `docs/outline/training-outline.md`：内容 Source of Truth；
- `docs/chapters/`：完整讲义；
- `docs/references/`：外部证据；
- `api/qwen/results/`：实测原始结果；
- `api/qwen/reports/`：实测报告；
- `.github/workflows/api-test-script-check.yml`：自动验证；
- `demos/`：可重复教学 Demo。

因此本章可以把仓库本身作为“从聊天到工程资产”的主案例，而不是虚构示例。

---

## 8. 本章教学框架的事实边界

以下分类属于本培训为了帮助学员做工程判断而建立的教学框架：

- 资产路由表；
- Always-on / On-demand / Executable；
- Prompt → Rule → Skill → Script/Test/CI 的“稳定化方向”。

它们不是行业正式标准。

尤其要避免：

> 每一个 Prompt 都必须最终升级成 Skill/CI。

正确表达：

> **随着流程稳定度增加，可以减少模型自由度，把确定性部分下沉到代码、测试和自动化。**

---

## 9. 当前待补证据

1. `ai-share` 根目录资产地图截图；
2. AGENTS.md 实际被某个 Harness 读取与遵守的 Tool Trace；
3. 长 Prompt → Skill 的同任务前后对比；
4. Skill 调用 Script / Test 的完整实例；
5. Asset 更新 → Git Diff → Review → Commit 的录屏；
6. 内网 qwen3.6 对“精简 vs 臃肿项目指令”的受控对比（可选，不急于当前阶段）。
