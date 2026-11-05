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
FONT    = "微软雅黑"

OUT = r"C:\Users\34962\AppData\Roaming\CherryStudio\Data\Agents\system\2026-10-07\52df430c-b810-458e-a68a-1cd30754a532\初中数学Educational-LLM-Benchmark-选题汇报.pptx"

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
        if isinstance(it, tuple):
            text, level = it
        else:
            text, level = it, 0
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
                font=14, top=1.65, height=5.55):
    s = prs.slides.add_slide(BLANK)
    header(s, title, subtitle)
    n_rows = len(rows) + 1
    n_cols = len(headers)
    gt = s.shapes.add_table(n_rows, n_cols, Inches(0.7), Inches(top),
                            Inches(11.93), Inches(height)).table
    gt.first_row = False
    gt.horz_banding = False
    if col_widths:
        for i, w in enumerate(col_widths):
            gt.columns[i].width = Inches(w)
    for j, htxt in enumerate(headers):
        cell = gt.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = PRIMARY
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = htxt
        set_font(r, font, True, WHITE)
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            cell = gt.cell(i, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = LIGHT if i % 2 == 1 else WHITE
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            r = p.add_run()
            r.text = str(val)
            set_font(r, font, j == 0, DARK if j == 0 else GRAY)
    for i in range(n_rows):
        gt.rows[i].height = Inches(height / n_rows)
    return s


# ---------- 1. 封面 ----------
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, prs.slide_width, prs.slide_height, PRIMARY)
rect(s, Inches(0.9), Inches(2.35), Inches(1.7), Inches(0.06), ACCENT)
tb = s.shapes.add_textbox(Inches(0.9), Inches(2.7), Inches(11.5), Inches(2.6))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
r = p.add_run()
r.text = "初中数学 Educational-LLM Benchmark"
set_font(r, 40, True, WHITE)
p2 = tf.add_paragraph()
p2.space_before = Pt(10)
r2 = p2.add_run()
r2.text = "选题汇报"
set_font(r2, 28, False, RGBColor(0xCD, 0xE0, 0xF0))
p3 = tf.add_paragraph()
p3.space_before = Pt(16)
r3 = p3.add_run()
r3.text = "课程项目：Educational LLM Benchmark（参考 CMMLU） ｜ 常规项目 —— 初中数学"
set_font(r3, 15, False, RGBColor(0xBF, 0xD4, 0xE8))
tb2 = s.shapes.add_textbox(Inches(0.9), Inches(6.35), Inches(11.5), Inches(0.6))
tf2 = tb2.text_frame
p4 = tf2.paragraphs[0]
r4 = p4.add_run()
r4.text = "汇报人：________     日期：2026 年 10 月     阶段：Week 2–4"
set_font(r4, 14, False, RGBColor(0xBF, 0xD4, 0xE8))

# ---------- 2. 目录 ----------
s = prs.slides.add_slide(BLANK)
header(s, "目录", "CONTENTS")
bullets(s, [
    "选题背景与意义",
    "研究现状与立项动机",
    "研究目标与研究内容",
    "数据集构建方案",
    "评测方案与技术路线",
    "创新点 / 难点 / 进度 / 预期成果",
], top=1.7, size=20)

# ---------- 3. 选题背景 ----------
s = prs.slides.add_slide(BLANK)
header(s, "选题背景", "大模型进课堂，教育能力成为关键瓶颈")
bullets(s, [
    "大语言模型加速进入教育场景：智能答疑、个性化辅导、作业批改、学情分析",
    "教育能力是当前 LLM 的短板，数学尤其需要严谨的多步推理",
    "通用中文基准（CMMLU / C-Eval / AGIEval）粒度粗，难以回答“某个知识点上到底行不行”",
    "数学专项基准（GSM8K / MATH / MGSM）多为英文或竞赛导向，与国内 K12 课标不对齐",
    "教育应用真正需要的是分学段、分知识点、分难度、分题型的“诊断式”评测",
])

