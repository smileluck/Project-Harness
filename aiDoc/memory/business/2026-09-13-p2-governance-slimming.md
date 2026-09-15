<!-- last-updated: 2026-09-15 -->
# P2 治理减负与保障补盲（已完成）

## 需求描述

用户确认 P2 方案六个决策点（不变量 9→6 合并、update_harness 处理、lessons 索引唯一化到 project-memory、CI 取 ubuntu × 3.9/3.11/3.12、generic-adapter 删除、--lang auto 阈值 30%），要求按"保障先行 → 清理 → 口径 → 收敛 → 瘦身"顺序执行。

## 状态

done（2026-09-15 完成。阶段一 WS-C/E/D 见 9042f1c；update 工作流落地后续作阶段二：WS-A 不变量 9→6 + DoD 唯一化、WS-B 占位符统一 + --lang auto；update_harness 悬案按"被并行实现取代"处理）

## 涉及范围

### 后端 / library

- `tests/selftest.py`：新增 [2d]–[2i] 六组用例（标签断言/en 全流程/--no-scan/frontend 裁剪/check_sync 负例/install.py）
- `.github/workflows/selftest.yml`：CI 上线（ubuntu × 3.9/3.11/3.12）
- `check_sync.py`：检查 2 去重改按 (文件, 路径)、`../` 引用解析修正
- `scan_repo.py`：detect_components 拆分为 8 个 `_detect_*` 检测器 + 编排
- mixed fixture 修正（补 react 依赖使其真判 mixed）

### 前端

无。

### 命令行（cli）

无新 CLI（--lang auto 属 WS-B 未做）。

## 约束与备注

- 与并行会话的 update 工作流共享工作树：不 commit（避免收编对方半成品）；不动 SKILL.md/AGENTS.md/init_project/harness_common
- update_harness"删除"决策已被并行实现推翻，按被取代处理

## 相关文件

- 计划：`aiDoc/plans/completed/2026-09-13-p2-governance-slimming.md`
- 碰撞事件：`aiDoc/memory/lessons/2026-09-13-untracked-files-vs-concurrent-agents.md`

## 记录日期

2026-09-13
