# Minecraft 资讯播报（mcnews）

`astrbot_plugin_mcnews` 是 AstrBot 的一个插件，用于自动抓取 Minecraft 最新资讯、版本更新与官方相关服务状态，并在订阅的群聊中进行推送提醒。

## 功能特性

- **资讯播报**：定期获取 Minecraft 官方新闻，推送标题、发布时间、摘要与原文链接
- **版本追踪**：监控最新正式版、快照版等版本发布，第一时间通知
- **版本详情**：自动获取版本更新的详细内容，包括新增内容、更改内容、修复漏洞和技术性更改
- **服务状态监控**：周期性检测 Mojang 认证、会话、材质等官方服务状态，异常或恢复时即时提醒
- **白名单推送**：仅向订阅白名单中的群聊发送通知，避免打扰未订阅的会话

## 快速开始

1. 将本插件目录放置于 AstrBot 插件目录（或通过插件市场安装）
2. 确保 AstrBot 已按官方文档正确配置并运行
3. 启动 AstrBot，插件会自动生成配置文件
4. 在需要接收推送的群聊中发送 `/mcnews add` 完成订阅

## 指令说明

| 指令 | 说明 |
| --- | --- |
| `/mcnews help` | 查看帮助信息 |
| `/mcnews add` | 将当前会话加入推送白名单 |
| `/mcnews remove` | 从白名单移除当前会话 |
| `/mcnews list` | 查看白名单列表 |
| `/mcnews news` | 手动查看最新资讯 |
| `/mcnews latest` | 查看最新版本信息 |
| `/mcnews version <版本号>` | 查看指定版本的详细更新内容 |
| `/mcnews status` | 查看服务状态 |

## 配置项

在 AstrBot 控制面板中可配置以下选项：

| 配置项 | 默认值 | 说明 |
| --- | --- | --- |
| 群聊白名单 | `[]` | 只在白名单内的会话发送推送消息 |
| 文章检查间隔(分钟) | `30` | 检查官方更新日志的间隔 |
| 版本检查间隔(分钟) | `15` | 检查版本更新的间隔 |
| 推送快照版本 | `true` | 是否推送快照版本更新 |
| 推送官方文章 | `true` | 是否推送官方更新日志 |

## 数据来源

- 官方更新日志：`https://launchercontent.mojang.com/v2/javaPatchNotes.json`（Java版更新日志）
- 版本信息：`https://piston-meta.mojang.com/mc/game/version_manifest_v2.json`（版本清单）

## Mojang 服务状态监控

实时检测 Mojang 官方基础服务的运行状态：

- **Mojang Session Server**：玩家档案与皮肤服务（用于获取玩家皮肤、披风等）
- **Minecraft Services API**：认证与账户服务（用于登录验证、账户管理）
- **Mojang API**：玩家查询服务（用于查询玩家 UUID、用户名等）

通过 `/mcnews status` 命令可查看各服务当前状态及响应延迟。

## 许可证

MIT License
