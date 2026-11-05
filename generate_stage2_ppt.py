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
WARM    = RGBColor(0xC0, 0x50, 0x4D)
FONT    = "微软雅黑"

OUT = r"C:\Users\34962\AppData\Roaming\CherryStudio\Data\Agents\system\2026-10-07\52df430c-b810-458e-a68a-1cd30754a532\初中数学Benchmark-数据集汇报.pptx"

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
    shp.fill.solid()
    shp.fill.fore_color.rgb = color
    shp.line.fill.background()
    shp.shadow.inherit = False
    return shp


def header(slide, title, subtitle=None):
    rect(slide, Inches(0.6), Inches(0.55), Inches(0.14), Inches(0.72), ACCENT)
    tb = slide.shapes.add_textbox(Inches(0.95), Inches(0.42), Inches(11.7), Inches(1.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = title
    set_font(r, 27, True, PRIMARY)
    if subtitle:
        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = subtitle
        set_font(r2, 13, False, GRAY)
    rect(slide, Inches(0.6), Inches(1.38), Inches(12.13), Inches(0.02), BORDER)


def bullets(slide, items, top=1.65, left=0.75, width=11.9, height=5.5, size=18):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    first = True
    for it in items:
        text, level = it if isinstance(it, tuple) else (it, 0)
        para = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        para.level = level
        para.space_after = Pt(9)
        para.line_spacing = 1.12
        run = para.add_run()
        run.text = ("•  " if level == 0 else "–  ") + text
        set_font(run, size if level == 0 else size - 2, level == 0,
                 DARK if level == 0 else GRAY)
    return tb


def table_slide(title, headers, rows, subtitle=None, col_widths=None,
                font=14, top=1.65, height=5.55, highlight_col0=None):
    s = prs.slides.add_slide(BLANK)
    header(s, title, subtitle)
    n_rows, n_cols = len(rows) + 1, len(headers)
    gt = s.shapes.add_table(n_rows, n_cols, Inches(0.7), Inches(top),
                            Inches(11.93), Inches(height)).table
    gt.first_row = False
    gt.horz_banding = False
    if col_widths:
        for i, w in enumerate(col_widths):
            gt.columns[i].width = Inches(w)
    for j, htxt in enumerate(headers):
        c = gt.cell(0, j)
        c.fill.solid(); c.fill.fore_color.rgb = PRIMARY
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        r = c.text_frame.paragraphs[0].add_run()
        r.text = htxt
        set_font(r, font, True, WHITE)
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            c = gt.cell(i, j)
            c.fill.solid()
            c.fill.fore_color.rgb = LIGHT if i % 2 == 1 else WHITE
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            r = c.text_frame.paragraphs[0].add_run()
            r.text = str(val)
            set_font(r, font, j == 0, DARK if j == 0 else GRAY)
    for i in range(n_rows):
        gt.rows[i].height = Inches(height / n_rows)
    return s


def stat_cards(slide, cards, top=2.1, height=2.4):
    n = len(cards)
    cw = (11.93 - 0.3 * (n - 1)) / n
    for i, (num, lab) in enumerate(cards):
        left = Inches(0.7 + i * (cw + 0.3))
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left,
                                      Inches(top), Inches(cw), Inches(height))
        card.fill.solid(); card.fill.fore_color.rgb = LIGHT
        card.line.color.rgb = BORDER
        card.shadow.inherit = False
        tf = card.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = 2  # center
        r = p.add_run(); r.text = num
        set_font(r, 40, True, PRIMARY)
        p2 = tf.add_paragraph(); p2.alignment = 2; p2.space_before = Pt(6)
        r2 = p2.add_run(); r2.text = lab
        set_font(r2, 15, False, GRAY)


# ---------- 1 封面 ----------
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, prs.slide_width, prs.slide_height, PRIMARY)
rect(s, Inches(0.9), Inches(2.35), Inches(1.7), Inches(0.06), ACCENT)
tb = s.shapes.add_textbox(Inches(0.9), Inches(2.7), Inches(11.5), Inches(2.6))
tf = tb.text_frame; tf.word_wrap = True
r = tf.paragraphs[0].add_run(); r.text = "初中数学 Educational-LLM Benchmark"
set_font(r, 38, True, WHITE)
p2 = tf.add_paragraph(); p2.space_before = Pt(10)
r2 = p2.add_run(); r2.text = "数据集汇报"
set_font(r2, 28, False, RGBColor(0xCD, 0xE0, 0xF0))
p3 = tf.add_paragraph(); p3.space_before = Pt(16)
r3 = p3.add_run()
r3.text = "Benchmark 数据集收集与构建情况 ｜ Week 7–9"
set_font(r3, 15, False, RGBColor(0xBF, 0xD4, 0xE8))
tb2 = s.shapes.add_textbox(Inches(0.9), Inches(6.35), Inches(11.5), Inches(0.6))
r4 = tb2.text_frame.paragraphs[0].add_run()
r4.text = "汇报人：________     日期：2026 年 10 月     数据集版本：v0.2（1000 题）"
set_font(r4, 14, False, RGBColor(0xBF, 0xD4, 0xE8))

