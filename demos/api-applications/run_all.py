#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run the four non-chat applications with one model endpoint."""

from __future__ import annotations

import argparse

import json_extract
import translate
import vision_ocr
import visual_qa
from common import DemoClient, add_connection_args, config_from_args, ensure_demo_assets


def main() -> None:
    parser = argparse.ArgumentParser(
        description="第一讲：同一个 qwen3.6 API 连续运行四个非 Chat 应用"
    )
    add_connection_args(parser)
    args = parser.parse_args()

    client = DemoClient(config_from_args(args))
    ensure_demo_assets()

    print("=" * 72)
    print("Same Model API → Translation → JSON → Vision OCR → Visual QA")
    print("=" * 72)

    translate.run(client)
    print("\n" + "-" * 72)
    json_extract.run(client)
    print("\n" + "-" * 72)
    vision_ocr.run(client)
    print("\n" + "-" * 72)
    visual_qa.run(client)

    print("\n" + "=" * 72)
    print("DONE: 四个应用使用的是同一个模型服务，变化的是 Input / Prompt / Output Contract。")
    print("=" * 72)


if __name__ == "__main__":
    main()
