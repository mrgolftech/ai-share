#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo B: extract a test record into JSON and validate it locally."""

from __future__ import annotations

import argparse
import json
from typing import Any

from common import (
    DemoClient,
    add_connection_args,
    config_from_args,
    parse_json_text,
    pretty_meta,
)


DEFAULT_TEXT = "SN=A102，温度 86.3°C，电压 3.28V，测试结果 FAIL，错误码 TEMP_HIGH。"


def validate_record(obj: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(obj, dict):
        return ["根节点不是 JSON object"]

    required = {
        "sn": str,
        "temperature_c": (int, float),
        "voltage_v": (int, float),
        "result": str,
        "error_code": str,
    }
    for key, expected in required.items():
        if key not in obj:
            errors.append(f"缺少字段: {key}")
        elif not isinstance(obj[key], expected):
            errors.append(f"字段类型错误: {key}={type(obj[key]).__name__}")

    if obj.get("result") not in {"PASS", "FAIL", "REVIEW"}:
        errors.append("result 必须是 PASS / FAIL / REVIEW")

    return errors


def run(client: DemoClient, text: str = DEFAULT_TEXT) -> dict[str, Any]:
    schema_hint = {
        "sn": "string",
        "temperature_c": "number",
        "voltage_v": "number",
        "result": "PASS|FAIL|REVIEW",
        "error_code": "string",
    }
    messages = [
        {
            "role": "system",
            "content": (
                "你是测试记录结构化程序。"
                "只输出一个合法 JSON object，不要 Markdown，不要解释。"
                "不得编造输入中不存在的字段值。"
            ),
        },
        {
            "role": "user",
            "content": (
                "把下面记录整理为固定字段。字段约束：\n"
                + json.dumps(schema_hint, ensure_ascii=False)
                + "\n记录：\n"
                + text
            ),
        },
    ]
    result, meta = client.chat(messages, max_tokens=256)
    obj = parse_json_text(result)
    errors = validate_record(obj)

    print("\n[JSON Extraction]")
    print(json.dumps(obj, ensure_ascii=False, indent=2))
    print(f"\n[local validation: {'PASS' if not errors else 'FAIL'}]")
    for error in errors:
        print(f"- {error}")
    print(f"[{pretty_meta(meta)}]")

    if errors:
        raise RuntimeError("JSON 本地校验失败")
    return obj


def main() -> None:
    parser = argparse.ArgumentParser(description="文本 → JSON 抽取 Demo")
    add_connection_args(parser)
    parser.add_argument("--text", default=DEFAULT_TEXT, help="待抽取测试记录")
    args = parser.parse_args()
    run(DemoClient(config_from_args(args)), args.text)


if __name__ == "__main__":
    main()
