---
name: prompt-gen
description: |
  图像提示词生成器。融合 SN 图像技能链（人物/风景/物体/概念/信息图/风格模仿）的提示词生成流程。
  通过 subagent 轮询执行，不依赖外部 API。
  遇到以下任一情况就主动使用本 skill：
  ①用户出现触发词：生成图像 / prompt / 提示词；
  ②用户要求生成、优化、扩写或评估图像提示词；
  ③用户要求制作人物/风景/物体/概念/信息图/风格模仿图像的提示词。
metadata:
  project: dev-workflow
  tier: 2
  category: utility
  user_visible: true
compatibility: Requires subagent and multimodal image capabilities
---

# prompt-gen — 多模式提示词生成

## 模式一览

| 模式 | 适用场景 | 来源 skill |
|------|----------|------------|
| `portrait` | 人物图像提示词生成 | 参考 SN 人像设计流程 |
| `landscape` | 风景场景提示词生成 | 参考 SN 场景设计流程 |
| `object` | 物体/产品展示提示词生成 | 参考 SN 物体设计流程 |
| `concept` | 概念/创意图像提示词生成 | 参考 SN 概念设计流程 |
| `infographic` | 信息图提示词生成 | sn-infographic |
| `imitate` | 风格模仿提示词生成（需参考图） | sn-image-imitate |

## 输入参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `user_prompt` | string | **必填** | 用户原始请求或要生成提示词的内容 |
| `mode` | string | `portrait` | `portrait` / `landscape` / `object` / `concept` / `infographic` / `imitate` |
| `language` | string | `zh` | 输出语言：`zh`（中文）/ `en`（英文） |
| `output_mode` | string | `friendly` | `friendly`：输出最终提示词+简短说明；`verbose`：输出完整过程+最终提示词 |
| `reference_image` | image | imitate 模式必填 | 风格模仿时的参考图（仅 imitate 模式）。格式：Subagent 通过多模态能力直接读取图像内容，Main Agent 将图像以附件形式传递给 Subagent，不进行 base64 编码或 URL 转换 |
| `target_content` | string | imitate 模式必填 | 风格模仿时的目标新内容（仅 imitate 模式） |
| `aspect_ratio` | string | `16:9` | 信息图特有：宽高比（仅 infographic 模式） |
| `image_size` | string | `2k` | 信息图特有：图像尺寸 `2k`/`4k`（仅 infographic 模式） |
| `prompts_expand_mode` | string | `auto` | 信息图特有：提示词扩写模式 `auto`/`force`/`disable`（仅 infographic 模式） |
| `max_rounds` | int | 1 | 最大迭代轮次，范围 1-5 |

### 参数提取规则（Main Agent 按优先级）

1. **内联 KV** — `mode=infographic`、`language=en`、`output=verbose`
2. **关键词识别**：

   | 参数 | 触发词 | 解析值 |
   |------|--------|--------|
   | `mode` | `人物`、`portrait`、`人像` | `portrait` |
   | `mode` | `风景`、`landscape`、`场景` | `landscape` |
   | `mode` | `物体`、`object`、`产品` | `object` |
   | `mode` | `概念`、`concept`、`创意` | `concept` |
   | `mode` | `信息图`、`infographic` | `infographic` |
   | `mode` | `风格模仿`、`风格迁移`、`imitate`、`仿照`、`模仿` | `imitate` |
   | `language` | `英文`、`English`、`en` | `en` |
   | `language` | `中文`、`Chinese`、`zh`（或无指定） | `zh` |
   | `output_mode` | `verbose`、`详细`、`完整` | `verbose` |
   | `max_rounds` | `N 轮`、`N rounds`、`重试 N 次`、`迭代 N 次` | N (范围 1-5) |

3. **内容推断**：若无明确 mode 关键词，按主体内容推断——人物/人像→`portrait`，风景/场景→`landscape`，产品/物体→`object`，概念/创意→`concept`，图表/数据/流程→`infographic`，参考图+新内容→`imitate`。
4. **默认值**：所有未设置参数用默认值。

