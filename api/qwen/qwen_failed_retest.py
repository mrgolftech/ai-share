#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Qwen3.6 失败项专项重测脚本

重测：
1) chat_thinking_off —— 修复上一版判定 bug
2) chat_thinking_on  —— 超时放宽
3) vision_chat_tool_call —— 修正 OCR 参数 Schema
4) vision_responses_base64 —— 两种 input_image 写法并保存完整 HTTP 400 Body

每轮还会做：
- GET /version
- 简单 Chat PING_OK

这样可以判断：
- 网络/服务整体不稳
- Thinking 自身太慢/排队
- Vision Tool 是提示/Schema 问题
- Responses Vision 是协议/格式问题

依赖：
    pip install requests pillow

示例：
    python qwen_failed_retest.py ^
      --base-url http://<INTRANET_API_HOST>:<PORT> ^
      --api-key xxx ^
      --retries 3 ^
      --timeout 600 ^
      --backoff 10
"""

from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
import re
import sys
import time
import traceback
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import requests
from PIL import Image, ImageDraw, ImageFont


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def dumps(x):
    return json.dumps(x, ensure_ascii=False, indent=2)


def mask_secret(s):
    if not s:
        return ""
    return "***" if len(s) <= 8 else s[:3] + "***" + s[-3:]


def redact(obj, secret):
    if isinstance(obj, dict):
        return {k: redact(v, secret) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact(v, secret) for v in obj]
    if isinstance(obj, str):
        s = obj.replace(secret, mask_secret(secret)) if secret else obj
        if s.startswith("data:image/") and ";base64," in s:
            head, b64 = s.split(";base64,", 1)
            try:
                raw = base64.b64decode(b64)
                return f"{head};base64,<OMITTED bytes={len(raw)} sha256={hashlib.sha256(raw).hexdigest()}>"
            except Exception:
                return f"{head};base64,<OMITTED>"
        return s
    return obj


def get_font(size=52):
    for p in [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        try:
            if Path(p).exists():
                return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


def make_test_image(path):
    img = Image.new("RGB", (1200, 800), "white")
    d = ImageDraw.Draw(img)
    d.text((45, 35), "AI TEST 2026", fill="black", font=get_font(52))
    for box in [(120,220,300,400),(390,220,570,400),(660,220,840,400)]:
        d.ellipse(box, fill=(230,30,30), outline="black", width=5)
    for box in [(135,520,295,680),(405,520,565,680)]:
        d.rectangle(box, fill=(30,90,230), outline="black", width=5)
    d.polygon([(900,685),(1130,685),(1015,465)], fill=(20,175,75), outline="black")
    img.save(path, "PNG")


def parse_json_text(text):
    if not text:
        return None
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.I)
    t = re.sub(r"\s*```$", "", t)
    try:
        x = json.loads(t)
        return x if isinstance(x, dict) else None
    except Exception:
        a, b = t.find("{"), t.rfind("}")
        if a >= 0 and b > a:
            try:
                x = json.loads(t[a:b+1])
                return x if isinstance(x, dict) else None
            except Exception:
                pass
    return None


def norm_pos(v):
    s = str(v or "").strip().lower().replace("_", "-").replace(" ", "-")
    if "右下" in s or ("bottom" in s and "right" in s):
        return "bottom-right"
    return s


@dataclass
class Row:
    test: str
    attempt: int
    status: str
    http_status: Optional[int]
    elapsed_ms: Optional[float]
    notes: str
    record_file: str


class Runner:
    def __init__(self, base, key, model, out, retries, timeout, backoff):
        base = base.rstrip("/")
        self.base = base[:-3] if base.endswith("/v1") else base
        self.key = key
        self.model = model
        self.out = out
        self.records = out / "records"
        self.assets = out / "assets"
        self.records.mkdir(parents=True, exist_ok=True)
        self.assets.mkdir(parents=True, exist_ok=True)
        self.retries = retries
        self.timeout = timeout
        self.backoff = backoff
        self.s = requests.Session()
        self.rows = []

        self.image_path = self.assets / "vision_test_1.png"
        make_test_image(self.image_path)
        raw = self.image_path.read_bytes()
        self.image_uri = "data:image/png;base64," + base64.b64encode(raw).decode()

    def url(self, ep):
        return self.base + ep

    def headers(self):
        h = {"Content-Type": "application/json"}
        if self.key:
            h["Authorization"] = "Bearer " + self.key
        return h

    def save(self, test, attempt, req, resp, status, notes):
        p = self.records / f"{test}_attempt_{attempt}.json"
        doc = {
            "test": test,
            "attempt": attempt,
            "recorded_at": now_iso(),
            "request": redact(req, self.key),
            "response": redact(resp, self.key),
            "analysis": {"status": status, "notes": notes},
        }
        p.write_text(dumps(doc), encoding="utf-8")
        self.rows.append(Row(test, attempt, status, resp.get("status_code"),
                             resp.get("elapsed_ms"), notes, p.name))
        print(f"[{status:<5}] {test:<30} attempt={attempt} "
              f"HTTP={resp.get('status_code')} elapsed={resp.get('elapsed_ms')} ms  {notes}")

    def request(self, test, attempt, method, ep, body=None):
        req = {"method": method, "url": self.url(ep),
               "headers": self.headers(), "json": body}
        t = time.perf_counter()
        try:
            r = self.s.request(
                method, self.url(ep),
                headers=self.headers(),
                json=body if method == "POST" else None,
                timeout=(15, self.timeout)
            )
            ms = round((time.perf_counter()-t)*1000, 2)
            try:
                data = r.json()
            except Exception:
                data = r.text
            return req, {
                "status_code": r.status_code,
                "elapsed_ms": ms,
                "headers": dict(r.headers),
                "body": data,
            }, r, data
        except Exception as e:
            ms = round((time.perf_counter()-t)*1000, 2)
            return req, {
                "status_code": None,
                "elapsed_ms": ms,
                "exception": f"{type(e).__name__}: {e}",
                "traceback": traceback.format_exc(),
            }, None, None

    def probe(self, attempt, label):
        req, resp, r, data = self.request(
            f"probe_version_{label}", attempt, "GET", "/version"
        )
        ok = r is not None and 200 <= r.status_code < 300
        self.save(f"probe_version_{label}", attempt, req, resp,
                  "PASS" if ok else "FAIL",
                  "version probe 正常" if ok else "version probe 失败")

        body = {
            "model": self.model,
            "messages": [{"role":"user","content":"请只回答：PING_OK"}],
            "temperature": 0,
            "max_tokens": 32,
            "chat_template_kwargs": {"enable_thinking": False},
        }
        req, resp, r, data = self.request(
            f"probe_chat_{label}", attempt, "POST", "/v1/chat/completions", body
        )
        text = ""
        if isinstance(data, dict):
            try:
                text = data["choices"][0]["message"].get("content") or ""
            except Exception:
                pass
        ok = r is not None and 200 <= r.status_code < 300 and "PING_OK" in text
        self.save(f"probe_chat_{label}", attempt, req, resp,
                  "PASS" if ok else "FAIL",
                  f"PING text={text!r}")

    def thinking_off(self, attempt):
        body = {
            "model": self.model,
            "messages": [{
                "role": "user",
                "content": "三个盒子的标签全部贴错，只能取一个水果，如何确定三个盒子的正确标签？请简洁回答。"
            }],
            "temperature": 0.1,
            "max_tokens": 512,
            "chat_template_kwargs": {"enable_thinking": False},
        }
        req, resp, r, data = self.request(
            "chat_thinking_off", attempt, "POST", "/v1/chat/completions", body
        )
        ok = False
        notes = resp.get("exception", "请求失败")
        if r is not None and 200 <= r.status_code < 300 and isinstance(data, dict):
            try:
                c = data["choices"][0]
                m = c["message"]
                reason = m.get("reasoning") or m.get("reasoning_content")
                content = m.get("content") or ""
                ok = bool(content) and not reason
                notes = (
                    f"reasoning={bool(reason)}, finish_reason={c.get('finish_reason')}, "
                    f"completion_tokens={(data.get('usage') or {}).get('completion_tokens')}"
                )
            except Exception as e:
                notes = f"解析失败: {e}"
        self.save("chat_thinking_off", attempt, req, resp,
                  "PASS" if ok else "FAIL", notes)

    def thinking_on(self, attempt):
        body = {
            "model": self.model,
            "messages": [{
                "role": "user",
                "content": "三个盒子的标签全部贴错，只能取一个水果，如何确定三个盒子的正确标签？请给出答案。"
            }],
            "temperature": 0.1,
            "max_tokens": 1536,
            "chat_template_kwargs": {"enable_thinking": True},
        }
        req, resp, r, data = self.request(
            "chat_thinking_on", attempt, "POST", "/v1/chat/completions", body
        )
        ok = False
        notes = resp.get("exception", "请求失败")
        if r is not None and 200 <= r.status_code < 300 and isinstance(data, dict):
            try:
                c = data["choices"][0]
                m = c["message"]
                reason = m.get("reasoning") or m.get("reasoning_content")
                content = m.get("content") or ""
                ok = bool(reason)
                notes = (
                    f"reasoning={bool(reason)}, final_content={bool(content)}, "
                    f"finish_reason={c.get('finish_reason')}, "
                    f"completion_tokens={(data.get('usage') or {}).get('completion_tokens')}"
                )
            except Exception as e:
                notes = f"解析失败: {e}"
        self.save("chat_thinking_on", attempt, req, resp,
                  "PASS" if ok else "FAIL", notes)

    def vision_tool(self, attempt):
        tool = {
            "type": "function",
            "function": {
                "name": "submit_visual_observation",
                "description": "提交图片中的结构化视觉事实",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "red_circles": {"type":"integer","description":"红色圆形数量"},
                        "blue_squares": {"type":"integer","description":"蓝色正方形数量"},
                        "green_triangle_position": {
                            "type":"string",
                            "description":"绿色三角形位置，例如 bottom-right"
                        },
                        "top_text": {
                            "type":"string",
                            "description":"逐字 OCR 图片顶部黑色英文，只填文字本身"
                        },
                    },
                    "required": [
                        "red_circles","blue_squares",
                        "green_triangle_position","top_text"
                    ],
                    "additionalProperties": False,
                },
            }
        }
        body = {
            "model": self.model,
            "messages": [{
                "role":"user",
                "content":[
                    {
                        "type":"text",
                        "text":"观察图片，必须调用 submit_visual_observation。数形状、判断绿色三角形位置，并逐字读取顶部英文。"
                    },
                    {"type":"image_url","image_url":{"url":self.image_uri}},
                ],
            }],
            "temperature":0,
            "max_tokens":512,
            "chat_template_kwargs":{"enable_thinking":False},
            "tools":[tool],
            "tool_choice":"required",
        }
        req, resp, r, data = self.request(
            "vision_chat_tool_call_fixed", attempt,
            "POST", "/v1/chat/completions", body
        )
        ok = False
        notes = resp.get("exception", "请求失败")
        if r is not None and 200 <= r.status_code < 300 and isinstance(data, dict):
            try:
                calls = data["choices"][0]["message"].get("tool_calls") or []
                if calls:
                    fn = calls[0]["function"]
                    args = json.loads(fn.get("arguments") or "{}")
                    ok = (
                        fn.get("name") == "submit_visual_observation"
                        and args.get("red_circles") == 3
                        and args.get("blue_squares") == 2
                        and norm_pos(args.get("green_triangle_position")) == "bottom-right"
                        and "AI TEST 2026" in str(args.get("top_text","")).upper()
                    )
                    notes = f"args={args}"
                else:
                    notes = "HTTP 200 但未返回 tool_calls"
            except Exception as e:
                notes = f"解析失败: {e}"
        self.save("vision_chat_tool_call_fixed", attempt, req, resp,
                  "PASS" if ok else "FAIL", notes)

    def responses_vision(self, attempt, variant):
        if variant == "string":
            image = {"type":"input_image","detail":"auto","image_url":self.image_uri}
        else:
            image = {"type":"input_image","detail":"auto","image_url":{"url":self.image_uri}}

        body = {
            "model": self.model,
            "input": [{
                "role":"user",
                "content":[
                    {
                        "type":"input_text",
                        "text":'只输出 JSON：{"red_circles":整数,"blue_squares":整数,"green_triangle_position":"bottom-right","text":"顶部文字"}'
                    },
                    image,
                ],
            }],
            "max_output_tokens":512,
            "reasoning":{"effort":"none"},
        }
        name = f"vision_responses_{variant}"
        req, resp, r, data = self.request(
            name, attempt, "POST", "/v1/responses", body
        )

        ok = False
        if r is None:
            notes = resp.get("exception", "请求失败")
        elif 200 <= r.status_code < 300 and isinstance(data, dict):
            texts = []
            for item in data.get("output") or []:
                if item.get("type") == "message":
                    for c in item.get("content") or []:
                        if c.get("type") == "output_text":
                            texts.append(c.get("text") or "")
            text = "".join(texts)
            obj = parse_json_text(text)
            ok = (
                isinstance(obj, dict)
                and obj.get("red_circles") == 3
                and obj.get("blue_squares") == 2
                and norm_pos(obj.get("green_triangle_position")) == "bottom-right"
                and "AI TEST 2026" in str(obj.get("text","")).upper()
            )
            notes = f"text={text!r}, parsed={obj}"
        else:
            # 这里最重要：把 400 的完整 Body 原样留在 record JSON
            notes = f"HTTP {r.status_code}, body={data!r}"

        self.save(name, attempt, req, resp,
                  "PASS" if ok else "FAIL", notes)

    def run_round(self, attempt):
        print("\n" + "="*90)
        print(f"Round {attempt}/{self.retries}")
        print("="*90)

        self.probe(attempt, "before")

        self.thinking_off(attempt)
        time.sleep(self.backoff)

        self.thinking_on(attempt)
        time.sleep(self.backoff)

        self.probe(attempt, "after_thinking")
        time.sleep(self.backoff)

        self.vision_tool(attempt)
        time.sleep(self.backoff)

        self.responses_vision(attempt, "string")
        time.sleep(self.backoff)

        self.responses_vision(attempt, "object")
        time.sleep(self.backoff)

        self.probe(attempt, "after")

    def finish(self):
        (self.out/"manifest.json").write_text(
            dumps({
                "generated_at":now_iso(),
                "base_url":self.base,
                "model":self.model,
                "retries":self.retries,
                "timeout":self.timeout,
                "backoff":self.backoff,
                "results":[asdict(x) for x in self.rows],
            }),
            encoding="utf-8"
        )

        groups = {}
        for r in self.rows:
            groups.setdefault(r.test, []).append(r)

        lines = [
            "# Qwen3.6 失败项专项重测",
            "",
            f"- 时间：`{now_iso()}`",
            f"- API：`{self.base}`",
            f"- 重试次数：`{self.retries}`",
            f"- Timeout：`{self.timeout}s`",
            "",
            "| 测试项 | PASS | FAIL | 最短ms | 最长ms |",
            "|---|---:|---:|---:|---:|",
        ]
        for name, rows in groups.items():
            ps = sum(x.status=="PASS" for x in rows)
            fs = sum(x.status!="PASS" for x in rows)
            ts = [x.elapsed_ms for x in rows if x.elapsed_ms is not None]
            lines.append(
                f"| {name} | {ps} | {fs} | "
                f"{min(ts) if ts else ''} | {max(ts) if ts else ''} |"
            )

        lines += [
            "",
            "## 判读原则",
            "",
            "- 同一测试出现 PASS / timeout / PASS，同时 PING 也变慢：偏向服务/网络波动。",
            "- PING 一直很快，但 Thinking 一直极慢：偏向模型推理或排队，而不是网络断开。",
            "- Responses Vision 连续稳定 HTTP 400：偏向协议/Schema/当前版本兼容问题，不像网络不稳定。",
            "- Responses Vision 两种写法只有一种成功：可以直接定位 input_image Schema。",
            "- 修正版 Vision Tool 稳定通过：上一版 FAIL 属于字段语义约束问题。",
            "",
            "请把整个目录压缩发回，尤其要保留 records/ 下的 HTTP 400 完整响应。",
        ]
        (self.out/"summary.md").write_text("\n".join(lines), encoding="utf-8")

    def run(self):
        print("="*90)
        print("Qwen3.6 失败项专项重测")
        print("Base URL:", self.base)
        print("Model:", self.model)
        print("Retries:", self.retries)
        print("Timeout:", self.timeout)
        print("Output:", self.out)
        print("="*90)
        for i in range(1, self.retries+1):
            self.run_round(i)
            if i < self.retries:
                time.sleep(self.backoff*2)
        self.finish()
        print("\n完成:", self.out/"summary.md")


def main():
    p = argparse.ArgumentParser(description="Qwen3.6 失败项专项重测")
    p.add_argument("--base-url", default=os.getenv("QWEN_BASE_URL",""))
    p.add_argument("--api-key", default=os.getenv("QWEN_API_KEY",""))
    p.add_argument("--model", default=os.getenv("QWEN_MODEL","qwen3.6"))
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--timeout", type=int, default=600)
    p.add_argument("--backoff", type=int, default=10)
    p.add_argument("--output", default="qwen_failed_retest_records")
    a = p.parse_args()

    if not a.base_url:
        print("请设置 QWEN_BASE_URL 或 --base-url", file=sys.stderr)
        return 2

    out = Path(a.output)/datetime.now().strftime("%Y%m%d_%H%M%S")
    out.mkdir(parents=True, exist_ok=True)

    Runner(
        a.base_url, a.api_key, a.model, out,
        a.retries, a.timeout, a.backoff
    ).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())