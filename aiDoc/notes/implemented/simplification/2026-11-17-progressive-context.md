<!-- last-updated: 2026-11-17 -->
# 按变更范围加载上下文

## 问题

EGO 平台的 `CLAUDE.md` 只导入 `AGENTS.md`（9,212 字节）。膨胀发生在任务路由：接口对接指向 100,413 字节的 `boundary.md`，修改既有逻辑默认要求架构规则和系统图，新需求指向 58,640 字节的记忆索引。样本的契约正文覆盖多组 HTTP API、平台认证、设备上传和处理调度。读其中一组接口时，其他组的正文几乎总是无关。升级预演也发现样本使用旧版裸哈希 manifest，现有更新器读取条目时崩溃。

## 提案 / 决策

- L0 保留跨任务约束和短入口。L1 以变更路径、组件、接口和操作为线索。局部任务从代码和测试进入，涉及共享行为时再确定受影响的生产方与消费方。正文布局见 [aiDoc 结构契约](../../../../skills/project-harness/references/aidoc-structure.md)。
- 独立变更的接口面有各自的正文。保留 `boundary.md` 作共享约定与契约索引，分册由同目录链接登记并由漂移检查校验。小项目保留单文件，已有根索引登记继续兼容。
- 旧版 manifest 经安全接管建立基线，项目名称和语言沿用原元数据。处理依据见 [更新流程](../../../../skills/project-harness/references/update-harness.md)。
- 历史记录按主题搜索。记忆索引保留可检索的路径，变更时读取和更新命中的区域。
- OpenAI 的 Harness Engineering 用短 `AGENTS.md` 指向分层文档，GPT-6 Astra 指南也建议按变更范围决定阅读内容。Anthropic 的上下文工程实践从路径等轻量标识出发即时检索。Claude Code 的导入会把正文展开进上下文，契约和档案入口用普通 Markdown 路径。[OpenAI Harness Engineering](https://openai.com/index/harness-engineering/) · [OpenAI GPT-6 Astra 指南](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) · [Anthropic 上下文工程](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) · [Claude Code 加载说明](https://code.claude.com/docs/en/memory#import-additional-files)

## 真实考虑过的备选

- 先按 Markdown 标题选段可以快速缓解存量问题。长期只保留单文件会让独立接口继续在同一个热文件竞争维护空间，正文拆分更容易从入口按接口检索。
- 将每个分册都写进根路由可以沿用现有检查。样本有十个可独立查阅的章节，继续用根索引登记会把膨胀移到每个任务共享的入口，因此让契约入口维护分册。
- 使用工具原生目录规则适合子树特有的命令与约束。一个契约常同时涉及路由、业务代码和外部消费方，跨工具基线用显式接口路由。

## 验收标准

- [x] 双语初始化、刷新和分册索引的正负例通过。
- [x] 旧版 manifest 的临时样本迁移通过。EGO 升级预演列出可登记 4 项、定制需合入 22 项，定制项包括 L0、L1 和契约入口。
- [x] 样本在临时目录按十个现有章节迁移，所有正文小节逐字节保留，契约索引校验通过。
- [x] 对比整份契约与索引加相关分册的字节数。单独查设备上传为 5,449 字节（少 94.6%），查平台开放面为 7,922 字节（少 92.1%），跨采集员端和设备上传为 29,789 字节（少 70.3%）。按标题定位「采集任务时长必填」只返回 537 字节的索引条目。
- [x] 验证代表性任务能找到需要的契约。平台 HMAC 对应开放面，`/device-api/v1` 对应设备上传，`upload-session` 凭证变更需要补读采集员端和使用凭证的设备端；管理面与 DataPlatform-front 共用的任务时长字段需要核对两边。枚举文案修复可从映射、词条与对应测试进入。

## 风险与后果

迁移时同步当前文档链接和已晋升经验的目标路径。按路径或符号定位时，跨面行为要补查共享规则。样本数字只计指定文档的 UTF-8 字节，实际会话的 token、工具输出、模型命中率需在真实任务重跑时测量。样本仓库本次作为只读参照。
