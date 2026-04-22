#!/usr/bin/env python3
"""Render the 4 root READMEs from templates/<name>.md + the live model catalog.

Templates live in `templates/` and use two marker lines to delimit the model
block:

    <!-- AUTOGEN:models:start -->
    ... placeholder / previous table, ignored ...
    <!-- AUTOGEN:models:end -->

On run, the script fetches `/v1/openapi/tools/catalog`, renders a localized
table per template, and writes the combined output to the configured path
(repo root or `skills/lovart-skill/`). The generated files have the AUTOGEN
markers stripped.

Local run (defaults to the prod gateway; override with CATALOG_URL env):
    python3 scripts/sync_models.py
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

def render_readme_table(tools: list[dict], locale: dict) -> str:
    """One flat table across all categories with a Premium column."""
    return render_table(tools, locale)


def render_skill_sections(tools: list[dict], locale: dict) -> str:
    """Three per-category sub-tables, no Premium column — matches the
    pre-existing SKILL.md layout that AI agents consume."""
    cat_map = locale["category"]
    grouped = group_by_category(tools)
    blocks: list[str] = []
    for cat in CATEGORY_ORDER:
        rows = [t for t in grouped if (t.get("category") or "") == cat]
        if not rows:
            continue
        label = cat_map.get(cat, cat)
        lines = [
            f"**{label}:**",
            "",
            "| Tool name | Display name |",
            "|---|---|",
        ]
        for t in rows:
            lines.append(f"| `{t.get('name','')}` | {t.get('display_name','')} |")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


# Per-output-file configuration. Each entry describes one template → output
# pair and how to render the AUTOGEN block for it.
LOCALES = {
    "README.md": {
        "template": "templates/README.md",
        "output": "README.md",
        "renderer": render_readme_table,
        "category": {"IMAGE": "IMAGE", "VIDEO": "VIDEO", "3D": "3D"},
        "headers": ["Category", "Tool name", "Display name", "Premium"],
        "premium": "⭐ Premium",
    },
    "README_CN.md": {
        "template": "templates/README_CN.md",
        "output": "README_CN.md",
        "renderer": render_readme_table,
        "category": {"IMAGE": "图片", "VIDEO": "视频", "3D": "3D"},
        "headers": ["类别", "Tool name", "显示名", "会员专属"],
        "premium": "⭐",
    },
    "README_TW.md": {
        "template": "templates/README_TW.md",
        "output": "README_TW.md",
        "renderer": render_readme_table,
        "category": {"IMAGE": "圖片", "VIDEO": "影片", "3D": "3D"},
        "headers": ["類別", "Tool name", "顯示名", "會員專屬"],
        "premium": "⭐",
    },
    "README_JA.md": {
        "template": "templates/README_JA.md",
        "output": "README_JA.md",
        "renderer": render_readme_table,
        "category": {"IMAGE": "画像", "VIDEO": "動画", "3D": "3D"},
        "headers": ["カテゴリ", "Tool name", "表示名", "プレミアム"],
        "premium": "⭐",
    },
    "SKILL.md": {
        "template": "templates/SKILL.md",
        "output": "skills/lovart-skill/SKILL.md",
        "renderer": render_skill_sections,
        # SKILL.md keeps English category labels so the AI agent sees the same
        # names it would pass to --prefer-models.
        "category": {"IMAGE": "IMAGE", "VIDEO": "VIDEO", "3D": "3D"},
    },
}


def fetch_catalog(url: str) -> list[dict]:
    # Cloudflare bot-management blocks the default `Python-urllib/*` UA with
    # a 403 at the edge; present a real-looking UA instead.
    headers = {
        "Accept": "application/json",
        "User-Agent": "lovart-skill-sync/1.0 (+https://github.com/lovartai/lovart-skill)",
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = json.loads(resp.read().decode())
    data = body.get("data") or {}
    tools = data.get("tools") or []
    if not tools:
        raise SystemExit(f"catalog returned 0 tools: {body!r}")
    return tools


def group_by_category(tools: list[dict]) -> list[dict]:
    """Return tools grouped by CATEGORY_ORDER (IMAGE → VIDEO → 3D → other),
    preserving the upstream order within each category.

    queryAgentInfo returns tools in curated order (agent_tool_relation.id),
    so within a category we keep whatever order the catalog hands us."""
    def cat_idx(t: dict) -> int:
        try:
            return CATEGORY_ORDER.index(t.get("category") or "")
        except ValueError:
            return len(CATEGORY_ORDER)

    indexed = list(enumerate(tools))
    indexed.sort(key=lambda pair: (cat_idx(pair[1]), pair[0]))
    return [t for _, t in indexed]


def render_table(tools: list[dict], locale: dict) -> str:
    headers = locale["headers"]
    premium_label = locale["premium"]
    cat_map = locale["category"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for t in group_by_category(tools):
        cat = cat_map.get(t.get("category") or "", t.get("category") or "")
        name = t.get("name") or ""
        disp = t.get("display_name") or ""
        premium = premium_label if t.get("is_premium") else ""
        lines.append(f"| {cat} | `{name}` | {disp} | {premium} |")
    return "\n".join(lines)


def render_from_template(template: str, table: str) -> str:
    """Replace the AUTOGEN block with the rendered table AND strip the markers."""
    try:
        i = template.index(BEGIN)
        j = template.index(END, i) + len(END)
    except ValueError:
        raise SystemExit(f"template missing {BEGIN} / {END} markers")
    # Strip the block including markers; rstrip trailing whitespace from prefix
    # and lstrip leading whitespace from suffix so we don't leave blank-line gunk.
    prefix = template[:i].rstrip() + "\n\n"
    suffix = "\n\n" + template[j:].lstrip()
    return f"{prefix}{table}{suffix}"


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent.parent
    tools = fetch_catalog(CATALOG_URL)
    print(
        f"fetched {len(tools)} tools ({sum(1 for t in tools if t.get('is_premium'))} premium) from {CATALOG_URL}",
        file=sys.stderr,
    )
    changed = []
    for name, locale in LOCALES.items():
        src = root / locale["template"]
        dst = root / locale["output"]
        if not src.exists():
            print(f"skip missing template {src}", file=sys.stderr)
            continue
        template = src.read_text(encoding="utf-8")
        block = locale["renderer"](tools, locale)
        rendered = render_from_template(template, block)
        before = dst.read_text(encoding="utf-8") if dst.exists() else ""
        if rendered != before:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(rendered, encoding="utf-8")
            changed.append(name)
            print(f"wrote {dst.relative_to(root)}", file=sys.stderr)
        else:
            print(f"unchanged {dst.relative_to(root)}", file=sys.stderr)
    if changed:
        print("CHANGED:" + ",".join(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
