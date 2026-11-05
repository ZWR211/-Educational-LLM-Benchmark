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
GOLD    = RGBColor(0xB8, 0x86, 0x0B)
FONT    = "微软雅黑"

OUT = r"C:\Users\34962\AppData\Roaming\CherryStudio\Data\Agents\system\2026-10-07\52df430c-b810-458e-a68a-1cd30754a532\初中数学Benchmark-数据集构建汇报.pptx"

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
    r = tf.paragraphs[0].add_run()
    r.text = title
    set_font(r, 27, True, PRIMARY)
    if subtitle:
        p2 = tf.add_paragraph()
        r2 = p2.add_run()
        r2.text = subtitle
        set_font(r2, 13, False, GRAY)
    rect(slide, Inches(0.6), Inches(1.38), Inches(12.13), Inches(0.02), BORDER)


def bullets(slide, items, top=1.65, left=0.75, width=11.9, height=5.4, size=17):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    first = True
    for it in items:
        text, level = it if isinstance(it, tuple) else (it, 0)
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.level = level
        p.space_after = Pt(8)
        p.line_spacing = 1.1
        r = p.add_run()
        r.text = ("•  " if level == 0 else "–  ") + text
        set_font(r, size if level == 0 else size - 2, level == 0,
                 DARK if level == 0 else GRAY)
    return tb


def table_slide(title, headers, rows, subtitle=None, col_widths=None,
                font=13, top=1.62, height=5.5, mono_cols=()):
    s = prs.slides.add_slide(BLANK)
    header(s, title, subtitle)
    n_rows, n_cols = len(rows) + 1, len(headers)
    gt = s.shapes.add_table(n_rows, n_cols, Inches(0.65), Inches(top),
                            Inches(12.0), Inches(height)).table
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
            set_font(r, font - 1 if j in mono_cols else font,
                     j == 0, DARK if j == 0 else GRAY)
    for i in range(n_rows):
        gt.rows[i].height = Inches(height / n_rows)
    return s


def stat_cards(slide, cards, top=2.15, height=2.3):
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
        p = tf.paragraphs[0]; p.alignment = 2
        r = p.add_run(); r.text = num
        set_font(r, 38, True, PRIMARY)
        p2 = tf.add_paragraph(); p2.alignment = 2; p2.space_before = Pt(6)
        r2 = p2.add_run(); r2.text = lab
        set_font(r2, 14, False, GRAY)


# ---------- 1 封面 ----------
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, prs.slide_width, prs.slide_height, PRIMARY)
rect(s, Inches(0.9), Inches(2.3), Inches(1.7), Inches(0.06), ACCENT)
tb = s.shapes.add_textbox(Inches(0.9), Inches(2.65), Inches(11.5), Inches(2.6))
tf = tb.text_frame; tf.word_wrap = True
r = tf.paragraphs[0].add_run(); r.text = "初中数学 Educational-LLM Benchmark"
set_font(r, 36, True, WHITE)
p2 = tf.add_paragraph(); p2.space_before = Pt(10)
r2 = p2.add_run(); r2.text = "数据集构建汇报"
set_font(r2, 28, False, RGBColor(0xCD, 0xE0, 0xF0))
p3 = tf.add_paragraph(); p3.space_before = Pt(14)
r3 = p3.add_run()
r3.text = "200 道中考真题 · 20 份试卷 · 12 省市 · 40 个考点"
set_font(r3, 16, False, RGBColor(0xBF, 0xD4, 0xE8))
tb2 = s.shapes.add_textbox(Inches(0.9), Inches(6.3), Inches(11.5), Inches(0.6))
r4 = tb2.text_frame.paragraphs[0].add_run()
r4.text = "汇报人：________     日期：2026 年 10 月     Week 7–9 数据集汇报"
set_font(r4, 14, False, RGBColor(0xBF, 0xD4, 0xE8))

# ---------- 2 目录 ----------
s = prs.slides.add_slide(BLANK)
header(s, "目录", "CONTENTS")
bullets(s, [
    "数据集总览与建设成果",
    "数据来源：采集地址与渠道",
    "采集方法与质量控制",
    "数据结构统计（题型 / 领域 / 难度 / 考点）",
    "试卷清单与样例展示",
    "困难应对与下一步计划",
], top=1.7, size=19)

