<!-- last-updated: 2026-09-11 -->
# 决策：规则自进化回路——lessons 经验层 + 晋升机制

> 路径：`aiDoc/notes/implemented/process/2026-09-11-rule-evolution-lessons.md`

## 问题

架构约束（`modules/architecture-rules.md` 等）此前只在"人提出/决策发生"时更新。多次开发中反复出现的模式、踩过的坑没有采集点，也不会自动提炼回约束层。缺三段机制：采集（踩坑当下无低成本记录入口）、提炼（无"何时把经验升格为规则"的纪律）、兜底（无定期扫描未晋升经验的环节）。

## 提案 / 决策

建立「经验 → 约束」自进化回路，核心原则：**一次是经历，两次是模式**。

1. **采集层**：新增 `aiDoc/memory/lessons/`（README + TEMPLATE，对齐 business/ 结构），5 行轻量模板：情境 / 坑或模式 / 出现次数 / 状态（pending/promoted/dropped）/ 晋升去向。
2. **捕获规则**：AGENTS.md 新增不变量 #9——踩坑、review 反复同类问题、可复用模式必须同一变更内记 lesson，同类再犯就地累加次数。
3. **晋升纪律**：同一 lesson 第 2 次出现或用户确认时，同一变更内把规则写进约束正文所在文档（architecture-rules.md / boundary.md / frontend-rules.md / AGENTS.md），lesson 标 promoted 并交叉链接；dropped 须写理由；涉及行为/架构/契约变化仍按不变量 #3 写决策记录。
4. **兜底**：sync 工作流 Step 2 新增 lesson 扫描——`pending` 且次数 ≥2 的条目在本次 sync 内晋升或标注理由。
5. **契约**：skill `record` action 扩展为 `[note|plan|handoff|lesson]`，同步 `aiDoc/contracts/boundary.md`。

同步面：SKILL.md、references（change-docs / sync-aidoc / aidoc-structure / harness-model）、templates zh/en（新建 lessons 4 文件 + memory/README、aidoc/README、AGENTS.md.tmpl 三处更新）、本仓库 aiDoc 与根 AGENTS.md。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| 轻量版：只在 notes/plans 模板加「模式候选」字段，sync 时批量提炼 | 捕获能力弱——够不上"决策"级别的坑永远不会被记录，提炼环节无米下锅；用户场景是"多次开发中反复出现"，需要独立低成本采集点 |
| 脚本化自动提炼（脚本扫描 lessons 自动改约束文档） | 违反「脚本做确定性的事，agent 做语义的事」职责二分；晋升判断是语义行为，不能自动化 |
| 工具 hook 触发 | 前一决策已否决：工具私有、无法跨工具适配 |

## 验收标准

- [x] 不变量 #9 落入根 AGENTS.md 与 zh/en 模板（selftest 镜像校验通过）
- [x] `aiDoc/memory/lessons/` 与模板侧 4 文件齐备，索引（project-memory.md）含 lessons 区
- [x] references 四篇与 SKILL.md、boundary.md 契约同步
- [x] `tests/selftest.py` 全过；`check_sync.py .` 4/4 通过

## 风险与后果

- 每次收尾成本略升；用「5 行模板 + 第二次出现才晋升」控制
- 晋升仍是规则强制而非机器拦截；靠不变量 #8 漂移自检 + sync 扫描双兜底
- 目标仓库存量 aiDoc 无 lessons 目录时，generate/sync 工作流负责补齐（references 已含结构契约）

## 交叉链接

- 前序决策：`aiDoc/notes/implemented/process/2026-09-11-self-evolution-loop.md`（强制漂移自检 + 决策回写约束）
- 变更计划：`aiDoc/plans/completed/2026-09-11-rule-evolution-lessons.md`
- 规则本体：`AGENTS.md` 不变量 #9、`aiDoc/memory/lessons/README.md`
