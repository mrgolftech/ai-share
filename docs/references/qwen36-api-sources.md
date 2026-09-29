# Qwen3.6 API 培训参考资料

> 用途：记录本章使用的官方资料。当前内网能力判断仍以 2026-09-29 本地实测为最高优先级。

## Qwen 官方

### Qwen3.6-35B-A3B Model Card

https://huggingface.co/Qwen/Qwen3.6-35B-A3B

本章用于确认：

- 模型类型：Causal Language Model with Vision Encoder；
- 35B 总参数、约 3B 激活参数；
- MoE 专家数量与激活专家配置；
- 官方原生 Context Length 262,144；
- vLLM Tool Calling 推荐配置；
- Thinking / Non-Thinking 相关说明。

### Qwen3.6-35B-A3B config.json

https://huggingface.co/Qwen/Qwen3.6-35B-A3B/blob/main/config.json

本章用于交叉确认：

- max_position_embeddings = 262144；
- num_experts = 256；
- num_experts_per_tok = 8；
- Vision Encoder 配置存在。

## vLLM 官方

### Online Serving

https://docs.vllm.ai/en/latest/serving/online_serving/

本章用于确认 vLLM 当前服务接口体系，包括：

- /v1/chat/completions；
- /v1/responses；
- /v1/messages；
- /tokenize；
- /detokenize；
- OpenAI-compatible 与 Anthropic-compatible 服务能力。

### Claude Code Integration

https://docs.vllm.ai/en/stable/serving/integrations/claude_code/

用于后续 Claude Code 实机接入测试。官方文档明确指出 Claude Code 对模型 Tool Calling 能力有要求。

## 本地最高优先级证据

- api/qwen/results/20260929_105316/evidence.md
- api/qwen/results/20260929_105316/summary.md
- api/qwen/results/20260929_105316/manifest.json
- api/qwen/qwen_api_training_test.py

## 资料使用原则

对培训中的每一个结论，优先判断它属于哪一类：

1. **官方模型能力**：引用 Qwen 官方模型卡/配置。
2. **推理服务框架能力**：引用 vLLM 官方文档。
3. **当前内网部署能力**：引用我们自己的 Request / Response / Metrics 实测。
4. **尚未验证的推测**：明确标注为待验证，不写成确定事实。

特别注意：官方模型 262K Context 不能直接写成“内网服务支持 262K”，因为当前 /v1/models 实测只暴露 131072。
