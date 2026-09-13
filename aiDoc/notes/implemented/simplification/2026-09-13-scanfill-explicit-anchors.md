<!-- last-updated: 2026-09-13 -->
# 决策：扫描填充改用模板显式 scan-fill 锚点

> class: simplification。关联计划：[../../../plans/completed/2026-09-13-scanfill-anchors.md](../../../plans/completed/2026-09-13-scanfill-anchors.md)

## 问题

`init_project.py` 的扫描填充按 `##` 标题文本定位小节，标题文本硬编码在脚本内的双语 `SECTION_ANCHORS` 表（zh/en 两套标题 + 一个英文变体）。模板改一个标题，脚本即失配，且此类漂移 check_sync.py 检测不到——脚本与双语言模板之间是隐性硬耦合。

## 提案 / 决策

模板小节标题行后内嵌显式标记 `<!-- scan-fill:<key> -->`（zh/en 镜像各 7 处，分布于 3 个 relations 模板），脚本按标记行定位：保留标题与标记行，替换标记之后到下一 `##` 标题之间的正文。删除 `SECTION_ANCHORS` 表；`tests/selftest.py` 新增标记 zh/en 镜像校验兜底。标记登记为契约 3 的产物标记约定，generate 校订时连同 auto-scan 标记一起移除。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| 单语言骨架 + `--lang` 只控制 generate 散文 | 方向可取但改动面大（骨架说明文字面向人类读者，中文团队直接受益）；本次先砍耦合，双模板保留，后续可再评估 |
| 保持标题文本匹配，仅补强测试 | 治标：标题改写的自由度仍被脚本锁死， bilingual 标题表仍需手工维护 |
| install 时按语言裁剪模板 | 语言是每个目标仓库的决策（init/generate 的 `--lang`），一次 user 级安装服务多仓库，安装时裁剪会破坏多仓库使用 |

## 验收标准

- [x] `init_project.py` 中无 `SECTION_ANCHORS`，定位只认 `<!-- scan-fill:<key> -->`
- [x] `python3 tests/selftest.py` 全过（含新增标记镜像检查）
- [x] `python3 skills/project-harness/scripts/check_sync.py .` exit 0

## 风险与后果

- 旧版本 skill 安装副本（copy 安装到各工具的）不含标记模板，与新脚本混用时填充会报「scan-fill 标记未找到」并跳过小节（行为降级为骨架，不破坏文件）；重新 install 即一致
- 模板作者新增需扫描填充的小节时，必须同时加标记并登记进 `_fill_specs`，否则静默跳过——selftest 的镜像检查只覆盖已登记的 7 个 key

## 交叉链接

- 契约登记：`aiDoc/contracts/boundary.md` 契约 3（标记约定）
- 实现：`skills/project-harness/scripts/init_project.py`（`_find_section` / `_fill_specs`）
