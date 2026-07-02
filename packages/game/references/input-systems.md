# 游戏输入系统

## 架构概览

建议采用**统一输入抽象层**，将原始输入事件转换为游戏内部动作：

```
Input Events (DOM) → Input Manager → Game Actions → Game Logic
```

## 输入管理器

```typescript
// 游戏动作枚举
enum GameAction {
  MOVE_LEFT = 'MOVE_LEFT',
  MOVE_RIGHT = 'MOVE_RIGHT',
  JUMP = 'JUMP',
  ATTACK = 'ATTACK',
  PAUSE = 'PAUSE',
  INTERACT = 'INTERACT',
}

class InputManager {
  private state = {
    justPressed: new Set<GameAction>(),  // 本帧按下的动作
    held: new Set<GameAction>(),         // 持续按住的动作
    released: new Set<GameAction>(),     // 本帧释放的动作
    pointer: { x: 0, y: 0, isDown: false },
    axis: { dx: 0, dy: 0 },
  }

  private keys: Map<string, GameAction> = new Map()
  private heldKeys: Set<string> = new Set()      // 当前按住的物理键
  private touchId: number | null = null
  private gamepadIdx: number = -1
  private prevGamepadButtons: Set<number> = new Set()
  private abortController: AbortController = new AbortController()

  constructor() {
    setupKeyboard.call(this)
    setupMouse.call(this)
    setupTouch.call(this)
    setupGamepad.call(this)
  }

  // 每帧开始前调用，为下一帧准备状态
  beginFrame() {
    this.state.justPressed.clear()
    this.state.held.clear()
    this.state.released.clear()
    this.state.axis.dx = 0
    this.state.axis.dy = 0

    // 从 heldKeys 重建 held 动作（支持连续按键）
    for (const key of this.heldKeys) {
      const action = this.keys.get(key)
      if (action) this.state.held.add(action)
    }

    pollGamepad.call(this) // 在 beginFrame() 末尾轮询手柄
  }

  // --- 查询 API ---

  /** 本帧刚按下 */
  isJustPressed(action: GameAction): boolean {
    return this.state.justPressed.has(action)
  }

  /** 正在按住 */
  isHeld(action: GameAction): boolean {
    return this.state.held.has(action)
  }

  /** 本帧刚释放 */
  isReleased(action: GameAction): boolean {
    return this.state.released.has(action)
  }

  /** 按下的任意状态（justPressed || held） */
  isDown(action: GameAction): boolean {
    return this.isJustPressed(action) || this.isHeld(action)
  }

  getPointer() { return this.state.pointer }
  getAxis() { return this.state.axis }

  destroy() {
    this.abortController.abort()
    this.abortController = new AbortController()
    this.heldKeys.clear()
    this.prevGamepadButtons.clear()
    this.state.justPressed.clear()
    this.state.held.clear()
    this.state.released.clear()
  }
}
```

## 键盘输入

```typescript
function setupKeyboard() {
  this.keys.set('ArrowLeft', GameAction.MOVE_LEFT)
  this.keys.set('ArrowRight', GameAction.MOVE_RIGHT)
  this.keys.set('ArrowUp', GameAction.JUMP)
  this.keys.set(' ', GameAction.JUMP)
  this.keys.set('z', GameAction.ATTACK)
  this.keys.set('Escape', GameAction.PAUSE)

  document.addEventListener('keydown', (e) => {
    const action = this.keys.get(e.key)
    if (action) {
      e.preventDefault()
      if (!this.heldKeys.has(e.key)) {
        this.state.justPressed.add(action)
      }
      this.heldKeys.add(e.key)
    }
  }, { signal: this.abortController.signal })

  document.addEventListener('keyup', (e) => {
    const action = this.keys.get(e.key)
    if (action) {
      this.heldKeys.delete(e.key)
      this.state.held.delete(action)
      this.state.released.add(action)
    }
  }, { signal: this.abortController.signal })

  // 窗口失焦时清空输入状态，防止粘滞键
  window.addEventListener('blur', () => {
    this.heldKeys.clear()
    this.prevGamepadButtons.clear()
    this.state.justPressed.clear()
    this.state.held.clear()
    this.state.released.clear()
  }, { signal: this.abortController.signal })

  // 标签页切换时同样清空输入状态
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      this.heldKeys.clear()
      this.prevGamepadButtons.clear()
      this.state.justPressed.clear()
      this.state.held.clear()
      this.state.released.clear()
    }
  }, { signal: this.abortController.signal })
}
```

### 注意事项
- 使用 `keydown`/`keyup`（非 `keypress`），以支持长按
- `heldKeys` 跟踪物理按键的持续状态，每帧 `beginFrame()` 中将 heldKeys 转换为 GameAction
- 防止页面滚动（`ArrowUp`/`ArrowDown`/`Space` 需要 `preventDefault`）
- 游戏失焦时清空 `heldKeys` 防止粘滞键

## 鼠标输入