## 架构：Main Agent + Subagent

| 角色 | 职责 |
|------|------|
| **Main Agent** | 接收用户请求、提取参数、迭代控制、评估质量、输出最终结果 |
| **Subagent** | 按模式执行提示词生成流水线，返回结构化 JSON |

**职责边界**：
- Subagent 不直接向用户发消息，只返回 JSON
- Main Agent 负责所有用户可见输出
- Subagent 最后一条消息必须是裸 JSON（无代码围栏，无前后说明）

**模式工作流差异**：
- portrait / landscape / object / concept：单次 LLM 调用，内部 4 步（内容分析 → 布局选择 → 结构化 → 扩写）
- infographic：单次 LLM 调用，内部 5 步（扩写判断 → 分析 → 布局选择 → 结构化 → 扩写，内联 reference 文件）
- imitate：单次 LLM 调用，内部 3 步（分析参考图 → 提取布局约束 → 重写目标内容）

## 工作流

### Main Agent 工作流

1. **参数提取** — 解析 `mode`、`language`、`output_mode`、`max_rounds`（默认 1，范围 1-5）
2. **模式路由** — 根据 `mode` 选择：
   - Subagent system prompt 路径（`references/{mode}/system.md`）
   - 评估标准：每个模式使用各自专用 critic 文件 `references/{mode}/prompt-critic-{mode}.md`；通用评估标准定义在 `references/prompt-critic-system.md`（各模式 critic 均扩展自此文件）
3. **迭代循环** — 执行 `max_rounds` 轮（详见 `docs/iteration-workflow.md`）：
   - **第 1 轮**：调用 Subagent 生成初始提示词
   - **第 2+ 轮**（若 `max_rounds > 1`）：
     - 使用 LLM 评估上一轮提示词质量
     - 若评估结果为 `PASS`（score >= 阈值且无 critical 违规），提前终止
     - 若评估结果为 `FAIL`，将 violations 和 optimization_hints 传递给 Subagent
     - Subagent 根据反馈优化提示词
   - 记录每轮的 `final_prompt`、`structured_content`、`evaluation`
4. **最佳提示词选择**（当 `max_rounds > 1` 时）：
  - **PASS 优先**：若存在提前终止（PASS）的轮次，选择该轮次的提示词
  - **分数次选**：若无 PASS，按 `score` 降序选择评分最高的提示词
5. **结果输出**：
   - `friendly` 模式：简短说明 + 最终提示词
   - `verbose` 模式：迭代过程 + 所有轮次评估结果 + 最终提示词
   - `status=error`：报告错误

**模式 PASS 阈值**（各模式通过各自 `prompt-critic-{mode}.md` 定义）：

| 模式 | 阈值 | 备注 |
|------|------|------|
| portrait | 0.80 | 人物图像质量要求高 |
| landscape | 0.80 | 风景场景要求高 |
| object | 0.80 | 物体展示精度要求高 |
| concept | 0.75 | 概念艺术可适当放宽 |
| infographic | 0.75 | 信息图复杂度可放宽 |
| imitate | 0.75 | 风格模仿可适当放宽 |

### Subagent 通用规则

所有模式的 subagent 共享以下规则。

**输出规范**：遵循 `references/shared-rules.md` 中定义的统一输出规范。最终返回裸 JSON，格式见各模式的 Return Contract。

**工作模式**：
- **初始生成模式**（`task=prompt-generation`）：接收 `user_prompt`，执行完整的生成流程
- **优化迭代模式**（`task=prompt-optimization`）：接收 `user_prompt` + `previous_prompt` + `previous_structured_content` + `evaluation_feedback`，执行 `references/optimization-workflow.md` 定义的通用优化流程

---

## 各模式 Subagent Prompt 模板

### 1. `portrait` — 人物图像提示词生成

