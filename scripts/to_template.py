# -*- coding: utf-8 -*-
"""
把内部数据集 data/math_benchmark.json 转成课程统一的 10 字段模板格式。

输出：
    dataset/questions.json     数组
    dataset/questions.jsonl    一行一题
"""
import re
import json
import os
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "data", "math_benchmark.json")
OUT_DIR = os.path.join(BASE, "dataset")

TYPE_MAP = {"单选题": "single_choice", "填空题": "fill_blank", "解答题": "short_answer"}
GROUP = "初中数学 Educational-LLM Benchmark"


def split_choice(s: str):
    """'A. 26.2883×10¹⁰' -> ('A', '26.2883×10¹⁰')"""
    m = re.match(r"\s*([A-D])\s*[.、．:：]\s*(.*)", s, re.S)
    if m:
        return m.group(1), m.group(2).strip()
    return None, s.strip()


def to_record(q):
    qtype = TYPE_MAP.get(q["type"], "short_answer")
    choices = {}
    if qtype in ("single_choice", "multiple_choice"):
        for opt in q.get("options") or []:
            k, v = split_choice(opt)
            if k:
                choices[k] = v

    ans = (q.get("answer") or "").strip()
    answers = [ans] if ans else []

    meta = {
        "group_name": GROUP,
        "domain": q.get("domain"),
        "difficulty": q.get("difficulty"),
        "knowledge_points": [q["knowledge_point"]] if q.get("knowledge_point") else [],
        "explanation": q.get("analysis", ""),
        "paper_name": q.get("batch"),
        "question_number": q.get("source_id"),
        "source_type": q.get("source_type"),
        "verify_status": q.get("verify_status"),
        "original_id": q.get("id"),
    }

    return {
        "question_type": qtype,
        "question": q["question"],
        "img_url": None,
        "choices": choices,
        "answers": answers,
        "grade": 9,
        "subject": "数学",
        "source": q.get("source", ""),
        "source_url": None,
        "meta_data": meta,
    }


def validate(rows):
    errs = []
    for i, r in enumerate(rows, 1):
        for f in ("question", "question_type", "subject", "source"):
            if not str(r.get(f) or "").strip():
                errs.append(f"#{i} 字段 {f} 为空")
        if not r["answers"] or not str(r["answers"][0]).strip():
            errs.append(f"#{i} answers 为空")
        if r["question_type"] in ("single_choice", "multiple_choice"):
            if not r["choices"]:
                errs.append(f"#{i} 选择题缺少 choices")
            for a in r["answers"]:
                if a not in r["choices"]:
                    errs.append(f"#{i} 答案 {a} 不在 choices 中")
    return errs


def main():
    data = json.load(open(SRC, encoding="utf-8"))
    rows = [to_record(q) for q in data]

    errs = validate(rows)
    os.makedirs(OUT_DIR, exist_ok=True)
    json.dump(rows, open(os.path.join(OUT_DIR, "questions.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    with open(os.path.join(OUT_DIR, "questions.jsonl"), "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"题目总数：{len(rows)}")
    print("题型：", dict(Counter(r["question_type"] for r in rows)))
    print("领域：", dict(Counter(r["meta_data"]["domain"] for r in rows)))
    print("难度：", dict(Counter(r["meta_data"]["difficulty"] for r in rows)))
    print(f"校验问题：{len(errs)}")
    for e in errs[:10]:
        print("  -", e)
    print(f"输出目录：{OUT_DIR}")


if __name__ == "__main__":
    main()
