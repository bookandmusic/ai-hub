# 概念/创意图像提示词专用评估标准

## 扩展自通用评估标准

此文件扩展 `prompt-critic-system.md`，添加概念/创意图像特有的评估规则。

## 概念/创意图像特有规则

### G. 概念表达完整性

**规则 12 — 核心概念不明确**
- 提示词未清晰传达核心概念或创意主题
- 或概念过于抽象，缺乏视觉化表达
- 示例：只说"创新"而无任何视觉隐喻或具体元素
- 要求：核心概念必须通过具体的视觉元素表达

**规则 13 — 视觉隐喻缺失或不清晰**
- 涉及抽象概念但未使用视觉隐喻或象征元素
- 或隐喻过于晦涩，无法传达预期含义
- 示例：表达"成长"概念但未使用树木、上升箭头等隐喻

### H. 构图和视觉焦点

**规则 14 — 构图类型不适合概念表达**
- 提示词的构图类型与概念表达不匹配
- 或缺少明确的视觉焦点
- 示例：表达"平衡"概念但未使用对称构图

**规则 15 — 视觉层次和元素关系不清晰**
- 多个概念元素之间的层次关系、大小对比、相对位置不明确
- 或缺少视觉引导，无法形成清晰的视觉流
- 示例：多个象征元素平铺，无主次之分

### I. 色彩和情绪

**规则 16 — 色彩方案与概念不匹配**
- 色彩选择与概念要传达的情绪不一致
- 或未描述色彩的象征意义
- 示例：表达"希望"概念但使用灰暗色调

**规则 17 — 情绪氛围描述缺失**
- 未描述整体的情绪氛围（神秘/震撼/宁静/活力/梦幻）
- 或情绪与概念主题矛盾
- 示例：表达"冲突"概念但描述"和谐宁静"的氛围

### J. 创意元素和象征性

**规则 18 — 象征元素过于直白或陈词滥调**
- 使用过于常见、缺乏创意的象征元素
- 示例：表达"时间"概念只用时钟（可以考虑沙漏、日影、年轮等）

**规则 19 — 超现实或抽象元素缺乏逻辑**
- 超现实元素的组合缺乏内在逻辑
- 或抽象程度过高，无法识别任何具象元素
- 示例：随机堆砌不相关的元素，无法形成连贯概念

### K. 风格和艺术表现

**规则 20 — 艺术风格不适合概念表达**
- 艺术风格与概念主题不匹配
- 或风格描述过于笼统
- 示例：表达"科技未来"概念但使用"古典油画风格"

## 概念/创意图像评分维度

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 内容完整性 | 5% | 是否包含所有核心元素，数据是否准确 |
| 描述清晰度 | 10% | 是否具体、明确、无歧义 |
| 技术规范性 | 5% | 是否符合格式要求，是否包含禁止元素 |
| 可执行性 | 5% | 是否可被图像生成模型实现 |
| 概念表达完整性 | 25% | 核心概念是否明确，视觉隐喻是否清晰 |
| 构图和视觉焦点 | 10% | 构图是否适合概念表达，视觉层次是否清晰 |
| 色彩和情绪 | 15% | 色彩方案是否匹配概念，情绪氛围是否协调 |
| 创意元素和象征性 | 15% | 象征元素是否有创意，超现实元素是否有逻辑 |
| 风格和艺术表现 | 10% | 艺术风格是否适合概念表达 |

**通过阈值**：`score >= 0.75` 且无 `critical` 违规 → `PASS`（概念艺术可适当放宽；通用阈值定义见 `prompt-critic-system.md`）

## 评估示例

### 示例 1：不合格提示词

**原始需求**：
```
生成一张表达"时间流逝"概念的创意图像
```

**生成的提示词**：
```
时间的概念，抽象风格，有创意，高质量
```

