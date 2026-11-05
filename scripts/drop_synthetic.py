# -*- coding: utf-8 -*-
"""
清理 AI 自编题目：移入 archive/（可恢复），data/ 下只保留真实来源题目。
用法：uv run python scripts/drop_synthetic.py
"""
import json
import os
import shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
ARCHIVE = os.path.join(BASE, "archive")

SRC = os.path.join(DATA, "math_benchmark_v0.3.json")   # 1000 自编 + 6 真题
OUT = os.path.join(DATA, "math_benchmark.json")        # 仅真题

os.makedirs(ARCHIVE, exist_ok=True)

with open(SRC, "r", encoding="utf-8") as f:
    items = json.load(f)

synthetic = [q for q in items if q.get("source_type") == "AI辅助自编"]
authentic = [q for q in items if q.get("source_type") != "AI辅助自编"]

# 1) 归档 AI 题目
arc_path = os.path.join(ARCHIVE, "synthetic_questions_1000.json")
with open(arc_path, "w", encoding="utf-8") as f:
    json.dump(synthetic, f, ensure_ascii=False, indent=2)
print(f"[归档] {len(synthetic)} 道 AI 自编题 -> {arc_path}")

# 2) 归档旧的整库文件
for name in ("math_benchmark_v0.1.json", "math_benchmark_v0.2.json", "math_benchmark_v0.3.json"):
    p = os.path.join(DATA, name)
    if os.path.exists(p):
        shutil.move(p, os.path.join(ARCHIVE, name))
        print(f"[归档] {name}")

# 3) 归档 parts 分片
parts = os.path.join(DATA, "parts")
if os.path.exists(parts):
    shutil.move(parts, os.path.join(ARCHIVE, "parts"))
    print("[归档] data/parts/")

# 4) 输出纯真题数据集
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(authentic, f, ensure_ascii=False, indent=2)

print(f"\n[输出] {OUT}")
print(f"[总计] {len(authentic)} 题（全部为真实来源）")
from collections import Counter
print("[来源类型]", dict(Counter(q["source_type"] for q in authentic)))
print("[批次]", dict(Counter(q.get("batch", "") for q in authentic)))
