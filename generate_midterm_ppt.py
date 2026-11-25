# -*- coding: utf-8 -*-
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

PRIMARY = RGBColor(0x1F, 0x4E, 0x79)
ACCENT  = RGBColor(0x2E, 0x86, 0xAB)
DARK    = RGBColor(0x26, 0x26, 0x26)
GRAY    = RGBColor(0x59, 0x59, 0x59)
LIGHT   = RGBColor(0xEF, 0xF4, 0xF9)
BORDER  = RGBColor(0xD9, 0xDE, 0xE5)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
GOLD    = RGBColor(0xC0, 0x8A, 0x1E)
WARM    = RGBColor(0xB5, 0x5A, 0x4A)
FONT    = "微软雅黑"

OUT = r"C:\Users\34962\AppData\Roaming\CherryStudio\Data\Agents\system\2026-10-07\52df430c-b810-458e-a68a-1cd30754a532\初中数学Benchmark-期中汇报.pptx"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def set_font(run, size=18, bold=False, color=DARK):
    f = run.font
    f.name = FONT
    f.size = Pt(size)
    f.bold = bold
    f.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {})
        rPr.append(ea)
    ea.set('typeface', FONT)


def rect(slide, l, t, w, h, color):
    shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    shp.fill.solid(); shp.fill.fore_color.rgb = color
    shp.line.fill.background(); shp.shadow.inherit = False
    return shp


def header(slide, title, subtitle=None):
    rect(slide, Inches(0.6), Inches(0.55), Inches(0.14), Inches(0.72), ACCENT)
    tb = slide.shapes.add_textbox(Inches(0.95), Inches(0.42), Inches(11.7), Inches(1.0))
    tf = tb.text_frame; tf.word_wrap = True
    r = tf.paragraphs[0].add_run(); r.text = title
    set_font(r, 27, True, PRIMARY)
    if subtitle:
        p2 = tf.add_paragraph()
        r2 = p2.add_run(); r2.text = subtitle
        set_font(r2, 13, False, GRAY)
    rect(slide, Inches(0.6), Inches(1.38), Inches(12.13), Inches(0.02), BORDER)


def bullets(slide, items, top=1.65, left=0.75, width=11.9, height=5.3, size=17):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame; tf.word_wrap = True
    first = True
    for it in items:
        text, level = it if isinstance(it, tuple) else (it, 0)
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.level = level
        p.space_after = Pt(9)
        p.line_spacing = 1.12
        r = p.add_run()
        r.text = ("•  " if level == 0 else "–  ") + text
        set_font(r, size if level == 0 else size - 2, level == 0,
                 DARK if level == 0 else GRAY)
    return tb


def table_slide(title, headers, rows, subtitle=None, col_widths=None,
                font=14, top=1.62, height=5.4):
    s = prs.slides.add_slide(BLANK)
    header(s, title, subtitle)
    n_rows, n_cols = len(rows) + 1, len(headers)
    gt = s.shapes.add_table(n_rows, n_cols, Inches(0.65), Inches(top),
                            Inches(12.0), Inches(height)).table
    gt.first_row = False; gt.horz_banding = False
    if col_widths:
        for i, w in enumerate(col_widths):
            gt.columns[i].width = Inches(w)
    for j, htxt in enumerate(headers):
        c = gt.cell(0, j)
        c.fill.solid(); c.fill.fore_color.rgb = PRIMARY
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        r = c.text_frame.paragraphs[0].add_run(); r.text = htxt
        set_font(r, font, True, WHITE)
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            c = gt.cell(i, j)
            c.fill.solid()
            c.fill.fore_color.rgb = LIGHT if i % 2 == 1 else WHITE
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            r = c.text_frame.paragraphs[0].add_run(); r.text = str(val)
            set_font(r, font, j == 0, DARK if j == 0 else GRAY)
    for i in range(n_rows):
        gt.rows[i].height = Inches(height / n_rows)
    return s


def stat_cards(slide, cards, top=2.1, height=2.2, colors=None):
    n = len(cards)
    cw = (11.93 - 0.3 * (n - 1)) / n
    for i, (num, lab) in enumerate(cards):
        left = Inches(0.7 + i * (cw + 0.3))
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left,
                                      Inches(top), Inches(cw), Inches(height))
        card.fill.solid(); card.fill.fore_color.rgb = LIGHT
        card.line.color.rgb = BORDER; card.shadow.inherit = False
        tf = card.text_frame; tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]; p.alignment = 2
        r = p.add_run(); r.text = num
        set_font(r, 36, True, colors[i] if colors else PRIMARY)
        p2 = tf.add_paragraph(); p2.alignment = 2; p2.space_before = Pt(6)
        r2 = p2.add_run(); r2.text = lab
        set_font(r2, 14, False, GRAY)


