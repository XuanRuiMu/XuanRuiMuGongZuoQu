import sys
import pathlib

技能根目录 = pathlib.Path(__file__).resolve().parents[3]

证据根目录 = 技能根目录 / '.agents' / 'evidence'
必要子目录列表 = [
    证据根目录 / 'traces',
    证据根目录 / 'proposals',
    证据根目录 / 'validations',
]

if not 证据根目录.exists():
    print("FAIL: .agents/evidence/ 目录不存在")
    sys.exit(1)

for 子目录 in 必要子目录列表:
    if not 子目录.exists():
        print(f"FAIL: {子目录.relative_to(技能根目录)} 目录不存在")
        sys.exit(1)

证据规范文件路径 = 技能根目录 / 'EVIDENCE.md'
if not 证据规范文件路径.exists():
    print("FAIL: EVIDENCE.md 不存在")
    sys.exit(1)

文件内容 = 证据规范文件路径.read_text(encoding='utf-8')
必要片段列表 = ['压缩与归档规则', '示例条目']
缺失片段列表 = [片段 for 片段 in 必要片段列表 if 片段 not in 文件内容]
if 缺失片段列表:
    print(f"FAIL: EVIDENCE.md 缺少必要片段: {缺失片段列表}")
    sys.exit(1)

print("PASS: 证据目录结构符合规范")
