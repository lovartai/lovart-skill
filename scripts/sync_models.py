#!/usr/bin/env python3
"""Render the 4 root READMEs from templates/<name>.md + the live model catalog.

Templates live in `templates/` and use two marker lines to delimit the model
block:

    <!-- AUTOGEN:models:start -->
    ... placeholder / previous table, ignored ...
    <!-- AUTOGEN:models:end -->

On run, the script fetches `/v1/openapi/tools/catalog`, renders a localized
table per README, and writes the combined output to the repo root. The root
files are fully generated (no markers, prefixed with an "auto-generated"
banner) so users never see scaffolding on GitHub.

Local run:
    CATALOG_URL=https://lgw.pre.lovart.cloud/v1/openapi/tools/catalog \\
        python3 scripts/sync_models.py

CI uses the prod gateway by default.
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
        "banner": "<!-- This file is auto-generated from templates/README.md. Do not edit directly — edit the template and let CI regenerate. -->",
    },
    "README_CN.md": {
        "category": {"IMAGE": "图片", "VIDEO": "视频", "3D": "3D"},
        "headers": ["类别", "Tool name", "显示名", "会员专属"],
        "premium": "⭐",
        "banner": "<!-- 本文件由 templates/README_CN.md 自动生成，请勿直接修改根目录文件；修改模板后 CI 会重新生成。 -->",
    },
    "README_TW.md": {
        "category": {"IMAGE": "圖片", "VIDEO": "影片", "3D": "3D"},
        "headers": ["類別", "Tool name", "顯示名", "會員專屬"],
        "premium": "⭐",
        "banner": "<!-- 本檔案由 templates/README_TW.md 自動生成，請勿直接修改根目錄檔案；修改範本後 CI 會重新生成。 -->",
    },
    "README_JA.md": {
        "category": {"IMAGE": "画像", "VIDEO": "動画", "3D": "3D"},
        "headers": ["カテゴリ", "Tool name", "表示名", "プレミアム"],
        "premium": "⭐",
        "banner": "<!-- このファイルは templates/README_JA.md から自動生成されます。直接編集せず、テンプレートを編集してください。 -->",
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


def render_from_template(template: str, table: str, banner: str) -> str:
    """Replace the AUTOGEN block with the rendered table AND strip the markers,
    prepend the banner."""
    try:
        i = template.index(BEGIN)
        j = template.index(END, i) + len(END)
    except ValueError:
        raise SystemExit(f"template missing {BEGIN} / {END} markers")
    # Strip the block including markers; rstrip trailing whitespace from prefix
    # and lstrip leading whitespace from suffix so we don't leave blank-line gunk.
    prefix = template[:i].rstrip() + "\n\n"
    suffix = "\n\n" + template[j:].lstrip()
    body = f"{prefix}{table}{suffix}"
    return f"{banner}\n\n{body}"


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent.parent
    templates_dir = root / "templates"
    if not templates_dir.is_dir():
        raise SystemExit(f"templates dir not found at {templates_dir}")

    tools = fetch_catalog(CATALOG_URL)
    print(
        f"fetched {len(tools)} tools ({sum(1 for t in tools if t.get('is_premium'))} premium) from {CATALOG_URL}",
        file=sys.stderr,
    )
    changed = []
    for filename, locale in LOCALES.items():
        src = templates_dir / filename
        dst = root / filename
        if not src.exists():
            print(f"skip missing template {src}", file=sys.stderr)
            continue
        template = src.read_text(encoding="utf-8")
        table = render_table(tools, locale)
        rendered = render_from_template(template, table, locale["banner"])
        before = dst.read_text(encoding="utf-8") if dst.exists() else ""
        if rendered != before:
            dst.write_text(rendered, encoding="utf-8")
            changed.append(filename)
            print(f"wrote {dst.relative_to(root)}", file=sys.stderr)
        else:
            print(f"unchanged {dst.relative_to(root)}", file=sys.stderr)
    if changed:
        print("CHANGED:" + ",".join(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
