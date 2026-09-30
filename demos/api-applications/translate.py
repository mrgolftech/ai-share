#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo A: technical text translation through the same model API."""

from __future__ import annotations

import argparse

from common import DemoClient, add_connection_args, config_from_args, pretty_meta


DEFAULT_TEXT = "The device entered thermal protection mode after 30 seconds."


def run(client: DemoClient, text: str = DEFAULT_TEXT) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "你是技术文档翻译器。把英文翻译为简洁、准确的技术中文。"
                "不要解释，不要添加标题，只返回译文。"
            ),
        },
        {"role": "user", "content": text},
    ]
    result, meta = client.chat(messages, max_tokens=256)
    if not result.strip():
        raise RuntimeError("模型返回空译文")
    print("\n[Translation]")
    print(result.strip())
    print(f"\n[{pretty_meta(meta)}]")
    return result.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="技术文本翻译 Demo")
    add_connection_args(parser)
    parser.add_argument("--text", default=DEFAULT_TEXT, help="待翻译英文")
    args = parser.parse_args()
    run(DemoClient(config_from_args(args)), args.text)


if __name__ == "__main__":
    main()
