<!-- last-updated: 2026-09-10 -->
# 开发流程（development workflow）

> 本仓库的日常开发、验证与提交规范。命令在仓库根目录执行。

## 环境与依赖

| 目的 | 命令 |
|---|---|
| 安装 skill 到工具 | `python3 install.py --tool agents\|kimi\|claude\|codex\|all [--link]` |
| 语法检查 | `python3 -m py_compile install.py skills/project-harness/scripts/*.py tests/selftest.py` |
| 脚本自测 | `python3 tests/selftest.py`（fixture 端到端 + zh/en 镜像 + 耦合校验，零依赖） |

## 推荐开发顺序

1. 判归属：确定性逻辑 → `skills/project-harness/scripts/`；agent 行为 → `skills/project-harness/references/`；产物结构 → `skills/project-harness/templates/`（zh/en 同步改）
2. 改脚本后跑 `python3 tests/selftest.py`（覆盖 init 多类型 + check_sync + 幂等 + dry-run + 嵌套 git + overwrite 备份）
3. 改模板后跑一遍 init 确认产物 check_sync 全过
4. 改 references/SKILL.md 后校验 frontmatter（name/description 齐全）与交叉引用路径
5. 涉及对外契约的变更同步 `aiDoc/contracts/boundary.md`

## 契约两侧协作

本仓库的"消费方"是**安装了 skill 的 agent**与**被初始化的目标仓库**。脚本 CLI、模板占位符、aiDoc 产物结构任一变更，都要同时检查：references 中的工作流描述、模板引用、check_sync 的检查逻辑三处是否仍然一致。

## 分支策略

- `main`：可发布状态
- 功能分支按需，直接合入 main

## 提交规范

`type(scope): description`，type ∈ feat / fix / refactor / docs / test / chore。历史示例：`feat: initial Project-Harness toolkit ...`、`fix: close drift-detection gaps ...`。
