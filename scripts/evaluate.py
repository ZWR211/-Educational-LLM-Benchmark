# -*- coding: utf-8 -*-
"""
初中数学 Educational-LLM Benchmark —— 模型评测脚本

用法示例：
    # 先设置密钥（以 DeepSeek 为例）
    $env:DEEPSEEK_API_KEY = "sk-..."

    # 小样本试跑（10 题）
    uv run --with requests python scripts/evaluate.py --provider deepseek --model deepseek-chat --limit 10

    # 全量评测（200 题）
    uv run --with requests python scripts/evaluate.py --provider deepseek --model deepseek-chat --all

    # 断点续跑
    uv run --with requests python scripts/evaluate.py --provider deepseek --model deepseek-chat --all --resume

服务商预设（--provider）：
    anthropic   ANTHROPIC_API_KEY
    openai      OPENAI_API_KEY
    deepseek    DEEPSEEK_API_KEY        https://api.deepseek.com/v1
    qwen        DASHSCOPE_API_KEY       dashscope 兼容模式
    glm         GLM_API_KEY             https://open.bigmodel.cn/api/paas/v4
    kimi        MOONSHOT_API_KEY        https://api.moonshot.cn/v1
    siliconflow SILICONFLOW_API_KEY     https://api.siliconflow.cn/v1

任意 OpenAI 兼容服务也可用 --base-url 和 --api-key-env 自定义。
"""
import os
import re
import json
import time
import argparse
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE = Path(__file__).resolve().parent.parent
DATASET = BASE / "data" / "math_benchmark.json"
RESULTS_DIR = BASE / "results"

_print_lock = threading.Lock()


# ---------------- prompt 模板 ----------------

SINGLE_TMPL = """请回答下面这道初中数学选择题。

要求：只输出正确选项的字母（A、B、C 或 D），不要输出任何解释、标点或其他文字。

题目：{question}
{options}"""

OPEN_TMPL = """请回答下面这道初中数学题。

要求：只给出最终答案，不要写解题过程。如果题目有多问，各问答案用分号“；”分隔。

题目：{question}"""


def build_prompt(q):
    if q["type"] == "单选题":
        return SINGLE_TMPL.format(question=q["question"], options="\n".join(q["options"]))
    return OPEN_TMPL.format(question=q["question"])


# ---------------- 答案提取与判分 ----------------

FULL2HALF = str.maketrans("（）：；，。＝＋－×÷", "():;,.=+-x/")


def normalize(s):
    """答案归一化：去空白、统一全角半角、去常见前缀。"""
    if s is None:
        return ""
    t = str(s).strip()
    t = t.translate(FULL2HALF)
    t = re.sub(r"\s+", "", t)
    # 去掉“答案：”“答：”“最终答案是”等前缀
    t = re.sub(r"^(最终)?(答案|答)[:：]?", "", t)
    t = t.strip("。.、")
    return t.lower()


def extract_choice(text):
    """从模型输出中提取选项字母。"""
    if not text:
        return ""
    t = text.strip().upper()
    # 优先匹配“答案：X”“选X”“X.”
    for pat in [r"答案\s*[:：]?\s*([ABCD])\b", r"选\s*([ABCD])\b", r"^\s*([ABCD])\s*[.、,，)）]?\s*$"]:
        m = re.search(pat, t)
        if m:
            return m.group(1)
    # 退化为找第一个独立出现的 A/B/C/D
    m = re.search(r"\b([ABCD])\b", t)
    return m.group(1) if m else ""


def to_number(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def is_correct(pred, gold, qtype):
    """判分：单选比字母，填空/解答比归一化后的最终答案。"""
    if qtype == "单选题":
        return extract_choice(pred) == gold.strip().upper()

    p, g = normalize(pred), normalize(gold)
    if not p:
        return False
    if p == g:
        return True

    # 数值等价：1/2 与 0.5
    pn, gn = to_number(p), to_number(g)
    if pn is not None and gn is not None and abs(pn - gn) < 1e-9:
        return True

    # 多问答案：按分号逐问比对，全部一致才算对
    gparts = [x for x in re.split(r"[;；]", g) if x]
    if len(gparts) > 1:
        pparts = [x for x in re.split(r"[;；]", p) if x]
        if len(pparts) == len(gparts):
            return all(normalize(a) == normalize(b) for a, b in zip(pparts, gparts))
    return False


# ---------------- API 调用 ----------------

def call_anthropic(prompt, model, api_key, max_tokens=512):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": 0,
        "messages": [{"role": "user", "content": prompt}],
    }
    r = requests.post(url, headers=headers, json=body, timeout=120)
    r.raise_for_status()
    data = r.json()
    return "".join(b.get("text", "") for b in data.get("content", []))


def call_openai(prompt, model, api_key, base_url, max_tokens=512):
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": 0,
        "messages": [{"role": "user", "content": prompt}],
    }
    r = requests.post(url, headers=headers, json=body, timeout=120)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]


