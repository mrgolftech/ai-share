#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the two local images used by the Vision demos."""

from common import ensure_demo_assets


if __name__ == "__main__":
    assets = ensure_demo_assets()
    for name, path in assets.items():
        print(f"{name}: {path}")
