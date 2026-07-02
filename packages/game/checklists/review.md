# 游戏代码审查清单

## State（状态管理）

- [ ] 状态机定义清晰，每个状态职责单一
- [ ] 状态转换图/表已记录，所有路径可达
- [ ] 状态转换时正确清理旧状态资源（定时器、事件监听）
- [ ] 游戏状态与 UI 状态分离（游戏逻辑不直接操作 DOM）
- [ ] 状态持久化方案明确（localStorage / IndexedDB / 无持久化）
- [ ] 存档/读档流程覆盖边界条件（空存档、损坏数据、版本迁移）
- [ ] 状态更新在 requestAnimationFrame 或固定 tick 中进行

## Input（输入系统）

- [ ] 触摸屏：支持 touchstart/touchmove/touchend，处理多点触控
- [ ] 触摸事件中正确调用 preventDefault 阻止页面滚动
- [ ] 鼠标：支持 mousedown/mousemove/mouseup、click、右击菜单处理
- [ ] 键盘：支持 keydown/keyup，处理组合键不冲突
- [ ] 输入映射可配置（允许玩家自定义按键）
- [ ] 输入状态每帧正确重置（防止粘滞键）
- [ ] 游戏失焦（blur/visibilitychange）时自动暂停并重置输入状态

## Audio（音频生命周期）

- [ ] AudioContext 在用户首次交互后创建（autoplay policy）
- [ ] 音频资源加载失败有 fallback（静默降级/重试）
- [ ] BGM 循环无缝衔接（loop 属性 / 手动拼接）
- [ ] SFX 支持多实例重叠播放（同一种音效可以同时播放多次）
- [ ] 页面可见性变化时正确暂停/恢复音频
- [ ] 音频资源在不再使用时释放内存（AudioBuffer 解引用）
- [ ] 音量设置跨页面持久化

## Render（渲染系统）

- [ ] Canvas/WebGL 纹理不再使用时释放（dispose / deleteTexture）
- [ ] WebGL 上下文丢失时正确处理（context lost / restored 事件）
- [ ] 每帧最多调用一次 clearRect / clear，避免无效重绘
- [ ] Canvas 尺寸适配 devicePixelRatio，避免模糊
- [ ] 离屏渲染使用 OffscreenCanvas（Web Worker 可选）
- [ ] 动画帧使用 requestAnimationFrame，有 setTimeout fallback

## Mobile（移动端适配）

- [ ] viewport meta 标签正确设置（width=device-width, user-scalable=no）
- [ ] Canvas 尺寸适配设备像素比（devicePixelRatio）
- [ ] 交互热区不小于 44x44px（Apple HIG 最小触控区域）
- [ ] 横竖屏切换时正确重排/重绘
- [ ] 移动端性能满足 30fps 最低要求
- [ ] 省电模式/低电量下降低帧率或特效
- [ ] 测试覆盖 iOS Safari 和 Android Chrome

## WebGPU（如果使用）

- [ ] `navigator.gpu` 存在性检查，缺失时回退到 WebGL/Canvas 2D
- [ ] 适配器 (adapter) 请求设置 `powerPreference: 'high-performance'`
- [ ] 设备丢失 (device lost) 事件处理：暂停渲染，尝试恢复
- [ ] 着色器编译错误捕获，不阻塞主线程
- [ ] 纹理/缓冲区在不再使用时调用 `destroy()`
- [ ] 验证（validation error）处理：开发环境启用，生产环境禁用
- [ ] 不在 Safari/iOS 上默认启用 WebGPU（截至 2026 年支持仍有限）

## Security（安全）

- [ ] 本地存储数据验证完整性（不信任客户端，关键数据由服务端校验）
- [ ] 排行榜/高分提交做频率限制和签名验证
- [ ] 无 XSS 风险（不使用 innerHTML 渲染用户输入）
- [ ] 外部资源（图片、音频）使用 HTTPS 加载

## Accessibility（无障碍）

- [ ] 提供音效开关选项（癫痫警告）
- [ ] 动画可关闭（prefers-reduced-motion）
- [ ] 颜色对比度满足 WCAG AA（如果含文字）
- [ ] 键盘可完全操作（如果适用）
- [ ] 色盲模式：不使用仅靠颜色区分敌我/状态（同时使用图标/形状/文字）
- [ ] 色盲模式：提供高对比度方案或色盲滤镜

## Code Quality

- [ ] 无魔法数字，所有游戏常量集中管理
- [ ] 碰撞检测使用空间索引（四叉树/网格）优化
- [ ] 对象池管理频繁创建/销毁的游戏对象（子弹、粒子）
- [ ] requestAnimationFrame 回退方案（setTimeout fallback）
- [ ] 无内存泄漏（全局变量、未清理的 event listener）
- [ ] 游戏循环使用固定时间步长（fixed timestep）
- [ ] 游戏主循环有明确的 Update / Render 分离
- [ ] 循环包含 maxFrameTime 上限保护，防止 spiral of death