def compare_bars(slide, rows, top=1.9, left=2.6, width=8.6, row_h=0.72, max_v=1.0):
    """rows: [(label, v1, v2)]，画两条对比横条。"""
    tb = slide.shapes.add_textbox(Inches(0.75), Inches(top - 0.5), Inches(11.8), Inches(0.4))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    r = p.add_run(); r.text = "■ deepseek-chat    "
    set_font(r, 12, True, PRIMARY)
    r2 = p.add_run(); r2.text = "■ deepseek-reasoner"
    set_font(r2, 12, True, ACCENT)

    for i, (label, v1, v2) in enumerate(rows):
        y = top + i * row_h
        lb = slide.shapes.add_textbox(Inches(0.75), Inches(y), Inches(1.75), Inches(0.55))
        tf = lb.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        r = tf.paragraphs[0].add_run(); r.text = label
        set_font(r, 14, True, DARK)

        for k, (v, color) in enumerate([(v1, PRIMARY), (v2, ACCENT)]):
            by = y + 0.03 + k * 0.26
            bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left),
                                        Inches(by), Inches(width), Inches(0.2))
            bg.fill.solid(); bg.fill.fore_color.rgb = RGBColor(0xEE, 0xEE, 0xEE)
            bg.line.fill.background(); bg.shadow.inherit = False

            w = max(0.02, width * v / max_v)
            bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left),
                                         Inches(by), Inches(w), Inches(0.2))
            bar.fill.solid(); bar.fill.fore_color.rgb = color
            bar.line.fill.background(); bar.shadow.inherit = False

            vt = slide.shapes.add_textbox(Inches(left + width + 0.12), Inches(by - 0.03),
                                          Inches(0.9), Inches(0.26))
            r = vt.text_frame.paragraphs[0].add_run()
            r.text = f"{v:.1%}"
            set_font(r, 11, True, color)


# ---------- 1 封面 ----------
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, prs.slide_width, prs.slide_height, PRIMARY)
rect(s, Inches(0.9), Inches(2.3), Inches(1.7), Inches(0.06), ACCENT)
tb = s.shapes.add_textbox(Inches(0.9), Inches(2.65), Inches(11.5), Inches(2.6))
tf = tb.text_frame; tf.word_wrap = True
r = tf.paragraphs[0].add_run(); r.text = "初中数学 Educational-LLM Benchmark"
set_font(r, 36, True, WHITE)
p2 = tf.add_paragraph(); p2.space_before = Pt(10)
r2 = p2.add_run(); r2.text = "期中汇报"
set_font(r2, 28, False, RGBColor(0xCD, 0xE0, 0xF0))
p3 = tf.add_paragraph(); p3.space_before = Pt(14)
r3 = p3.add_run()
r3.text = "数据集构建完成 ｜ 双模型基础评测"
set_font(r3, 16, False, RGBColor(0xBF, 0xD4, 0xE8))
tb2 = s.shapes.add_textbox(Inches(0.9), Inches(6.3), Inches(11.5), Inches(0.6))
r4 = tb2.text_frame.paragraphs[0].add_run()
r4.text = "汇报人：________     日期：2026 年 11 月     Week 11–13 期中汇报"
set_font(r4, 14, False, RGBColor(0xBF, 0xD4, 0xE8))

# ---------- 2 目录 ----------
s = prs.slides.add_slide(BLANK)
header(s, "目录", "CONTENTS")
bullets(s, [
    "项目进度与数据集成果",
    "评测设计：Prompt 与判分规则",
    "判分器的可靠性与验证",
    "评测结果：总体 / 题型 / 领域 / 难度",
    "关键发现与错误分析",
    "局限与下一步计划",
], top=1.7, size=19)

