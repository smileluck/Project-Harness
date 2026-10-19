<!-- last-updated: 2026-10-19 -->
# 模板精简与加载层裁剪

## 问题

模板体系两处冗余：其一，记录模板（business/lessons/notes/change-plan/handoff）携带无需记录的小节——如 business 的后端/前端/cli 三分支脚手架、与文件名重复的「记录日期」、与头部 `lesson-meta` 标记重复的 lessons 状态小节；其二，L0 自动加载层（`AGENTS.md.tmpl`）承载记忆规则、留痕细则等记录类内容，每次会话全量加载，挤占上下文，而这些内容只在需要记录时才用得到。

## 提案 / 决策

1. 五个记录模板砍非必要小节：business 合并涉及范围、删记录日期；lessons 的状态类四节合并为「状态与去向」（`lesson-meta` 标记不动，仍是 `check_sync.py` 唯一机械依据）；notes 删「交叉链接」节；change-plan 十节并为七节；handoff 末节合并。
2. 骨架模板（relations/modules/contracts/frontend/examples）只压缩 TODO 脚手架注释，不动小节层级序列。
3. L0 只留项目约束 + 一行指针：删「记忆规则」固定节，不变量 3/5/6 压为指针式一行；加载模型新增「记录层（memory/notes/plans）正文不自动加载，仅路由命中时按需读写」，`aiDoc/README.md` 模板同步该规则。
4. zh/en 镜像、本仓 dogfood 实例（含 9 个 BOILERPLATE_FILES 与根 AGENTS.md）、`skills/project-harness/references/aidoc-structure.md`、`check_sync.py` 提示文案在同一变更内同步。

## 真实考虑过的备选

- 只精简记录模板、不动 L0：加载冗余是大头，不解；
- L0 完全移除记录类表述（连指针也不留）：留痕触发依赖 agent 主动查路由表，漏记风险高，故保留一行指针。

## 验收标准

- [x] `python3 tests/selftest.py` 全绿（含 zh/en 镜像、BOILERPLATE 逐字节一致、耦合校验）
- [x] `python3 skills/project-harness/scripts/check_sync.py .` 通过

## 风险与后果

- 模板小节改名（如 lessons「晋升去向」→「状态与去向」）使存量记录的节名与新模板不一致；机械扫描只读 `lesson-meta`，不受影响，存量记录不强行回填。
- 目标仓库经 update 工作流刷新后，其 AGENTS.md 的「记忆规则」节会被移除——属预期行为，记忆纪律正文在 `aiDoc/memory/README.md` 仍在。
