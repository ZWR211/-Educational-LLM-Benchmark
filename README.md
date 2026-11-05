# 初中数学 Educational-LLM Benchmark

一个面向**初中数学教育能力评测**的中文基准数据集，参考 CMMLU 的构建方式，
题目全部来自 2021–2026 年各省市中考数学真题。

## 数据集概览

| 指标 | 数值 |
|---|---|
| 题目总数 | 200 |
| 来源试卷 | 20 份（中考真题） |
| 覆盖地区 | 12 省市 |
| 知识点标签 | 40 个 |
| 年份跨度 | 2021 – 2026 |

**题型分布**

| 题型 | 数量 | 判分方式 |
|---|---:|---|
| 单选题 | 116 | 选项字母精确匹配 |
| 填空题 | 57 | 最终答案文本匹配 |
| 解答题 | 27 | 按最终答案判分，过程不计 |

**领域分布**

| 领域 | 数量 |
|---|---:|
| 数与代数 | 111 |
| 图形与几何 | 54 |
| 统计与概率 | 31 |
| 综合与实践 | 4 |

**难度分布**

| 难度 | 数量 |
|---|---:|
| 基础 | 101 |
| 中等 | 74 |
| 较难 | 25 |

## 数据格式

数据集文件：`data/math_benchmark.json`，为 JSON 数组，每题一个对象：

```json
{
  "id": "NA-0001",
  "domain": "数与代数",
  "knowledge_point": "科学记数法与近似数",
  "difficulty": "基础",
  "type": "单选题",
  "question": "……",
  "options": ["A. …", "B. …", "C. …", "D. …"],
  "answer": "B",
  "analysis": "……",
  "source": "2023年北京市中考数学试卷 第1题（原题收录）",
  "source_type": "真题",
  "batch": "北京2023",
  "verify_status": "已人工校验"
}
```

字段说明：

| 字段 | 说明 |
|---|---|
| `id` | 唯一编号，领域代码 + 流水号（NA/GG/SP/CP） |
| `domain` | 四大领域之一 |
| `knowledge_point` | 知识点标签（共 40 个） |
| `difficulty` | 基础 / 中等 / 较难 |
| `type` | 单选题 / 填空题 / 解答题 |
| `answer` | 单选题为选项字母；其他为最终答案文本 |
| `source` | 真实出处，可回溯到原卷 |
| `source_type` | 真题 |
| `batch` | 采集批次（地区 + 年份） |
| `verify_status` | 校验状态 |

## 目录结构

```
.
├── data/
│   └── math_benchmark.json     # 200 题数据集
├── scripts/
│   ├── build_dataset.py        # 由分片构建数据集：合并、去重、重编号
│   ├── dataset_stats.py        # 校验与分布统计，生成统计报告
│   ├── svg_text.py             # 从试卷预览 SVG 提取文字
│   ├── add_real_sources.py     # 真题并入
│   ├── merge_dataset.py        # 多分片合并
│   ├── relabel_sources.py      # 来源字段规范化
│   └── drop_synthetic.py       # 清理合成数据
└── generate_*.py               # 汇报 PPT 生成脚本
```

## 使用方法

```bash
# 校验数据集并生成统计报告
uv run python scripts/dataset_stats.py

# 由分片重新构建数据集
uv run python scripts/build_dataset.py
```

## 数据来源说明

题目来自公开可访问的中考真题资源（各地中考原卷），每题均在 `source` 字段标注
年份、地区与题号，可回溯核对。原始试卷图片与 PDF 未纳入版本库。

## 说明

- 全部题目均为真实中考真题，无合成或生成题目
- 每题经过人工复算校验
- 数据用于课程项目与非商业研究
