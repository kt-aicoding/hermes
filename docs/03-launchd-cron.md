# launchd 开机启动与 Cron 运行

## Gateway 安装

Hermes gateway 使用 launchd 用户服务托管：

```bash
hermes gateway install --force
hermes gateway start
```

验证：

```bash
hermes gateway status --full
```

预期：

```text
Launchd plist: $HOME/Library/LaunchAgents/ai.hermes.gateway.plist
Service definition matches the current Hermes install
Gateway is supervised by launchd
Auto-start at login and auto-restart on crash are available.
```

## Cron 状态

```bash
hermes cron status
```

预期：

```text
Gateway is running — cron jobs will fire automatically
Ticker heartbeat: ... ago
30 active job(s)
Next run: ...
```

## OpenClaw 停用

迁移完成后避免双跑：

```bash
launchctl remove ai.openclaw.gateway
launchctl disable "gui/$(id -u)/ai.openclaw.gateway"
```

验证：

```bash
launchctl list | rg 'ai\.(hermes|openclaw)\.gateway'
launchctl print-disabled "gui/$(id -u)" | rg 'ai\.openclaw\.gateway'
```

期望只看到 Hermes gateway 正在运行，OpenClaw gateway 处于 disabled。

## 输出位置

当任务 `deliver=local` 时，cron 输出会保存到：

```text
$HOME/.hermes/cron/output/<job-id>/<timestamp>.md
```

这适合没有配置 Telegram/Discord/Slack 的本地环境。

