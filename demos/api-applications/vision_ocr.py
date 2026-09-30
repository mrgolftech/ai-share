#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo C: OCR-like recognition with the already-tested Vision Chat path."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import (
    DemoClient,
    add_connection_args,
    config_from_args,
    ensure_demo_assets,
    pretty_meta,
    vision_message,
)


EXPECTED = "BLUE-7319"


def normalize(text: str) -> str:
    return "".join(text.strip().upper().split())


def run(
    client: DemoClient,
    image: Path | None = None,
    expected: str = EXPECTED,
) -> str:
    assets = ensure_demo_assets()
    image = image or assets["ocr"]

    messages = [
        vision_message(
            "读取图片中的字符。只返回识别到的字符，不要解释，不要 Markdown。",
            image,
        )
    ]
    result, meta = client.chat(messages, max_tokens=64)
    got = normalize(result)
    expected_norm = normalize(expected)
    ok = got == expected_norm

    print("\n[Vision OCR]")
    print(f"image: {image}")
    print(f"result: {result.strip()}")
    print(f"expected: {expected}")
    print(f"validation: {'PASS' if ok else 'FAIL'}")
    print(f"[{pretty_meta(meta)}]")

    if not ok:
        raise RuntimeError(
            f"OCR 校验失败: got={got!r}, expected={expected_norm!r}"
        )
    return result.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Vision OCR Demo")
    add_connection_args(parser)
    parser.add_argument("--image", type=Path, default=None, help="自定义图片路径")
    parser.add_argument(
        "--expected",
        default=EXPECTED,
        help="预期识别文本；更换自定义图片时请同步指定",
    )
    args = parser.parse_args()
    run(DemoClient(config_from_args(args)), args.image, args.expected)


if __name__ == "__main__":
    main()
