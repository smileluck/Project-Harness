<!-- last-updated: 2026-10-03 -->
# 决策记录：项目集（project set）批量初始化工作流 init-set

## 问题

用户常把多个独立项目放在同一个「项目集根目录」下，希望一次处理：列出全部子目录作为候选、对未配置 project-harness 的成员项目批量初始化、并在项目集根生成一个根 `AGENTS.md` 描述项目间关系，方便 AI 协调多项目。既有 init 工作流只面向单仓库，且会拒绝嵌套 git 子目录，无法覆盖该场景。

## 提案 / 决策

新增 `init-set` 工作流（SKILL.md 第六个 action），按架构二分拆分：

- **确定性逻辑** → 新脚本 `skills/project-harness/scripts/init_project_set.py`：discovery 模式（不带 `--members`/`--all` 只打印候选表，零写入）+ 批量模式（对未配置成员复用 `init_project.py` 的 `build_and_run`/`apply_scan_fill`/`write_manifest` 管线逐项目初始化），收尾在项目集根写 `AGENTS.md`，用既有 `<!-- scan-fill:members -->` 机制填成员索引表。
- **agent 行为** → 新 reference `skills/project-harness/references/init-project-set.md`：确认成员清单、逐成员接续 generate、撰写「项目间关系与协作」小节。
- **产物结构** → 新模板 `templates/<lang>/project-set/AGENTS.md.tmpl`（zh/en 镜像）。

关键设计点（与用户确认）：

- 成员识别：根目录下所有非隐藏一级子目录都列为候选，由 agent/用户确认；脚本标注 git 根 / harness 状态 / 清单文件作证据。
- 已配置成员（存在 `aiDoc/.harness-manifest.json`）完全跳过，不刷新 code-index、不跑漂移检测。
- 项目集根产物仅 `AGENTS.md`：不写根级 manifest、不建根级 `aiDoc/`；根 `AGENTS.md` 不属于任何成员的托管文件集，`update_harness.py` 不刷新它。
- 嵌套在父 git 仓库内且自身非 git 根的子目录标记 blocked 并跳过（init_project.py 会拒绝，批量场景不中断整批）。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| 项目集根建精简 `aiDoc/`（含跨项目 system-map） | 用户选择仅根 `AGENTS.md`；跨项目事实量小，单文件足够，避免第三层文档体系 |
| 只认独立 git 仓库为成员 | 用户要求列出全部子目录作候选；非 git 项目（init 仅警告不拒绝）也可被确认纳入 |
| 已配置成员刷新 code-index / 跑漂移检测 | 用户选择完全跳过；批量场景最小副作用 |
| 扩展 `init_project.py` 加 `--set` 模式 | 单脚本两套主流程会模糊单仓库/项目集边界；独立脚本复用其管线函数（内部契约已登记 boundary.md）更清晰 |

## 验收标准

- [x] `python3 tests/selftest.py` 全绿（含新增 `test_init_project_set`：discovery 零写入、未知成员 exit 2、dry-run 零写入、未配置初始化/已配置跳过/根索引表、二跑幂等、嵌套 blocked）
- [x] zh/en 模板镜像检查通过（scan-fill `members` 标记纳入 fill_targets 耦合校验）
- [x] /tmp fixture 端到端：zh（auto 探测）与 en 两套语言的真实批量初始化 + 幂等重跑 + 成员产物 check_sync 全过

## 风险与后果

- `init_project_set.py` 复用 `init_project.py` 的管线私有函数（`build_and_run`/`apply_scan_fill`/`write_manifest`/`_fill_sections`/`_prep_dst`/`make_render_ctx`/`AUTO_SCAN_MARK`），属内部契约，已在 `contracts/boundary.md` 契约 2 登记——这些签名变更须同批更新两个脚本。
- 根 `AGENTS.md` 无 manifest 基线，工具包升级不会机械刷新它；模板演进需用户手工对齐（有意取舍：根产物只有单文件）。
- 项目集根若是 git 仓库，其子目录全部 blocked——该形态（monorepo）应走单仓库 init（`mixed` 类型）而非 init-set。

## 交叉链接

- 契约：`aiDoc/contracts/boundary.md`（契约 1/2/3 均已登记）
- 业务需求：`aiDoc/memory/business/2026-10-03-project-set-init.md`
- 单项目 init：`skills/project-harness/references/init-harness.md`
