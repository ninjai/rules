# 整理后的 Surge 发布规则

审阅日期：2026-09-29。此目录按 `apple/`、`media/`、`apps/`、`network/` 分类提供设备实际引用的规则。

## 维护结构

- `../vendor/`：16 个第三方原始快照及许可证，原有字节和导入清单保持不变。
- `../apple/`、`../media/` 等旧路径：既有规则输入，保留旧 URL，兼容尚未迁移的配置。
- `../curated-plan.json`：发布文件与来源映射、策略名及人工修改决定。
- `../curated-sources/`：已核对的官方数据快照。当前包含 Telegram 官方 CIDR。
- 本目录：离线生成结果，不应直接编辑 `.list`。
- `build-report.json`：每个输入与输出的 SHA-256、条数及逐条修改理由。

54 个输出合并了 56 个来源文件（输入 7,438 条、输出 7,432 条）。合并仅涉及原先相邻、同策略的 Apple News 两个列表和国内规则两个列表。不是把所有规则合成一个巨型文件，也不改变各业务策略组的成员或国家出口顺序。

## 已处理的问题

| 问题 | 处理与边界 |
| --- | --- |
| 相同规则重复 | 删除 7 条完全重复项，含 Apple News、运营商更新、国内规则；比较时保留 flags 差异 |
| 同策略父域已覆盖具体域名 | 删除 4 条冗余项；只在同一输出列表、相同 flags 下执行 |
| 微信 IP 前缀写成 DOMAIN-KEYWORD | 将 233 个合法的三段 IPv4 前缀转换成对应 /24 CIDR，带 no-resolve；避免无关域名因包含数字片段而匹配。这依据原列表前缀意图，不宣称这些地址由微信官方重新确认 |
| TeamViewer 全局列表包含私网 IP | 移除 172.16.102.56/32；该地址由配置的局域网/进程规则决定，不能充当公网服务指纹 |
| YouTube 整域接管 gvt1.com | 移到 Google 通用列表，YouTube 保留自身媒体域名。Google 官方明确将 edgedl.me.gvt1.com 用于 ChromeOS 更新 |
| Telegram 使用旧 IP/ASN 范围 | IP 部分使用当前官方 14 个 CIDR；移除旧 8 条 IP/ASN，保留域名/进程规则，全部 CIDR 带 no-resolve。缩小了未被官方清单覆盖的地址范围，不据此断言旧地址全部失效 |
| 爱奇艺 CIDR 存在 host bits | 223.119.62.225/28 规范为 223.119.62.224/28，保留 /28 覆盖范围 |
| 部分应用/URL 规则排在 IP 后 | 4 个列表做稳定分区：非 IP 规则在前、IP/ASN 在后，各区内顺序不变，减少提前触发 DNS 的机会 |

来源：[Surge 域名语义](https://manual.nssurge.com/rules/domain.html)、[IP 规则](https://manual.nssurge.com/rules/ip.html)、[Google ChromeOS 主机清单](https://support.google.com/chrome/a/answer/6334001?hl=en)、[Telegram 官方 CIDR](https://core.telegram.org/resources/cidr.txt)。上游归属及许可继续见 `../vendor/manifest.json` 和 `../vendor/licenses/`。

## 构建与检查

从仓库根目录运行（仅 Python 标准库）：

```sh
python3 scripts/build-curated-rules.py
python3 scripts/build-curated-rules.py --check
python3 -m unittest discover -s tests -p 'test_curated_rules.py' -v
```

构建无网络请求、不写来源文件、不自动提交或推送。每次验证原始 vendor 清单和官方快照哈希；参数、规则类型或待删除条目发生非预期变化时直接失败，避免静默遗漏。生成物包含确定的日期和哈希，不加入每次执行变化的时间戳。

人工审核上游更新后，更新输入和 `curated-plan.json`，再生成、检查差异、校验、提交发布。新的 Telegram 快照应独立保存日期文件并更新 URL/哈希；不要把“历史快照”伪装成刚刚确认的数据。

## 验证与后续事项

本次 54 个输出均通过 Surge CLI 最小配置语法检查。11 项标准库回归测试覆盖同策略去重、flags、CIDR 边界、稳定排序、构建一致性、Telegram IPv4/IPv6、私网地址排除、共享 CDN 和全部 233 个微信前缀的正反例。

构建结果未模拟设备模块、SNI、HTTP Host、实际 DNS、进程识别及设备保存的策略选择；尚未完成线上应用验收。微信 /24 改写与 Telegram 范围替换需在实际客户端核对。

保留中国 ASN 及微信 ASN 等既有兜底；ASN 并不等同于地理位置或服务独占，不进行无证据的大范围裁剪。TikTok 的关键词和部分跨服务域名也仍保留，后续按连接记录细化。上游原始版权/归属注释保留在原始来源文件，并在生成文件中注明来源；上游历史 TOTAL/UPDATED 注释不是生成物的当前条数与审阅日期。

回退时按计划文件的 `profile_urls` 恢复旧链接即可，旧文件不会因本次整理而被删除或覆盖。
