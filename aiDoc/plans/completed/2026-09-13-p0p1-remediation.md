<!-- last-updated: 2026-09-13 -->
# 变更计划：P0+P1 整改——破损修复 + 高频规则单源化

> 路径：`aiDoc/plans/completed/2026-09-13-p0p1-remediation.md`

## 目标

按 2026-09-13 架构评审结论执行整改：

1. P0：修复全部已确认的真实破损——code-index 修复路径死锁、check_sync 白名单缺口、已发生漂移的模板样板与过期索引、本仓 `.agents/skills/` 未渲染占位符。
2. P1：高频规则单源化（冲突优先级 / lessons 状态机 / code-index 生命周期 / auto-scan 标记），zh/en 镜像升级为结构级校验并修复 agents-skills 分叉，aiDoc↔模板样板一致性入测，框架关键词表单源化，脚本公共库与展示文案数据模块化。

## 非目标

- 治理哲学调整：不变量合并、DoD 合一、占位符统一、`--lang` 默认口径统一、CI（均属 P2，另行决策）
- `memory/long-term/` 沉淀流动规则
- git commit（本变更全部留在工作区，由维护者自行提交）

## 假设

- 单源化的"唯一家"只约束 skill 源与本仓文档；模板实例化副本保持自包含（注入后目标仓库没有 skill 可链接），由样板一致性检查机械兜底
- check_sync 白名单扩容会暴露本仓更多路径违规，属预期收益，当步修复
- 本仓 zh 侧为 agents-skills 结构基准（本仓工作语言为中文）

## 影响面

- `skills/project-harness/scripts/`：scan_repo.py（新 CLI 参数）、check_sync.py（白名单+argparse）、init_project.py（公共库迁移）、新增 harness_common.py、render_data.py
- `skills/project-harness/references/`：7 篇单源化与死锁话术修正
- `skills/project-harness/templates/{zh,en}/`：样板同步、agents-skills en 补齐
- 本仓 aiDoc：modules 路径修正、business 索引、relations 重生成/校订、notes 新增 2 条、contracts/boundary.md、README TODO 清理
- 根 AGENTS.md：仓库概览补 tests/、去"9 篇"硬编码计数
- `tests/selftest.py`：新增 5 组断言
- `.agents/skills/`：渲染 `<harness>` 占位符

## 验收标准

- [ ] `python3 tests/selftest.py` 全量通过（含新增断言）
- [ ] `python3 skills/project-harness/scripts/check_sync.py .` 通过（含扩容后白名单的新覆盖）
- [ ] 对 fixture 与本仓各跑一次 `scan_repo.py --write-code-index` 产物正确
- [ ] 冲突优先级 / lessons 状态机 / code-index 生命周期 / auto-scan 标记全文在 skill 源内各仅 1 处正典
- [ ] 已确认漂移（模板 memory/README、business 索引、code-index、auto-scan 残留、AGENTS.md 概览、旧 note、README TODO）全部清理
- [ ] 决策记录 2 条 + boundary.md 契约同步 + business 记忆已写

## 工作项

| # | 工作项 | owner | 依赖 | 建议写范围 | 验证命令 | 状态 |
|---|---|---|---|---|---|---|
| 1 | 立项（本计划） | main | 无 | aiDoc/plans/active/ | check_sync | 完成 |
| 2 | P0-1 scan_repo `--write-code-index` | main | 1 | scripts/scan_repo.py、selftest | selftest + 冒烟 | 完成 |
| 3 | P0-2 check_sync 白名单 + modules 路径修正 | main | 1 | scripts/check_sync.py、aiDoc/modules/ | check_sync | 完成 |
| 4 | P0-3 漂移清理批次 | main | 2 | templates、aiDoc/memory、relations、AGENTS.md、notes、README、tool-adapters | check_sync + selftest | 完成 |
| 5 | P0-4 渲染 .agents/skills | main | 1 | .agents/skills/ | grep 无 `<harness>` | 完成 |
| 6 | P1-⑤ 规则单源化 + 唯一性断言 | main | 2 | references ×6、selftest | selftest | 完成 |
| 7 | P1-⑥ 镜像结构校验 + 修 agents-skills 分叉 | main | 5 | templates/en/agents-skills、selftest | selftest | 完成 |
| 8 | P1-⑦ 样板一致性入测 | main | 4 | tests/selftest.py | selftest | 完成 |
| 9 | P1-⑧ 关键词表单源化 | main | 1 | scan_repo.py、generate-aidoc.md | selftest | 完成 |
| 10 | P1-⑨ harness_common + argparse + 拷贝合并 | main | 2,3 | scripts/ | selftest | 完成 |
| 11 | P1-⑩ render_data 数据模块 | main | 10 | scripts/ | selftest | 完成 |
| 12 | 治理收尾 + 验证 + 归档 | main | 2-11 | notes、contracts、memory、本计划 | 全量验证命令 | 完成 |

