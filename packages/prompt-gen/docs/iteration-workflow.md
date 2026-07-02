# prompt-gen 迭代优化流程设计

## 概述

prompt-gen 的迭代流程基于 LLM 原生对话能力，不依赖文件系统或 bash 脚本。中间状态保存在对话上下文中。

```
for round in 1 to max_rounds:
    1. 调用 Subagent 生成/优化提示词
    2. 评估提示词质量（仅 max_rounds > 1）
    3. 若 PASS，提前终止；否则继续
```

## Main Agent 迭代工作流

### Step 1: 参数提取

参数提取规则见 `SKILL.md` 的"输入参数"章节。Main Agent 按优先级从用户请求中提取参数（内联 KV > 关键词识别 > 内容推断 > 默认值）。

### Step 2: 模式路由

根据 `mode` 选择对应的 Subagent system prompt 和 critic 标准，见 `SKILL.md` 的「Main Agent 工作流」第 2 步（模式路由）。

所有 critic 文件均扩展自 `references/prompt-critic-system.md`。

### Step 3: 迭代循环

Main Agent 在对话上下文中维护以下状态：
- `best_score`: 所有轮次中的最高评分（初始 0.0）
- `best_round`: 最高评分对应的轮次编号（初始 0）
- `best_prompt`: 最高评分对应的提示词
- `best_structured_content`: 最高评分对应的结构化内容
- `early_terminated`: 是否因 PASS 提前终止（初始 false）
- `rounds_log`: 所有轮次的日志（用于 verbose 模式输出）

每轮执行：

#### 3.1 生成/优化提示词

调用 Subagent（使用 Task tool）：

**第 1 轮（初始生成）**：
- 构造 Subagent 输入 JSON，包含 `task=prompt-generation`、`mode`、`user_prompt`、`language`、`output_mode`
- 对 infographic 模式，额外包含 `aspect_ratio`、`image_size`、`prompts_expand_mode`
- 对 imitate 模式，额外包含 `reference_image`（多模态）、`target_content`
- Subagent system prompt 来自 `references/{mode}/system.md`

**第 2+ 轮（优化迭代）**：
- 构造 Subagent 输入 JSON，包含 `task=prompt-optimization`、`mode`、`user_prompt`、`previous_prompt`、`previous_structured_content`、`evaluation_feedback`、`language`、`output_mode`
- `evaluation_feedback` 包含上一轮的 `score`、`result`、`violations`、`strengths`、`optimization_hints`
- Subagent 根据反馈修复违规项并重新生成提示词

#### 3.2 评估质量（仅当 `max_rounds > 1` 时执行）

使用 LLM 评估提示词质量：
- system prompt 来自对应的 critic 文件
- 评估请求包含：原始需求、生成的提示词、结构化内容
- 返回评估 JSON：`reasoning`、`result`、`score`、`violations`、`strengths`、`optimization_hints`

#### 3.3 更新最佳提示词

- **PASS 优先**：若当前轮 `result == "PASS"`，直接覆盖 best_score、best_round、best_prompt、best_structured_content（PASS 轮次优先于分数最高的 FAIL 轮次）
- **分数次选**：若当前轮为 FAIL 且 score > best_score，更新 best_score、best_round、best_prompt、best_structured_content
- 记录当前轮日志到 rounds_log

#### 3.4 提前终止检查

- 若 `result == "PASS"`，设置 `early_terminated = true`，跳出循环
- 否则继续下一轮

### Step 4: 结果处理

#### friendly 模式（默认）

输出格式：
```
<简短说明（≤ 50 字符）>

最终提示词：
<selected_prompt>
```

**简短说明规则**：
- `max_rounds = 1`: "已生成 {mode} 提示词"
- `max_rounds > 1, early_terminated`: "经 {round} 轮优化，提示词已通过质量检查（评分 {score}）"
- `max_rounds > 1, 未提前终止`: "经 {max_rounds} 轮优化，已返回最佳版本（评分 {best_score}）"

#### verbose 模式

输出格式：
```
提示词生成结果
---
模式: {mode}
语言: {language}
---
迭代过程（{轮数} 轮）:
#1 round=1 score={score} result={PASS|FAIL} [early terminated]
  违规项: {violations 数量} critical, {violations 数量} major, {violations 数量} minor
  优点: {strengths 列表}
#2 round=2 score={score} result={PASS|FAIL}
  违规项: ...
...
---
最终选择: round={selected_round} score={best_score}
---
最终提示词：
{selected_prompt}
---
结构化内容：
{selected_structured_content}
```

## 评估调用

Main Agent 使用当前 LLM 直接执行评估，无需外部 API：

1. 读取对应模式的 critic 文件作为 system prompt
2. 构建评估请求（包含原始需求、生成的提示词、结构化内容）
3. 解析评估结果 JSON

## 错误处理

### Subagent 调用失败

**策略**：立即中止，返回错误信息。
**理由**：Subagent 是核心生成器，失败意味着无法产生有效提示词。

### 评估调用失败

**策略**：降级处理，使用默认评估结果 `{"score": 0.5, "result": "UNKNOWN", "violations": [], "note": "evaluation_failed"}`，继续下一轮。
**理由**：评估是辅助功能，失败不应阻止提示词生成。

### 所有轮次评估都失败

**策略**：返回最后一轮生成的提示词，标注 `all_evaluations_failed: true`。

### 错误处理优先级

1. **Critical（立即中止）**：Subagent 调用失败、JSON 解析失败
2. **Degraded（降级继续）**：评估调用失败 → 继续生成不评估
3. **Warning（记录不影响）**：单轮评估超时

## 实现注意事项

1. **Main Agent 负责循环控制** — Subagent 只负责单轮生成/优化
2. **评估在 Main Agent 中执行** — 使用当前 LLM 直接评估，无需外部 API
3. **中间状态保存在对话上下文中** — 不依赖文件系统
4. **最佳提示词选择** — 按 score 降序选择，而非简单选择最后一轮
5. **语言一致性** — 评估反馈的语言应与 `language` 参数一致
