<!-- last-updated: 2026-09-10 -->
# 决策：aiDoc 区域从前后端预设改为契约+范式中立

## 问题

初版 aiDoc 结构预设了"前后端 Web 应用"：`modules/backend-layer-rules.md`、`frontend-backend/`。但大量项目不是这种形态——CLI 工具、库、Qt 桌面应用——它们没有前端，"边界"也不是 HTTP API。用户反馈：简单用 front/backend 划分不合适。

## 提案 / 决策

区域重命名与泛化：`frontend-backend/boundary.md` → `contracts/boundary.md`（契约层，web-api / library / cli 三变体，generate 保留匹配变体）；前端文档独立为条件性区域 `frontend/`；`backend-layer-rules.md` → `architecture-rules.md`（分层服务/包模块/插件体系变体）。同步更新模板 zh/en、check_sync 区域清单、references、README。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| 保留目录名，只改内容说明 | 非 Web 项目里目录名名实不符，问题没有根除 |
| 只改 contracts/，保留 backend-layer-rules 文件名 | 对库/CLI 项目依然不准确，改名不彻底 |

## 验收标准

- [x] 全仓库 grep `frontend-backend`、`backend-layer-rules` 零残留
- [x] 六类 fixture（含非 Web 类型）init 产物 check_sync 全过
- [x] zh/en 模板结构 diff 为空

## 风险与后果

- 契约内容依赖 generate 工作流执行变体裁剪；骨架阶段的 boundary.md 同时含三个变体注释，校订前略冗长
- 引用裁剪逻辑（init 删索引行）按行过滤，依赖"索引引用都在单行表格行内"的模板约定

## 交叉链接

- 被后续决策扩展：`2026-09-10-component-detection-model.md`（项目类型进一步组件化）
- 实施提交：`e60923c`
