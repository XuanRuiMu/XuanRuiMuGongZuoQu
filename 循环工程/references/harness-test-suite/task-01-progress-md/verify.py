import sys
import pathlib
import re

进度文件路径 = pathlib.Path(__file__).resolve().parents[3] / 'PROGRESS.md'

if not 进度文件路径.exists():
    print("FAIL: PROGRESS.md 不存在")
    sys.exit(1)

文件内容 = 进度文件路径.read_text(encoding='utf-8')

标题行匹配 = re.search(r'(?m)^# .+$', 文件内容)
if not 标题行匹配:
    print("FAIL: PROGRESS.md 缺少以 '# ' 开头的非空 H1 标题行")
    sys.exit(1)

必要章节列表 = [
    '## 元信息',
    '## 范围边界',
    '## 功能点列表',
    '## 已完成',
    '## 当前决策',
]
缺失章节列表 = [章节 for 章节 in 必要章节列表 if 章节 not in 文件内容]
if 缺失章节列表:
    print(f"FAIL: 缺少必要章节: {缺失章节列表}")
    sys.exit(1)

if not re.search(r'(?m)^(?:\|.*\bFP-\w+\b.*\||- .*\bFP-\w+\b.*)', 文件内容):
    print("FAIL: PROGRESS.md 中至少应包含一条 FP- 前缀的功能点记录")
    sys.exit(1)

print("PASS: PROGRESS.md 结构正确")
