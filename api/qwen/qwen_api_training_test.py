#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Qwen3.6 / vLLM API 培训留档测试。

依赖: pip install requests

环境变量示例:
  QWEN_BASE_URL=http://<host>:<port>
  QWEN_API_KEY=<key>
  QWEN_MODEL=qwen3.6

覆盖:
- /v1/models, /version, /metrics, /openapi.json
- /tokenize, /detokenize
- OpenAI Chat: 非流式、SSE、Thinking ON/OFF、tool_calls
- OpenAI Responses/Codex: 非流式、SSE、function_call
- Anthropic Messages/Claude: 非流式、SSE、tool_use

输出目录包含逐项请求/响应、SSE 原文、manifest.json 和 summary.md。
API Key 在落盘前自动脱敏。
"""
from __future__ import annotations

import argparse, json, os, sys, time, traceback
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

import requests


def now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def dump(x: Any) -> str:
    return json.dumps(x, ensure_ascii=False, indent=2)


def mask(text: Any, key: str) -> Any:
    if not key:
        return text
    shown = "***" if len(key) <= 8 else key[:3] + "***" + key[-3:]
    if isinstance(text, str):
        return text.replace(key, shown)
    if isinstance(text, list):
        return [mask(x, key) for x in text]
    if isinstance(text, dict):
        return {k: mask(v, key) for k, v in text.items()}
    return text


@dataclass
class Result:
    seq: int
    name: str
    category: str
    method: str
    endpoint: str
    status: str
    http_status: Optional[int]
    elapsed_ms: Optional[float]
    notes: str
    record_file: str
    stream_file: Optional[str] = None


class Tester:
    def __init__(self, base: str, key: str, model: str, out: Path, timeout: int = 180):
        base = base.rstrip("/")
        self.base = base[:-3] if base.endswith("/v1") else base
        self.key, self.model, self.out, self.timeout = key, model, out, timeout
        self.s = requests.Session()
        self.results: list[Result] = []
        self.seq = 0
        self.token_ids: list[int] = []
        self.token_text = "你好，Qwen3.6。这是一段用于 tokenizer 接口验证的中文测试文本。"

    def url(self, ep: str) -> str:
        return self.base + ep

    def headers(self, anthropic: bool = False) -> dict[str, str]:
        h = {"Content-Type": "application/json"}
        if self.key:
            h["Authorization"] = f"Bearer {self.key}"
            if anthropic:
                h["x-api-key"] = self.key
        if anthropic:
            h["anthropic-version"] = "2023-06-01"
        return h

    def next(self) -> int:
        self.seq += 1
        return self.seq

    def save(self, seq: int, name: str, req: dict, resp: dict, status: str, notes: str) -> Path:
        p = self.out / f"{seq:02d}_{name}.json"
        obj = {
            "test": name,
            "recorded_at": now(),
            "deployment": {"model": self.model, "base_url": self.base},
            "request": mask(req, self.key),
            "response": mask(resp, self.key),
            "analysis": {"status": status, "notes": notes},
        }
        p.write_text(dump(obj), encoding="utf-8")
        return p

    def record_result(self, seq, name, cat, method, ep, status, code, ms, notes, record, stream=None):
        self.results.append(Result(seq, name, cat, method, ep, status, code, ms, notes,
                                   record.name, stream.name if stream else None))
        print(f"[{status}] {seq:02d} {name} HTTP={code} elapsed={ms}ms {notes}")

    def request(self, name: str, cat: str, method: str, ep: str, body: dict | None = None,
                anthropic: bool = False,
                check: Callable[[Any], tuple[bool, str]] | None = None) -> Any:
        seq = self.next(); start = time.perf_counter()
        req = {"method": method, "url": self.url(ep), "headers": self.headers(anthropic), "json": body}
        try:
            r = self.s.request(method, self.url(ep), headers=self.headers(anthropic),
                               json=body if method == "POST" else None,
                               timeout=(10, self.timeout))
            ms = round((time.perf_counter()-start)*1000, 2)
            try: data = r.json()
            except Exception: data = r.text
            ok = 200 <= r.status_code < 300
            notes = "HTTP 2xx"
            if ok and check:
                ok, notes = check(data)
            elif not ok:
                notes = f"HTTP {r.status_code}"
            status = "PASS" if ok else "FAIL"
            response = {"status_code": r.status_code, "elapsed_ms": ms,
                        "headers": dict(r.headers), "body": data}
            rec = self.save(seq, name, req, response, status, notes)
            self.record_result(seq, name, cat, method, ep, status, r.status_code, ms, notes, rec)
            return data
        except Exception as e:
            ms = round((time.perf_counter()-start)*1000, 2)
            notes = f"{type(e).__name__}: {e}"
            rec = self.save(seq, name, req, {"elapsed_ms": ms, "exception": notes,
                            "traceback": traceback.format_exc()}, "ERROR", notes)
            self.record_result(seq, name, cat, method, ep, "ERROR", None, ms, notes, rec)
            return None

    def stream(self, name: str, cat: str, ep: str, body: dict, anthropic: bool,
               required_events: list[str], finish_markers: list[str]):
        seq = self.next(); start = time.perf_counter(); req = {
            "method":"POST", "url":self.url(ep), "headers":self.headers(anthropic), "json":body}
        raw: list[str] = []; events: list[str] = []; first_ms = None; code = None
        try:
            with self.s.post(self.url(ep), headers=self.headers(anthropic), json=body,
                             stream=True, timeout=(10,self.timeout)) as r:
                code = r.status_code
                for line in r.iter_lines(decode_unicode=True):
                    if line is None: continue
                    t = round((time.perf_counter()-start)*1000,2)
                    if line and first_ms is None: first_ms = t
                    raw.append(line)
                    if line.startswith("event:"):
                        events.append(line.split(":",1)[1].strip())
            ms=round((time.perf_counter()-start)*1000,2)
            text="\n".join(raw); missing=[x for x in required_events if x not in events]
            ok=(code is not None and 200<=code<300 and not missing and any(x in text for x in finish_markers))
            notes="流式协议与完成事件符合预期" if ok else f"missing_events={missing}"
            sp=self.out/f"{seq:02d}_{name}.sse.txt"; sp.write_text(text,encoding="utf-8")
            rec=self.save(seq,name,req,{"status_code":code,"elapsed_ms":ms,"first_data_ms":first_ms,
                                      "events":events,"raw_sse_file":sp.name},
                          "PASS" if ok else "FAIL",notes)
            self.record_result(seq,name,cat,"POST",ep,"PASS" if ok else "FAIL",code,ms,notes,rec,sp)
        except Exception as e:
            ms=round((time.perf_counter()-start)*1000,2); notes=f"{type(e).__name__}: {e}"
            rec=self.save(seq,name,req,{"exception":notes,"partial":raw},"ERROR",notes)
            self.record_result(seq,name,cat,"POST",ep,"ERROR",code,ms,notes,rec)

    def run(self):
        def models_check(d):
            if not isinstance(d,dict) or d.get("object")!="list": return False,"不是 models list"
            m=next((x for x in d.get("data",[]) if x.get("id")==self.model),None)
            return (bool(m), f"找到 {self.model}，max_model_len={m.get('max_model_len') if m else None}")
        self.request("models","基础接口","GET","/v1/models",check=models_check)
        self.request("version","基础接口","GET","/version",check=lambda d:(True,f"version={d.get('version') if isinstance(d,dict) else d}"))
        self.request("metrics","基础接口","GET","/metrics",check=lambda d:(isinstance(d,str) and ("# HELP" in d or "vllm:" in d),"Prometheus metrics 可读取"))
        self.request("openapi","基础接口","GET","/openapi.json",check=lambda d:(isinstance(d,dict) and "openapi" in d and "paths" in d,"OpenAPI schema 可读取"))

        def tok_check(d):
            self.token_ids=(d.get("tokens") or []) if isinstance(d,dict) else []
            return (bool(self.token_ids), f"count={d.get('count') if isinstance(d,dict) else None}, max_model_len={d.get('max_model_len') if isinstance(d,dict) else None}")
        self.request("tokenize","Tokenizer","POST","/tokenize",{
            "model":self.model,"prompt":self.token_text,"add_special_tokens":False,"return_token_strs":True},check=tok_check)
        if self.token_ids:
            self.request("detokenize","Tokenizer","POST","/detokenize",{"model":self.model,"tokens":self.token_ids},
                         check=lambda d:(isinstance(d,dict) and d.get("prompt")==self.token_text,"detokenize 与原文一致"))

        base_chat={"model":self.model,"messages":[{"role":"user","content":"请只回答：CHAT_OK"}],
                   "temperature":0,"max_tokens":128,"chat_template_kwargs":{"enable_thinking":False}}
        self.request("chat_nonstream","OpenAI Chat","POST","/v1/chat/completions",base_chat,
                     check=lambda d:(isinstance(d,dict) and d.get("object")=="chat.completion" and bool(d.get("choices")),"标准 chat.completion"))
        sb=dict(base_chat); sb["stream"]=True
        self.stream("chat_stream","OpenAI Chat","/v1/chat/completions",sb,False,[],["[DONE]","finish_reason"])
        puzzle="有三个盒子，标签分别为苹果、橘子、苹果和橘子，且三个标签都贴错了。只能取一个水果，如何判断？请给出答案。"
        off={"model":self.model,"messages":[{"role":"user","content":puzzle}],"temperature":0.1,"max_tokens":512,
             "chat_template_kwargs":{"enable_thinking":False}}
        self.request("chat_thinking_off","OpenAI Chat","POST","/v1/chat/completions",off,
                     check=lambda d:(d["choices"][0]["message"].get("reasoning") in (None,"") and bool(d["choices"][0]["message"].get("content")),"Thinking OFF：reasoning 为空"))
        on=dict(off); on["max_tokens"]=1024; on["chat_template_kwargs"]={"enable_thinking":True}
        self.request("chat_thinking_on","OpenAI Chat","POST","/v1/chat/completions",on,
                     check=lambda d:(bool(d["choices"][0]["message"].get("reasoning") or d["choices"][0]["message"].get("reasoning_content")),"Thinking ON：检测到 reasoning"))
        tool_schema={"type":"function","function":{"name":"get_weather","description":"查询指定城市当前天气",
                     "parameters":{"type":"object","properties":{"city":{"type":"string"}},"required":["city"],"additionalProperties":False}}}
        tb={"model":self.model,"messages":[{"role":"user","content":"查询北京天气，必须调用 get_weather 工具。"}],
            "temperature":0.1,"max_tokens":512,"chat_template_kwargs":{"enable_thinking":False},"tools":[tool_schema],"tool_choice":"required"}
        self.request("chat_tool_call","OpenAI Chat","POST","/v1/chat/completions",tb,
                     check=lambda d:(bool(d["choices"][0]["message"].get("tool_calls")),"标准 message.tool_calls[]"))

        rb={"model":self.model,"input":"请只回答：RESPONSES_OK","max_output_tokens":256,"reasoning":{"effort":"none"}}
        self.request("responses_nonstream","Codex / Responses","POST","/v1/responses",rb,
                     check=lambda d:(isinstance(d,dict) and d.get("object")=="response" and isinstance(d.get("output"),list),"标准 Responses object/output"))
        rs=dict(rb); rs["stream"]=True
        self.stream("responses_stream","Codex / Responses","/v1/responses",rs,False,["response.created","response.completed"],["response.completed"])
        rtool={"model":self.model,"input":"查询北京天气。必须调用 get_weather 工具。","max_output_tokens":512,
               "reasoning":{"effort":"none"},"tools":[{"type":"function","name":"get_weather","description":"查询指定城市当前天气",
               "parameters":{"type":"object","properties":{"city":{"type":"string"}},"required":["city"],"additionalProperties":False}}],
               "tool_choice":"required","parallel_tool_calls":False}
        self.request("responses_tool_call","Codex / Responses","POST","/v1/responses",rtool,
                     check=lambda d:(any(x.get("type")=="function_call" for x in d.get("output",[])),"Responses function_call"))

        ab={"model":self.model,"max_tokens":256,"thinking":{"type":"disabled"},
            "messages":[{"role":"user","content":"请只回答：CLAUDE_OK"}]}
        self.request("anthropic_nonstream","Claude / Anthropic","POST","/v1/messages",ab,True,
                     check=lambda d:(isinstance(d,dict) and d.get("type")=="message" and isinstance(d.get("content"),list),"标准 Anthropic message/content"))
        ast=dict(ab); ast["stream"]=True
        self.stream("anthropic_stream","Claude / Anthropic","/v1/messages",ast,True,["message_start","message_stop"],["message_stop"])
        atool={"model":self.model,"max_tokens":512,"thinking":{"type":"disabled"},
               "messages":[{"role":"user","content":"查询北京天气，必须使用 get_weather 工具。"}],
               "tools":[{"name":"get_weather","description":"查询指定城市当前天气","input_schema":{"type":"object","properties":{"city":{"type":"string"}},"required":["city"],"additionalProperties":False}}],
               "tool_choice":{"type":"any"}}
        def ac(d):
            calls=[x for x in d.get("content",[]) if isinstance(x,dict) and x.get("type")=="tool_use"] if isinstance(d,dict) else []
            return bool(calls), ("Anthropic tool_use" if calls else f"未返回 tool_use；stop_reason={d.get('stop_reason') if isinstance(d,dict) else None}")
        self.request("anthropic_tool_use","Claude / Anthropic","POST","/v1/messages",atool,True,ac)
        self.finish()

    def finish(self):
        def level(names):
            rows=[next((r for r in self.results if r.name==n),None) for n in names]
            if all(r and r.status=="PASS" for r in rows): return "PASS"
            if any(r and r.status=="PASS" for r in rows): return "PARTIAL"
            return "FAIL"
        matrix=[
            {"protocol":"OpenAI Chat Completions","status":level(["models","chat_nonstream","chat_stream","chat_tool_call"])},
            {"protocol":"Codex / OpenAI Responses","status":level(["responses_nonstream","responses_stream","responses_tool_call"])},
            {"protocol":"Claude / Anthropic Messages","status":level(["anthropic_nonstream","anthropic_stream","anthropic_tool_use"])},
        ]
        manifest={"generated_at":now(),"base_url":self.base,"model":self.model,"results":[asdict(x) for x in self.results],"support_matrix":matrix}
        (self.out/"manifest.json").write_text(dump(manifest),encoding="utf-8")
        lines=["# Qwen3.6 内网 API 兼容性测试记录","",f"- 生成时间：`{now()}`",f"- API 根地址：`{self.base}`",f"- 模型：`{self.model}`","",
               "## 协议兼容性结论","","| 协议 | 结果 |","|---|---|"]
        lines += [f"| {x['protocol']} | **{x['status']}** |" for x in matrix]
        lines += ["","## 逐项测试结果","","| # | 分类 | 测试项 | Endpoint | 结果 | HTTP | 耗时(ms) | 说明 |","|---:|---|---|---|---|---:|---:|---|"]
        lines += [f"| {r.seq} | {r.category} | {r.name} | `{r.endpoint}` | **{r.status}** | {r.http_status or ''} | {r.elapsed_ms or ''} | {r.notes.replace('|','/')} |" for r in self.results]
        (self.out/"summary.md").write_text("\n".join(lines),encoding="utf-8")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base-url",default=os.getenv("QWEN_BASE_URL",""))
    ap.add_argument("--api-key",default=os.getenv("QWEN_API_KEY",""))
    ap.add_argument("--model",default=os.getenv("QWEN_MODEL","qwen3.6"))
    ap.add_argument("--output",default="qwen_api_test_records")
    ap.add_argument("--timeout",type=int,default=180)
    a=ap.parse_args()
    if not a.base_url:
        print("请提供 --base-url 或 QWEN_BASE_URL",file=sys.stderr); return 2
    out=Path(a.output)/datetime.now().strftime("%Y%m%d_%H%M%S"); out.mkdir(parents=True,exist_ok=True)
    Tester(a.base_url,a.api_key,a.model,out,a.timeout).run()
    print(f"结果目录: {out}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
