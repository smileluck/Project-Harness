<!-- last-updated: 2026-10-03 -->
# 业务需求：项目集批量初始化——多项目根目录一次配置 project-harness + 根 AGENTS.md

## 需求描述

用户会把几个项目放在同一个文件夹（项目集根目录）下，希望一次处理这些项目：为未配置的成员项目独立配置 project-harness，并在项目集根目录创建根 `AGENTS.md`，书写不同项目之间的关系和作用，方便 AI 协调多项目。确认范围：成员识别=列出全部子目录由 AI 确认；已配置成员完全跳过；根产物仅 `AGENTS.md`。

## 状态

已完成

## 涉及范围

### 核心逻辑

- `skills/project-harness/scripts/init_project_set.py`（新增）：discovery + 批量 init + 根 AGENTS.md
- `skills/project-harness/templates/zh|en/project-set/AGENTS.md.tmpl`（新增，双语镜像）
- skill 层：`SKILL.md` 路由（`init-set`）、`skills/project-harness/references/init-project-set.md`（新增）、`init-harness.md`/`harness-model.md` 指针
- 契约/文档：`aiDoc/contracts/boundary.md`（契约 1/2/3）、根 `AGENTS.md` 仓库概览
- `tests/selftest.py`：`test_init_project_set` 19 项断言 + scan-fill 耦合校验扩展

## 约束与备注

- 已配置成员（有 `aiDoc/.harness-manifest.json`）完全跳过；嵌套 git 子目录 blocked 不中断整批
- 项目集根只写 `AGENTS.md`，不写根级 manifest/aiDoc；根文件不进 update_harness 托管集
- 每个新初始化成员默认接续独立 generate 工作流（无批量 generate）

## 相关文件

- `aiDoc/notes/implemented/feature/2026-10-03-project-set-init.md`

## 记录日期

2026-10-03
