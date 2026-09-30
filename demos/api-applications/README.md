# API 应用体验套件：从 Tokens/s 体感到真实非 Chat 应用

> 状态：Runnable Demo v0.2  
> 对应讲义：`docs/lectures/01-api-to-agent.md`  
> 目标：把第一讲两个容易被割裂的认知放在一起：**模型输出速度会改变应用体验；模型 API 又远不止能做 Chat。**

---

# 0. 这一组 Demo 包含什么

```text
体验层
└─ Token 输出速率体感模拟器
   └─ token-output-speed/index.html

真实 API 应用层
├─ translate.py      技术文本翻译
├─ json_extract.py   非结构化记录 → JSON + 本地校验
├─ vision_ocr.py     自制字符图片 → Vision OCR
├─ visual_qa.py      网页截图 → Visual QA JSON
└─ run_all.py        一次连续跑完上述四项
```

两类 Demo 不要混淆：

- `token-output-speed` 是**离线速度体感模拟器**，不调用真实模型；
- 四个 Python Demo 是**真实模型 API 调用**，默认使用当前内网已实测通过的 OpenAI Chat / Vision 路径。

---

# 1. 先体验 Tokens/s：模型“开始回答以后”到底有多快

现有 Demo：

```text
demos/api-applications/token-output-speed/index.html
```

直接双击即可运行。

建议课堂顺序：

```text
5 tok/s
→ 20 tok/s
→ 50 tok/s
→ 100 tok/s
→ Race Mode: 5 / 30 / 120 tok/s
```

它的目的不是 Benchmark，而是建立体感：

> **同样一段答案，Decode 输出速度不同，人的等待体验会完全不同。**

但 Tokens/s 不能脱离 TTFT 单独看。

一个实用的近似关系：

```text
总时延
≈ TTFT
+ 输出 Token 数 / Decode Tokens/s
+ Tool / Network / Queue 等额外时间
```

其中：

- **TTFT (Time To First Token)**：按下发送后多久看到第一个 Token；
- **Decode Tokens/s**：开始输出后，每秒产生多少 Token；
- **Total Latency**：整个任务最终完成需要多久。

## 不同应用，对速度指标的敏感度不同

| 应用 | 输出通常多长 | 更敏感的指标 | 原因 |
|---|---:|---|---|
| 分类 / 路由 | 很短 | TTFT、稳定性 | 可能只输出一个标签，Decode 再快也省不了多少时间 |
| JSON 抽取 | 短 | TTFT、结构正确率 | 业务更关心尽快拿到可解析结果 |
| OCR / 标签识别 | 很短 | Vision 前处理、TTFT、正确率 | 输出字符少，Tokens/s 通常不是主要瓶颈 |
| 短文本翻译 | 短～中 | TTFT + Tokens/s | 第一屏等待和持续输出都会影响交互体验 |
| Visual QA 报告 | 中～长 | TTFT + Tokens/s | 问题列表、建议较长，Decode 会明显影响总等待 |
| 长文 / 代码生成 | 长 | Tokens/s 很重要 | 输出 Token 很多，Decode 时间占比迅速上升 |
| Agent | 多次短/中输出 | 每步 TTFT + Tool 延迟 + 累计时延 | 一次任务可能串联十几次模型/工具调用，单步延迟会累计 |

所以培训不要给学员留下：

> “Tokens/s 越高，这个模型所有应用都一定越快。”

更准确是：

> **短输出应用首先看 TTFT；长输出应用越来越受 Decode Tokens/s 影响；Agent 还要看多步累计延迟和工具执行时间。**

另外必须区分：

```text
单请求 Decode Tokens/s
≠
服务端 Aggregate Output TPS
```

前者是一个用户这一条请求的输出速度；后者是整个共享服务所有并发请求合起来的吞吐。

---

# 2. 四个 Python 应用：同一个 API，不只有 Chat

所有 Demo 尽量固定：

- 同一个内网模型：`qwen3.6`；
- 同一个 Base URL；
- 同一套鉴权方式；
- 同一个 `POST /v1/chat/completions` 路径；
- Vision 使用当前仓库 r4 已实测通过的 `image_url + data:image/...;base64` 形式；
- 每个应用只改变 Input / System Prompt / Output Contract。

依赖：

```bash
cd demos/api-applications
python -m pip install -r requirements.txt
```

推荐先使用环境变量，避免 API Key 出现在 shell history：

PowerShell：

```powershell
$env:QWEN_BASE_URL="http://<INTERNAL_HOST>:<PORT>"
$env:QWEN_API_KEY="<API_KEY>"
$env:QWEN_MODEL="qwen3.6"
```

Linux / macOS：