# ---------- 3 建设成果 ----------
s = prs.slides.add_slide(BLANK)
header(s, "数据集建设成果", "从 0 到 200 道真实中考真题")
stat_cards(s, [
    ("200", "题目总数"),
    ("20", "中考真题试卷"),
    ("12", "覆盖省市"),
    ("40", "知识点标签"),
], top=2.1, height=2.2)
bullets(s, [
    "全部为 2021–2026 年各省市中考真题，无任何合成或 AI 生成题目",
    "每题人工复算校验，标注真实出处（年份 + 地区 + 题号）",
    "覆盖选择、填空、解答三种题型，可按最终答案自动判分",
], top=4.9, size=16)

# ---------- 3.5 采集过程与工作量 ----------
s = table_slide(
    "采集过程与工作量",
    ["环节", "工作内容", "产出"],
    [
        ["① 检索定位", "按「年份 + 地区 + 中考数学真题」逐地检索，逐一确认公开可访问", "20 份试卷"],
        ["② 批量下载", "按页序拉取高清试卷图，本地留存原卷备查", "约 120 页"],
        ["③ 逐页读题", "通读全部页面，逐题记录题干、选项与答案线索", "约 500 道"],
        ["④ 筛选求解", "剔除图形依赖题与纯证明题；解答题逐题人工求解", "200 道（含 27 道解答）"],
        ["⑤ 入库校验", "统一 Schema 写入，去重、格式校验、分维度统计", "去重 3 条，校验 100%"],
    ],
    subtitle="从约 500 道候选题中筛选出 200 道可评测题，入选率约 40%",
    col_widths=[2.2, 7.3, 2.5],
    font=14,
    height=4.5,
)

# ---------- 4 数据来源总览 ----------
s = table_slide(
    "数据来源：三个公开渠道",
    ["来源", "资源类型", "采集形式", "试卷数"],
    [
        ["通通好课网", "中考真题原卷（各地市）", "高清图片逐页采集", "14"],
        ["教习网", "中考真题原卷 / 解析版", "文档预览采集", "3"],
        ["公开 PDF 资源", "教育考试院及公开渠道发布", "PDF 原文解析", "3"],
    ],
    subtitle="三个渠道均为公开可访问资源，未绕过登录或付费墙",
    col_widths=[2.6, 4.4, 3.6, 1.4],
    font=14,
    height=3.4,
)

# ---------- 5 主渠道：通通好课 ----------
s = prs.slides.add_slide(BLANK)
header(s, "主渠道：通通好课网（14 份试卷）", "各地市中考原卷，逐页高清图，单卷产出 7–18 题")
bullets(s, [
    ("资源特点", 0),
    ("覆盖各年度、各地市的中考数学原卷，按页提供高清图片", 1),
    ("公开页面即可查看完整试卷，无需登录", 1),
    ("已采集地区（14 份）", 0),
    ("湖北：随州、武汉、十堰、黄石、仙桃", 1),
    ("四川：成都　｜　青海：西宁　｜　湖南：长沙　｜　浙江：绍兴、台州", 1),
    ("山东：潍坊　｜　甘肃：武威　｜　河北　｜　上海", 1),
    ("采集方式", 0),
    ("按页序批量下载整卷 → 逐页读题 → 人工求解并校验", 1),
], top=1.65, size=15)

# ---------- 6 辅助渠道 ----------
s = prs.slides.add_slide(BLANK)
header(s, "辅助渠道：教习网 + 公开 PDF（6 份试卷）", "用于补充年份跨度与地区覆盖")
bullets(s, [
    ("教习网（3 份）", 0),
    ("提供中考真题原卷与解析版文档预览", 1),
    ("预览页可直接读取文字内容，适合快速提取", 1),
    ("已采集：北京 2026、广东 2026、海南 2026", 1),
    ("公开 PDF 资源（3 份）", 0),
    ("来自教育考试院及公开渠道发布的原始试卷 PDF", 1),
    ("已采集：2022 北京、2023 北京、2024 浙江", 1),
    ("部分试卷附带官方答案，可直接用于交叉核对", 1),
], top=1.65, size=15)

