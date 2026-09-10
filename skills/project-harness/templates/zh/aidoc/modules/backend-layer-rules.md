<!-- last-updated: {{DATE}} -->
# 后端分层规则（backend layer rules）

> 后端各层必须遵守的约束。所有规则必须引用实际代码中的类名和文件路径；TODO 项由 generate 工作流按真实代码填充。

## 总原则

- 严格分层，禁止跨层调用、禁止反向依赖
- 每层只通过下层的公开接口交互
- TODO: 本项目的实际分层调用链（如 Endpoint → Service → Model）

## Model 层

<!-- TODO: 按真实代码填写 -->

- 基类继承：TODO:（引用实际基类，如 `app/models/base.py:Base`）
- 字段声明方式：TODO:
- 表名/集合命名规则：TODO:
- 存放位置：TODO:

## Schema / DTO 层

<!-- TODO: 按真实代码填写 -->

- 请求/响应基类：TODO:
- 序列化规则：TODO:
- 验证方式：TODO:
- 存放位置：TODO:

## Service 层

<!-- TODO: 按真实代码填写 -->

- 只放纯业务逻辑，禁止处理 HTTP/传输层细节
- 方法签名模式：TODO:
- 异常处理：TODO:（引用实际异常类）
- 查询优化：TODO:（如分页、N+1 规避约定）

## Controller / Endpoint 层

<!-- TODO: 按真实代码填写 -->

- 只负责参数提取、调用 Service、响应格式化
- 分页处理：TODO:
- 响应格式：必须遵循 [../frontend-backend/boundary.md](../frontend-backend/boundary.md) 的统一响应结构

## Router 层

<!-- TODO: 路由注册方式与位置 -->

TODO:

## 错误码分配

<!-- TODO: 如有错误码体系，列出已使用的错误码范围；无则删除本节 -->

| 范围 | 用途 |
|---|---|
| TODO: | TODO: |
