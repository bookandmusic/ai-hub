# game

Web 游戏开发工作流。聚焦游戏特有节点：玩法规划、资源清单、游戏循环实现、游戏特有审查、游戏验收。通用步骤（需求分析/视觉风格/UI 实现/lint/commit/push）委托对应 skill 或遵守 AGENTS.md。

## 兼容性

全部 agent（无特殊环境要求）。

## 安装

```bash
# 项目级
npx skills add bookandmusic/ai-hub --skill game

# 全局
npx skills add bookandmusic/ai-hub --skill game -g

# 指定 agent
npx skills add bookandmusic/ai-hub --skill game -a opencode -a claude-code -a codex -a cursor
```

## 使用

agent 自动识别 `SKILL.md` 并按触发词（网页游戏 / 做一个游戏 / web game / make a game）加载。完整规范见 [SKILL.md](./SKILL.md)。
