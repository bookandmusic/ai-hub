# Layout & Style Selection

信息图布局选择和风格选择规则。基于内容分析结果，选择最匹配的布局和风格。

## 选择方式

Subagent 作为 LLM，基于分析结果和候选表进行推理选择（非随机）。选择时需考虑：
1. 内容类型与布局的匹配度
2. 语气基调与风格的一致性
3. 复杂度对布局/风格的约束
4. 受众对风格的偏好

---

## Layout Selection (布局选择)

### 候选布局表

| 布局名称 | 适用内容类型 | 描述 | 定义文件 |
|----------|-------------|------|----------|
| `horizontal-timeline` | timeline | 水平时间线，适合线性时间序列 | ✅ |
| `vertical-sections` | timeline, process | 垂直分区，适合纵向分段展示 | ✅ |
| `grid` | comparison, statistics, matrix | 网格布局，适合多维对比/数据展示 | ✅ |
| `numbered-list` | infographic-list, process | 编号列表，适合有序要点 | ✅ |
| `split-screen` | comparison | 分屏对比，左右对比 | — |
| `flow-diagram` | process | 流程图，标准流程展示 | — |
| `step-by-step` | process | 分步展示，逐步引导 | — |
| `org-chart` | hierarchy | 组织结构图，树形层级 | — |
| `pyramid` | hierarchy, pyramid | 金字塔，层级递减 | — |
| `dashboard` | statistics | 仪表盘，多图表组合 | — |
| `circular-cycle` | cycle | 圆形循环，闭环周期 | — |
| `node-network` | network | 节点网络，关系展示 | — |
| `funnel-chart` | funnel | 漏斗图，转化流程 | — |
| `radar-chart` | radar | 雷达图，多维对比 | — |

**定义文件标记**：✅ 表示 `layouts/` 目录下有对应 `.md` 文件；— 表示无定义文件。

### 选择规则

1. **内容类型优先**：首先根据 `content_type` 筛选适用布局
2. **语气基调调整**：
   - `professional` → 优先 `dashboard`, `flow-diagram`, `org-chart`
   - `minimalist` → 优先 `numbered-list`, `grid`
   - `playful` → 优先 `card-stack`, `icon-list`
3. **复杂度约束**：
   - `simple` → 选择简单布局（`numbered-list`, `split-screen`）
   - `complex` → 选择分层布局（`dashboard`, `grid`）
4. **定义文件优先**：优先选择有对应 `.md` 定义文件的布局
5. **回退规则**：若无合适布局，按以下规则回退：
   - `infographic-list` → `numbered-list`
   - `process` → `grid`
   - `timeline` → `horizontal-timeline`
   - 其余 → `grid`

### SN 扩展布局（参考）

SenseNova 提供了 87 种布局定义，可作为扩展参考。当前内建 4 种布局，未来可按需从 SN 引入更多布局定义文件。

---

## Style Selection (风格选择)

### 候选风格表

| 风格名称 | 适用语气基调 | 描述 | 定义文件 |
|----------|-------------|------|----------|
| `business-professional` | professional | 商务专业，简洁线条 | ✅ |
| `corporate-memphis` | professional, casual | 企业孟菲斯，几何图形 | ✅ |
| `flat-modern` | casual, minimalist | 扁平现代，简洁色彩 | ✅ |
| `minimal-business` | professional, minimalist | 极简商务，大量留白 | ✅ |
| `clean-tech` | professional, technical | 科技简洁，现代感 | — |
| `playful-colors` | casual, playful | 活泼色彩，明亮色调 | — |
| `textbook-clear` | educational | 教科书清晰，教学风格 | — |
| `bold-impact` | persuasive | 大胆冲击，强调效果 | — |
| `ultra-clean` | minimalist | 超简洁，大量留白 | — |
| `cartoon-bright` | playful | 卡通明亮，活泼感 | — |
| `technical-diagram` | technical | 技术图表，精确风格 | — |
| `artistic-abstract` | creative | 艺术抽象，创意感 | — |

**定义文件标记**：✅ 表示 `styles/` 目录下有对应 `.md` 文件；— 表示无定义文件。

### 选择规则

1. **语气基调优先**：首先根据 `tone` 筛选适用风格
2. **受众调整**：
   - `business` → 优先 `corporate-memphis`, `minimal-business`
   - `children` → 优先 `cartoon-bright`, `playful-colors`
   - `technical` → 优先 `technical-diagram`, `clean-tech`
3. **复杂度约束**：
   - `simple` → 选择简洁风格（`ultra-clean`, `minimal-business`）
   - `complex` → 选择丰富风格（`corporate-memphis`, `flat-modern`）
4. **定义文件优先**：优先选择有对应 `.md` 定义文件的风格
5. **回退规则**：若无合适风格，按以下规则回退：
   - `professional` → `business-professional`
   - `playful` → `corporate-memphis`
   - `minimalist` → `flat-modern`
   - 其余 → `minimal-business`

### SN 扩展风格（参考）

SenseNova 提供了 66 种风格定义，可作为扩展参考。当前内建 4 种风格，未来可按需从 SN 引入更多风格定义文件。

---

## Combined Selection Output

最终选择结果输出为以下 JSON 格式：

```json
{
  "layout": "<layout name>",
  "style": "<style name>",
  "selection_reason": "<选择理由，说明为何此布局/风格最匹配分析结果>"
}
```

## 注意事项

1. **推理选择**：选择过程基于推理，不是随机
2. **定义文件优先**：优先选择有 `.md` 定义文件的布局/风格，确保扩写时有详细参考
3. **回退保底**：当候选集中无合适选项时，使用回退规则确保总能选出有效值
4. **可追溯性**：记录选择理由，便于调试和复现
