<!-- last-updated: 2026-09-15 -->
# 项目档案（repo profile）

> 项目定位与技术栈速查。所有内容必须来自真实配置文件与代码探测，禁止编造。

## 项目定位

Project-Harness 是一个可安装的多工具通用工具包：把任意仓库变成 Agent 就绪项目（分层 AGENTS.md + aiDoc/ 文档体系 + 决策记录 + 漂移检测）。项目类型：general（无包清单文件；纯 Python 脚本 + Markdown skill 文档）。

## 核心技术栈

| 类别 | 选型 |
|---|---|
| 语言 / 运行时 | Python ≥ 3.9（仅标准库，零三方依赖） |
| 分发形态 | 目录形式 agent skill（`skills/project-harness/SKILL.md`），安装 = 拷贝/符号链接 |
| 目标工具 | 通用 agents（`~/.agents/skills/`）、Kimi Code（`~/.kimi-code/skills/`）、Claude Code（`~/.claude/skills/`）、Codex（`~/.codex/skills/`）；project 级装 `.<tool>/skills/` |
| 文档语言 | 模板双语（zh/en）；references 英文；README 双语 |

## 包管理

无（不分发为包；用户 git clone 后运行 `install.py`）。

## 核心特性

| 特性 | 说明 | 位置 |
|---|---|---|
| 五工作流 | init / generate / sync / record / update | `skills/project-harness/SKILL.md` |
| 非破坏性初始化 | 默认不覆盖、--dry-run、--overwrite 自动备份、幂等 | `skills/project-harness/scripts/init_project.py` |
| 静态扫描 | 多语言 manifest 解析 + 组件探测（混合项目）+ code-index 生成与漂移修复（`--write-code-index`） | `skills/project-harness/scripts/scan_repo.py` |
| 漂移检测 | 索引完整性/路径真实性/last-updated/区域一致性/lessons 晋升闸门 | `skills/project-harness/scripts/check_sync.py` |
| 多工具安装 | copy 或 --link，user/project 两级 | `install.py` |