**system prompt**：从 `references/portrait/system.md` 读取角色设定和工作流。

**subagent 接收**：
```json
{
  "task": "prompt-generation",
  "mode": "portrait",
  "user_prompt": "<原始请求>",
  "language": "zh|en",
  "output_mode": "friendly|verbose"
}
```

**subagent 工作流**（单步 LLM）：内容分析 → 布局选择 → 结构化内容 → 提示词扩写

**Return Contract**：
```json
{
  "status": "ok",
  "need_main_agent_send": true,
  "structured_content": {
    "portrait_type": "...",
    "composition": {...},
    "subject": {...},
    "style": {...},
    "environment": {...},
    "technical": {...}
  },
  "final_prompt": "<最终人物图像提示词>"
}
```

**参考文件**：
- `references/portrait/system.md` — 人物提示词生成系统提示
- `references/portrait/prompt-critic-portrait.md` — 人物专用评估标准（规则 12-20 + 评分维度）
- `references/portrait/templates/` — 构图模板（可选参考）
- `references/portrait/styles/` — 风格定义（可选参考）

---

### 2. `landscape` — 风景场景提示词生成

**system prompt**：从 `references/landscape/system.md` 读取角色设定和工作流。

**subagent 接收**：
```json
{
  "task": "prompt-generation",
  "mode": "landscape",
  "user_prompt": "<原始请求>",
  "language": "zh|en",
  "output_mode": "friendly|verbose"
}
```

**subagent 工作流**（单步 LLM）：内容分析 → 布局选择 → 结构化内容 → 提示词扩写

**Return Contract**：
```json
{
  "status": "ok",
  "need_main_agent_send": true,
  "structured_content": {
    "scene_type": "...",
    "composition": {...},
    "environment": {...},
    "lighting": {...},
    "style": {...},
    "technical": {...}
  },
  "final_prompt": "<最终风景场景提示词>"
}
```

**参考文件**：
- `references/landscape/system.md` — 风景提示词生成系统提示
- `references/landscape/prompt-critic-landscape.md` — 风景专用评估标准（规则 12-20 + 评分维度）
- `references/landscape/templates/` — 构图模板（可选参考）
- `references/landscape/styles/` — 风格定义（可选参考）

---

### 3. `object` — 物体/产品展示提示词生成

**system prompt**：从 `references/object/system.md` 读取角色设定和工作流。

**subagent 接收**：
```json
{
  "task": "prompt-generation",
  "mode": "object",
  "user_prompt": "<原始请求>",
  "language": "zh|en",
  "output_mode": "friendly|verbose"
}
```

**subagent 工作流**（单步 LLM）：内容分析 → 布局选择 → 结构化内容 → 提示词扩写

**Return Contract**：
```json
{
  "status": "ok",
  "need_main_agent_send": true,
  "structured_content": {
    "object_type": "...",
    "composition": {...},
    "object": {...},
    "display": {...},
    "style": {...},
    "technical": {...}
  },
  "final_prompt": "<最终物体/产品展示提示词>"
}
```

**参考文件**：
- `references/object/system.md` — 物体提示词生成系统提示
- `references/object/prompt-critic-object.md` — 物体专用评估标准（规则 12-20 + 评分维度）
- `references/object/templates/` — 构图模板（可选参考）
- `references/object/styles/` — 风格定义（可选参考）

---

### 4. `concept` — 概念/创意图像提示词生成

**system prompt**：从 `references/concept/system.md` 读取角色设定和工作流。

**subagent 接收**：
```json
{
  "task": "prompt-generation",
  "mode": "concept",
  "user_prompt": "<原始请求>",
  "language": "zh|en",
  "output_mode": "friendly|verbose"
}
```

**subagent 工作流**（单步 LLM）：内容分析 → 布局选择 → 结构化内容 → 提示词扩写