# ---------- 7 采集方法 ----------
s = prs.slides.add_slide(BLANK)
header(s, "采集方法：五步流程", "从找到试卷到题目入库")
steps = [
    ("① 检索定位", "搜索引擎检索「XX年XX市中考数学真题 原卷版」，\n定位到通通好课 / 教习网等公开试卷页"),
    ("② 获取直链", "从页面源码中提取预览图 CDN 地址\n（img 标签的 src 属性）"),
    ("③ 下载高清图", "按 p001–p0NN 批量下载 JPG/SVG，\n保留原始页面以备核查"),
    ("④ 读题与求解", "逐页读取题目，剔除图形依赖题、\n表述不清题；解答题人工解出最终答案"),
    ("⑤ 入库校验", "按统一 Schema 写入 JSON，\n脚本校验格式、去重、统计"),
]
y = 1.6
for i, (t, b) in enumerate(steps):
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75),
                             Inches(y), Inches(11.85), Inches(0.95))
    box.fill.solid(); box.fill.fore_color.rgb = LIGHT if i % 2 == 0 else WHITE
    box.line.color.rgb = BORDER
    box.shadow.inherit = False
    tf = box.text_frame; tf.word_wrap = True
    tf.margin_left = Inches(0.25); tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    r = p.add_run(); r.text = t + "　"
    set_font(r, 15, True, PRIMARY)
    r2 = p.add_run(); r2.text = b.replace("\n", " ")
    set_font(r2, 13, False, DARK)
    y += 1.05

# ---------- 8 质量控制 ----------
s = table_slide(
    "数据质量控制",
    ["检查项", "具体做法", "工作量 / 结果"],
    [
        ["来源真实", "每题 source 字段标注年份、地区、题号，可回溯原卷", "200 题全部标注"],
        ["答案正确", "逐题人工复算；有官方答案的交叉核对", "200 题复算 + 27 道解答逐题求解"],
        ["题目去重", "题干归一化（去空格、统一括号）后比对", "剔除重复 3 条"],
        ["格式合规", "脚本校验字段完整性、选项数、答案格式", "200 题 100% 通过"],
        ["考点标注", "按课标四大领域归入 40 个知识点标签", "40 个标签全覆盖"],
    ],
    subtitle="数据集可被脚本自动校验与统计，保证可复现",
    col_widths=[2.0, 7.0, 3.0],
    font=13,
    height=4.4,
)

# ---------- 9 题型分布 ----------
s = table_slide(
    "数据结构：题型分布",
    ["题型", "题数", "占比", "判分方式"],
    [
        ["单选题", "116", "58.0%", "选项字母精确匹配"],
        ["填空题", "57", "28.5%", "最终答案文本匹配"],
        ["解答题", "27", "13.5%", "按最终答案判分，过程不计"],
        ["合计", "200", "100%", "—"],
    ],
    subtitle="三种题型均支持自动化判分",
    col_widths=[2.6, 2.6, 2.6, 4.2],
    font=15,
    height=3.4,
)

# ---------- 10 领域分布 ----------
s = table_slide(
    "数据结构：领域分布",
    ["领域", "题数", "占比", "说明"],
    [
        ["数与代数", "111", "55.5%", "中考客观题的主力"],
        ["图形与几何", "54", "27.0%", "含圆、四边形、变换、三角函数"],
        ["统计与概率", "31", "15.5%", "含统计图表、概率计算"],
        ["综合与实践", "4", "2.0%", "实际建模与跨领域应用"],
    ],
    subtitle="数与代数占比偏高，源于中考客观题的天然分布",
    col_widths=[2.6, 2.2, 2.2, 5.0],
    font=15,
    height=3.6,
)

# ---------- 11 难度分布 ----------
s = table_slide(
    "数据结构：难度分布",
    ["难度", "题数", "占比", "判定标准"],
    [
        ["基础", "101", "50.5%", "单一知识点，直接套用，1 步可得"],
        ["中等", "74", "37.0%", "2 个知识点或 2–3 步推理"],
        ["较难", "25", "12.5%", "多知识点综合 / 分类讨论 / 4 步以上"],
    ],
    subtitle="难度按可操作规则标注，非主观判断",
    col_widths=[2.4, 2.2, 2.2, 5.2],
    font=15,
    height=3.4,
)

