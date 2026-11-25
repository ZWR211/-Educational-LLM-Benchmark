# -*- coding: utf-8 -*-
"""
用保存的模型原始输出重新判分（判分规则升级后无需重跑 API）。

用法：
    uv run --with requests python scripts/rescore.py results/<model>_results.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate import is_correct, extract_choice, normalize


def main(path):
    p = Path(path)
    rows = json.loads(p.read_text(encoding="utf-8"))

    changed = []
    for r in rows:
        old = bool(r.get("correct"))
        new = is_correct(r.get("raw", ""), r["gold"], r["type"])
        r["pred"] = extract_choice(r["raw"]) if r["type"] == "单选题" else normalize(r["raw"])
        r["correct"] = new
        if old != new:
            changed.append((r["id"], r["type"], r["gold"], r["raw"][:60], old, new))

    p.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    n = len(rows)
    c = sum(1 for r in rows if r["correct"])
    print(f"重判分完成：{c}/{n} = {c/n:.1%}")
    print(f"判分结果变化：{len(changed)} 题")
    for cid, ctype, gold, raw, old, new in changed:
        print(f"  {cid} [{ctype}] gold={gold!r} raw={raw!r}  {'错→对' if new else '对→错'}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("用法：uv run --with requests python scripts/rescore.py <results.json>")
    main(sys.argv[1])
