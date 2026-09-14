<!-- last-updated: 2026-09-13 -->
# 项目记忆索引

## 长期记忆

暂无。

## 业务需求记忆

- `business/2026-09-11-self-evolution-loop.md`：AI 开发自动触发规则更新（自进化回路），规则级强制漂移自检 + 决策回写约束，已完成
- `business/2026-09-11-rule-evolution-lessons.md`：规则自进化——lessons 经验采集层 + 晋升约束层机制，已完成
- `business/2026-09-11-init-auto-generate.md`：init 默认自动接续 generate 工作流（`--no-generate` 可退出），已完成
- `business/2026-09-13-rsi-optimization.md`：AI 自进化（RSI）回路优化——lessons 机械闸门 + 晋升后复发闭环，已完成
- `business/2026-09-13-harness-update.md`：harness 更新功能——git 版本标识 + manifest 基线 + update 工作流（install/skill/产物三层），已完成
- `business/2026-09-13-p0p1-remediation.md`：架构评审后的 P0+P1 整改——破损修复（code-index 死锁/白名单盲区/漂移清理）与单源化去冗余，已完成
- `business/2026-09-13-p2-governance-slimming.md`：P2 治理减负与保障补盲——CI 上线、测试盲区补齐、lessons 索引唯一化、组件检测拆分等，部分完成（WS-A/B 待 update 工作流落地后续作）

## 经验记忆（lessons）

- `lessons/2026-09-13-explicit-markers-over-heading-text.md`：程序化填充点用显式标记，不用标题文本匹配（promoted，2 次 → `modules/architecture-rules.md` 脚本层）
- `lessons/2026-09-13-untracked-files-vs-concurrent-agents.md`：并行 agent 同仓工作时未提交的新文件会被对方工作流冲掉（写入侧：尽早提交；操作侧：删除前查活跃写入）（pending，1 次）
- `lessons/2026-09-13-boilerplate-dual-home-drift.md`：固定样板的 dogfood 双家必须机械 diff 校验（pending，1 次；已落地 selftest 样板检查，候选晋升位 architecture-rules 模板层）

新增/晋升/累加 lesson 时必须同步本区索引，规则见 `lessons/README.md`。

## 维护说明

- 新增记忆时创建文件并更新此索引
- 过时记忆及时清理，并同步清理索引条目
- 索引每条一行：文件相对路径 + 一句话摘要
