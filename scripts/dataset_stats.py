# -*- coding: utf-8 -*-
"""
初中数学 LLM Benchmark —— 数据集校验与统计脚本
用法：uv run python scripts/dataset_stats.py
输出：控制台统计 + 04_数据统计报告.md
"""
import json
import os
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = "v0.2"
DATA = os.path.join(BASE, "data", f"math_benchmark_{VERSION}.json")
OUT = os.path.join(BASE, "04_数据统计报告.md")

VALID_DOMAIN = {"数与代数", "图形与几何", "统计与概率", "综合与实践"}
VALID_DIFF = {"基础", "中等", "较难"}
VALID_TYPE = {"单选题", "填空题", "解答题"}
VALID_ANSWER = {"A", "B", "C", "D"}


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate(items):
    """返回问题列表；空列表表示全部合规。"""
    problems = []
    ids = Counter(x.get("id") for x in items)
    for i, q in enumerate(items):
        qid = q.get("id", f"<第{i+1}条>")
        for field in ("id", "domain", "knowledge_point", "difficulty",
                      "type", "question", "options", "answer", "analysis",
                      "source", "source_type", "batch", "verify_status"):
            if field not in q:
                problems.append(f"{qid}: 缺少字段 {field}")
        if q.get("domain") not in VALID_DOMAIN:
            problems.append(f"{qid}: domain 非法 -> {q.get('domain')}")
        if q.get("difficulty") not in VALID_DIFF:
            problems.append(f"{qid}: difficulty 非法 -> {q.get('difficulty')}")
        if q.get("type") not in VALID_TYPE:
            problems.append(f"{qid}: type 非法 -> {q.get('type')}")
        if q.get("type") == "单选题":
            opts = q.get("options", [])
            if len(opts) != 4:
                problems.append(f"{qid}: 单选题选项数 != 4 -> {len(opts)}")
            if q.get("answer") not in VALID_ANSWER:
                problems.append(f"{qid}: 单选题答案非法 -> {q.get('answer')}")
    dup = [k for k, v in ids.items() if v > 1 and k is not None]
    if dup:
        problems.append(f"存在重复 id: {dup}")
    return problems


def dist(items, key):
    return Counter(x[key] for x in items)


def pct(n, total):
    return f"{n} ({n/total*100:.1f}%)" if total else "0"


def bar(n, total, width=20):
    filled = round(n / total * width) if total else 0
    return "█" * filled + "░" * (width - filled)


def table(counter, total, label):
    lines = [f"| {label} | 题数 | 占比 | 可视化 |", "|---|---:|---:|---|"]
    for k, v in counter.most_common():
        lines.append(f"| {k} | {v} | {v/total*100:.1f}% | {bar(v, total)} |")
    return "\n".join(lines)


def main():
    items = load(DATA)
    total = len(items)
    problems = validate(items)

    print(f"数据集文件：{DATA}")
    print(f"题目总数：{total}")
    print(f"格式校验：{'全部通过 ✅' if not problems else '发现 ' + str(len(problems)) + ' 个问题 ⚠️'}")
    for p in problems:
        print("  -", p)

    c_domain = dist(items, "domain")
    c_diff = dist(items, "difficulty")
    c_type = dist(items, "type")
    c_kp = dist(items, "knowledge_point")
    c_src = dist(items, "source_type")
    c_batch = dist(items, "batch")
    c_verify = dist(items, "verify_status")

    md = []
    md.append(f"# 数据统计报告（{VERSION}）\n")
    md.append(f"> 由 `scripts/dataset_stats.py` 自动生成，对应数据集 `data/math_benchmark_{VERSION}.json`\n")
    md.append(f"## 一、总览\n")
    md.append(f"- **题目总数**：{total} 题")
    md.append(f"- **领域数**：{len(c_domain)}")
    md.append(f"- **知识点数**：{len(c_kp)}")
    md.append(f"- **格式校验**：{'全部通过 ✅' if not problems else f'发现 {len(problems)} 个问题 ⚠️'}\n")

    md.append("## 二、按领域分布\n")
    md.append(table(c_domain, total, "领域"))
    md.append("")
    md.append("## 三、按难度分布\n")
    md.append(table(c_diff, total, "难度"))
    md.append("")
    md.append("> 参考配比目标：基础 : 中等 : 较难 ≈ 4 : 4 : 2\n")
    md.append("## 四、按题型分布\n")
    md.append(table(c_type, total, "题型"))
    md.append("")
    md.append("## 五、按知识点分布\n")
    md.append(table(c_kp, total, "知识点"))
    md.append("")
    md.append("## 六、按来源分布\n")
    md.append(table(c_src, total, "来源类型"))
    md.append("")
    md.append(table(c_batch, total, "批次"))
    md.append("")
    md.append(table(c_verify, total, "校验状态"))
    md.append("")
    md.append("> **来源说明**：当前 v0.2 全部题目为「AI 辅助自编」——依据《义务教育数学课程标准（2022 年版）》四大领域知识点命题生成，**并非**取自教材或中考真题。\n")
    md.append("> 下一步将引入权威来源（国家中小学智慧教育平台电子教材、人教版/北师大版教材、各地中考真题）进行改编替换，详见《03_数据收集与来源说明.md》。\n")

    if problems:
        md.append("## 七、校验问题清单\n")
        for p in problems:
            md.append(f"- {p}")
    else:
        md.append("## 七、校验问题清单\n")
        md.append("无。全部题目字段合规、无重复 id、结构完整。\n")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print(f"\n报告已生成：{OUT}")


if __name__ == "__main__":
    main()
