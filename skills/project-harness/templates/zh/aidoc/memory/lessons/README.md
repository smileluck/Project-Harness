<!-- last-updated: {{DATE}} -->
# 经验记忆（lessons）

存放开发过程中踩过的坑与反复出现的模式。本目录是**经验 staging 区**：经验在此低成本采集，达到晋升条件后写进约束正文（`/AGENTS.md`、`modules/architecture-rules.md`、`contracts/boundary.md` 等），本目录只留记录与去向链接。

## 规则

- 工作中踩坑、review 反复发现同类问题、或发现可复用模式时，必须在同一变更内记一条 lesson
- 已有同类 lesson 时**就地累加出现次数**，不重复建档
- 使用 [TEMPLATE.md](TEMPLATE.md) 作为新记录模板（保持轻量，5 行成本）
- 记录或累加后在 [../project-memory.md](../project-memory.md) 中更新索引
- 命名约定：`yyyy-mm-dd-主题.md`

## 晋升纪律

- 触发：同一 lesson 第 2 次出现，或用户显式确认——**一次是经历，两次是模式**
- 动作：在同一变更内把规则写进约束正文所在文档，本记录状态改 `promoted` 并填晋升去向链接
- 晋升涉及行为/架构/契约变化时，仍须按 `aiDoc/notes/README.md` 写决策记录
- 确认无通用价值的条目标 `dropped`，必须写理由
- 禁止只攒经验不晋升；sync 工作流会扫描 `pending` 且次数 ≥2 的条目兜底

## 经验索引

暂无。