# ---------- 12 考点覆盖 ----------
s = prs.slides.add_slide(BLANK)
header(s, "考点覆盖：40 个知识点标签", "已补齐此前的空白考点")
left = s.shapes.add_textbox(Inches(0.7), Inches(1.6), Inches(6.0), Inches(5.0))
tf = left.text_frame; tf.word_wrap = True
lines_l = [
    ("覆盖最充分的考点", True),
    ("科学记数法与近似数（12）", False),
    ("有理数及其运算（12）", False),
    ("因式分解（8）", False),
    ("整式运算（8）", False),
    ("数据的集中趋势（8）", False),
    ("多边形与四边形（8）", False),
    ("一元二次方程（7）", False),
    ("二次函数（7）", False),
]
for i, (t, b) in enumerate(lines_l):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(5)
    r = p.add_run(); r.text = t
    set_font(r, 15 if b else 14, b, PRIMARY if b else DARK)

right = s.shapes.add_textbox(Inches(6.9), Inches(1.6), Inches(5.8), Inches(5.0))
tf2 = right.text_frame; tf2.word_wrap = True
lines_r = [
    ("本轮重点补充的空白考点", True),
    ("平移（0 → 1）", False),
    ("旋转与中心对称（0 → 1）", False),
    ("数据的收集（0 → 1）", False),
    ("全等三角形（1 → 2）", False),
    ("三角形的性质（1 → 3）", False),
    ("锐角三角函数（2 → 5）", False),
    ("轴对称与轴对称图形（1）", False),
    ("事件的分类（1）", False),
]
for i, (t, b) in enumerate(lines_r):
    p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
    p.space_after = Pt(5)
    r = p.add_run(); r.text = t
    set_font(r, 15 if b else 14, b, GOLD if b else DARK)

# ---------- 13 试卷清单 ----------
s = table_slide(
    "试卷清单（20 份）",
    ["地区", "年份", "题数", "地区", "年份", "题数"],
    [
        ["湖北随州", "2022", "18", "北京", "2026", "8"],
        ["青海西宁", "2023", "17", "广东", "2026", "8"],
        ["湖南长沙", "2023", "16", "山东潍坊", "2023", "8"],
        ["浙江绍兴", "2023", "16", "湖北仙桃", "2022", "8"],
        ["上海", "2023", "15", "浙江台州", "2021", "7"],
        ["四川成都", "2023", "11", "甘肃武威", "2023", "7"],
        ["海南", "2026", "10", "浙江", "2024", "7"],
        ["湖北黄石", "2022", "10", "北京", "2023", "6"],
        ["湖北十堰", "2022", "10", "河北", "2022", "6"],
        ["湖北武汉", "2022", "9", "北京", "2022", "3"],
    ],
    subtitle="覆盖 12 省市，年份跨度 2021–2026",
    col_widths=[2.1, 1.3, 1.2, 2.1, 1.3, 1.2],
    font=12,
    height=5.2,
)

# ---------- 14 样例题 1 ----------
s = prs.slides.add_slide(BLANK)
header(s, "样例题展示（一）", "单选题 · 平移 · 2023 山东潍坊")
box = rect(s, Inches(0.75), Inches(1.65), Inches(11.83), Inches(4.9), LIGHT)
tf = box.text_frame; tf.word_wrap = True
tf.margin_left = Inches(0.35); tf.margin_right = Inches(0.35); tf.margin_top = Inches(0.3)
lines = [
    ("在直角坐标系中，菱形 OABC 顶点 A 的坐标为 (-2, 0)，∠AOC = 60°．", 17, True, PRIMARY),
    ("将菱形沿 x 轴向右平移 1 个单位，再沿 y 轴向下平移 1 个单位，", 17, True, PRIMARY),
    ("得到菱形 O'A'B'C'，其中点 B' 的坐标为（　）", 17, True, PRIMARY),
    ("A. (-2, √3-1)　　B. (-2, 1)　　C. (-√3, 1)　　D. (-√3, √3-1)", 15, False, DARK),
    ("答案：A", 16, True, ACCENT),
    ("解析：C(-1, √3)，B = A+C-O = (-3, √3)；平移后 B' = (-2, √3-1)。", 15, False, GRAY),
    ("来源：2023年山东省潍坊市中考数学试卷 第6题", 13, False, GRAY),
]
for i, (txt, sz, bd, col) in enumerate(lines):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(10)
    r = p.add_run(); r.text = txt
    set_font(r, sz, bd, col)

