<!-- last-updated: {{DATE}} -->
# 模块开发指南（module development）

> 新建模块/功能/命令的完整步骤。步骤与参考文件必须指向真实路径。

## 设计原则

- 模块自包含：一个模块的各层文件集中在其目录内
- 遵循现有模式：动手前先读一个既有模块（优先功能完整、最近修改的模块）
- 不引入项目尚未使用的库或模式；确有需要时先写决策记录（见 [../notes/README.md](../notes/README.md)）

<!-- 变体：分层服务模块 / library 功能 / cli 命令，generate 工作流保留匹配变体并删除其余 -->

## 新建分层服务模块

<!-- TODO: 分层服务（典型 Web/后端）项目保留本变体；按真实结构补全每一步的命令与路径 -->

1. 创建模块目录：TODO:
2. 定义模型：TODO:（参考 [architecture-rules.md](architecture-rules.md) 数据层）
3. 定义 Schema/DTO：TODO:
4. 实现业务逻辑：TODO:
5. 实现入口层（Endpoint/Controller）：TODO:
6. 注册路由：TODO:
7. 数据库迁移：TODO:
8. 补充聚焦测试：TODO:

## 新建 library 功能

<!-- TODO: library/SDK 项目保留本变体；其余项目删除本变体 -->

1. 设计公开 API 面（函数/类签名）：TODO:
2. 实现内部逻辑：TODO:
3. 登记导出（包入口/公开导出路径）：TODO:（导出契约见 [../contracts/boundary.md](../contracts/boundary.md)）
4. 确认版本兼容影响（是否破坏性变更）：TODO:
5. 补充聚焦测试：TODO:

## 新建 cli 命令

<!-- TODO: cli 项目保留本变体；其余项目删除本变体 -->

1. 定义命令规格（命令名、参数、选项）：TODO:
2. 实现命令处理器：TODO:
3. 注册命令：TODO:
4. 约定输出与退出码：TODO:（退出码约定见 [../contracts/boundary.md](../contracts/boundary.md)）
5. 补充聚焦测试：TODO:

## 新建前端功能

<!-- TODO: 无前端时删除本节 -->

1. 定义类型声明：TODO:
2. 编写 API 封装函数：TODO:（复用规则见 [../frontend/frontend-utils.md](../frontend/frontend-utils.md)）
3. 编写页面/组件：TODO:（规范见 [../frontend/frontend-rules.md](../frontend/frontend-rules.md)）
4. 注册路由：TODO:
5. 国际化条目（如有）：TODO:

## 完成前检查

- [ ] 契约两侧字段与 [../contracts/boundary.md](../contracts/boundary.md) 一致
- [ ] 按影响面跑过聚焦验证（见根 `AGENTS.md` 操作不变量）
- [ ] 若模块带来非平凡决策，已写 `aiDoc/notes/` 决策记录

## 真实参考文件

<!-- TODO: 列出 1-2 个可作为范本的真实模块路径 -->

- TODO:
