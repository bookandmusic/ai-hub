---
name: game
description: |
  Web 游戏开发。聚焦游戏特有节点：玩法规划、资源清单、游戏循环实现、游戏特有审查、游戏验收。
  通用步骤（需求分析/视觉风格/UI 实现/lint/commit/push）委托对应 skill 或遵守 AGENTS.md。
  遇到以下任一情况就主动使用本 skill：
  ①用户出现触发词：网页游戏 / 做一个游戏 / 游戏开发 / 做游戏 / web game / make a game；
  ②用户要求开发 Web 游戏。
metadata:
  project: dev-workflow
  tier: 2
  category: domain-specific
  user_visible: true
---

# game — Web 游戏开发

## 定位

游戏特有工作流编排器 + 游戏技术知识包。
通用步骤委托外部 skill 或遵守 AGENTS.md，game 只聚焦游戏特有节点。

## 流程

1. **玩法规划** → `templates/gameplay-template.md`（核心循环 / 时间系统 / 难度曲线 / 奖励机制 / 胜负判定 / 暂停重开）
   - 确认核心玩法后再进入下一步
2. **资源清单** → `templates/asset-plan.md`（视觉 / 音频资源规划；可用占位资源先行）
3. **游戏循环实现** → 实现顺序：①循环骨架（`references/game-loop.md`）→ ②输入系统（`references/input-systems.md`，移动端含虚拟摇杆）→ ③音频生命周期（`references/audio-lifecycle.md`）→ ④性能优化（`references/performance.md` 空间索引 / 对象池）→ ⑤编写测试（`references/testing.md`）；存档需求参考 `references/save-system.md`
   - 完成后运行 lint / typecheck（参考 AGENTS.md）
4. **游戏特有审查** → `checklists/review.md`（State / Input / Audio / Render / Mobile / WebGPU / Security / Accessibility / Code Quality）
5. **游戏验收** → `checklists/acceptance.md`（核心路径 / 边界路径 / 性能指标）

> 步骤 3-5 为迭代循环（实现 → 审查 → 验收 → 改进）

## 委托的外部 skill

| 步骤 | 委托 skill | 状态 | Fallback |
|------|-----------|------|----------|
| 需求分析 | `brainstorming` | 全局已安装即可用 | — |
| UI/HUD 视觉风格 | `huashu-design` | 全局已安装即可用 | game 自带游戏整体视觉 |
| UI/HUD 实现 | `vue` + `responsive-design` + `tailwind-design-system` | 需用户安装 | 原生 HTML / Canvas |
| 提交 | `git-commit` | 本仓库可用 | — |
| lint / typecheck | — | 遵守 AGENTS.md | — |
| 发布 | — | 需用户明确要求 | 不主动 push |

## 游戏特有内容

### templates/

- `gameplay-template.md` — 玩法、核心循环、时间系统、难度曲线、奖励机制、胜负判定、暂停重开
- `asset-plan.md` — 视觉 / 音频资源规划

### checklists/

- `review.md` — State / Input / Audio / Render / Mobile / WebGPU / Security / Accessibility / Code Quality 审查
- `acceptance.md` — 核心路径、边界路径、性能指标

### references/

- `game-loop.md` — 游戏循环架构（固定时间步长 + 系统组合）
- `input-systems.md` — 输入系统（键盘 / 鼠标 / 触摸 / 手柄 / 虚拟摇杆）
- `audio-lifecycle.md` — 音频生命周期
- `performance.md` — 性能优化模式（空间索引 / 对象池 / Draw Call 优化 / 内存管理）
- `save-system.md` — 存档与持久化（localStorage / IndexedDB / 版本迁移 / 防作弊）
- `testing.md` — 游戏测试最佳实践

## 核心技术栈（非 skill）

- Canvas 2D API / WebGL / WebGPU — 游戏渲染
- requestAnimationFrame — 游戏循环
- 固定时间步长 (fixed timestep) + deltaTime — 物理 / 逻辑更新