# ---------- 15 样例题 2 ----------
s = prs.slides.add_slide(BLANK)
header(s, "样例题展示（二）", "解答题 · 综合实践 · 2023 浙江绍兴")
box = rect(s, Inches(0.75), Inches(1.65), Inches(11.83), Inches(4.9), LIGHT)
tf = box.text_frame; tf.word_wrap = True
tf.margin_left = Inches(0.35); tf.margin_right = Inches(0.35); tf.margin_top = Inches(0.3)
lines = [
    ("一条笔直的路上依次有 M，P，N 三地，其中 M，N 两地相距 1000 米．", 16, True, PRIMARY),
    ("甲、乙两机器人分别从 M，N 同时出发，匀速相向而行，OA、BC 分别表示", 16, True, PRIMARY),
    ("甲、乙离 M 地的距离 y（米）与时间 x（分钟）的函数关系图象．", 16, True, PRIMARY),
    ("（1）求 OA 所在直线的表达式；", 15, False, DARK),
    ("（2）出发后甲行走多少时间与乙相遇？", 15, False, DARK),
    ("（3）甲到 P 地后再过 1 分钟乙也到 P 地，求 P、M 两地距离．", 15, False, DARK),
    ("答案：（1）y=200x；（2）10/3 分钟；（3）600 米", 16, True, ACCENT),
    ("来源：2023年浙江省绍兴市中考数学试卷 第20题（按最终答案判分）", 13, False, GRAY),
]
for i, (txt, sz, bd, col) in enumerate(lines):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.space_after = Pt(9)
    r = p.add_run(); r.text = txt
    set_font(r, sz, bd, col)

# ---------- 16 困难与应对 ----------
s = table_slide(
    "采集中的困难与应对",
    ["困难", "具体表现", "应对"],
    [
        ["公式为图片", "教习网预览图中公式不随文本导出", "改为整页截图读取"],
        ["站点限流", "连续请求出现 502 / 超时", "切换通通好课渠道"],
        ["图形依赖题", "约 1/3 客观题需原图才能作答", "直接剔除，不做改编"],
        ["解答题耗时", "需人工完整求解才能得到最终答案", "优先选统计、应用类可判分题"],
        ["考点重复", "科学记数法、有理数等反复出现", "后期专挑空白考点采集"],
    ],
    col_widths=[2.4, 5.6, 4.0],
    font=13,
    height=4.6,
)

# ---------- 17 下一步 ----------
s = prs.slides.add_slide(BLANK)
header(s, "下一步计划", "Week 11–13 期中汇报前")
bullets(s, [
    ("冻结数据集 v1.0：完成全部题目复核，形成正式版本", 0),
    ("构建评测框架：统一 prompt 模板 + 批量调用主流模型", 0),
    ("评测模型：DeepSeek、Qwen、GLM、GPT、豆包等 3–5 个", 0),
    ("产出首批结果：整体准确率 + 分领域 / 分题型准确率", 0),
    ("错误归因：区分概念错误、计算错误、推理断裂", 0),
    ("目标：期中汇报时给出「数据集 + 基础评测」完整闭环", 0),
], top=1.7, size=17)

# ---------- 18 结束页 ----------
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
r3.text = "初中数学 Educational-LLM Benchmark ｜ 数据集构建汇报"
set_font(r3, 14, False, RGBColor(0xBF, 0xD4, 0xE8))

try:
    prs.save(OUT)
    print("SAVED:", OUT)
except PermissionError:
    alt = OUT.replace(".pptx", "-更新版.pptx")
    prs.save(alt)
    print("原文件被占用（可能正在 WPS 中打开），已另存为：", alt)
print("SLIDES:", len(prs.slides._sldIdLst))