**Return Contract**：
```json
{
  "status": "ok",
  "need_main_agent_send": true,
  "structured_content": {
    "concept_type": "...",
    "composition": {...},
    "concept": {...},
    "visual_elements": {...},
    "style": {...},
    "technical": {...}
  },
  "final_prompt": "<最终概念/创意图像提示词>"
}
```

**参考文件**：
- `references/concept/system.md` — 概念提示词生成系统提示
- `references/concept/prompt-critic-concept.md` — 概念专用评估标准（规则 12-20 + 评分维度）
- `references/concept/templates/` — 构图模板（可选参考）
- `references/concept/styles/` — 风格定义（可选参考）

---

### 5. `infographic` — 信息图提示词生成

**system prompt**：从 `references/infographic/system.md` 读取角色设定（Senior Visual Information Architect）。

**subagent 接收**：
```json
{
  "task": "prompt-generation",
  "mode": "infographic",
  "user_prompt": "<用户提供的信息图内容>",
  "language": "zh|en",
  "output_mode": "friendly|verbose",
  "aspect_ratio": "16:9|9:16|4:3|3:4|1:1",
  "image_size": "2k|4k",
  "prompts_expand_mode": "auto|force|disable"
}
```

**subagent 工作流**（单步 LLM）：
1. 内容分析（使用 `analysis-framework.md` 的维度）
2. 布局选择（从 `layout-style-selection.md` 候选集中选择）
3. 结构化内容（按 `structured-content-template.md` 生成）
4. 提示词扩写（组合布局定义 + 风格定义 + 结构化内容 → 最终提示词）

**参考文件**：
- `references/infographic/system.md` — 信息图提示词扩写系统提示
- `references/infographic/analysis-framework.md` — 内容分析框架
- `references/infographic/evaluation-standard.md` — 评估标准（用于 Step 1 是否扩写判断）
- `references/infographic/prompt-critic-infographic.md` — 信息图专用评估标准（规则 12-21 + 评分维度）
- `references/infographic/layout-style-selection.md` — 布局/风格选择规则
- `references/infographic/prompts-expand-system.md` — 提示词扩写系统提示
- `references/infographic/base-prompt.md` — 基础提示词模板
- `references/infographic/structured-content-template.md` — 结构化内容模板
- `references/infographic/runtime-parameters.md` — 运行时参数定义
- `references/prompt-critic-system.md` — 通用提示词质量评估标准（11 条规则，各模式 critic 均扩展自此文件）

**Return Contract**（与其他模式统一，infographic 额外包含 `analysis` 和 `layout_style_selection`）：
```json
{
  "status": "ok",
  "need_main_agent_send": true,
  "analysis": {
    "content_type": "...",
    "tone": "...",
    "audience": "...",
    "complexity": "...",
    "data_density": "..."
  },
  "layout_style_selection": {
    "layout": "...",
    "style": "..."
  },
  "structured_content": {
    "title": "...",
    "overview": "...",
    "key_points": [...],
    "data_check": {...}
  },
  "final_prompt": "<最终信息图提示词>"
}
```

---

### 6. `imitate` — 风格模仿提示词生成

**system prompt**：从 `references/imitate/system.md` 读取角色设定和工作流。

**subagent 接收**：
```json
{
  "task": "prompt-generation",
  "mode": "imitate",
  "reference_image": "<参考图（多模态）>",
  "target_content": "<用户想要的新内容>",
  "language": "zh|en",
  "output_mode": "friendly|verbose"
}
```

**subagent 工作流**（单步 LLM）：
1. 分析参考图：提取风格特征、布局结构、色彩方案、光影特征
2. 提取布局约束：识别视觉层次、区块拓扑、对齐节奏、阅读流
3. 重写目标内容：在保持布局约束的前提下，将 `target_content` 嵌入新的提示词

**布局锁定约束**（5 个非协商约束，必须全部保持，详见 `references/imitate/system.md`）：visual hierarchy、region topology、alignment rhythm、chart structure、reading flow

