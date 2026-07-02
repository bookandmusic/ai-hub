---
name: git-commit
description: |
  Git 提交规范。覆盖提交拆分、提交信息格式、安全提交。
  保留个人修改习惯。
  遇到以下任一情况就主动使用本 skill：
  ①用户出现触发词：Git 提交 / commit / git commit；
  ②用户要求提交代码。
metadata:
  project: dev-workflow
  tier: 2
  category: utility
  user_visible: true
---

# git-commit — Git 提交

## 流程

1. **检查状态** — `git status` + `git diff` + `git log --oneline -10`（理解仓库风格）
2. **拆分提交** — 按逻辑模块拆分提交；只 stage 意图文件，避免 `git add .` / `git add -A`
3. **提交信息** — 使用约定式提交格式，匹配仓库现有风格（参考第1步 log）
4. **安全检查** — 不提交敏感信息
5. **展示提交计划** — 默认到此为止，只展示 staged 文件清单和提交信息，不执行提交
6. **执行提交** — 仅当用户明确要求提交（"提交"/"commit"/"git commit"）时执行 `git commit`；pre-commit hook 自动校验

## 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档变更
- `style`: 代码格式（不影响语义）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试
- `chore`: 构建/工具变更

### Scope

模块名称，如 `auth`, `api`, `ui`, `utils`

### Subject

简短描述，不超过 50 字符

### Body

详细描述，说明为什么变更；每行不超过 72 字符

### Footer

- 关联的 issue：`Closes #123`
- Breaking changes：`BREAKING CHANGE: ...`

## 提交拆分原则

1. **功能独立** — 每个提交只完成一个功能
2. **逻辑清晰** — 相关变更放在同一个提交；功能独立优先，只有强相关变更（同一功能的不同文件）才合并
3. **可回滚** — 每个提交都可独立回滚
4. **不混合** — 不要混合不同功能的变更

## 安全规则

1. **不提交敏感信息** — 密码、密钥、token、.env 文件
2. **不提交临时文件** — 编译产物、日志文件
3. **不提交大文件** — 使用 Git LFS 或外部存储
4. **检查 diff** — 提交前检查 diff 内容
5. **不绕过 Git 保护** — 不更新 git config、不 `--no-verify`、不 force-push、不 `--allow-empty`、不用 `-i`
6. **不主动 amend** — amend 需用户明确请求；hook 拒绝后修复问题并创建新提交，不要 amend 失败的提交
7. **提交前校验** — 仓库有 pre-commit hook 自动运行 `validate-skills.sh`，克隆后执行 `git config core.hooksPath scripts/hooks` 启用
8. **不主动 push** — push 需用户明确请求，提交后不自动 push

## 示例

```
feat(auth): add OAuth2 login support

- Add Google OAuth2 integration
- Add GitHub OAuth2 integration
- Update user model with OAuth fields
- Add login/logout endpoints

Closes #123
```

