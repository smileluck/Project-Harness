<!-- last-updated: 2026-09-13 -->
# 业务需求：AI 自进化（RSI）回路优化——lessons 机械闸门 + 复发闭环

## 需求描述

用户要求在当前项目实现 RSI（Recursive Self-Improvement，递归自我改进）并优化现有机制：让「踩坑 → 记录 → 晋升 → 验证」回路具备机械强制力与效果反馈，而不只依赖 agent 自觉。

## 状态

已完成

## 涉及范围

### 核心逻辑

- `skills/project-harness/scripts/check_sync.py`：新增检查 5/6（lessons 晋升纪律 + 可扫描性）
- `tests/selftest.py`：lessons 闸门 fixture
- `skills/project-harness/templates/{zh,en}/`：lessons TEMPLATE/README、AGENTS.md.tmpl
- `skills/project-harness/references/`：change-docs.md、sync-aidoc.md、aidoc-structure.md
- 本仓库规则层：`AGENTS.md` 不变量 #9、`aiDoc/modules/architecture-rules.md`、`aiDoc/memory/lessons/`

## 约束与备注

- 机械判定只读头部 `lesson-meta` 显式标记，禁止标题文本匹配（应用已晋升的 lesson）
- 存量仓库旧格式 lesson 只提示不拦截，不强制迁移

## 相关文件

- `aiDoc/notes/implemented/process/2026-09-13-rsi-lessons-mechanization.md`
- `aiDoc/plans/completed/2026-09-13-rsi-lessons-mechanization.md`
- `aiDoc/memory/lessons/2026-09-13-explicit-markers-over-heading-text.md`

## 记录日期

2026-09-13
