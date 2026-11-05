# -*- coding: utf-8 -*-
"""
合并 v0.1 与并行生成的各分片，去重、校验、重新编号，输出最终数据集 v0.2。
用法：uv run python scripts/merge_dataset.py
"""
import json
import os
import re
import glob
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V01 = os.path.join(BASE, "data", "math_benchmark_v0.1.json")
PARTS_DIR = os.path.join(BASE, "data", "parts")
OUT = os.path.join(BASE, "data", "math_benchmark_v0.2.json")

DOMAIN_ORDER = ["数与代数", "图形与几何", "统计与概率", "综合与实践"]
DOMAIN_CODE = {"数与代数": "NA", "图形与几何": "GG", "统计与概率": "SP", "综合与实践": "CP"}
VALID_DOMAIN = set(DOMAIN_ORDER)
VALID_DIFF = {"基础", "中等", "较难"}
VALID_TYPE = {"单选题", "填空题", "解答题"}
VALID_ANSWER = {"A", "B", "C", "D"}
FIELDS = ("id", "domain", "knowledge_point", "difficulty", "type",
          "question", "options", "answer", "analysis", "source")


def load_json_loose(path):
    """容错读取：去掉可能的 markdown 代码围栏和 BOM。"""
    with open(path, "r", encoding="utf-8-sig") as f:
        txt = f.read().strip()
    if txt.startswith("```"):
        txt = re.sub(r"^```[a-zA-Z]*\s*", "", txt)
        txt = re.sub(r"\s*```$", "", txt)
    return json.loads(txt)


def norm_q(text):
    """题干归一化，用于去重。"""
    t = re.sub(r"\s+", "", text)
    t = t.replace("（", "(").replace("）", ")").replace("　", "")
    return t


def validate_one(q):
    probs = []
    for f in FIELDS:
        if f not in q:
            probs.append(f"缺字段 {f}")
    if q.get("domain") not in VALID_DOMAIN:
        probs.append(f"domain 非法:{q.get('domain')}")
    if q.get("difficulty") not in VALID_DIFF:
        probs.append(f"difficulty 非法:{q.get('difficulty')}")
    if q.get("type") not in VALID_TYPE:
        probs.append(f"type 非法:{q.get('type')}")
    if q.get("type") == "单选题":
        if len(q.get("options", [])) != 4:
            probs.append("选项数≠4")
        if q.get("answer") not in VALID_ANSWER:
            probs.append(f"答案非法:{q.get('answer')}")
    return probs


def main():
    items = []
    src_count = {}

    # 1) 先收 v0.1
    v01 = load_json_loose(V01)
    for q in v01:
        q["_src"] = "v0.1"
    items.extend(v01)
    src_count["v0.1"] = len(v01)
    print(f"[载入] v0.1: {len(v01)} 题")

    # 2) 收各分片
    part_files = sorted(glob.glob(os.path.join(PARTS_DIR, "*.json")))
    for pf in part_files:
        name = os.path.basename(pf)
        try:
            data = load_json_loose(pf)
        except Exception as e:
            print(f"[错误] {name} 解析失败: {e}")
            src_count[name] = f"解析失败({e})"
            continue
        for q in data:
            q["_src"] = name
        items.extend(data)
        src_count[name] = len(data)
        print(f"[载入] {name}: {len(data)} 题")

    raw_total = len(items)

    # 3) 去重（按题干）
    seen = {}
    kept, dropped = [], []
    for q in items:
        key = norm_q(q.get("question", ""))
        if key in seen:
            dropped.append(q)
        else:
            seen[key] = True
            kept.append(q)

    # 4) 校验 + 剔除不合规
    good, bad = [], []
    for q in kept:
        probs = validate_one(q)
        if probs:
            bad.append((q.get("id"), probs))
        else:
            good.append(q)

    print(f"\n[合并] 原始 {raw_total} 题 → 去重后 {len(kept)} 题 → 校验通过 {len(good)} 题")
    print(f"[去重] 丢弃重复 {len(dropped)} 题")
    print(f"[校验] 剔除不合规 {len(bad)} 题")
    for qid, probs in bad[:20]:
        print(f"   - {qid}: {'; '.join(probs)}")

    # 5) 重新编号（按领域顺序）
    good.sort(key=lambda q: DOMAIN_ORDER.index(q["domain"]))
    counters = Counter()
    for q in good:
        code = DOMAIN_CODE[q["domain"]]
        counters[code] += 1
        q["id"] = f"{code}-{counters[code]:04d}"
        q.pop("_src", None)

    # 6) 写出
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(good, f, ensure_ascii=False, indent=2)

    # 7) 汇总
    total = len(good)
    print(f"\n[输出] {OUT}")
    print(f"[总计] {total} 题")
    for d in DOMAIN_ORDER:
        n = sum(1 for q in good if q["domain"] == d)
        print(f"   {d}: {n}")
    print("[难度]")
    for k, v in Counter(q["difficulty"] for q in good).most_common():
        print(f"   {k}: {v} ({v/total*100:.1f}%)")
    print("[答案分布]")
    for k, v in sorted(Counter(q["answer"] for q in good).items()):
        print(f"   {k}: {v} ({v/total*100:.1f}%)")
    print("[知识点数]", len(set(q['knowledge_point'] for q in good)))


if __name__ == "__main__":
    main()
