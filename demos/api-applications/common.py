#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Shared helpers for the first-lecture API application demos."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from PIL import Image, ImageDraw, ImageFont


DEFAULT_MODEL = os.getenv("QWEN_MODEL", "qwen3.6")
DEFAULT_CONNECT_TIMEOUT = 15
DEFAULT_READ_TIMEOUT = 300
HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"


@dataclass
class Config:
    base_url: str
    api_key: str
    model: str = DEFAULT_MODEL
    connect_timeout: int = DEFAULT_CONNECT_TIMEOUT
    read_timeout: int = DEFAULT_READ_TIMEOUT
    verify_tls: bool = True


def add_connection_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--base-url",
        default=os.getenv("QWEN_BASE_URL", ""),
        help="模型服务 Base URL，也可使用环境变量 QWEN_BASE_URL",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("QWEN_API_KEY", ""),
        help="API Key，也可使用环境变量 QWEN_API_KEY",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"模型 ID，默认 {DEFAULT_MODEL}",
    )
    parser.add_argument(
        "--no-verify-tls",
        action="store_true",
        help="仅在受控内网测试环境中关闭 TLS 证书校验",
    )


def config_from_args(args: argparse.Namespace) -> Config:
    if not args.base_url:
        raise SystemExit("缺少 --base-url 或环境变量 QWEN_BASE_URL")
    if not args.api_key:
        raise SystemExit("缺少 --api-key 或环境变量 QWEN_API_KEY")
    return Config(
        base_url=args.base_url.rstrip("/"),
        api_key=args.api_key,
        model=args.model,
        verify_tls=not args.no_verify_tls,
    )


class DemoClient:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.session = requests.Session()

    def chat(
        self,
        messages: list[dict[str, Any]],
        *,
        max_tokens: int = 512,
        temperature: float = 0,
    ) -> tuple[str, dict[str, Any]]:
        url = f"{self.cfg.base_url}/v1/chat/completions"
        payload = {
            "model": self.cfg.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "chat_template_kwargs": {"enable_thinking": False},
        }
        headers = {
            "Authorization": f"Bearer {self.cfg.api_key}",
            "Content-Type": "application/json",
        }

        started = time.perf_counter()
        response = self.session.post(
            url,
            headers=headers,
            json=payload,
            timeout=(self.cfg.connect_timeout, self.cfg.read_timeout),
            verify=self.cfg.verify_tls,
        )
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)

        if not response.ok:
            body = response.text[:2000]
            raise RuntimeError(
                f"HTTP {response.status_code} from {url}\n{body}"
            )

        data = response.json()
        try:
            content = data["choices"][0]["message"].get("content") or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                "返回结构不是预期的 OpenAI Chat Completions 格式"
            ) from exc

        usage = data.get("usage") if isinstance(data, dict) else None
        meta = {
            "elapsed_ms": elapsed_ms,
            "usage": usage,
            "model": data.get("model") if isinstance(data, dict) else None,
            "finish_reason": (
                data.get("choices", [{}])[0].get("finish_reason")
                if isinstance(data, dict)
                else None
            ),
        }
        return content, meta


def image_to_data_url(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    raw = path.read_bytes()
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def vision_message(prompt: str, image_path: Path) -> dict[str, Any]:
    return {
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {"url": image_to_data_url(image_path)},
            },
        ],
    }


def parse_json_text(text: str) -> Any:
    text = text.strip()
    fence = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.S | re.I)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start_obj = text.find("{")
        start_arr = text.find("[")
        starts = [x for x in (start_obj, start_arr) if x >= 0]
        if not starts:
            raise
        start = min(starts)
        for end_char in ("}", "]"):
            end = text.rfind(end_char)
            if end > start:
                try:
                    return json.loads(text[start : end + 1])
                except json.JSONDecodeError:
                    pass
        raise


def pretty_meta(meta: dict[str, Any]) -> str:
    usage = meta.get("usage") or {}
    parts = [f"elapsed={meta.get('elapsed_ms')} ms"]
    if usage:
        parts.append(
            "tokens="
            f"{usage.get('prompt_tokens', '?')} in / "
            f"{usage.get('completion_tokens', '?')} out"
        )
    if meta.get("finish_reason"):
        parts.append(f"finish={meta['finish_reason']}")
    return " | ".join(parts)


def _font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in candidates:
        try:
            if Path(path).exists():
                return ImageFont.truetype(path, size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def ensure_demo_assets() -> dict[str, Path]:
    ASSETS.mkdir(parents=True, exist_ok=True)

    ocr = ASSETS / "ocr-demo.png"
    if not ocr.exists():
        image = Image.new("RGB", (900, 300), "white")
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((40, 50, 860, 250), radius=28, outline="black", width=5)
        text = "BLUE-7319"
        font = _font(72)
        box = draw.textbbox((0, 0), text, font=font)
        x = (900 - (box[2] - box[0])) / 2
        y = (300 - (box[3] - box[1])) / 2 - 10
        draw.text((x, y), text, fill="black", font=font)
        image.save(ocr)

    ui = ASSETS / "ui-qa-demo.png"
    if not ui.exists():
        image = Image.new("RGB", (1280, 720), "#f4f6f8")
        draw = ImageDraw.Draw(image)
        title_font = _font(42)
        body_font = _font(24)
        small_font = _font(18)

        draw.rectangle((0, 0, 1280, 86), fill="#182230")
        draw.text((40, 22), "Device Monitor", fill="white", font=_font(32))
        draw.text((990, 30), "DEMO / INTENTIONAL DEFECTS", fill="#d8dee9", font=small_font)

        # Main title.
        draw.text((62, 132), "Thermal Safety Dashboard", fill="#111827", font=title_font)

        # Defect 1: CTA visibly overlaps the title area.
        draw.rounded_rectangle((475, 126, 785, 188), radius=12, fill="#2563eb")
        draw.text((500, 140), "Export current report", fill="white", font=body_font)

        # Cards.
        cards = [(60, 240, 390, 520), (430, 240, 760, 520), (800, 240, 1130, 520)]
        labels = ["Temperature", "Voltage", "Recent events"]
        for box, label in zip(cards, labels):
            draw.rounded_rectangle(box, radius=16, fill="white", outline="#cbd5e1", width=2)
            draw.text((box[0] + 24, box[1] + 22), label, fill="#111827", font=body_font)

        draw.text((88, 330), "86.3 °C", fill="#b91c1c", font=_font(44))
        draw.text((458, 330), "3.28 V", fill="#111827", font=_font(44))

        # Defect 2: long text intentionally runs beyond the visible card area.
        overflow = "TEMP_HIGH event description is too long and should wrap inside this card, but it does not."
        draw.text((825, 325), overflow, fill="#374151", font=small_font)

        # Defect 3: footer action is partly outside the viewport.
        draw.rounded_rectangle((980, 665, 1285, 735), radius=12, fill="#111827")
        draw.text((1010, 682), "Acknowledge all", fill="white", font=body_font)

        image.save(ui)

    return {"ocr": ocr, "ui": ui}
