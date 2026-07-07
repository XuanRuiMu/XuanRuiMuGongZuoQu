# 跨平台导出

## 支持平台

Claude Code、GitHub Copilot、Cursor、Windsurf、Cline、Codex CLI、Gemini CLI、Kiro、Goose、OpenCode、Roo
Code 等共17个平台。

## 双输出机制

每个技能同时生成：

- `SKILL.md`：技能定义
- `AGENTS.md`：指令文件

## 自动安装

创建后自动检测当前平台并安装到原生路径，同时在 `~/.agents/skills/` 创建符号链接供通用路径工具发现。

Tier 2平台（Cursor/Windsurf/Trae）自动生成原生格式：

- Cursor：`.mdc` 规则
- Windsurf/Trae：`.md` 规则

## 常用脚本

```bash
# 规范验证
python3 scripts/validate.py path/to/skill/

# 安全扫描
python3 scripts/security_scan.py path/to/skill/

# 团队registry发布
python3 scripts/skill_registry.py publish ./skill/
```

## 目录模式

```
skill-name/
├── SKILL.md
├── AGENTS.md
├── scripts/
├── references/
└── assets/
```
