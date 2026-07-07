# M08 AI 集成

> 本模块聚焦前端 AI 功能的集成模式：Vercel AI
> SDK、流式聊天 UI、工具调用、结构化输出、服务端集成、安全与限流。不包含 React/Next.js 基础（见 M07）、设计 token（M02）、通用 UI 实现（M03）、动画细节（M04）。

---

## 1. 触发时机

在以下场景激活本模块：

- 需要实现 AI 聊天、问答、Copilot 面板、智能助手界面。
- 需要流式显示大模型返回内容（逐字输出、打字机效果）。
- 需要模型调用外部工具（查询天气、检索知识库、执行计算等）并在 UI 中反馈。
- 需要模型返回结构化数据（JSON、表格、表单、枚举分类）。
- 用户提到 Vercel AI SDK、useChat、LangChain、LangGraph、工具调用、Function Calling、streaming。
- 需要决定 AI 调用放服务端还是客户端、如何保护 API Key、如何做限流。

不适用本模块：

- React 组件基础、Next.js 路由/SSR → M07。
- 视觉设计、配色、排版 → M02 / M03。
- 复杂动画、入场动效 → M04。
- 纯后端模型训练/部署 → 不在「前端炫技实验室」范围。

### 1.1 前置条件

本模块示例默认基于 React 19 + Next.js App Router。若项目尚未具备以下基础，需先进入 [M07 组件与框架](M07-组件与框架.md) 完成环境搭建：

- React 组件与 hooks 基础
- Next.js App Router 项目结构
- Server Actions / API Route 基础
- 环境变量与依赖管理

若项目为纯 HTML/Tailwind 静态页面，AI 集成需通过客户端直接调用 API，此时安全与限流策略需另行设计（不建议在生产环境直接使用客户端 API Key）。

---

## 2. Vercel AI SDK 基础

### 2.1 安装与 Provider 配置

```bash
npm install ai @ai-sdk/openai zod
# 多厂商场景可同时安装 @ai-sdk/anthropic @ai-sdk/google 等
```

环境变量仅用于服务端：

```bash
# .env.local
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-xxx
```

Provider 初始化：

```ts
import { openai } from "@ai-sdk/openai";
import { anthropic } from "@ai-sdk/anthropic";

// 模型字符串决定具体模型与参数
const 模型 = openai("gpt-4o");
```

### 2.2 核心调用模式

| 模式     | API                                    | 用途                   | 返回值           |
| -------- | -------------------------------------- | ---------------------- | ---------------- |
| 同步文本 | `generateText`                         | 短问答、一次性生成     | 完整字符串与用量 |
| 流式文本 | `streamText`                           | 聊天、长文本、逐字显示 | 可转为数据流响应 |
| 同步对象 | `generateText` + `Output.object` (v6+) | 结构化输出             | 类型安全对象     |
| 流式对象 | `streamText` + `Output.object` (v6+)   | 渐进式 JSON            | 部分对象流       |

基础示例：

```ts
import { generateText, streamText } from "ai";

// 同步
const { text } = await generateText({ model: 模型, prompt: "简述边缘计算" });

// 流式（服务端返回给前端）
const result = streamText({
  model: 模型,
  messages: [{ role: "user", content: "写一个登录页文案" }],
});
return result.toDataStreamResponse();
```

> AI SDK 6 起推荐使用 `Output` API 替代旧的 `generateObject`/`streamObject`；旧版项目仍会遇到后者，迁移时替换为
> `output: Output.object({ schema })`。

### 2.3 统一 Provider 与类型安全

- 通过替换 `openai('gpt-4o')` 为 `anthropic('claude-sonnet-4')` 即可切换模型，业务代码不变。
- 使用 `zod` 定义输出 schema，实现运行时校验与 TypeScript 类型推导。
- 工具参数、结构化输出、调用选项均应走 schema，禁止用 `any` 透传。

---

## 3. 聊天界面与流式渲染

### 3.1 useChat 基础

```tsx
"use client";
import { useChat } from "@ai-sdk/react";

export default function 聊天界面() {
  const { messages, input, handleInputChange, handleSubmit, isLoading, stop, error, reload } = useChat({
    api: "/api/chat",
    maxSteps: 5, // 允许多步工具调用循环
  });

  return (
    <div className="聊天容器">
      <消息列表 messages={messages} isLoading={isLoading} />
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={handleInputChange} disabled={isLoading} placeholder="输入消息" />
        <button type="submit" disabled={isLoading}>
          发送
        </button>
        {isLoading && (
          <button type="button" onClick={stop}>
            停止
          </button>
        )}
      </form>
      {error && <错误提示 error={error} onRetry={reload} />}
    </div>
  );
}
```

### 3.2 消息列表渲染

- 区分 `user` 与 `assistant` 角色。
- 助手消息使用 Markdown 渲染；代码块需语法高亮与复制按钮。
- 每条消息保持稳定 `key`（使用消息 id），避免流式更新时重排。
- 工具调用消息通过 `message.toolInvocations` 单独渲染（见第 4 节）。

