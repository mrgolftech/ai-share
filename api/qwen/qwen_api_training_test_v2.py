#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen3.6 / vLLM 全面 API + Agent + Vision 测试脚本 v2

依赖:
    pip install requests pillow

默认覆盖:
- /v1/models, /version, /metrics, /openapi.json
- /tokenize, /detokenize, /v1/messages/count_tokens
- OpenAI Chat: 非流式、SSE、Thinking ON/OFF、Tool Call、Tool Result 闭环
- OpenAI Responses/Codex: 非流式、SSE、Function Call、Function Output 闭环
- Anthropic Messages: 非流式、SSE、Tool Use、Tool Result 闭环
- Vision:
  * 自动生成 Ground Truth PNG
  * OpenAI Chat 单图 Base64
  * Vision SSE
  * 多图
  * 图像 + Tool Calling
  * Responses input_image
  * Anthropic Base64 image
- 可选公网 image_url
- 可选长上下文

输出:
qwen_api_test_records_v2/<timestamp>/
  summary.md
  manifest.json
  environment.json
  assets/*.png
  records/*.json
  streams/*.sse.txt
  long_context/*.txt

安全:
- API Key 落盘时自动打码
- Base64 图片不重复写入 JSON 日志，只记录 SHA256/大小
- 内网地址仍保存在本地测试包中，提交公开 GitHub 前需再次脱敏
"""

from __future__ import annotations
import argparse, base64, hashlib, json, os, platform, re, sys, time, traceback
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

import requests
from PIL import Image, ImageDraw, ImageFont

DEFAULT_MODEL = "qwen3.6"
DEFAULT_CONTEXT = 131072
DEFAULT_TIMEOUT = 240

def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def js(x):
    return json.dumps(x, ensure_ascii=False, indent=2)

def sha_bytes(b: bytes):
    return hashlib.sha256(b).hexdigest()

def sha_text(s: str):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def masked(s: str):
    if not s: return ""
    return "***" if len(s) <= 8 else s[:3] + "***" + s[-3:]

def redact(x: Any, secret: str) -> Any:
    if isinstance(x, dict):
        out = {}
        for k, v in x.items():
            if k == "data" and isinstance(v, str) and len(v) > 1000:
                try:
                    raw = base64.b64decode(v)
                    out[k] = f"<BASE64_IMAGE_OMITTED bytes={len(raw)} sha256={sha_bytes(raw)}>"
                except Exception:
                    out[k] = f"<LARGE_DATA_OMITTED chars={len(v)}>"
            else:
                out[k] = redact(v, secret)
        return out
    if isinstance(x, list):
        return [redact(v, secret) for v in x]
    if isinstance(x, str):
        s = x.replace(secret, masked(secret)) if secret else x
        if s.startswith("data:image/") and ";base64," in s:
            head, b64 = s.split(";base64,", 1)
            try:
                raw = base64.b64decode(b64)
                return f"{head};base64,<OMITTED bytes={len(raw)} sha256={sha_bytes(raw)}>"
            except Exception:
                return f"{head};base64,<OMITTED>"
        if len(s) > 30000:
            return f"<LONG_TEXT_OMITTED chars={len(s)} sha256={sha_text(s)}>\nHEAD:{s[:500]}\n...\nTAIL:{s[-500:]}"
        return s
    return x

def font(size=54):
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for p in candidates:
        try:
            if Path(p).exists():
                return ImageFont.truetype(p, size)
        except Exception:
            pass
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()

def make_assets(out: Path):
    out.mkdir(parents=True, exist_ok=True)
    f, fs = font(54), font(30)

    a = Image.new("RGB", (1200, 800), "white")
    d = ImageDraw.Draw(a)
    d.text((45, 35), "AI TEST 2026", fill="black", font=f)
    for box in [(120,220,300,400),(390,220,570,400),(660,220,840,400)]:
        d.ellipse(box, fill=(230,30,30), outline="black", width=5)
    for box in [(135,520,295,680),(405,520,565,680)]:
        d.rectangle(box, fill=(30,90,230), outline="black", width=5)
    d.polygon([(900,685),(1130,685),(1015,465)], fill=(20,175,75), outline="black")
    d.text((855,720), "BOTTOM RIGHT", fill="black", font=fs)
    p1 = out / "vision_test_1.png"
    a.save(p1)

    b = Image.new("RGB", (1200, 800), "white")
    d = ImageDraw.Draw(b)
    d.text((45,35), "SECOND IMAGE", fill="black", font=f)
    for i in range(4):
        x = 120 + i * 230
        d.rectangle((x,240,x+150,390), fill=(145,60,190), outline="black", width=5)
    d.ellipse((470,500,730,760), fill=(245,145,30), outline="black", width=5)
    p2 = out / "vision_test_2.png"
    b.save(p2)

    def item(path, truth):
        raw = path.read_bytes()
        return {"path":str(path),"filename":path.name,"bytes":len(raw),
                "sha256":sha_bytes(raw),"b64":base64.b64encode(raw).decode(),
                "truth":truth}
    return {
        "image1": item(p1, {"text":"AI TEST 2026","red_circles":3,"blue_squares":2,
                           "green_triangle_position":"bottom-right"}),
        "image2": item(p2, {"text":"SECOND IMAGE","purple_squares":4,"orange_circles":1}),
    }

def parse_json_text(s: str):
    if not s: return None
    t = s.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.I)
    t = re.sub(r"\s*```$", "", t)
    try:
        o = json.loads(t)
        return o if isinstance(o, dict) else None
    except Exception:
        a, b = t.find("{"), t.rfind("}")
        if a >= 0 and b > a:
            try:
                o = json.loads(t[a:b+1])
                return o if isinstance(o, dict) else None
            except Exception:
                pass
    return None

def pos(v):
    s = str(v or "").lower().replace("_","-").replace(" ","-")
    if "右下" in s or ("bottom" in s and "right" in s):
        return "bottom-right"
    return s

def vision_check(obj):
    if not isinstance(obj, dict):
        return False, "未得到可解析 JSON", {}
    ok = (obj.get("red_circles") == 3 and obj.get("blue_squares") == 2
          and pos(obj.get("green_triangle_position")) == "bottom-right"
          and "AI TEST 2026" in str(obj.get("text","")).upper())
    return ok, ("Vision Ground Truth 全部匹配" if ok else f"Vision Ground Truth 不完全匹配: {obj}"), obj

@dataclass
class Result:
    seq: int
    name: str
    category: str
    endpoint: str
    status: str
    http_status: Optional[int]
    elapsed_ms: Optional[float]
    ttft_ms: Optional[float]
    notes: str
    record_file: str
    stream_file: Optional[str] = None
    facts: Optional[dict] = None

class Suite:
    def __init__(self, base, key, model, out, timeout, verify_tls, context_len,
                 remote_url="", long_targets=None):
        base = base.rstrip("/")
        self.base = base[:-3] if base.endswith("/v1") else base
        self.key, self.model, self.out = key, model, out
        self.timeout, self.verify_tls, self.context_len = timeout, verify_tls, context_len
        self.remote_url, self.long_targets = remote_url, long_targets or []
        self.records, self.streams, self.assets_dir = out/"records", out/"streams", out/"assets"
        for p in [self.records,self.streams,self.assets_dir]: p.mkdir(parents=True, exist_ok=True)
        self.assets = make_assets(self.assets_dir)
        self.s = requests.Session()
        self.seq = 0
        self.results = []
        self.detok_ids = []
        self.token_text = "你好，Qwen3.6。这是一段用于 tokenizer 接口验证的中文测试文本。"
        self.chat_call = None
        self.resp_call = None
        self.anth_call = None
        if not verify_tls:
            try: requests.packages.urllib3.disable_warnings()
            except Exception: pass

    def url(self, ep): return self.base + ep
    def oh(self):
        h={"Content-Type":"application/json"}
        if self.key: h["Authorization"]="Bearer "+self.key
        return h
    def ah(self):
        h={"Content-Type":"application/json","anthropic-version":"2023-06-01"}
        if self.key:
            h["Authorization"]="Bearer "+self.key
            h["x-api-key"]=self.key
        return h
    def next(self):
        self.seq += 1; return self.seq

    def save(self, seq, name, req, resp, status, notes, facts=None):
        p=self.records/f"{seq:02d}_{name}.json"
        p.write_text(js({"test":name,"recorded_at":now_iso(),
                         "deployment":{"base_url":self.base,"model":self.model,
                         "declared_context_length":self.context_len},
                         "request":redact(req,self.key),"response":redact(resp,self.key),
                         "analysis":{"status":status,"notes":notes,"facts":facts or {}}}),
                     encoding="utf-8")
        return p

    def add(self, seq,name,cat,ep,status,code,elapsed,ttft,notes,rec,stream=None,facts=None):
        self.results.append(Result(seq,name,cat,ep,status,code,elapsed,ttft,notes,
                                   rec.name,stream.name if stream else None,facts))
        print(f"[{status:<5}] {seq:02d} {name:<31} HTTP={str(code):<4} "
              f"elapsed={str(elapsed):<10} ttft={str(ttft):<10} {notes}")

    def skip(self,name,cat,ep,notes):
        seq=self.next(); req={"method":"POST","url":self.url(ep),"skipped":True}
        rec=self.save(seq,name,req,{"skipped":True},"SKIP",notes)
        self.add(seq,name,cat,ep,"SKIP",None,None,None,notes,rec)

    def request(self,name,cat,method,ep,body=None,headers=None,check=None):
        seq=self.next(); headers=headers or self.oh()
        req={"method":method,"url":self.url(ep),"headers":headers,"json":body}
        t=time.perf_counter()
        try:
            r=self.s.request(method,self.url(ep),headers=headers,
                             json=body if method=="POST" else None,
                             timeout=(15,self.timeout),verify=self.verify_tls)
            ms=round((time.perf_counter()-t)*1000,2)
            try: data=r.json()
            except Exception: data=r.text
            ok=200<=r.status_code<300; notes="HTTP 2xx"; facts={}
            if ok and check:
                try: ok,notes,facts=check(data,r)
                except Exception as e: ok=False; notes=f"判定异常: {e}"
            elif not ok: notes=f"HTTP {r.status_code}"
            status="PASS" if ok else "FAIL"
            rec=self.save(seq,name,req,{"status_code":r.status_code,"elapsed_ms":ms,
                          "headers":dict(r.headers),"body":data},status,notes,facts)
            self.add(seq,name,cat,ep,status,r.status_code,ms,None,notes,rec,facts=facts)
            return data
        except Exception as e:
            ms=round((time.perf_counter()-t)*1000,2); notes=f"{type(e).__name__}: {e}"
            rec=self.save(seq,name,req,{"exception":notes,"traceback":traceback.format_exc()},
                          "ERROR",notes)
            self.add(seq,name,cat,ep,"ERROR",None,ms,None,notes,rec)
            return None

    def stream(self,name,cat,ep,body,headers,mode,events=None,markers=None,validate=None):
        seq=self.next(); req={"method":"POST","url":self.url(ep),"headers":headers,"json":body}
        t=time.perf_counter(); raw=[]; evs=[]; parts=[]; first=None; code=None
        try:
            with self.s.post(self.url(ep),headers=headers,json=body,stream=True,
                             timeout=(15,self.timeout),verify=self.verify_tls) as r:
                code=r.status_code
                for line in r.iter_lines(decode_unicode=True):
                    if line is None: continue
                    raw.append(line)
                    if not line.startswith("data:"):
                        if line.startswith("event:"): evs.append(line.split(":",1)[1].strip())
                        continue
                    p=line.split(":",1)[1].strip()
                    if p=="[DONE]": continue
                    try: o=json.loads(p)
                    except Exception: continue
                    piece=""
                    if mode=="chat":
                        try: piece=o["choices"][0]["delta"].get("content") or ""
                        except Exception: pass
                    elif mode=="responses" and o.get("type")=="response.output_text.delta":
                        piece=o.get("delta") or ""
                    elif mode=="anthropic" and o.get("type")=="content_block_delta":
                        d=o.get("delta") or {}
                        if d.get("type")=="text_delta": piece=d.get("text") or ""
                    if piece:
                        if first is None: first=round((time.perf_counter()-t)*1000,2)
                        parts.append(piece)
            ms=round((time.perf_counter()-t)*1000,2); text="".join(parts)
            rawtxt="\n".join(raw); missing=[x for x in (events or []) if x not in evs]
            ok=code is not None and 200<=code<300 and not missing
            if markers: ok=ok and any(x in rawtxt for x in markers)
            notes="流式协议通过"; facts={"events":evs,"reconstructed_text":text}
            if ok and validate:
                ok,n,f=validate(text); notes=n; facts.update(f)
            elif not ok: notes=f"缺少事件={missing} 或完成标记"
            sf=self.streams/f"{seq:02d}_{name}.sse.txt"; sf.write_text(rawtxt,encoding="utf-8")
            status="PASS" if ok else "FAIL"
            rec=self.save(seq,name,req,{"status_code":code,"elapsed_ms":ms,
                          "first_content_ms":first,"events":evs,"reconstructed_text":text,
                          "raw_sse_file":sf.name},status,notes,facts)
            self.add(seq,name,cat,ep,status,code,ms,first,notes,rec,sf,facts)
            return text
        except Exception as e:
            ms=round((time.perf_counter()-t)*1000,2); notes=f"{type(e).__name__}: {e}"
            rec=self.save(seq,name,req,{"exception":notes,"partial_lines":raw},"ERROR",notes)
            self.add(seq,name,cat,ep,"ERROR",code,ms,first,notes,rec)
            return ""

    # ---- basic ----
    def basic(self):
        def mcheck(d,_):
            ms=d.get("data",[]) if isinstance(d,dict) else []
            m=next((x for x in ms if x.get("id")==self.model),None)
            return bool(m), (f"找到 {self.model}, max_model_len={m.get('max_model_len')}" if m else "未找到模型"), (m or {})
        self.request("models","基础接口","GET","/v1/models",headers=self.oh(),check=mcheck)
        self.request("version","基础接口","GET","/version",headers=self.oh(),
                     check=lambda d,_:(bool(d),f"version={d.get('version') if isinstance(d,dict) else d}",{}))
        self.metrics("before")
        def ocheck(d,_):
            paths=sorted((d.get("paths") or {}).keys()) if isinstance(d,dict) else []
            (self.out/"openapi_paths.txt").write_text("\n".join(paths),encoding="utf-8")
            ok=isinstance(d,dict) and "openapi" in d and "paths" in d
            return ok,f"OpenAPI paths={len(paths)}",{"paths":paths}
        self.request("openapi","基础接口","GET","/openapi.json",headers=self.oh(),check=ocheck)
        body={"model":self.model,"prompt":self.token_text,"add_special_tokens":False,"return_token_strs":True}
        def tcheck(d,_):
            self.detok_ids=(d.get("tokens") or []) if isinstance(d,dict) else []
            return bool(self.detok_ids),f"count={d.get('count')}, max_model_len={d.get('max_model_len')}",{"count":d.get("count")}
        self.request("tokenize","Tokenizer","POST","/tokenize",body,self.oh(),tcheck)
        if self.detok_ids:
            self.request("detokenize","Tokenizer","POST","/detokenize",
                         {"model":self.model,"tokens":self.detok_ids},self.oh(),
                         lambda d,_:(d.get("prompt")==self.token_text,"与原文一致" if d.get("prompt")==self.token_text else "与原文不一致",{}))
        self.request("anthropic_count_tokens","Claude / Anthropic","POST","/v1/messages/count_tokens",
                     {"model":self.model,"messages":[{"role":"user","content":"count tokens test"}]},self.ah(),
                     lambda d,_:(isinstance(d,dict) and isinstance(d.get("input_tokens"),int),
                                 f"input_tokens={d.get('input_tokens')}",{"input_tokens":d.get("input_tokens")}))

    def metrics(self,suffix):
        def ck(d,_):
            s=d if isinstance(d,str) else js(d)
            keys=["vllm:num_requests_running","vllm:num_requests_waiting",
                  "vllm:kv_cache_usage_perc","vllm:prefix_cache_hits_total","vllm:prompt_tokens_total"]
            found=[x for x in keys if x in s]
            return ("# HELP" in s or "vllm:" in s),f"关键指标 {len(found)}/{len(keys)}",{"found":found}
        self.request(f"metrics_{suffix}","基础接口","GET","/metrics",headers=self.oh(),check=ck)

    # ---- OpenAI Chat ----
    def chat(self):
        b={"model":self.model,"messages":[{"role":"user","content":"请只回答：CHAT_OK"}],
           "temperature":0,"max_tokens":128,"stream":False,
           "chat_template_kwargs":{"enable_thinking":False}}
        self.request("chat_nonstream","OpenAI Chat","POST","/v1/chat/completions",b,self.oh(),
                     lambda d,_:(("CHAT_OK" in ((d["choices"][0]["message"].get("content") or ""))),
                                  "chat.completion 正常",{"usage":d.get("usage")}))
        bs=dict(b); bs["stream"]=True; bs["messages"]=[{"role":"user","content":"请只回答：CHAT_STREAM_OK"}]
        self.stream("chat_stream","OpenAI Chat","/v1/chat/completions",bs,self.oh(),"chat",
                    markers=["[DONE]","finish_reason"],
                    validate=lambda t:("CHAT_STREAM_OK" in t,"流式文本正确",{"text":t}))

        puzzle="三个盒子标签全错，只能取一个水果，如何确定标签？请给出答案。"
        off={"model":self.model,"messages":[{"role":"user","content":puzzle}],"temperature":0.1,
             "max_tokens":512,"chat_template_kwargs":{"enable_thinking":False}}
        def offck(d,_):
            c=d["choices"][0]; m=c["message"]; r=m.get("reasoning") or m.get("reasoning_content")
            return (
                bool(m.get("content")) and not r,
                "Thinking OFF 检测完成",
                {"finish_reason":c.get("finish_reason"),"usage":d.get("usage"),"reasoning_present":bool(r)}
            )
        self.request("chat_thinking_off","Thinking","POST","/v1/chat/completions",off,self.oh(),offck)

        on=dict(off); on["max_tokens"]=1536; on["chat_template_kwargs"]={"enable_thinking":True}
        def onck(d,_):
            c=d["choices"][0]; m=c["message"]; r=m.get("reasoning") or m.get("reasoning_content")
            return (
                bool(r),
                "Thinking ON 检测到 reasoning" if r else "未检测到 reasoning",
                {"finish_reason":c.get("finish_reason"),"usage":d.get("usage"),"reasoning_present":bool(r)}
            )
        self.request("chat_thinking_on","Thinking","POST","/v1/chat/completions",on,self.oh(),onck)

        tool={"type":"function","function":{"name":"get_weather","description":"查询城市天气",
              "parameters":{"type":"object","properties":{"city":{"type":"string"}},
                            "required":["city"],"additionalProperties":False}}}
        tb={"model":self.model,"messages":[{"role":"user","content":"查询北京天气，必须调用 get_weather。"}],
            "max_tokens":512,"chat_template_kwargs":{"enable_thinking":False},
            "tools":[tool],"tool_choice":"required"}
        def tck(d,_):
            m=d["choices"][0]["message"]; calls=m.get("tool_calls") or []
            if not calls: return False,"没有 tool_calls",{}
            fn=calls[0]["function"]; args=json.loads(fn.get("arguments") or "{}")
            ok=fn.get("name")=="get_weather" and args.get("city") in {"北京","北京市","Beijing"}
            if ok: self.chat_call={"role":"assistant","content":m.get("content"),"tool_calls":calls}
            return ok,"Chat Tool Call 正确",{"arguments":args,"tool_call_id":calls[0].get("id")}
        self.request("chat_tool_call","OpenAI Chat / Agent","POST","/v1/chat/completions",tb,self.oh(),tck)

        if self.chat_call:
            call=self.chat_call["tool_calls"][0]; result={"city":"北京","temperature":23,"weather":"晴"}
            lb={"model":self.model,"messages":[
                {"role":"user","content":"查询北京天气，必须调用 get_weather。"},self.chat_call,
                {"role":"tool","tool_call_id":call["id"],"content":json.dumps(result,ensure_ascii=False)}],
                "max_tokens":256,"chat_template_kwargs":{"enable_thinking":False},
                "tools":[tool],"tool_choice":"auto"}
            def lck(d,_):
                m=d["choices"][0]["message"]; text=m.get("content") or ""
                ok="23" in text and ("晴" in text or "sunny" in text.lower()) and not (m.get("tool_calls") or [])
                return ok,"Chat Tool Result 闭环完成" if ok else f"闭环异常: {text}",{"text":text}
            self.request("chat_tool_result_loop","OpenAI Chat / Agent","POST","/v1/chat/completions",lb,self.oh(),lck)
        else: self.skip("chat_tool_result_loop","OpenAI Chat / Agent","/v1/chat/completions","前置 Tool Call 失败")

    # ---- Responses ----
    def responses(self):
        b={"model":self.model,"input":"请只回答：RESPONSES_OK","max_output_tokens":256,
           "reasoning":{"effort":"none"}}
        def text_of(d):
            out=[]
            for i in d.get("output",[]) if isinstance(d,dict) else []:
                if i.get("type")=="message":
                    out += [c.get("text") or "" for c in i.get("content",[]) if c.get("type")=="output_text"]
            return "".join(out)
        self.request("responses_nonstream","Codex / Responses","POST","/v1/responses",b,self.oh(),
                     lambda d,_:(d.get("object")=="response" and "RESPONSES_OK" in text_of(d),
                                 "Responses 文本正确",{"status":d.get("status"),"usage":d.get("usage")}))
        bs=dict(b); bs["stream"]=True; bs["input"]="请只回答：RESPONSES_STREAM_OK"
        self.stream("responses_stream","Codex / Responses","/v1/responses",bs,self.oh(),"responses",
                    ["response.created","response.completed"],["response.completed"],
                    lambda t:("RESPONSES_STREAM_OK" in t,"Responses SSE 文本正确",{"text":t}))

        tool={"type":"function","name":"get_weather","description":"查询城市天气",
              "parameters":{"type":"object","properties":{"city":{"type":"string"}},
                            "required":["city"],"additionalProperties":False}}
        tb={"model":self.model,"input":"查询北京天气，必须调用 get_weather。","max_output_tokens":512,
            "reasoning":{"effort":"none"},"tools":[tool],"tool_choice":"required","parallel_tool_calls":False}
        def tck(d,_):
            calls=[x for x in d.get("output",[]) if x.get("type")=="function_call"] if isinstance(d,dict) else []
            if not calls: return False,"没有 function_call",{}
            c=calls[0]; args=json.loads(c.get("arguments") or "{}")
            ok=c.get("name")=="get_weather" and args.get("city") in {"北京","北京市","Beijing"}
            if ok: self.resp_call=c
            return ok,"Responses function_call 正确",{"arguments":args,"call_id":c.get("call_id")}
        self.request("responses_tool_call","Codex / Responses","POST","/v1/responses",tb,self.oh(),tck)

        if self.resp_call:
            result={"city":"北京","temperature":23,"weather":"晴"}
            lb={"model":self.model,"input":[
                {"role":"user","content":"查询北京天气，必须调用 get_weather。"},
                self.resp_call,
                {"type":"function_call_output","call_id":self.resp_call.get("call_id"),
                 "output":json.dumps(result,ensure_ascii=False)}],
                "max_output_tokens":256,"reasoning":{"effort":"none"},"tools":[tool],"tool_choice":"auto"}
            def lck(d,_):
                txt=text_of(d); calls=[x for x in d.get("output",[]) if x.get("type")=="function_call"]
                ok="23" in txt and ("晴" in txt or "sunny" in txt.lower()) and not calls
                return ok,"Responses Tool Result 闭环完成" if ok else f"闭环异常: {txt}",{"text":txt}
            self.request("responses_tool_result_loop","Codex / Responses","POST","/v1/responses",lb,self.oh(),lck)
        else: self.skip("responses_tool_result_loop","Codex / Responses","/v1/responses","前置 function_call 失败")

    # ---- Anthropic ----
    def anthropic(self):
        b={"model":self.model,"max_tokens":384,"thinking":{"type":"disabled"},
           "messages":[{"role":"user","content":"请只回答：CLAUDE_OK"}]}
        def text_blocks(d):
            return "".join(x.get("text") or "" for x in (d.get("content") or [])
                           if isinstance(x,dict) and x.get("type")=="text")
        def ck(d,_):
            blocks=d.get("content") or []; th=sum(1 for x in blocks if x.get("type")=="thinking")
            txt=text_blocks(d); ok=d.get("type")=="message" and "CLAUDE_OK" in txt
            note="Anthropic 文本正确" + ("；disabled 后仍出现 thinking" if th else "")
            return ok,note,{"thinking_blocks":th,"thinking_disabled_effective":th==0,
                            "stop_reason":d.get("stop_reason"),"usage":d.get("usage")}
        self.request("anthropic_nonstream","Claude / Anthropic","POST","/v1/messages",b,self.ah(),ck)

        bs=dict(b); bs["stream"]=True; bs["messages"]=[{"role":"user","content":"请只回答：CLAUDE_STREAM_OK"}]
        self.stream("anthropic_stream","Claude / Anthropic","/v1/messages",bs,self.ah(),"anthropic",
                    ["message_start","message_stop"],["message_stop"],
                    lambda t:("CLAUDE_STREAM_OK" in t,"Anthropic SSE 文本正确",{"text":t}))

        tool={"name":"get_weather","description":"查询城市天气",
              "input_schema":{"type":"object","properties":{"city":{"type":"string"}},
                              "required":["city"],"additionalProperties":False}}
        tb={"model":self.model,"max_tokens":1536,"thinking":{"type":"disabled"},
            "messages":[{"role":"user","content":"查询北京天气，必须使用 get_weather。"}],
            "tools":[tool],"tool_choice":{"type":"any"}}
        def tck(d,_):
            calls=[x for x in (d.get("content") or []) if x.get("type")=="tool_use"]
            if not calls: return False,f"未返回 tool_use；stop_reason={d.get('stop_reason')}",{"usage":d.get("usage")}
            c=calls[0]; inp=c.get("input") or {}
            ok=c.get("name")=="get_weather" and inp.get("city") in {"北京","北京市","Beijing"}
            if ok: self.anth_call=c
            return ok,"Anthropic tool_use 正确",{"input":inp,"tool_use_id":c.get("id")}
        self.request("anthropic_tool_use","Claude / Anthropic","POST","/v1/messages",tb,self.ah(),tck)

        if self.anth_call:
            result={"city":"北京","temperature":23,"weather":"晴"}
            lb={"model":self.model,"max_tokens":768,"thinking":{"type":"disabled"},
                "messages":[{"role":"user","content":"查询北京天气，必须使用 get_weather。"},
                            {"role":"assistant","content":[self.anth_call]},
                            {"role":"user","content":[{"type":"tool_result",
                             "tool_use_id":self.anth_call.get("id"),
                             "content":json.dumps(result,ensure_ascii=False)}]}],
                "tools":[tool]}
            def lck(d,_):
                txt=text_blocks(d); calls=[x for x in (d.get("content") or []) if x.get("type")=="tool_use"]
                ok="23" in txt and ("晴" in txt or "sunny" in txt.lower()) and not calls
                return ok,"Anthropic Tool Result 闭环完成" if ok else f"闭环异常: {txt}",{"text":txt}
            self.request("anthropic_tool_result_loop","Claude / Anthropic","POST","/v1/messages",lb,self.ah(),lck)
        else: self.skip("anthropic_tool_result_loop","Claude / Anthropic","/v1/messages","前置 tool_use 失败")

    # ---- Vision ----
    def uri(self,n): return "data:image/png;base64,"+self.assets[n]["b64"]
    def vprompt(self):
        return ('只输出 JSON，不要解释：{"red_circles":整数,"blue_squares":整数,'
                '"green_triangle_position":"bottom-right 或其他位置","text":"顶部文字"}')

    def vision(self):
        b={"model":self.model,"messages":[{"role":"user","content":[
            {"type":"text","text":self.vprompt()},
            {"type":"image_url","image_url":{"url":self.uri("image1")}}]}],
            "temperature":0,"max_tokens":512,"chat_template_kwargs":{"enable_thinking":False}}
        def ck(d,_):
            txt=d["choices"][0]["message"].get("content") or ""; o=parse_json_text(txt)
            ok,n,f=vision_check(o); f["raw_text"]=txt
            return ok,n,f
        self.request("vision_chat_base64","Vision / OpenAI Chat","POST","/v1/chat/completions",b,self.oh(),ck)

        bs={"model":self.model,"messages":[{"role":"user","content":[
            {"type":"text","text":'只输出 JSON：{"red_circles":整数}'},
            {"type":"image_url","image_url":{"url":self.uri("image1")}}]}],
            "temperature":0,"max_tokens":128,"stream":True,
            "chat_template_kwargs":{"enable_thinking":False}}
        def sv(t):
            o=parse_json_text(t); ok=isinstance(o,dict) and o.get("red_circles")==3
            return ok,"Vision SSE 识别正确" if ok else f"Vision SSE 异常: {t}",{"parsed":o}
        self.stream("vision_chat_stream","Vision / OpenAI Chat","/v1/chat/completions",bs,self.oh(),"chat",
                    markers=["[DONE]","finish_reason"],validate=sv)

        mb={"model":self.model,"messages":[{"role":"user","content":[
            {"type":"text","text":('两张图，只输出 JSON：{"image1_red_circles":整数,'
             '"image1_text":"文字","image2_purple_squares":整数,'
             '"image2_orange_circles":整数,"image2_text":"文字"}\n第一张：')},
            {"type":"image_url","image_url":{"url":self.uri("image1")}},
            {"type":"text","text":"\n第二张："},
            {"type":"image_url","image_url":{"url":self.uri("image2")}}]}],
            "temperature":0,"max_tokens":512,"chat_template_kwargs":{"enable_thinking":False}}
        def mck(d,_):
            txt=d["choices"][0]["message"].get("content") or ""; o=parse_json_text(txt)
            ok=(isinstance(o,dict) and o.get("image1_red_circles")==3
                and "AI TEST 2026" in str(o.get("image1_text","")).upper()
                and o.get("image2_purple_squares")==4 and o.get("image2_orange_circles")==1
                and "SECOND IMAGE" in str(o.get("image2_text","")).upper())
            return ok,"多图 Ground Truth 匹配" if ok else f"多图异常: {o}",{"parsed":o}
        self.request("vision_multi_image","Vision / OpenAI Chat","POST","/v1/chat/completions",mb,self.oh(),mck)

        tool={"type":"function","function":{"name":"submit_visual_observation",
             "description":"提交测试图片观察结果",
             "parameters":{"type":"object","properties":{
                 "red_circles":{"type":"integer"},"blue_squares":{"type":"integer"},
                 "green_triangle_position":{"type":"string"},"text":{"type":"string"}},
                 "required":["red_circles","blue_squares","green_triangle_position","text"],
                 "additionalProperties":False}}}
        vb={"model":self.model,"messages":[{"role":"user","content":[
            {"type":"text","text":"观察图片，必须调用 submit_visual_observation 提交你看到的结果。"},
            {"type":"image_url","image_url":{"url":self.uri("image1")}}]}],
            "temperature":0,"max_tokens":512,"chat_template_kwargs":{"enable_thinking":False},
            "tools":[tool],"tool_choice":"required"}
        def vt(d,_):
            calls=d["choices"][0]["message"].get("tool_calls") or []
            if not calls: return False,"图片输入后无 tool_calls",{}
            fn=calls[0]["function"]; a=json.loads(fn.get("arguments") or "{}")
            ok,n,f=vision_check(a); ok=ok and fn.get("name")=="submit_visual_observation"
            return ok,"Vision + Tool Calling Ground Truth 匹配" if ok else f"Vision Tool 异常: {a}",f
        self.request("vision_chat_tool_call","Vision + Agent","POST","/v1/chat/completions",vb,self.oh(),vt)

        rb={"model":self.model,"input":[{"role":"user","content":[
            {"type":"input_text","text":self.vprompt()},
            {"type":"input_image","detail":"auto","image_url":self.uri("image1")}]}],
            "max_output_tokens":512,"reasoning":{"effort":"none"}}
        def rck(d,_):
            texts=[]
            for i in d.get("output",[]) if isinstance(d,dict) else []:
                if i.get("type")=="message":
                    texts += [c.get("text") or "" for c in i.get("content",[]) if c.get("type")=="output_text"]
            txt="".join(texts); o=parse_json_text(txt); ok,n,f=vision_check(o); f["raw_text"]=txt
            return ok,("Responses input_image 匹配" if ok else n),f
        self.request("vision_responses_base64","Vision / Responses","POST","/v1/responses",rb,self.oh(),rck)

        ab={"model":self.model,"max_tokens":768,"thinking":{"type":"disabled"},
            "messages":[{"role":"user","content":[
                {"type":"image","source":{"type":"base64","media_type":"image/png",
                                         "data":self.assets["image1"]["b64"]}},
                {"type":"text","text":self.vprompt()}]}]}
        def ack(d,_):
            txt="".join(x.get("text") or "" for x in (d.get("content") or [])
                        if x.get("type")=="text")
            o=parse_json_text(txt); ok,n,f=vision_check(o); f["raw_text"]=txt
            return ok,("Anthropic image 匹配" if ok else n),f
        self.request("vision_anthropic_base64","Vision / Anthropic","POST","/v1/messages",ab,self.ah(),ack)

        if self.remote_url:
            ub={"model":self.model,"messages":[{"role":"user","content":[
                {"type":"text","text":"用一句话描述图片。"},
                {"type":"image_url","image_url":{"url":self.remote_url}}]}],
                "max_tokens":256,"chat_template_kwargs":{"enable_thinking":False}}
            self.request("vision_remote_url","Vision / Network","POST","/v1/chat/completions",ub,self.oh(),
                         lambda d,_:(bool(d["choices"][0]["message"].get("content")),
                                     "公网 image_url 可读取",{}))
        else:
            self.skip("vision_remote_url","Vision / Network","/v1/chat/completions",
                      "默认不测公网 URL，避免把出网问题误判为 Vision 不支持")

    # ---- long context ----
    def tokenize_count(self,text):
        try:
            r=self.s.post(self.url("/tokenize"),headers=self.oh(),
                json={"model":self.model,"prompt":text,"add_special_tokens":False},
                timeout=(15,self.timeout),verify=self.verify_tls)
            d=r.json()
            return d.get("count") if isinstance(d.get("count"),int) else len(d.get("tokens") or [])
        except Exception: return None

    def long_context(self):
        if not self.long_targets: return
        ld=self.out/"long_context"; ld.mkdir(exist_ok=True)
        unit=("这是长上下文测试固定段落。The quick brown fox jumps over the lazy dog. "
              "0123456789 ABCDEFGHIJKLMNOPQRSTUVWXYZ。\n")
        for target in self.long_targets:
            if target >= self.context_len:
                self.skip(f"long_context_{target}","Long Context","/v1/chat/completions",
                          "目标达到/超过 max_model_len；需为模板和输出预留空间")
                continue
            repeats=max(10,target//25); text=unit*repeats; count=self.tokenize_count(text)
            for _ in range(3):
                if not count: break
                ratio=target/count
                if .96<=ratio<=1.04: break
                repeats=max(1,int(repeats*ratio)); text=unit*repeats; count=self.tokenize_count(text)
            fp=ld/f"target_{target}_actual_{count}.txt"; fp.write_text(text,encoding="utf-8")
            b={"model":self.model,"messages":[{"role":"user","content":text+"\n只回答：LONG_CONTEXT_OK"}],
               "temperature":0,"max_tokens":32,"chat_template_kwargs":{"enable_thinking":False}}
            def lck(d,_,target=target,count=count,fp=fp):
                txt=d["choices"][0]["message"].get("content") or ""; ok="LONG_CONTEXT_OK" in txt
                return ok,f"target={target}, tokenize_count≈{count}",{"target":target,"count":count,
                       "prompt_file":fp.name,"usage":d.get("usage")}
            self.request(f"long_context_{target}","Long Context","POST","/v1/chat/completions",b,self.oh(),lck)

    # ---- summary ----
    def status(self,n):
        r=next((x for x in self.results if x.name==n),None); return r.status if r else None
    def group(self,names):
        s=[self.status(n) for n in names]
        if all(x=="PASS" for x in s): return "PASS"
        if any(x=="PASS" for x in s): return "PARTIAL"
        if all(x in {None,"SKIP"} for x in s): return "NOT_TESTED"
        return "FAIL"
    def matrix(self):
        rows=[
          ("OpenAI Chat Text",["chat_nonstream","chat_stream"],"非流式 + SSE"),
          ("OpenAI Chat Tool Loop",["chat_tool_call","chat_tool_result_loop"],"tool_calls + tool result"),
          ("Responses / Codex",["responses_nonstream","responses_stream"],"Responses JSON + SSE"),
          ("Responses Tool Loop",["responses_tool_call","responses_tool_result_loop"],"function_call + output"),
          ("Anthropic Messages",["anthropic_nonstream","anthropic_stream"],"Message + SSE"),
          ("Anthropic Tool Loop",["anthropic_tool_use","anthropic_tool_result_loop"],"tool_use + result"),
          ("Vision / OpenAI Chat",["vision_chat_base64","vision_chat_stream","vision_multi_image"],"单图 + SSE + 多图"),
          ("Vision + Tool Calling",["vision_chat_tool_call"],"图像 -> 结构化 Tool Call"),
          ("Vision / Responses",["vision_responses_base64"],"input_image"),
          ("Vision / Anthropic",["vision_anthropic_base64"],"base64 image block"),
        ]
        if self.long_targets:
            rows.append(("Long Context",[f"long_context_{x}" for x in self.long_targets],
                         f"targets={self.long_targets}"))
        return [{"capability":a,"status":self.group(b),"basis":c} for a,b,c in rows]

    def finish(self):
        env={"generated_at":now_iso(),"python":sys.version,"platform":platform.platform(),
             "requests_version":requests.__version__,"pillow_version":getattr(Image,"__version__",None),
             "base_url":self.base,"model":self.model,"declared_context_length":self.context_len,
             "remote_url_test":bool(self.remote_url),"long_context_targets":self.long_targets,
             "assets":{k:{x:v[x] for x in ["filename","bytes","sha256","truth"]}
                       for k,v in self.assets.items()}}
        (self.out/"environment.json").write_text(js(env),encoding="utf-8")
        manifest={"generated_at":now_iso(),"base_url":self.base,"model":self.model,
                  "results":[asdict(x) for x in self.results],"support_matrix":self.matrix()}
        (self.out/"manifest.json").write_text(js(manifest),encoding="utf-8")

        lines=["# Qwen3.6 / vLLM 全面 API、Agent 与 Vision 测试","",
               f"- 时间：`{now_iso()}`",f"- API：`{self.base}`",f"- 模型：`{self.model}`",
               f"- 声明 Context：`{self.context_len}`","",
               "## 能力矩阵","","| 能力 | 结果 | 判定依据 |","|---|---|---|"]
        for r in self.matrix(): lines.append(f"| {r['capability']} | **{r['status']}** | {r['basis']} |")
        lines += ["","## 逐项测试","","| # | 分类 | 测试 | Endpoint | 结果 | HTTP | 耗时ms | TTFTms | 说明 |",
                  "|---:|---|---|---|---|---:|---:|---:|---|"]
        for r in self.results:
            lines.append(f"| {r.seq} | {r.category} | {r.name} | `{r.endpoint}` | **{r.status}** | "
                         f"{'' if r.http_status is None else r.http_status} | "
                         f"{'' if r.elapsed_ms is None else r.elapsed_ms} | "
                         f"{'' if r.ttft_ms is None else r.ttft_ms} | {r.notes.replace('|','/')} |")
        lines += ["","## Vision Ground Truth","",
                  "- vision_test_1.png：`AI TEST 2026`；3 红圆；2 蓝方块；绿色三角形右下。",
                  "- vision_test_2.png：`SECOND IMAGE`；4 紫方块；1 橙色圆。",
                  "",
                  "Vision PASS 要求模型输出与 Ground Truth 匹配，不是只检查 HTTP 200。",
                  "",
                  "## 失败解释原则","",
                  "- Base64 Vision 失败：优先检查模型部署是否加载视觉模块、Chat Template 和多模态协议。",
                  "- Base64 成功但公网 URL 失败：更可能是出网/DNS/代理/远程媒体策略问题。",
                  "- Endpoint 200 但没有 tool_call/tool_use：工具能力不能判 PASS。",
                  "- 三套协议的 Vision 结果必须分别判断；模型本体支持图片不等于每种兼容协议都支持图片。"]
        (self.out/"summary.md").write_text("\n".join(lines),encoding="utf-8")

    def run(self):
        print("="*96); print("Qwen3.6 全面 API + Agent + Vision 测试")
        print("Base URL:",self.base); print("Model:",self.model); print("Output:",self.out); print("="*96)
        self.basic()
        self.chat()
        self.responses()
        self.anthropic()
        self.vision()
        self.long_context()
        self.metrics("after")
        self.finish()
        print("="*96); print("完成:",self.out/"summary.md"); print("="*96)

def parse_targets(s):
    return [int(x.strip()) for x in s.split(",") if x.strip()] if s.strip() else []

def main():
    p=argparse.ArgumentParser(description="Qwen3.6 全面 API + Agent + Vision 测试")
    p.add_argument("--base-url",default=os.getenv("QWEN_BASE_URL",""))
    p.add_argument("--api-key",default=os.getenv("QWEN_API_KEY",""))
    p.add_argument("--model",default=os.getenv("QWEN_MODEL",DEFAULT_MODEL))
    p.add_argument("--context-len",type=int,default=int(os.getenv("QWEN_CONTEXT_LEN",str(DEFAULT_CONTEXT))))
    p.add_argument("--timeout",type=int,default=DEFAULT_TIMEOUT)
    p.add_argument("--output",default="qwen_api_test_records_v2")
    p.add_argument("--insecure",action="store_true")
    p.add_argument("--remote-image-url",default="")
    p.add_argument("--long-context-targets",default="",
                   help="可选，例如 4096,16384,60000；默认不做长上下文压力测试")
    a=p.parse_args()
    if not a.base_url:
        print("请设置 QWEN_BASE_URL 或 --base-url",file=sys.stderr); return 2
    out=Path(a.output)/datetime.now().strftime("%Y%m%d_%H%M%S"); out.mkdir(parents=True,exist_ok=True)
    Suite(a.base_url,a.api_key,a.model,out,a.timeout,not a.insecure,a.context_len,
          a.remote_image_url,parse_targets(a.long_context_targets)).run()
    return 0

if __name__=="__main__":
    raise SystemExit(main())