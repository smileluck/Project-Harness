<!-- last-updated: 2026-09-13 -->
# 变更计划：P2 治理减负与保障补盲

> 路径：`aiDoc/plans/active/2026-09-13-p2-governance-slimming.md`

## 目标

P0+P1 之后完成第三阶段：治理强度与对象规模校准（不变量 9→6、DoD 唯一化）、使用摩擦消除（占位符/`--lang` 口径统一）、保障盲区归零（测试盲区补齐 + CI 上线）、aiDoc/README 收敛与路由机械闸门、遗留清理包。

## 非目标

- 不重构 references 按需加载架构（网状引用是合理复用）
- 不动 lessons 晋升机制本身（只消除索引双记账）
- 不引入三方依赖

## 已拍板决策（2026-09-13 用户确认）

1. 不变量 9→6 合并映射：认可
2. update_harness.py：删除并清理引用
3. lessons 索引：project-memory 唯一索引
4. CI 矩阵：ubuntu × Python 3.9/3.11/3.12（3 job）
5. generic-adapter.md：删除
6. `--lang auto` 阈值：中文字符占比 >30% 判 zh

## 影响面

- `tests/selftest.py`（六组新用例）、`.github/workflows/selftest.yml`（新增）
- `skills/project-harness/scripts/`：init_project.py（--lang auto、引用清理、detect_components 拆分）、scan_repo.py（--lang auto）、check_sync.py（去重修正、检查 7）、harness_common.py（detect_doc_lang）
- `skills/project-harness/references/`：change-docs.md（索引降为 3 处）、generate-aidoc.md（指针化）、SKILL.md（占位符、参数可见性）
- `skills/project-harness/templates/{zh,en}/`：AGENTS.md.tmpl（不变量合并）、aidoc/README.md（删目录说明表）、lessons README（删索引节）、adapters/generic-adapter.md（删除）
- 根 `AGENTS.md`、`aiDoc/README.md`、`aiDoc/contracts/boundary.md`
- 删除 update_harness 悬案文件（scripts 目录下未跟踪文件，见决策点 2）

## 验收标准

- [ ] selftest 全量通过（含六组新用例），CI 配置文件入库
- [ ] check_sync 通过（含新检查 7：常用入口完整性）
- [ ] AGENTS.md 不变量 = 6 条、三份完成清单零重叠、模板镜像同步
- [ ] 全仓无 `${KIMI_SKILL_DIR}`；`--lang` 默认 auto 且中英 fixture 探测正确
- [ ] update_harness.py、generic-adapter.md（zh/en）删除且无残留引用
- [ ] lessons 索引仅存 project-memory 一处

## 工作项

| # | 工作项 | owner | 依赖 | 验证 | 状态 |
|---|---|---|---|---|---|
| 1 | WS-C1 selftest 六组新用例 | main | 无 | selftest | 完成 |
| 2 | WS-C2 CI 上线 | main | 1 | push 后 Actions 绿 | 完成（待 push 首跑） |
| 3 | WS-E1 update_harness 删除 | main | 无 | grep 无引用 | 已失效（被并行 update 工作流实现取代） |
| 4 | WS-E2 lessons 索引唯一化 | main | 无 | check_sync + selftest | 完成 |
| 5 | WS-E3 generic-adapter 删除 | main | 无 | selftest 镜像 | 完成 |
| 6 | WS-E4 检查 2 去重修正 | main | 无 | check_sync | 完成 |
| 7 | WS-E5 detect_components 拆分 | main | 1 | selftest 标签断言 | 完成 |
| 8 | WS-E6 adaptivity 指针化 | main | 无 | selftest | 完成 |
| 9 | WS-B1 占位符统一 | main | 无 | grep | 暂停（SKILL.md 与并行会话冲突） |
| 10 | WS-B2 --lang auto | main | 1 | selftest 用例 | 暂停（init_project/harness_common 冲突） |
| 11 | WS-D1 README 四表收敛 | main | 无 | check_sync + selftest | 完成 |
| 12 | WS-D2 检查 7 入口完整性 | main | 11 | check_sync + 负例 | 完成 |
| 13 | WS-A1 不变量合并 + DoD 唯一化 | main | 1-12 | check_sync + selftest | 暂停（AGENTS.md 与并行会话冲突） |
| 14 | 治理收尾 + 归档 | main | 1-13 | 全量验证 | 阶段一已留痕；归档待 WS-A/B 完成 |

## 验证命令

```bash
python3 tests/selftest.py
python3 skills/project-harness/scripts/check_sync.py .
python3 -m py_compile skills/project-harness/scripts/*.py install.py tests/selftest.py
```

## 回滚 / 迁移

纯文档 + 测试 + 配置新增，无数据迁移。回滚 = git revert。CI 文件删除即下线。

## 当前状态

**阶段一完成，WS-A/WS-B 暂停待续。** 执行中发现另一会话在相同工作树并行实现 update 工作流（update_harness.py + references + SKILL.md 路由 + manifest 基线），与本计划 WS-A/WS-B 的目标文件重叠；本会话曾按过时决策删除其未跟踪脚本（已由对方重建，lesson 已记）。处置：只完成冷文件上的剩余工作（WS-D 全部 + 留痕），不 commit（避免收编对方半成品），WS-A/WS-B 待 update 工作流落地后续作并 reconcile（含 init_project 两处"供未来"措辞的口径修正）。

阶段一验证：selftest 全部通过（含并行方 [3u] 用例共存）、check_sync 7/7、脚本编译全过。

## 交付摘要（完成时填写）

阶段一交付（详见 `aiDoc/notes/implemented/process/2026-09-13-p2-phase1-guard-cleanup.md`）：CI 上线（ubuntu × 3.9/3.11/3.12）、selftest 六组新用例、mixed fixture 修正、check_index `../` 解析修复、模板 code-index 死锁话术修正、lessons 索引唯一化、generic-adapter 删除、检查 2 去重修正、detect_components 拆分（8 检测器 + 编排）、README 四表收敛与模板字典补全、检查 7 常用入口完整性 + 负例。剩余：WS-A（不变量 9→6 + DoD 唯一化）、WS-B（占位符统一 + --lang auto）。
