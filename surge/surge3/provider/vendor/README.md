# 外部 Surge 规则归集

本目录保存 Surge Profiles 原先直接引用的第三方规则快照，由 `ninjai/rules` 统一发布和管理。导入日期：2026-09-29。

## 目录

| 目录 | 来源 | 数量 |
| --- | --- | --- |
| `dler/` | dler-io/Rules | 7 |
| `blackmatrix7/` | blackmatrix7/ios_rule_script | 6 |
| `get-some-fries/` | VirgilClyne/GetSomeFries | 2 |
| `nsringo/` | NSRingo/News | 1 |

现有 `provider/` 下的自有规则不被覆盖。同名服务也保留独立来源路径，以维持原来的两个列表、顺序和策略。例如 Apple News 原有列表与 NSRingo 补充列表仍分别存在。

## 来源与更新

`manifest.json` 记录原引用 URL、上游仓库、提交或 Release、下载地址、SHA-256 和有效规则行数。各 `.list` 按原始字节保存，原有注释、作者信息、规则顺序和参数均保留。

Dler 的 `master` 在导入时不能通过 GitHub commits API 解析（422），但原 raw URL 仍可下载。这些条目的 `revision` 为 null，以下载时间和内容哈希标识快照，不冒充已固定的 Git 提交。

后续更新流程：

1. 从清单的上游来源重新获取候选内容，尽量解析到具体提交或 Release。
2. 比较规则新增、删除、类型和顺序，核对共享域名/ASN 是否过宽。不要直接覆盖已审阅快照。
3. 更新选中的 `.list` 与对应清单记录，保留来源和许可证。
4. 检查规则语法及服务命中样例，只提交本次规则文件。
5. 发布后检查 raw URL 内容哈希，再重载需要更新的设备。

这里不设置自动跟随第三方上游的同步任务；设备引用 `ninjai/rules/master` 时，只接收本仓库已发布的变更。

## 归属与许可证

原始规则注释保持完整。三个上游仓库的许可证副本保存在 `licenses/`，来源和哈希记录在清单中。Dler 根目录未发现独立 LICENSE；保留其来源及文件内声明，不为第三方内容另外声明许可。下游使用时同时遵循相应上游要求。
