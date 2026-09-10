---
tool: <tool-name>
role: compatibility-adapter
canonical_source: /AGENTS.md
structured_context: /aiDoc
---

# <工具名> 规则适配层

> 通用薄适配模板：为不支持 `@import` 的工具生成适配文件时使用。
> 将 `<tool-name>` 与 `<工具名>` 替换为目标工具标识；frontmatter 字段保持不变。
> 只对**实际存在**的工具目录生成适配文件，禁止为不存在的工具硬造目录。

本文件只用于兼容 <工具名> 现有的自动加载路径。

## 真实规则入口

1. `/AGENTS.md`
2. `/aiDoc/README.md`（含「任务→必读文档」路由表，先查表再深读）
3. 路由表指向的 `/aiDoc/` 子文档

## 适配层约束

- 不要在这里扩写项目级规则
- 项目级规则变更时，先更新 `/AGENTS.md` 与 `/aiDoc/`，本文件无需改
- 工具目录只保留薄适配层职责
