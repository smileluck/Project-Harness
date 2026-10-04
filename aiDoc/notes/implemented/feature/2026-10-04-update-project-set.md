<!-- last-updated: 2026-10-04 -->
# 决策记录：项目集更新工作流 update-set（成员索引机械刷新）

## 问题

项目集根 `AGENTS.md` 落地后，成员会增删、成员的 harness 配置状态会变化，根索引表随之漂移。用户要求一个项目集更新能力，且边界明确：更新项目集时**不更新成员 harness**——常态只是增删成员并维护成员简介；涉及多成员的功能变更才到各受影响成员仓库内按其自身 harness 更新。

## 提案 / 决策

新增 `update-set` action，脚本侧复用 `init_project_set.py` 增加 `--refresh` 模式（与 `--members`/`--all` 互斥）：

- 只重写项目集根 `AGENTS.md` 的成员索引表，绝不触碰成员目录（已配置成员不更新，新增未配置成员不自动初始化，报告提示可跑 init-set）。
- 成员索引表升级为 5 列（项目 | 路径 | 类型 | 简介 | harness 状态），简介列由 agent 校订；`--refresh` 三方合并：存续成员保留整行仅机械刷新 harness 状态列、目录消失的成员删行、新目录追加行（扫描取类型/描述，无则 TODO 占位）；兼容旧版 4 列表迁移。
- 有变化才重写（先备份到 `<set-root>/.harness-backups/` 并刷新 last-updated），无变化零写入；前置（根 AGENTS.md 缺失或 scan-fill 标记被删）不满足 exit 2。
- 校订约定调整：agent 校订根 AGENTS.md 时移除 auto-scan 标记但**保留** `<!-- scan-fill:members -->` 标记（refresh 靠它定位小节）。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| 简介写在「项目间关系与协作」散文小节，不加表列 | 用户选择表列；散文无法机械合并，refresh 只能全量重写丢失校订内容 |
| 合并进 init-set（根 AGENTS.md 已存在时自动转刷新双态） | 用户选择独立 action；双态入口语义含糊，与既有 init/update 分工不对齐 |
| 消失成员标记「疑似移除」待确认 | 用户选择自动删行；重写前有备份可回滚，报告列明删除项 |
| refresh 连类型列也机械重扫覆盖 | 类型列可能已被 agent 校订为更准确的表述；只有 harness 状态是纯机械事实，只刷它 |

## 验收标准

- [x] `python3 tests/selftest.py` 全绿（新增 `test_init_project_set_refresh` 12 项断言：前置 exit 2、增删合并、简介保留、状态列刷新、备份、不动成员目录、幂等）
- [x] /tmp fixture 端到端：zh 冒烟 + en 全流程（init-set → 增删成员 → refresh → 幂等），新增未配置成员提示跑 init-set
- [x] zh/en 模板镜像检查通过

## 风险与后果

- `--refresh` 依赖 `<!-- scan-fill:members -->` 标记定位小节；references 已明确校订时只移除 auto-scan 标记、保留 scan-fill 标记，标记被人工删除时 exit 2 并给出恢复指引。
- 根 `AGENTS.md` 仍不进 manifest 托管集（与 init-set 决策一致），`--refresh` 是其唯一机械更新通道。
- 简介列内容若含 `|`/换行会被脚本转义/折叠（`_sanitize_cell`），agent 校订时应保持单行。

## 交叉链接

- 前置决策：`aiDoc/notes/implemented/feature/2026-10-03-project-set-init.md`
- 契约：`aiDoc/contracts/boundary.md`（契约 1/2/3 均已登记）
- 工作流细则：`skills/project-harness/references/init-project-set.md`
