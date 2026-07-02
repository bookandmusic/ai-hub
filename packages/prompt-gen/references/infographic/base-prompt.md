# Base Prompt Template

信息图基础提示词模板。定义信息图提示词的基本结构和元素。

## 基础结构

### 标准格式

```
[构图描述], [信息图类型], [标题], [核心内容], [数据元素], [布局说明], [风格描述], [色彩方案], [质量词]
```

### 元素说明

| 元素 | 描述 | 示例 |
|------|------|------|
| **构图描述** | 布局类型和结构 | `horizontal timeline layout with 5 sections` |
| **信息图类型** | 内容类型 | `infographic about remote work advantages` |
| **标题** | 信息图标题 | `title: "5 Benefits of Remote Work"` |
| **核心内容** | 主要要点/数据 | `5 key benefits with icons and data points` |
| **数据元素** | 具体数据点 | `1.8 hours daily saved, 35% productivity increase` |
| **布局说明** | 布局细节 | `numbered list with connecting arrows` |
| **风格描述** | 视觉风格 | `clean modern layout with corporate memphis style` |
| **色彩方案** | 色彩搭配 | `blue and green color palette` |
| **质量词** | 质量描述 | `infographic, clean layout, professional, high quality` |

## 布局模板

### Timeline (时间线)

```
[时间线类型] layout showing [主题], [时间点数量] milestones from [开始时间] to [结束时间], 
[视觉元素] at each milestone, [色彩方案], [风格描述], [质量词]
```

### Comparison (对比)

```
[对比类型] layout comparing [主题 A] vs [主题 B], 
[对比维度数量] comparison points, [视觉元素], [色彩方案], [风格描述], [质量词]
```

### Process (流程)

```
[流程类型] layout showing [主题] process, [步骤数量] steps from [开始] to [结束], 
[视觉元素] at each step, [色彩方案], [风格描述], [质量词]
```

### Hierarchy (层级)

```
[层级类型] layout showing [主题] hierarchy, [层级数量] levels, 
[视觉元素], [色彩方案], [风格描述], [质量词]
```

### Statistics (统计)

```
[统计类型] layout showing [主题] statistics, [数据点数量] data points, 
[图表类型], [视觉元素], [色彩方案], [风格描述], [质量词]
```

### Infographic List (列表)

```
[列表类型] layout showing [主题], [要点数量] key points, 
[视觉元素] for each point, [色彩方案], [风格描述], [质量词]
```

### Cycle (循环)

```
[循环类型] layout showing [主题] cycle, [阶段数量] stages, 
[视觉元素] at each stage, [色彩方案], [风格描述], [质量词]
```

### Network (网络)

```
[网络类型] layout showing [主题] network, [节点数量] nodes and connections, 
[视觉元素], [色彩方案], [风格描述], [质量词]
```

### Map-based (地图)

```
[地图类型] showing [主题] across [地理范围], [数据点数量] data points, 
[视觉元素], [色彩方案], [风格描述], [质量词]
```

### Pyramid (金字塔)

```
[金字塔类型] layout showing [主题], [层级数量] levels from [底层] to [顶层], 
[视觉元素], [色彩方案], [风格描述], [质量词]
```

## 风格模板

> **说明**：以下风格模板为内置简化示例。风格选择流程优先使用 `styles/` 目录下独立的 `.md` 风格定义文件；本章节作为内置 fallback，仅在对应风格文件不存在时使用。

### Corporate Memphis

```
corporate memphis style, geometric shapes, flat colors, professional, clean lines, 
blue and orange color palette, modern business aesthetic
```

### Minimal Business

```
minimal business style, clean lines, ample whitespace, professional, 
monochrome with accent color, sophisticated, elegant
```

### Clean Tech

```
clean tech style, modern, sleek, technological, 
blue and white color palette, geometric, precise
```

### Flat Modern

```
flat modern style, simple shapes, bold colors, clean, 
vibrant color palette, contemporary, accessible
```

### Playful Colors

```
playful colors style, bright and cheerful, fun, 
multicolor palette, rounded shapes, friendly
```

### Textbook Clear

```
textbook clear style, educational, easy to understand, 
color-coded sections, labeled diagrams, academic
```

### Bold Impact

```
bold impact style, strong visual presence, attention-grabbing, 
high contrast, dramatic, powerful
```

### Ultra Clean

```
ultra clean style, minimal, pristine, 
monochrome, ample whitespace, sophisticated, refined
```

### Cartoon Bright

```
cartoon bright style, colorful, fun, playful, 
vibrant multicolor palette, rounded shapes, cheerful
```

### Technical Diagram

```
technical diagram style, precise, detailed, 
blueprint aesthetic, accurate proportions, professional
```

## 质量词库

### 通用质量词

```
infographic, clean layout, professional, well-organized, high quality, detailed
```

### 可读性质量词

```
clear typography, readable text, well-spaced, legible
```

### 视觉质量词

```
visually appealing, balanced composition, harmonious colors, professional aesthetic
```

### 数据质量词

```
data-driven, accurate, precise, informative, insightful
```

### 风格质量词

```
modern, contemporary, elegant, sophisticated, polished
```

## 注意事项

1. 遵循 `references/shared-rules.md` 中定义的统一输出规范（语言一致、禁止颜色代码/尺寸描述/代码围栏/元评论）
2. **数据完整性**：所有原始数据必须逐字保留
3. **风格一致**：严格使用选定的风格模板
4. **布局优先**：首先明确布局类型
5. **质量词**：必须包含基础质量词