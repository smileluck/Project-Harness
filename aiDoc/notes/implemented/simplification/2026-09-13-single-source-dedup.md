<!-- last-updated: 2026-09-13 -->
# 决策：高频规则单源化与镜像结构机械化（P1 去冗余重构）

> 路径：`aiDoc/notes/implemented/simplification/2026-09-13-single-source-dedup.md`
> class: simplification

## 问题

评审证实"一个事实一个维护家"在高频规则上被系统性违反：冲突优先级 skill 源内 3 处全文展开、lessons 晋升纪律 ≥6 处、code-index 生命周期 4 处完整重述、auto-scan 标记重复且被 selftest"≥2 次"断言制度化。zh/en 模板镜像校验只查文件清单+占位符计数，agents-skills 等模板已结构性分叉（pre-push zh 5 节 vs en 3 节；module-development en 是残缺桩）却测不出。脚本层存在 find_git_root 逐字重复、拷贝协议两份实现、约 300 行双语展示文案住在逻辑层。

## 提案 / 决策

1. **单源化手术**：每条高频规则在 skill 源内只留一个全文正典，其余一句话+链接——冲突优先级正典 `SKILL.md`；lessons 状态机正典 `change-docs.md`；code-index 生命周期正典 `aidoc-structure.md`（含新的 `--write-code-index` 命令）；auto-scan 标记全文仅 `init-harness.md`。模板实例化副本保持自包含（注入后目标仓库没有 skill 可链接），属设计意图，由样板 diff 校验机械兜底。
2. **唯一性断言入 selftest**：四条正典的特征串断言全 skill 源内恰出现 1 次；auto-scan 标记断言从"≥2"改为"恰 1 次且在正典文件"。
3. **镜像升级结构级校验**：zh/en 每对文件比对标题层级序列（跳过代码块，语言差异归一化）；新增断言"本仓 `.agents/skills/` == zh 模板 `<harness>/`→空串渲染实例（逐字节）"。
4. **样板一致性入测**：9 个固定样板文件（memory/business/notes/plans 的 README 与 TEMPLATE）断言仓库实例 == 模板（剥离首行 last-updated 后逐字节相等）；排除含仓库自维护索引区的文件（lessons/README、project-memory）。
5. **关键词表单源化**：`generate-aidoc.md` 的框架关键词表删除，唯一维护点移入 `scan_repo.py` 常量，并合并两表差异（补 uvicorn/gorm/actix/axum/clap/servlet，Rust web/cli 与 Java servlet 组件探测随之落地）。
6. **脚本公共库与数据模块**：新建 `harness_common.py`（`find_git_root`/`read_text_relaxed` 唯一实现）；`render_data.py`（`CONFIG_PURPOSE`/`DIR_CONVENTIONS` 双语文案表）；`check_sync.py` 补 argparse（repo_path 默认 `.`，兼容既有调用）；`init_project` 两段 os.walk 合并为 `_walk_copy`、拷贝协议统一为 `_prep_dst`。
7. **模板分叉修复**：en 侧补齐 10 处结构分叉（AGENTS.md.tmpl 路由两子节、pre-push 5 步、code-review 输出模板、module-development 全量重建、memory/README 边界节、architecture-rules 注册节、notes/plans 模板结构、boundary 变体嵌套）；zh business/TEMPLATE 补 CLI 小节。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| 报告输出格式化也统一进公共库 | 三脚本的报告结构本质不同（Plan 分组 vs 检查项 vs 扫描摘要），强行抽象是过度设计；只抽真正逐字重复的部分 |
| 双语表头常量也迁入 render_data | 每个表头只用一次，迁移只增加间接层不减重复；只迁真正双家维护的数据表 |
| 模板实例化副本也改链接（彻底单源） | 注入目标仓库后无 skill 可链接，自包含是注入模型的硬约束；用机械 diff 校验替代人工纪律是可达的最优解 |
| 镜像校验直接比对全文（翻译对齐） | 机器翻译对齐不可靠；标题层级序列已能拦截全部已发现的结构分叉，误报率低 |

## 验收标准

- [x] 四条正典特征串在 skill 源内各恰 1 处（selftest [5] 唯一性组全绿）
- [x] zh/en 31 对文件标题层级序列一致（selftest [4] 结构镜像）
- [x] `.agents/skills/` == zh 模板渲染实例（selftest [4b]）
- [x] 9 个样板文件仓库实例与模板一致（selftest [5b]）
- [x] Rust axum/clap fixture 探测为 web-backend/cli（selftest [2c]）
- [x] `python3 tests/selftest.py` 与 `check_sync.py .` 全过

## 风险与后果

- 唯一性断言锚定特征串，规则改写措辞时需同步断言 → 断言只锚定稳定特征（优先级链、marker 字面量、CLI 参数名），改写常规措辞不触发
- 结构镜像按层级对比，同层级标题增删仍需人工保证语义对应 → 层级+数量已拦截已知分叉模式，语义级对齐留给 review
- check_sync argparse 化后无参数默认检查当前目录 → 与 references 的显式 `<repo-root>` 调用兼容，`--help` 退出码 0

## 交叉链接

- 计划：`aiDoc/plans/completed/2026-09-13-p0p1-remediation.md`
- 前置修复：`aiDoc/notes/implemented/bug-fix/2026-09-13-code-index-deadlock-whitelist.md`
- 正典位置：`skills/project-harness/SKILL.md`（冲突优先级）、`skills/project-harness/references/change-docs.md`（lessons）、`skills/project-harness/references/aidoc-structure.md`（code-index）、`skills/project-harness/references/init-harness.md`（auto-scan）、`skills/project-harness/scripts/scan_repo.py`（关键词表）
- 契约登记：`aiDoc/contracts/boundary.md` 契约 2（内部模块）
