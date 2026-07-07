# M05 3D 与 WebGL

> 本模块聚焦展示型网页中的三维与 WebGL 技术。不涉及 React/Next.js 集成细节（见 M07）、CSS 动画（见 M04）、2D
> Canvas 生成艺术（见 M06）或设计 token（见 M02）。

---

## 1. 触发时机

在以下场景激活本模块：

- 需要全屏/英雄区 3D 背景（粒子场、流体、点阵、星云等）。
- 需要在页面中嵌入可交互 3D 物体（产品展示、建筑/角色预览、数据可视化）。
- 需要基于 shader 的定制视觉效果（等高线、色散、扭曲、后期处理）。
- 用户提到 Three.js、WebGL、GLSL、shader、粒子系统、流体模拟、3D 模型展示。
- 项目要求零依赖/单文件 HTML 演示，但需要 3D 氛围背景。

不适用本模块：

- 纯 CSS 3D transform 效果 → M04。
- 2D canvas 绘制或 p5.js 生成艺术 → M06。
- 3D 内容需要复杂 React 状态管理或 SSR → M07。

## 1.1 集成到现有页面

当本模块用于为 M03/M04 等模块已生成的页面添加 3D 背景或氛围层时，必须遵守：

- **作为独立层添加**：将 Three.js 画布容器以固定/绝对定位层插入页面，不改动现有内容 DOM 结构。
- **不修改现有 class**：原有布局、栅格、字体、颜色类保持不动；3D 层通过 z-index 控制叠加。
- **事件不冲突**：3D 层设置 `pointer-events: none`（除非需要交互），避免阻挡页面滚动、点击和表单操作。
- **提供关闭/降级**：通过按钮、`B` 键或 `prefers-reduced-motion` 停止 RAF 渲染，确保低端设备可阅读内容。

---

## 2. Three.js 展示页基础

### 2.1 核心对象与最小渲染循环

```js
import * as THREE from "three";

const 场景 = new THREE.Scene();
const 相机 = new THREE.PerspectiveCamera(75, 宽 / 高, 0.1, 1000);
const 渲染器 = new THREE.WebGLRenderer({ alpha: true, antialias: true });
渲染器.setSize(宽, 高);
渲染器.setPixelRatio(Math.min(window.devicePixelRatio, 2));
容器.appendChild(渲染器.domElement);

function 动画(时间) {
  requestAnimationFrame(动画);
  渲染器.render(场景, 相机);
}
动画();
```

展示页通常不需要完整游戏循环，但以下要素必须显式处理：

| 要素     | 说明                                                                        |
| -------- | --------------------------------------------------------------------------- |
| Scene    | 组织所有对象、灯光、相机。                                                  |
| Camera   | 一般使用 `PerspectiveCamera`；产品展示可考虑 `OrthographicCamera`。         |
| Renderer | 设置 `alpha: true` 以叠加 HTML 内容；限制 `pixelRatio` 上限防止移动端过载。 |
| Resize   | 监听 `resize` 更新 `camera.aspect` 与 `renderer.setSize`。                  |
| Dispose  | 页面卸载或背景销毁时释放 geometry/material/texture/WebGL context。          |

### 2.2 灯光与材质速查

- **环境光 + 定向光**是展示场景的最小可用组合，避免纯环境光导致模型扁平。
- **PBR 材质** (`MeshStandardMaterial`/`MeshPhysicalMaterial`) 需要至少一盏光才能正确显示。
- **自发光/单色材质** (`MeshBasicMaterial`) 适合粒子、UI 元素、霓虹效果，不受光照影响。
- **透明与深度写入**：透明粒子需设置 `transparent: true`、`depthWrite: false`，并按需开启
  `blending: THREE.AdditiveBlending`。

### 2.3 相机与轨道控制

- 产品展示：使用 `OrbitControls`，限制极角 `maxPolarAngle` 避免穿底，启用阻尼 `enableDamping = true`。
- 英雄背景：固定相机或缓慢程序运动，避免用户控制权。
- 相机初始位置与目标应服务于视觉焦点，而非默认朝向。

---

## 3. Shader 基础与使用时机

### 3.1 何时使用 Shader

| 场景                                 | 推荐方案                                         |
| ------------------------------------ | ------------------------------------------------ |
| 渐变/噪波/流体背景                   | 全屏 shader quad                                 |
| 物体表面特殊效果（全息、玻璃、扭曲） | 自定义 material shader                           |
| 后期处理（辉光、色差、模糊）         | EffectComposer + pass                            |
| 简单色彩/透明度变化                  | 优先用 Three.js 内置材质 + uniforms，不写 shader |

### 3.2 GLSL 最小结构

```glsl
// Vertex
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}

// Fragment
uniform float uTime;
uniform vec2 uResolution;
varying vec2 vUv;
void main() {
  vec2 uv = vUv;
  vec3 color = vec3(0.5 + 0.5 * sin(uTime + uv.xyx * 3.0));
  gl_FragColor = vec4(color, 1.0);
}
```

### 3.3 展示页 shader 规范

- **Uniform 命名**：统一使用 `uTime`、`uResolution`、`uMouse`、`uScroll` 等前缀，方便跨项目复用。
- **时间单位**：传入秒而非毫秒，避免在 shader 内做除法。
- **精度修饰**：移动端显式声明 `precision mediump float;`，高端桌面可 `highp`。
- **避免复杂分支**：GPU 不喜 `if` 分支，尽量用 `mix`、`step`、`smoothstep` 表达条件。
- **低功耗切换**：提供停止 uniform 更新的机制（如 `body.low-power` 类停止 `uTime` 递增）。

---

## 4. 粒子系统与流体模拟

### 4.1 粒子系统

- **Points + BufferGeometry** 是 Three.js 高性能粒子的标准方案。
- 每个粒子由 `position` 属性定义，额外属性可携带尺寸、颜色、生命周期等。
- 动画方式：
  - CPU 更新：每帧修改 `geometry.attributes.position.array`，适合少量粒子（< 5000）。
  - GPU 更新：在 vertex shader 中基于 `uTime` 计算位置，适合大量粒子（> 10000）。

```js
const 几何 = new THREE.BufferGeometry();
几何.setAttribute("position", new THREE.Float32BufferAttribute(位置数组, 3));
const 材质 = new THREE.PointsMaterial({
  size: 2,
  color: 0xffffff,
  transparent: true,
  opacity: 0.8,
  blending: THREE.AdditiveBlending,
  depthWrite: false,
});
const 粒子 = new THREE.Points(几何, 材质);
场景.add(粒子);
```

### 4.2 流体/点阵背景

- **流体背景**：全屏 quad + fragment shader 使用 Simplex/Perlin 噪波，配合时间 uniform 产生缓慢流动。
- **点阵背景**：大量小点配合 `gl_PointSize` 与鼠标距离计算，产生细微波动。
- 背景类 WebGL 应几乎不可见，避免抢夺前景内容注意力。
- 使用 `alpha: true` 让背景融入 CSS 背景色，而非全黑 canvas。

### 4.3 流体模拟边界

- 复杂流体（SPH、Navier-Stokes）超出展示页范围，如需物理正确模拟应评估是否适合 WebGL。
- 展示页流体以**视觉暗示**为主：噪波、拖尾、颜色流动、缓慢形变。
- 永远提供 `B` 键或类似低功耗开关，停止流体动画与 RAF。

---

## 5. WebGL 性能规则

### 5.1 几何与材质

- **合并几何**：大量静态物体使用 `BufferGeometryUtils.mergeGeometries` 减少 draw call。
- **实例化渲染**：重复对象（树木、星星、建筑单元）使用 `InstancedMesh`。
- **纹理尺寸**：使用 2 的幂次方尺寸，移动端限制在 2048x2048 以下。
- **压缩纹理**：必要时使用 KTX2/Basis 压缩减少显存占用。

### 5.2 动画与 Mixer

Three.js 动画系统三核心：

- **AnimationClip**：关键帧数据。
- **AnimationMixer**：管理 clip 播放，必须每帧调用 `mixer.update(delta)`。
- **AnimationAction**：控制播放、暂停、速度、权重、循环、淡入淡出。

优化规则：

- 共享 clip，调用 `clip.optimize()`。
- 离屏或不可见时暂停 mixer，避免空转。
- 限制同时活跃的 mixer 数量，通常不超过 3 个。
- 使用 `GLTFLoader` 加载 glTF 时，动画数组在 `gltf.animations` 中自动可用。

### 5.3 LOD 与可见性

- 对复杂模型启用 `THREE.LOD`，根据相机距离切换高/中/低模。
- 使用视锥剔除：`renderer.frustumCulled = true`（默认开启，不要误关）。
- 离屏 canvas 停止 `requestAnimationFrame`，避免后台标签页耗电。

### 5.4 Context 数量

- 单个页面同时活跃的 WebGL context 尽量不超过 1 个。
- 需要多个 canvas 时，优先共享同一个 renderer 的 render target，或顺序渲染。
- 销毁 context 前调用 `renderer.dispose()` 释放资源。

---

## 6. 与 HTML/CSS 页面集成

### 6.1 Canvas 尺寸与定位

