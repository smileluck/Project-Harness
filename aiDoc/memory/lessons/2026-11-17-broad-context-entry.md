<!-- last-updated: 2026-11-17 -->
<!-- lesson-meta: status=pending count=1 post=0 target= -->
# 检查任务路由实际读取量

## 情境

EGO 平台的启动入口已经按层组织，接口和记录任务仍带入大量项目文档。

## 坑 / 模式

只检查启动导入和目录结构，会漏掉路由项指向的单文件膨胀。选一个具体接口变更和一个记录任务，沿实际入口统计会读取的文件或片段，才能定位膨胀发生在哪一层。

## 出现次数

1 次。样本的契约入口和记忆索引都出现此问题。

## 状态与去向

pending。调查证据见 [按变更范围加载上下文](../../notes/implemented/simplification/2026-11-17-progressive-context.md)。
