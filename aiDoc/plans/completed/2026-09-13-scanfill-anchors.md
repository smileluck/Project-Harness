<!-- last-updated: 2026-09-13 -->
# 变更计划：scan-fill 显式锚点 + references 冗余单源化

## 目标

- `init_project.py` 的扫描填充不再按 `##` 标题文本定位小节，改为模板内置 `<!-- scan-fill:<key> -->` 显式标记；删除双语 `SECTION_ANCHORS` 硬编码表。
- references 中三处复述（语义校验清单、Operating invariants、报告纪律）单源化；清理 generate-aidoc.md 迁移残留措辞与 aidoc-structure.md 的组件模型复述。
- selftest 新增 scan-fill 标记 zh/en 镜像校验。

## 非目标

- 不砍 zh/en 双模板（保留，仅砍脚本与双模板的耦合）。
- 不给 install.py 加语言参数；不改 `--lang` 参数语义与默认值（zh）。
- 不动 SKILL.md 四工作流划分；不改 scan_repo.py。
- 不改变扫描填充填入的内容本身（仅改定位机制）。

## 假设

- 填充目标仅为 3 个 relations 模板中的 7 个小节（positioning/stack/pkgmgmt/features/env/rootdirs/config），无其它调用方依赖 `SECTION_ANCHORS`。
- 骨架中保留 scan-fill 标记无害，generate 校订时连同 auto-scan 标记一起移除。

## 影响面

- 脚本：`skills/project-harness/scripts/init_project.py`（定位机制）
- 模板：zh/en 各 3 个 relations 模板（契约 3 产物结构新增标记约定）
- references：sync-aidoc.md、generate-aidoc.md、harness-model.md、aidoc-structure.md
- 测试：tests/selftest.py 新增耦合校验
- 契约文档：aiDoc/contracts/boundary.md 契约 3

## 验收标准

- [x] `python3 tests/selftest.py` 全过（含新增标记镜像检查）
- [x] `python3 skills/project-harness/scripts/check_sync.py .` exit 0
- [x] `init_project.py` 中无 `SECTION_ANCHORS`；模板改标题不影响填充
- [x] 语义校验清单正文只在 sync-aidoc.md；重复 invariants 只在 SKILL.md

## 工作项

| # | 工作项 | owner | 依赖 | 建议写范围 | 验证命令 | 状态 |
|---|---|---|---|---|---|---|
| 1 | 6 个 relations 模板加 scan-fill 锚点（zh/en 镜像） | main | — | templates/{zh,en}/aidoc/relations/ | grep 标记计数 | 完成 |
| 2 | init_project.py 改标记定位、删 SECTION_ANCHORS | main | 1 | scripts/init_project.py | selftest | 完成 |
| 3 | selftest.py 加 scan-fill 镜像校验 | main | 1 | tests/selftest.py | selftest | 完成 |
| 4 | references 单源化与措辞清理 | main | — | references/*.md | check_sync | 完成 |
| 5 | 治理：notes/lesson/boundary/索引/last-updated | main | 1-4 | aiDoc/ | check_sync | 完成 |

## 验证命令

```bash
python3 tests/selftest.py
python3 skills/project-harness/scripts/check_sync.py .
```

## 回滚 / 迁移

全部为新增标记 + 文档改写 + 删除一张查找表；git 回滚即可，无持久数据迁移。

## 当前状态

全部工作项完成，验证通过（2026-09-13）。

## 交付摘要（完成时填写）

实际交付与计划一致，无偏差：

- 6 个 relations 模板（zh/en 镜像）内嵌 7 个 `<!-- scan-fill:<key> -->` 锚点；`init_project.py` 改为按标记定位（保留标题与标记行，替换标记后正文），删除 `SECTION_ANCHORS` 与不再使用的 `import re`
- `tests/selftest.py` 耦合校验新增 scan-fill 标记 zh/en 镜像检查（7 key × 2 语言各出现一次）
- references 单源化：语义校验清单收敛至 sync-aidoc.md Step 2（generate 改为引用 + 仅保留 "No invented facts"）；harness-model.md 重复 invariants 改为指向 SKILL.md；报告纪律在 generate/sync 中改为指向 quality-workflow.md
- 措辞清理：删除 generate-aidoc.md 的 "former --scope backend/frontend" 与 "legacy six-type detection" 迁移残留；aidoc-structure.md 组件模型复述收敛为指向 generate Phase 1.4
- 治理：本计划 + 决策记录 `notes/implemented/simplification/2026-09-13-scanfill-explicit-anchors.md` + lesson `memory/lessons/2026-09-13-explicit-markers-over-heading-text.md`（pending）；`contracts/boundary.md` 契约 3 登记 scan-fill 标记约定；memory 两处索引同步

验证：passed — `python3 tests/selftest.py` 全部通过（含新检查）；真实 fixture init 确认 7 个小节均按标记填充成功；`python3 skills/project-harness/scripts/check_sync.py .` 4 通过 0 失败。failed：无。not-run：无。

遗留事项：旧 copy 安装的 skill 副本与新脚本混用时填充会跳过小节（降级为骨架，不破坏文件），重新 install 即一致——已记入决策记录风险节。
