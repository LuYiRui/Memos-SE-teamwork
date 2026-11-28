# 张凯硕模块与证据核对记录

**责任范围：部署与架构、跨功能模块名称及数据关系。**
**日期：2026-11-28**
**方式：工具辅助核对固定版本源码、仓库Markdown、归档JSON与部分原始截图。**

本记录核对固定版本源码、功能报告、截图及归档请求，关注模块名称、存储边界、证据完整性和可复查性。
## 1. 基线与材料

- 上游版本26.11.0，完整提交 `b40d8a7b573774c52b022c8d6537d6baf2129dc0`。
- 团队仓库复核起点 `aa7a085`，对象为 `docs/phase-1/uc-03-search.md`、`uc-04-attachments.md`、`uc-05-sharing.md` 及对应归档资源。
- 新增[部署与架构](deployment-architecture.md)和三张可编辑源码配套的PNG架构图。
- UC-05归档摘要11项一致；请求记录38条中37项带预期状态，边界记录13项带预期状态，合计50项归档断言的状态一致。此处仅验证归档内部一致性。
- 目视核对UC-04 PNG上传图：仍有Save按钮、两条UploadAttachment 200；UC-05管理面板：Active share links中显示到期日期及复制按钮。图像能支持的结论与原文边界基本一致。

## 2. 发现、处理与结论

| 编号 | 对象与检查项 | 依据/发现 | 本次处理 | 结论 |
| --- | --- | --- | --- | --- |
| REV-ZKS-01 | UC-05 受众组件固定链接 | 原文 `edit/toolbar/AudienceMenu.tsx` 不存在；真实目录为 `edit/Toolbar/` | 仅修正文件路径及相应链接的大小写，不改功能结果 | 已修正，链接路径检查通过 |
| REV-ZKS-02 | UC-05 模块名称 | `useMemoShareQueries` → `memo_share_service` → `core/access` / Store → `store/db/sqlite/memo_share`；可见性更新通过笔记API和事务 | 已纳入部署与架构的五流程对应表 | 模块名称和依赖核对通过；不代替整页运行验收 |
| REV-ZKS-03 | UC-04 默认附件存储 | `store/instance_setting.go` 默认LOCAL；`attachment_service_storage.go`相对路径以Profile.Data为基准 | 文档明确数据库类型与附件存储类型独立，Docker默认路径位于命名卷 | 源码默认值已确认；成员实例的实际设置仍需原始配置证据 |
| REV-ZKS-04 | UC-04 事务与清理 | `ApplyMemoMutation`先提交数据库，再执行`cleanupDeletedAttachmentStorage`；清理失败返回Internal | 架构文档区分数据库事务和外部存储操作 | 原文风险描述有源码依据 |
| REV-ZKS-05 | UC-04 功能证据完整性 | 图3仍为编辑状态；图4不能单独证明PNG刷新成功或PDF字节成功读取 | 保留原报告的待补项，不勾选完成 | 需原负责人补刷新、PDF实际访问及存储设置证据 |
| REV-ZKS-06 | UC-03 架构对应 | 前端条件→ListMemos→filter编译→SQLite；`filter/`不能在合图时遗漏 | 已将filter/单列，保留日期本地日与UTC访问器的区别 | 模块映射核对通过；不替代吴政泓的互审 |
| REV-ZKS-07 | 互审分配一致性 | UC-03写宋佳辉复核UC-04，UC-04页首写谢宇轩，现有仓库无法确认最新分配 | 不覆盖任何已有互审人或签字 | 待组长确认互审配对，保留原有互审人 |

## 3. 主要源码定位

| 核对点 | 固定提交源码 |
| --- | --- |
| 受众菜单真实路径 | [AudienceMenu.tsx](https://github.com/usememos/memos/blob/b40d8a7b573774c52b022c8d6537d6baf2129dc0/web/src/components/MemoEditor/edit/Toolbar/AudienceMenu.tsx#L29) |
| 分享处理与限定目标 | [memo_share_service.go](https://github.com/usememos/memos/blob/b40d8a7b573774c52b022c8d6537d6baf2129dc0/server/api/memo_share_service.go#L172) |
| 普通读取与分享策略 | [core/access/memo.go](https://github.com/usememos/memos/blob/b40d8a7b573774c52b022c8d6537d6baf2129dc0/core/access/memo.go#L92) |
| 默认LOCAL存储 | [instance_setting.go](https://github.com/usememos/memos/blob/b40d8a7b573774c52b022c8d6537d6baf2129dc0/store/instance_setting.go#L322) |
| 数据目录与附件路径 | [attachment_service_storage.go](https://github.com/usememos/memos/blob/b40d8a7b573774c52b022c8d6537d6baf2129dc0/server/api/attachment_service_storage.go#L69) |
| 事务之后清理 | [memo_attachment_service.go](https://github.com/usememos/memos/blob/b40d8a7b573774c52b022c8d6537d6baf2129dc0/server/api/memo_attachment_service.go#L235) |

## 4. 可复核检查

在团队仓库根目录执行，源码目录需位于指定提交：

```sh
python scripts/check_phase1_docs.py --source /path/to/memos-source --output docs/phase-1/assets/architecture-review-checks.json
```

[检查输出](assets/architecture-review-checks.json)记录固定源码路径、行号范围、相对文件存在性、UC-05证据摘要及归档断言一致性。通过该检查只能证明上述材料检查通过，不能证明函数语义、界面行为、全组互审或运行测试全部通过。

## 5. 模型整合核对

| 检查对象 | 结论 |
| --- | --- |
| 运行架构 | 浏览器、Go服务、SQLite及默认本地附件的边界明确 |
| 模块职责 | 补充filter/、文件服务和默认LOCAL存储，五条核心流程均可定位 |
| 数据对象 | 用户、笔记、标签、附件、分享及空间关系与固定版本表结构相符 |
| 系统用例图 | 保留五个核心UC边界，区分作者、其他已登录用户和访客 |
| 概念类图 | 标签为派生概念；附件可未绑定；分享指向一条笔记；关联不传递授权 |
| 术语统一 | 普通地址与专门分享、附件资源与内容、概念关系与外键分开表述 |

[系统模型整合](../phase-2/system-models.md)包含系统用例图、概念类图及统一术语，PNG和可编辑DOT源码随文档归档。各UC的局部模型、实测补证及组长合稿按各自分工维护。
