# 游戏玩法模板

## 核心循环

### 循环模板（填空）

```
- **核心循环**: <30 秒核心循环描述，如：玩家移动 → 遭遇敌人 → 战斗 → 获得奖励 → 升级>
- **单局时长**: <预期单局游戏时长>
- **玩家目标**: <玩家需要达成的核心目标>
- **胜利判定**: <胜利条件，如：击败最终 BOSS / 达到指定分数 / 完成所有关卡>
- **失败判定**: <失败条件，如：生命值归零 / 时间耗尽 / 未达成目标>
- **暂停/重开**: <暂停和重开机制，如：按 Escape 暂停，显示暂停菜单，可选择继续或重新开始>
- **进度保存**: <存档机制，如：关卡自动保存 / 手动存档 / 无存档；详细模式参考 references/save-system.md>
```

### 循环要素

| 要素 | 描述 | 示例 |
|------|------|------|
| 玩家动作 | 玩家能做什么 | 移动、跳跃、攻击、收集、建造 |
| 世界响应 | 环境如何反应 | 敌人巡逻、道具刷新、平台移动、天气变化 |
| 反馈 | 玩家如何感知 | 得分变化、音效、特效、震动、伤害数字 |
| 奖励 | 玩家为什么继续 | 分数增长、升级、新能力解锁、剧情推进 |
| 循环周期 | 完成一次完整交互的时间 | 3-10 秒（动作游戏）或 30-60 秒（策略） |

### 代码骨架（集成 game-loop.md）

```typescript
import { GameState } from './state-machine'

class Game {
  private state: GameState = GameState.MENU
  private input: InputManager
  private audio: AudioManager
  private entities: Entity[] = []

  // 核心 update —— 每固定步长调用一次
  update(dt: number) {
    this.input.beginFrame()                    // 1. 重建输入状态 + 轮询手柄

    switch (this.state) {
      case GameState.MENU:
        this.updateMenu(dt)                    // 菜单动画、光标
        break
      case GameState.PLAYING:
        this.updatePlaying(dt)                 // 完整游戏逻辑
        break
      case GameState.PAUSED:
        // 不更新逻辑，保留最后一帧
        break
      case GameState.GAME_OVER:
        this.updateGameOver(dt)                // 分数展示、重试倒计时
        break
    }

    this.audio.update()                        // 2. 音频状态
  }

  private updatePlaying(dt: number) {
    for (const e of this.entities) {
      e.update(dt, this.input)                 // 更新游戏对象
    }
    this.checkCollisions()                     // 碰撞检测（参考 references/performance.md 空间索引）
    this.checkWinLose()                        // 胜负判定
    this.updateUI()                            // 刷新 HUD（分数、血量、进度）
  }

  // 渲染 —— 每帧调用，alpha 为插值因子
  render(alpha: number) {
    this.renderer.clear()
    for (const e of this.entities) {
      e.render(this.renderer, alpha)
    }
  }
}
```

**设计要点：**
- `update` 与 `render` 分离：update 用固定步长，render 每帧调用
- 状态机决定 update 行为，但 render 始终执行（暂停时仍渲染最后一帧）
- 帧顺序固定：Input → Logic → Physics → Audio → Render（详见 `references/game-loop.md`）

## 时间系统

### deltaTime

所有与时间相关的计算（移动、动画、冷却）必须乘以 dt，确保不同帧率下行为一致：

```typescript
class Player {
  speed = 200  // 像素/秒

  update(dt: number, input: InputManager) {
    if (input.isHeld(GameAction.MOVE_RIGHT)) {
      this.x += this.speed * dt   // 正确：速度 × 时间 = 位移
    }
  }
}
```

**错误示例：** `this.x += this.speed`（帧率依赖，60fps 走 200px/帧，30fps 也走 200px/帧 → 速度差 2 倍）

### 固定时间步长

物理/逻辑更新使用固定步长，避免物理不稳定。完整实现见 `references/game-loop.md`：

```typescript
const FIXED_DT = 1 / 60      // 物理/逻辑更新步长
const MAX_FRAME_TIME = 0.1    // 防止 spiral of death

// update 固定步长调用，render 每帧用 alpha 插值
while (accumulator >= FIXED_DT) {
  update(FIXED_DT)
  accumulator -= FIXED_DT
}
render(accumulator / FIXED_DT)
```

### 时间缩放

支持减速/加速效果（慢动作、加速道具），不影响 deltaTime 基准：

