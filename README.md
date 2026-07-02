# ai-hub

Agent skills 与 MCP 资源集合，基于 GitHub 仓库分发。所有 skill 内容 agent 无关，支持 OpenCode / Claude Code / Codex / Cursor 等所有兼容 SKILL.md 标准的工具，通过 skills.sh 索引、`npx skills` 安装。

## 包含的 Skills

| 包名 | 描述 | 兼容性 |
|---|---|---|
| `git-commit` | Git 提交规范：约定式提交、提交拆分、安全规则 | 全部 agent |
| `prompt-gen` | 图像提示词生成器：6 种模式，模板/风格/评估体系完备 | 需 subagent + 多模态 |
| `game` | Web 游戏开发工作流：规划、实现、审查、测试 | 全部 agent |

> MCP 资源后续整理加入。

## 安装使用

```bash
# 安装单个 skill（默认项目级，装到当前项目的 agent skills 目录）
npx skills add bookandmusic/ai-hub --skill git-commit

# 全局安装（所有项目可用）
npx skills add bookandmusic/ai-hub --skill git-commit -g

# 安装到指定 agent（可重复 -a 指定多个）
npx skills add bookandmusic/ai-hub --skill prompt-gen -a opencode -a claude-code -a codex -a cursor

# 安装全部 skills
npx skills add bookandmusic/ai-hub --skill '*'

# 列出仓库内可安装的 skills（不实际安装）
npx skills add bookandmusic/ai-hub --list
```

也支持 URL / 本地路径：

```bash
npx skills add https://github.com/bookandmusic/ai-hub --skill game
npx skills add ./ --skill game          # 本地开发
```

## 安装位置

`npx skills` 按目标 agent 安装到对应目录，各 agent 自动发现这些路径下的 `SKILL.md`：

| 范围 | OpenCode | Claude Code | Codex | Cursor |
|---|---|---|---|---|
| 项目级 | `.agents/skills/` | `.claude/skills/` | `.agents/skills/` | `.agents/skills/` |
| 全局（-g） | `~/.config/opencode/skills/` | `~/.claude/skills/` | `~/.codex/skills/` | `~/.cursor/skills/` |

> OpenCode 还会额外搜索 `.opencode/skills/`，与上表路径均可被发现。

## 本地开发

```bash
pnpm install
git config core.hooksPath scripts/hooks   # 启用 pre-commit 校验（克隆后执行一次）
```

启用后每次 `git commit` 前自动校验 SKILL.md frontmatter（name 正则 / description 必填 / `---` 闭合），失败则提交被拒绝。

## 目录结构

```
packages/
├── git-commit/       # Git 提交规范
├── prompt-gen/       # 图像提示词生成器
└── game/             # Web 游戏开发工作流
```

每个 skill 是独立目录，包含 `SKILL.md` + 可选子目录（`references/`、`templates/`、`checklists/` 等）。skills CLI 通过递归发现自动识别 `packages/` 下的 skill（已实测验证）。

## 许可证

MIT
