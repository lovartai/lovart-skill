#!/usr/bin/env python3
"""Regenerate the model tables in README.md / README_CN.md / README_TW.md / README_JA.md
from the agent-openapi public catalog endpoint.

Each README has an auto-generated block delimited by:

    <!-- AUTOGEN:models:start -->
    ...
    <!-- AUTOGEN:models:end -->

Run locally:
    CATALOG_URL=https://lgw.pre.lovart.cloud/v1/openapi/tools/catalog python3 scripts/sync_models.py

In CI: defaults to the prod gateway.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import urllib.request

CATALOG_URL = os.environ.get(
    "CATALOG_URL", "https://lgw.lovart.ai/v1/openapi/tools/catalog"
)
BEGIN = "<!-- AUTOGEN:models:start -->"
END = "<!-- AUTOGEN:models:end -->"
CATEGORY_ORDER = ["IMAGE", "VIDEO", "3D"]

# Per-README localization.
LOCALES = {
    "README.md": {
        "category": {"IMAGE": "IMAGE", "VIDEO": "VIDEO", "3D": "3D"},
        "headers": ["Category", "Tool name", "Display name", "Premium"],
        "premium": "⭐ Premium",
    },
    "README_CN.md": {
        "category": {"IMAGE": "图片", "VIDEO": "视频", "3D": "3D"},
        "headers": ["类别", "Tool name", "显示名", "会员专属"],
        "premium": "⭐",
    },
    "README_TW.md": {
        "category": {"IMAGE": "圖片", "VIDEO": "影片", "3D": "3D"},
        "headers": ["類別", "Tool name", "顯示名", "會員專屬"],
        "premium": "⭐",
    },
    "README_JA.md": {
        "category": {"IMAGE": "画像", "VIDEO": "動画", "3D": "3D"},
        "headers": ["カテゴリ", "Tool name", "表示名", "プレミアム"],
        "premium": "⭐",
    },
}


def fetch_catalog(url: str) -> list[dict]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = json.loads(resp.read().decode())
    data = body.get("data") or {}
    tools = data.get("tools") or []
    if not tools:
        raise SystemExit(f"catalog returned 0 tools: {body!r}")
    return tools


def sort_key(tool: dict) -> tuple[int, str]:
    try:
        cat_idx = CATEGORY_ORDER.index(tool.get("category") or "")
    except ValueError:
        cat_idx = len(CATEGORY_ORDER)
    return (cat_idx, tool.get("name") or "")


def render_table(tools: list[dict], locale: dict) -> str:
    headers = locale["headers"]
    premium_label = locale["premium"]
    cat_map = locale["category"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for t in sorted(tools, key=sort_key):
        cat = cat_map.get(t.get("category") or "", t.get("category") or "")
        name = t.get("name") or ""
        disp = t.get("display_name") or ""
        premium = premium_label if t.get("is_premium") else ""
        lines.append(f"| {cat} | `{name}` | {disp} | {premium} |")
    return "\n".join(lines)


def splice_block(content: str, table: str) -> str:
    try:
        i = content.index(BEGIN)
        j = content.index(END, i)
    except ValueError:
        raise SystemExit(
            f"markers {BEGIN} / {END} missing; run the initial migration first"
        )
    prefix = content[: i + len(BEGIN)]
    suffix = content[j:]
    return f"{prefix}\n\n{table}\n\n{suffix}"


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent.parent
    tools = fetch_catalog(CATALOG_URL)
    print(
        f"fetched {len(tools)} tools ({sum(1 for t in tools if t.get('is_premium'))} premium) from {CATALOG_URL}",
        file=sys.stderr,
    )
    changed = []
    for filename, locale in LOCALES.items():
        path = root / filename
        if not path.exists():
            print(f"skip missing {filename}", file=sys.stderr)
            continue
        before = path.read_text(encoding="utf-8")
        table = render_table(tools, locale)
        after = splice_block(before, table)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed.append(filename)
            print(f"updated {filename}", file=sys.stderr)
        else:
            print(f"unchanged {filename}", file=sys.stderr)
    if changed:
        print("CHANGED:" + ",".join(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
