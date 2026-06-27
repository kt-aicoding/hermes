# Hermes Local Agent Practice

这个仓库沉淀一次从 OpenClaw 迁移到 Hermes Agent 的本机实践：安装、模型接入、开机自启、cron 迁移、任务修复和验证方法。

重点不是复制某台机器的私有配置，而是记录可复用的方法和踩坑点，方便后续团队成员搭建自己的 Hermes 本地智能体环境。

## 实践结论

- Hermes 可以作为 OpenClaw 的本地替代运行：支持 CLI、gateway、launchd 开机自启和 cron 定时任务。
- 火山引擎 Ark 可以通过 Hermes custom provider 接入，实测 `chat_completions` 可用。
- OpenClaw cron 数据可以迁移到 Hermes，但要注意不能只迁移任务名；必须恢复 OpenClaw `payload.message` 作为 Hermes `prompt`。
- Hermes cron 在没有消息平台时可以用 `deliver=local`，输出保存在本机 `~/.hermes/cron/output/`。
- 自动审批外部命令是高风险开关。涉及 GitHub Issue/PR、curl、写文件的任务，建议先通过更明确的 prompt 和 workdir 提升稳定性，不默认打开全局自动审批。

## 仓库结构

```text
.
├── README.md
├── docs
│   ├── 01-install-and-provider.md
│   ├── 02-openclaw-migration.md
│   ├── 03-launchd-cron.md
│   ├── 04-cron-optimization.md
│   └── 05-verification-checklist.md
└── scripts
    ├── optimize-cron-from-openclaw.py
    └── verify-hermes.sh
```

## 快速验证

```bash
./scripts/verify-hermes.sh
```

这个脚本只做只读检查：

- Hermes CLI 是否可用
- LLM 是否能返回 `OK`
- gateway 是否被 launchd 托管
- cron scheduler 是否运行
- cron 任务数量、prompt/workdir 质量
- OpenClaw gateway 是否仍在运行

## 关键路径

以下路径是本次实践中的默认布局，使用时按自己的机器调整：

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

本仓库不保存：

- API key、GitHub token、Telegram token
- 完整私有日志
- 个人聊天上下文
- 可直接外发消息的平台凭据

文档中出现的 provider/model 名称、目录结构和命令是实践信息，不包含密钥。

