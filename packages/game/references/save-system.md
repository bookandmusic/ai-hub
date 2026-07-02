# 存档与持久化系统

## 存储后端选择

| 方案 | 容量 | 同步 | 适用场景 |
|------|------|------|---------|
| localStorage | 5-10MB | 同步 | 小型游戏，存档 < 1MB |
| IndexedDB | 50MB+ | 异步 | 中大型游戏，存档 > 1MB，含二进制资源 |
| sessionStorage | 5-10MB | 同步 | 单局存档，关闭标签即失效 |
| Cookie | 4KB | 同步 | 仅配置项，不推荐存档 |

**推荐：** localStorage 用于小存档（< 1MB），IndexedDB 用于大存档。

## 存档结构设计

### 版本化存档结构

```typescript
interface SaveData {
  version: number              // 存档版本号，用于迁移
  createdAt: number            // 创建时间戳
  updatedAt: number            // 最后更新时间戳
  meta: MetaState              // Meta 层（等级、解锁、成就）
  session?: GameSession        // 核心层（可选，存档点）
  settings: GameSettings       // 设置（音量、按键）
}

interface MetaState {
  playerLevel: number
  totalCoins: number
  unlockedLevels: string[]
  achievements: string[]
}

interface GameSettings {
  masterVolume: number
  bgmVolume: number
  sfxVolume: number
  keyBindings: Record<string, string>
}
```

**分层原则：**
- 必存：version、meta、settings
- 可选：session（存档点模式才存）
- 不存：feedback 层（震动、闪屏等瞬时状态）

## localStorage 实现

```typescript
const SAVE_KEY = 'game_save'
const CURRENT_VERSION = 2

class SaveManager {
  save(data: SaveData): boolean {
    try {
      data.version = CURRENT_VERSION
      data.updatedAt = Date.now()
      localStorage.setItem(SAVE_KEY, JSON.stringify(data))
      return true
    } catch (e) {
      if (e instanceof DOMException && e.name === 'QuotaExceededError') {
        // 存储空间已满
        console.warn('存储空间已满，存档失败')
        this.handleQuotaExceeded()
        return false
      }
      throw e
    }
  }

  load(): SaveData | null {
    const raw = localStorage.getItem(SAVE_KEY)
    if (!raw) return null  // 无存档

    try {
      const data = JSON.parse(raw) as SaveData
      return this.migrate(data)  // 版本迁移
    } catch (e) {
      // JSON 解析失败：存档损坏
      console.warn('存档损坏，重置为新存档', e)
      this.backupCorrupted(raw)
      return null
    }
  }

  delete() {
    localStorage.removeItem(SAVE_KEY)
  }

  private handleQuotaExceeded() {
    // 策略：删除旧备份，重试
    const backups = Object.keys(localStorage)
      .filter(k => k.startsWith('game_save_backup_'))
      .sort().reverse()
    for (const k of backups) {
      localStorage.removeItem(k)
      try {
        // 重试保存
        return
      } catch {
        continue
      }
    }
  }

  private backupCorrupted(raw: string) {
    try {
      localStorage.setItem(`game_save_corrupted_${Date.now()}`, raw)
    } catch {
      // 备份也失败，放弃
    }
  }

  // 版本迁移：逐版本升级
  private migrate(data: SaveData): SaveData {
    let current = data
    while (current.version < CURRENT_VERSION) {
      current = this.applyMigration(current)
    }
    return current
  }

  private applyMigration(data: SaveData): SaveData {
    switch (data.version) {
      case 1:
        // v1 → v2：新增 achievements 字段
        return {
          ...data,
          version: 2,
          meta: {
            ...data.meta,
            achievements: data.meta.achievements ?? [],
          },
        }
      default:
        return data
    }
  }
}
```

## IndexedDB 实现

适合大存档（> 1MB）或需存二进制资源：

