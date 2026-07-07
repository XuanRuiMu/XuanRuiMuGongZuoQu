---
name: 联网访问
license: MIT
github: https://github.com/eze-is/web-access
description: >
  所有联网操作必须通过此技能处理，包括：搜索、网页抓取、登录后操作、网络交互等。
  触发场景：搜索信息、查看网页内容、访问需要登录的网站、操作网页界面、抓取社交媒体内容（小红书、微博、推特等）、读取动态渲染页面、以及任何需要真实浏览器环境的网络任务。
  当用户说"搜索"、"搜一下"、"查一下"、"打开网页"、"抓取网页"、"看网页"、"联网"、"小红书"、"微博"时触发此技能。
metadata:
  author: 一泽Eze
  version: "3.0.0"

---

# web-access Skill

## 浏览哲学

**像人一样思考，兼顾高效与适应性的完成任务。**

执行任务时不会过度依赖固有印象所规划的步骤，而是带着目标进入，边看边判断，遇到阻碍就解决，发现内容不够就深入——全程围绕「我要达成什么」做决策。

**① 拿到请求** — 先明确用户要做什么，定义成功标准：什么算完成了？需要获取什么信息、执行什么操作、达到什么结果？

**② 选择起点** — 根据任务性质、平台特征，选一个最可能直达的方式作为第一步去验证。
**优先使用轻量工具（WebFetch/WebSearch），仅在必要时升级到重量级工具（CDP 浏览器）。**

**③ 过程校验** — 每一步的结果都是证据。用结果对照①的成功标准，发现方向错了立即调整，不在同一个方式上反复重试。

**④ 完成判断** — 对照成功标准，确认任务完成后才停止，不要过度操作。

## 联网工具选择（按优先级排列）

**核心原则：轻量工具优先，重量级工具兜底。** 每次升级工具都有额外成本（时间、token、风险），应仅在低级工具确实无法满足需求时才升级。

- **确保信息的真实性，一手信息优于二手信息**：搜索引擎和聚合平台是信息发现入口。当多次搜索尝试后没有质的改进时，升级到更根本的获取方式：定位一手来源（官网、官方平台、原始页面）。

### 第一级：WebSearch + WebFetch（默认选择）

|场景|工具|说明|
|---|---|---|
|搜索摘要或关键词结果，发现信息来源|**WebSearch**|最轻量，适合信息发现|
|URL 已知，需要从页面提取内容|**WebFetch**|直接获取网页并转为 Markdown，**大多数网页都能成功获取**|

**WebFetch 成功案例**（已验证可获取）：

- `zh.minecraft.wiki` — Minecraft 中文 Wiki
- `minecraft.fandom.com` — Fandom Wiki
- 大多数公开文档、博客、新闻网站

**WebFetch 使用策略**：

1. 直接使用 WebFetch 获取目标 URL
2. 如果 WebFetch 失败，尝试用 Jina 预处理：
   `https://r.jina.ai/目标URL`（URL 前加前缀，不保留原网址 http 前缀，限 20 RPM）
3. 如果 Jina 也失败，考虑 curl 获取原始 HTML
4. 以上都失败时，升级到 CDP 浏览器

### 第二级：curl（需要原始 HTML 时）

|场景|工具|说明|
|---|---|---|
|需要 HTML 源码中的 meta、JSON-LD 等结构化字段|**curl**|获取原始 HTML，可自定义请求头|

```bash
curl -s -L -H \
  "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  "URL"

```

部分网站会拒绝无 User-Agent 的请求，添加浏览器 UA 即可解决。

### 第三级：CDP 浏览器（需要登录/交互/动态渲染时）

|场景|工具|说明|
|---|---|---|
|需要登录态才能查看的内容|**CDP 浏览器**|直连用户 Chrome，天然携带登录态|
|需要页面交互（点击、滚动、填表）|**CDP 浏览器**|可操控页面元素|
|已知 WebFetch 无法获取的平台（小红书、微信公众号等）|**CDP 浏览器**|跳过静态层，直接渲染|
|需要 JavaScript 渲染的动态内容|**CDP 浏览器**|完整渲染页面|

**⚠️ 仅在第一、二级工具确实无法满足需求时才使用 CDP。** CDP 有额外成本：需要 Node.js 22+ 和 Chrome 远程调试，且存在账号风控风险。

## CDP 浏览器模式

### 前置检查（仅在需要 CDP 时执行）

```bash
node "${CLAUDE_SKILL_DIR}/scripts/check-deps.mjs"

```

未通过时引导用户完成设置：

