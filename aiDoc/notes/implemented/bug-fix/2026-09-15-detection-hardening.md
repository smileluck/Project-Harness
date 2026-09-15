<!-- last-updated: 2026-09-15 -->
# 2026-09-15 检测体系加固与 manifest 基线生命周期修复

## 问题

用户要求全方位审阅项目（结构 / 输入输出 / 机制 / 检测）。三方向并行审阅（含 fixture 实测）发现两个高危缺陷与一批检测盲区，核心主题：① manifest 基线的生命周期管理有缺陷；② 检测体系存在结构性盲区——检测器自身无负例回归、机械一致性校验锁死合法分化、内容级漂移不可见。

## 提案 / 决策

按批准的「全量修复 H+M+低成本 L」方案落地：

1. **H1 manifest 基线保护**：`init_project.write_manifest` 合并未重写文件的旧基线条目（保留旧哈希而非按现内容重算，不掩盖 user_modified 判定；剔除已不存在文件），重跑 init 不再清空基线。selftest 增加二跑基线保留断言与「SKIP 文件保留旧哈希」断言。
2. **H2 TODO 锁死解耦**：本仓 `.agents/skills/project-pre-push-checks` 填入真实验证命令（py_compile + selftest）；selftest test 4b 改为「无 TODO 文件逐字节锁定；含 TODO 模板要求实例已解析且标题结构镜像」；check_sync 新增检查 8（`.agents/skills` 残留 `TODO:`，提示级）。
3. **M1 口径统一**：报告分类以 `skills/project-harness/references/quality-workflow.md` 五类（passed/failed/skipped/unavailable/not-run）为正典，回写根 AGENTS.md、zh/en AGENTS.md.tmpl、code-review/pre-push skill（模板 zh/en + 本仓实例）、handoff.TEMPLATE（三处）。
4. **M2**：`scan_repo.list_files` 改为 `git ls-files --cached --others --exclude-standard`，覆盖未跟踪但未忽略文件（init 典型场景「代码未提交」不再漏扫）。
5. **M3/M6**：selftest 补 check_sync 检查 2 负例（断言明细输出而非仅标题/退出码）、SKILL.md→references 链接存在性校验。
6. **M4**：check_sync 新增检查 9——manifest 基线 vs 托管文件现内容 sha256 比对（提示级），内容级漂移在 pre-push 出口可见。
7. **M5**：lessons 闸门——glob 改递归（子目录纳入）、`post` 非数字列提示（不再静默逃逸）、补 status/count 非法分支负例。
8. **M7**：install.py——link 安装以 copy 模式重跑可切换回独立副本；copytree 排除 `__pycache__`/`*.pyc`。
9. **M8**：双语 README 补 update 工作流行与完整 scripts 清单（保持镜像）。
10. **L 项**：boundary.md 登记 update→init 私有管线耦合与 install.py `--project-dir`/codex 限制；AGENTS.md 概览补 `.agents/skills/`、`.github/` 行；development-workflow.md 登记 CI 与 check_sync 命令；`.gitignore` 加 `.zcode/`；`git_version` 超时路径改为 continue 回退；scan_repo 的 render_data 导入加兜底。
11. **本仓 manifest 重建基线**：本仓 manifest 是 H1 既有受害者（仅 14 项、AGENTS.md 等未登记、boundary.md 哈希陈旧），用 `update_harness.iter_managed` 一次性按当前内容重建基线（24 项，frontend 区域本仓不存在故跳过）。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| H1 改为「对所有现存托管文件重算哈希」 | 会把用户改过的 SKIP 文件重基线，掩盖 update_harness 的 user_modified 判定；保留旧哈希才符合基线语义 |
| H2 中 check_sync 的 TODO 检查设为阻塞级 | init 刚完成的仓库合法存在待填 TODO，阻塞级会让「产物 check_sync 全过」恒红；提示级 + 自检锁本仓实例足够 |
| check 9（manifest 比对）设为阻塞级 | update 正当刷新后与 generate 语义合入之间存在合法窗口期，阻塞会误伤；先提示级观察 |
| M2 仅在 docstring 说明「只覆盖已跟踪文件」 | 文档说明不能修复 init 主场景的系统性漏扫，直接补扫成本同样低 |
| 给 update_harness 加 `--rebaseline` 正式参数 | 本次只需一次性修复本仓基线；是否产品化等出现第二个受害者再议 |

## 验收标准

- [x] `python3 -m py_compile install.py skills/project-harness/scripts/*.py tests/selftest.py` 通过
- [x] `python3 tests/selftest.py` 全部通过（新增断言：基线保留、SKIP 保留旧哈希、未跟踪文件扫描、检查 2 负例、manifest 漂移提示、lessons 三负例 + 子目录、SKILL.md 链接校验、link→copy 切换、copy 无 __pycache__）
- [x] `python3 skills/project-harness/scripts/check_sync.py .` 9/9 通过 0 提示（含本仓 manifest 重建基线后检查 9 转绿）

## 风险与后果

- check_sync 检查项 7 → 9（新增 8/9 均提示级，不影响退出码）；references/sync-aidoc.md 的检查清单描述需同步
- 含 `TODO:` 的 agents-skills 模板在目标仓库会触发检查 8 提示，直至 generate/init 填写真实命令——这是设计意图（机械闸门兜底 references/init-harness.md 的 TODO 解析契约）
- 本仓 manifest 基线重建后，未来对托管文件的任何改动都会触发检查 9 提示，需在收尾时甄别「有意改动 → 重建基线」与「无意漂移 → 修复」
- 未修项（记录在案，本批不动）：dry-run 裁剪记账混入 created、探测深度一层、依赖子串匹配误判、install 其他工具路径无测试、update 版本降档无警告、`<harness>` 绝对路径移动失效、CI 单平台、last-updated 不查新鲜度

## 交叉链接

- 审阅计划：`~/.kimi-code/sessions/.../plans/bobbi-morse-devil-dinosaur-doctor-mid-nite.md`（会话内）
- 前一轮评审整改：`aiDoc/notes/implemented/feature/2026-09-13-harness-update.md`、`aiDoc/memory/business/2026-09-15-full-review-remediation.md`
- 业务记录：`aiDoc/memory/business/2026-09-15-detection-hardening-review.md`
- lesson：`aiDoc/memory/lessons/2026-09-15-detector-efficacy-blind-spots.md`
