<!-- last-updated: 2026-10-04 -->
# 业务需求记录

## 需求描述

修复 scan_repo.py 启发式误判：对 Flutter 仓库重生成 `aiDoc/relations/code-index.md` 时，依据 `android/build.gradle.kts` 把 Flutter 工程误判为 Java Gradle 工程，丢失 flutter-app 分类、入口点与 flutter 命令索引（产物比已提交版本差，用户已回滚保留原版）。修好脚本前不对该文件跑重生成。

## 状态

已完成

## 涉及范围

### 命令行（cli）

- `skills/project-harness/scripts/scan_repo.py`：新增 pubspec.yaml 解析、flutter-app 组件 kind、Flutter 脚手架 gradle 抑制、flutter/dart 命令索引与包管理、`.dart` 语言统计、lib/main.dart 入口点
- `tests/selftest.py`：新增 test_flutter_detection 回归断言

## 约束与备注

- 保持零依赖与安全模型（只读扫描，仅 `--write-code-index` 写机器产物）
- Flutter 工程自带的 android/ios 宿主构建文件是脚手架，不得作为独立 Java 工程信号
- 修复决策与验收见 `aiDoc/notes/implemented/bug-fix/2026-10-04-flutter-scan-misdetection.md`

## 相关文件

- `skills/project-harness/scripts/scan_repo.py`
- `tests/selftest.py`
- `skills/project-harness/references/generate-aidoc.md`、`skills/project-harness/references/init-harness.md`
- `aiDoc/notes/implemented/architecture/2026-09-10-component-detection-model.md`

## 记录日期

2026-10-04
