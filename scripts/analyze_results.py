# -*- coding: utf-8 -*-
"""
评测结果分析：按整体 / 领域 / 题型 / 难度 / 知识点统计准确率。

用法：
    uv run python scripts/analyze_results.py results/<model>_results.json
"""
import json
import sys
from collections import defaultdict, Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def acc(rows):
    n = len(rows)
    if not n:
        return 0.0, 0, 0
    c = sum(1 for r in rows if r.get("correct"))
    return c / n, c, n


def table(counter_rows, title):
    lines = [f"### {title}\n", "| 分组 | 正确 | 总数 | 准确率 |", "|---|---:|---:|---:|"]
    for key, rows in counter_rows:
        a, c, n = acc(rows)
        lines.append(f"| {key} | {c} | {n} | {a:.1%} |")
    return "\n".join(lines)


def main(path):
    rows = json.loads(Path(path).read_text(encoding="utf-8"))
    if not rows:
        raise SystemExit("结果文件为空")

    errors = [r for r in rows if r.get("error")]
    overall, c, n = acc(rows)

    def group(field):
        buckets = defaultdict(list)
        for r in rows:
            buckets[r.get(field, "未知")].append(r)
        return sorted(buckets.items(), key=lambda kv: -len(kv[1]))

    md = [f"# 评测结果分析\n", f"> 结果文件：`{Path(path).name}`\n"]
    md.append("## 一、总览\n")
    md.append(f"- 题目总数：{n}")
    md.append(f"- 正确题数：{c}")
    md.append(f"- **整体准确率：{overall:.1%}**")
    if errors:
        md.append(f"- 调用失败：{len(errors)} 题（计入错误）")
    md.append("")
    md.append(table(group("type"), "二、按题型"))
    md.append("")
    md.append(table(group("domain"), "三、按领域"))
    md.append("")
    md.append(table(group("difficulty"), "四、按难度"))
    md.append("")
    md.append(table(group("knowledge_point"), "五、按知识点"))
    md.append("")

    out = Path(path).with_suffix("").with_name(Path(path).stem.replace("_results", "") + "_分析.md")
    out.write_text("\n".join(md), encoding="utf-8")

    print(f"整体准确率：{overall:.1%}（{c}/{n}）")
    for field in ("type", "domain", "difficulty"):
        print(f"\n[{field}]")
        for key, rs in group(field):
            a, cc, nn = acc(rs)
            print(f"  {key}: {a:.1%} ({cc}/{nn})")
    print(f"\n报告已生成：{out}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("用法：uv run python scripts/analyze_results.py <results.json>")
    main(sys.argv[1])
