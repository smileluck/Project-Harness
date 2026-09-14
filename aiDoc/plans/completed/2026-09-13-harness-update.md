<!-- last-updated: 2026-09-13 -->
# 变更计划：harness 更新功能——git 版本标识 + manifest 基线 + update 工作流

> 路径：`aiDoc/plans/completed/2026-09-13-harness-update.md`

## 目标

工具包出新版本后，已安装 skill 副本与已 init 的目标仓库产物都能更新：安装层有版本检测，产物层有机械刷新路径且不覆盖项目改动。

## 非目标

- 自动删除模板已移除的项目文件（首版只报告）
- 项目已改文件的自动合并（归 generate/sync 语义层）
- 显式 VERSION 文件（用户选定 git 版本）

## 假设

- 版本可从不保证：skill 被脱离仓库拷贝时为 `unknown`，行为回退可预期
- 无 manifest 的存量仓库先 adopt 建基线

## 影响面

- `install.py`、`skills/project-harness/scripts/harness_common.py`、`skills/project-harness/scripts/init_project.py`、`skills/project-harness/scripts/update_harness.py`（新增）
- `SKILL.md`、`skills/project-harness/references/update-harness.md`（新增）、`init-harness.md`、`aidoc-structure.md`、`harness-model.md`
- `aiDoc/contracts/boundary.md`、根 `AGENTS.md`、`tests/selftest.py`

## 验收标准

- [x] install 同版本 SKIP / 旧版 UPDATE / `--check` 退出码
- [x] init 产物 manifest 基线正确
- [x] update 五分类（refreshed/unchanged/user-modified/removed-in-template/deleted-by-user）行为正确，`--force` 收敛，`--dry-run` 零写入，adopt 不登记已改文件
- [x] `python3 tests/selftest.py` 全绿、`check_sync.py .` 全绿
- [x] 本仓库 adopt 建立自身基线

## 工作项

| # | 工作项 | 状态 |
|---|---|---|
| 1 | install.py 版本固化 + SKIP + `--check` | 完成 |
| 2 | harness_common.git_version 单源 + init manifest | 完成 |
| 3 | update_harness.py（刷新/adopt/五分类报告） | 完成 |
| 4 | skill 路由 + update-harness.md + 契约文档同步 | 完成 |
| 5 | selftest `test_update_flow` 12 项断言 | 完成 |
| 6 | 本仓库 adopt 建基线 + 漂移自检 | 完成 |
| 7 | 留痕（note/business/lesson/索引） | 完成 |

## 验证命令

```bash
python3 tests/selftest.py
python3 skills/project-harness/scripts/check_sync.py .
```

## 回滚 / 迁移

git revert；存量仓库无 manifest 时 update 自动走 adopt，无需迁移。

## 当前状态

已完成。

## 交付摘要

- 两层更新链路落地：install 版本检测（SKIP/`--check`）→ init 写 manifest 基线 → update_harness 机械刷新 + 语义合入分流。
- 与计划偏差：开发中与并行 agent 的架构整改（f638fa1）同仓冲突，未跟踪的 update_harness.py 被抹掉一次后重建；版本 helper 随整改单源化进 harness_common；据此记 lesson `2026-09-13-untracked-files-vs-concurrent-agents.md`（并行工作要尽早提交）。
- 遗留：模板已删文件的自动清理、项目已改文件的辅助合并，列入后续候选。
