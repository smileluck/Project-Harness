<!-- last-updated: 2026-11-17 -->
<!-- lesson-meta: status=pending count=1 post=0 target= -->
# 升级前用存量产物验证 manifest 结构

## 情境

在 EGO 平台预览 harness 更新时，`update_harness.py` 把字符串哈希条目当成对象读取，升级预览中止。

## 坑 / 模式

用当前 init 产物测 update 会漏掉旧仓库里的格式差异。版本字段和文件哈希也无法证明旧基线来自模板。迁移需用真实旧格式验证预览、正式接管和定制文档保留。

## 出现次数

1 次。样本使用旧版裸哈希条目。

## 状态与去向

pending。处理契约见 [更新流程](../../../skills/project-harness/references/update-harness.md)。