**评估结果**：
```json
{
  "reasoning": "提示词过于抽象，核心概念'时间流逝'未通过任何具体视觉元素表达，缺少视觉隐喻，未描述构图、色彩、情绪氛围，风格描述过于笼统。",
  "result": "FAIL",
  "score": 0.20,
  "violations": [
    {
      "rule_id": "12",
      "rule_name": "核心概念不明确",
      "detail": "只说'时间的概念'，未通过任何视觉元素表达",
      "severity": "critical",
      "revised_description": "添加视觉元素表达时间流逝，例如：'巨大的沙漏，沙粒从上方流向下方，每个沙粒中包含一个微小的场景或记忆'"
    },
    {
      "rule_id": "13",
      "rule_name": "视觉隐喻缺失或不清晰",
      "detail": "未使用任何隐喻元素（沙漏、时钟、日历、年轮、光影变化等）",
      "severity": "critical",
      "revised_description": "添加视觉隐喻，例如：'融化的时钟（达利风格）、漂浮的日历页、从年轻到衰老的人物变化序列'"
    },
    {
      "rule_id": "16",
      "rule_name": "色彩方案与概念不匹配",
      "detail": "未描述色彩如何表达'流逝'的感觉",
      "severity": "major",
      "revised_description": "添加色彩方案，例如：'从明亮的金色渐变到深沉的蓝灰色，象征从现在到过去，从鲜活到褪色'"
    }
  ],
  "strengths": [],
  "optimization_hints": [
    "可以添加构图方式，例如'对角线构图，从左上到右下，象征时间的流动方向'",
    "可以添加情绪氛围，例如'怀旧而宁静的氛围，带有一丝淡淡的忧伤'",
    "可以指定艺术风格，例如'超现实主义风格，数字绘画，细腻柔和'"
  ]
}
```

### 示例 2：合格提示词

**原始需求**：
```
生成一张表达"时间流逝"概念的创意图像
```

**生成的提示词**：
```
Conceptual art illustrating the passage of time,
central composition with massive ethereal hourglass floating in cosmic space,
golden sand flowing from upper chamber to lower, each grain containing a tiny luminous scene,
upper chamber filled with bright golden light, representing present and future,
lower chamber accumulating darker amber sand, representing past and memories,
around the hourglass, floating fragments of calendars, clock faces, and wilting flowers,
spiral motion lines showing the continuous flow,
background transitions from warm golden yellow at top to deep twilight blue at bottom,
creating a vertical gradient symbolizing temporal progression,
scattered particles of light and dust drifting downward,
dreamy and melancholic atmosphere with a touch of serenity,
soft ethereal lighting with gentle glow emanating from the hourglass,
surrealist style with digital painting technique,
inspired by Salvador Dali's time concepts but more gentle and contemplative,
smooth color transitions, detailed but not cluttered,
conceptual art, philosophical, high quality, ultra-high definition
```

**评估结果**：
```json
{
  "reasoning": "提示词清晰表达了'时间流逝'概念，使用沙漏作为核心视觉隐喻，添加了日历、时钟、花朵等辅助象征元素，构图适合概念表达（中心对称+纵向流动），色彩方案（金色到深蓝）匹配时间流逝的感觉，情绪氛围协调（梦幻忧郁但宁静），艺术风格明确（超现实主义、数字绘画）。",
  "result": "PASS",
  "score": 0.89,
  "violations": [],
  "strengths": [
    "核心概念明确：沙漏作为主要隐喻，清晰传达时间流逝",
    "视觉隐喻丰富：沙漏、日历、时钟、凋谢的花朵，多层次表达",
    "构图适合：中心对称+纵向流动，符合'流逝'的视觉表达",
    "色彩方案匹配：金色到深蓝渐变，象征从现在到过去",
    "情绪氛围协调：梦幻忧郁但宁静，符合时间主题的哲思感",
    "创意元素：每粒沙中包含微小场景，增加创意和细节",
    "艺术风格明确：超现实主义风格，参考达利但更柔和"
  ],
  "optimization_hints": [
    "可以添加更多细节：例如'沙漏玻璃上刻有古老的时间刻度'",
    "可以增强象征性：例如'下方的沙堆中隐约可见被掩埋的记忆碎片'",
    "可以添加人物元素：例如'沙漏旁有一个半透明的人影，静静注视着时间流逝'"
  ]
}
```

## 使用建议

- 评估时优先检查 critical 级别的违规（规则 12, 13）
- 概念图像允许更大的创作自由度，但核心概念必须可识别
- 不同概念类型有不同的视觉表达方式：
  - 抽象概念（爱、希望、自由）→ 象征元素 + 情绪氛围
  - 哲学概念（存在、虚无、永恒）→ 超现实元素 + 深邃氛围
  - 社会概念（联结、孤独、冲突）→ 人物关系 + 环境隐喻
- 创意的平衡：既要有新意（避免陈词滥调），又要可理解（避免晦涩难懂）
- 超现实元素的组合应有内在逻辑，而非随机堆砌
- 色彩和情绪是概念表达的重要工具，必须与主题匹配
