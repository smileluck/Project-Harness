<!-- last-updated: 2026-10-04 -->
<!-- lesson-meta: status=promoted count=2 post=0 target=aiDoc/README.md -->
# aiDoc 文档引用 skill 内文件用短路径导致路径真实性检查失败

## 情境

写 `aiDoc/notes/`、`aiDoc/memory/business/` 记录时引用 skill 仓库内的 references 文件。

## 坑 / 模式

把 `skills/project-harness/references/` 下的文件错写成从 references 目录直接开头的短路径——check_sync 检查 2（路径真实性）按仓库根解析行内代码路径，短路径不存在而 ❌。2026-10-03（init-set 收尾）与 2026-10-04（update-set 收尾）各犯一次，都是写完记录后由 check_sync 拦下再返工。

## 出现次数

2（2026-10-03 一次、2026-10-04 一次）

## 状态

promoted

## 晋升去向

规则写进 `aiDoc/README.md` 的「维护原则」一节：aiDoc 文档引用仓库内文件一律用仓库根相对全路径。

## 晋升后复发

0

## 记录日期

2026-10-04