```bash
export QWEN_BASE_URL="http://<INTERNAL_HOST>:<PORT>"
export QWEN_API_KEY="<API_KEY>"
export QWEN_MODEL="qwen3.6"
```

也可以显式传：

```bash
python translate.py --base-url http://<INTERNAL_HOST>:<PORT> --api-key xxx
```

---

# 3. Demo A：文本翻译

```bash
python translate.py
```

默认输入：

```text
The device entered thermal protection mode after 30 seconds.
```

教学点：

> 没有 Chat UI、没有历史对话，同一个模型 API 已经可以直接成为“翻译能力”。

---

# 4. Demo B：非结构化文本 → JSON

```bash
python json_extract.py
```

默认输入：

```text
SN=A102，温度 86.3°C，电压 3.28V，测试结果 FAIL，错误码 TEMP_HIGH。
```

程序不是只打印模型答案，而是继续执行：

```text
Model Output
→ JSON Parse
→ Local Schema / Type Validation
→ PASS / FAIL
```

教学点：

> **模型输出只是中间结果，真正的业务应用还需要程序验证。**

当前内网尚未在正式 r4 矩阵中验证 `response_format/json_schema`，所以本 Demo 只使用 Prompt JSON + 本地校验，不宣称 Structured Outputs 已兼容。

---

# 5. Demo C：Vision OCR

先生成自有样例图片：

```bash
python generate_samples.py
```

再运行：

```bash
python vision_ocr.py
```

默认图片：

```text
assets/ocr-demo.png
```

Ground Truth：

```text
BLUE-7319
```

程序会自动做结果校验。

也可以换自己的授权图片：

```bash
python vision_ocr.py --image path/to/image.png --expected "YOUR-TEXT"
```

边界：

> 只用自制/授权图片，不做第三方 CAPTCHA 绕过。

---

# 6. Demo D：网页截图 Visual QA

```bash
python visual_qa.py
```

默认会生成一张“故意有布局问题”的网页样式截图：

```text
assets/ui-qa-demo.png
```

其中包含：

- CTA 与标题区域重叠；
- 长文本溢出卡片；
- 底部按钮被视口裁切。

模型被要求只返回：

```json
{
  "issues": [
    {
      "type": "layout|overflow|clipping|spacing|other",
      "region": "位置",
      "description": "可见问题",
      "suggestion": "修复建议"
    }
  ]
}
```

程序继续做 JSON 结构校验。

真实课堂也可以直接传入自己 Web 项目的截图：

```bash
python visual_qa.py --image path/to/screenshot.png
```

教学点：

> **Vision 可以成为 Visual QA 的“判断层”；后续 Agent + Browser / Playwright 再负责操作、修改和复测。**

---

# 7. 一次连续跑完四个真实 API 应用

```bash
python run_all.py
```

输出顺序：

```text
Translation
→ JSON Extraction + Validation
→ Vision OCR + Ground Truth
→ Visual QA + JSON Validation
```

脚本会在开头打印 Base URL 和 Model（不会打印 API Key）。课堂录屏建议保留 Base URL / Model 配置不变，让大家直观看到：

> **变化的是 Input / Prompt / Output Contract，而不是换了四个模型。**

---

# 8. 建议现场演示节奏

第一段，约 1 分钟：

```text
Token 输出速率模拟器
5 → 20 → 50 → 100 tok/s
```

讲清：

> TTFT 决定“多久开始”，Tokens/s 决定“开始后多快”，Total Latency 决定“最终多久完成”。

第二段，约 1～2 分钟：

```text
python run_all.py
```

连续跑四种非 Chat 应用。

最后用一张图收束：

```text
                 Model API
                    │
      ┌─────────────┼────────────────┐
      ↓             ↓                ↓
    Chat        Translation       Vision/OCR
      │             │                │
      ├─ Knowledge  ├─ JSON Extract  ├─ Visual QA
      │             └─ Classification│
      └─ Agent                         └─ Workflow
```

核心结论：

> **Chat 是一种交互界面；API 才是把模型能力嵌入应用和流程的工程接口。**

---

# 9. 与正式实测的边界

这组 Python Demo 是教学应用，不替代正式兼容性测试。

正式证据仍以：

```text
api/qwen/qwen_api_training_test_v3.py
api/qwen/results/20260930_095033/
api/qwen/reports/qwen36_api_test_report_20260930.md
```

为准。

速度体感模拟也不替代 model-metric / API Benchmark。

因此第一讲形成三层：

```text
Token Speed Demo
→ 建立人的速度体感

Python Mini Apps
→ 建立“API 不只是 Chat”的应用直觉

Qwen Test + model-metric
→ 给出真实兼容性与性能证据
```
