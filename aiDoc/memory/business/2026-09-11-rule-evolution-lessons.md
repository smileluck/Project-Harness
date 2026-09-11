<!-- last-updated: 2026-09-11 -->
# 业务需求：规则自进化——经验自动提炼回约束层

## 需求描述

用户要求：架构约束规则不能只在人提出时更新，需要机制把多次开发中反复出现的模式、踩过的坑自动提炼回约束层（规则本身的进化），且方案适配不同 AI 工具。

## 状态

已完成

## 涉及范围

### 核心逻辑

- 新增 `aiDoc/memory/lessons/` 经验采集层（模板 zh/en 镜像）
- AGENTS.md 不变量 #9（捕获）+ 晋升纪律（references/change-docs.md）+ sync 兜底扫描
- skill record action 增加 lesson 子命令（契约同步 boundary.md）

## 约束与备注

- 规则级强制步骤，不依赖工具 hook；晋升判断是语义行为，由 agent 执行，脚本不参与
- 原则：一次是经历，两次是模式——第二次出现即晋升约束正文

## 相关文件

- `AGENTS.md`（不变量 #9）
- `aiDoc/memory/lessons/README.md`、`aiDoc/memory/lessons/TEMPLATE.md`
- `skills/project-harness/templates/{zh,en}/aidoc/memory/lessons/`
- `skills/project-harness/references/change-docs.md`、`sync-aidoc.md`、`aidoc-structure.md`、`harness-model.md`
- `aiDoc/notes/implemented/process/2026-09-11-rule-evolution-lessons.md`

## 记录日期

2026-09-11
