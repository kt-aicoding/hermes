# Hermes 安装与 Ark Provider 接入

## 安装位置

本次实践使用官方安装方式安装 Hermes Agent，最终本机布局：

```text
$HOME/.hermes/hermes-agent
$HOME/.hermes/hermes-agent/venv/bin/hermes
$HOME/.local/bin/hermes
$HOME/.npm-global/bin/hermes
```

验证版本：

```bash
hermes --version
```

实践环境中版本为：

```text
Hermes Agent v0.17.0
Python 3.11.x
OpenAI SDK 2.x
```

## Ark Provider 配置

Hermes 使用 custom provider 方式接入火山引擎 Ark。

有效配置要点：

```yaml
providers:
  ark:
    name: Volcengine Ark
    api: https://ark.cn-beijing.volces.com/api/coding/v3
    key_env: ARK_API_KEY
    default_model: doubao-seed-2-0-code-preview-260215
    transport: chat_completions

model:
  provider: custom:volcengine-ark
  default: doubao-seed-2-0-code-preview-260215
  api_mode: chat_completions
```

`.env` 中只保存环境变量名对应的值，不要提交真实 key：

```bash
ARK_API_KEY=...
```

## 连通性验证

```bash
hermes -z '只回复 OK'
```

预期输出：

```text
OK
```

## 注意事项

- Ark 标准 `/api/v3` 和 coding `/api/coding/v3` 行为可能不同。本次实践中 coding endpoint 对代码模型可用。
- `hermes doctor` 可能提示 `No API key found in $HOME/.hermes/.env`，因为它不一定识别自定义 `ARK_API_KEY`。只要 `hermes -z` 实际返回正常，就说明 runtime provider 可用。
- 不要把 `.env`、shell 历史、命令输出中的 token 写入仓库。

