# 游戏循环架构 — Game Loop Architecture

## 固定时间步长（Fixed Timestep）

游戏逻辑更新使用固定步长，渲染独立进行，确保不同帧率下行为一致。

```typescript
const FIXED_DT = 1 / 60      // 物理/逻辑更新步长
const MAX_FRAME_TIME = 0.1    // 防止 spiral of death

let accumulator = 0
let previousTime = 0

function gameLoop(currentTime: number) {
  const deltaTime = Math.min((currentTime - previousTime) / 1000, MAX_FRAME_TIME)
  previousTime = currentTime
  accumulator += deltaTime

  while (accumulator >= FIXED_DT) {
    update(FIXED_DT)
    accumulator -= FIXED_DT
  }

  render(accumulator / FIXED_DT)  // alpha 插值因子
  requestAnimationFrame(gameLoop)
}

requestAnimationFrame(gameLoop)
```

**为什么这样设计：**
- `MAX_FRAME_TIME` 防止浏览器长时间挂起后一次执行数百次更新（物理爆炸）
- Update 用固定步长，物理表现可预测/可复现
- Render 独立于 update 频率，保证视觉流畅
- `accumulator / FIXED_DT` 作为 alpha 插值因子，让渲染在 update 之间平滑过渡

## 系统组合

```typescript
class Game {
  private input: InputManager
  private audio: AudioManager
  private renderer: Renderer
  private entities: Entity[]

  constructor() {
    this.input = new InputManager()
    this.audio = new AudioManager()
    this.renderer = new Renderer()
    this.entities = []
  }

  update(dt: number) {
    this.input.beginFrame()          // 1. 重建输入状态 + 轮询手柄
    for (const e of this.entities) { // 2. 更新游戏对象
      e.update(dt, this.input)
    }
    this.checkCollisions()           // 3. 碰撞检测
    this.audio.update()              // 4. 音频状态
  }

  render(alpha: number) {
    this.renderer.clear()
    for (const e of this.entities) {
      e.render(this.renderer, alpha) // 传入插值因子用于平滑渲染
    }
  }
}
```

**设计要点：**
- 帧顺序固定：Input → Logic → Physics → Audio → Render
- Entity 不直接依赖 InputManager 类型，通过接口或动作查询解耦
- Renderer 作为渲染抽象，支持 Canvas 2D / WebGL 切换

## 状态机集成

游戏状态决定循环行为：

```typescript
enum GameState {
  MENU, PLAYING, PAUSED, GAME_OVER
}

function updateByState(dt: number) {
  switch (state) {
    case GameState.MENU:
      updateMenu(dt)       // 菜单动画、光标
      break
    case GameState.PLAYING:
      update(dt)           // 完整游戏逻辑
      checkWinLose()       // 胜负判定
      break
    case GameState.PAUSED:
      // 不调用 update()，保留最后一帧
      break
    case GameState.GAME_OVER:
      updateGameOver(dt)   // 分数展示、重试倒计时
      break
  }
}
```

**状态转换时清理：** input state、部分 AudioBuffer、计时器。

## 实体生命周期

```typescript
class Entity {
  active = true

  update(dt: number, input: InputManager) { /* 子类实现 */ }
  render(renderer: Renderer, alpha: number) { /* 子类实现 */ }

  destroy() {
    this.active = false
    // 清理引用，允许 GC
  }
}

// 对象池管理频繁创建/销毁的对象
class ObjectPool<T extends Entity> {
  private pool: T[] = []

  get(): T {
    return this.pool.find(e => !e.active) ?? this.create()
  }

  release(entity: T) {
    entity.destroy()
  }
}
```

## 暂停/恢复

```typescript
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    previousTime = 0  // 重置时间基准，防止 resume 后大跳跃
    audioCtx?.suspend()
  } else {
    audioCtx?.resume()
    previousTime = performance.now()  // 重新校准
    requestAnimationFrame(gameLoop)
  }
})

window.addEventListener('blur', () => {
  previousTime = 0
})
```

**关键：** visibilitychange 隐藏时暂停循环和音频，返回时重置时间基准而非累加空档期。