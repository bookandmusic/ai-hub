# 资源规划模板

## 视觉资源

### 资源清单

| 资源类型 | 格式 | 最大尺寸 | 数量预估 | 备注 |
|---------|------|---------|---------|------|
| 页面背景图 | WebP | 200KB | 1-3 | 首屏加载优化 |
| 角色/元素图 | WebP/PNG | 50KB/个 | 5-20 | 使用 Sprite Sheet 合并 |
| HUD 元素 | SVG/PNG | 10KB/个 | 10-30 | 优先 SVG 以支持缩放 |
| 按钮/图标 | SVG | 5KB/个 | 5-15 | 保持交互状态（normal/hover/active） |
| 特效/动画帧 | WebP/Canvas | 100KB/组 | 3-10 | 考虑 CSS Animation 替代方案 |
| 过渡动画 | CSS/Canvas | — | 2-5 | 优先 CSS transitions |
| 字体 | WOFF2 | 50KB/种 | 1-3 | 仅包含用到的字符子集 |

### Sprite Sheet（纹理图集）

- 将多个小图合并为一张大图，减少 HTTP 请求和 GPU 状态切换
- 建议最大尺寸 1024x1024（移动端兼容）
- 使用工具：TexturePacker、Shoebox、Free Texture Packer
- 每帧通过 Canvas drawImage(src, sx, sy, sw, sh) 从图集中裁剪（CSS background-position 仅适用于 CSS Sprite，不适用于 Canvas/WebGL 渲染）

### 动画资源

| 格式 | 适用场景 | 大小参考 | 兼容性 |
|------|---------|---------|--------|
| CSS Animation/Transition | 简单 UI 动效 | 0（纯代码） | 全平台 |
| Sprite Sheet 逐帧动画 | 像素风/2D角色动画 | 50-200KB/角色 | 全平台 |
| Lottie (JSON) | 矢量 UI 动效 | 10-50KB/个 | 需 Lottie 库 |
| Rive (.riv) | 交互式动画/状态机 | 30-100KB/个 | 需 Rive Runtime |
| Spine JSON | 骨骼动画（2D 角色） | 20-80KB/个 + 纹理 | 需 Spine Runtime |

- 优先使用 Sprite Sheet 或 CSS 动画以降低第三方依赖
- Lottie/Rive/Spine 适合复杂角色动画，但需评估库体积（通常 50-200KB gzip）

### 命名规范

```
{类型}_{名称}_{状态}_{尺寸}.[ext]
示例：
bg_menu_1920.webp
char_player_idle_64.png
btn_start_hover.svg
```

### 加载策略

- **关键路径资源**: 内联或 preload（背景、角色、核心 UI）
- **按需加载**: 关卡资源在进入关卡时加载
- **预加载**: 下一关资源在玩家通关时开始预加载
- **降级**: 网络慢时使用低分辨率占位图

## 音频资源

### 资源清单

| 资源类型 | 格式 | 最大时长 | 最大大小 | 备注 |
|---------|------|---------|---------|------|
| 背景音乐 (BGM) | MP3/OGG | 180s | 1MB | 可循环，准备渐进式淡入淡出 |
| 音效 (SFX) | MP3/OGG | 3s | 30KB/个 | 即时触发，低延迟要求 |
| 语音 | MP3 | 10s | 50KB/个 | 可选，按需加载 |

### 音频命名规范

```
{类型}_{场景}_{动作}.[ext]
示例：
bgm_level1_loop.mp3
sfx_jump_01.mp3
sfx_hit_player.mp3
```

### 加载策略

- BGM: 场景加载时开始预加载，使用 AudioBuffer 解码
- SFX: 游戏初始化时批量加载，常驻内存
- 语音: 按需加载，使用后释放

### 音频格式兼容性

| 格式 | Chrome | Firefox | Safari (macOS) | Safari (iOS) | 说明 |
|------|--------|---------|---------------|-------------|------|
| MP3 | ✅ | ✅ | ✅ | ✅ | 通用格式，首选 |
| OGG Vorbis | ✅ | ✅ | ❌ | ❌ | 桌面开源首选 |
| AAC (M4A) | ✅ | ✅ | ✅ | ✅ | iOS 原生格式 |
| WAV | ✅ | ✅ | ✅ | ✅ | 体积大，不适合长时间音频 |

- 推荐方案：MP3 作为主格式，桌面端对 OGG 做 `<source>` fallback
- 使用 `AudioContext.decodeAudioData()` 解码，而非 `<audio>` 标签播放

## 字体资源

| 类型 | 格式 | 大小 | 备注 |
|------|------|------|------|
| UI 字体 | WOFF2 | < 30KB | 仅数字+字母+常用标点 |
| 游戏内字体 | WOFF2 | < 50KB | 包含游戏内特有字符 |
| 中文字体 | WOFF2 | 按需 | 仅包含用到的汉字子集（中文游戏） |

- 使用 `unicode-range` 限制字符子集，大幅减少体积
- 使用 `font-display: swap` 避免 FOIT（Flash of Invisible Text）
- 考虑系统字体回退方案，减少字体加载依赖

## 资源目录结构

```
assets/
  images/
    backgrounds/
    characters/
    hud/
    effects/
    spritesheets/
  audio/
    bgm/
    sfx/
    voices/
  fonts/
```

## 体积预算

| 阶段 | 总预算 | 首屏 | 备注 |
|------|-------|------|------|
| 初始加载 | < 500KB | < 200KB | 含核心资源和骨架屏 |
| 每关加载 | < 300KB | — | 按需加载 |
| 总游戏 | < 3MB | — | 含所有资源和代码 |