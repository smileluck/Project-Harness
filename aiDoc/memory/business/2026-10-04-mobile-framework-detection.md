<!-- last-updated: 2026-10-04 -->
# 业务需求记录

## 需求描述

scan_repo.py 增加 React Native / uni-app / uni-app x 的判断。

## 状态

已完成

## 涉及范围

### 命令行（cli）

- `skills/project-harness/scripts/scan_repo.py`：新增 `react-native-app` 与 `uni-app` 组件 kind（uni-app x 以 stack 区分）；RN 工程脚手架 gradle 抑制（原 Flutter 抑制机制泛化）；RN/uni-app 伴随 react/vue 依赖不触发 web-frontend；uni-app pages.json 入口点；`.uvue`/`.uts` 语言统计
- `tests/selftest.py`：新增 test_mobile_detection 三条 fixture 断言

## 约束与备注

- 保持零依赖与安全模型
- RN/uni-app 均为 npm 生态，命令索引与包管理沿用 package.json 既有探测，不新增
- 修复决策与验收见 `aiDoc/notes/implemented/feature/2026-10-04-mobile-framework-detection.md`

## 相关文件

- `skills/project-harness/scripts/scan_repo.py`
- `tests/selftest.py`
- `skills/project-harness/references/generate-aidoc.md`
- `aiDoc/notes/implemented/architecture/2026-09-10-component-detection-model.md`

## 记录日期

2026-10-04
