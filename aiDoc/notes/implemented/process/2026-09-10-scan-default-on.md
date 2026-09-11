<!-- last-updated: 2026-09-10 -->
# 决策：init 默认执行静态扫描并生成机器产物 code-index.md

## 问题

初版 init 只生成带 TODO 的空骨架，全部内容依赖 agent 在 generate 工作流中从零探测。Harness_Handbook 证明了"纯静态分析先行"的价值：机械可得的事实（依赖、命令、目录结构）不该消耗 agent 的探测成本。

## 提案 / 决策

init 默认执行 `scan_repo.py`（`--no-scan` 可关）：扫描结果填充 repo-profile / development-workflow / system-map 的事实小节（标 `auto-scan` 待校订），并生成机器产物 `aiDoc/relations/code-index.md`（组件/语言/模块/入口点/命令五张表）。code-index.md 是覆盖规则的显式例外：总是重新生成、头部声明 `do not hand-edit`。扫描深度只做"清单+结构"，不做 import 依赖图与符号清单。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| 扫描默认关闭，显式 `--scan` 才执行 | 用户意图是"顺带"生成第一版信息；默认关闭则多数用户永远得不到事实底座 |
| 扫描产出独立 scan-report，不碰 aiDoc 文档 | 文档仍是空 TODO，agent 还要二次搬运事实，收益减半 |
| 加深分析到 import 依赖图/符号清单 | 多语言只能靠启发式，准确率与维护成本不成比例（用户选择了"清单+结构"档） |

## 验收标准

- [x] 六类 fixture 扫描填充值真实（技术栈表含实际框架名、命令表含真实 scripts/targets）
- [x] `--no-scan` 保留 TODO 骨架；dry-run 零写入；二跑幂等
- [x] auto-scan 标记字符串在脚本与 references 中逐字一致

## 风险与后果

- 填充事实的准确性受探测启发式限制，因此所有填充小节必须带 auto-scan 标记，generate 校订后才移除
- code-index.md 总是重写意味着用户手改会丢失——依赖头部声明与文档反复强调"机器产物"
- 标记字符串成为跨模块契约（脚本写入、references 描述、check 侧未来可能校验），改动需三处同步

## 交叉链接

- 依赖：`2026-09-10-component-detection-model.md`（扫描的探测模型）
- 契约登记：`aiDoc/contracts/boundary.md` 契约 3
