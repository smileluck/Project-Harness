<!-- last-updated: 2026-09-15 -->
# 2026-09-15 全面评审整改

## 需求描述

用户要求对仓库做"全方位评审"，随后以一句"开始"授权按评审给出的行动顺序执行整改：修推送通道、机械产物再生成、口径修正批、init_project 正确性修正、update_harness 新增下发逻辑、manifest 刷新、zh/en 路由表对齐。

## 状态

done（2026-09-15。除推送通道外全部落地——SSH key 带 passphrase 需用户侧解锁后 push，CI 首跑待推送后确认。剩余未做项：AGENTS.md.tmpl 等约 15 处 zh/en 条目级互缺、architecture-rules 模板变体结构统一、CODE_INDEX_REL 双份定义收敛、双语字符串内联收敛、AUTO_SCAN_MARK 分语言，见决策记录"剩余工作"）

## 涉及范围

- 脚本：init_project.py（GBK 容错、as_posix、渲染降级警告、gitignore 去重、project-name 校验、dry-run 报告）、update_harness.py（模板新增文件下发/补登记/冲突三分类 + skip_set 形式修复）
- references：sync-aidoc.md（findings 表对齐 7 项真实检查）、SKILL.md、init-harness.md、tool-adapters.md、aidoc-structure.md、generate-aidoc.md
- 模板：zh/en aidoc/README.md 路由表对齐到 13 行并集；本仓实例同步
- 机械产物：code-index.md 再生成、manifest 刷新至 14 文件（补登记 pre-push-checks）
- 口径：五工作流×4 处、boundary 契约 2 补 update 新行为
- 测试：selftest 新增 6 用例（下发/补登记/冲突/不收敛回归/frontend 不下发）

## 验收标准

selftest 全过、check_sync 7/7、py_compile 全过；推送与 CI 首跑为用户侧遗留动作。

## 后续动作

push 后确认 Actions 首跑；剩余工作按决策记录排期。
