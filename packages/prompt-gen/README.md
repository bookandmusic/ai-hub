# prompt-gen

图像提示词生成器。融合 SN 图像技能链（人物/风景/物体/概念/信息图/风格模仿）的提示词生成流程。通过 subagent 轮询执行，不依赖外部 API。

## 兼容性

需 subagent + 多模态图像能力（`compatibility: Requires subagent and multimodal image capabilities`）。

## 安装

```bash
# 项目级
npx skills add bookandmusic/ai-hub --skill prompt-gen

# 全局
npx skills add bookandmusic/ai-hub --skill prompt-gen -g

# 指定 agent
npx skills add bookandmusic/ai-hub --skill prompt-gen -a opencode -a claude-code -a codex -a cursor
```

## 使用

agent 自动识别 `SKILL.md` 并按触发词（生成图像 / prompt / 提示词）加载。完整规范与 6 种模式参考文档见 [SKILL.md](./SKILL.md)。
