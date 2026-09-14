<!-- last-updated: 2026-09-13 -->
# 业务需求：harness 更新功能——已安装 skill 与目标仓库产物可升级到新版本

## 需求描述

用户要求增加更新功能：工具包出新版本后，已安装的 skill 副本与已 init 的目标仓库产物都能更新。确认范围：安装层 + 目标仓库产物层两者都要；版本标识用 git 标签/提交，不引入 VERSION 文件。

## 状态

已完成

## 涉及范围

### 核心逻辑

- `install.py`：版本写入标识文件、同版本 SKIP、`--check`
- `skills/project-harness/scripts/harness_common.py`：新增 `git_version` 单源实现
- `skills/project-harness/scripts/init_project.py`：产物 manifest 基线
- `skills/project-harness/scripts/update_harness.py`（新增）：目标仓库托管文件机械更新 + adopt 模式
- skill 层：`SKILL.md` 路由、`skills/project-harness/references/update-harness.md`（新增）、`init-harness.md`
- 契约/文档：`aiDoc/contracts/boundary.md`、`skills/project-harness/references/aidoc-structure.md`、`skills/project-harness/references/harness-model.md`、根 `AGENTS.md` 仓库概览
- `tests/selftest.py`：`test_update_flow` 12 项断言（install 侧由既有 `test_install` 覆盖）

## 约束与备注

- 安全模型不回退：项目改过的文件永不覆盖；模板已删的文件首版不自动删；刷新前必备份
- 本仓库已用 update_harness.py adopt 建立自身基线（`aiDoc/.harness-manifest.json`）

## 相关文件

- `aiDoc/notes/implemented/feature/2026-09-13-harness-update.md`
- `aiDoc/plans/completed/2026-09-13-harness-update.md`

## 记录日期

2026-09-13