**参考文件**：
- `references/imitate/system.md` — 风格模仿提示词重写系统提示
- `references/imitate/prompt-critic-imitate.md` — 风格模仿专用评估标准（规则 12-22 + 评分维度）
- `references/imitate/prompts/image_annotate.md` — 图像标注分析参考
- `references/imitate/prompts/caption_rewrite.md` — 重写逻辑参考（layout-lock）

**Return Contract**：
```json
{
  "status": "ok",
  "need_main_agent_send": true,
  "reference": {
    "short_caption": "<参考图 short caption>",
    "long_caption": "<参考图 long caption>",
    "layout_blueprint": { ... }
  },
  "style_cues": {
    "lighting": "<光影特征>",
    "color_palette": ["<色彩特征>"],
    "mood": "<情绪氛围>",
    "composition": "<构图特征>"
  },
  "layout_constraints": {
    "visual_hierarchy": "<视觉层次约束>",
    "region_topology": "<区块拓扑约束>",
    "alignment_rhythm": "<对齐节奏约束>",
    "reading_flow": "<阅读流约束>"
  },
  "final_prompt": "<重写后的最终提示词>"
}
```

---

## 输出格式

### friendly 模式（默认）

Main Agent 输出：一行简短描述（≤ 50 字符，语言遵循 `language` 参数）+ 最终提示词文本。

### verbose 模式

```
提示词生成结果
---
模式: <portrait|landscape|object|concept|infographic|imitate>
语言: <zh|en>
---
迭代过程（{轮数} 轮）:
#1 round=1 score=X.XX result=<PASS|FAIL> [early terminated]
  违规项: {N} critical, {N} major, {N} minor
  优点: <strengths 列表>
#2 round=2 score=X.XX result=<PASS|FAIL>
  违规项: ...
---
最终选择: round={selected_round} score={best_score}
---
最终提示词：
<final_prompt>
```

注：`structured_content` 摘要为各模式结构化内容的核心字段（如 portrait 的 portrait_type + composition.type + style.name），非完整 JSON。

## 参考文件

```
references/
  shared-rules.md                 共享规则（输出规范、提示词写作规则、数据完整性、精简原则、提示词长度、质量词库）
  optimization-workflow.md         通用优化流程
  prompt-critic-system.md         通用提示词质量评估标准（11 条规则 + 评分维度 + 通过阈值）
  portrait/
    system.md                     人物提示词生成系统提示
    templates/                    构图模板（6 种）
    styles/                       风格定义（6 种）
    prompt-critic-portrait.md     人物专用评估标准
  landscape/
    system.md                     风景提示词生成系统提示
    templates/                    构图模板（10 种）
    styles/                       风格定义（8 种）
    prompt-critic-landscape.md    风景专用评估标准
  object/
    system.md                     物体提示词生成系统提示
    templates/                    构图模板（8 种）
    styles/                       风格定义（6 种）
    prompt-critic-object.md       物体专用评估标准
  concept/
    system.md                     概念提示词生成系统提示
    templates/                    构图模板（8 种）
    styles/                       风格定义（10 种）
    prompt-critic-concept.md      概念专用评估标准
  infographic/
    system.md                     信息图提示词扩写系统提示
    analysis-framework.md         内容分析框架
    evaluation-standard.md        评估标准
    layout-style-selection.md     布局/风格选择规则
    prompts-expand-system.md      提示词扩写系统提示
    base-prompt.md                基础提示词模板
    structured-content-template.md 结构化内容模板
    runtime-parameters.md         运行时参数定义
    prompt-critic-infographic.md  信息图专用评估标准
    layouts/                      布局定义（4 种）
    styles/                       风格定义（4 种）
  imitate/
    system.md                     风格模仿提示词重写系统提示
    prompts/
      image_annotate.md           图像标注系统提示
      caption_rewrite.md          重写系统提示（layout-lock）
    prompt-critic-imitate.md      风格模仿专用评估标准

docs/
  iteration-workflow.md           迭代优化流程设计文档
```