## 验证命令

```bash
python3 tests/selftest.py
python3 skills/project-harness/scripts/check_sync.py .
python3 skills/project-harness/scripts/scan_repo.py . --write-code-index --dry-check
```

（第三条为冒烟：确认重生成内容与现有 code-index 的一致性后落盘。）

## 回滚 / 迁移

纯脚本参数新增 + 文档修正，无数据迁移。回滚 = git 检出本变更前版本。`--write-code-index` 为新增能力，不破坏既有 `scan_repo.py <repo>` 调用方。

## 当前状态

已完成。全部验收标准达成：selftest 全过（含新增六组断言）、check_sync 6/6、本仓与 fixture 的 --write-code-index 冒烟通过。

## 交付摘要（完成时填写）

- 交付：
  - P0：`scan_repo.py --write-code-index [--lang]`（解 code-index 修复死锁，selftest [2b]）；check_sync 白名单扩容 + TEMPLATE/占位符豁免收窄 + OSError 保护（selftest 通过后曾拦截本次自己的决策记录短路径，闸门有效性实证）；9+3 处短路径改全路径；模板样板（memory/README zh+en）与 business 索引双记账清理；本仓 code-index 重生成；auto-scan 残留清零并校订 repo-profile/system-map；AGENTS.md 补 tests/ 行、去"9 篇"硬编码；旧 note 状态集就地刷新；aiDoc/README 两条 TODO 清理并补全路由缺口；tool-adapters 补 .claude/skills 说明；.agents/skills 的 <harness> 渲染。
  - P1：四条高频规则单源化（正典：SKILL.md/change-docs/aidoc-structure/init-harness）+ 唯一性断言；zh/en 镜像升级标题层级校验并修复 10 处结构分叉（AGENTS.md.tmpl、pre-push、code-review、module-development 全量重建等）；.agents/skills == zh 模板渲染实例断言；9 文件样板一致性入测；框架关键词表合并进 scan_repo.py（uvicorn/gorm/actix/axum/clap/servlet，Rust web/cli 与 Java servlet 组件探测落地）+ Rust fixture 用例；harness_common.py（find_git_root/read_text_relaxed）与 render_data.py（CONFIG_PURPOSE/DIR_CONVENTIONS）；check_sync argparse 化；init_project 拷贝协议统一为 _prep_dst/_walk_copy。
  - 治理：决策记录 2 条（bug-fix + simplification）、boundary.md 契约 2 更新、business 记忆 + 索引、lesson `boilerplate-dual-home-drift`（pending，1 次）。
- 与计划偏差：①"报告输出统一进公共库"评估后放弃——三脚本报告结构本质不同，强行抽象属过度设计（已记入决策记录备选表）；②模板分叉修复范围从 agents-skills 扩大到全部 31 对文件的层级对比（AGENTS.tmpl/module-development/notes/plans/boundary 等均有分叉），属同一根因的完整修复。
- 遗留事项：P2 未做（不变量合并/DoD 合一/占位符统一/--lang 口径/CI/en init 全流程测试/install.py 测试），见评审报告；lesson `boilerplate-dual-home-drift` 待第 2 次出现或用户确认后晋升。
