# 案例：从 API 调用到运行观测——model-metric

> 项目：`mrgolftech/model-metric`  
> 2026-09-30 读取仓库 HEAD：`562c587be2bf4d2a77f59c16fcd5e929756cb3b5`  
> 当前源码 FastAPI version：`2.3.2`  
> 部署状态：已在部门内网上线（现场演示以实际页面/版本为准）。

## 1. 为什么放进 API 章节
Postman/Python 回答“这一条请求能不能正确调用”；`/metrics` 和 model-metric 回答“共享模型服务持续运行时到底发生了什么”。

```text
Postman GET/POST
→ Cherry Studio Network
→ Python 自动验收
→ vLLM /metrics
→ model-metric 采集/聚合/时序
→ 并发、排队、TTFT、TPS、KV、实例覆盖
→ API Benchmark / Context Window / Endpoint Compatibility
```

## 2. 当前仓库实际能力
- FastAPI + SQLite WAL；Vue3 + Element Plus + ECharts。
- `/api/overview`、`/api/instances`、并发/吞吐/Token/KV/Latency 时序。
- WebSocket `/ws/realtime`。
- direct 多实例聚合与 `gateway-estimate` 覆盖率。
- 每实例 Counter 差分得到 service TPS，避免生命周期累计值形成假峰。
- TTFT/E2E/Queue/Prefill/Decode/TPOT/ITL 使用 Histogram 差分加权。
- KV Cache 明确是 vLLM cache block 使用率，不等于 Ascend HBM。
- 当前源码包含 `/api/test-batch`、Context Window 验证和 Endpoint Compatibility 相关实现与测试。

## 3. 单请求与服务指标不要混为一谈
Chat Response 的 `usage` 是单请求 Token；客户端可测单请求 TTFT/tokens/s。
`/metrics`/model-metric 是服务侧 running/waiting、聚合 Token rate、KV、延迟 Histogram、实例覆盖。

> **单请求输出速率 ≠ 整个服务聚合 output TPS。**

## 4. 现场 Demo
1. 自编 Postman：`GET /v1/models`。
2. 自编 Postman：`POST /v1/chat/completions`。
3. Cherry Network 对照同类真实请求。
4. `qwen_api_training_test_v3.py` 展示自动断言。
5. model-metric 总览观察请求前后 running/waiting/TPS/KV。
6. model-metric API Benchmark 演示并发、TTFT、吞吐。
7. Context Window / Endpoint Compatibility 对应回前面的 API 概念。

## 5. 素材占位
- `MM-01`：内网 model-metric 总览。
- `MM-02`：API Benchmark。
- `MM-03`：Context Window / Endpoint Compatibility。
- `MM-R01`：Postman 发请求 → model-metric 指标变化。
- `MM-R02`：Benchmark 产生负载 → 实时总览变化。