# Token 输出速率体感 Demo

> 规范位置：`demos/api-applications/token-output-speed/`，属于第一讲 API 应用体验套件。

用于“模型怎么调用”模块的现场演示，让学员直观看到不同输出吞吐（tokens/s）是什么感觉。

## 上游来源

本 Demo **不是从零实现**，基于：

- Repository: https://github.com/aaravchour/token-speed-visualiser
- Upstream commit: `52c8a7c50b78c2814395db90c1901ada79512e26`
- License: Apache-2.0

本目录保留上游 Apache-2.0 `LICENSE`。

## 培训版只做了必要改造

保留上游的核心页面结构、单速率模拟逻辑、`requestAnimationFrame` 输出节奏和 Race Mode。

培训版调整：

- 中文化界面；
- 去掉 GPT-4 / GPT-3.5 / Groq 等容易过时的固定模型速度标签；
- Race Mode 改为通用的 `5 / 30 / 120 tok/s`；
- 单速率仍保留 `1 / 5 / 10 / 20 / 50 / 100 / 200 / 500 tok/s`；
- 替换为培训相关中文示例文本；
- 去掉 Tailwind CDN、Google Fonts / Material Symbols 外部依赖，便于内网/离线现场演示；
- 增加 TTFT / Tokens/s / Total Latency 的解释。

## 使用

直接双击：

`index.html`

即可运行，不需要 npm、Python 或模型 API。

建议现场：

1. 单速率依次点击 `5 → 20 → 50 → 100 tok/s`；
2. 切到“并排对比”；
3. 同时观察 `5 / 30 / 120 tok/s`。

## 重要边界

本 Demo 是**速度体感模拟器**，不是：

- 真正的 tokenizer；
- 模型性能测试工具；
- TTFT 测试；
- 实际 API benchmark。

页面中的一个“显示 Token”采用 Unicode 字符近似，仅用于让学员快速建立速度直觉。

真实性能结论使用本仓库的 Qwen API 实测与 model-metric 数据。
