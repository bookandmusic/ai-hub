# 物体/产品展示提示词专用评估标准

## 扩展自通用评估标准

此文件扩展 `prompt-critic-system.md`，添加物体/产品展示特有的评估规则。

## 物体/产品展示特有规则

### G. 物体描述完整性

**规则 12 — 物体核心特征缺失**
- 提示词未描述物体的关键特征（形状、材质、颜色、尺寸、纹理）
- 示例：只说"一个产品"而无任何特征描述
- 要求：至少包含 4-5 个可识别的物体特征

**规则 13 — 产品细节和品质感不足**
- 涉及产品展示但未描述细节（表面质感、工艺细节、品牌元素）
- 或品质感描述与产品定位不匹配
- 示例：高端产品但描述"简单朴素"

### H. 展示方式和构图

**规则 14 — 展示构图类型缺失**
- 提示词未明确展示方式（主角特写/细节放大/情境展示/平铺排列/悬浮展示）
- 或视角不明确（正面/侧面/45度角/俯视/仰视）
- 示例：未说明是单品特写还是场景化展示

**规则 15 — 物体位置和角度不清晰**
- 未描述物体在画面中的位置（居中/黄金分割点/前景/背景）
- 或拍摄角度与物体特性不匹配
- 示例：手表产品但用俯视角度（应该用 45 度角展示表盘）

### I. 光影和材质表现

**规则 16 — 光影不足以展现材质**
- 未描述光照方式（工作室布光/自然光/戏剧性光影）
- 或光影无法突出物体的材质特性（金属、玻璃、布料、木材等）
- 示例：金属产品但未描述高光和反射

**规则 17 — 材质质感描述缺失**
- 提到材质但未描述质感细节
- 示例："金属材质" vs "拉丝不锈钢，细腻的纹理，柔和的亚光表面"

### J. 背景和环境

**规则 18 — 背景选择不当**
- 背景与物体类型、用途不匹配
- 或背景过于复杂，干扰物体主体
- 示例：科技产品但用自然森林背景

**规则 19 — 背景与物体的关系不清晰**
- 未描述背景的虚化程度、颜色、留白
- 或物体与背景的对比度不足
- 示例：白色产品配白色背景，无对比度

### K. 商业和用途展示

**规则 20 — 产品使用场景缺失**
- 情境展示类型但未描述使用场景或搭配元素
- 示例：说"生活化展示"但未描述具体场景（桌面/厨房/户外等）

## 物体/产品展示评分维度

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 内容完整性 | 5% | 是否包含所有核心元素，数据是否准确 |
| 描述清晰度 | 10% | 是否具体、明确、无歧义 |
| 元素具体性 | 10% | 视觉细节是否充分，位置关系是否清晰 |
| 技术规范性 | 5% | 是否符合格式要求，是否包含禁止元素 |
| 可执行性 | 5% | 是否可被图像生成模型实现 |
| 物体描述完整性 | 20% | 是否包含核心特征，产品细节和品质感是否充分 |
| 展示方式和构图 | 15% | 展示构图类型是否明确，物体位置和角度是否清晰 |
| 光影和材质表现 | 15% | 光影是否突出材质，材质质感描述是否充分 |
| 背景和环境 | 10% | 背景选择是否恰当，背景与物体关系是否清晰 |
| 商业和用途展示 | 5% | 使用场景是否明确（情境展示时） |

**通过阈值**：`score >= 0.80` 且无 `critical` 违规 → `PASS`（通用阈值定义见 `prompt-critic-system.md`）

## 评估示例

### 示例 1：不合格提示词

**原始需求**：
```
生成一张高端手表的产品展示图
```

**生成的提示词**：
```
一块手表，高端风格，精美，高质量
```