```typescript
const DB_NAME = 'game_db'
const DB_VERSION = 1
const STORE_NAME = 'saves'

class IndexedDBSaveManager {
  private db: IDBDatabase | null = null

  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(DB_NAME, DB_VERSION)
      req.onupgradeneeded = () => {
        const db = req.result
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME, { keyPath: 'id' })
        }
      }
      req.onsuccess = () => { this.db = req.result; resolve() }
      req.onerror = () => reject(req.error)
    })
  }

  async save(id: string, data: SaveData): Promise<void> {
    if (!this.db) throw new Error('DB not initialized')
    return new Promise((resolve, reject) => {
      const tx = this.db!.transaction(STORE_NAME, 'readwrite')
      const store = tx.objectStore(STORE_NAME)
      const record = { id, data, updatedAt: Date.now() }
      const req = store.put(record)
      req.onsuccess = () => resolve()
      req.onerror = () => reject(req.error)
    })
  }

  async load(id: string): Promise<SaveData | null> {
    if (!this.db) throw new Error('DB not initialized')
    return new Promise((resolve, reject) => {
      const tx = this.db!.transaction(STORE_NAME, 'readonly')
      const store = tx.objectStore(STORE_NAME)
      const req = store.get(id)
      req.onsuccess = () => resolve(req.result?.data ?? null)
      req.onerror = () => reject(req.error)
    })
  }

  async list(): Promise<string[]> {
    if (!this.db) throw new Error('DB not initialized')
    return new Promise((resolve, reject) => {
      const tx = this.db!.transaction(STORE_NAME, 'readonly')
      const store = tx.objectStore(STORE_NAME)
      const req = store.getAllKeys()
      req.onsuccess = () => resolve(req.result as string[])
      req.onerror = () => reject(req.error)
    })
  }

  async delete(id: string): Promise<void> {
    if (!this.db) throw new Error('DB not initialized')
    return new Promise((resolve, reject) => {
      const tx = this.db!.transaction(STORE_NAME, 'readwrite')
      const req = tx.objectStore(STORE_NAME).delete(id)
      req.onsuccess = () => resolve()
      req.onerror = () => reject(req.error)
    })
  }
}
```

## 自动保存模式

```typescript
class AutoSave {
  private saveManager: SaveManager
  private dirty = false
  private timer: number | null = null
  private readonly interval = 30000  // 30 秒自动保存

  constructor(saveManager: SaveManager) {
    this.saveManager = saveManager
  }

  // 数据变更时标记为脏
  markDirty() {
    this.dirty = true
  }

  start() {
    if (this.timer) return
    this.timer = window.setInterval(() => {
      if (this.dirty) this.saveNow()
    }, this.interval)
  }

  stop() {
    if (this.timer) {
      clearInterval(this.timer)
      this.timer = null
    }
  }

  saveNow(): boolean {
    const data = collectSaveData()
    const ok = this.saveManager.save(data)
    if (ok) this.dirty = false
    return ok
  }
}

// 关键时机自动保存
window.addEventListener('beforeunload', () => autoSave.saveNow())
document.addEventListener('visibilitychange', () => {
  if (document.hidden) autoSave.saveNow()
})
```

## 防作弊（可选）

本地存档可被玩家修改，关键数据需服务端校验。无服务端时可加签名：

```typescript
class SignedSaveManager extends SaveManager {
  constructor(private secret: string) {
    super()
  }

  private sign(data: string): string {
    // 简单签名：SHA-256(data + secret)
    // 注意：客户端 secret 可被逆向，仅防普通玩家
    return sha256(data + this.secret)
  }

  save(data: SaveData): boolean {
    const json = JSON.stringify(data)
    const signature = this.sign(json)
    const payload = { data: json, sig: signature }
    try {
      localStorage.setItem(SAVE_KEY, JSON.stringify(payload))
      return true
    } catch {
      return false
    }
  }

  load(): SaveData | null {
    const raw = localStorage.getItem(SAVE_KEY)
    if (!raw) return null
    try {
      const payload = JSON.parse(raw)
      if (this.sign(payload.data) !== payload.sig) {
        console.warn('存档签名校验失败，可能被篡改')
        return null
      }
      return this.migrate(JSON.parse(payload.data))
    } catch {
      return null
    }
  }
}
```

**安全边界：**
- 客户端签名仅防普通玩家，专业破解者可逆向
- 排行榜/竞技场景必须服务端校验
- 单机游戏可接受客户端存档，作弊只影响自己
