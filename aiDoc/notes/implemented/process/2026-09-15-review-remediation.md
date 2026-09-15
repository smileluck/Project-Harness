<!-- last-updated: 2026-09-15 -->
# 2026-09-15 全面评审整改：口径修正 + init 正确性 + update 下发链路

## 背景与动机

2026-09-15 四路并行全面评审（aiDoc 治理一致性 / zh-en 模板镜像 / skill 行为契约 / 脚本代码质量）产出约 50 项发现。本变更落地其中的高优先批次：文档对脚本行为的事实性失真、init_project 错误路径缺陷、update_harness 无法下发模板新增文件的结构缺口、机械产物陈旧与口径过时。

## 决策

### D1 update_harness 增加"模板新增文件"三分类处理

**备选**：(a) 仅手工补登记本仓缺的 pre-push-checks；(b) 无 manifest 时走 adopt 重建；(c) update 循环内补差集逻辑。
**取舍**：(a)(b) 只解本仓一例，不改结构缺口——旧版 init 的 manifest 永远长不出新模板文件，update 是唯一通道。选 (c)：目标不存在→写入并登记；存在且与期望一致（忽略 last-updated 行）→补登记；存在且不同→报告 new-conflict 不覆盖不登记（交语义层）。本仓 pre-push-checks 因 `<harness>` 渲染值差异（绝对路径 vs 实例的相对路径）走不进自动补登记，**手工补登记**——源仓库自身用相对路径是更优实例形态，不改渲染规则迁就。

### D2 init_project 错误路径加固

- GBK 等非 utf-8 的 .gitignore 从崩溃（UnicodeDecodeError 穿透，留半安装状态且重跑拿不到 manifest）改为 `read_text_relaxed` 容错。
- 计划记账相对路径统一 `as_posix()`（Windows 下 `str(rel)` 反斜杠破坏 FRONTEND_SKIP 匹配与扫描填充）。
- 模板解码失败降级为原样拷贝时向 stderr 打警告（原为静默，占位符生字符串泄漏进用户仓库无从排查）。
- .gitignore 去重按 `strip().strip("/")` 归一（前导/尾随斜杠变体不再重复追加）。
- `--project-name` 拒绝换行与 `|`（防注入 markdown 结构）。
- dry-run manifest 行不再显示"0 个托管文件"的误导计数。

### D3 行为契约文档对齐脚本真实能力

sync-aidoc.md findings 表原含两行脚本不存在的检查（"Stale last-updated vs code mtime"、"Missing example reference"），重写为与 check_sync 七项检查一一对应，并显式声明脚本不查示例新鲜度与文档-代码时序（那是 Step 2 语义检查）。`--scope` 枚举修正为合法集。SKILL.md 删残留的第二份参数清单（5f0ca5f 声称已消除的口径）。init 骨架产物清单不再声称含 tool adapters（脚本不写，generate 才写）。tool-adapters.md 模板路径改为实际文件名清单。"四工作流"四处口径统一为五工作流。

### D4 机械产物与登记刷新

code-index.md 以 `--lang zh` 再生成（统计 7→8 个 .py、49→58 个 aiDoc 文件、补 .github 模块）。manifest 刷新至 5f0ca5f-dirty、14 文件。**发现**：`--lang auto` 对本仓误判 en——中英双语 README 并存时拼接字符占比把中文稀释到 30% 阈值下。阈值与回退是 2026-09-13 用户确认值，未擅改；候选修法（按文件多数表决）留待用户拍板。

## 过程缺陷（已修）

新增下发循环首版用 `rel in skip_set` 过滤 frontend 文件，但 `iter_managed` 产出仓库相对形式、`FRONTEND_SKIP` 是 aidoc 树相对形式，键形式错配导致无前端仓库被下发 frontend 文件、aiDoc 计数自反馈、`--force` 不收敛。selftest 收敛断言拦截后修复（两侧归一 + adopt 循环同类错配一并修），见 lessons/2026-09-15-relpath-form-mismatch.md。

## 验证

- selftest 全过（新增 6 用例：模板新增下发/登记/冲突、无 frontend 下发拦截、收敛回归）
- check_sync 7/7 通过
- py_compile 全部脚本通过
- 本仓 update 实跑：10 文件机械刷新、11 冲突如实报告、基线校验除 boundary.md（设计内 user-modified）外全部一致

## 剩余工作（评审发现、本变更未含）

- zh/en 模板约 15 处条目级互缺（AGENTS.md.tmpl 规则互缺、notes/memory/frontend 模板互缺等）；architecture-rules.md 双语变体结构不同构
- CODE_INDEX_REL 双份定义、`_root_disp`/`_path_disp` 三份实现、`iter_managed` 与 init 写入计划双份维护
- update_harness 深度消费 init_project 下划线私有符号，未在 boundary 登记
- AUTO_SCAN_MARK 中文硬编码进 en 产物；双语字符串 40+ 处内联未进 render_data
- check_sync 白名单 CODE_TOP_DIRS 不含 `.agents`/`.github`/`.claude`；CI 无 Windows 矩阵（Windows 特有缺陷无法被 CI 发现）
- en AGENTS.md.tmpl 写死 `.trae/rules/project_rules.md` 路径
- aiDoc 单源原则残留三处双份正文（业务需求规则、lessons 触发条件、职责二分）
- detect_doc_lang 双语 README 误判（D4）
