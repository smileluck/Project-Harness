<!-- last-updated: 2026-09-10 -->
# 架构与模块组织规则（architecture rules）

> 范式：工具包（skill bundle + 零依赖脚本层）。所有规则引用真实代码位置。

## 总原则

- **确定性归脚本，语义归 agent**：能被机械判定/生成的逻辑必须进 `skills/project-harness/scripts/`；需要代码理解的写进 `skills/project-harness/references/` 由 agent 执行。禁止在 references 里写"用脚本实现的步骤"，也禁止在脚本里写需要语义判断的逻辑。
- **一个事实一个维护家**：aiDoc 目录契约只在 `references/aidoc-structure.md`；探测/扫描逻辑只在 `scan_repo.py`；他处只引用。

## 脚本层（`skills/project-harness/scripts/`、`install.py`）

- 零三方依赖、Python 3.9+ 兼容（注意 `tomllib` 需 3.11+ fallback）。
- 安全模型不可回退：默认不覆盖已存在文件、`--dry-run` 零写入、`--overwrite` 先备份、嵌套 git 拒绝、幂等。
- 无法探测的信息留可见 `TODO` 或 `auto-scan` 标记，**禁止编造**。
- 入口统一 `main(argv)` + `if __name__ == "__main__": sys.exit(main())`，退出码 0/1/2 语义见 `aiDoc/contracts/boundary.md`。

## Skill 层（`SKILL.md` + `references/`）

- `SKILL.md` 只做路由与不变量，不展开流程细节；流程细节的唯一维护点是对应 `references/*.md`。
- references 之间用相对路径交叉引用；英文撰写；指令性风格（must/should/never）。
- frontmatter 必须显式含 `name` 与 `description`（Kimi Code 目录形式硬性要求）。

## 模板层（`templates/zh/` + `templates/en/`）

- 两套**严格镜像**：文件清单一致、占位符（`{{PROJECT_NAME}}`/`{{DATE}}`）一致、小节结构一致。改一侧必须同步另一侧。
- 模板是骨架不是内容：项目特定内容一律 TODO 占位 + `auto-scan` 标记约定，不写具体技术栈。
- 条件性区域只有 `frontend/`；其余区域全类型生成，内容由 generate 按范式适配。

## 错误处理约定

- 参数错误/前置条件不满足（嵌套 git、模板缺失）→ 退出码 2 + stderr 中文报错。
- 检查类脚本（check_sync）发现失败项 → 退出码 1；目标缺 AGENTS.md/aiDoc → 退出码 2。
