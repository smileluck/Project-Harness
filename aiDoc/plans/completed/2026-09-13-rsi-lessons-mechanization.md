<!-- last-updated: 2026-09-13 -->
# 变更计划：RSI 回路机械化——lessons 扫描闸门 + 晋升后复发闭环

> 路径：`aiDoc/plans/completed/2026-09-13-rsi-lessons-mechanization.md`

## 目标

把 2026-09-11 规则级自进化回路补成完整 RSI 闭环：lessons 晋升纪律从纯语义层下沉为 `check_sync.py` 机械闸门（检查 5/6），并新增晋升后复发验证环节。

## 非目标

- `memory/long-term/` 沉淀流动规则
- 规则退役/降噪机制
- 跨仓库 lessons 统计与回顾仪表盘

## 假设

- 存量接入仓库的 lessons 可能无 meta 标记，机械扫描对其只提示、不 fail

## 影响面

- `skills/project-harness/scripts/check_sync.py`（新增检查）、`tests/selftest.py`（新 fixture）
- `templates/{zh,en}/`：lessons TEMPLATE/README、AGENTS.md.tmpl
- `skills/project-harness/references/`：change-docs.md、sync-aidoc.md、aidoc-structure.md
- 本仓库 aiDoc：lessons TEMPLATE/README/现有 lesson、architecture-rules.md、根 AGENTS.md、memory 索引

## 验收标准

- [x] check_sync.py 检查 5/6 落地：pending≥2 未处理 ❌、promoted 缺 target ❌、deferred ✅、缺标记 ⚠️
- [x] selftest 新增 lessons 闸门 fixture 且全量通过
- [x] zh/en 模板镜像一致（selftest 覆盖）
- [x] lesson explicit-markers-over-heading-text 完成第 2 次出现的晋升（architecture-rules.md 脚本层）
- [x] `python3 skills/project-harness/scripts/check_sync.py .` 全过

## 工作项

| # | 工作项 | owner | 依赖 | 建议写范围 | 验证命令 | 状态 |
|---|---|---|---|---|---|---|
| 1 | lessons TEMPLATE 加 lesson-meta 标记 | main | 无 | templates/{zh,en}/aidoc/memory/lessons/、aiDoc/memory/lessons/ | selftest 镜像项 | 完成 |
| 2 | check_sync.py 检查 5/6 | main | 1 | scripts/check_sync.py | selftest [3] | 完成 |
| 3 | 纪律文档与 references 同步 | main | 1、2 | lessons README ×3、references ×3 | check_sync | 完成 |
| 4 | lesson 联动晋升 | main | 1 | architecture-rules.md、lesson 文件、索引 ×2 | check_sync | 完成 |
| 5 | 不变量 #9 + 模板镜像 | main | 2 | AGENTS.md、templates/{zh,en}/AGENTS.md.tmpl | selftest 镜像项 | 完成 |
| 6 | selftest fixture | main | 2 | tests/selftest.py | `python3 tests/selftest.py` | 完成 |
| 7 | 留痕（plan/note/business） | main | 1-6 | aiDoc/plans、notes、memory | check_sync | 完成 |

## 验证命令

```bash
python3 tests/selftest.py
python3 skills/project-harness/scripts/check_sync.py .
```

## 回滚 / 迁移

纯文档 + 单脚本新增检查，无数据迁移；回滚 = git revert 本变更。存量仓库旧格式 lesson 仅提示不拦截，无需迁移。

## 当前状态

已完成。全部验收标准达成，验证命令通过。

## 交付摘要（完成时填写）

- 交付：lessons 头部 `lesson-meta` 显式标记（zh/en 模板 + 本仓库实例）；`check_sync.py` 检查 5/6 机械闸门；`deferred` 暂缓状态与晋升后复发（`post`）闭环纪律写入 lessons README ×3 与 references ×3；lesson `explicit-markers-over-heading-text` 第 2 次出现并晋升至 `architecture-rules.md` 脚本层；不变量 #9 与 zh/en 模板同步；selftest 新增 5 项闸门断言（全绿）。
- 与计划偏差：机械判定从「解析晋升去向节内容」细化为「全部只读 lesson-meta 标记」——避免标题文本匹配（正是本次晋升的 lesson 所禁止的反模式），且双语模板下更稳健。
- 遗留事项：`memory/long-term/` 沉淀流动、规则退役机制、跨仓库回顾统计，列入后续候选。
