# AGENTS.md

## 提交规则

**必须用户明确提交才可以提交，否则绝对不能提交。**

**提交前必须运行校验**，校验不通过则禁止提交（不允许产生格式错误的 SKILL.md 提交）：

```bash
bash scripts/validate-skills.sh
```

仓库内置可移植 `pre-commit` hook（位于 `scripts/hooks/pre-commit`，随仓库分发）。克隆后执行一次以启用：

```bash
git config core.hooksPath scripts/hooks
```

启用后每次 `git commit` 前自动校验，失败则提交被拒绝。

## 项目性质

这是 **OpenCode skills 分发仓库**，不是传统代码项目。核心资产是 `SKILL.md` 及配套参考文档，通过 GitHub 仓库分发，skills.sh 自动索引。

## 关键约束

- **SKILL.md frontmatter `name` 必须与所在目录名完全一致**
- 正则：`^[a-z0-9]+(-[a-z0-9]+)*$`，只能小写字母+数字+连字符
- **不能包含 `/`**，这是最常见的错误来源
- OpenCode 只识别 5 个 frontmatter 字段：`name`、`description`、`license`、`compatibility`、`metadata`
- 其他字段（如 `triggers`）会被静默忽略，不要添加

## 目录边界

```
packages/
├── git-commit/        # Git 提交规范（纯 markdown）
├── prompt-gen/        # 图像提示词生成器（60+ 参考文档）
└── game/              # Web 游戏开发工作流（模板+检查清单+参考）
```

每个 skill 是一个独立目录，包含 `SKILL.md` + 可选子目录（`references/`、`templates/`、`checklists/` 等）。

## 验证命令

```bash
# 检查 SKILL.md frontmatter 是否合法
head -1 packages/*/SKILL.md
# 第一行必须是 ---

# 检查 name 字段与目录名是否一致
for d in packages/*/; do
  dir=$(basename "$d")
  name=$(grep "^name:" "$d/SKILL.md" | head -1 | sed 's/name: *//')
  echo "$dir -> $name"
  [ "$dir" != "$name" ] && echo "  ❌ 不一致！"
done
```

## 发布方式

- **不使用 npm**，不使用 changesets，不使用 GitHub Packages
- 直接推送到 GitHub public repo → skills.sh 自动索引
- 用户使用：`npx skills add bookandmusic/ai-hub --skill <name>`
- 无注册、无 token、无 CI 配置即可分发

## 本地开发

```bash
pnpm install          # 安装依赖（验证工具）
git config core.hooksPath scripts/hooks   # 启用 pre-commit 校验（克隆后执行一次）
```

`.opencode/skills.json` 用于本地开发时注册 skill 路径，修改后需重启 OpenCode 生效。

## 命名规范

- 目录名：小写+连字符，如 `git-commit`（不是 `skill-git-commit`）
- `package.json` 的 `name`：`@bookandmusic/<目录名>`，如 `@bookandmusic/git-commit`
- SKILL.md 的 `name`：与目录名完全一致
