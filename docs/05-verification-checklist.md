# 验证清单

## 1. CLI 与模型

```bash
command -v hermes
hermes --version
hermes -z '只回复 OK'
```

预期：

```text
OK
```

## 2. Gateway

```bash
hermes gateway status --full
```

检查：

- launchd plist 存在
- service definition matches
- gateway supervised by launchd
- PID 存在

## 3. Cron Scheduler

```bash
hermes cron status
hermes cron list --all
```

检查：

- gateway running
- ticker heartbeat 新鲜
- active / paused 数量符合预期
- next run 不为空

## 4. Cron 数据质量

```bash
jq '{
  total:(.jobs|length),
  prompt_equals_name:(.jobs|map(select(.prompt == .name))|length),
  empty_prompt:(.jobs|map(select((.prompt // "") == ""))|length),
  workdir_null:(.jobs|map(select(.workdir == null))|length),
  old_openclaw_prompt_refs:(.jobs|map(select((.prompt // "") | contains(".openclaw")))|length),
  active:(.jobs|map(select(.enabled == true and .state != "paused"))|length),
  paused:(.jobs|map(select(.enabled == false or .state == "paused"))|length)
}' $HOME/.hermes/cron/jobs.json
```

期望：

```text
prompt_equals_name: 0
empty_prompt: 0
workdir_null: 0
old_openclaw_prompt_refs: 0
```

## 5. 迁移后执行结果

```bash
jq -r '
  .jobs
  | map(select((.last_run_at // "") >= (.created_at // "9999")))
  | sort_by(.last_run_at)[]
  | [.last_run_at, .name, .last_status, (.next_run_at // "-"), (.workdir // "-")]
  | @tsv
' $HOME/.hermes/cron/jobs.json
```

重点看：

- 迁移后真实执行数
- `last_status`
- `last_error`
- 输出文件是否生成

## 6. 输出文件

```bash
find $HOME/.hermes/cron/output -maxdepth 2 -type f | sort | tail -20
```

## 7. OpenClaw 是否停用

```bash
launchctl list | rg 'ai\.(hermes|openclaw)\.gateway'
launchctl print-disabled "gui/$(id -u)" | rg 'ai\.openclaw\.gateway'
```

期望：

- 只看到 `ai.hermes.gateway` 正在运行
- `ai.openclaw.gateway` disabled

## 8. 敏感信息扫描

```bash
python3 scripts/scan-sensitive.py --history
```

期望：

```text
findings_count: 0
```

扫描脚本覆盖当前仓库文件；加 `--history` 时也检查当前 Git 历史中的文件内容。它只输出 finding 类型、文件和行号，不打印匹配到的具体值。
