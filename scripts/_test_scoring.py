# -*- coding: utf-8 -*-
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from evaluate import is_correct, extract_choice, normalize

cases = [
    # (pred, gold, type, expected)
    ("A", "A", "单选题", True),
    ("答案：B", "B", "单选题", True),
    ("我认为应该选 C。", "C", "单选题", True),
    ("D", "A", "单选题", False),
    ("18", "18", "填空题", True),
    (" 18 ", "18", "填空题", True),
    ("x=3", "x=3", "填空题", True),
    ("X＝3", "x=3", "填空题", True),      # 全角等号
    ("0.5", "1/2", "填空题", False),       # 分数与小数不等价（保守）
    ("3", "3", "解答题", True),
    ("（1）60；（2）m=11，α=66°", "（1）60；（2）m=11，α=66°", "解答题", True),
    ("（1）60；（2）m=11，α=66°", "（1）60；（2）m=11，α=66°；（3）100；（4）1/6", "解答题", False),
]

ok = 0
for pred, gold, qtype, expected in cases:
    got = is_correct(pred, gold, qtype)
    flag = "OK " if got == expected else "FAIL"
    if got == expected:
        ok += 1
    print(f"{flag} [{qtype}] pred={pred!r} gold={gold!r} -> {got} (expected {expected})")

print(f"\n{ok}/{len(cases)} passed")
