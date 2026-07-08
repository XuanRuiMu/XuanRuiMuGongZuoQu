import sys
import pathlib
import re


def 查找所有进度文件():
    """PROGRESS.md 可能位于技能根目录、项目根目录或子工作区；返回所有候选。"""
    技能根目录 = pathlib.Path(__file__).resolve().parents[3]
    # 向上搜索项目根目录（直到出现 .agents 或到达盘符根）
    搜索起点 = 技能根目录
    for _ in range(5):
        if (搜索起点 / '.agents').exists() or (搜索起点 / '.git').exists():
            break
        搜索起点 = 搜索起点.parent

    候选集合 = {
        技能根目录 / 'PROGRESS.md',
        搜索起点 / 'PROGRESS.md',
    }
    # 兼容项目子工作区
    if 搜索起点.exists():
        for 子目录 in 搜索起点.iterdir():
            if 子目录.is_dir() and not 子目录.name.startswith('.'):
                候选集合.add(子目录 / 'PROGRESS.md')
    return [候选 for 候选 in 候选集合 if 候选.exists()]


def 验证进度文件(进度文件路径):
    文件内容 = 进度文件路径.read_text(encoding='utf-8')

    if not re.search(r'(?m)^# .+$', 文件内容):
        return "缺少以 '# ' 开头的非空 H1 标题行"

    必要章节列表 = [
        ('## 元信息',),
        ('## 范围边界', '范围边界：'),
        ('## 功能点列表', '## 待处理功能点列表', '## 待处理功能点'),
        ('## 已完成',),
        ('## 当前决策',),
    ]
    缺失章节列表 = []
    for 章节 in 必要章节列表:
        if not any(替代 in 文件内容 for 替代 in 章节):
            缺失章节列表.append(章节[0])
    if 缺失章节列表:
        return f"缺少必要章节: {缺失章节列表}"

    if not re.search(r'(?m)^(?:\|.*\bFP-\w+\b.*\||- .*\bFP-\w+\b.*)', 文件内容):
        return "至少应包含一条 FP- 前缀的功能点记录"

    return None


进度文件列表 = 查找所有进度文件()

if not 进度文件列表:
    print("FAIL: PROGRESS.md 不存在")
    sys.exit(1)

错误列表 = []
for 进度文件 in 进度文件列表:
    错误 = 验证进度文件(进度文件)
    if 错误 is None:
        try:
            显示路径 = 进度文件.relative_to(pathlib.Path(__file__).resolve().parents[4])
        except ValueError:
            显示路径 = 进度文件.name
        print(f"PASS: PROGRESS.md 结构正确 ({显示路径})")
        sys.exit(0)
    错误列表.append(f"{进度文件}: {错误}")

print(f"FAIL: 所有候选 PROGRESS.md 验证未通过")
for 错误 in 错误列表:
    print(f"  - {错误}")
sys.exit(1)
