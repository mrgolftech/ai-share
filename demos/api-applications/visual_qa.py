#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo D: use a webpage screenshot as input for visual QA."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from common import (
    DemoClient,
    add_connection_args,
    config_from_args,
    ensure_demo_assets,
    parse_json_text,
    pretty_meta,
    vision_message,
)


def validate_qa(obj: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(obj, dict):
        return ["根节点不是 JSON object"]
    issues = obj.get("issues")
    if not isinstance(issues, list):
        return ["issues 不是数组"]
    if not issues:
        return ["没有识别出任何可见问题"]
    for index, issue in enumerate(issues):
        if not isinstance(issue, dict):
            errors.append(f"issues[{index}] 不是 object")
            continue
        for key in ("type", "region", "description", "suggestion"):
            if not isinstance(issue.get(key), str) or not issue.get(key, "").strip():
                errors.append(f"issues[{index}] 缺少有效字段 {key}")
    return errors


def run(client: DemoClient, image: Path | None = None) -> dict[str, Any]:
    assets = ensure_demo_assets()
    image = image or assets["ui"]

    prompt = (
        "这是一个我们自己制作的 Demo 网页截图。请从视觉上检查明显的 UI/布局问题，"
        "例如遮挡、溢出、裁切、错位、间距异常。"
        "只输出合法 JSON，不要 Markdown，不要解释。格式为："
        '{"issues":[{"type":"layout|overflow|clipping|spacing|other",'
        '"region":"位置","description":"可见问题","suggestion":"修复建议"}]}。'
        "只报告从图片中确实能看到的问题，不要臆测代码原因。"
    )
    messages = [vision_message(prompt, image)]
    result, meta = client.chat(messages, max_tokens=700)
    obj = parse_json_text(result)
    errors = validate_qa(obj)

    print("\n[Visual QA]")
    print(f"image: {image}")
    print(json.dumps(obj, ensure_ascii=False, indent=2))
    print(f"\n[local validation: {'PASS' if not errors else 'FAIL'}]")
    for error in errors:
        print(f"- {error}")
    print(f"[{pretty_meta(meta)}]")

    if errors:
        raise RuntimeError("Visual QA JSON 本地校验失败")
    return obj


def main() -> None:
    parser = argparse.ArgumentParser(description="网页截图 Visual QA Demo")
    add_connection_args(parser)
    parser.add_argument("--image", type=Path, default=None, help="自定义网页截图路径")
    args = parser.parse_args()
    run(DemoClient(config_from_args(args)), args.image)


if __name__ == "__main__":
    main()
