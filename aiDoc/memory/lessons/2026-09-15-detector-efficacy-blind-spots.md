<!-- last-updated: 2026-09-15 -->
<!-- lesson-meta: status=pending count=1 post=0 target= -->
# 检测器自身的有效性需要负例回归保护

## 情境

2026-09-15 全方位审阅（检测与验证体系方向），tests/selftest.py 与 check_sync.py。

## 坑 / 模式

检测体系存在「检测器自身无检测」的盲区，一次审阅出现三种形态：① 断言只看 stdout 计数不看状态文件内容——init 二跑清空 manifest 基线的破坏性回归全绿通过；② 逐字节一致性校验锁死合法分化——pre-push skill 的 TODO 因此永远无法填真实命令；③ 漂移检测器最高频场景（源码改名→引用失效）无负例测试，检测器改坏不会变红。检测代码和断言本身也是代码，其「真的能拦住目标回归」必须用负例证明，不能靠默认信任。

## 出现次数

1（2026-09-15 审阅，单次审阅内三种形态同现）

## 状态

pending

## 晋升去向

references/quality-workflow.md 已有「Test efficacy: the tests would actually fail on the intended regression——verify, don't assume」条款但未约束住本仓实践；若同类盲区再次出现，晋升时应把「新增检测/断言必须配负例」写进该文件报告纪律节或 modules/architecture-rules.md 脚本层。

## 晋升后复发

0

## 记录日期

2026-09-15
