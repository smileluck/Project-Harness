---
tool: cursor
role: compatibility-adapter
canonical_source: /AGENTS.md
structured_context: /aiDoc
---

# Cursor 规则适配层

本文件只用于兼容 Cursor 现有的自动加载路径。

## 真实规则入口

1. `/AGENTS.md`
2. `/aiDoc/README.md`（按变更范围选读）
3. 受影响的 `/aiDoc/` 文档或章节

## 适配层约束

- 不要在这里扩写项目级规则
- 项目级规则变更时，先更新 `/AGENTS.md` 与 `/aiDoc/`，本文件无需改
- 工具目录只保留薄适配层职责
