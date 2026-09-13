<!-- last-updated: 2026-09-13 -->
<!-- lesson-meta: status=pending count=1 post=0 target= -->
# 经验：固定样板的 dogfood 双家必须机械 diff 校验，人工同步必漏

## 情境

2026-09-13 评审发现：lessons 机制上线时更新了本仓 `aiDoc/memory/README.md` 定位文案（补"与经验教训"），漏改 `templates/{zh,en}/aidoc/memory/README.md` 同一句——模板与 dogfood 实例的固定样板区一份事实两个家，同批变更只改了一侧。

## 坑 / 模式

"模板是骨架、仓库是实例"的分层在内容区成立，但在固定样板区（README/TEMPLATE 类文件）意味着逐字节重复维护。靠"改模板时记得同步仓库"的人工纪律必然周期性漏改，且 selftest 原有的清单+占位符校验完全测不出文案漂移。任何"模板 + 自举实例"结构都应把样板区 diff=0 做成机械断言。

## 出现次数

1

## 状态

pending

## 晋升去向

（未晋升；本次已按此经验落地 selftest [5b] 样板一致性检查，晋升候选位置：`aiDoc/modules/architecture-rules.md` 模板层小节）

## 晋升后复发

0

## 记录日期

2026-09-13
