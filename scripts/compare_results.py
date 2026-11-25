# -*- coding: utf-8 -*-
"""
多模型评测结果对比，生成 Markdown 对比表。

用法：
    uv run python scripts/compare_results.py results/a_results.json results/b_results.json
"""
import json
import sys
from pathlib import Path
from collections import defaultdict


def load(path):
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    name = Path(path).stem.replace("_results", "")
    return name, rows


def acc(rows):
    n = len(rows)
    return (sum(1 for r in rows if r.get("correct")) / n) if n else 0.0


def group(rows, field):
    buckets = defaultdict(list)
    for r in rows:
        buckets[r.get(field, "未知")].append(r)
    return buckets


def main(paths):
    models = [load(p) for p in paths]
    names = [n for n, _ in models]

    lines = ["# 多模型评测对比\n"]
    lines.append("| 维度 | " + " | ".join(names) + " |")
    lines.append("|---|" + "---:|" * len(names))

    # 整体
    lines.append("| **整体** | " + " | ".join(f"**{acc(rows):.1%}**" for _, rows in models) + " |")

    for field, title in [("type", "题型"), ("domain", "领域"), ("difficulty", "难度")]:
        lines.append(f"\n### 按{title}\n")
        lines.append("| " + title + " | " + " | ".join(names) + " |")
        lines.append("|---|" + "---:|" * len(names))
        keys = []
        for _, rows in models:
            for k in group(rows, field):
                if k not in keys:
                    keys.append(k)
        for k in keys:
            cells = []
            for _, rows in models:
                sub = group(rows, field).get(k, [])
                cells.append(f"{acc(sub):.1%}" if sub else "—")
            lines.append(f"| {k} | " + " | ".join(cells) + " |")

    out = Path("results") / "模型对比.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\n已保存：{out}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("用法：uv run python scripts/compare_results.py <results1.json> [results2.json ...]")
    main(sys.argv[1:])
