# Cron 任务优化

## 问题

迁移后首次检查发现：

```text
total: 36
prompt_equals_name: 36
workdir_null: 36
```

这意味着 Hermes 的 cron 任务只知道任务标题，不知道完整任务指令。结果是：

- 任务可以成功执行
- 但输出容易偏题
- agent 会自己猜要做什么
- 涉及 GitHub Issue/PR、curl、写文件时更容易触发安全策略或错误路径

## 修复

从 OpenClaw 源文件恢复：

```text
~/.openclaw/cron/jobs.json.migrated
```

恢复规则：

- Hermes `prompt` = OpenClaw `payload.message`
- Hermes `workdir` = 按任务类型映射到迁移后的 workspace
- 保留 Hermes schedule / enabled / paused / next_run / provider / model
- 保留 `deliver=local`，避免没有消息平台时制造 delivery error

优化后校验：

```text
total: 36
prompt_equals_name: 0
empty_prompt: 0
workdir_null: 0
old_openclaw_prompt_refs: 0
active: 30
paused: 6
```

## 可复用脚本

见：

```text
scripts/optimize-cron-from-openclaw.py
```

默认是 dry-run：

```bash
python scripts/optimize-cron-from-openclaw.py
```

实际写入：

```bash
python scripts/optimize-cron-from-openclaw.py --apply
```

## 审批策略

日志中出现过类似问题：

- terminal 命令等待审批
- curl 被拦截
- write_file 被拒绝
- execute_code 在 cron 中被禁用

这是安全策略，不建议直接全局关闭。更稳妥的优化顺序：

1. 先恢复完整 prompt
2. 补 workdir 和 AGENTS.md 上下文
3. 观察下一轮真实 cron 输出
4. 对确实需要外部写入的任务，逐个设计脚本或安全 allowlist
5. 不要默认开启全局自动审批

