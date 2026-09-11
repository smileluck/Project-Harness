<!-- last-updated: 2026-09-11 -->
# 业务需求：AI 开发自动触发规则更新（自进化回路）

## 需求描述

用户要求：AI 在开发改动时能自动触发对 aiDoc 的检测与回写，使分层架构约束规则随改动持续更新（"自进化"）；且方案需适配不同 AI 工具，不依赖单一工具的 hook 机制。

## 状态

已完成

## 涉及范围

### 核心逻辑

- 规则层：根 `AGENTS.md` 操作不变量与 DoD
- skill 产物：`skills/project-harness/templates/{zh,en}/AGENTS.md.tmpl`
- agent 行为契约：`skills/project-harness/references/sync-aidoc.md`、`change-docs.md`

## 约束与备注

- 实现为规则级强制步骤（不变量 #3 强化 + 新增 #8），不配置工具私有 hook，保证跨工具适配
- 漂移检测复用既有 `check_sync.py`，无脚本时降级为路由表人工核对

## 相关文件

- `AGENTS.md`
- `skills/project-harness/templates/zh/AGENTS.md.tmpl`、`skills/project-harness/templates/en/AGENTS.md.tmpl`
- `skills/project-harness/references/sync-aidoc.md`、`skills/project-harness/references/change-docs.md`
- `aiDoc/notes/implemented/process/2026-09-11-self-evolution-loop.md`

## 记录日期

2026-09-11
