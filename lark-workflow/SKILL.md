---
name: lark-workflow
version: 1.0.0
description: "飞书工作流：会议纪要汇总与日程待办摘要。汇总指定时间范围内的会议纪要并生成结构化报告，或编排calendar和task数据生成日程与未完成任务摘要。"
metadata:
  requires:
    bins: ["lark-cli"]
---

# 飞书工作流

**CRITICAL — 开始前 MUST 先用 Read 工具读取 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md)，其中包含认证、权限处理**

## 模式选择

| 需求 | 模式 |
|------|------|
| 整理会议纪要、生成会议周报 | 会议纪要汇总 |
| 今天有什么安排、日程待办摘要 | 日程待办摘要 |

---

## 模式一：会议纪要汇总

### 适用场景

- "帮我整理这周的会议纪要" / "总结最近的会议" / "生成会议周报"
- "看看今天开了哪些会" / "回顾过去一周开了哪些会"

### 前置条件

仅支持 **user 身份**。执行前确保已授权：

```bash
lark-cli auth login --domain vc        # 基础（查询+纪要）
lark-cli auth login --domain vc,drive   # 含读取纪要文档正文、生成文档
```

### 工作流

```
{时间范围} → vc +search → 会议列表 (meeting_ids)
                   │
                   ▼
               vc +notes → 纪要文档 tokens
                   │
                   ▼
               drive metas batch_query 纪要元数据
                   │
                   ▼
               结构化报告
```

#### Step 1: 确定时间范围

默认**过去 7 天**。推断规则："今天"→当天，"这周"→本周一~now，"上周"→上周一~上周日，"这个月"→1日~now。

#### Step 2: 查询会议记录

```bash
lark-cli vc +search --start "<YYYY-MM-DD>" --end "<YYYY-MM-DD>" --format json --page-size 30
```

- 时间范围最大1个月，超过需拆分多次查询
- 有 `page_token` 时必须继续翻页

#### Step 3: 获取纪要元数据

```bash
lark-cli vc +notes --meeting-ids "id1,id2,...,idN"
lark-cli drive metas batch_query --data '{"request_docs": [{"doc_type": "docx", "doc_token": "<doc_token>"}], "with_url": true}'
```

#### Step 4: 整理纪要报告

- 单日汇总：用"今日会议概览"标题，逐会议列出时间、主题、纪要链接、逐字稿链接
- 多日/周报：用"会议纪要周报"标题，含概览统计、逐会议详情

#### Step 5: 生成文档（可选）

```bash
lark-cli docs +create --api-version v2 --doc-format markdown --content $'<title>会议纪要汇总</title>\n<内容>'
```

---

## 模式二：日程待办摘要

### 适用场景

- "今天有什么安排" / "今天的日程和待办"
- "明天有什么会" / "明日日程与未完成任务"
- "开工摘要" / "standup report"

### 前置条件

```bash
lark-cli auth login --domain calendar,task
```

### 工作流

```
{date} ─┬─→ calendar +agenda ──→ 日程列表
        └─→ task +get-my-tasks ──→ 未完成待办列表
                    │
                    ▼
              AI 汇总（时间转换 + 冲突检测 + 排序）──→ 摘要
```

#### Step 1: 获取日程

```bash
# 今天（默认）
lark-cli calendar +agenda

# 指定日期（ISO 8601）
lark-cli calendar +agenda --start "2026-03-26T00:00:00+08:00" --end "2026-03-26T23:59:59+08:00"
```

#### Step 2: 获取未完成待办

```bash
lark-cli task +get-my-tasks --due-end "2026-03-27T23:59:59+08:00"
```

#### Step 3: AI 汇总

按以下结构输出：

```
## {日期}摘要（{YYYY-MM-DD 星期X}）

### 日程安排
| 时间 | 事件 | 组织者 | 状态 |
|------|------|--------|------|
| 09:00-10:00 | 产品需求评审 | 张三 | 已接受 |

### 待办事项
- [ ] {task_summary}（截止：{due_date}）

### 小结
- 共 {n} 场会议，{m} 项待办
- 冲突提醒：{列出时间重叠的日程}
```

## 权限

| 命令 | 所需 scope |
|------|-----------|
| `calendar +agenda` | `calendar:calendar.event:read` |
| `task +get-my-tasks` | `task:task:read` |

## 参考

- [lark-shared](../lark-shared/SKILL.md) — 认证、权限（必读）
- [lark-vc](../lark-vc/SKILL.md) — `+search`、`+notes` 详细用法
- [lark-calendar](../lark-calendar/SKILL.md) — `+agenda` 详细用法
- [lark-task](../lark-task/SKILL.md) — `+get-my-tasks` 详细用法
- [lark-doc](../lark-doc/SKILL.md) — `+fetch`、`+create`、`+update` 详细用法