```typescript
function setupMouse() {
  const canvas = document.getElementById('game-canvas')!

  canvas.addEventListener('mousedown', (e) => {
    this.state.pointer.isDown = true
    updatePointerPosition.call(this, e, canvas)
    this.state.justPressed.add(GameAction.ATTACK)
  }, { signal: this.abortController.signal })

  canvas.addEventListener('mousemove', (e) => {
    updatePointerPosition.call(this, e, canvas)
  }, { signal: this.abortController.signal })

  document.addEventListener('mouseup', () => {
    this.state.pointer.isDown = false
    this.state.released.add(GameAction.ATTACK)
  }, { signal: this.abortController.signal })

  canvas.addEventListener('contextmenu', (e) => e.preventDefault(), { signal: this.abortController.signal })
}

function updatePointerPosition(e: MouseEvent, canvas: HTMLCanvasElement) {
  const rect = canvas.getBoundingClientRect()
  this.state.pointer.x = (e.clientX - rect.left) * (canvas.width / rect.width)
  this.state.pointer.y = (e.clientY - rect.top) * (canvas.height / rect.height)
}
```

## 触摸输入

```typescript
function setupTouch() {
  const canvas = document.getElementById('game-canvas')!

  canvas.addEventListener('touchstart', (e) => {
    e.preventDefault()
    this.state.pointer.isDown = true
    const touch = e.changedTouches[0]
    this.touchId = touch.identifier
    updateTouchPosition.call(this, touch, canvas)
    this.state.justPressed.add(GameAction.ATTACK)
  }, { signal: this.abortController.signal })

  canvas.addEventListener('touchmove', (e) => {
    e.preventDefault()
    for (const touch of e.changedTouches) {
      if (touch.identifier === this.touchId) {
        updateTouchPosition.call(this, touch, canvas)
      }
    }
  }, { signal: this.abortController.signal })

  canvas.addEventListener('touchend', (e) => {
    for (const touch of e.changedTouches) {
      if (touch.identifier === this.touchId) {
        this.touchId = null
        this.state.pointer.isDown = false
        this.state.released.add(GameAction.ATTACK)
      }
    }
  }, { signal: this.abortController.signal })

  canvas.addEventListener('touchcancel', () => {
    this.touchId = null
    this.state.pointer.isDown = false
    this.state.released.add(GameAction.ATTACK)
  }, { signal: this.abortController.signal })
}

function updateTouchPosition(touch: Touch, canvas: HTMLCanvasElement) {
  const rect = canvas.getBoundingClientRect()
  this.state.pointer.x = (touch.clientX - rect.left) * (canvas.width / rect.width)
  this.state.pointer.y = (touch.clientY - rect.top) * (canvas.height / rect.height)
}
```

### 触摸要点
- 必须 `preventDefault` 防止页面滚动/缩放
- 记录 `touch.identifier` 跟踪特定手指（多点触控支持）
- 虚拟摇杆：使用 touchstart 位置作为摇杆原点

## Gamepad（手柄）支持

```typescript
function setupGamepad() {
  window.addEventListener('gamepadconnected', (e: GamepadEvent) => {
    this.gamepadIdx = e.gamepad.index
  }, { signal: this.abortController.signal })
  window.addEventListener('gamepaddisconnected', () => {
    this.gamepadIdx = -1
    this.prevGamepadButtons.clear()
  }, { signal: this.abortController.signal })
}

// 由 beginFrame() 自动轮询（无需手动调用）
function pollGamepad() {
  if (this.gamepadIdx === -1) return
  const gamepad = navigator.getGamepads()[this.gamepadIdx]
  if (!gamepad) return

  // 按钮映射
  const BTN_MAP: [number, GameAction][] = [
    [0, GameAction.ATTACK],   // A
    [1, GameAction.JUMP],     // B
    [9, GameAction.PAUSE],    // Start
  ]
  const currentButtons = new Set<number>()
  for (const [btnIdx, action] of BTN_MAP) {
    if (gamepad.buttons[btnIdx]?.pressed) {
      currentButtons.add(btnIdx)
      if (!this.prevGamepadButtons.has(btnIdx)) {
        this.state.justPressed.add(action)
      }
      this.state.held.add(action)
    }
  }
  // 处理释放的按钮
  for (const btnIdx of this.prevGamepadButtons) {
    if (!currentButtons.has(btnIdx)) {
      const entry = BTN_MAP.find(([i]) => i === btnIdx)
      if (entry) {
        this.state.held.delete(entry[1])
        this.state.released.add(entry[1])
      }
    }
  }

  this.prevGamepadButtons = currentButtons

  // 左摇杆 → axis
  this.state.axis.dx = Math.abs(gamepad.axes[0]) > 0.2 ? gamepad.axes[0] : 0
  this.state.axis.dy = Math.abs(gamepad.axes[1]) > 0.2 ? gamepad.axes[1] : 0
}
```

## 游戏循环集成

```typescript
function gameLoop(timestamp: number) {
  input.beginFrame()  // 重建 justPressed / held / released + 轮询手柄

  if (input.isDown(GameAction.MOVE_LEFT)) {
    player.velocity.x -= speed * dt
  }
  if (input.isJustPressed(GameAction.JUMP)) {
    player.jump()
  }
  if (input.isReleased(GameAction.ATTACK)) {
    player.stopAttack()
  }

  update(dt)
  render()

  requestAnimationFrame(gameLoop)
}
```