# 常见服务商预设：provider -> (协议, base_url, 密钥环境变量)
PROVIDERS = {
    "anthropic": ("anthropic", None, "ANTHROPIC_API_KEY"),
    "openai":    ("openai", "https://api.openai.com/v1", "OPENAI_API_KEY"),
    "deepseek":  ("openai", "https://api.deepseek.com/v1", "DEEPSEEK_API_KEY"),
    "qwen":      ("openai", "https://dashscope.aliyuncs.com/compatible-mode/v1", "DASHSCOPE_API_KEY"),
    "glm":       ("openai", "https://open.bigmodel.cn/api/paas/v4", "GLM_API_KEY"),
    "kimi":      ("openai", "https://api.moonshot.cn/v1", "MOONSHOT_API_KEY"),
    "siliconflow": ("openai", "https://api.siliconflow.cn/v1", "SILICONFLOW_API_KEY"),
}


def call_model(prompt, args, key):
    if args.provider == "anthropic":
        return call_anthropic(prompt, args.model, key, args.max_tokens)
    return call_openai(prompt, args.model, key, args.base_url, args.max_tokens)


# ---------------- 主流程 ----------------

def evaluate_one(q, args, key, retries=3):
    prompt = build_prompt(q)
    last_err = ""
    for attempt in range(retries):
        try:
            raw = call_model(prompt, args, key)
            return {
                "id": q["id"],
                "type": q["type"],
                "domain": q["domain"],
                "difficulty": q["difficulty"],
                "knowledge_point": q["knowledge_point"],
                "gold": q["answer"],
                "raw": raw.strip(),
                "pred": extract_choice(raw) if q["type"] == "单选题" else normalize(raw),
                "correct": is_correct(raw, q["answer"], q["type"]),
            }
        except Exception as e:
            last_err = str(e)
            time.sleep(2 * (attempt + 1))
    return {
        "id": q["id"],
        "type": q["type"],
        "domain": q["domain"],
        "difficulty": q["difficulty"],
        "knowledge_point": q["knowledge_point"],
        "gold": q["answer"],
        "raw": "",
        "pred": "",
        "correct": False,
        "error": last_err,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="模型名称")
    ap.add_argument("--provider", default="anthropic", choices=list(PROVIDERS.keys()))
    ap.add_argument("--base-url", default=None, help="自定义 OpenAI 兼容地址（覆盖预设）")
    ap.add_argument("--api-key-env", default=None, help="读取密钥的环境变量名（覆盖预设）")
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 题（试跑用）")
    ap.add_argument("--all", action="store_true", help="跑全部题目")
    ap.add_argument("--resume", action="store_true", help="跳过已完成题目")
    ap.add_argument("--workers", type=int, default=4, help="并发数")
    ap.add_argument("--max-tokens", type=int, default=512)
    args = ap.parse_args()

    if not args.all and not args.limit:
        ap.error("请指定 --limit N（试跑）或 --all（全量）")

    # 解析服务商预设
    protocol, preset_url, preset_env = PROVIDERS[args.provider]
    args.provider = protocol                       # 实际协议：anthropic / openai
    args.base_url = args.base_url or preset_url or "https://api.openai.com/v1"
    key_env = args.api_key_env or preset_env
    key = os.environ.get(key_env)
    if not key:
        raise SystemExit(
            f"未找到环境变量 {key_env}。\n"
            f"请先设置，例如：$env:{key_env}=\"你的密钥\""
        )

    data = json.loads(DATASET.read_text(encoding="utf-8"))
    if args.limit:
        data = data[: args.limit]

    RESULTS_DIR.mkdir(exist_ok=True)
    safe_model = re.sub(r"[^\w\-.]", "_", args.model)
    out_path = RESULTS_DIR / f"{safe_model}_results.json"

    done = {}
    if args.resume and out_path.exists():
        for row in json.loads(out_path.read_text(encoding="utf-8")):
            done[row["id"]] = row
        print(f"[续跑] 已完成 {len(done)} 题")

    todo = [q for q in data if q["id"] not in done]
    print(f"[开始] 模型={args.model} 题数={len(todo)} 并发={args.workers}")

    results = list(done.values())
    lock = threading.Lock()
    finished = 0

    def save():
        out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(evaluate_one, q, args, key): q for q in todo}
        for fut in as_completed(futures):
            row = fut.result()
            with lock:
                results.append(row)
                finished += 1
                if finished % 10 == 0 or finished == len(todo):
                    save()
                    acc = sum(1 for r in results if r["correct"]) / len(results)
                    with _print_lock:
                        print(f"  进度 {finished}/{len(todo)}  当前准确率 {acc:.1%}")

    save()
    total = len(results)
    acc = sum(1 for r in results if r["correct"]) / total if total else 0
    print(f"\n[完成] {total} 题，准确率 {acc:.1%}")
    print(f"[输出] {out_path}")


if __name__ == "__main__":
    main()
