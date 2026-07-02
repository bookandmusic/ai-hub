# 性能优化模式

## 空间索引

碰撞检测是性能瓶颈。O(n²) 的两两检测在 n > 100 时会显著卡顿。空间索引将查询降到 O(n) 或 O(n log n)。

### 均匀网格（Grid）

适合对象分布均匀的场景（弹幕、粒子）：

```typescript
class SpatialGrid {
  private cellSize: number
  private cells: Map<string, Entity[]> = new Map()

  constructor(cellSize: number) {
    this.cellSize = cellSize
  }

  private key(x: number, y: number): string {
    return `${Math.floor(x / this.cellSize)},${Math.floor(y / this.cellSize)}`
  }

  insert(entity: Entity) {
    const k = this.key(entity.x, entity.y)
    if (!this.cells.has(k)) this.cells.set(k, [])
    this.cells.get(k)!.push(entity)
  }

  // 查询某实体附近的候选碰撞对象（只检查 3x3 邻域）
  queryNearby(entity: Entity): Entity[] {
    const cx = Math.floor(entity.x / this.cellSize)
    const cy = Math.floor(entity.y / this.cellSize)
    const result: Entity[] = []
    for (let dx = -1; dx <= 1; dx++) {
      for (let dy = -1; dy <= 1; dy++) {
        const cell = this.cells.get(`${cx + dx},${cy + dy}`)
        if (cell) result.push(...cell)
      }
    }
    return result
  }

  clear() {
    this.cells.clear()
  }
}

// 使用：每帧重建
const grid = new SpatialGrid(64)  // cellSize 略大于最大实体尺寸
grid.clear()
for (const e of entities) grid.insert(e)
for (const e of entities) {
  const candidates = grid.queryNearby(e)
  for (const other of candidates) {
    if (e.id < other.id && aabbCollision(e, other)) {
      handleCollision(e, other)
    }
  }
}
```

**要点：**
- cellSize 应略大于最大实体尺寸，确保 3x3 邻域覆盖所有可能碰撞
- `e.id < other.id` 避免重复检测同一对
- 每帧 clear + 重建，无需增量更新（实现简单且够快）

### 四叉树（Quadtree）

适合对象分布不均的场景（开放世界、稀疏区域）：

```typescript
interface Bounds { x: number; y: number; w: number; h: number }

class Quadtree {
  private capacity = 8
  private entities: Entity[] = []
  private divided = false
  private children: Quadtree[] = []

  constructor(private bounds: Bounds, private depth = 0) {}

  private subdivide() {
    const { x, y, w, h } = this.bounds
    const hw = w / 2, hh = h / 2
    this.children = [
      new Quadtree({ x, y, w: hw, h: hh }, this.depth + 1),
      new Quadtree({ x: x + hw, y, w: hw, h: hh }, this.depth + 1),
      new Quadtree({ x, y: y + hh, w: hw, h: hh }, this.depth + 1),
      new Quadtree({ x: x + hw, y: y + hh, w: hw, h: hh }, this.depth + 1),
    ]
    this.divided = true
  }

  insert(entity: Entity): boolean {
    if (!contains(this.bounds, entity)) return false
    if (this.entities.length < this.capacity || this.depth >= 5) {
      this.entities.push(entity)
      return true
    }
    if (!this.divided) this.subdivide()
    for (const child of this.children) {
      if (child.insert(entity)) return true
    }
    return false
  }

  query(range: Bounds, found: Entity[] = []): Entity[] {
    if (!intersects(this.bounds, range)) return found
    for (const e of this.entities) {
      if (contains(range, e)) found.push(e)
    }
    if (this.divided) {
      for (const child of this.children) child.query(range, found)
    }
    return found
  }

  clear() {
    this.entities = []
    if (this.divided) {
      for (const c of this.children) c.clear()
    }
    this.divided = false
    this.children = []
  }
}
```

**对比：**

| 场景 | 推荐 | 原因 |
|------|------|------|
| 弹幕/粒子（均匀分布） | 网格 | 实现简单，常数因子小 |
| 开放世界（稀疏分布） | 四叉树 | 稀疏区域查询快 |
| 实时策略（大量单位） | 网格 | 单位尺寸接近 |
| 平台跳跃（少量对象） | 两两检测 | n < 50 时索引开销 > 收益 |

## 对象池

频繁创建/销毁对象（子弹、粒子、伤害数字）会导致 GC 卡顿。对象池预分配并复用：

```typescript
class ObjectPool<T> {
  private pool: T[] = []
  private active: Set<T> = new Set()

  constructor(
    private factory: () => T,
    private reset: (obj: T) => void,
    initialSize: number = 0
  ) {
    for (let i = 0; i < initialSize; i++) {
      this.pool.push(this.factory())
    }
  }

  acquire(): T {
    let obj = this.pool.pop()
    if (!obj) obj = this.factory()
    this.active.add(obj)
    return obj
  }

  release(obj: T): void {
    if (!this.active.has(obj)) return
    this.reset(obj)
    this.active.delete(obj)
    this.pool.push(obj)
  }

  // 每帧结束后批量回收 inactive 对象
  releaseInactive(isActive: (obj: T) => boolean): void {
    for (const obj of [...this.active]) {
      if (!isActive(obj)) this.release(obj)
    }
  }

  get activeCount(): number {
    return this.active.size
  }
}

// 子弹池示例
interface Bullet {
  active: boolean
  x: number; y: number
  vx: number; vy: number
  damage: number
}

const bulletPool = new ObjectPool<Bullet>(
  () => ({ active: false, x: 0, y: 0, vx: 0, vy: 0, damage: 10 }),
  (b) => { b.active = false; b.x = 0; b.y = 0; b.vx = 0; b.vy = 0 },
  100  // 预分配 100 个
)

// 发射
function fireBullet(x: number, y: number, vx: number, vy: number) {
  const bullet = bulletPool.acquire()
  bullet.active = true
  bullet.x = x; bullet.y = y
  bullet.vx = vx; bullet.vy = vy
}

// 每帧更新后回收
function updateBullets(dt: number) {
  for (const b of bulletPool.active) {
    b.x += b.vx * dt
    b.y += b.vy * dt
    if (b.x < 0 || b.x > 800) b.active = false  // 出界
  }
  bulletPool.releaseInactive(b => b.active)
}
```