**评估结果**：
```json
{
  "reasoning": "提示词过于抽象，缺少物体核心特征（材质、颜色、款式、表盘设计），未描述展示方式和视角，未描述光影如何突出手表的质感，背景不明确。",
  "result": "FAIL",
  "score": 0.25,
  "violations": [
    {
      "rule_id": "12",
      "rule_name": "物体核心特征缺失",
      "detail": "只说'一块手表'，无材质、颜色、款式、表盘设计等描述",
      "severity": "critical",
      "revised_description": "添加手表特征，例如：'瑞士机械表，不锈钢表壳，深蓝色表盘，罗马数字刻度，皮革表带'"
    },
    {
      "rule_id": "14",
      "rule_name": "展示构图类型缺失",
      "detail": "未明确展示方式（特写/45度角/俯视等）",
      "severity": "critical",
      "revised_description": "明确展示方式，例如：'45度角展示，表盘正对镜头，能看到表冠和部分表带'"
    },
    {
      "rule_id": "16",
      "rule_name": "光影不足以展现材质",
      "detail": "未描述光照如何突出手表的金属质感和表盘细节",
      "severity": "major",
      "revised_description": "添加光影描述，例如：'工作室三点布光，主光从左侧照射，在不锈钢表壳上形成柔和高光，凸显金属质感'"
    }
  ],
  "strengths": [
    "指定了高端定位"
  ],
  "optimization_hints": [
    "可以添加背景描述，例如'深灰色渐变背景，简洁专业'",
    "可以添加产品细节，例如'蓝宝石水晶表镜，透视机械机芯'",
    "可以添加拍摄参数，例如'微距镜头，浅景深，焦点在表盘上'"
  ]
}
```

### 示例 2：合格提示词

**原始需求**：
```
生成一张高端手表的产品展示图
```

**生成的提示词**：
```
Luxury Swiss mechanical watch product photography,
stainless steel case with brushed finish, polished edges,
deep blue sunburst dial with silver Roman numeral hour markers,
silver luminous hands, date window at 3 o'clock position,
genuine brown leather strap with contrast stitching,
45-degree angle view showcasing the dial face and side profile,
watch positioned at golden ratio point in frame,
three-point studio lighting setup,
main light from 45-degree left creating highlights on steel case,
fill light softening shadows, rim light separating watch from background,
sapphire crystal glass with subtle reflections,
showcasing intricate details of crown and lugs,
deep charcoal gray gradient background, fading to black,
shallow depth of field, focus on dial and hands,
macro lens perspective, sharp details, professional product photography,
commercial style, high-end luxury aesthetic,
photorealistic, ultra-detailed, ultra-high definition
```

**评估结果**：
```json
{
  "reasoning": "提示词完整描述了手表的核心特征（材质、颜色、表盘设计、表带），展示方式明确（45度角特写），光影充分描述（三点布光、高光反射），材质质感突出（拉丝不锈钢、皮革纹理），背景恰当（深灰色渐变），商业风格明确（高端奢华）。",
  "result": "PASS",
  "score": 0.93,
  "violations": [],
  "strengths": [
    "物体特征完整：材质、颜色、表盘设计、表带、表壳工艺全部描述",
    "展示方式明确：45度角、黄金分割点构图",
    "光影充分：三点布光详细描述，突出金属质感和细节",
    "材质质感具体：拉丝不锈钢、抛光边缘、蓝宝石水晶、皮革缝线",
    "背景恰当：深灰色渐变，简洁专业，不干扰主体",
    "商业风格明确：高端奢华定位，商业摄影风格"
  ],
  "optimization_hints": [
    "可以添加品牌元素：例如'品牌logo清晰可见在表盘顶部'",
    "可以添加环境反射：例如'表壳上有微弱的环境反射，增加真实感'",
    "可以添加使用场景暗示：例如'背景模糊的西装袖口，暗示商务场景'"
  ]
}
```

## 使用建议

- 评估时优先检查 critical 级别的违规（规则 12, 14）
- 不同产品类型有不同的关键特征：
  - 电子产品：屏幕、接口、材质、按键、指示灯
  - 珠宝：宝石、金属、切工、光泽、镶嵌工艺
  - 化妆品：包装、材质、品牌元素、色彩、质感
  - 食品：色泽、质感、摆盘、新鲜度、配料
- 展示方式应匹配产品特性：
  - 平面产品（书籍、海报）→ 正面平拍
  - 立体产品（手表、包包）→ 45度角或侧面
  - 细节工艺（珠宝、机械）→ 微距特写
  - 使用场景（家具、服装）→ 情境展示
- 光影是产品摄影的关键，必须充分描述
