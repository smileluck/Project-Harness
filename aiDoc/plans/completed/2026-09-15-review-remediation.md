<!-- last-updated: 2026-09-15 -->
# 变更计划：2026-09-15 全面评审整改

## 目标

落地全面评审的高优先发现：推送通道、机械产物、口径修正、脚本正确性、update 下发链路、模板路由表对齐。

## 工作项

| # | 工作项 | 状态 |
|---|---|---|
| 1 | 推送通道诊断（SSH key 带 passphrase，需用户解锁后 push） | 阻塞-用户侧 |
| 2 | code-index.md 以 zh 再生成并核对统计 | 完成 |
| 3 | 口径修正批（五工作流×4、sync-aidoc 表/scope、SKILL.md×3、init-harness、tool-adapters、--lang auto、中文格） | 完成 |
| 4 | init_project 六项正确性修正 | 完成 |
| 5 | update_harness 模板新增文件三分类 + skip_set 形式修复 + selftest 用例 | 完成 |
| 6 | manifest 刷新（14 文件、补登记 pre-push-checks、boundary 契约回写） | 完成 |
| 7 | zh/en 路由表对齐 13 行并集 + 本仓实例同步 | 完成 |
| 8 | 收尾（last-updated、P2 标题、business 记忆、lesson、决策记录、本计划） | 完成 |
| 9 | 全量验证（selftest + check_sync + py_compile） | 完成 |

## 验证命令

- `python3 tests/selftest.py` — 覆盖新增下发链路与收敛回归
- `python3 skills/project-harness/scripts/check_sync.py .` — 漂移闸门
- `python3 -m py_compile install.py skills/project-harness/scripts/*.py tests/selftest.py`

## 遗留

- push + CI 首跑（用户解锁 SSH 后）
- 剩余评审发现见 aiDoc/notes/implemented/process/2026-09-15-review-remediation.md「剩余工作」