# ---------- 3 进度 ----------
s = prs.slides.add_slide(BLANK)
header(s, "项目进度", "三个阶段，按期完成")
steps = [
    ("Week 2–4", "选题汇报", "确定选题与方案", "✅ 已完成"),
    ("Week 7–9", "数据集汇报", "构建 200 题真题基准", "✅ 已完成"),
    ("Week 11–13", "期中汇报", "数据集定稿 + 基础评测", "▶ 本次"),
    ("Week 16–18", "期末汇报", "完整评测与分析报告", "待开展"),
]
y = 1.75
for stage, name, desc, status in steps:
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75),
                             Inches(y), Inches(11.85), Inches(1.0))
    box.fill.solid()
    box.fill.fore_color.rgb = LIGHT if status.startswith("✅") else (
        RGBColor(0xE8, 0xF1, 0xF8) if status == "▶ 本次" else WHITE)
    box.line.color.rgb = BORDER; box.shadow.inherit = False
    tf = box.text_frame; tf.word_wrap = True
    tf.margin_left = Inches(0.3); tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    r = p.add_run(); r.text = f"{stage}　"
    set_font(r, 15, True, ACCENT)
    r = p.add_run(); r.text = f"{name}　"
    set_font(r, 16, True, PRIMARY)
    r = p.add_run(); r.text = f"{desc}　　"
    set_font(r, 14, False, GRAY)
    r = p.add_run(); r.text = status
    set_font(r, 15, True, GOLD if status == "▶ 本次" else GRAY)
    y += 1.12

# ---------- 4 数据集成果 ----------
s = prs.slides.add_slide(BLANK)
header(s, "数据集成果", "200 道中考真题，已定稿")
stat_cards(s, [
    ("200", "题目总数"),
    ("20", "中考真题试卷"),
    ("12", "覆盖省市"),
    ("40", "知识点标签"),
], top=2.0, height=2.1)
bullets(s, [
    "题型：单选题 116 · 填空题 57 · 解答题 27",
    "领域：数与代数 111 · 图形与几何 54 · 统计与概率 31 · 综合与实践 4",
    "难度：基础 101 · 中等 74 · 较难 25",
    "全部为真实真题，每题标注年份、地区、题号，可回溯原卷",
], top=4.5, size=15)

# ---------- 5 评测设计 ----------
s = prs.slides.add_slide(BLANK)
header(s, "评测设计", "统一 Prompt + 自动判分")
bullets(s, [
    ("Prompt 模板（两类）", 0),
    ("选择题：只输出正确选项字母 A/B/C/D，不输出其他内容", 1),
    ("填空/解答：只给最终答案，多问用分号分隔，不写过程", 1),
    ("参数：temperature = 0，保证结果可复现", 0),
    ("判分规则", 0),
    ("单选题：从输出中提取选项字母，与标准答案比对", 1),
    ("填空题：归一化后比对（全半角、空格、LaTeX、说明文字）", 1),
    ("解答题：按分号逐问比对，全部答对才计分", 1),
], top=1.7, size=15)

# ---------- 6 判分器验证 ----------
s = prs.slides.add_slide(BLANK)
header(s, "判分器的可靠性", "22 条单元测试全部通过")
bullets(s, [
    ("已覆盖的等价写法", 0),
    ("LaTeX 格式：\\(1.1\\times 10^{12}\\)  ≡  1.1×10¹²", 1),
    ("分数形式：(2)/(5) ≡ 2/5，\\frac{1}{6} ≡ 1/6", 1),
    ("等式前缀：x=3 ≡ 3，y=-x²+1 ≡ -x²+1", 1),
    ("数值等价：-1+√2-1-1 ≡ √2-3，0.5 ≡ 1/2", 1),
    ("不等式：(3<x<10/3) ≡ (x>3；x<10/3)", 1),
    ("说明文字：3（答案不唯一） ≡ 3", 1),
    ("仍存在的局限", 0),
    ("代数恒等变形（如 (b-a)/3 与 1/3b−1/3a）尚未识别，会轻微低估准确率", 1),
], top=1.7, size=14)

# ---------- 7 评测对象 ----------
s = prs.slides.add_slide(BLANK)
header(s, "评测对象", "同一服务商的两个不同能力档位模型")
stat_cards(s, [
    ("deepseek-chat", "通用对话模型"),
    ("deepseek-reasoner", "推理增强模型"),
    ("200", "每题评测题数"),
    ("2 分钟", "单模型评测耗时"),
], top=2.0, height=2.1, colors=[PRIMARY, ACCENT, GRAY, GRAY])
bullets(s, [
    "两个模型来自同一服务商，参数量与训练方式不同，形成天然的能力对照",
    "200 题全量评测，未抽样；每题独立调用，temperature = 0",
    "评测时间：2026 年 11 月",
], top=4.5, size=15)

