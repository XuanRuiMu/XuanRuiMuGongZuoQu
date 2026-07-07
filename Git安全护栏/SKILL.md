---
name: Git安全护栏
description: >
  设置Claude Code钩子，在执行前拦截并阻止危险的git命令。阻止push、reset --hard、clean、branch -D等破坏性操作。
  触发场景：需要防止Claude执行破坏性git操作、添加git安全钩子、阻止git push/reset。
  当用户说"Git安全护栏"、"阻止危险git命令"、"git安全钩子"、"git guardrails"时触发此技能。
---

# 设置Git安全护栏

设置PreToolUse钩子，在Claude执行危险git命令之前拦截并阻止它们。

## 被阻止的命令

- `git push`（包括`--force`在内的所有变体）
- `git reset --hard`
- `git clean -f` / `git clean -fd`
- `git branch -D`
- `git checkout .` / `git restore .`

被阻止时，Claude会看到一条消息，告知它没有权限执行这些命令。

## 步骤

### 1. 询问作用范围

询问用户：安装到**仅此项目**（`.claude/settings.json`）还是**所有项目**（`~/.claude/settings.json`）？

### 2. 复制钩子脚本

内置脚本位于：[scripts/block-dangerous-git.sh](scripts/block-dangerous-git.sh)

根据作用范围复制到目标位置：

- **项目级**：`.claude/hooks/block-dangerous-git.sh`
- **全局**：`~/.claude/hooks/block-dangerous-git.sh`

使用 `chmod +x` 设置可执行权限。

### 3. 将钩子添加到配置

添加到对应的配置文件：

**项目级**（`.claude/settings.json`）：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

**全局**（`~/.claude/settings.json`）：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

如果配置文件已存在，将钩子合并到现有的 `hooks.PreToolUse` 数组中——不要覆盖其他设置。

### 4. 询问自定义

询问用户是否要从阻止列表中添加或移除任何模式。相应地编辑复制的脚本。

### 5. 验证

运行快速测试：

```bash
echo '{"tool_input":{"command":"git push origin main"}}' | <脚本路径>
```

应该以退出码2退出，并在stderr中打印BLOCKED消息。
