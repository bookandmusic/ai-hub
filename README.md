# ai-hub

Agent skills 与 MCP 服务集合，基于 GitHub 仓库分发。所有 skill 内容 agent 无关，支持 OpenCode / Claude Code / Codex / Cursor 等所有兼容 SKILL.md 标准的工具，通过 skills.sh 索引、`npx skills` 安装。MCP 服务按子目录独立自治，通过 `uvx` / `npx` 在线执行。

## Skills

Markdown 资产，通过 skills CLI 安装到 agent 目录，agent 自动识别 `SKILL.md` 按触发词加载。

| 包名 | 描述 | 兼容性 | 详情 |
|---|---|---|---|
| `git-commit` | Git 提交规范：约定式提交、提交拆分、安全规则 | 全部 agent | [→](packages/git-commit/README.md) |
| `prompt-gen` | 图像提示词生成器：6 种模式，模板/风格/评估体系完备 | 需 subagent + 多模态 | [→](packages/prompt-gen/README.md) |
| `game` | Web 游戏开发工作流：规划、实现、审查、测试 | 全部 agent | [→](packages/game/README.md) |

## MCP

可执行 MCP 服务，子目录独立工具链，各自 venv + lock，互不共享依赖（MCP 是独立服务，按需安装，不强制跨包统一）。

| MCP | 语言 | 说明 | 详情 |
|---|---|---|---|
| `openai-image-mcp` | Python | 多后端图像生成（Sensenova、ModelScope）暴露为独立 MCP 工具 | [→](mcp/openai-image-mcp/README.md) |

## 安装 Skills

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

## 使用 MCP

无需克隆仓库，`uvx` 从 GitHub 拉取执行（`#subdirectory=` 指向 monorepo 子目录，自动建临时 venv、装依赖、执行 entry script，不落盘）：

```bash
uvx --from "git+https://github.com/bookandmusic/ai-hub#subdirectory=mcp/openai-image-mcp" \
    openai-image-mcp
```

或配置到 agent 的 MCP 客户端（opencode `opencode.json` / Claude Code `~/.claude/settings.json`）自动拉起，完整配置示例与各 MCP 参数详见对应 [MCP README](#mcp)。

## 安装位置（Skills）

`npx skills` 按目标 agent 安装到对应目录，各 agent 自动发现这些路径下的 `SKILL.md`：

| 范围 | OpenCode | Claude Code | Codex | Cursor |
|---|---|---|---|---|
| 项目级 | `.agents/skills/` | `.claude/skills/` | `.agents/skills/` | `.agents/skills/` |
| 全局（-g） | `~/.config/opencode/skills/` | `~/.claude/skills/` | `~/.codex/skills/` | `~/.cursor/skills/` |

> OpenCode 还会额外搜索 `.opencode/skills/`，与上表路径均可被发现。

## 目录结构

```
packages/             # Skills（Markdown 资产，skills CLI 分发）
├── git-commit/
├── prompt-gen/
└── game/
mcp/                  # MCP 服务（可执行，子目录独立工具链，各自 venv + lock）
└── openai-image-mcp/ # Python（pyproject.toml + .venv + uv.lock 自治）
pnpm-workspace.yaml   # pnpm workspace 根（仅 packages/*，不扫 mcp/）
```

每个 skill 子目录含 `SKILL.md` + 可选 `references/`、`templates/`、`checklists/`。skills CLI 通过递归发现自动识别 `packages/` 下的 skill。每个 MCP 子目录是完全独立的 Python 包，自带 `pyproject.toml`、`.venv/`、`uv.lock`，互不共享依赖；不设根 `pyproject.toml`，避免 `uv sync` 误装所有 MCP 依赖。未来如新增 Node 实现的 MCP，按子目录独立工具链组织（`package.json` + `bin`，启动用 `npx`）。

## 许可证

MIT
