<!-- last-updated: 2026-09-11 -->
# 业务需求：init 后自动接续 generate

## 需求描述

用户要求：init 完成后自动运行 generate，一次完成仓库的 agent-ready 化，不需要二次确认。

## 状态

已完成

## 涉及范围

### 核心逻辑

- skill `init` action 改为 `init [--no-generate]`：默认串联 generate，`--no-generate` 只搭骨架
- 串联实现于工作流契约（references/init-harness.md），脚本层不变

## 约束与备注

- 保持职责二分：`init_project.py` 不新增参数，generate 由 agent 按 generate-aidoc.md 执行
- 同步面：SKILL.md、boundary.md 契约 1、README 双语

## 相关文件

- `skills/project-harness/references/init-harness.md`
- `skills/project-harness/SKILL.md`
- `aiDoc/contracts/boundary.md`
- `aiDoc/notes/implemented/process/2026-09-11-init-auto-generate.md`

## 记录日期

2026-09-11
