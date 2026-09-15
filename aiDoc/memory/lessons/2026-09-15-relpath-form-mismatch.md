<!-- lesson-meta: status=pending count=1 post=0 target= -->
<!-- last-updated: 2026-09-15 -->
# 跨常量做键匹配前先核对两侧路径形式

## 现象

为 update_harness.py 新增"模板新增文件下发"循环时，用 `rel in skip_set` 过滤无前端仓库的 frontend 文件。`iter_managed()` 产出**仓库相对**形式（带 `aiDoc/` 前缀），而 `FRONTEND_SKIP` 常量是 **aidoc 树相对**形式（不带前缀），判断永远不匹配：无前端 fixture 被 update 下发了 2 个 frontend 文件，进而 aiDoc 文件计数自反馈增长，`--force` 两轮不收敛。selftest 的收敛断言当场拦截。

## 根因

同一"相对路径"概念在仓库里有两种基准（仓库根 vs templates/<lang>/aidoc/），常量定义处未标注基准，新代码凭直觉假设了基准。

## 修法

- 匹配前显式归一：`aidoc_rel = rel[len("aiDoc/"):] if rel.startswith("aiDoc/") else rel`，并用注释写明两侧形式（update_harness.py 两处循环已修）。
- 复发预防：新增跨常量键匹配时，先 grep 常量定义处确认形式；带形式注释。

## 晋升去向

若再次出现"路径/键形式基准错配"类缺陷，晋升为 module-development.md 的规则：跨模块共享的路径常量必须注释其相对基准。