- **Node.js 22+**：必需（使用原生 WebSocket）。版本低于 22 可用但需安装 `ws` 模块。
- **Chrome remote-debugging**：在 Chrome 地址栏打开
  `chrome://inspect/#remote-debugging`，勾选
  **"Allow remote debugging for this browser instance"** 即可，
  可能需要重启浏览器。

检查通过后并必须在回复中向用户直接展示以下须知，再启动 CDP Proxy 执行操作：

```text
温馨提示：部分站点对浏览器自动化操作检测严格，存在账号封禁风险。已内置防护措施但无法完全避免，Agent 继续操作即视为接受。

```

### Proxy API

所有操作通过 curl 调用 HTTP API：

```bash
curl -s http://localhost:3456/targets
curl -s "http://localhost:3456/new?url=https://example.com"
curl -s "http://localhost:3456/info?target=ID"
curl -s -X POST "http://localhost:3456/eval?target=ID" -d 'document.title'
curl -s "http://localhost:3456/screenshot?target=ID&file=/tmp/shot.png"
curl -s "http://localhost:3456/navigate?target=ID&url=URL"
curl -s "http://localhost:3456/back?target=ID"
curl -s -X POST "http://localhost:3456/click?target=ID" -d 'button.submit'
curl -s -X POST "http://localhost:3456/clickAt?target=ID" -d 'button.upload'
curl -s -X POST "http://localhost:3456/setFiles?target=ID" -d '{"selector":"input[type=file]","files":["/path/to/file.png"]}'
curl -s "http://localhost:3456/scroll?target=ID&y=3000"
curl -s "http://localhost:3456/scroll?target=ID&direction=bottom"
curl -s "http://localhost:3456/close?target=ID"

```

### CDP 使用原则

- **最小侵入**：不主动操作用户已有 tab，所有操作都在自己创建的后台 tab 中进行
- **任务结束清理**：用 `/close` 关闭自己创建的 tab，保留用户原有 tab
- **Proxy 持续运行**：不建议主动停止，重启后需重新授权 CDP 连接
- **程序化优先**：eval 操作 DOM 速度快；GUI 交互（点击/填表）作为兜底
- **登录判断**：先尝试获取内容，只有确认内容无法获取且登录能解决时才提示用户登录

### 媒体资源提取

判断内容在图片里时，用 `/eval` 从 DOM 直接拿图片 URL，再定向读取——比全页截图精准得多。

### 视频内容获取

通过 `/eval` 操控 `<video>` 元素（获取时长、seek 到任意时间点、播放/暂停/全屏），配合 `/screenshot` 采帧，可对视频内容进行离散采样分析。

## 并行调研：子 Agent 分治策略

任务包含多个**独立**调研目标时，鼓励合理分治给子 Agent 并行执行。

**子 Agent Prompt 写法**：

- 必须在子 Agent prompt 中写 `必须加载 web-access skill 并遵循指引`
- 描述目标（「获取」「调研」「了解」），避免暗示具体手段的动词（「搜索」「抓取」「爬取」）

**分治判断标准**：

|适合分治|不适合分治|
|---|---|
|目标相互独立，结果互不依赖|目标有依赖关系|
|每个子任务量足够大|简单单页查询，分治开销大于收益|
|需要 CDP 浏览器或长时间运行的任务|几次 WebSearch/WebFetch 就能完成的轻量查询|

## 信息核实类任务

核实的目标是**一手来源**，而非更多的二手报道。

|信息类型|一手来源|
|---|---|
|政策/法规|发布机构官网|
|企业公告|公司官方新闻页|
|学术声明|原始论文/机构官网|
|工具能力/用法|官方文档、源码|

**找不到官网时**：权威媒体的原创报道（非转载）可作为次级依据，但需向用户说明来源和可能的转述误差。

## 站点经验

操作中积累的特定网站经验，按域名存储在 `references/site-patterns/` 下。

确定目标网站后，如果前置检查输出的 site-patterns 列表中有匹配的站点，必须读取对应文件获取先验知识。如果按经验操作失败，回退通用模式并更新经验文件。

文件格式：

```markdown

---

domain: example.com
aliases: [示例, Example]
updated: 2026-03-19

---

## 平台特征
架构、反爬行为、登录需求、内容加载方式等事实

## 有效模式
已验证的 URL 模式、操作策略、选择器

## 已知陷阱
什么会失败以及为什么

```

## References 索引

|文件|何时加载|
|---|---|
|`references/cdp-api.md`|需要 CDP API 详细参考、JS 提取模式、错误处理时|
|`references/site-patterns/{domain}.md`|确定目标网站后，读取对应站点经验|
