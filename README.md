# Hermes 本地智能体实践手册

把 OpenClaw 迁移到 Hermes Agent，并在本机跑通 Ark 模型、launchd 开机自启和 cron 定时任务的一套实践记录。

这个仓库不包含私有配置或密钥，目标是沉淀可复用的方法、验证清单和脚本，方便团队成员搭建自己的 Hermes 本地智能体环境。

## 适合谁看

- 想把 OpenClaw 迁移到 Hermes 的用户
- 想用 Hermes 跑本地 gateway 和定时任务的人
- 想接入火山引擎 Ark / 自定义 OpenAI-compatible provider 的人
- 想排查 Hermes cron “任务能跑但输出偏题”问题的人
- 想把本机 agent 实践整理成可分享工程资产的人

## 已验证能力

本次实践已验证：

- Hermes CLI 可用，模型调用可返回 `OK`
- Ark coding endpoint 可作为 Hermes custom provider 使用
- Hermes gateway 可通过 macOS `launchd` 开机自启
- Hermes cron scheduler 可自动触发任务并保存输出
- OpenClaw cron 可迁移到 Hermes
- OpenClaw `payload.message` 可恢复为 Hermes cron `prompt`
- cron 任务可绑定迁移后的 workspace，让 agent 加载对应 `AGENTS.md` 上下文
- OpenClaw gateway 可停用，避免双跑

## 核心结论

OpenClaw cron 迁移到 Hermes 时，最容易踩的坑是只迁移了任务标题。

错误状态通常长这样：

```text
prompt_equals_name: 36
workdir_null: 36
```

这会导致 Hermes 只知道“任务叫什么”，不知道“任务要怎么做”。任务可能会成功执行，但输出容易偏题。

正确修复方式：

- 从 OpenClaw `~/.openclaw/cron/jobs.json.migrated` 读取 `payload.message`
- 写回 Hermes `~/.hermes/cron/jobs.json` 的 `prompt`
- 给任务补上合适的 `workdir`
- 保留原有 schedule、enabled/paused、next_run、provider/model

优化后应接近：

```text
prompt_equals_name: 0
empty_prompt: 0
workdir_null: 0
old_openclaw_prompt_refs: 0
```

## 快速开始

只读检查当前 Hermes 状态：

```bash
./scripts/verify-hermes.sh
```

检查内容包括：

- Hermes CLI 和版本
- LLM 连通性
- gateway / launchd 状态
- cron scheduler 心跳
- cron 任务数量
- prompt / workdir 数据质量
- 迁移后真实执行记录
- OpenClaw gateway 是否仍在运行

从 OpenClaw cron 恢复 Hermes prompt 和 workdir，先 dry-run：

```bash
python3 scripts/optimize-cron-from-openclaw.py
```

确认输出后实际写入：

```bash
python3 scripts/optimize-cron-from-openclaw.py --apply
```

## 文档导航

| 文档 | 内容 |
| --- | --- |
| [安装与 Ark Provider](docs/01-install-and-provider.md) | Hermes 安装路径、Ark custom provider 配置、模型连通性验证 |
| [OpenClaw 迁移](docs/02-openclaw-migration.md) | 备份、官方迁移命令、cron 源数据结构、workspace 迁移 |
| [launchd 与 Cron](docs/03-launchd-cron.md) | gateway 安装、开机自启、cron 状态、OpenClaw 停用 |
| [Cron 任务优化](docs/04-cron-optimization.md) | prompt 恢复、workdir 映射、安全审批策略 |
| [验证清单](docs/05-verification-checklist.md) | CLI、模型、gateway、cron、输出、数据质量检查命令 |

## 脚本

| 脚本 | 用途 | 是否写入 |
| --- | --- | --- |
| [`scripts/verify-hermes.sh`](scripts/verify-hermes.sh) | 检查 Hermes、gateway、cron 和任务数据质量 | 否 |
| [`scripts/optimize-cron-from-openclaw.py`](scripts/optimize-cron-from-openclaw.py) | 从 OpenClaw cron 恢复 Hermes prompt/workdir | 默认否，传 `--apply` 才写入 |

## 推荐迁移流程

1. 安装 Hermes Agent。
2. 配置 Ark 或其他 custom provider。
3. 用 `hermes -z '只回复 OK'` 验证模型连通。
4. 运行 `hermes gateway install --force` 和 `hermes gateway start`。
5. 执行 OpenClaw 官方迁移。
6. 复制或映射 OpenClaw workspace。
7. 检查 Hermes cron 数据质量。
8. 用 `optimize-cron-from-openclaw.py` 恢复完整 prompt/workdir。
9. 停用 OpenClaw gateway，避免双跑。
10. 等待下一轮真实 cron 执行，再检查输出文件和 `last_status`。

## 关键路径

这些是常见默认路径，实际使用时按自己的机器调整：

```text
~/.hermes/hermes-agent
~/.hermes/config.yaml
~/.hermes/.env
~/.hermes/cron/jobs.json
~/.hermes/cron/output/
~/.openclaw/cron/jobs.json.migrated
~/.openclaw/workspace/
```

## 安全边界

这个仓库刻意不保存：

- API key
- GitHub token
- Telegram / Discord / Slack token
- 完整私有日志
- 个人聊天上下文
- 可直接外发消息的平台凭据

文档中的 provider 名称、model 名称、目录结构和命令是实践信息，不包含可用密钥。

涉及 cron 自动执行时，尤其要谨慎处理：

- `curl` / 外部网络请求
- GitHub Issue / PR 创建或评论
- 写文件、提交、推送
- 全局自动审批

建议先通过明确 prompt、正确 workdir 和可审计脚本提升稳定性，不要默认打开高风险的全局自动审批。

## 当前仓库定位

这是一个实践手册，不是 Hermes Agent 的源码镜像。

如果你要安装或升级 Hermes Agent，请使用 Hermes 官方仓库和官方安装方式；如果你要复用本次迁移经验，从本仓库的文档和脚本开始即可。
