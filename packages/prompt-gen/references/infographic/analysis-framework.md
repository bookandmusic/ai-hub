# Analysis Framework

信息图内容分析框架。定义内容分析的 schema 和维度，用于指导后续的布局选择和提示词扩写。

## 分析维度

### 1. Content Type (内容类型)

| 类型 | 描述 | 适用布局 |
|------|------|----------|
| `timeline` | 时间线/时间轴 | horizontal-timeline, vertical-timeline, curved-path |
| `comparison` | 对比/比较 | split-screen, vs-battle, matrix-comparison |
| `process` | 流程/步骤 | flow-diagram, step-by-step, circular-flow |
| `hierarchy` | 层级/组织结构 | org-chart, pyramid, tree-structure |
| `statistics` | 统计数据 | dashboard, data-grid, chart-mix |
| `infographic-list` | 列表/要点 | numbered-list, icon-list, card-stack |
| `cycle` | 循环/周期 | circular-cycle, infinity-loop, spiral |
| `network` | 网络/关系 | node-network, hub-spoke, mind-map |
| `map-based` | 地图/地理 | regional-map, world-map, local-map |
| `pyramid` | 金字塔/层级 | classic-pyramid, layered-pyramid, inverted-pyramid |
| `funnel` | 漏斗/转化 | funnel-chart, conversion-funnel |
| `radar` | 雷达/多维 | radar-chart, spider-chart |
| `flowchart` | 流程图 | decision-tree, flowchart, swimlane |
| `matrix` | 矩阵/四象限 | 2x2-matrix, 3x3-matrix, bcg-matrix |
| `other` | 其他 | 根据内容推断 |

### 2. Tone (语气基调)

| 基调 | 描述 | 适用风格 |
|------|------|----------|
| `professional` | 专业、商务 | corporate-memphis, minimal-business, clean-tech |
| `casual` | 休闲、轻松 | flat-modern, playful-colors, hand-drawn-lite |
| `educational` | 教育、教学 | textbook-clear, diagram-focused, color-coded |
| `persuasive` | 说服、影响 | bold-impact, data-driven, storytelling |
| `minimalist` | 极简、简洁 | ultra-clean, monochrome-plus, whitespace-heavy |
| `playful` | 活泼、有趣 | cartoon-bright, illustration-heavy, emoji-style |
| `technical` | 技术、专业 | technical-diagram, blueprint-style, precise |
| `creative` | 创意、艺术 | artistic-abstract, colorful-expression, innovative |

### 3. Audience (目标受众)

| 受众 | 描述 | 设计考虑 |
|------|------|----------|
| `business` | 商务人士 | 专业、简洁、数据驱动 |
| `academic` | 学术/研究人员 | 精确、详细、引用规范 |
| `general` | 大众/普通用户 | 易懂、直观、视觉友好 |
| `technical` | 技术人员 | 精确、详细、专业术语 |
| `children` | 儿童/青少年 | 活泼、色彩丰富、简单 |
| `executives` | 高管/决策者 | 简洁、重点突出、数据驱动 |

### 4. Complexity (复杂度)

| 级别 | 描述 | 设计考虑 |
|------|------|----------|
| `simple` | 简单，1-3 个要点 | 简洁布局，少元素 |
| `standard` | 标准，4-8 个要点 | 平衡布局，适度元素 |
| `complex` | 复杂，9+ 个要点 | 分层布局，分组展示 |

### 5. Data Density (数据密度)

| 密度 | 描述 | 设计考虑 |
|------|------|----------|
| `low` | 低密度，少量数据 | 大量留白，大元素 |
| `medium` | 中密度，适度数据 | 平衡布局，适中元素 |
| `high` | 高密度，大量数据 | 紧凑布局，小元素，分组 |

### 6. Visual Elements (视觉元素)

| 元素类型 | 描述 |
|----------|------|
| `icons` | 图标/符号 |
| `charts` | 图表（柱状图、折线图、饼图等） |
| `illustrations` | 插图/手绘 |
| `photos` | 照片/真实图像 |
| `diagrams` | 流程图/结构图 |
| `maps` | 地图 |
| `text-heavy` | 文字为主 |
| `data-heavy` | 数据为主 |

### 7. Color Scheme (色彩方案)

| 方案 | 描述 |
|------|------|
| `monochrome` | 单色/黑白 |
| `analogous` | 类似色 |
| `complementary` | 互补色 |
| `triadic` | 三原色 |
| `gradient` | 渐变 |
| `vibrant` | 鲜艳多彩 |
| `pastel` | 柔和/粉彩 |
| `dark-mode` | 深色模式 |

## 输出格式

分析结果应输出为以下 JSON 格式：

```json
{
  "content_type": "timeline|comparison|process|hierarchy|statistics|infographic-list|cycle|network|map-based|pyramid|funnel|radar|flowchart|matrix|other",
  "tone": "professional|casual|educational|persuasive|minimalist|playful|technical|creative",
  "audience": "business|academic|general|technical|children|executives",
  "complexity": "simple|standard|complex",
  "data_density": "low|medium|high",
  "visual_elements": ["icons", "charts", "illustrations", "photos", "diagrams", "maps", "text-heavy", "data-heavy"],
  "color_scheme": "monochrome|analogous|complementary|triadic|gradient|vibrant|pastel|dark-mode",
  "key_data_points": ["数据点 1", "数据点 2", "..."],
  "main_message": "核心信息/主题",
  "visual_opportunities": ["视觉机会 1", "视觉机会 2", "..."]
}
```

## 使用示例

**输入**：
```
用户请求：生成一张关于"远程办公优势"的信息图，包含 5 个要点
```

**输出**：
```json
{
  "content_type": "infographic-list",
  "tone": "professional",
  "audience": "business",
  "complexity": "standard",
  "data_density": "medium",
  "visual_elements": ["icons", "charts"],
  "color_scheme": "analogous",
  "key_data_points": ["1.8 hours daily saved", "35% productivity increase", "$4,500 annual savings", "87% satisfaction improvement", "3,200 pounds carbon reduction"],
  "main_message": "远程办公的 5 大优势",
  "visual_opportunities": ["时钟图标表示时间节省", "上升趋势图表示效率提升", "钱包图标表示成本节省", "天平图标表示工作生活平衡", "绿叶图标表示环保"]
}
```

## 注意事项

1. **数据完整性**：所有原始数据必须逐字保留，不可改写
2. **逻辑清晰**：内容组织符合信息图逻辑
3. **视觉就绪**：每个要点附带视觉表达建议
4. **层级分明**：标题 - 子标题 - 内容的层级清晰
5. **受众适配**：根据目标受众调整设计复杂度
6. **风格一致**：语气基调决定整体风格方向