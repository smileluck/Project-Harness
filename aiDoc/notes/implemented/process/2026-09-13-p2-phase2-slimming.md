<!-- last-updated: 2026-09-13 -->
# 决策：P2 阶段二——占位符/`--lang` 口径统一与不变量 9→6 合并

> 路径：`aiDoc/notes/implemented/process/2026-09-13-p2-phase2-slimming.md`
> class: process

## 问题

P2 阶段一（见 `2026-09-13-p2-phase1-guard-cleanup.md`）因并行会话碰撞暂停后，update 工作流已落地（3c0f639），剩余两项续作：① `${KIMI_SKILL_DIR}` 与 `<skill-dir>` 两种路径写法并存、脚本级参数对使用者不可见、`--lang` 在 references 宣称"跟随仓库文档语言"而脚本硬编码默认 zh（承诺与实现不一致）；② 操作不变量 9 条中 3 对是同一件事的两个侧面、不变量 9 单条 5 行内嵌机械扫描细节（L0 不再 L0）、DoD 与 boundary/module-dev 三份完成清单互相重叠。

## 提案 / 决策（用户已确认合并映射）

1. **占位符统一**：SKILL.md 与 init-harness.md 的 `${KIMI_SKILL_DIR}` 写法废除，统一 `<skill-dir>`（Kimi 变量降为括号附注）；SKILL.md 路由表 init 行注明脚本级参数见 `--help`（不做参数清单的第二份维护）。
2. **`--lang auto`**：`harness_common.detect_doc_lang()`（读 AGENTS.md/README 系列各前 20000 字符，CJK 占比 >30% 判 zh，否则 en，无文档回退 zh——用户确认的阈值）；init_project / scan_repo `--write-code-index` / update_harness 三处 `--lang` 默认改为 auto（update 的优先级：显式参数（含 auto 探测）> manifest 登记值 > zh），init 输出"文档语言: auto（探测为 X）"；boundary 契约 2、SKILL.md、generate-aidoc.md 口径同步。
3. **不变量 9→6**（映射表，无一删除只有合并）：

| 旧 | 新 |
|---|---|
| 1 一个事实一个维护家 / 2 规则不进工具私有目录 | 保留为 1 / 2 |
| 3 决策留痕+约束回写 + 4 多步骤计划 | 合并为 3「变更要留痕」 |
| 5 证据按影响面 + 6 报告区分状态 | 合并为 4「证据与报告纪律」 |
| 7 交接要完整 | 保留为 5 |
| 8 漂移自检 + 9 lessons 入库（机械细节下沉 lessons/README 正典） | 合并为 6「收尾双闸门」 |

4. **DoD 唯一化**：DoD 为唯一完成定义；boundary/module-dev 完成清单删去与 DoD 重叠的镜像/契约同步项，只留领域特有条并注明归属；zh/en AGENTS.md.tmpl 的不变量与 DoD 同构合并（en 版顺带补齐缺失的"交接要完整"条）。目标仓库模板不含 harness 专属的"zh/en 模板镜像"DoD 项（实例化差异，有意为之）。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| AGENTS.md 压缩到 ≤85 行（方案估算值） | 实际合并后 119 行——不变量正文承载的内容未删除，强行砍行数只会牺牲仓库概览/路由等真实信息；以"6 条不变量 + 三清单零重叠"为验收口径，放弃行数 KPI |
| detect_doc_lang 放进 scan_repo | 它是文档语言策略（init/update/scan 三方消费），属公共工具，放 harness_common |
| update 的 auto 覆盖 manifest | 显式 auto 是用户当场选择，应优先于历史登记值 |

## 验收标准

- [x] 全仓（SKILL/references）无 `${KIMI_SKILL_DIR}` 独立写法（仅存一处括号附注）
- [x] selftest [2j]：英文 README→en、中文 README→zh、显式 `--lang en` 覆盖探测
- [x] AGENTS.md 不变量 = 6，zh/en 模板镜像（结构级校验）全绿
- [x] boundary 契约 2 三行 `--lang auto|zh|en` 登记
- [x] selftest 全量通过、check_sync 7/7

## 风险与后果

- auto 探测在"中英混排 README"依赖 30% 阈值，边界项目可能误判 → 显式 `--lang` 恒可覆盖；阈值在 boundary 契约 2 明示
- 不变量合并后旧编号引用（历史 notes/plans 中的"不变量 #9"）指向失效 → 历史档案不改写；新文档一律用不变量名不用编号

## 交叉链接

- 前置：`aiDoc/notes/implemented/process/2026-09-13-p2-phase1-guard-cleanup.md`
- 计划：`aiDoc/plans/completed/2026-09-13-p2-governance-slimming.md`
- 正典落点：`AGENTS.md`（不变量/DoD）、`skills/project-harness/scripts/harness_common.py`（detect_doc_lang）