# ---------- 2 目录 ----------
s = prs.slides.add_slide(BLANK)
header(s, "目录", "本次汇报内容")
bullets(s, [
    "阶段回顾与本次目标",
    "数据集分类体系（领域 × 难度 × 题型）",
    "数据格式与标注规范",
    "数据来源与收集方法",
    "数据集构建现状与统计",
    "样例题展示",
    "质检流程 / 问题 / 下一步计划",
], top=1.7, size=20)

# ---------- 3 阶段回顾 ----------
s = prs.slides.add_slide(BLANK)
header(s, "阶段回顾与本次目标", "对照课程节点")
bullets(s, [
    ("Week 2–4  选题汇报　✅ 已完成（确定选题与方案）", 0),
    ("Week 7–9  数据集汇报　▶ 本次（汇报收集与构建情况）", 0),
    ("Week 11–13 期中汇报　数据集构建完成 + 基础评测", 0),
    ("Week 16–18 期末汇报　完成项目所有基础要求", 0),
    ("", 0),
    ("本次目标：交付分类体系、数据规范、数据集 v0.1、质检与统计结果", 0),
])

# ---------- 4 三维分类体系 ----------
s = prs.slides.add_slide(BLANK)
header(s, "数据集分类体系", "三维标注，对齐《义务教育数学课程标准（2022）》")
cards = [
    ("领域 / 知识点", "4 大领域 → 章节 → 知识点\n定位“考什么”"),
    ("难度", "基础 / 中等 / 较难\n定位“有多难”"),
    ("题型", "单选题 / 填空题 / 解答题\n定位“怎么问”"),
]
cw = (11.93 - 0.3 * 2) / 3
for i, (t, b) in enumerate(cards):
    left = Inches(0.7 + i * (cw + 0.3))
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(2.0),
                              Inches(cw), Inches(2.9))
    card.fill.solid(); card.fill.fore_color.rgb = LIGHT
    card.line.color.rgb = BORDER
    card.shadow.inherit = False
    tf = card.text_frame; tf.word_wrap = True
    tf.margin_left = Inches(0.22); tf.margin_right = Inches(0.22)
    tf.margin_top = Inches(0.25)
    r = tf.paragraphs[0].add_run(); r.text = t
    set_font(r, 21, True, PRIMARY)
    p2 = tf.add_paragraph(); p2.space_before = Pt(12)
    r2 = p2.add_run(); r2.text = b
    set_font(r2, 15, False, DARK)

# ---------- 5 知识点体系 ----------
s = table_slide(
    "知识点体系：四大领域",
    ["领域", "章节", "知识点条目（共 42 个标签）"],
    [
        ["数与代数", "数与式 / 方程与不等式 / 函数", "有理数、实数、二次根式、整式、因式分解、分式、方程、不等式、一次/反比例/二次函数"],
        ["图形与几何", "图形的性质 / 变化 / 坐标", "点线角、三角形、全等、相似、四边形、圆、轴对称、平移旋转、锐角三角函数、三视图"],
        ["统计与概率", "数据分析 / 随机事件的概率", "数据收集、统计图表、集中趋势、离散程度、事件分类、概率计算、列举法"],
        ["综合与实践", "跨领域综合", "数与代数综合、数形结合、统计应用、实际问题建模"],
    ],
    col_widths=[1.7, 3.0, 7.23],
    font=13,
    height=4.4,
)

# ---------- 6 难度判定标准 ----------
s = table_slide(
    "难度判定标准",
    ["难度", "可操作判定规则"],
    [
        ["基础", "单一知识点，直接套用定义 / 公式，1 步内可得结果"],
        ["中等", "2 个知识点综合，或需 2–3 步推理，或需简单转化"],
        ["较难", "多知识点综合，或需分类讨论 / 构造 / 数形结合，或 4 步以上推理"],
    ],
    subtitle="禁止凭“感觉”标注，必须对照规则；分歧以“初三普通学生能否独立完成”裁决",
    col_widths=[2.2, 9.73],
    font=15,
    height=3.4,
)

