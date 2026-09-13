<!-- last-updated: 2026-09-11 -->
# 决策：init 默认自动接续 generate 工作流

> 路径：`aiDoc/notes/implemented/process/2026-09-11-init-auto-generate.md`

## 问题

用户提出：init 之后应自动接 generate，一次把仓库变成 agent-ready。此前 init 完成后只是"提醒并询问是否运行 generate"（init-harness.md Path A step 3），需要用户二次确认，中断了 onboarding 连贯性。

## 提案 / 决策

skill 的 `init` action 改为 `init [--no-generate]`：**默认在 init 脚本与骨架校订完成后直接接续 generate 工作流**（init 与 generate 视为同一次 onboarding）；用户明确只要骨架或传 `--no-generate` 时才停在骨架，且必须把"待运行 generate"显式列为 deferral。

要点：

- 串联写在工作流契约（references/init-harness.md）而非脚本——`init_project.py` 保持确定性职责，不新增脚本参数；`--no-generate` 是 skill 调用接口参数，由 agent 解释
- `generate-aidoc.md` 原生支持 post-init 入口（auto-scan 内容作为预探测事实），无需改动
- completion checklist 更新：默认串联时报告在 generate 完成后收口；skeleton-only 运行必须显式声明 pending 的 generate 步骤

同步面：`SKILL.md` 路由表、`skills/project-harness/references/init-harness.md`、`aiDoc/contracts/boundary.md` 契约 1、README 双语 init 行。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| 显式参数触发（`init --generate` 或独立 `bootstrap` 动作才串联） | 用户选择了默认自动串联；onboarding 的直觉就是一次到位，多问一次确认是摩擦 |
| 脚本侧加 `--then-generate` 自动跑 | 违反职责二分：generate 是 agent 语义工作流，脚本无法执行；脚本只能打印下一步提示 |

## 验收标准

- [x] SKILL.md init 行标注 `--no-generate` 与默认串联语义
- [x] init-harness.md Path A step 3 与 completion checklist 体现"默认串联、显式退出"
- [x] boundary.md 契约 1 同步；README 双语 init 行一致
- [x] `tests/selftest.py` 全过；`check_sync.py .` 4/4 通过

## 风险与后果

- 默认行为变更：只想快速搭骨架的用户会经历更长的 run；用 `--no-generate` 与显式 deferral 报告兜底
- 串联仍由 agent 按工作流契约执行，非脚本强制；各工具表现一致因为规则正文只有一份

## 交叉链接

- 前序决策：`2026-09-11-self-evolution-loop.md`、`2026-09-11-rule-evolution-lessons.md`
- 行为契约：`skills/project-harness/references/init-harness.md`、`skills/project-harness/SKILL.md`
- 接口契约：`aiDoc/contracts/boundary.md` 契约 1
