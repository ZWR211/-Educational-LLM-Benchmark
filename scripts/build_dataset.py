# -*- coding: utf-8 -*-
"""
由 data/sources/ 下的真题重建数据集（纯真实来源）。
用法：uv run python scripts/build_dataset.py
"""
import json
import os
import re
import glob
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES_DIR = os.path.join(BASE, "data", "sources")
OUT = os.path.join(BASE, "data", "math_benchmark.json")

DOMAIN_CODE = {"数与代数": "NA", "图形与几何": "GG", "统计与概率": "SP", "综合与实践": "CP"}
DOMAIN_ORDER = list(DOMAIN_CODE.keys())


def norm_q(t):
    return re.sub(r"\s+", "", t).replace("（", "(").replace("）", ")").replace("　", "")


def main():
    items = []
    for pf in sorted(glob.glob(os.path.join(SOURCES_DIR, "*.json"))):
        with open(pf, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"[载入] {os.path.basename(pf)}: {len(data)} 题")
        items.extend(data)

    # 去重
    seen, kept, dup = set(), [], 0
    for q in items:
        k = norm_q(q["question"])
        if k in seen:
            dup += 1
            continue
        seen.add(k)
        kept.append(q)

    # 按领域排序 + 编号
    kept.sort(key=lambda q: DOMAIN_ORDER.index(q["domain"]))
    counter = Counter()
    for q in kept:
        code = DOMAIN_CODE[q["domain"]]
        counter[code] += 1
        q["source_id"] = q.get("source_id", q["id"])
        q["id"] = f"{code}-{counter[code]:04d}"

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(kept, f, ensure_ascii=False, indent=2)

    total = len(kept)
    print(f"\n[去重] {len(items)-dup}/{len(items)} 保留（重复 {dup}）")
    print(f"[输出] {OUT}")
    print(f"[总计] {total} 题")
    print("[批次]")
    for k, v in Counter(q["batch"] for q in kept).most_common():
        print(f"   {k}: {v}")
    print("[领域]")
    for k, v in Counter(q["domain"] for q in kept).most_common():
        print(f"   {k}: {v}")
    print("[题型]")
    for k, v in Counter(q["type"] for q in kept).most_common():
        print(f"   {k}: {v}")


if __name__ == "__main__":
    main()
