# API Mini Apps：同一个模型接口，不只有 Chat

> 状态：Demo Spec v0.1  
> 对应讲义：`docs/lectures/01-api-to-agent.md`  
> 目标：用 3～5 分钟让学员建立“Model API 是可编程能力接口，Chat 只是其中一种 UI”的直觉。

---

# 1. 演示原则

所有 Demo 尽量固定：

- 同一个内网模型：`qwen3.6`；
- 同一个 Base URL；
- 同一套鉴权方式；
- 优先使用当前已实测通过的 OpenAI Chat / Vision 路径；
- 每个 Demo 只改变输入、Instructions 和期望输出；
- 每个 Demo 必须有 Expected Result 和程序端校验思路。

不要把这一段做成“六个新产品”。

核心只讲一句：

> **同一个模型 API，换输入和输出契约，就能嵌入不同业务流程。**

---

# 2. Demo A：文本翻译

输入：

```text
The device entered thermal protection mode after 30 seconds.
```

固定指令：

```text
翻译为简洁、准确的技术中文。只返回译文。
```

输出：

```text
设备运行 30 秒后进入热保护模式。
```

教学点：

> 没有对话历史也能调用模型；这就是一个最小“翻译 API”。

---

# 3. Demo B：非结构化文本 → JSON

输入：

```text
SN=A102，温度 86.3°C，电压 3.28V，测试结果 FAIL，错误码 TEMP_HIGH。
```

期望：

```json
{
  "sn": "A102",
  "temperature_c": 86.3,
  "voltage_v": 3.28,
  "result": "FAIL",
  "error_code": "TEMP_HIGH"
}
```

程序端必须继续做：

```text
Model Output
→ JSON Parse
→ Schema / Type Validation
→ Pass / Retry / Reject
```

教学点：

> “让模型输出 JSON”开始具备系统集成价值，但生产系统不能只靠 Prompt 保证格式。

当前内网若尚未正式验证 `response_format/json_schema`，只演示 Prompt JSON + 本地校验，不宣称 Structured Outputs 已支持。

---

# 4. Demo C：图片文字识别 / 自制验证码样式图片

准备一张自有图片：

```text
BLUE-7319
```

或自制 4～6 位字符图片。

问题：

```text
读取图片中的字符，只返回识别文本。
```

教学点：

> Vision API 可以被封装成 OCR / 标签识别，而不是必须放在聊天窗口里。

边界：

> 只使用自制/授权图片，不演示第三方 CAPTCHA 绕过。

---

# 5. Demo D：网页截图视觉 QA

准备我们自己的 Demo 网页截图，故意包含：

- 按钮被遮挡；
- 文本溢出；
- 左右间距不一致；
- 移动端布局错位。

要求模型返回：

```json
{
  "issues": [
    {
      "type": "layout",
      "region": "右上角",
      "description": "按钮与标题发生重叠",
      "suggestion": "增加容器最小高度或调整响应式断点"
    }
  ]
}
```

教学点：

> 视觉模型可以进入 UI Review / Visual QA 流程，后续 Agent 再结合 Browser、Playwright 自动复测。

---

# 6. Demo E：分类 / 路由

输入多条测试记录，让模型只返回：

```text
NORMAL
REVIEW
INVALID
```

或 JSON：

```json
{"category":"REVIEW","reason":"温度超过人工复核阈值"}
```

教学点：

> 模型可以成为业务流程中的一个判断节点，而不是面向人的聊天终点。

---

# 7. Demo F：固定格式摘要 / 报告生成

输入一段测试日志，固定输出：

```markdown
## 结论
## 异常
## 建议复核项
```

教学点：

> API 可以把重复的文本整理工作封装为稳定服务。

---

# 8. 一张图收束

```text
                Model API
                    │
      ┌─────────────┼─────────────┐
      ↓             ↓             ↓
    Chat        Translation     OCR/Vision
      ↓             ↓             ↓
 Knowledge      JSON Extract    Visual QA
      ↓             ↓             ↓
   Agent       Classification   Workflow Node
```

真正的应用通常是：

```text
业务输入
→ Preprocess
→ Prompt / Instructions
→ Model API
→ Parse / Validate
→ Business Logic
→ UI / DB / Workflow
```

而 Agent 是进一步让模型参与：

```text
Decide
→ Call Tool
→ Observe
→ Continue
→ Verify
```

---

# 9. 素材建议

- `API-APP-01`：同一 API → 多应用分叉图；
- `API-APP-02`：翻译 Request / Response；
- `API-APP-03`：文本 → JSON + 本地校验；
- `API-APP-04`：自制字符图片 → Vision 识别；
- `API-APP-05`：网页截图 → Visual QA JSON；
- `API-APP-06`：分类 / 路由；
- `API-APP-R01`：60～90 秒串联录屏，连续展示 4 个小应用。
