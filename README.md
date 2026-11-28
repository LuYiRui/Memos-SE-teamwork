# Memos 系统代码阅读、标注和维护申请

上游：[usememos/memos](https://github.com/usememos/memos)

固定版本：26.11.0；提交：`b40d8a7b573774c52b022c8d6537d6baf2129dc0`

## 第一阶段文档

| 文档 | 内容 |
| --- | --- |
| [部署与架构](docs/phase-1/deployment-architecture.md) | 张凯硕：部署方案、整体架构、模块职责、数据对象及固定源码依据 |
| [模块与证据核对记录](docs/phase-1/peer-review-zhangkaishuo.md) | 张凯硕：模块互审、修正记录、存储边界及证据核对 |
| [搜索与日期筛选](docs/phase-1/uc-03-search.md) | 宋佳辉：UC-03 |
| [附件上传与查看](docs/phase-1/uc-04-attachments.md) | 宗锌城：UC-04 |
| [可见性与分享](docs/phase-1/uc-05-sharing.md) | 谢宇轩：UC-05 |
| [总报告](docs/phase-1/report.md) | 小组汇总入口 |

## 第二阶段模型整合

[系统用例与概念模型整合](docs/phase-2/system-models.md)：张凯硕负责系统用例图、系统概念类图及术语统一。

图示PNG及可编辑DOT源码位于`docs/phase-1/assets/`。[静态核对结果](docs/phase-1/assets/architecture-review-checks.json)可通过`scripts/check_phase1_docs.py`复核。
