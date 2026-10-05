# 流媒体规则审阅（2026-10-06）

本次在线读取 blackmatrix7 固定提交的 23 份候选清单，原字节及哈希保存在 vendor/blackmatrix7/streaming-20261006 与 vendor/manifest.json；候选不自动参与发布。dler 的 YouTube、Netflix、Spotify 与旧快照哈希一致，使用 blackmatrix7 的精选差异补充。v2fly 固定提交为 Tubi 提供两个补充入口，许可随记录保存。

- 实际更新：YouTube、Netflix、Spotify、BBC iPlayer、Bilibili、爱奇艺、腾讯视频、优酷、网易云音乐，以及配置内联 Disney+、HBO/Max、Tubi。
- Apple TV+、Hulu、Prime Video、Channel 4、ITV、Viki、Rakuten、Peacock、Paramount+、TikTok：比较候选后现有核心业务域已覆盖，未导入品牌周边、共享平台或无关业务。
- Roku：v2fly 候选含整机/商店和其他品牌范围；保留现有 vod.delivery.roku.com，未扩大到整个设备域名。
- UHDNow、Shudder、STARZ、Vevo：保留已有专用规则；未取得可用的新专用上游列表，不能宣称已完整更新。
- 不导入 Netflix 上游的广泛 AWS IP/区域端点、腾讯 fake-IP/IPv4 映射范围，以及 Disney/HBO 共享统计、播放器、API 父域。TikTok 的 Trae/MarsCode 不属于本次流媒体范围。
- 保持 Netflix CDN 优先、Hulu 专用 bamgrid 优先、其他服务主站/CDN 分组；不涉及节点、IPv4 特设或策略选择。

accepted.json 是审阅通过的 94 条候选（包含已有覆盖项），生成器去重后远程发布列表净增 62 条；内联净增 17 条。审阅日期仅更新实际变更列表，未修改其他类别审阅日期。build-report.json 保存去重和新增依据。

验证：离线生成一致性、11 个整理器单元测试、原 108 个路由样例及新增 94 个端点的三配置匹配。设备刷新与实时结果另见配置仓库 manual/streaming-rules-update-20261006.md。域名匹配不是播放成功证明。
