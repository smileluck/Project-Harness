<!-- last-updated: 2026-09-13 -->
# 决策：harness 更新功能——git 版本标识 + manifest 基线 + update 工作流

> 路径：`aiDoc/notes/implemented/feature/2026-09-13-harness-update.md`

## 问题

工具包持续演进，但两层都没有更新路径：(1) install.py 重跑即删旧装新，无版本概念，无法判断"是否需要更新"；(2) init 注入目标仓库的骨架（AGENTS.md/aiDoc/模板文件）一旦生成就与模板脱钩，模板升级后存量仓库拿不到改进。

## 提案 / 决策

1. **版本标识用 git**：`harness_common.git_version()` = `git describe --tags --always --dirty`，回退 short HEAD / `unknown`；不引入 VERSION 文件（用户选定）。install.py 与 skill 脚本共用此单源实现。
2. **安装层**：copy 安装把版本写入标识文件；已装版本一致则 SKIP 不删重装；新增 `--check` 只报告各目标版本（全部最新 exit 0，有旧版/未安装 exit 1）；`--link` 恒视为最新。
3. **产物层**：init 收尾写 `aiDoc/.harness-manifest.json`（版本 + 每个本次写入文件的 sha256 基线 + 模板相对路径）；新脚本 `update_harness.py` 逐文件判定——基线一致（项目未改）→ 刷新为「模板渲染 + 扫描填充 + 引用裁剪」的期望内容（先备份）；基线不一致（项目已改）→ 跳过交 generate/sync 语义合入；项目已删不复活；模板已删首版不自动删项目文件。无 manifest 的旧仓库走 adopt 只建基线。
4. **工作流层**：SKILL.md 新增 `update` action + `skills/project-harness/references/update-harness.md`（机械刷新 → 语义合入 → check_sync 收尾）。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| 显式 VERSION 文件 + 语义化版本号 | 用户选定 git 标签/提交为版本；零维护成本，dirty 后缀天然区分开发中改动 |
| update 时自动删除模板已移除的文件 | 安全模型不可回退：删除项目文件不可逆，首版只报告保留 |
| 用 git 三方合并更新产物文件 | 目标仓库产物非 git 子模块，无共同祖先可参考；哈希基线 + 分类报告更简单且确定 |

## 验收标准

- [x] install.py：同版本 SKIP / 旧版 UPDATE / `--check` 退出码正确（selftest `test_install` 覆盖）
- [x] init 产物 manifest 字段齐全、基线哈希与产物一致、code-index 不登记
- [x] update：同版本短路、`--force` 收敛（末轮 0 刷新）、项目改动跳过且内容保留、模板变更触发刷新、adopt 只建基线不登记已改文件、`--dry-run` 零写入（selftest `test_update_flow` 12 项断言）
- [x] 本仓库自身 adopt 建基线，`check_sync.py .` 全绿

## 风险与后果

- adopt 的「忽略 last-updated 行比对」是近似判定；宁可误判为"已改"（跳过）也不误刷，与安全模型方向一致
- 版本为 `unknown`（skill 脱离仓库拷贝）时：install 回退总是 UPDATE，update 无短路只按哈希判定——行为可预期
- 并行协作事故：开发中未跟踪的 update_harness.py 被并行 agent 的提交工作流抹掉一次，已记 lesson `2026-09-13-untracked-files-vs-concurrent-agents.md`

## 交叉链接

- 变更计划：`aiDoc/plans/completed/2026-09-13-harness-update.md`
- 契约：`aiDoc/contracts/boundary.md` 契约 1/2/3
- 行为契约：`skills/project-harness/references/update-harness.md`
- 相关 lesson：`aiDoc/memory/lessons/2026-09-13-untracked-files-vs-concurrent-agents.md`
