# git-commit

Git 提交规范。覆盖提交拆分、提交信息格式、安全提交。保留个人修改习惯。

## 兼容性

全部 agent（无特殊环境要求）。

## 安装

```bash
# 项目级
npx skills add bookandmusic/ai-hub --skill git-commit

# 全局
npx skills add bookandmusic/ai-hub --skill git-commit -g

# 指定 agent
npx skills add bookandmusic/ai-hub --skill git-commit -a opencode -a claude-code -a codex -a cursor
```

## 使用

agent 自动识别 `SKILL.md` 并按触发词（Git 提交 / commit / git commit）加载。完整规范见 [SKILL.md](./SKILL.md)。
