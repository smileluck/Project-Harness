<!-- last-updated: 2026-09-11 -->
# 决策：规则级自进化回路——强制漂移自检 + 决策回写约束

> 路径：`aiDoc/notes/implemented/process/2026-09-11-self-evolution-loop.md`

## 问题

用户提出：AI 开发过程中应能"自动触发"对 aiDoc 的访问与回写，使分层架构约束规则随改动不断更新（即"自进化"）。现状只有纪律约束 + 手动触发（sync 工作流、pre-push 检查），没有任何机制保证改动收尾时文档与规则被回写；且工具私有 hook 方案无法跨工具适配。

## 提案 / 决策

把"自动触发"实现为**规则级强制步骤**而非工具 hook，两处变更：

1. **强制漂移自检**（新增操作不变量 #8）：完成任何代码或文档改动前，agent 必须主动运行 `check_sync.py`（无脚本时按路由表人工核对），发现的漂移在同一变更内修复；自检结果纳入 Definition of Done。
2. **决策回写约束**（强化不变量 #3）：决策涉及架构/契约/流程约束时，必须在同一变更内同步更新约束正文所在文档，禁止只记决策不改规则。

同步面：根 `AGENTS.md`、`templates/{zh,en}/AGENTS.md.tmpl` 镜像、`references/sync-aidoc.md`（completion gate）、`references/change-docs.md`（constraints are rewritten）。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| 配置工具 hook（如 Kimi Code config.toml hooks）自动跑 check_sync.py | 工具私有、无法跨 Claude/Cursor/Trae 适配；违反「规则不进工具私有目录」不变量；且本仓库是 toolkit，方案需对所有目标仓库成立 |
| 维持现状（纪律 + 手动 sync） | 用户明确指出需要自动触发与持续更新，现状靠自觉无强制力 |

## 验收标准

- [x] 根 AGENTS.md 含不变量 #8 与强化后的 #3，DoD 含漂移自检勾选项
- [x] zh/en 模板结构一致、语义一致
- [x] references/sync-aidoc.md 将 Step 1 列为强制收尾闸门；references/change-docs.md 含约束回写纪律
- [x] `python3 skills/project-harness/scripts/check_sync.py .` 无因本次改动产生的漂移

## 风险与后果

- 规则级强制仍依赖 agent 遵守，非机器拦截；但配合 DoD 勾选项与 pre-push 检查形成双层兜底
- 不变量条目增多，提高 agent 每次收尾的固定成本；用「无脚本时按路由表核对」降级路径控制成本
- 后续若某工具支持 hook，可在其上叠加自动触发，但规则正文仍以本文件为准

## 交叉链接

- 变更计划：`aiDoc/plans/completed/2026-09-11-self-evolution-loop.md`
- 规则本体：`AGENTS.md` 操作不变量 #3/#8
- 行为契约：`skills/project-harness/references/sync-aidoc.md`、`skills/project-harness/references/change-docs.md`
