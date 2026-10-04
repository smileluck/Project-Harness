<!-- last-updated: 2026-10-04 -->
# 业务需求：项目集更新功能——成员增删时刷新根 AGENTS.md 索引，不动成员 harness

## 需求描述

用户要求增加项目集更新功能：项目成员已有 harness 时，更新项目集不更新成员；一般情况下只是增删成员并维护成员的简单说明；功能涉及多成员时，到对应成员的 harness 内分别更新。确认范围：简介放索引表新增「简介」列；入口为新 action `update-set`（脚本 `--refresh` 模式）；目录已消失的成员自动删行并报告。

## 状态

已完成

## 涉及范围

### 核心逻辑

- `skills/project-harness/scripts/init_project_set.py`：`--refresh` 模式（三方合并成员表：保留校订简介、机械刷新状态列、删消失行、追加新行；备份+幂等+前置校验）；init 路径根表升 5 列、跳过成员也只读扫描取简介
- `skills/project-harness/templates/zh|en/project-set/AGENTS.md.tmpl`：索引表说明加简介列（双语镜像）
- skill 层：`SKILL.md` 路由（`update-set`）、`skills/project-harness/references/init-project-set.md` 加 Update-set 小节（含「跨成员功能变更到各成员仓库内更新」边界）
- 契约/文档：`aiDoc/contracts/boundary.md`（契约 1/2/3）、根 `AGENTS.md` 仓库概览
- `tests/selftest.py`：`test_init_project_set_refresh` 12 项断言 + init-set 表格断言升 5 列

## 约束与备注

- update-set 绝不写成员目录；新增未配置成员只在报告中提示可跑 init-set
- 校订根 AGENTS.md 时保留 `<!-- scan-fill:members -->` 标记（refresh 定位依赖），只移除 auto-scan 标记
- 根 AGENTS.md 不进 manifest 托管集，`--refresh` 是其唯一机械更新通道

## 相关文件

- `aiDoc/notes/implemented/feature/2026-10-04-update-project-set.md`
- `aiDoc/notes/implemented/feature/2026-10-03-project-set-init.md`

## 记录日期

2026-10-04
