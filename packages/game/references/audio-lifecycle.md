# Web 音频生命周期

## AudioContext 管理

### 创建时机

```typescript
// Safari 兼容：webkitAudioContext
const AC = window.AudioContext || (window as any).webkitAudioContext

let audioCtx: AudioContext | null = null
let masterGain: GainNode | null = null
let bgmGain: GainNode | null = null
let sfxGain: GainNode | null = null

// 在用户首次交互（click/touch）时创建，满足 autoplay policy
function initAudio() {
  if (audioCtx && audioCtx.state !== 'closed') return
  audioCtx = new AC()
  masterGain = audioCtx.createGain()
  masterGain.connect(audioCtx.destination)
  bgmGain = audioCtx.createGain()
  bgmGain.connect(masterGain)
  sfxGain = audioCtx.createGain()
  sfxGain.connect(masterGain)
}
```

### 状态管理

| 状态 | 含义 | 处理 |
|------|------|------|
| running | 正常播放 | 正常工作 |
| suspended | 被浏览器暂停 | 调用 `audioCtx.resume()` |
| closed | 已关闭 | 重新创建 |

### 页面可见性

```typescript
const audioAbortController = new AbortController()

document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    audioCtx?.suspend()
  } else {
    audioCtx?.resume()
  }
}, { signal: audioAbortController.signal })

// 清理时调用 audioAbortController.abort()
```

## 音频加载

### 预加载策略

```typescript
async function loadAudio(url: string): Promise<AudioBuffer> {
  const response = await fetch(url)
  const arrayBuffer = await response.arrayBuffer()

  // Safari <15 使用 callback 版 decodeAudioData，优先尝试 Promise 版
  if (audioCtx!.decodeAudioData.length === 1) {
    return await audioCtx!.decodeAudioData(arrayBuffer)
  }
  // Safari callback fallback
  return new Promise((resolve, reject) => {
    audioCtx!.decodeAudioData(arrayBuffer, resolve, reject)
  })
}

// 初始化时批量加载核心 SFX
async function loadCoreSFX() {
  const SFX_FILES = ['sfx_jump', 'sfx_hit', 'sfx_coin']
  await Promise.all(SFX_FILES.map(name => loadAudio(`/audio/sfx/${name}.mp3`)))
}
```

### 错误处理

- 加载失败 → 静默降级（不阻塞游戏启动）
- 解码失败 → 跳过该音频，不抛异常
- 记录失败日志用于调试

## 播放与停止

### BGM（单实例，循环）

```typescript
let bgmSource: AudioBufferSourceNode | null = null

function playBGM(buffer: AudioBuffer) {
  stopBGM()
  bgmSource = audioCtx!.createBufferSource()
  bgmSource.buffer = buffer
  bgmSource.loop = true
  bgmSource.connect(bgmGain!)
  bgmSource.start()
}

function stopBGM() {
  if (!bgmSource) return
  try {
    bgmSource.stop()
  } catch {
    // 节点已自然播放结束，忽略 InvalidStateNode 错误
  }
  bgmSource.disconnect()
  bgmSource = null
}
```

### SFX（多实例，重叠播放）

```typescript
function playSFX(buffer: AudioBuffer, volume = 1) {
  const source = audioCtx!.createBufferSource()
  const gain = audioCtx!.createGain()
  source.buffer = buffer
  gain.gain.value = volume
  source.connect(gain)
  gain.connect(sfxGain!)
  source.start()
  // 播放结束后自动清理
  source.onended = () => {
    source.disconnect()
    gain.disconnect()
  }
}
```

## 音量控制

```typescript
function setMasterVolume(v: number) {
  masterGain!.gain.value = v
  localStorage.setItem('game_volume', String(v))
}

// 分别控制
function setBGMVolume(v: number) {
  bgmGain!.gain.value = v
}

function setSFXVolume(v: number) {
  sfxGain!.gain.value = v
}
```

## 音频可视化（AnalyserNode）

```typescript
function createAudioVisualizer() {
  const analyser = audioCtx!.createAnalyser()
  analyser.fftSize = 256
  // 将 analyser 插入音频链：source → analyser → destination
  // source.connect(analyser)
  // analyser.connect(audioCtx!.destination)

  const dataArray = new Uint8Array(analyser.frequencyBinCount)

  function drawVisualizer(canvas: HTMLCanvasElement) {
    const ctx = canvas.getContext('2d')!
    analyser.getByteFrequencyData(dataArray)
    // 使用 dataArray 绘制频谱
    requestAnimationFrame(() => drawVisualizer(canvas))
  }

  return { analyser, drawVisualizer }
}
```

## 资源释放

- 场景切换时：停止所有 BGM，释放当前场景的 AudioBuffer 引用（从 Map 中 delete）
- 游戏结束：关闭 AudioContext（`audioCtx.close()`），audioCtx 置 null
- 不再使用的 SFX 从 Map 中 `delete` 以便 GC 回收

## 浏览器兼容

| API | Chrome | Firefox | Safari | 备注 |
|-----|--------|---------|--------|------|
| AudioContext | ✅ | ✅ | ✅ | Safari 需前缀 `webkitAudioContext` |
| decodeAudioData | ✅ | ✅ | ✅ | Safari 使用 callback 版本 |
| AudioBufferSourceNode | ✅ | ✅ | ✅ | 全兼容 |
| GainNode | ✅ | ✅ | ✅ | 全兼容 |
| AnalyserNode | ✅ | ✅ | ✅ | 全兼容 |