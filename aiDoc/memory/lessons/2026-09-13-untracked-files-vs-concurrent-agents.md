<!-- last-updated: 2026-09-13 -->
<!-- lesson-meta: status=pending count=1 post=0 target= -->
# 经验：并行 agent 同仓工作时，未提交的新文件会被对方工作流冲掉

## 情境

本次 update 功能开发与另一 agent 的架构整改（f638fa1）同仓并行：对方提交把Tracked 文件的改动一并收编，而未跟踪的新文件 `update_harness.py` 被其工作流抹掉（同批新建的 reference/manifest 幸存，仅脚本丢失），selftest 直接 ModuleNotFoundError。

## 坑 / 模式

多 agent 并行改同一仓库时，未提交（untracked/uncommitted）的工作成果没有任何保护，规则分两侧：

- **写入侧（受害预防）**：跨组件大变更应尽早 commit（或至少让新文件进入 git 跟踪），把"工作成果落 git"作为可恢复点，而不是攒到最后一次提交。
- **操作侧（加害预防，同日另一次会话补充）**：对共享工作树中的文件做删除/清理/覆盖前，必须确认无并行会话活跃写入（`stat` 检查 mtime 是否在分钟级新鲜度内、观察 untracked 文件是否在变化），禁止按"孤儿/悬案文件"假设定罪——本事件的 rm 正是只看了"零引用"没看"正在被写"。

## 出现次数

1

## 状态

pending

## 晋升去向

（未晋升；第二次出现时写入 `modules/architecture-rules.md` 协作约束节：并行工作时阶段性提交 + 破坏性操作前检查活跃写入）

## 晋升后复发

0

## 记录日期

2026-09-13
