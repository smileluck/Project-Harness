<!-- last-updated: 2026-10-04 -->
# 2026-10-04 scan_repo 新增 React Native / uni-app / uni-app x 探测

## 问题

Flutter 误判修复后，移动/跨端框架探测仍有缺口：React Native 与 uni-app 项目依赖中伴随的 `react`/`vue` 会被误判为 `web-frontend`（RN 项目的 `android/build.gradle` 还会误判 `java-app`），uni-app x（.uvue/uts 技术栈）完全无识别能力。

## 提案 / 决策

沿用 Flutter 修复的范式扩展 scan_repo.py：

1. **新组件 kind**：`react-native-app`（`package.json` 依赖 `react-native`，常量 `RN_DEPS`）与 `uni-app`（`@dcloudio/*` 依赖或本目录 `pages.json` 路由配置；子目录存在 `.uvue` 文件时 stack 判为 `uni-app x`）。均入 `KIND_ORDER`（flutter-app 与 qt-app 之间）与 `SPECIAL_KINDS`（单成分标签映射 `general`）。
2. **web-frontend 抑制**：同目录检出 RN 或 uni-app 时，伴随的 react/vue 依赖不再触发 `web-frontend`（与 qt 抑制 cpp 同理）。
3. **脚手架抑制泛化**：`_flutter_roots`/`_is_flutter_scaffold` 更名为 `_mobile_app_roots`/`_is_mobile_scaffold`，RN 工程根一并纳入——RN 项目的 `android/build.gradle` 同样不计入 java-app 判定与命令索引。
4. **uni-app 强信号约束**：组件成立需 `@dcloudio/*` 依赖或本目录 `pages.json` 其一；`.uvue` 单独出现只作 x 变体升级信号（应用内 `pages/` 页面目录不重复计组件）。
5. **入口点**：uni-app 工程登记 `pages.json`（type `uni-app pages`，需文件实际存在）。
6. **语言构成**：`LANG_EXTS` 增补 `.uvue`、`.uts`。
7. **命令/包管理不新增**：RN/uni-app 均为 npm 生态，`package.json` scripts 与 npm/pnpm/yarn 包管理探测已覆盖。
8. **selftest 新增 test_mobile_detection**：RN（脚手架不误判 java-app/web-frontend）、uni-app（dcloudio + pages.json 入口）、uni-app x（pages.json + .uvue，页面目录不重复计）三个 fixture。

## 真实考虑过的备选

| 备选 | 放弃理由 |
|---|---|
| RN/uni-app 统一为一个 `mobile-app` kind | 三者技术栈与工程结构差异大（Dart/npm+原生宿主/DCloud Vue），kind 合一会让 code-index 丢失框架区分度；标签层面已由 SPECIAL_KINDS 统一映射 general |
| `.uvue` 单独出现即判 uni-app x | 实测会把应用内 `pages/` 页面目录重复计为独立组件；pages.json 是 uni-app 必备文件，作强信号无漏判 |
| 为 uni-app x 单设 kind | uni-app x 与 uni-app 同属 DCloud 工程体系（pages.json/manifest.json 同构），stack 字符串区分已足够，避免 kind 膨胀 |
| RN 补充 `npx react-native run-*` 命令索引 | RN 工程脚本入口约定在 package.json scripts（已被索引），硬编码 react-native CLI 命令是猜测性内容 |

## 验收标准

- [x] 临时 fixture 实测：RN → `react-native-app` + `general` + 无 java-app/web-frontend/gradle 命令；uni-app → `uni-app` + pages.json 入口；uni-app x → 单组件 `uni-app`/`uni-app x`；Flutter 与纯 Web React 工程回归无损
- [x] `python3 tests/selftest.py` 全部通过（含新增 test_mobile_detection 三条断言）
- [x] `python3 skills/project-harness/scripts/check_sync.py .` 通过

## 风险与后果

- 组件 kind 集合十种 → 十二种，`skills/project-harness/references/generate-aidoc.md` kind 表/优先级链与组件探测模型决策记录已同批同步；下游消费方按 kind 集合泛化处理，无需改动
- web-frontend 抑制按目录粒度生效：同仓 Web 前端（另一目录的 react/vue package.json）不受影响
- Expo 等 RN 衍生框架依赖中必含 `react-native`，由 RN_DEPS 覆盖；`react-native-web` 等边缘形态暂按 RN 处理

## 交叉链接

- 前置修复：`aiDoc/notes/implemented/bug-fix/2026-10-04-flutter-scan-misdetection.md`（脚手架抑制机制源头）
- 组件探测模型：`aiDoc/notes/implemented/architecture/2026-09-10-component-detection-model.md`（已就地更新 kind 清单与抑制规则）
- 业务记录：`aiDoc/memory/business/2026-10-04-mobile-framework-detection.md`