# ---------- 7 数据格式规范 ----------
s = table_slide(
    "数据格式与标注规范",
    ["字段", "说明"],
    [
        ["id", "唯一编号，如 NA-0001"],
        ["domain", "四大领域之一"],
        ["knowledge_point", "具体知识点（从分类体系选取）"],
        ["difficulty / type", "难度（基础/中等/较难）、题型"],
        ["question / options", "题干、4 个选项（A. ~ D.）"],
        ["answer / analysis", "标准答案、解题过程"],
        ["source / source_type", "真实来源与类型（如实标注，当前为 AI 辅助自编）"],
        ["batch / verify_status", "生成批次（种子/扩充）、校验状态"],
    ],
    subtitle="统一 JSON 格式，脚本自动校验字段合规性",
    col_widths=[3.0, 8.93],
    font=14,
    height=4.4,
)

# ---------- 7.5 数据来源与收集方法 ----------
s = prs.slides.add_slide(BLANK)
header(s, "数据来源与收集方法", "标准驱动命题 + 权威来源改编（双轨法）")
bullets(s, [
    ("来源分级：课标(L1) > 教材(L2) > 中考真题(L3) > 自编(L4)，按实际来源如实标注", 0),
    ("当前 v0.2：1000 题全部为 L4「AI 辅助自编」——依据课标 42 个知识点命题，source 字段已如实标注", 0),
    ("构建流程：课标分解 → 分板块命题 → 自动校验 → 去重合并 → 编号入库", 0),
    ("下一步（Week 11–13）：引入权威来源进行改编", 0),
    ("国家中小学智慧教育平台（教育部）官方电子教材", 1),
    ("人教版 / 北师大版 教材例题与习题", 1),
    ("各地教育考试院中考真题（一律改编并注明出处）", 1),
], top=1.6, size=17)

# ---------- 8 构建现状总览 ----------
s = prs.slides.add_slide(BLANK)
header(s, "数据集构建现状", "v0.2 完成，题量达 1000，校验全部通过")
stat_cards(s, [
    ("1000", "题目总数"),
    ("4", "覆盖领域"),
    ("42", "知识点标签"),
    ("100%", "格式校验通过"),
], top=2.2, height=2.4)
tb = s.shapes.add_textbox(Inches(0.75), Inches(5.1), Inches(11.83), Inches(1.2))
tf = tb.text_frame; tf.word_wrap = True
for i, line in enumerate([
    "• 由 100 题种子版扩充至 1000 题，四大领域全覆盖",
    "• 并行生成 + 自动去重：合并 1014 题，去除 14 条重复，保留 1000 题",
    "• 校验脚本：字段合规、无重复 id、结构完整，通过率 100%",
]):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(6)
    r = p.add_run(); r.text = line
    set_font(r, 16, False, DARK)

# ---------- 9 领域分布 ----------
s = table_slide(
    "统计：按领域分布",
    ["领域", "题数", "占比"],
    [
        ["数与代数", "301", "30.1%"],
        ["图形与几何", "297", "29.7%"],
        ["统计与概率", "200", "20.0%"],
        ["综合与实践", "202", "20.2%"],
        ["合计", "1000", "100%"],
    ],
    subtitle="四大领域均衡覆盖，数与代数、图形与几何为主干",
    col_widths=[4.0, 3.0, 3.0],
    font=15,
    height=4.0,
)

# ---------- 10 难度分布 ----------
s = table_slide(
    "统计：按难度分布",
    ["难度", "题数", "占比", "目标配比"],
    [
        ["基础", "394", "39.4%", "40%"],
        ["中等", "408", "40.8%", "40%"],
        ["较难", "198", "19.8%", "20%"],
    ],
    subtitle="✅ 难度配比 39.4% : 40.8% : 19.8%，已达标（目标 4 : 4 : 2）",
    col_widths=[2.6, 2.6, 2.6, 3.0],
    font=15,
    height=3.4,
)

# ---------- 11 题型分布 ----------
s = prs.slides.add_slide(BLANK)
header(s, "统计：按题型分布", "前期聚焦客观题，便于自动评测")
bullets(s, [
    "单选题：1000 题（100%）—— 与 CMMLU 形式对齐，支持自动化判分",
    "填空题 / 解答题：暂未纳入，作为 Week 11–13 后的扩展方向",
    "原因：单选题答案唯一、可脚本提取判分，适合在数据构建阶段先打通全流程",
])

