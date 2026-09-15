<!-- last-updated: 2026-09-15 -->
# 2026-09-15 全方位审阅与检测加固（第二轮）

## 需求描述

用户要求「全方位审阅项目，判断目前结构，输入输出，机制和检测等是否有问题」。三方向并行审阅（结构文档层 / 脚本机制与输入输出 / 检测验证体系）后，用户批准「全量修复 H+M+低成本 L」方案。

## 状态

done（2026-09-15。2 高危 + 8 中危 + 6 低成本低危全部落地；selftest 全绿、check_sync 9/9、py_compile 通过；本仓 manifest 基线已重建为 24 项）

## 涉及范围

- 脚本：init_project.py（manifest 基线合并）、check_sync.py（检查 8 TODO 占位 + 检查 9 manifest 比对 + lessons 递归/post 提示）、scan_repo.py（未跟踪文件补扫 + render_data 兜底）、harness_common.py（git_version 超时回退）、install.py（link→copy 切换 + copytree ignore）
- 检测：selftest 新增 12 项断言（基线保留、负例回归、链接校验、install 切换等）
- 文档：双语 README 五工作流 + 完整脚本清单；AGENTS.md 概览补目录行 + 五类口径；boundary.md 补内部契约登记；development-workflow.md 登记 CI；init-harness.md TODO 解析指向机械闸门；handoff.TEMPLATE 五类口径（zh/en/实例三处）
- dogfood 实例：.agents/skills/project-pre-push-checks 填入真实验证命令
- 记忆：本记录 + 决策记录 notes/implemented/bug-fix/2026-09-15-detection-hardening.md + lesson lessons/2026-09-15-detector-efficacy-blind-spots.md

## 验收标准

selftest 全过、check_sync 9/9 全绿、py_compile 全过；`.zcode/` 已入 .gitignore。

## 后续动作

未修低危项按决策记录「风险与后果」节排期；推送与 CI 确认为用户侧动作。
