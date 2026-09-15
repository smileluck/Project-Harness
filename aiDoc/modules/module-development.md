<!-- last-updated: 2026-09-13 -->
# 模块开发指南（module development）

> 本仓库的"新功能"通常是：新工作流、新脚本能力、新模板区域、新工具适配。先判归属，再动手。

## 新增/修改脚本能力（如 scan 新语言支持）

1. 改 `skills/project-harness/scripts/scan_repo.py`（或对应脚本），保持零依赖与安全模型。
2. 在 /tmp 建 fixture 实测：正例（能探测）+ 反例（不误判）+ 幂等。
3. 同步 `skills/project-harness/references/` 中描述该能力的文档（如探测矩阵表）。
4. 若改了产物结构（新增/删除生成文件），同步 `skills/project-harness/templates/{zh,en}`、`check_sync.py` 检查逻辑、`skills/project-harness/references/aidoc-structure.md` 三处。

## 新增工作流（references 新篇）

1. 在 `skills/project-harness/references/` 新建英文文档，相对路径交叉引用。
2. 在 `SKILL.md` 路由表登记（一行说明 + 链接）。
3. 若工作流产生新的 aiDoc 区域，先改 `skills/project-harness/references/aidoc-structure.md` 的目录契约，再改模板。

## 新增/修改模板区域

1. `skills/project-harness/templates/zh/` 与 `skills/project-harness/templates/en/` 同改，保持文件清单与结构镜像。
2. 若新增条件性区域，同步 `init_project.py` 的跳过/裁剪逻辑与 `check_sync.py` 的 `AIDOC_SECTIONS`。
3. 跑一遍 init 确认产物 `check_sync.py` 全过。

## 完成前检查

- [ ] `python3 -m py_compile` 全部脚本通过
- [ ] /tmp fixture 实测（至少正例 + 幂等 + dry-run）
- [ ] references 交叉引用路径真实存在

（zh/en 镜像与契约同步属根 `AGENTS.md` Definition of Done，此处不重复。）

## 真实参考文件

- `skills/project-harness/scripts/scan_repo.py`（探测器范式：解析器函数 + 组件判定 + 报告）
- `skills/project-harness/scripts/init_project.py`（安全模型范式：Plan 分组报告 + _copy_file + 备份）
- `skills/project-harness/references/generate-aidoc.md`（工作流文档范式：模式表 + 阶段流程 + 验证节）
