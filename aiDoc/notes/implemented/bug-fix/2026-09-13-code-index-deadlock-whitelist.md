<!-- last-updated: 2026-09-13 -->
# 决策：修复 code-index 修复路径死锁与 check_sync 白名单盲区（P0 破损修复）

> 路径：`aiDoc/notes/implemented/bug-fix/2026-09-13-code-index-deadlock-whitelist.md`
> class: bug-fix

## 问题

2026-09-13 架构评审发现两处真实破损：

1. **code-index 修复死锁**：4 处 references 指示"code-index.md 漂移时 rerun `scan_repo.py` 修复、禁止手编"，但 `scan_repo.py` CLI 只 print、从不写任何文件；唯一写入者是 `init_project.apply_scan_fill`。三条规则合起来构成死锁——文档承诺的修复路径走不通，agent 又被禁止手编。
2. **check_sync 白名单盲区**：检查 2 的 `CODE_TOP_DIRS` 只含 `src`、`app`、`tests`、`scripts` 等常见源码目录，不含 `skills`、`templates`、`references`、`aiDoc`——本仓最常用的路径前缀零校验。后果实证：`aiDoc/modules/` 下 9 处短路径引用（如 `skills/project-harness/references/aidoc-structure.md` 写成短路径）从仓库根解析并不存在，但检查全绿，形成虚假安全感。
3. 连带清理的全量已确认漂移：模板样板 `memory/README.md` 缺"与经验教训"文案（lessons 机制上线改了 dogfood 漏改模板）、`business/README.md` 索引"暂无"实际 4 条、本仓 code-index.md 过期（.py=4 实际 5）、auto-scan 标记残留 `repo-profile.md`/`system-map.md`、AGENTS.md 硬编码"9 篇"与概览缺 `tests/`、旧决策记录状态集口径未就地更新、`.agents/skills/` 残留未渲染的 `<harness>` 占位符。

## 提案 / 决策

1. `scan_repo.py` 新增 `--write-code-index [--lang zh|en]`：复用既有 `render_code_index()`，写入唯一机器产物 `aiDoc/relations/code-index.md`，打印"已重新生成/已是最新"。默认行为保持只读。
2. `check_sync.py` 白名单扩容，新增 `skills`、`templates`、`references`、`aiDoc` 四个顶层前缀；连带修两处误报源：TEMPLATE 系文件从检查 2 豁免（占位符路径如 `yyyy-mm-dd-topic.md` 不是真实引用）、行内代码含 `< > |` 的多选/占位 token 不视为路径。`check_index` 补 OSError 保护；`TEMPLATE` 豁免从子串匹配收窄为文件名精确匹配。
3. 短路径引用全部改为仓库根全路径；漂移逐项清理；`.agents/skills/` 以仓库根相对路径渲染 `<harness>`，并使 zh 模板注释改为两种渲染状态都成立的表述。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| 让 references 改口"漂移时重跑整个 init 修复 code-index" | init 会触碰全部骨架文件，为修一个机器产物付出过大的影响面；且 --overwrite 语义（备份+覆盖）对日常修复过重 |
| check_sync 短路径智能解析（按 skills/ 前缀尝试拼接） | 掩盖引用错误：文档写短路径本身就是缺陷，应修复文档而非让检查器猜 |
| 白名单保持宁缺毋滥不动 | 已实证漏掉本仓最高频路径前缀；harness 自举仓库是 check_sync 的第一等消费方 |

## 验收标准

- [x] `scan_repo.py <repo> --write-code-index` 生成含 auto-generated 头的机器产物；重复执行报告"已是最新"；`--lang en` 渲染英文标题（selftest [2b] 三断言）
- [x] 本仓 `check_sync.py .` 在扩容白名单下 6/6 通过
- [x] 短路径引用清零（全量扫描 aiDoc + AGENTS.md 无不可解析行内路径）
- [x] 模板样板与仓库实例 diff 为空；business 索引双记账消除；code-index 重生成含 tests/；auto-scan 残留清零；`<harness>` 残留清零

## 风险与后果

- `--write-code-index` 打破"扫描只读"承诺 → 文档口径改为"默认只读，唯一例外是显式 --write-code-index"，契约 2 已登记
- 白名单扩容对目标仓库可能产生新误报（引用了不存在的 `skills` 前缀路径等）→ 属预期收益方向（宁误报不漏报），发现即修文档

## 交叉链接

- 计划：`aiDoc/plans/completed/2026-09-13-p0p1-remediation.md`
- 后续重构：`aiDoc/notes/implemented/simplification/2026-09-13-single-source-dedup.md`
- 契约登记：`aiDoc/contracts/boundary.md` 契约 2
