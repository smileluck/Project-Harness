<!-- last-updated: 2026-11-17 -->
# aiDoc

## 按变更范围查阅

从 `AGENTS.md` 和任务涉及的代码开始。需要定位代码、确认约束或按规定留痕时，按下表选读。长文档先用标题、路径或符号定位相关段落。范围扩大时补读新增影响面的约束。

| 变更范围 | 需要时查阅 |
|---|---|
| 局部修复 / 文案调整 / 内部重构 | 先读相关代码和最近的测试。触及下列约束时再查对应条目 |
| 新增模块、调整分层或依赖方向 | `modules/architecture-rules.md` 对应层或组件；需要接入步骤时查 `modules/module-development.md` |
| 需要某一层的写法示例 | 从 `examples/README.md` 定位该层示例 |
| API、公共类型、CLI 或跨组件行为变化 | 从 `contracts/boundary.md` 定位受影响契约，核对生产方与消费方。跨多个边界时逐一查阅 |
| 定位入口 / 组件 / 命令 | 搜索 `relations/code-index.md`；需要组件关系时查 `relations/system-map.md` |
| 项目定位 / 技术栈 | `relations/repo-profile.md` |
| 构建 / 部署 / 提交 | `relations/development-workflow.md` 对应章节 |
| 记录业务需求或踩坑 | 业务需求查 `memory/business/README.md`；经验查 `memory/lessons/README.md`。在记忆索引中按主题搜索并定点更新 |
| 非平凡决策 / 复杂变更 / 交接 | 按实际需要查 `notes/README.md`、`plans/README.md` 或 `plans/handoff.TEMPLATE.md` |
| 代码审查 | `../.agents/skills/project-code-review/SKILL.md` |
| 推送前检查 | `../.agents/skills/project-pre-push-checks/SKILL.md` |

## 常用入口

| 文档 | 用途 |
|---|---|
| `relations/repo-profile.md` | 项目定位与技术栈速查 |
| `relations/development-workflow.md` | 开发流程、提交规范、环境命令 |
| `relations/system-map.md` | 系统架构与组件关系 |
| `relations/code-index.md` | 组件清单、语言构成、入口点、命令索引（机器生成，不手改） |
| `modules/architecture-rules.md` | 架构各层必须遵守的约束 |
| `modules/module-development.md` | 新建模块/功能/命令的完整步骤 |
| `contracts/boundary.md` | 共享约定与按接口面查找契约的入口 |
| `examples/README.md` | 讲解型示例的阅读入口 |
| `memory/README.md` | 记忆层总览与使用规则 |
| `memory/long-term/README.md` | 长期稳定偏好的沉淀规则 |
| `memory/business/README.md` | 业务需求记录规则（索引唯一维护于 project-memory.md） |
| `memory/project-memory.md` | 记忆层索引 |
| `memory/lessons/README.md` | 经验记录的捕获与晋升纪律 |
| `notes/README.md` | 决策记录的分类与维护纪律 |
| `plans/README.md` | 变更计划的生命周期与何时需要计划 |

## 维护原则

- 按代码入口、组件或契约面维护路由。根索引登记一级入口，契约分册在 `contracts/boundary.md` 登记，记录按本区域的维护规则入索引。
- 新增、删除或移动文档时同步其入口；事实变更时就地更新对应正文。
- 本仓 aiDoc 的行内代码路径从仓库根写起，供 `skills/project-harness/scripts/check_sync.py` 核对。
