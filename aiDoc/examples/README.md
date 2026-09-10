<!-- last-updated: 2026-09-10 -->
# 示例层

`aiDoc/examples/` 是讲解型示例层，告诉 AI 每一层应该按什么标准组织和书写。

## 用途

- 示例不是要求逐字复制，而是展示项目标准的代码组织方式
- 当 AI 需要新增某一层文件时，应先阅读对应示例
- 示例代码必须从项目真实代码中提取，禁止凭空编写

## 示例阅读顺序

本仓库规模小，未生成独立示例文件；以下真实文件即各层标准范式，按此顺序阅读：

1. `skills/project-harness/SKILL.md` — skill 入口范式（frontmatter + 路由表 + 不变量）
2. `skills/project-harness/scripts/scan_repo.py` — 探测器范式（解析器 + 组件判定 + 报告）
3. `skills/project-harness/scripts/init_project.py` — 安全模型范式（Plan 分组报告、备份、幂等）
4. `skills/project-harness/scripts/check_sync.py` — 检查器范式（Report 类 + 逐项检查 + 退出码）
5. `skills/project-harness/references/generate-aidoc.md` — 工作流文档范式（模式表 + 阶段 + 验证节）
6. `install.py` — 安装器范式（路径映射表 + copy/symlink）

新增独立示例文件时，必须包含「真实参考文件」一节，并把路径登记到本文件的阅读顺序。

## 原则

- 仓库真实代码与示例不一致时，以真实代码为准，并更新示例
- 每个示例文件必须包含「真实参考文件」一节，指向示例代码的出处
