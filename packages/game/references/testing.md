# 游戏测试最佳实践

## 测试分层

```
单元测试 → 集成测试 → E2E 测试 → 验收测试
```

- **单元测试**: 测试独立函数/类（碰撞检测、状态机、数值计算）
- **集成测试**: 测试子系统协作（输入→逻辑→渲染）
- **E2E 测试**: 模拟真实用户操作（Playwright/Puppeteer）
- **验收测试**: 使用 `checklists/acceptance.md` 逐项验证

## 测试框架

| 场景 | 推荐框架 | 备注 |
|------|---------|------|
| 单元/集成测试 | Vitest / Jest | 优先 Vitest（Vite 生态，更快） |
| E2E 测试 | Playwright | 支持移动端模拟、网络条件模拟 |
| 性能测试 | Vitest bench / Lighthouse CI | 基准测试 + 性能预算 |
| 视觉回归 | Playwright Screenshot | 像素级对比 Canvas 输出 |

## 关键测试领域

### 状态机测试

```typescript
// 示例：状态转换测试
describe('GameStateMachine', () => {
  it('从 MENU 转换到 PLAYING', () => {
    const fsm = new GameStateMachine()
    fsm.transition('START_GAME')
    expect(fsm.current).toBe('PLAYING')
  })

  it('PLAYING 状态下暂停键切换到 PAUSED', () => {
    const fsm = new GameStateMachine()
    fsm.transition('START_GAME')
    fsm.transition('PAUSE')
    expect(fsm.current).toBe('PAUSED')
  })

  it('无效转换抛出错误', () => {
    const fsm = new GameStateMachine()
    expect(() => fsm.transition('PAUSE')).toThrow()
  })
})
```

- 覆盖状态转换表（可用的状态→事件→目标状态）
- 测试边界转换（同一状态连续触发同一事件）
- 测试状态进入/离开时的资源清理

### 碰撞检测测试

```typescript
describe('Collision Detection', () => {
  it('AABB 碰撞——重叠时返回 true', () => {
    const a = { x: 0, y: 0, w: 10, h: 10 }
    const b = { x: 5, y: 5, w: 10, h: 10 }
    expect(aabbCollision(a, b)).toBe(true)
  })

  it('AABB 碰撞——不重叠时返回 false', () => {
    const a = { x: 0, y: 0, w: 10, h: 10 }
    const b = { x: 20, y: 20, w: 10, h: 10 }
    expect(aabbCollision(a, b)).toBe(false)
  })

  it('圆形碰撞——边缘接触时返回 true', () => {
    const a = { x: 0, y: 0, r: 5 }
    const b = { x: 10, y: 0, r: 5 }
    expect(circleCollision(a, b)).toBe(true)
  })
})
```

- AABB、圆形、像素级碰撞等各实现类型独立测试
- 边界条件：恰好接触、完全重叠、零尺寸对象

### 固定时间步长测试

```typescript
describe('Fixed Timestep', () => {
  it('累积时间达到步长时执行固定次数的更新', () => {
    const loop = new GameLoop({ fixedDt: 1 / 60 })
    let updateCount = 0
    loop.onUpdate = () => { updateCount++ }

    loop.tick(1 / 30)  // 累积 33ms，应执行 2 次更新
    expect(updateCount).toBe(2)
  })

  it('长时间暂停后不会一次执行大量更新（上限保护）', () => {
    const loop = new GameLoop({ fixedDt: 1 / 60, maxFrameTime: 0.1 })
    let updateCount = 0
    loop.onUpdate = () => { updateCount++ }

    loop.tick(5)  // 5 秒 pause，受 maxFrameTime 限制
    expect(updateCount).toBeLessThanOrEqual(6)  // 0.1 / (1/60) = 6
  })
})
```

- 帧率无关断言：不断言固定帧数，用 fixedDt 和累积时间推导
- 大时间片保护（spiral of death）：确认 maxFrameTime 生效
- deltaTime 传递验证：更新函数收到的 dt 是否为固定值

### 输入系统测试

```typescript
describe('InputManager', () => {
  let im: InputManager

  afterEach(() => {
    im?.destroy()
  })

  it('keydown 设置 justPressed 和 held', () => {
    im = new InputManager()
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowLeft' }))
    im.beginFrame()
    expect(im.isJustPressed(GameAction.MOVE_LEFT)).toBe(true)
    expect(im.isHeld(GameAction.MOVE_LEFT)).toBe(true)
  })

  it('按键重复不会重复触发 justPressed', () => {
    im = new InputManager()
    document.dispatchEvent(new KeyboardEvent('keydown', { key: ' ' }))
    document.dispatchEvent(new KeyboardEvent('keydown', { key: ' ' }))
    im.beginFrame()
    expect(im.state.justPressed.size).toBe(1)
  })

  it('keyup 清除 held 并设置 released', () => {
    im = new InputManager()
    // 第一帧：按下
    document.dispatchEvent(new KeyboardEvent('keydown', { key: ' ' }))
    im.beginFrame()
    expect(im.isHeld(GameAction.JUMP)).toBe(true)

    // 第二帧：释放（在 beginFrame 前检查 released）
    document.dispatchEvent(new KeyboardEvent('keyup', { key: ' ' }))
    expect(im.isReleased(GameAction.JUMP)).toBe(true)
    im.beginFrame()
    expect(im.isReleased(GameAction.JUMP)).toBe(false)
  })

  it('blur 事件清空所有输入状态', () => {
    im = new InputManager()
    document.dispatchEvent(new KeyboardEvent('keydown', { key: ' ' }))
    window.dispatchEvent(new Event('blur'))
    im.beginFrame()
    expect(im.isDown(GameAction.JUMP)).toBe(false)
  })

  it('visibilitychange 隐藏时清空输入状态', () => {
    im = new InputManager()
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'z' }))
    Object.defineProperty(document, 'hidden', { value: true })
    document.dispatchEvent(new Event('visibilitychange'))
    im.beginFrame()
    expect(im.isDown(GameAction.ATTACK)).toBe(false)
  })
})
```

- 使用真实的 DOM 事件分发（`dispatchEvent`）而非 mock
- 注意 `beginFrame()` 必须在断言前调用（状态在帧开始重建）
- 测试 blur/visibilitychange 的粘滞键保护

### 音频生命周期测试

```typescript
describe('Audio Lifecycle', () => {
  it('initAudio 在首次调用时创建 AudioContext', () => {
    initAudio()
    expect(audioCtx).not.toBeNull()
    expect(audioCtx?.state).not.toBe('closed')
  })

  it('AudioContext closed 后 initAudio 重新创建', () => {
    initAudio()
    audioCtx!.close()
    initAudio()
    expect(audioCtx?.state).not.toBe('closed')
  })

  it('BGM 通过 bgmGain 连接 masterGain', () => {
    initAudio()
    // 验证拓扑：bgmGain → masterGain → destination
    // 通过 mock AudioNode.connect 追踪调用链
  })
})
```

- 注意：AudioContext 在测试环境中可能受限，建议对 `AudioContext` 做 mock 或使用 `fakeAudioContext`
- 测试连接拓扑：验证 GainNode 的 connect 调用顺序
- 验证 `visibilitychange` 正确调用 `suspend`/`resume`

### 游戏循环 E2E 测试

```typescript
import { test, expect } from '@playwright/test'

test('游戏循环在页面加载后启动', async ({ page }) => {
  await page.goto('/game')
  // 等待 Canvas 渲染开始（帧计数增长）
  await page.waitForFunction(() => {
    const canvas = document.querySelector('canvas')
    // 通过像素变化检测渲染是否活跃
    return canvas && canvas.getContext?.('2d')
  })
})

test('暂停/恢复功能正常', async ({ page }) => {
  await page.goto('/game')
  await page.keyboard.press('Escape')
  // 暂停菜单可见
  await expect(page.locator('.pause-menu')).toBeVisible()
  await page.click('.pause-menu .resume-btn')
  // 暂停菜单消失
  await expect(page.locator('.pause-menu')).not.toBeVisible()
})
```

## 性能测试

```typescript
describe('Performance', () => {
  it('对象池复用减少 GC 压力', () => {
    const pool = new ObjectPool(() => new Bullet(), 100)
    // 使用 globalThis.performance.memory（Chrome DevTools）或 mock 衡量
    // 注：process.memoryUsage() 仅限 Node.js 环境；浏览器中可用 performance.memory
    const before = (performance as any).memory?.usedJSHeapSize ?? 0
    for (let i = 0; i < 1000; i++) {
      const obj = pool.get()
      pool.release(obj)
    }
    const after = (performance as any).memory?.usedJSHeapSize ?? 0
    // 1000 次 get/release 不应有明显内存增长
    expect(after - before).toBeLessThan(1024 * 50) // < 50KB
  })
})
```

## 测试注意事项

- **帧率无关**: 断言不要依赖具体帧数，使用累积时间推导
- **时间控制**: 使用 `vi.useFakeTimers()` (Vitest) 控制 requestAnimationFrame
- **DOM 隔离**: 使用 `jsdom` 环境或真实浏览器（Playwright）
- **Canvas mock**: 测试逻辑时 mock Canvas API，避免 headless 运行问题
- **资源清理**: 每个测试后清理 event listener、AudioContext、Canvas