```tsx
function 消息列表({ messages, isLoading }: { messages: Message[]; isLoading: boolean }) {
  return (
    <div className="消息列表">
      {messages.map((m) => (
        <div key={m.id} className={m.role === "user" ? "用户消息" : "助手消息"}>
          {m.role === "user" ? m.content : <MarkdownContent content={m.content} />}
          {m.toolInvocations?.map((tool) => (
            <工具调用卡片 key={tool.toolCallId} tool={tool} />
          ))}
        </div>
      ))}
      {isLoading && <流式指示器 />}
    </div>
  );
}
```

### 3.3 流式指示与加载

- `isLoading` 为真时显示骨架屏或脉冲光标，但不阻塞已输出内容的阅读。
- 流式文本会自动追加到当前助手消息，`m.content` 从空字符串逐步增长。
- 提供「停止生成」按钮，调用 `stop()` 取消请求。
- 对 `prefers-reduced-motion` 用户，关闭逐字动画，直接显示完整内容。

---

## 4. 工具调用与结构化输出 UI

### 4.1 工具定义与执行

工具定义放在服务端，参数用 Zod 校验：

```ts
import { streamText } from "ai";
import { z } from "zod";

const result = streamText({
  model: openai("gpt-4o"),
  messages,
  tools: {
    查询天气: {
      description: "获取指定城市当前天气",
      parameters: z.object({
        城市: z.string().describe("城市名称，如 北京"),
      }),
      async execute({ 城市 }) {
        // 实际调用天气 API
        return { 城市, 温度: 24, 天气: "晴" };
      },
    },
    搜索文档: {
      description: "从知识库检索相关段落",
      parameters: z.object({ 查询: z.string() }),
      async execute({ 查询 }) {
        return await 向量检索(查询);
      },
    },
  },
});

return result.toDataStreamResponse();
```

执行原则：

- 工具函数内只包含数据获取/计算，不操作 UI。
- 工具返回可序列化的 JSON，前端据此渲染。
- 敏感工具（下单、删除、发送邮件）必须加二次确认或人工审批。

### 4.2 工具调用 UI 模式

| 阶段         | UI 表现                                           |
| ------------ | ------------------------------------------------- |
| 工具调用中   | 显示调用名与参数骨架，配合脉冲或旋转指示器。      |
| 工具执行完成 | 展示折叠/展开的结果卡片，如天气小部件、引用列表。 |
| 工具失败     | 红色提示，允许重试或让模型继续生成解释。          |

示例：

```tsx
function 工具调用卡片({ tool }: { tool: ToolInvocation }) {
  return (
    <div className="工具卡片">
      <div className="工具头">
        <span>{tool.toolName}</span>
        {tool.state === "call" && <加载指示器 />}
      </div>
      {tool.state === "result" && <pre className="工具结果">{JSON.stringify(tool.result, null, 2)}</pre>}
    </div>
  );
}
```

### 4.3 结构化输出

AI SDK 6 使用 `Output` API：

```ts
import { generateText, Output } from "ai";
import { z } from "zod";

const 食谱Schema = z.object({
  名称: z.string(),
  材料: z.array(z.object({ 名称: z.string(), 用量: z.string() })),
  步骤: z.array(z.string()),
});

const result = await generateText({
  model: openai("gpt-4o"),
  output: Output.object({ schema: 食谱Schema }),
  prompt: "生成一份番茄炒蛋食谱",
});

const 食谱 = result.object; // 类型推导为 RecipeSchema
```

UI 渲染建议：

- 对象 → 表格、卡片、表单字段。
- 数组 → 列表、时间线、数据网格。
- 枚举 → 标签、徽章、筛选器。
- 流式对象 → 渐进填充骨架，避免整页闪烁。

---

## 5. 服务端 AI 集成

### 5.1 API Route 流式端点

推荐用 Next.js App Router API Route 承载 AI 调用：

```ts
// app/api/chat/route.ts
import { openai } from "@ai-sdk/openai";
import { streamText } from "ai";

export const runtime = "edge"; // 或 'nodejs'，视模型 provider 与超时需求
export const maxDuration = 30;

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai("gpt-4o"),
    messages,
    maxTokens: 2048,
    abortSignal: req.signal,
  });

  return result.toDataStreamResponse();
}
```

要点：

- API Key 永远留在服务端环境变量。
- 使用 `req.signal` 让客户端取消时同步中断模型调用。
- 长任务选择 Node.js runtime 并设置 `maxDuration`；低延迟首字节场景可尝试 Edge。

### 5.2 Server Actions

Server Actions 适合无流式或需要组合多次 AI 调用的场景：

```ts
"use server";
import { generateText } from "ai";
import { openai } from "@ai-sdk/openai";

export async function 生成摘要(原文: string) {
  "use server";
  const { text } = await generateText({
    model: openai("gpt-4o-mini"),
    prompt: `用一句话总结：${原文.slice(0, 4000)}`,
  });
  return text;
}
```

