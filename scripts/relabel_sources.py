# -*- coding: utf-8 -*-
"""
来源字段如实化处理：
把原先不准确的 source 值（如"改编自中考真题"）改写为诚实的来源标注，
并新增 source_type / batch / verify_status 三个字段。
用法：uv run python scripts/relabel_sources.py
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "math_benchmark_v0.2.json")

# v0.1 种子批次在重新编号后占据各领域的前若干位
SEED_RANGE = {"NA": 30, "GG": 30, "SP": 20, "CP": 20}

SEED_SOURCE = "AI 辅助自编 · 种子批次（依据课标知识点命题，待人工校验）"
EXPAND_SOURCE = "AI 辅助自编 · 扩充批次（依据课标知识点命题，待人工校验）"


def main():
    with open(DATA, "r", encoding="utf-8") as f:
        items = json.load(f)

    n_seed = n_expand = 0
    for q in items:
        code = q["id"].split("-")[0]
        num = int(q["id"].split("-")[1])
        is_seed = num <= SEED_RANGE.get(code, 0)

        q["source_type"] = "AI辅助自编"
        q["batch"] = "种子批次" if is_seed else "扩充批次"
        q["verify_status"] = "待人工校验"
        q["source"] = SEED_SOURCE if is_seed else EXPAND_SOURCE

        if is_seed:
            n_seed += 1
        else:
            n_expand += 1

    # 字段顺序整理：把新增字段放在 source 之后
    ordered_keys = ["id", "domain", "knowledge_point", "difficulty", "type",
                    "question", "options", "answer", "analysis",
                    "source", "source_type", "batch", "verify_status"]
    items = [{k: q[k] for k in ordered_keys if k in q} for q in items]

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    print(f"已更新：{DATA}")
    print(f"  种子批次: {n_seed} 题")
    print(f"  扩充批次: {n_expand} 题")
    print(f"  合计: {len(items)} 题")


if __name__ == "__main__":
    main()
