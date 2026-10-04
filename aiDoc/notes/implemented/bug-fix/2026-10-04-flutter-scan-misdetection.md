<!-- last-updated: 2026-10-04 -->
# 2026-10-04 scan_repo 修复 Flutter 工程误判为 Java Gradle 工程

## 问题

对 Flutter 仓库跑 `scan_repo.py --write-code-index` 重生成 `aiDoc/relations/code-index.md` 时，Flutter 工程被误判为 Java Gradle 工程：依据是 `android/build.gradle.kts`（Flutter 脚手架自带的 Android 宿主工程），导致丢失 flutter-app 组件分类、lib/main.dart 入口点与 flutter 命令索引，产物比已提交版本差。用户已回滚保留原版，并要求修好脚本前不对该文件跑重生成。

根因：scan_repo 完全没有 Dart/Flutter 意识——不解析 `pubspec.yaml`，语言统计不收 `.dart`，组件/入口/命令/包管理四层均无 Flutter 分支；而 `android/` 恰好在扫描深度（根+一级子目录）内，其 build.gradle 被当作独立 Java 工程信号。

## 提案 / 决策

在 scan_repo.py 一次性补齐 Flutter/Dart 支持，并修复误判：

1. **新增 `parse_pubspec`**（注册进 `MANIFEST_PARSERS`）：正则提取 `name`/`version`；Flutter 信号 = 顶层 `flutter:` 配置节或依赖中 `sdk: flutter`。
2. **新增 `flutter-app` 组件 kind**：`_detect_flutter` 检测器（pubspec 含 flutter 信号 → stack `Flutter`）；入 `KIND_ORDER`（qt-app 前）与 `SPECIAL_KINDS`（单成分标签映射 `general`，与 qt-app 一致）；纯 Dart 包（无 flutter 信号）记 note 不参与组件判定。
3. **脚手架抑制**：`_flutter_roots` + `_is_flutter_scaffold`——Flutter 工程子目录（如 `android/`）下的 build.gradle(.kts) 不计入 java-app/web-backend 判定、不生成 `gradle build/test` 命令、不计入 Gradle 包管理证据，并写 note 说明。Flutter 根同级的 build.gradle 不受影响。
4. **入口点**：`collect_entry_points` 增加 `files` 参数，flutter-app 且目标仓库 lib/main.dart 实际存在时登记入口（type `flutter entrypoint`）。
5. **命令索引**：flutter 工程登记 `flutter pub get` / `flutter run` / `flutter test` / `flutter build`（install/run/test/build 权重）；纯 Dart 包登记 `dart pub get` / `dart test`。
6. **包管理**：pubspec 存在 → `flutter pub`（含 flutter 信号）或 `dart pub`；被抑制的脚手架 gradle 从 Gradle 证据中剔除，全剔除则不列 Gradle。
7. **语言构成**：`LANG_EXTS` 增补 `.dart`。
8. **selftest 新增 test_flutter_detection**：fixture（pubspec + lib/main.dart + android/build.gradle.kts）断言 flutter-app 分类、无 java-app、`general` 标签、入口点、flutter 命令、无 gradle 命令、包管理为 flutter pub。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| 只做抑制（识别 flutter 后忽略 android/ 的 gradle），不补 flutter-app 探测 | 治标：Flutter 工程仍无组件分类、入口点与命令索引，重生成产物依旧比人工校订版差 |
| 用扩展名/目录结构（lib/*.dart、android+ios 并存）推断 Flutter | 与「框架识别从依赖/清单出发，不硬编码文件特征」的既有原则冲突；pubspec 是确定性信号且零依赖可解析 |
| flutter-app 映射为 frontend 标签 | 六类型标签中 frontend 语义绑定 Web 前端且驱动 `frontend/` 区域条件生成；移动端 GUI 与 qt-app 同类，按 SPECIAL_KINDS 映射 general 更一致 |

## 验收标准

- [x] 临时 fixture 实测：根级 Flutter 工程 → `flutter-app` 组件 + `general` 标签 + lib/main.dart 入口 + 四条 flutter 命令 + `flutter pub` 包管理，android/ gradle 不再产生 java-app/gradle 命令；嵌套（app/ 子目录）Flutter 工程同样正确；纯 Java Gradle 工程行为不变（回归）
- [x] `python3 tests/selftest.py` 全部通过（含新增 test_flutter_detection）
- [x] `python3 skills/project-harness/scripts/check_sync.py .` 通过

## 风险与后果

- 组件 kind 集合九种 → 十种，`skills/project-harness/references/generate-aidoc.md` 的 kind 表/优先级链、`skills/project-harness/references/init-harness.md` 的清单列表、组件探测模型决策记录均已同批同步；下游消费方（init_project 的 detect_project、repo_label）按 kind 集合泛化处理，无分支依赖具体 kind，无需改动
- `collect_entry_points` 签名变更（新增 `files` 参数）：脚本内唯一调用点已同步；属脚本内部函数，非对外 CLI 契约
- 抑制规则只覆盖扫描深度内的脚手架（根+一级子目录），更深的 `android/app/build.gradle` 本就不在扫描范围，无遗漏面
- 纯 Dart 包只有 install/test 两条命令且无组件分类（记 note），后续如出现真实 Dart CLI/服务端项目再扩展检测器

## 交叉链接

- 组件探测模型：`aiDoc/notes/implemented/architecture/2026-09-10-component-detection-model.md`（已就地更新 kind 清单与脚手架抑制规则）
- 检测器盲区教训：`aiDoc/memory/lessons/2026-09-15-detector-efficacy-blind-spots.md`
- 业务记录：`aiDoc/memory/business/2026-10-04-flutter-scan-misdetection.md`