需要流式返回的 Server Action 可结合 `ai/rsc` 的 `createStreamableValue` 或 `createStreamableUI`；具体 RSC 用法参考 AI
SDK 官方文档，本模块不展开 React Server Components 基础。

### 5.3 LangChain / LangGraph 接入

当需要复杂编排（RAG、记忆、多工具 Agent、状态图）时，可在服务端用 LangChain / LangGraph 生成流，再用 AI
SDK 适配为前端可消费的 Data Stream：

```ts
import { ChatOpenAI } from "@langchain/openai";
import { LangChainAdapter } from "ai";

export async function POST(req: Request) {
  const { messages } = await req.json();
  const model = new ChatOpenAI({ model: "gpt-4o", streaming: true });
  const stream = await model.stream(messages);
  return LangChainAdapter.toDataStreamResponse(stream);
}
```

LangGraph 接入思路：

1. 构建 LangGraph 状态图，节点负责检索、调用工具、生成回复。
2. 用 `toUIMessageStream()`（AI SDK 6+）将 LangGraph 事件流转换为 AI SDK UI 消息流。
3. 保持前端 `useChat` 不变，后端实现替换为 LangGraph 编排。

---

## 6. 错误处理与加载状态

### 6.1 客户端错误处理

```tsx
const { error, reload } = useChat({ api: "/api/chat" });

{
  error && (
    <div role="alert">
      <p>生成失败：{error.message}</p>
      <button onClick={() => reload()}>重试</button>
    </div>
  );
}
```

错误分类：

| 类型      | 表现             | 处理                                   |
| --------- | ---------------- | -------------------------------------- |
| 网络/超时 | 无响应、连接中断 | 提示重试，保留已生成内容。             |
| 鉴权      | 401/403          | 不暴露 key；提示联系管理员或重新登录。 |
| 内容安全  | 模型拒绝、敏感词 | 显示中性提示，不渲染原始拒绝原因。     |
| 参数/校验 | 400、schema 失败 | 前端预校验，服务端返回翻译后错误码。   |

### 6.2 服务端错误处理

```ts
export async function POST(req: Request) {
  try {
    const { messages } = await req.json();
    // ...
    return result.toDataStreamResponse();
  } catch (err) {
    // 记录服务端日志，不泄露原始错误给客户端
    console.error("AI 调用失败", err);
    return new Response(JSON.stringify({ 错误: "服务暂不可用" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
```

### 6.3 加载状态规范

- 发送按钮在 `isLoading` 时禁用并显示「生成中…」。
- 流式输出期间保持滚动到底部，但用户手动上滚时暂停自动滚动。
- 对慢请求提供进度暗示（如「正在查询天气」「正在整理答案」）。
- 请求失败保留用户已输入消息，便于一键重试。

---

## 7. 安全与限流

### 7.1 API Key 与凭据

- API Key 只存在于服务端环境变量，禁止写入客户端代码、日志、错误消息。
- 不同环境使用不同 Key，生产 Key 最小权限。
- 旋转 Key 时无需改动业务代码，仅更新环境变量。

### 7.2 限流与滥用防护

推荐基于用户身份或 IP 限流：

```ts
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

const 限流器 = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, "1 m"),
});

export async function POST(req: Request) {
  const 用户标识 = await 获取当前用户标识(req);
  const { success } = await 限流器.limit(用户标识 ?? req.ip ?? "anonymous");
  if (!success) {
    return new Response("请求过于频繁", { status: 429 });
  }
  // ...
}
```

限流策略：

- 按用户 ID 限流优于按 IP，避免共享网络误伤。
- 免费/匿名用户限制更严；付费用户按套餐分级。
- 关键工具调用单独限流，防止资源耗尽。

### 7.3 输入输出安全

- 限制单条消息长度与上下文总 token 数。
- 对用户输入做基本清理，拒绝明显恶意 payload。
- 设置 `maxTokens`、`temperature`、超时，避免异常消耗。
- 对模型输出做 XSS 过滤后再渲染；Markdown 渲染需净化。
- 涉及 PII 的输入禁止用于日志或训练。

### 7.4 成本与超时

- 记录每次调用的 token 用量与模型名，便于成本分析。
- 超时设置不超过 `maxDuration`；慢工具调用考虑异步队列。
- 为高成本模型设置fallback：先调用轻量模型，复杂任务再升级。

---

## 8. 模块边界速查

| 主题                                                   | 归属模块         |
| ------------------------------------------------------ | ---------------- |
| React/Next.js 基础、组件生命周期、SSR                  | M07 组件与框架   |
| 设计 token、配色、字体、间距                           | M02 设计系统     |
| 通用 UI 实现、布局、卡片、表单                         | M03 创意实现     |
| 动画、transition、keyframes、微交互                    | M04 动效与交互   |
| 可访问性修复                                           | M13 可访问性修复 |
| 性能优化、Core Web Vitals                              | M14 性能优化     |
| Vercel AI SDK、聊天流式、工具调用、结构化输出、AI 安全 | 本模块 M08       |
