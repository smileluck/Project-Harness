<!-- last-updated: 2026-09-10 -->
# 决策：aiDoc 文档层与 harness 协作系统合并为单一文档家园

## 问题

工具包要同时吸收两个参考的设计：generate-aidoc 的 aiDoc 分层文档体系（路由表/模块规则/示例/记忆）与 dsh-project-harness 的协作工件（决策记录 notes、变更计划 plans、handoff）。两者各有自己的目录（aiDoc/ vs .agents/notes|plans），直接并存会产生两个文档家园、两张索引，违反"一个事实一个维护家"。

## 提案 / 决策

单一文档家园 `aiDoc/`：dsh 的决策记录与变更计划并入为 `aiDoc/notes/`（`<proposed|implemented|rejected>/<class>/yyyy-mm-dd-topic.md`）与 `aiDoc/plans/`（`active/completed/`），由 `aiDoc/README.md` 的唯一路由表统一覆盖。`.agents/` 只保留项目级工作流 skills（project-code-review、project-pre-push-checks），不放文档。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| 保留 dsh 的 `.agents/notes` + `.agents/plans` 独立目录 | 两套索引并行维护，口径漂移风险高；路由表失去单一入口 |
| 完整引入 Harness_Handbook 的 LLM 手册流水线 | 重量级、需要 LLM 凭据与 tree-sitter 依赖，违背零依赖定位（用户明确未选） |

## 验收标准

- [x] 目标项目产物中文档类工件全部位于 `aiDoc/`，路由表唯一维护于 `aiDoc/README.md`
- [x] notes 采用 lifecycle/class 两级结构并带纪律规则（不编造备选、implemented 就地更新、推翻新建交叉链接）

## 风险与后果

- 与 dsh 原版路径不同，熟悉 dsh 的用户需要按本仓库的结构重新定位
- aiDoc/README.md 成为单点：它失真则整个路由层失真，因此 check_sync 把索引完整性作为硬性检查

## 交叉链接

- 参考来源：`README.md` 致谢节的 generate-aidoc / dsh-project-harness
- 结构契约：`skills/project-harness/references/aidoc-structure.md`
