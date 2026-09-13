<!-- last-updated: 2026-09-11 -->
# 变更计划：规则级自进化回路（强制漂移自检 + 决策回写约束）

## 目标

把「改动后自动触发漂移检测与规则回写」从依赖工具 hook 的方案，改为写进 `AGENTS.md` 操作不变量的**强制步骤**（任何工具的 agent 都必须执行），并强化「决策涉及约束时必须同步更新约束正文」的回路。

## 非目标

- 不配置任何工具私有 hook（config.toml / .claude 等）
- 不改动 check_sync.py 脚本本身
- 不改 aiDoc 目录结构与路由表

## 假设

- 目标仓库规则正文只维护在 `AGENTS.md` 与 `aiDoc/`，模板 zh/en 严格镜像
- references 是 agent 行为契约，需与不变量同步

## 影响面

- 根 `AGENTS.md`（操作不变量、DoD）
- `skills/project-harness/templates/{zh,en}/AGENTS.md.tmpl`（镜像）
- `skills/project-harness/references/{sync-aidoc,change-docs}.md`（行为契约）
- `aiDoc/notes/`、`aiDoc/memory/business/`（记录层）

## 验收标准

- [ ] 根 AGENTS.md 新增「改动收尾必过漂移自检」不变量，且「决策要留痕」含约束回写条款
- [ ] zh/en 模板结构一致、语义一致
- [ ] references 两处同步更新
- [ ] 决策记录与 business 记忆落盘、索引更新
- [ ] `check_sync.py` 跑通且无因本次改动产生的漂移

## 工作项

| # | 工作项 | owner | 依赖 | 建议写范围 | 验证命令 | 状态 |
|---|---|---|---|---|---|---|
| 1 | 根 AGENTS.md 规则变更 | agent | 无 | `AGENTS.md` | 目视 + check_sync | 完成 |
| 2 | zh/en 模板镜像 | agent | 1 | `skills/project-harness/templates/{zh,en}/AGENTS.md.tmpl` | diff 结构对比 | 完成 |
| 3 | references 同步 | agent | 1 | `skills/project-harness/references/` | 目视 | 完成 |
| 4 | 决策记录 + 记忆 | agent | 1 | `aiDoc/notes/`、`aiDoc/memory/` | 索引一致性 | 完成 |

## 验证命令

```bash
python3 skills/project-harness/scripts/check_sync.py .
```

## 回滚 / 迁移

纯文档变更，git revert 即可。

## 当前状态

已完成。

## 交付摘要（完成时填写）

- 根 `AGENTS.md`：不变量 #3 强化为「决策要留痕、约束要回写」，新增 #8「改动收尾必过漂移自检」，DoD 增加漂移自检勾选项
- `templates/{zh,en}/AGENTS.md.tmpl`：同步镜像（zh 编号列表 / en 项目符号，语义一致）
- `skills/project-harness/references/sync-aidoc.md`：Step 1 机械检查列为每次变更的强制收尾闸门；`skills/project-harness/references/change-docs.md`：新增「constraints are rewritten, not just noted」纪律
- 决策记录 `aiDoc/notes/implemented/process/2026-09-11-self-evolution-loop.md`、业务记忆 `aiDoc/memory/business/2026-09-11-self-evolution-loop.md` 落盘，记忆索引已更新
- 验证：`check_sync.py .` 4/4 通过；`tests/selftest.py` 全部通过（含 zh/en 镜像校验）。与计划无偏差，无遗留事项