# ---------- 8 总体结果 ----------
s = prs.slides.add_slide(BLANK)
header(s, "总体结果", "推理模型领先 5 个百分点")
stat_cards(s, [
    ("81.0%", "deepseek-chat"),
    ("86.0%", "deepseek-reasoner"),
    ("+5.0pp", "推理模型提升"),
    ("18.5%", "随机基线（四选一）"),
], top=2.0, height=2.1, colors=[PRIMARY, ACCENT, GOLD, GRAY])
bullets(s, [
    "两个模型都显著高于随机基线，说明基准对模型能力有区分度",
    "推理模型在整体上领先，但差距并非均匀分布——差距主要集中在难题上",
], top=4.5, size=15)

# ---------- 9 按题型 ----------
s = prs.slides.add_slide(BLANK)
header(s, "结果：按题型", "解答题是最大分水岭")
compare_bars(s, [
    ("单选题", 0.905, 0.966),
    ("填空题", 0.860, 0.860),
    ("解答题", 0.296, 0.407),
], top=2.0)
tb = s.shapes.add_textbox(Inches(0.75), Inches(4.5), Inches(11.8), Inches(1.4))
tf = tb.text_frame; tf.word_wrap = True
for i, line in enumerate([
    "• 单选题两者都接近 90%，说明基础知识点掌握良好",
    "• 解答题骤降至 30%~41%，三倍差距——多步推理是主要瓶颈",
    "• 填空题两者持平（86.0%），题型的区分度主要体现在解答题",
]):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(6)
    r = p.add_run(); r.text = line
    set_font(r, 15, False, DARK)

# ---------- 10 按领域 ----------
s = prs.slides.add_slide(BLANK)
header(s, "结果：按领域", "图形与几何最弱，综合与实践几乎空白")
compare_bars(s, [
    ("数与代数", 0.865, 0.919),
    ("图形与几何", 0.722, 0.778),
    ("统计与概率", 0.839, 0.871),
    ("综合与实践", 0.250, 0.250),
], top=1.95)
tb = s.shapes.add_textbox(Inches(0.75), Inches(5.05), Inches(11.8), Inches(1.0))
tf = tb.text_frame; tf.word_wrap = True
for i, line in enumerate([
    "• 数与代数最强，图形与几何低 10 个百分点以上，符合「几何需要辅助线构造」的直觉",
    "• 综合与实践两者都只有 25%，且完全无差异——样本仅 4 题，结论需谨慎",
]):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(5)
    r = p.add_run(); r.text = line
    set_font(r, 14, False, DARK)

# ---------- 11 按难度 ----------
s = prs.slides.add_slide(BLANK)
header(s, "结果：按难度", "差距随难度急剧放大")
compare_bars(s, [
    ("基础", 0.970, 0.960),
    ("中等", 0.716, 0.784),
    ("较难", 0.440, 0.680),
], top=2.0)
tb = s.shapes.add_textbox(Inches(0.75), Inches(4.5), Inches(11.8), Inches(1.4))
tf = tb.text_frame; tf.word_wrap = True
for i, line in enumerate([
    "• 基础题：chat 97.0% 甚至略高于 reasoner 的 96.0% —— 基础题区分度不足",
    "• 中等题：差距 6.8 个百分点",
    "• 较难题：差距扩大到 24 个百分点（44.0% → 68.0%），推理能力优势充分显现",
]):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(6)
    r = p.add_run(); r.text = line
    set_font(r, 15, False, DARK)

# ---------- 12 核心发现 ----------
s = prs.slides.add_slide(BLANK)
header(s, "核心发现", "三条可写进结论的观察")
findings = [
    ("01", "推理能力的价值集中在难题上",
     "基础题两者几乎无差异（97.0% vs 96.0%），但较难题相差 24 个百分点。"
     "说明推理模型并非全面更强，而是「难题才更强」。"),
    ("02", "解答题是当前大模型的真实短板",
     "选择题 90%+，解答题不足 41%。模型能选对答案，但难以独立完成多步推理并给出正确结果。"),
    ("03", "图形与几何是共同弱项",
     "两个模型在图形与几何上分别只有 72.2% 和 77.8%，明显低于数与代数（86.5% / 91.9%）。"),
]
y = 1.62
for num, title, body in findings:
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75),
                             Inches(y), Inches(11.85), Inches(1.55))
    box.fill.solid(); box.fill.fore_color.rgb = LIGHT
    box.line.color.rgb = BORDER; box.shadow.inherit = False
    tf = box.text_frame; tf.word_wrap = True
    tf.margin_left = Inches(0.3); tf.margin_top = Inches(0.12)
    p = tf.paragraphs[0]
    p.alignment = 1
    r = p.add_run(); r.text = num + "　"
    set_font(r, 20, True, GOLD)
    r = p.add_run(); r.text = title
    set_font(r, 16, True, PRIMARY)
    p2 = tf.add_paragraph(); p2.space_before = Pt(4); p2.alignment = 1
    r2 = p2.add_run(); r2.text = body
    set_font(r2, 13, False, GRAY)
    y += 1.68

