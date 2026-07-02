# 通用优化流程

所有模式共享的迭代优化工作流。各模式 `system.md` 中的"优化模式"章节引用本文件，不再重复描述。

## 输入识别

优化模式的输入包含以下额外字段：
- `previous_prompt` — 上一轮生成的提示词
- `previous_structured_content` — 上一轮的结构化内容
- `evaluation_feedback` — 评估反馈
  - `score` — 质量评分（0.0-1.0）
  - `result` — 评估结果（PASS/FAIL）
  - `violations` — 违规项列表（每项包含 rule_id, rule_name, detail, severity, revised_description）
  - `strengths` — 优点列表
  - `optimization_hints` — 可选的优化建议

## 优化流程

### Step 1: 反馈分析

按 severity 排序违规项（critical > major > minor），从 strengths 识别保留部分。

### Step 2: 内容修复

根据违规规则修复结构化内容：
- 规则 1-2（内容完整性）→ 从 user_prompt 补充缺失元素/修正错误数据
- 规则 3-4（描述清晰度）→ 抽象词具体化/移除逻辑冲突
- 规则 5-6（视觉细节）→ 添加颜色/形状/位置/空间关系
- 规则 7-8（风格一致性）→ 移除冲突风格/补充风格关键特征
- 规则 9-11（技术规范）→ 移除禁止元素（颜色代码/尺寸/元评论）、去重压缩、移除不可实现要求

各模式的规则 12-20（infographic 为 12-21，imitate 为 12-22）映射见对应 `prompt-critic-{mode}.md`。

### Step 3: 应用优化建议

逐条评估 `optimization_hints`，不冲突则应用。

### Step 4: 保留优点

确保 `strengths` 中提到的部分在修复后保留。

### Step 5: 重新生成

基于修复后的结构化内容重新执行初始生成的 Step 4（提示词扩写）。

## 输出要求

与初始生成模式完全相同：返回包含 `status`、`structured_content`、`final_prompt` 的裸 JSON。
不输出修改过程，确保所有 critical 违规已修复。
