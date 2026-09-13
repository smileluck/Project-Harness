<!-- last-updated: 2026-09-13 -->
# P0+P1 整改：破损修复与单源化去冗余

## 需求描述

用户要求以资深 harness 工程师/架构师视角对 project-harness 做整体评审并整改：修复全部已确认的真实破损（code-index 修复死锁、check_sync 白名单盲区、模板与 dogfood 实例漂移、未渲染占位符），并对高频规则做单源化手术、zh/en 镜像升级结构级校验、脚本公共库抽取。整改范围选定 P0+P1（不含治理哲学调整）。

## 状态

done（2026-09-13 完成；全部验证通过）

## 涉及范围

### 后端 / library

- `skills/project-harness/scripts/scan_repo.py`：`--write-code-index`/`--lang`、关键词表合并、Cargo/pom 解析扩展、`render_data` 导入
- `skills/project-harness/scripts/check_sync.py`：白名单扩容、TEMPLATE/占位符豁免、argparse、公共读取
- `skills/project-harness/scripts/init_project.py`：`_walk_copy`/`_prep_dst` 合并、公共库接入
- 新增 `harness_common.py`、`render_data.py`；`install.py` 接入公共库
- `tests/selftest.py`：新增 [2b][2c][4 结构][4b][5 唯一性][5b 样板] 六组断言

### 前端

无。

### 命令行（cli）

`scan_repo.py --write-code-index [--lang zh|en]` 新 CLI 能力。

## 约束与备注

- 不做 git commit，全部改动留在工作区
- 模板实例化副本保持自包含（注入模型硬约束），靠样板 diff 校验兜底

## 相关文件

- 计划：`aiDoc/plans/completed/2026-09-13-p0p1-remediation.md`
- 决策：`aiDoc/notes/implemented/bug-fix/2026-09-13-code-index-deadlock-whitelist.md`、`aiDoc/notes/implemented/simplification/2026-09-13-single-source-dedup.md`
- 契约：`aiDoc/contracts/boundary.md` 契约 2

## 记录日期

2026-09-13