# ---------- 13 典型错误 ----------
s = table_slide(
    "典型错误分析",
    ["题目", "标准答案", "模型输出", "错误类型"],
    [
        ["解不等式组", "3<x<10/3", "x>3；x<10/3", "格式差异（判分已修正）"],
        ["化简求值", "√2-3", "-1+√2-1-1", "未化简（判分已修正）"],
        ["一元二次方程根与系数", "k>3/4；k=2", "k<3/4；k=-2", "符号错误"],
        ["反比例函数", "-6", "-2", "计算错误"],
        ["三角形相似", "CF=1", "输出大段证明过程", "未按指令给最终答案"],
    ],
    subtitle="错误类型可分为：计算错误、符号错误、指令遵循不足、判分格式差异",
    col_widths=[3.4, 2.6, 3.6, 2.4],
    font=13,
    height=4.4,
)

# ---------- 14 局限 ----------
s = prs.slides.add_slide(BLANK)
header(s, "当前局限", "如实说明，避免过度解读")
bullets(s, [
    ("样本与覆盖", 0),
    ("综合与实践仅 4 题，该维度的 25% 不具备统计意义", 1),
    ("仅评测 2 个模型，且来自同一服务商，代表性有限", 1),
    ("评测方式", 0),
    ("仅测 zero-shot，未对比 few-shot / CoT 提示的效果差异", 1),
    ("解答题只判最终答案，未评估推理过程质量", 1),
    ("数据集", 0),
    ("图形依赖题已被剔除，基准不覆盖「读图」能力", 1),
    ("数与代数占比 55.5%，领域分布不均衡", 1),
], top=1.7, size=15)

# ---------- 15 下一步 ----------
s = prs.slides.add_slide(BLANK)
header(s, "下一步计划", "Week 16–18 期末汇报前")
bullets(s, [
    ("扩充模型：增加 3–5 个模型（Qwen、GLM、GPT 等），形成横向对比", 0),
    ("补充提示策略：对比 zero-shot / few-shot / CoT 三种设置", 0),
    ("扩充综合实践题：把该领域题量从 4 题提升到 20 题以上", 0),
    ("人工复核错题：抽查 50 道错题，确认是模型错误还是判分误差", 0),
    ("产出完整评测报告：模型能力画像 + 错误归因 + 改进建议", 0),
    ("目标：期末形成「数据集 + 多模型评测 + 分析报告」完整闭环", 0),
], top=1.7, size=16)

# ---------- 16 结束页 ----------
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, prs.slide_width, prs.slide_height, PRIMARY)
tb = s.shapes.add_textbox(Inches(1), Inches(2.6), Inches(11.3), Inches(2.2))
tf = tb.text_frame; tf.word_wrap = True
r = tf.paragraphs[0].add_run(); r.text = "谢谢聆听"
set_font(r, 44, True, WHITE)
p2 = tf.add_paragraph(); p2.space_before = Pt(10)
r2 = p2.add_run(); r2.text = "Q & A"
set_font(r2, 24, False, RGBColor(0xCD, 0xE0, 0xF0))
p3 = tf.add_paragraph(); p3.space_before = Pt(20)
r3 = p3.add_run()
r3.text = "初中数学 Educational-LLM Benchmark ｜ 期中汇报"
set_font(r3, 14, False, RGBColor(0xBF, 0xD4, 0xE8))

try:
    prs.save(OUT)
    print("SAVED:", OUT)
except PermissionError:
    alt = OUT.replace(".pptx", "-更新版.pptx")
    prs.save(alt)
    print("原文件被占用，已另存为：", alt)
print("SLIDES:", len(prs.slides._sldIdLst))
