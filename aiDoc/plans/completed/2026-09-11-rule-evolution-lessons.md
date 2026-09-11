<!-- last-updated: 2026-09-11 -->
# 变更计划：规则自进化回路（lessons 经验层 + 晋升机制）

## 目标

建立「经验 → 约束」的自进化回路：新增 `aiDoc/memory/lessons/` 采集层；AGENTS.md 新增不变量 #9 强制捕获；「第二次出现即晋升约束层」纪律；sync 工作流兜底扫描；skill record 增加 lesson 子动作。toolkit 与本仓库自身同步落地。

## 非目标

- 不配置工具 hook；不改 check_sync.py / init_project.py 脚本逻辑
- 不改变 notes/plans 既有生命周期与分类

## 假设

- init_project.py 整树拷贝模板，新增 lessons 模板文件自动分发（已核实）
- check_sync.py 区域列表是顶层 area，memory/lessons 不影响（已核实）

## 影响面

- skill 调用接口契约：record action 增加 lesson → 同步 `aiDoc/contracts/boundary.md`
- 模板产物契约：zh/en 新增 memory/lessons/ 两文件 → selftest 镜像校验必须全绿
- aiDoc 结构契约：references/aidoc-structure.md、harness-model.md

## 验收标准

- [ ] zh/en 模板严格镜像（selftest [3] 通过）
- [ ] 本仓库 aiDoc 与根 AGENTS.md 同步落地不变量 #9 与 lessons 层
- [ ] `python3 tests/selftest.py` 全过；`check_sync.py .` 4/4 通过
- [ ] 决策记录、变更计划、业务记忆三类留痕齐备

## 工作项

| # | 工作项 | owner | 依赖 | 建议写范围 | 验证命令 | 状态 |
|---|---|---|---|---|---|---|
| 1 | zh/en lessons 模板新建 | agent | 无 | `skills/project-harness/templates/{zh,en}/aidoc/memory/lessons/` | selftest [3] | 完成 |
| 2 | zh/en 既有模板更新 | agent | 1 | `templates/{zh,en}/` 下 memory/README、aidoc/README、AGENTS.md.tmpl | selftest | 完成 |
| 3 | references + SKILL.md | agent | 1 | `skills/project-harness/references/`、`SKILL.md` | 目视 | 完成 |
| 4 | 本仓库 aiDoc 同步 | agent | 1-3 | `AGENTS.md`、`aiDoc/` | check_sync | 完成 |
| 5 | 留痕（note/memory/plan 归档） | agent | 4 | `aiDoc/notes/`、`aiDoc/memory/`、`aiDoc/plans/` | check_sync | 完成 |

## 验证命令

```bash
python3 tests/selftest.py
python3 skills/project-harness/scripts/check_sync.py .
```

## 回滚 / 迁移

纯文档与模板变更，git revert 即可；已生成 lessons 的目标仓库不受影响（模板只影响新 init/generate）。

## 当前状态

已完成。

## 交付摘要（完成时填写）

- 新增 `aiDoc/memory/lessons/` 采集层（本仓库 + zh/en 模板各 README/TEMPLATE，共 6 文件）
- 根 `AGENTS.md` 新增不变量 #9「踩坑与反复模式必须入库」，zh/en 模板镜像
- 晋升纪律入 `references/change-docs.md`；sync 兜底扫描入 `references/sync-aidoc.md` Step 2；结构契约入 `aidoc-structure.md`、`harness-model.md`
- skill 契约扩展 `record [note|plan|handoff|lesson]`，`aiDoc/contracts/boundary.md` 已同步
- 本仓库 `aiDoc/README.md`、`memory/README.md`、`project-memory.md` 索引与路由表同步
- 留痕：决策记录 `notes/implemented/process/2026-09-11-rule-evolution-lessons.md`、业务记忆 `memory/business/2026-09-11-rule-evolution-lessons.md`
- 验证：`tests/selftest.py` 全部通过（含 zh/en 镜像、init 产物 check_sync）；`check_sync.py .` 4/4 通过。与计划无偏差，无遗留事项
