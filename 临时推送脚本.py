# -*- coding: utf-8 -*-
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

sys.path.insert(0, r"d:\XiTongWenJianJia\ZhuoMian\燃烧之陨我的世界服务端\总控制台")

from 总控制台 import Git推送器

推送器 = Git推送器()

# 推送XuanRuiMuGongZuoQu仓库（skill改进）
仓库1 = next((r for r in 推送器.仓库列表 if r["名称"] == "XuanRuiMuGongZuoQu"), None)
提交信息1 = """循环工程skill Self-Harness元循环改进：应用3个待确认级提案

提案A：SKILL.md阶段3主代理循环逻辑增加依赖验证强制项+并行前强制编译验证
提案B：子代理提示词模板增加debug日志安全自审强制项（不得修改业务调用次数/变量/控制流）
提案C：子代理提示词模板增加翻译模板修改测试同步自审强制项（修改模板后必须grep同步测试断言）

同步更新：HARNESS.md组件版本日期、EVIDENCE.md提案状态、BUDGET.md环境规避节追加2条
"""
print(f"=== 推送仓库1：{仓库1['名称']} ===")
结果1 = 推送器.非交互推送单个仓库(仓库1, 提交信息=提交信息1)
print(f"仓库1推送结果: {'成功' if 结果1 else '失败'}")

# 推送MMORPG服务端仓库（删除过程性文件）
仓库2 = next((r for r in 推送器.仓库列表 if r["名称"] == "MMORPG服务端"), None)
提交信息2 = """删除循环工程过程性文件：5个FP需求文档+5个测试报告

删除文件：
- FP-01因果事件日志事务与严格单行输出.md
- FP-01怪物名称完整性与HealthBar策略.md
- FP-08技能释放结果日志必输出.md
- FP-09伤害来源染色与躲闪日志一致性.md
- FP-10所有技能debug日志增强.md
- 测试报告5个（受击修正/日志合并/实体适配/事件日志/奥能法师技能基础）

这些文件是循环工程本轮任务的过程性文档，代码修复已完成并上传，过程性文件清理
"""
print(f"\n=== 推送仓库2：{仓库2['名称']} ===")
结果2 = 推送器.非交互推送单个仓库(仓库2, 提交信息=提交信息2)
print(f"仓库2推送结果: {'成功' if 结果2 else '失败'}")

print(f"\n=== 总体结果：{'全部成功' if 结果1 and 结果2 else '部分失败'} ===")
sys.exit(0 if (结果1 and 结果2) else 1)