```typescript
class TimeManager {
  private scale = 1  // 1 = 正常，0.5 = 慢动作，2 = 加速

  // 游戏逻辑使用 scaledDt，UI 动画用原始 dt
  getGameDt(dt: number): number {
    return dt * this.scale
  }

  setSlowMotion(scale: number = 0.3) {
    this.scale = scale
  }

  reset() {
    this.scale = 1
  }
}

// 使用：游戏对象用 scaledDt，UI 动画用原始 dt
private updatePlaying(dt: number) {
  const gameDt = this.timeManager.getGameDt(dt)
  for (const e of this.entities) {
    e.update(gameDt, this.input)
  }
}
```

## 难度曲线

| 维度 | 描述 | 设计要点 | 数值参考 |
|------|------|---------|---------|
| 渐进难度 | 关卡/敌人强度随时间递增 | 每关提升 10-15% 属性 | 攻击力 ×1.1^level，血量 ×1.15^level |
| 自适应难度 | 根据玩家表现动态调整 | 连续失败 → 降低敌人数/伤害 | 连续死亡 3 次 → 敌人血量 ×0.8 |
| 难度选项 | 玩家可选的难度级别 | 简单/普通/困难 差异化参数 | 简单 ×0.7，普通 ×1.0，困难 ×1.3 |

### 自适应难度实现

```typescript
class DynamicDifficulty {
  baseMultiplier = 1.0
  private failureStreak = 0
  private successStreak = 0

  onPlayerDeath() {
    this.failureStreak++
    this.successStreak = 0
    if (this.failureStreak >= 3) {
      // 连续失败 3 次：降低 20% 难度，下限 0.6
      this.baseMultiplier = Math.max(0.6, this.baseMultiplier * 0.8)
      this.failureStreak = 0
    }
  }

  onLevelComplete() {
    this.successStreak++
    this.failureStreak = 0
    if (this.successStreak >= 2) {
      // 连续成功 2 次：提升 10% 难度，上限 1.5
      this.baseMultiplier = Math.min(1.5, this.baseMultiplier * 1.1)
      this.successStreak = 0
    }
  }

  // 应用到敌人属性
  getEnemyStat(base: number): number {
    return base * this.baseMultiplier
  }
}
```

## 奖励机制

| 类型 | 触发时机 | 实现要点 | 数值平衡参考 |
|------|---------|---------|-------------|
| 即时奖励 | 击杀/收集/到达 | 立即加分/掉落道具 | 小奖励 10-50 分，中奖励 100-500 分 |
| 累积奖励 | 多步操作后 | 连击计数器、收集进度 | 连击倍率 ×1.5/×2/×3，3/5/10 连击递增 |
| 随机奖励 | 概率掉落 | 权重表 + 随机抽取 | 普通道具 70%，稀有 25%，传说 5% |
| 长期奖励 | 成就/等级/赛季 | 持久化存储（见 save-system.md） | 等级经验曲线：next = 100 × 1.5^level |

### 奖励数值平衡

```typescript
interface DropEntry {
  item: string
  weight: number                 // 权重（相对概率）
  rarity: 'common' | 'rare' | 'legendary'
}

// 经验曲线：等级 n 升级所需经验
function expForLevel(level: number): number {
  return Math.floor(100 * Math.pow(1.5, level - 1))
}

// 随机掉落（加权抽取）
function rollDrop(table: DropEntry[]): DropEntry | null {
  const total = table.reduce((sum, e) => sum + e.weight, 0)
  let roll = Math.random() * total
  for (const entry of table) {
    roll -= entry.weight
    if (roll <= 0) return entry
  }
  return table[0]
}

// 连击倍率
function comboMultiplier(combo: number): number {
  if (combo >= 10) return 3
  if (combo >= 5) return 2
  if (combo >= 3) return 1.5
  return 1
}
```

## 玩法层级

### 架构示例（状态分离）

