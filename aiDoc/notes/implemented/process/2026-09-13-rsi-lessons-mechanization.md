<!-- last-updated: 2026-09-13 -->
# 决策：RSI 闭环机械化——lessons 扫描闸门 + 晋升后复发验证

> 路径：`aiDoc/notes/implemented/process/2026-09-13-rsi-lessons-mechanization.md`

## 问题

2026-09-11 的规则级自进化回路（不变量 #8/#9 + lessons 晋升纪律）有两个缺口：(1) lessons 晋升扫描只在 sync 工作流语义层，每个变更收尾必跑的 `check_sync.py` 看不见 lessons 状态，"第二次出现立即晋升"无机械强制力；(2) 晋升 = 规则写完即闭环，晋升后是否复发无人跟踪，规则无效时不会被发现。

## 提案 / 决策

1. lessons 文件头部引入显式机器标记 `<!-- lesson-meta: status=... count=N post=M target=... -->`，作为机械扫描的唯一依据（不解析标题文本）。
2. `check_sync.py` 新增检查 5（阻塞级：`pending` 且 `count≥2` 未晋升也未显式 `deferred`、`promoted` 缺 `target`、`status`/`count` 非法）与检查 6（提示级：缺标记、`post≥1`）。
3. 新增 `deferred` 显式暂缓状态：理由写在「晋升去向」节，sync 工作流复核其是否仍成立。
4. 晋升后复发闭环：`post` +1 → 同一变更内修订已晋升的规则正文（不再记新 lesson）+ 决策记录"第一次为什么没拦住"。
5. 联动：lesson `explicit-markers-over-heading-text` 本次第 2 次出现，按晋升纪律写入 `aiDoc/modules/architecture-rules.md` 脚本层。

同步面：`templates/{zh,en}/`（lessons TEMPLATE/README、AGENTS.md.tmpl）、`references/`（change-docs、sync-aidoc、aidoc-structure）、根 `AGENTS.md` 不变量 #9、`tests/selftest.py` fixture。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| 机械判定解析「晋升去向」标题节内容（是否填了暂缓理由） | 标题文本匹配正是待晋升 lesson 指出的反模式；双语模板标题不同，判定脆弱。改为全部机器判定只读 lesson-meta 标记 |
| 维持语义层扫描（sync 工作流 agent 人工兜底） | 2026-09-11 决策已指出纯纪律无强制力；收尾闸门看不见 lessons 意味着 pending≥2 可无限滞留 |
| 配置工具 hook 自动跑检查 | 沿用 2026-09-11 放弃理由：工具私有、无法跨工具适配 |

## 验收标准

- [x] check_sync.py 检查 5/6 按上述口径实现，docstring 同步
- [x] selftest 覆盖 4 种闸门情形 + 缺标记提示情形，全量通过
- [x] zh/en 模板镜像一致
- [x] `python3 skills/project-harness/scripts/check_sync.py .` 无漂移
- [x] 联动 lesson 晋升完成且索引同步

## 风险与后果

- 存量接入仓库的旧格式 lesson 无 meta 标记：检查 6 仅提示不 fail，不强制迁移
- lesson 标记与人读小节双写，存在不一致风险：纪律要求同步修改，语义层 review 兜底
- 不变量 #9 变长，收尾固定成本微增；机械闸门替代人工翻目录，净成本下降

## 交叉链接

- 前置决策：`aiDoc/notes/implemented/process/2026-09-11-self-evolution-loop.md`、`aiDoc/notes/implemented/process/2026-09-11-rule-evolution-lessons.md`
- 变更计划：`aiDoc/plans/completed/2026-09-13-rsi-lessons-mechanization.md`
- 规则本体：`AGENTS.md` 不变量 #9、`aiDoc/modules/architecture-rules.md` 脚本层、`aiDoc/memory/lessons/README.md`
- 行为契约：`skills/project-harness/references/change-docs.md`、`skills/project-harness/references/sync-aidoc.md`
