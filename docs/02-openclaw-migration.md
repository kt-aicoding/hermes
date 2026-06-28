# 从 OpenClaw 迁移到 Hermes

## 迁移目标

本次迁移覆盖：

- OpenClaw memory / user / soul
- skills
- workspace 文件
- cron jobs
- Ark provider 配置
- launchd 开机启动

## 备份

迁移前先备份 Hermes 和 OpenClaw：

```bash
mkdir -p "$HOME/hermes-migration-backups/manual-openclaw-migration-$(date +%Y%m%d-%H%M%S)"
```

建议备份：

```text
$HOME/.hermes
$HOME/.openclaw
$HOME/.hermes/config.yaml
$HOME/.hermes/.env
```

## 官方迁移命令

示例：

```bash
hermes claw migrate \
  --source "$HOME/.openclaw" \
  --preset full \
  --migrate-secrets \
  --skill-conflict rename \
  --overwrite \
  --yes
```

实践中官方迁移能处理大部分数据，但 cron 需要额外核对。

## Cron 迁移坑点

OpenClaw cron 源数据位于：

```text
$HOME/.openclaw/cron/jobs.json.migrated
```

关键字段：

```json
{
  "id": "...",
  "name": "...",
  "schedule": {"kind": "cron", "expr": "0 9 * * *", "tz": "Asia/Shanghai"},
  "payload": {
    "kind": "agentTurn",
    "message": "真正的任务指令",
    "timeoutSeconds": 900,
    "model": "doubao-seed-2-0-code-preview-260215"
  },
  "delivery": {
    "mode": "announce",
    "channel": "telegram",
    "to": "..."
  }
}
```

最重要的字段是 `payload.message`。如果迁移时只把 `name` 写入 Hermes `prompt`，任务会“能跑但偏题”。

## Workspace 迁移

本次实践将 OpenClaw workspace 复制到：

```text
$HOME/.hermes/openclaw-workspaces
```

推荐映射：

- AI Ideas / Issue / PR / 创意类任务：
  `$HOME/.hermes/openclaw-workspaces/workspace/awesome-ai-ideas`
- 系统健康、账单提醒、三爪协作类任务：
  `$HOME/.hermes/openclaw-workspaces/workspace`

这样 Hermes cron 执行时可以加载对应的 `AGENTS.md` 和仓库上下文。