## 输入映射配置

```typescript
interface KeyBindings {
  [action: string]: string
}

function applyBindings(manager: InputManager, bindings: KeyBindings) {
  const map = new Map<string, GameAction>()
  for (const [action, key] of Object.entries(bindings)) {
    map.set(key, action as GameAction)
  }
  manager.keys = map
  manager.heldKeys.clear()
  manager.prevGamepadButtons.clear()
  manager.state.held.clear()
}
```

## 虚拟摇杆（移动端）

动态原点摇杆：玩家在屏幕左侧任意位置按下即激活摇杆，拖动控制方向：

```typescript
class VirtualJoystick {
  private origin: { x: number; y: number } | null = null
  private current: { x: number; y: number } | null = null
  private touchId: number | null = null
  private maxRadius = 50   // 最大拖动半径（像素）
  private deadZone = 0.15  // 死区阈值（归一化后）

  constructor(private canvas: HTMLCanvasElement, private abortController: AbortController) {
    this.setup()
  }

  private setup() {
    this.canvas.addEventListener('touchstart', (e) => {
      // 仅在左侧屏幕激活摇杆（右侧留给攻击按钮）
      const touch = e.changedTouches[0]
      if (touch.clientX < window.innerWidth / 2 && this.touchId === null) {
        e.preventDefault()
        this.touchId = touch.identifier
        this.origin = { x: touch.clientX, y: touch.clientY }
        this.current = { x: touch.clientX, y: touch.clientY }
      }
    }, { signal: this.abortController.signal })

    this.canvas.addEventListener('touchmove', (e) => {
      for (const touch of e.changedTouches) {
        if (touch.identifier === this.touchId) {
          this.current = { x: touch.clientX, y: touch.clientY }
        }
      }
    }, { signal: this.abortController.signal })

    this.canvas.addEventListener('touchend', (e) => {
      for (const touch of e.changedTouches) {
        if (touch.identifier === this.touchId) {
          this.touchId = null
          this.origin = null
          this.current = null
        }
      }
    }, { signal: this.abortController.signal })

    this.canvas.addEventListener('touchcancel', () => {
      this.touchId = null
      this.origin = null
      this.current = null
    }, { signal: this.abortController.signal })
  }

  // 获取归一化轴向输入 [-1, 1]
  getAxis(): { dx: number; dy: number } {
    if (!this.origin || !this.current) return { dx: 0, dy: 0 }
    let dx = (this.current.x - this.origin.x) / this.maxRadius
    let dy = (this.current.y - this.origin.y) / this.maxRadius
    // 限制到单位圆
    const mag = Math.sqrt(dx * dx + dy * dy)
    if (mag > 1) {
      dx /= mag
      dy /= mag
    }
    // 死区
    if (Math.abs(dx) < this.deadZone) dx = 0
    if (Math.abs(dy) < this.deadZone) dy = 0
    return { dx, dy }
  }

  // 渲染摇杆 UI（调试或始终显示）
  render(ctx: CanvasRenderingContext2D) {
    if (!this.origin) return
    ctx.save()
    // 外圈
    ctx.strokeStyle = 'rgba(255,255,255,0.3)'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.arc(this.origin.x, this.origin.y, this.maxRadius, 0, Math.PI * 2)
    ctx.stroke()
    // 拇指
    if (this.current) {
      ctx.fillStyle = 'rgba(255,255,255,0.5)'
      ctx.beginPath()
      ctx.arc(this.current.x, this.current.y, 20, 0, Math.PI * 2)
      ctx.fill()
    }
    ctx.restore()
  }
}
```

### 集成到 InputManager

```typescript
class InputManager {
  private joystick: VirtualJoystick | null = null

  // 移动端初始化时创建摇杆
  initTouchControls(canvas: HTMLCanvasElement) {
    this.joystick = new VirtualJoystick(canvas, this.abortController)
  }

  beginFrame() {
    // ... 原有重建逻辑
    // 覆盖 axis 输入（如果有摇杆输入则优先）
    if (this.joystick) {
      const axis = this.joystick.getAxis()
      if (axis.dx !== 0 || axis.dy !== 0) {
        this.state.axis.dx = axis.dx
        this.state.axis.dy = axis.dy
      }
    }
  }

  // 渲染摇杆 UI（在游戏渲染之后调用）
  renderJoystick(ctx: CanvasRenderingContext2D) {
    this.joystick?.render(ctx)
  }
}
```

**要点：**
- 动态原点：touchstart 位置作为摇杆原点，玩家可在屏幕左侧任意位置开始拖动
- 死区：避免微小抖动导致角色漂移（0.15 阈值）
- 单位圆限制：拖动超过 maxRadius 时归一化到边缘
- 左右分区：左侧摇杆，右侧留给攻击/跳跃按钮（避免冲突）
- `touchcancel` 必须处理：系统中断触摸时重置状态
```