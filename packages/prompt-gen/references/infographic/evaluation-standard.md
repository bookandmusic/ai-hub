# Evaluation Standard

信息图提示词评估标准。定义如何评估用户提示词的质量，决定是否需要进行扩写。

## 评估维度

### Required Results (必需结果)

以下维度必须全部通过（answer="yes"）：

| ID | 维度 | 评估标准 |
|----|------|----------|
| `req_1` | **内容完整性** | 提示词是否包含核心内容/主题？ |
| `req_2` | **可执行性** | 提示词是否足够具体，可被图像生成模型理解？ |
| `req_3` | **结构清晰** | 提示词是否有清晰的结构（布局、内容、风格）？ |

### Optional Results (可选结果)

以下维度需要 ≥ 60% 通过（answer="yes"）：

| ID | 维度 | 评估标准 |
|----|------|----------|
| `opt_1` | **细节丰富** | 提示词是否包含足够的细节（数据、视觉元素、色彩）？ |
| `opt_2` | **风格明确** | 提示词是否明确指定了视觉风格？ |
| `opt_3` | **布局清晰** | 提示词是否明确指定了布局类型？ |
| `opt_4` | **质量词** | 提示词是否包含质量词（high quality, professional 等）？ |
| `opt_5` | **可读性** | 提示词是否考虑了文字可读性？ |

## 评估流程

### 1. 输入

- `user_prompt` — 用户原始提示词

### 2. 评估

对每个维度进行评估，输出 `yes` 或 `no`。

### 3. 判断

```
required_pass = all(req.answer == "yes" for req in required_results)
optional_pass = (count(opt.answer == "yes" for opt in optional_results) / total_optional) >= 0.6

should_expand = not (required_pass and optional_pass)
```

### 4. 输出

评估结果输出为以下 JSON 格式：

```json
{
  "required_results": [
    {"id": "req_1", "dimension": "内容完整性", "answer": "yes|no", "reason": "..."},
    {"id": "req_2", "dimension": "可执行性", "answer": "yes|no", "reason": "..."},
    {"id": "req_3", "dimension": "结构清晰", "answer": "yes|no", "reason": "..."}
  ],
  "optional_results": [
    {"id": "opt_1", "dimension": "细节丰富", "answer": "yes|no", "reason": "..."},
    {"id": "opt_2", "dimension": "风格明确", "answer": "yes|no", "reason": "..."},
    {"id": "opt_3", "dimension": "布局清晰", "answer": "yes|no", "reason": "..."},
    {"id": "opt_4", "dimension": "质量词", "answer": "yes|no", "reason": "..."},
    {"id": "opt_5", "dimension": "可读性", "answer": "yes|no", "reason": "..."}
  ],
  "required_pass": true|false,
  "optional_pass": true|false,
  "should_expand": true|false,
  "expansion_reason": "..."
}
```

## 评估示例

### 输入 1（简单提示词）

```
生成一张远程办公优势信息图
```

### 输出 1

```json
{
  "required_results": [
    {"id": "req_1", "dimension": "内容完整性", "answer": "yes", "reason": "包含核心主题：远程办公优势"},
    {"id": "req_2", "dimension": "可执行性", "answer": "no", "reason": "缺少布局、风格、数据等具体细节"},
    {"id": "req_3", "dimension": "结构清晰", "answer": "no", "reason": "没有明确的结构（布局、内容、风格）"}
  ],
  "optional_results": [
    {"id": "opt_1", "dimension": "细节丰富", "answer": "no", "reason": "缺少数据、视觉元素、色彩等细节"},
    {"id": "opt_2", "dimension": "风格明确", "answer": "no", "reason": "没有指定视觉风格"},
    {"id": "opt_3", "dimension": "布局清晰", "answer": "no", "reason": "没有指定布局类型"},
    {"id": "opt_4", "dimension": "质量词", "answer": "no", "reason": "没有质量词"},
    {"id": "opt_5", "dimension": "可读性", "answer": "no", "reason": "没有考虑文字可读性"}
  ],
  "required_pass": false,
  "optional_pass": false,
  "should_expand": true,
  "expansion_reason": "提示词过于简单，缺少布局、风格、数据等关键信息，需要扩写"
}
```

### 输入 2（详细提示词）

```
Professional infographic about remote work advantages, horizontal timeline layout with 5 sections, 
title: "5 Benefits of Remote Work", clean modern layout with corporate memphis style, 
5 numbered sections with icons: clock for time saving, chart for productivity, wallet for cost, 
balance scale for work-life, leaf for environment, 
data points: 1.8 hours daily saved, 35% productivity increase, $4,500 annual savings, 
87% satisfaction improvement, 3,200 pounds carbon reduction, 
blue and green color palette, professional tone, 
clear typography, well-organized, infographic, clean layout, professional, high quality
```

### 输出 2

```json
{
  "required_results": [
    {"id": "req_1", "dimension": "内容完整性", "answer": "yes", "reason": "包含完整的核心内容和主题"},
    {"id": "req_2", "dimension": "可执行性", "answer": "yes", "reason": "足够具体，包含布局、风格、数据等细节"},
    {"id": "req_3", "dimension": "结构清晰", "answer": "yes", "reason": "结构清晰：布局 + 内容 + 风格 + 数据 + 质量词"}
  ],
  "optional_results": [
    {"id": "opt_1", "dimension": "细节丰富", "answer": "yes", "reason": "包含详细的数据、视觉元素、色彩"},
    {"id": "opt_2", "dimension": "风格明确", "answer": "yes", "reason": "明确指定 corporate memphis 风格"},
    {"id": "opt_3", "dimension": "布局清晰", "answer": "yes", "reason": "明确指定 horizontal timeline 布局"},
    {"id": "opt_4", "dimension": "质量词", "answer": "yes", "reason": "包含多个质量词"},
    {"id": "opt_5", "dimension": "可读性", "answer": "yes", "reason": "明确提到 clear typography"}
  ],
  "required_pass": true,
  "optional_pass": true,
  "should_expand": false,
  "expansion_reason": null
}
```

## 注意事项

1. **保守原则**：评估失败时，默认 `should_expand=true`
2. **必需维度**：所有必需维度必须通过
3. **可选维度**：可选维度通过率 ≥ 60%
4. **记录原因**：每个评估结果必须包含原因
5. **可追溯性**：评估结果用于决定是否扩写，需记录判断依据