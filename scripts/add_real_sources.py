# -*- coding: utf-8 -*-
"""
把 data/sources/ 下的真实来源题目并入数据集，输出 v0.3。
真题保留原始编号于 source_id 字段，便于追溯。
用法：uv run python scripts/add_real_sources.py
"""
import json
import os
import glob
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_IN = os.path.join(BASE, "data", "math_benchmark_v0.2.json")
SOURCES_DIR = os.path.join(BASE, "data", "sources")
OUT = os.path.join(BASE, "data", "math_benchmark_v0.3.json")

DOMAIN_CODE = {"数与代数": "NA", "图形与几何": "GG", "统计与概率": "SP", "综合与实践": "CP"}


def main():
    with open(SRC_IN, "r", encoding="utf-8") as f:
        base = json.load(f)

    # 各领域当前最大编号
    counter = Counter()
    for q in base:
        code = q["id"].split("-")[0]
        counter[code] = max(counter[code], int(q["id"].split("-")[1]))

    added = []
    for pf in sorted(glob.glob(os.path.join(SOURCES_DIR, "*.json"))):
        with open(pf, "r", encoding="utf-8") as f:
            items = json.load(f)
        for q in items:
            q["source_id"] = q["id"]          # 保留原始编号
            code = DOMAIN_CODE[q["domain"]]
            counter[code] += 1
            q["id"] = f"{code}-{counter[code]:04d}"
            added.append(q)
        print(f"[载入] {os.path.basename(pf)}: {len(items)} 题")

    merged = base + added
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    total = len(merged)
    print(f"\n[输出] {OUT}")
    print(f"[总计] {total} 题（自编 {len(base)} + 真题 {len(added)}）")
    print("[来源类型]")
    for k, v in Counter(q["source_type"] for q in merged).most_common():
        print(f"   {k}: {v} ({v/total*100:.1f}%)")


if __name__ == "__main__":
    main()
