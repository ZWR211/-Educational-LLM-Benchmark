# 初中数学 Educational-LLM Benchmark

面向**初中数学教育能力评测**的中文基准数据集，参考 CMMLU 的构建方式。
题目全部来自 2021–2026 年各省市中考数学真题，只收录**客观题**（单选、填空）。

## 数据集文件位置

| 文件 | 说明 |
|---|---|
| **`dataset/questions.json`** | 主交付文件，JSON 数组，共 173 题 |
| **`dataset/questions.jsonl`** | 同样内容，一行一题，便于批量处理 |
| `data/math_benchmark.json` | 内部源数据（含额外字段），由 `data/sources/` 分片构建 |
| `data/sources/*.json` | 按试卷分片的原始题目，供重建与追溯 |

`dataset/` 下的两个文件采用课程**统一 10 字段模板**，可直接提交。

## 数据集概览

| 指标 | 数值 |
|---|---|
| 题目总数 | 173 |
| 来源试卷 | 20 份（中考真题） |
| 覆盖地区 | 12 省市 |
| 知识点标签 | 38 个 |
| 年份跨度 | 2021 – 2026 |

**题型分布**

| 题型 | question_type | 数量 |
|---|---|---:|
| 单选题 | `single_choice` | 116 |
| 填空题 | `fill_blank` | 57 |

**领域分布**

| 领域 | 数量 |
|---|---:|
| 数与代数 | 98 |
| 图形与几何 | 47 |
| 统计与概率 | 27 |
| 综合与实践 | 1 |

**难度分布**

| 难度 | 数量 |
|---|---:|
| 基础 | 95 |
| 中等 | 59 |
| 较难 | 19 |

## 数据格式（统一模板）

```json
{
  "question_type": "single_choice",
  "question": "截至 2021 年 12 月 31 日，……用科学记数法表示应为（　）",
  "img_url": null,
  "choices": {
    "A": "26.2883×10¹⁰",
    "B": "2.62883×10¹¹",
    "C": "2.62883×10¹²",
    "D": "0.262883×10¹²"
  },
  "answers": ["B"],
  "grade": 9,
  "subject": "数学",
  "source": "2022年北京市中考数学试卷 第2题（原题收录）",
  "source_url": null,
  "meta_data": {
    "group_name": "初中数学 Educational-LLM Benchmark",
    "domain": "数与代数",
    "difficulty": "基础",
    "knowledge_points": ["科学记数法与近似数"],
    "explanation": "262883000000 共 12 位整数，写成 2.62883×10¹¹。",
    "paper_name": "北京2022",
    "question_number": "BJ2022-02",
    "source_type": "真题",
    "verify_status": "已人工校验",
    "original_id": "NA-0001"
  }
}
```

字段说明：

| 字段 | 说明 |
|---|---|
| `question_type` | `single_choice` 单选 / `fill_blank` 填空 |
| `question` | 完整题干，可含 LaTeX |
| `img_url` | 本数据集题目均为纯文本，无图，固定为 `null` |
| `choices` | 单选题为 `{"A": "...", ...}`；填空题为 `{}` |
| `answers` | 单选题填选项编号；填空题填完整答案 |
| `grade` | 固定 `9`（初三） |
| `subject` | 固定 `数学` |
| `source` | 年份 + 地区 + 试卷名 + 原题号，可回溯 |
| `source_url` | 无公开稳定链接，填 `null` |
| `meta_data` | 领域、难度、知识点、解析等小组自定义信息 |

## 目录结构

```
.
├── dataset/
│   ├── questions.json          # 交付用数据集（统一模板）
│   └── questions.jsonl         # 同上，一行一题
├── data/
│   ├── math_benchmark.json     # 内部源数据
│   └── sources/*.json          # 按试卷分片的原始题目
└── scripts/
    ├── build_dataset.py        # 由分片构建数据集：合并、去重、重编号
    ├── to_template.py          # 转换为课程统一 10 字段模板
    ├── dataset_stats.py        # 校验与分布统计
    └── evaluate.py             # 模型评测脚本（含自动判分）
```

## 使用方法

```bash
# 由分片重新构建内部数据集
uv run python scripts/build_dataset.py

# 转换为统一模板格式（生成 dataset/questions.json）
uv run python scripts/to_template.py
```

## 数据来源说明

题目来自公开可访问的中考真题资源（各地中考原卷），每题均在 `source` 字段标注
年份、地区与题号，可回溯核对。原始试卷图片与 PDF 未纳入版本库。

## 说明

- 全部题目均为真实中考真题，无合成或生成题目
- 每题经过人工复算校验
- 仅收录纯文本可作答的客观题；依赖图形的题目已剔除
- 数据用于课程项目与非商业研究
