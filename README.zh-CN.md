# Project-Harness

[English](README.md) | **中文**

把任意仓库变成 **Agent 就绪的项目**：分层 `AGENTS.md` 指令、结构化 `aiDoc/` 文档体系、持久化决策记录、变更计划、交接文档、项目级审查 skill、文档漂移检测——以可安装 skill 的形式接入你已经在用的 Agent 工具。

## 为什么

一个 `AGENTS.md` 文件有帮助，但它不是完整的协作系统。重度使用 Agent 的项目还需要：

- 现状事实的维护家园（架构、契约、模块规则）
- 决策的持久化依据（包括被否决的备选方案）
- 进行中工作的执行状态（计划、交接）
- 按需加载的情境化工作流（审查、pre-push 检查）
- 以及检测文档与代码漂移的手段

Project-Harness 把这一切打包成一个带确定性脚本的可安装 skill，支持 Kimi Code、Claude Code、Codex 及任何扫描 `.agents/skills/` 的工具。

## Harness 模型

五层协作，一个事实一个维护家：

| 层 | 目标仓库中的位置 |
|---|---|
| 常驻指令 | 根 `AGENTS.md`（子树规则确实不同时才用嵌套 `AGENTS.md`） |
| 现状文档 | `aiDoc/`（relations、modules、contracts、frontend、examples、memory） |
| 决策记录 | `aiDoc/notes/<proposed\|implemented\|rejected>/<class>/` |
| 执行状态 | `aiDoc/plans/active/` → `completed/`，交接文档 |
| 工作流 skill 与可执行证据 | `.agents/skills/`、聚焦检查（`check_sync.py`），穷举矩阵归 CI |

冲突优先级：`AGENTS.md` > `aiDoc/README.md` > aiDoc 子文档 > 工具适配文件。工具私有目录只放薄指针，绝不复制规则正文。

## 安装

要求：Python 3.9+（仅标准库）。

```bash
git clone <本仓库地址>
cd Project-Harness

# 把 skill 安装到你的 agent 工具（用户级）
python3 install.py --tool agents    # ~/.agents/skills/（Kimi Code 及其他识别 .agents 的工具）
python3 install.py --tool kimi      # ~/.kimi-code/skills/
python3 install.py --tool claude    # ~/.claude/skills/
python3 install.py --tool codex     # ~/.codex/skills/
python3 install.py --tool all       # 以上全部

# 选项：--scope project（装进当前仓库）、--link（符号链接，仓库更新即时生效）、--dry-run
```

## 四个工作流

在 agent 中调用 skill（如 Kimi Code：`/skill:project-harness <参数>`）：

| 命令 | 作用 |
|---|---|
| `init` | 非破坏性骨架初始化：探测项目类型/技术栈，拷贝 `AGENTS.md` + `aiDoc/` 骨架，默认绝不覆盖（支持 `--dry-run`、`--overwrite` 自动备份、幂等）。成熟仓库走 gap audit，只补缺失件。 |
| `generate [--incremental\|--scope <区域>\|--dry-run] [--lang zh\|en]` | Agent 驱动：探测代码库并基于真实代码撰写 `AGENTS.md` + `aiDoc/` 内容——分层规则、API 契约、示例、路由表。支持增量与局部再生成。 |
| `sync` | 漂移检测：`check_sync.py` 校验索引完整性、引用路径、`last-updated` 头部、区域一致性；agent 再处理语义漂移。 |
| `record [note\|plan\|handoff]` | 按生命周期纪律创建决策记录 / 变更计划 / 交接（不编造备选方案；implemented 就地更新；推翻旧决策新建交叉链接 note）。 |

## 目标仓库会得到什么

```
<目标仓库>/
├── AGENTS.md                # L0 唯一真源：规则、操作不变量、DoD、路由
├── CLAUDE.md                # 仅一行：@AGENTS.md
├── aiDoc/
│   ├── README.md            # L1 路由：索引、任务→必读路由表、信息归属表
│   ├── relations/           # 仓库画像、开发流程、系统地图
│   ├── modules/             # 架构与模块组织规则、模块开发指南
│   ├── contracts/           # 契约层：web-api / library / cli 变体
│   ├── frontend/            # 前端规范、工具复用（仅前端项目生成）
│   ├── examples/            # 各层讲解型示例
│   ├── memory/              # 长期偏好 + 业务需求记录
│   ├── notes/               # 决策记录：<生命周期>/<分类>/yyyy-mm-dd-主题.md
│   └── plans/               # 变更计划（active/completed）+ 交接
├── .agents/skills/
│   ├── project-code-review/       # 语义审查清单 + 证据选择
│   └── project-pre-push-checks/   # 最小可信出口检查
└── 工具薄适配文件            # 只对已存在的工具目录生成（.trae、.cursor、copilot 等）
```

## 安全模型

- 默认初始化**绝不覆盖**已有文件；已存在的目标报 `SKIP`
- `--overwrite` 先把被替换文件备份到 `aiDoc/.harness-backups/<timestamp>/`
- 初始化器拒绝在已有 Git 仓库的子目录运行
- 无法验证的事实留下可见 `TODO` 标记——工具包绝不编造命令或技术栈细节
- 规则正文只在 `AGENTS.md` + `aiDoc/`；工具目录只有薄适配指针

## 仓库结构

```
Project-Harness/
├── install.py                    # 多工具安装器（copy 或 symlink）
└── skills/project-harness/       # 完整 skill；安装 = 拷贝此目录
    ├── SKILL.md                  # 入口路由：init / generate / sync / record
    ├── references/               # 工作流细则（harness 模型、aiDoc 契约、质量、协作……）
    ├── templates/zh/  templates/en/   # 注入目标仓库的双语骨架
    └── scripts/
        ├── init_project.py       # 非破坏性脚手架
        └── check_sync.py         # 机械漂移检查
```

## 致谢

设计改编并泛化自：

- [generate-aidoc](https://github.com/smileluck/SmileX-Fastapi-Cloud/blob/main/.claude/commands/generate-aidoc.md) — aiDoc 分层文档生成工作流
- [dsh-project-harness](https://github.com/Pytorchlover/dsh-project-harness) — 五层 harness 模型、决策记录、变更计划、团队协作、与改动面成比例的证据
- [Harness_Handbook](https://github.com/Ruhan-Wang/Harness_Handbook) — 面向 agent 导航的代码库手册（灵感来源；重量级 LLM 流水线有意不纳入）

## 许可证

[MIT](LICENSE)