# ---------- 4. 问题定位（三大缺口） ----------
s = prs.slides.add_slide(BLANK)
header(s, "现有基准的三方面不足", "为什么需要一个初中数学专项基准")
cards = [
    ("学段空白", "缺少针对“初中数学”这一 K12 关键学段的专门评测基准"),
    ("粒度粗", "通用基准只有总分，无法定位模型“哪个知识点薄弱”"),
    ("不对齐", "现有数学基准不遵循国内课程标准，难以直接指导教学"),
]
cw = 3.8
gap = 0.25
for i, (t, b) in enumerate(cards):
    left = Inches(0.7 + i * (cw + gap))
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(2.0),
                              Inches(cw), Inches(2.7))
    card.fill.solid()
    card.fill.fore_color.rgb = LIGHT
    card.line.color.rgb = BORDER
    card.shadow.inherit = False
    ctf = card.text_frame
    ctf.word_wrap = True
    ctf.margin_left = Inches(0.22)
    ctf.margin_right = Inches(0.22)
    ctf.margin_top = Inches(0.2)
    cp = ctf.paragraphs[0]
    cr = cp.add_run()
    cr.text = t
    set_font(cr, 22, True, PRIMARY)
    cp2 = ctf.add_paragraph()
    cp2.space_before = Pt(10)
    cr2 = cp2.add_run()
    cr2.text = b
    set_font(cr2, 15, False, DARK)

# ---------- 5. 研究现状对比 ----------
s = table_slide(
    "研究现状：主流评测基准对比",
    ["基准", "语言", "定位", "特点"],
    [
        ["MMLU", "英文", "通用多任务理解", "57 学科，含基础数学"],
        ["CMMLU", "中文", "通用多任务理解", "67 学科，覆盖自然科学/社科/工程/人文"],
        ["C-Eval", "中文", "多学科分层评测", "52 学科、4 难度等级，约 1.4 万题"],
        ["AGIEval", "中英", "真实考试基准", "以高考、司法考试等真实试题为基准"],
        ["GSM8K", "英文", "小学数学应用题", "8500 道，强调多步推理"],
        ["MATH", "英文", "竞赛数学", "5000 道，难度高"],
        ["MGSM", "多语言", "小学数学应用题", "GSM8K 的多语言扩展"],
    ],
    col_widths=[1.4, 1.2, 2.4, 6.9],
    font=13,
)

# ---------- 6. 立项动机 ----------
s = prs.slides.add_slide(BLANK)
header(s, "立项动机", "数学能力仍是短板，值得做一个诊断基准")
bullets(s, [
    ("CMMLU 评测了 18 个主流多语言/中文模型，即便给出上下文示例与思维链（CoT）提示，多数模型平均准确率仍不足 50%，随机基线仅为 25%", 0),
    ("这说明大模型在中文知识理解与推理上仍有巨大提升空间", 0),
    ("数学需要严谨推理，是检验模型“真懂还是背题”的最佳试金石", 0),
    ("结论：值得构建一个对齐课标、可诊断的初中数学专项基准", 0),
])
# 高亮结论条
bar = rect(s, Inches(0.75), Inches(6.0), Inches(11.83), Inches(0.9), PRIMARY)
btf = bar.text_frame
btf.word_wrap = True
bp = btf.paragraphs[0]
br = bp.add_run()
br.text = "立项结论：做一个“对齐课标”的初中数学 LLM 教育能力诊断基准"
set_font(br, 18, True, WHITE)

# ---------- 7. 研究目标 ----------
s = prs.slides.add_slide(BLANK)
header(s, "研究目标", "构建基准 + 系统评测 + 能力分析")
bullets(s, [
    "构建一个覆盖初中数学课程标准的细粒度中文评测基准（参考 CMMLU 的题目与评测形式）",
    "建立“知识点 × 难度 × 题型”三维分类体系，并完成题目标注",
    "系统评测主流大模型（开源 + 闭源），得到整体准确率与分维度子分数",
    "分析模型的能力画像与共性薄弱点，输出《主流大模型初中数学教育能力评测分析报告》",
])

# ---------- 8. 研究内容总览 ----------
s = prs.slides.add_slide(BLANK)
header(s, "研究内容总览", "两大模块：数据集构建 + 评测分析")
bullets(s, [
    ("数据集构建：真题改编 + 教材习题改编 + 人工命题", 0),
    ("分类体系：对齐《义务教育数学课程标准（2022）》四大领域", 0),
    ("评测方案：zero-shot / few-shot / CoT 对比评测", 0),
    ("分析输出：多维统计 + 错误归因 + 能力画像", 0),
])

# ---------- 9. 数据集构建 - 题目来源 ----------
s = prs.slides.add_slide(BLANK)
header(s, "数据集构建：题目来源", "多渠道采集，兼顾质量与版权")
bullets(s, [
    "中考真题改编：改写数字与情境，规避版权风险",
    "教材例题与习题改编：人教版 / 北师大版等主流教材",
    "教师人工命题 + 专家审核，保证题目质量",
    ("每题统一标注：知识点、难度、题型、标准答案、解析、来源", 0),
])

# ---------- 10. 分类体系 ----------
s = prs.slides.add_slide(BLANK)
header(s, "数据集构建：分类体系", "对齐《义务教育数学课程标准（2022）》四大领域")
bullets(s, [
    ("数与代数：有理数 / 整式 / 方程 / 不等式 / 实数 / 函数（一次、反比例、二次）", 0),
    ("图形与几何：三角形 / 全等相似 / 勾股定理 / 四边形 / 圆 / 图形变换 / 三角函数", 0),
    ("统计与概率：数据收集整理 / 统计图表 / 概率初步", 0),
    ("综合与实践：跨知识点综合应用题", 0),
])

# ---------- 11. 题型 / 难度 / 规模 ----------
s = prs.slides.add_slide(BLANK)
header(s, "数据集构建：题型 / 难度 / 规模", "前期以客观题为主，便于自动评测")
bullets(s, [
    "题型：前期以单选题（4 选项）为主，与 CMMLU 对齐；后续扩展填空 / 解答题",
    "难度：基础 / 中等 / 较难 三级，对应中考易、中、难题分布",
    "规模：第一阶段 2000–3000 题，最终约 5000 题（可按进度调整）",
])

# ---------- 12. 评测方案 ----------
s = prs.slides.add_slide(BLANK)
header(s, "评测方案", "多模型、多配置、多维指标")
bullets(s, [
    "评测方式：zero-shot / few-shot，并对比是否使用 CoT（思维链）提示",
    "评测指标：整体准确率 + 知识点/难度/题型分维度子准确率 + 错误类型分析",
    "评测模型：DeepSeek、GPT、Qwen、GLM、文心、豆包、Kimi 等主流中英文模型",
    "评测框架：基于 OpenCompass / lm-evaluation-harness 等开源框架",
])

# ---------- 13. 技术路线 ----------
s = prs.slides.add_slide(BLANK)
header(s, "技术路线", "四阶段推进")
bullets(s, [
    ("阶段一 · 方案设计：梳理课标与考纲 → 设计分类体系与标注规范", 0),
    ("阶段二 · 数据构建：真题/教材改编 + 人工命题 → 清洗标注 → 交叉校验", 0),
    ("阶段三 · 评测实施：搭建评测框架 → 多模型多配置批量评测", 0),
    ("阶段四 · 分析汇报：多维统计 → 错误归因 → 报告撰写与展示", 0),
])

# ---------- 14. 创新点 ----------
s = prs.slides.add_slide(BLANK)
header(s, "创新点", "三个关键词")
bullets(s, [
    ("学段垂直化：聚焦初中数学这一被通用基准忽略的关键学段", 0),
    ("课标对齐：分类体系对齐《义务教育数学课程标准（2022）》，结果可直接指导教学", 0),
    ("诊断式多维评测：知识点 × 难度 × 题型画像，定位“哪里不会、为什么错”", 0),
])

