<!-- last-updated: {{DATE}} -->
# 开发流程（development workflow）

> 开发顺序、协作方式、分支与提交规范、环境命令。命令必须来自真实配置文件，禁止编造。

## 推荐开发顺序

<!-- TODO: 根据实际分层设计开发步骤，如 模型 → Schema → Service → Endpoint → Router 注册 → 迁移 -->

1. TODO:
2. TODO:

## 前后端协作

<!-- TODO: 无前端时删除本节 -->

- 后端先定义接口契约（见 [../frontend-backend/boundary.md](../frontend-backend/boundary.md)），前端可并行开发
- 联调前必须确认契约两侧字段一致
- TODO: 联调验证方式

## 分支策略

<!-- TODO: 按实际约定填写，如 main/develop/feature/hotfix -->

| 分支 | 用途 |
|---|---|
| TODO: | TODO: |

## 提交规范

<!-- TODO: 按实际约定填写，如 type(scope): description -->

- 格式：`TODO: type(scope): description`
- TODO: 允许的 type 列表

## 环境与依赖

<!-- TODO: 具体的安装、启动、迁移、测试命令，必须可在真实环境运行 -->

| 操作 | 命令 |
|---|---|
| 安装依赖 | `TODO:` |
| 启动开发服务 | `TODO:` |
| 数据库迁移 | `TODO:` |
| 运行测试 | `TODO:` |
| 构建 | `TODO:` |

## API 文档

<!-- TODO: Swagger/ReDoc 等地址（如有）；无则删除本节 -->

TODO:
