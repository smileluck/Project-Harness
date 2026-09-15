<!-- last-updated: 2026-09-13 -->
# 决策：P2 阶段一——保障补盲、CI 上线与清理包（含并行会话碰撞处置）

> 路径：`aiDoc/notes/implemented/process/2026-09-13-p2-phase1-guard-cleanup.md`
> class: process

## 问题

P0+P1 后仍存三类缺口：① 保障盲区——`--lang en` 从未走过 init 全流程、`--no-scan` 与 install.py 零测试、组件探测无标签断言（实证：名为 mixed 的 fixture 因缺依赖从未真正判成 mixed）、无 CI；② 遗留摩擦——lessons 索引双记账、检查 2 全局去重吞定位信息、detect_components 186 行单函数、adapters 孤儿模板；③ aiDoc/README 四张同构表且"文档登记路由"纯靠自觉（P0 曾实证漏登记）。

## 提案 / 决策

按用户确认的六个决策点执行 P2，顺序"保障先行"：

1. **WS-C 保障**：selftest 新增六组用例（[2d] 标签断言——并修正 mixed fixture 补 react 依赖使其真判 mixed、[2e] en 全流程、[2f] --no-scan、[2g] frontend 裁剪、[2h] check_sync 负例、[2i] install.py 含临时 HOME 重定向）；CI 上线 `.github/workflows/selftest.yml`（ubuntu × Python 3.9/3.11/3.12，3.9 覆盖 tomllib 正则回退路径）。
2. **WS-C 连带修复**：check_index 对 `../` 引用按 aiDoc/ 目录解析（en 模板 README 的合法链接形式，此前被误判为仓库根相对）；模板 code-index.md 的死锁话术改为内联 `--write-code-index` 真实命令。
3. **WS-E 清理**：lessons 索引唯一化到 project-memory（repo + zh/en 模板三处索引节删除，aidoc-structure 指针同步）；generic-adapter.md（zh/en）删除；检查 2 去重改按 (文件, 路径)；detect_components 拆分为 8 个 `_detect_*` 检测器 + 编排（行为字符串逐字保留，标签断言护航）；generate-aidoc 的 adaptivity "short version" 改纯指针。
4. **WS-D 收敛**：三份 README 删「目录说明」表（4 表 → 3 表，信息归属表吸收）；模板字典补全 memory 三条目并清过时 TODO；check_sync 新增**检查 7 常用入口完整性**——文档型 aiDoc .md（各区域 README + 五个核心区域直接子文档）必须在 README 字典登记，未登记 exit 1，"文档入库 = 路由登记"从纪律变闸门。
5. **update_harness 决策被取代**：原定"删除并清理引用"在执行后发现该文件是另一并行会话进行中的 update 工作流实现（已在重建），按被取代处理；并行碰撞细节见 lesson。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| WS-A/WS-B（不变量合并、--lang auto）同批执行 | 与并行会话的活跃文件（SKILL.md/AGENTS.md/init_project/harness_common）重叠，继续编辑会互相覆盖；暂停待 update 工作流落地后 reconcile |
| 检查 7 覆盖全部 aiDoc .md | notes/plans 是档案区、examples 分层示例有自己的索引（examples/README），全量覆盖会产生大量误报；收敛到"区域 README + 五核心区直接子文档" |
| 碰撞后继续全量 P2 并提交 | 工作树含并行会话半成品，commit 会再次收编对方未完成改动（f638fa1 已发生过一次）；改为只做冷文件 + 不提交 |

## 验收标准

- [x] selftest 全量通过（新增六组 + [3u] 并行方用例共存）
- [x] check_sync 7/7 通过（含检查 7 与负例测试）
- [x] CI 配置入库待 push 激活
- [x] mixed fixture 真判 mixed（label 断言锁定）
- [x] lessons 索引仅存 project-memory；generic-adapter 无残留
- [ ] WS-A/WS-B 暂停待续（另见计划文档）

## 风险与后果

- CI 首跑在 push 后发生，矩阵配置未实测（纯 stdlib + git，预期低风险）
- 检查 7 对目标仓库新增登记义务，init 产物由模板字典保证满足；存量仓库升级后需补登记（发现即修）
- P2 未完成项（WS-A 不变量合并、WS-B --lang auto/占位符统一）与并行 update 工作流的 reconcile 待续作

## 交叉链接

- 计划：`aiDoc/plans/completed/2026-09-13-p2-governance-slimming.md`（未归档，WS-A/B 待续）
- 碰撞 lesson：`aiDoc/memory/lessons/2026-09-13-untracked-files-vs-concurrent-agents.md`
- 前置：`aiDoc/notes/implemented/bug-fix/2026-09-13-code-index-deadlock-whitelist.md`、`aiDoc/notes/implemented/simplification/2026-09-13-single-source-dedup.md`
