<!-- last-updated: {{DATE}} -->
# 模块开发指南（module development）

> 新建模块/功能的完整步骤。步骤与参考文件必须指向真实路径。

## 设计原则

- 模块自包含：一个模块的各层文件集中在其目录内
- 遵循现有模式：动手前先读一个既有模块（优先 CRUD 完整、最近修改的模块）
- 不引入项目尚未使用的库或模式；确有需要时先写决策记录（见 [../notes/README.md](../notes/README.md)）

## 新建后端模块

<!-- TODO: 按真实结构补全每一步的命令与路径 -->

1. 创建模块目录：TODO:
2. 定义模型：TODO:（参考 [backend-layer-rules.md](backend-layer-rules.md) Model 层）
3. 定义 Schema/DTO：TODO:
4. 实现 Service：TODO:
5. 实现 Endpoint/Controller：TODO:
6. 注册路由：TODO:
7. 数据库迁移：TODO:
8. 补充聚焦测试：TODO:

## 新建前端功能

<!-- TODO: 无前端时删除本节 -->

1. 定义类型声明：TODO:
2. 编写 API 封装函数：TODO:（复用规则见 [../frontend-backend/frontend-utils.md](../frontend-backend/frontend-utils.md)）
3. 编写页面/组件：TODO:（规范见 [../frontend-backend/frontend-rules.md](../frontend-backend/frontend-rules.md)）
4. 注册路由：TODO:
5. 国际化条目（如有）：TODO:

## 完成前检查

- [ ] 契约两侧字段与 [../frontend-backend/boundary.md](../frontend-backend/boundary.md) 一致
- [ ] 按影响面跑过聚焦验证（见根 `AGENTS.md` 操作不变量）
- [ ] 若模块带来非平凡决策，已写 `aiDoc/notes/` 决策记录

## 真实参考文件

<!-- TODO: 列出 1-2 个可作为范本的真实模块路径 -->

- TODO:
