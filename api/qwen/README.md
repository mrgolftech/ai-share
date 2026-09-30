# Qwen3.6 内网 API / Agent / Vision 实测材料

## 当前事实来源
- **当前实测基线**：`results/20260930_095033/`
- 当前报告：`reports/qwen36_api_test_report_20260930.md`
- 培训讲义：`../../docs/chapters/01-intranet-qwen-api.md`
- 当前测试脚本：`qwen_api_training_test_v3.py`
- model-metric 案例：`../../docs/cases/model-metric-api-observability.md`
- 历史结果：`results/archive/`
- 历史报告：`reports/archive/`

## 当前结论
- 模型：`qwen3.6`；Context `131072`；vLLM `0.23.0`。
- r4：28 PASS / 1 SKIP / 0 FAIL / 0 ERROR。
- Chat / Responses / Anthropic 三套 Tool Loop PASS。
- Chat / Responses / Anthropic Vision PASS；Chat 额外通过多图、Vision SSE、Vision + Tool Calling。
- Anthropic `thinking.type=disabled` 仍存在兼容异常。
- 128K 长上下文稳定性尚未专项验证。

旧结果保留用于排障教学，不再作为当前能力结论。

模块一推荐教学顺序：`Postman → Cherry Network → Python Test → /metrics → model-metric`。