# ---------- 15. 难点与风险 ----------
s = table_slide(
    "难点与风险",
    ["难点 / 风险", "应对措施"],
    [
        ["真题版权问题", "一律改编（改数字/情境），并注明来源"],
        ["标注一致性难保证", "制定标注规范 + 双人交叉校验 + 抽检"],
        ["评测 API 成本高", "优先开源模型本地推理，闭源模型控制调用量"],
        ["解答题难以自动判分", "前期以单选题为主，解答题作为后续扩展"],
        ["模型更新迭代快", "固定评测时间点与模型版本号，保证可比性"],
    ],
    col_widths=[3.4, 8.5],
    font=14,
)

# ---------- 16. 可行性分析 ----------
s = prs.slides.add_slide(BLANK)
header(s, "可行性分析", "资源、工具、方法、人力均可支撑")
bullets(s, [
    "资源充分：中考真题、教材、教辅等公开资源丰富，可支撑数据构建",
    "工具成熟：OpenCompass、lm-evaluation-harness 等开源评测框架可直接复用",
    "方法可参考：CMMLU、C-Eval 等基准提供了成熟的构建与评测范式",
    "个人可控：任务模块清晰、边界明确，可按阶段顺序独立推进（本项目单人完成）",
])

# ---------- 17. 进度安排 ----------
s = table_slide(
    "进度安排（对齐课程节点）",
    ["阶段", "时间", "交付内容"],
    [
        ["选题汇报", "Week 2–4", "选题确定 + 方案设计（本次）"],
        ["数据集汇报", "Week 7–9", "分类体系 + 数据采集与构建进展"],
        ["期中汇报", "Week 11–13", "完成数据集构建 + 基础评测"],
        ["期末汇报", "Week 16–18", "完整评测 + 分析报告 + 全部基础要求"],
    ],
    col_widths=[2.2, 2.4, 7.3],
    font=14,
)

# ---------- 18. 预期成果 ----------
s = prs.slides.add_slide(BLANK)
header(s, "预期成果", "数据集 + 评测结果 + 分析报告")
bullets(s, [
    "初中数学 Benchmark 数据集（三维分类体系 + 题目标注 + 质检记录）",
    "主流大模型评测结果（整体准确率 + 分维度子分数）",
    "教育能力分析报告（能力画像 + 错误归因 + 建议）",
    "可复用的评测代码框架与 Prompt 模板",
    "项目汇报 PPT 与项目文档",
])

# ---------- 19. 个人工作安排 ----------
s = prs.slides.add_slide(BLANK)
header(s, "个人工作安排", "本项目单人完成，按阶段顺序推进")
bullets(s, [
    ("选题与方案：确定选题、梳理课标、设计分类与评测方案（本次汇报）", 0),
    ("数据构建：真题/教材改编 + 命题 → 清洗标注 → 质检", 0),
    ("评测实施：搭建评测框架 → 多模型评测 → 结果统计", 0),
    ("分析汇报：错误归因 → 能力画像 → 报告撰写 → 期末汇报", 0),
], size=18)
bar = rect(s, Inches(0.75), Inches(6.0), Inches(11.83), Inches(0.9), ACCENT)
btf = bar.text_frame
btf.word_wrap = True
bp = btf.paragraphs[0]
br = bp.add_run()
br.text = "策略：任务模块化、分阶段独立推进，善用开源工具（OpenCompass 等）降低工作量"
set_font(br, 16, True, WHITE)

# ---------- 20. 结束页 ----------
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, prs.slide_width, prs.slide_height, PRIMARY)
tb = s.shapes.add_textbox(Inches(1), Inches(2.6), Inches(11.3), Inches(2.0))
tf = tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
r = p.add_run()
r.text = "谢谢聆听"
set_font(r, 44, True, WHITE)
p2 = tf.add_paragraph()
p2.space_before = Pt(10)
r2 = p2.add_run()
r2.text = "Q & A"
set_font(r2, 24, False, RGBColor(0xCD, 0xE0, 0xF0))
p3 = tf.add_paragraph()
p3.space_before = Pt(20)
r3 = p3.add_run()
r3.text = "初中数学 Educational-LLM Benchmark ｜ 选题汇报"
set_font(r3, 14, False, RGBColor(0xBF, 0xD4, 0xE8))

prs.save(OUT)
print("SAVED:", OUT)