```typescript
// Meta 层：局外系统，持久化存储
class MetaState {
  playerLevel = 1
  totalCoins = 0
  unlockedLevels: Set<string> = new Set()
  achievements: Set<string> = new Set()

  // 持久化（详见 references/save-system.md）
  save(): object {
    return {
      version: 2,
      playerLevel: this.playerLevel,
      totalCoins: this.totalCoins,
      unlockedLevels: [...this.unlockedLevels],
      achievements: [...this.achievements],
    }
  }
}

// 核心层：每局体验，仅在 PLAYING 状态存在
class GameSession {
  score = 0
  health = 100
  currentLevel: string
  combo = 0

  reset(level: string) {
    this.score = 0
    this.health = 100
    this.currentLevel = level
    this.combo = 0
  }
}

// 反馈层：即时响应，不持久化
class FeedbackSystem {
  private shakeAmount = 0
  private flashAlpha = 0

  triggerShake(amount: number) {
    this.shakeAmount = Math.max(this.shakeAmount, amount)
  }

  triggerFlash() {
    this.flashAlpha = 1
  }

  render(ctx: CanvasRenderingContext2D) {
    // 屏幕震动：偏移渲染原点
    if (this.shakeAmount > 0) {
      const dx = (Math.random() - 0.5) * this.shakeAmount
      const dy = (Math.random() - 0.5) * this.shakeAmount
      ctx.save()
      ctx.translate(dx, dy)
      // ... 渲染游戏场景
      ctx.restore()
      this.shakeAmount *= 0.9  // 衰减
    }
    // 闪屏
    if (this.flashAlpha > 0) {
      ctx.fillStyle = `rgba(255,255,255,${this.flashAlpha})`
      ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height)
      this.flashAlpha *= 0.85
    }
  }
}
```

**分层原则：**
- Meta 层：跨局存在，必须持久化（save-system.md）
- 核心层：单局存在，每局重置，可选持久化（存档点）
- 反馈层：瞬时存在，每帧重算，不持久化

## 游戏类型参考

| 类型 | 核心循环 | 关键机制 | 实现要点 |
|------|---------|---------|---------|
| 动作 | 移动→攻击→闪避→连击 | 碰撞检测、帧精确输入 | hitbox/hurtbox 分离；攻击有 startup/active/recovery 三阶段；输入缓冲 100ms |
| RPG | 探索→战斗→升级→装备 | 属性系统、经验曲线、任务树 | 属性用 Modifier 链（base + 装备 + buff）；经验曲线用 1.5^n；任务状态机 |
| 解谜 | 观察→思考→操作→反馈 | 状态机、关卡状态回溯 | 关卡状态可序列化用于回溯；操作历史栈支持撤销 |
| 策略 | 规划→执行→评估→调整 | 回合制/实时决策树 | A*寻路；行为树 AI；Fog of War 用网格可见性 |
| 跑酷 | 前进→躲避→收集→加速 | 程序化生成、速度曲线 | 关卡段池随机拼接；速度递增曲线；预生成前方段 |
| 射击 | 探索→瞄准→射击→换弹 | 弹道计算、命中判定 | 子弹用对象池；射线检测（hitscan）vs 实体弹道；友军伤害 |
| 模拟 | 操作→反馈→优化→扩张 | 数值平衡、资源循环 | 经济系统用差分方程平衡；tick-based 更新；数据驱动配置 |
| 音乐/节奏 | 跟随节拍→输入→判定→连击 | BPM 同步、精确判定窗口 | 音频时间戳而非 rAF 判定；判定窗口 ±50ms（perfect）/±100ms（good） |
| 格斗 | 立回→择→连段→受击 | 帧数据、hitbox/hurtbox、取消链 | 帧数据表（startup/active/recovery）；取消窗口；格挡/招架时机 |
| 卡牌 | 抽牌→出牌→结算→抽牌 | 卡组构筑、费用系统、combo | 牌库洗牌算法；手牌上限；费用曲线（每回合 +1 最大费用） |
| Roguelike | 探索→战斗→收集→死亡→永久升级 | 程序化生成、permadeath、meta-progression | 房间生成算法（BSP/Cellular）；死亡后 meta 升级持久化；种子可复现 |
| 体育 | 操作→对抗→得分→重置 | 物理模拟、AI 行为树 | 球类物理（弹性碰撞）；AI 评分函数；规则状态机 |
| 放置/Idle | 等待→收集→升级→等待 | 离线收益、指数增长曲线 | 离线时间戳计算收益；数值用大数库；增长曲线 log 渐近 |
| 塔防 | 布置→升级→抵御→波次 | 寻路算法、炮塔放置、兵种克制 | 预计算路径；塔射程可视化；波次配置表；兵种伤害矩阵 |
| 平台跳跃 | 移动→跳跃→躲避→到达终点 | 重力系统、碰撞检测、关卡设计 | 重力 + 跳跃速度计算 apex；土狼时间 (coyote time) 100ms；跳跃缓冲 |
| 赛车 | 加速→转向→漂移→冲刺 | 物理模拟、赛道程序化生成、AI 对手 | 轮胎摩擦模型；漂移加速度；AI 路径跟随 + 难度调节 |
