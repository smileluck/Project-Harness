<!-- last-updated: 2026-09-10 -->
# 决策：项目探测从单一类型标签升级为组件模型

## 问题

六类型标签（fullstack/backend/frontend/library/cli/general）假设一个仓库只有一种成分。真实存在混合项目：同一仓库存放前端代码 + Java 服务端、Qt 客户端 + Python 工具等。单一标签无法表达，且用户明确要求支持 java/python/go/c++/c/web/qt 与混合项目。

## 提案 / 决策

探测产出**组件列表** `(path, kind, stack, evidence)`，kind 九种（web-frontend/web-backend/cli/library/qt-app/java-app/go-module/cpp-app/generic）；扫描根目录+一级子目录的标志文件与扩展名，同目录允许多组件。仓库标签：单成分沿用六类型，多成分标 `mixed` 并列组件清单，无信号标 `general`。`has_frontend` = 任一组件为 web-frontend（仍只驱动 `frontend/` 区域的条件生成）。判定启发式必须带 evidence，误判由 generate 校订。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| 保持六类型，mixed 项目取"最主要"成分 | 丢失其他组件信息，frontend/ 等区域生成会出错 |
| 递归全树探测组件（不限一级子目录） | 扫描成本上升且深层嵌套组件罕见；一级子目录 + 根目录覆盖主流 monorepo 形态 |
| 更细的类型细分（monorepo/mobile 等） | 探测准确率下降，收益有限（用户在方案选择时未选更细粒度） |

## 验收标准

- [x] mixed fixture（web/ vue + server/ maven）探测为 mixed、两组件、frontend/ 正确生成
- [x] qt fixture（.pro + .ui）识别为 qt-app 组件
- [x] 既有单成分行为不回退（react+fastapi 根级混合仍判 fullstack）

## 风险与后果

- 探测是启发式：子串匹配可能误报（如注释里出现框架名）；evidence 字段是给 generate 校订的抓手
- Java 标志文件恢复纳入探测矩阵（此前六类型版本曾移除 pom.xml/build.gradle）
- 二级及更深目录的组件不探测，深层 monorepo 需 generate 补充

## 交叉链接

- 依赖：`2026-09-10-contract-paradigm-areas.md`（区域契约先中立化，组件内容才有落点）
- 实施：`skills/project-harness/scripts/scan_repo.py`；提交 `0d622c3`