**要点：**
- 预分配数量参考峰值用量（如子弹池预分配 100-500）
- `reset` 函数必须重置所有字段，避免状态泄漏
- `releaseInactive` 用 `[...this.active]` 避免迭代中修改集合

## Draw Call 优化

### Canvas 2D：状态最小化

每次 `fillStyle`/`strokeStyle`/`font` 变更都会触发状态切换：

```typescript
// 错误：每个对象都切换 fillStyle
for (const e of entities) {
  ctx.fillStyle = e.color
  ctx.fillRect(e.x, e.y, e.w, e.h)
}

// 正确：按 fillStyle 分组
const byColor = new Map<string, Entity[]>()
for (const e of entities) {
  if (!byColor.has(e.color)) byColor.set(e.color, [])
  byColor.get(e.color)!.push(e)
}
for (const [color, group] of byColor) {
  ctx.fillStyle = color
  for (const e of group) {
    ctx.fillRect(e.x, e.y, e.w, e.h)
  }
}
```

### Sprite Atlas 批渲染

```typescript
class SpriteAtlas {
  private regions: Map<string, { x: number; y: number; w: number; h: number }> = new Map()

  constructor(private image: HTMLImageElement) {}

  register(name: string, x: number, y: number, w: number, h: number) {
    this.regions.set(name, { x, y, w, h })
  }

  draw(ctx: CanvasRenderingContext2D, name: string, dx: number, dy: number) {
    const r = this.regions.get(name)
    if (!r) return
    ctx.drawImage(this.image, r.x, r.y, r.w, r.h, dx, dy, r.w, r.h)
  }
}

// 所有 sprite 共享同一张图，GPU 纹理绑定只发生一次
const atlas = new SpriteAtlas(await loadImage('/sprites/atlas.webp'))
atlas.register('player_idle', 0, 0, 32, 32)
atlas.register('player_run', 32, 0, 32, 32)
```

## 内存管理

### AudioBuffer 释放

```typescript
class AudioManager {
  private buffers: Map<string, AudioBuffer> = new Map()

  // 场景切换时释放该场景独有的音频
  unloadScene(scene: string) {
    const keys = [...this.buffers.keys()].filter(k => k.startsWith(`${scene}_`))
    for (const k of keys) {
      this.buffers.delete(k)  // 解除引用，让 GC 回收
    }
  }

  // 游戏结束时彻底清理
  destroy() {
    this.buffers.clear()
    this.audioCtx?.close()
    this.audioCtx = null
  }
}
```

### 纹理释放（WebGL）

```typescript
class TextureManager {
  private textures: Map<string, WebGLTexture> = new Map()

  unload(name: string) {
    const tex = this.textures.get(name)
    if (tex) {
      gl.deleteTexture(tex)
      this.textures.delete(name)
    }
  }

  destroy() {
    for (const tex of this.textures.values()) {
      gl.deleteTexture(tex)
    }
    this.textures.clear()
  }
}
```

## 性能测量

### FPS 监控

```typescript
class FPSMonitor {
  private frames = 0
  private lastTime = performance.now()
  private fps = 0

  update() {
    this.frames++
    const now = performance.now()
    if (now - this.lastTime >= 1000) {
      this.fps = Math.round(this.frames * 1000 / (now - this.lastTime))
      this.frames = 0
      this.lastTime = now
    }
  }

  get current(): number {
    return this.fps
  }
}

// 帧耗时分析
class FrameTimer {
  private samples: number[] = []
  private maxSamples = 60

  record(frameTime: number) {
    this.samples.push(frameTime)
    if (this.samples.length > this.maxSamples) this.samples.shift()
  }

  get avg(): number {
    return this.samples.reduce((a, b) => a + b, 0) / this.samples.length
  }

  get p99(): number {
    const sorted = [...this.samples].sort((a, b) => a - b)
    return sorted[Math.floor(sorted.length * 0.99)] ?? 0
  }
}
```

### 内存泄漏检测

```typescript
// 在游戏开始和运行 30 分钟后各拍一次堆快照对比
function logMemory(label: string) {
  const mem = (performance as any).memory
  if (mem) {
    console.log(`${label}: used=${(mem.usedJSHeapSize / 1024 / 1024).toFixed(1)}MB, total=${(mem.totalJSHeapSize / 1024 / 1024).toFixed(1)}MB`)
  }
}
```

**性能预算（与 acceptance.md 对齐）：**
- 桌面：60fps，帧耗时 < 16ms
- 移动：30fps 最低，帧耗时 < 33ms
- 内存：30 分钟运行增长 < 50MB（Canvas 2D）/ < 80MB（WebGL）