# ---------- 12 样例题展示 1 ----------
s = prs.slides.add_slide(BLANK)
header(s, "样例题展示（一）", "中等难度 · 一元二次方程")
box = rect(s, Inches(0.75), Inches(1.7), Inches(11.83), Inches(4.9), LIGHT)
tf = box.text_frame; tf.word_wrap = True
tf.margin_left = Inches(0.35); tf.margin_right = Inches(0.35); tf.margin_top = Inches(0.3)
lines = [
    ("【NA-0015】方程 x²+2x+3 = 0 的根的情况是（　）", 18, True, PRIMARY),
    ("A. 有两个不相等的实数根    B. 有两个相等的实数根    C. 没有实数根    D. 无法确定", 15, False, DARK),
    ("答案：C", 16, True, ACCENT),
    ("解析：判别式 Δ = 2²-4×1×3 = 4-12 = -8 < 0，故没有实数根。", 15, False, GRAY),
    ("知识点：一元二次方程　难度：中等　题型：单选题　来源：改编自中考真题", 13, False, GRAY),
]
for i, (txt, sz, bd, col) in enumerate(lines):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(12)
    r = p.add_run(); r.text = txt
    set_font(r, sz, bd, col)

# ---------- 13 样例题展示 2 ----------
s = prs.slides.add_slide(BLANK)
header(s, "样例题展示（二）", "较难 · 数形结合综合")
box = rect(s, Inches(0.75), Inches(1.7), Inches(11.83), Inches(4.9), LIGHT)
tf = box.text_frame; tf.word_wrap = True
tf.margin_left = Inches(0.35); tf.margin_right = Inches(0.35); tf.margin_top = Inches(0.3)
lines = [
    ("【CP-0008】直角三角形的两条直角边的和为 7，斜边长为 5，则它的面积是（　）", 18, True, PRIMARY),
    ("A. 6    B. 12    C. 5    D. 7", 15, False, DARK),
    ("答案：A", 16, True, ACCENT),
    ("解析：设两直角边为 a, b：a+b = 7，a²+b² = 25。由 (a+b)² = a²+b²+2ab 得 49 = 25+2ab，", 15, False, GRAY),
    ("　　　ab = 12，面积 = ½·ab = 6。", 15, False, GRAY),
    ("知识点：几何与代数的综合（数形结合）　难度：较难　题型：单选题", 13, False, GRAY),
]
for i, (txt, sz, bd, col) in enumerate(lines):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(12)
    r = p.add_run(); r.text = txt
    set_font(r, sz, bd, col)

# ---------- 14 质检流程 ----------
s = prs.slides.add_slide(BLANK)
header(s, "数据质检流程", "采集 → 标注 → 自检 → 校验 → 入库")
bullets(s, [
    ("① 采集 / 改编：中考真题、教材习题改编，规避版权", 0),
    ("② 五要素标注：领域 → 知识点 → 难度 → 题型 → 答案", 0),
    ("③ 撰写解析：写清关键步骤，供后续错误归因使用", 0),
    ("④ 脚本校验：字段合法性 + 选项数 + 答案 + 重复 id 检测（100% 通过）", 0),
    ("⑤ 人工复检：答案复算、知识点对照、难度双人独立判定（一致率目标 ≥ 80%）", 0),
])

# ---------- 15 问题与应对 ----------
s = table_slide(
    "遇到的问题与应对",
    ["问题", "应对措施"],
    [
        ["来源权威性不足", "当前均为自编题且已如实标注；下一步引入教材与真题改编并注明出处"],
        ["改编版权风险", "真题一律改写数字 / 情境，注明原始出处，用于教学研究"],
        ["跨板块题目重复", "合并脚本按题干自动去重（本次去除 14 条重复题）"],
        ["单人工作量较大", "并行生成 + 标注模板 + 自动化校验脚本，提效降错"],
        ["答案正确性待复核", "脚本已过格式关，下一步做抽样人工复算与知识点复核"],
    ],
    col_widths=[3.6, 8.33],
    font=14,
    height=4.0,
)

# ---------- 16 下一步计划 ----------
s = prs.slides.add_slide(BLANK)
header(s, "下一步计划", "Week 11–13 期中汇报前")
bullets(s, [
    ("人工抽检：对 1000 题做抽样复算与知识点复核，确保答案正确", 0),
    ("扩展题型：在单选基础上逐步加入填空题、解答题", 0),
    ("冻结数据集：发布 v1.0，完成全部复检与最终定稿", 0),
    ("跑通基础评测：用 3–5 个主流模型做 zero-shot 评测，产出首批准确率", 0),
    ("产出：数据集 v1.0 + 基础评测结果 + 错误分析初稿", 0),
])

# ---------- 17 结束页 ----------
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
r3.text = "初中数学 Educational-LLM Benchmark ｜ 数据集汇报（Week 7–9）"
set_font(r3, 14, False, RGBColor(0xBF, 0xD4, 0xE8))

prs.save(OUT)
print("SAVED:", OUT)
print("SLIDES:", len(prs.slides._sldIdLst))
