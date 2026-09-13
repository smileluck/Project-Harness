<!-- last-updated: 2026-09-13 -->
<!-- lesson-meta: status=promoted count=2 post=0 target=aiDoc/modules/architecture-rules.md -->
# 经验：程序化填充点用显式标记，不用标题文本匹配

## 情境

首次：审阅工作流时发现 `init_project.py` 用硬编码的双语 `##` 标题文本表（SECTION_ANCHORS）定位模板小节做扫描填充。
第 2 次：为 `check_sync.py` 新增 lessons 晋升扫描时需要机械读取 lesson 的状态/次数——同类「脚本程序化读取文档内容」场景，按本经验改用头部显式 `lesson-meta` 标记。

## 坑 / 模式

脚本按「人类可读的标题文本」定位填充点，是把展示层当成了程序化接口：标题一改脚本就失配，双语模板时耦合翻倍，且静态漂移检查难以覆盖。凡脚本需要程序化定位/填充文档位置，应在文档内嵌显式机器标记（如 `<!-- scan-fill:key -->`），标题等展示文本保持自由。

## 出现次数

2

## 状态

promoted

## 晋升去向

`aiDoc/modules/architecture-rules.md`「脚本层」小节：脚本程序化定位/读取文档内容必须使用显式机器标记，禁止标题文本匹配。

## 晋升后复发

0

## 记录日期

2026-09-13