- canvas 容器使用 `position: fixed; inset: 0; z-index: -1;` 作为全屏背景。
- 或使用 `position: relative; width: 100%; height: 100vh;` 作为英雄区元素。
- 通过 CSS `pointer-events: none` 让背景不阻挡点击；需要交互时给 canvas 容器加 `pointer-events: auto`。

### 6.2 z-index 与分层

- WebGL 背景：`z-index: -1` 或 `0`。
- 内容层：`z-index: 1` 以上，确保文本可读。
- 导航/浮层：按项目 z-index 体系放置，避免与 canvas 层级混乱。
- 不要给 WebGL canvas 设置任意高 `z-index`，除非确实需要覆盖 UI。

### 6.3 响应式

- 监听 `window resize` 更新 renderer 尺寸与相机比例。
- 移动端降低粒子数量、纹理尺寸、pixel ratio。
- 窄屏上避免需要精细鼠标交互的 3D 对象，改用触控友好的旋转幅度。

### 6.4 与 CSS 变量联动

- 可通过 JavaScript 读取 CSS 变量并传入 shader uniform，使 3D 背景与页面主题色一致。
- 示例：`getComputedStyle(document.documentElement).getPropertyValue('--accent')`。
- 不要在 shader 内硬编码品牌色。

---

## 7. 常见模式

### 7.1 Hero 背景

- 用途： landing page、演示文稿封面。
- 实现：全屏 shader quad 或粒子场 + 前景排版。
- 规则：动画速度缓慢、颜色克制、不干扰阅读。
- 示例：流体噪波、缓慢旋转点阵、星云尘埃。

### 7.2 交互式 3D 物体

- 用途：产品展示、角色/建筑预览、数据 artifact。
- 实现：`OrbitControls` + 模型加载 + 可选热点标注。
- 规则：
  - 标注使用 HTML 覆盖，不渲染在 3D 内。
  - 加载时显示骨架或占位模型。
  - 鼠标悬停提供微反馈（缩放、高亮）。

### 7.3 粒子场

- 用途：科技感背景、节日氛围、数据可视化氛围。
- 实现：`Points` + `BufferGeometry`，vertex shader 驱动运动。
- 规则：
  - 粒子数量按设备性能分级（桌面 20000，中端移动 5000，低端 1000）。
  - 使用 `AdditiveBlending` 时注意亮度叠加导致过曝。

### 7.4 后期处理辉光

- 用途：霓虹、能量、科幻主题。
- 实现：`EffectComposer` + `UnrealBloomPass`。
- 规则：强度克制，避免大面积泛白；移动端慎用。

---

## 8. 加载与降级策略

### 8.1 加载状态

- 3D 资源加载期间显示进度指示或品牌占位。
- 使用 `LoadingManager` 统一追踪纹理、模型、字体资源。
- 大型 glTF 使用 Draco/KTX2 压缩并开启 CDN/分块加载。

### 8.2 WebGL 不可用降级

```js
const canvas = document.createElement("canvas");
const gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
if (!gl) {
  // 降级为静态 CSS 背景或低帧动画
}
```

- WebGL 不支持时：使用 CSS 渐变、静态图片、CSS 动画替代。
- `prefers-reduced-motion` 为 reduce 时：停止 RAF、禁用自动旋转、使用静态帧。
- 低功耗模式：提供显式开关（如 `B` 键），停止 WebGL 动画与 Motion 入场。

### 8.3 性能降级阶梯

| 等级 | 条件            | 措施                                                |
| ---- | --------------- | --------------------------------------------------- |
| 高端 | 桌面/高性能 GPU | 全效 shader、高粒子数、后期处理。                   |
| 中端 | 普通笔记本/平板 | 降低 particle count、关闭 bloom、限制 pixel ratio。 |
| 低端 | 旧手机/低电量   | 停止动画，显示静态最后一帧或 CSS 背景。             |

### 8.4 资源清理

页面切换或组件销毁时：

```js
window.removeEventListener("resize", 调整大小);
cancelAnimationFrame(动画ID);
mixer?.stopAllAction();
几何?.dispose();
材质?.dispose();
纹理?.dispose();
渲染器?.dispose();
```

---

## 9. 模块边界速查

| 主题                                                        | 归属模块       |
| ----------------------------------------------------------- | -------------- |
| CSS 动画、transition、keyframes、UI 层面页面/组件动效       | M04 动效与交互 |
| 3D 场景内部动画（相机移动、模型旋转、粒子、射线交互反馈）   | 本模块 M05     |
| 2D Canvas、p5.js、生成艺术                                  | M06 生成艺术   |
| 设计系统、颜色 token、排版                                  | M02 设计系统   |
| React/Next.js、组件集成、SSR                                | M07 组件与框架 |
| Three.js 展示页基础、shader、粒子、性能                     | 本模块 M05     |
