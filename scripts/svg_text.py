# -*- coding: utf-8 -*-
"""
提取教习网预览 SVG 中的文字，支持单栏/双栏排版。
用法：uv run python scripts/svg_text.py <svg文件> [--cols 1|2|auto]
"""
import re
import sys
import html


def parse_svg(path):
    with open(path, "r", encoding="utf-8") as f:
        s = f.read()
    frags = []
    for m in re.finditer(r'<tspan([^>]*)>(.*?)</tspan>', s, re.S):
        attrs, inner = m.group(1), m.group(2)
        x = re.search(r'\bx="([-\d.]+)"', attrs)
        y = re.search(r'\by="([-\d.]+)"', attrs)
        txt = html.unescape(re.sub(r'<[^>]+>', '', inner))
        if txt.strip() and y and x:
            frags.append((float(y.group(1)), float(x.group(1)), txt))
    w = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+)', s)
    width = float(w.group(1)) if w else 595.0
    return frags, width


def group_lines(frags):
    frags = sorted(frags, key=lambda t: (t[0], t[1]))
    lines, cur, base = [], [], None
    for y, x, t in frags:
        if base is None or abs(y - base) > 3.5:
            if cur:
                lines.append("".join(p[1] for p in sorted(cur)))
            cur, base = [(x, t)], y
        else:
            cur.append((x, t))
    if cur:
        lines.append("".join(p[1] for p in sorted(cur)))
    return lines


def main(path):
    mode = "auto"
    if "--cols" in sys.argv:
        mode = sys.argv[sys.argv.index("--cols") + 1]
    frags, width = parse_svg(path)

    if mode == "auto":
        # 若 x 在页面中部存在明显空隙，判为双栏
        xs = sorted(f[1] for f in frags)
        mid = width / 2
        left = [x for x in xs if x < mid - 20]
        right = [x for x in xs if x > mid + 20]
        mode = "2" if (len(left) > 20 and len(right) > 20) else "1"

    if mode == "2":
        mid = width / 2
        print("====== 左栏 ======")
        for ln in group_lines([f for f in frags if f[1] < mid]):
            print(ln)
        print("\n====== 右栏 ======")
        for ln in group_lines([f for f in frags if f[1] >= mid]):
            print(ln)
    else:
        for ln in group_lines(frags):
            print(ln)


if __name__ == "__main__":
    main(sys.argv[1])
