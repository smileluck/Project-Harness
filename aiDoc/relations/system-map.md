<!-- last-updated: 2026-09-13 -->
# 系统地图（system map）

> 组件关系与调用链速查。

## 根目录职责

| 目录 | 职责 |
|---|---|
| `skills/project-harness/` | 完整 skill：SKILL.md 入口 + references/ + templates/ + scripts/ |
| `aiDoc/` | 本仓库自身的 AI 协作文档层 |
| `tests/` | 自检脚本 `selftest.py`（init/scan/check_sync 行为 + 脚本↔模板↔文档耦合契约） |
| `.agents/skills/` | 本仓库自身的预置 skill（代码审查、推送前检查；zh 模板的渲染实例） |
| `install.py` | 多工具安装器（copy/symlink 到各工具 skills 目录） |
| `README.md` / `README.zh-CN.md` | 双语入口文档 |
| `CLAUDE.md` | 仅一行 `@AGENTS.md` |

## 分层调用关系

```
用户 agent（Kimi Code / Claude Code / Codex）
  └─ SKILL.md（路由 init/generate/sync/record）
       ├─ references/*.md          # agent 行为契约（语义层）
       └─ scripts/                 # 确定性底座
            ├─ init_project.py ──调用──> scan_repo.py
            │        └─ 拷贝并渲染 templates/{zh,en}/
            └─ check_sync.py      # 对目标仓库产物做机械校验
```

单向依赖：references 指引 agent 调用 scripts；scripts 读取 templates；反向不存在。

## 模块对应关系

| 能力 | 入口 | 核心文件 |
|---|---|---|
| init（骨架+扫描） | `init_project.py: main` | `scan_repo.py`（探测）、`skills/project-harness/templates/`（骨架） |
| sync（漂移检测） | `check_sync.py: main` | 目标仓库的 AGENTS.md + aiDoc/ |
| 安装 | `install.py: main` | 工具路径映射表 |

## 配置文件

| 文件 | 用途 |
|---|---|
| （无项目级配置文件） | 全部配置通过 CLI 参数传入；脚本零配置 |
