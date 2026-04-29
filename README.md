# AutoSH / ah

一句中文，秒出命令。

AutoSH（`ah`）是给中文程序员的终端 AI 助手。在 zsh 里写中文，按一下就出命令。

```
天下苦 Bash 久已，快来 ah 一下。
```

## 两种模式



| 快捷键 | 模式 | 效果 |
|--------|------|------|
| `Ctrl+/` | 极速 | 直接出命令，一步到位 |
| `Ctrl+Shift+/` | 选择 | 弹出三个候选 + 中文解释，看懂了选 |

> `/` 和 `?` 是同一个键，所以 `Ctrl+Shift+/` = 按住 Ctrl+Shift 再按 `/`。

```bash
$ docker 清理无用镜像

# Ctrl+/  → docker system prune -f

# Ctrl+Shift+/  →
#   [1] docker system prune -f  清理所有未使用的镜像和容器
#   [2] docker rm $(docker ps -aq)  删除所有已停止的容器
#   [3] docker image prune -a  删除所有未被引用的镜像
```

## 安装

```bash
# 安装 CLI
pip install autosh

# 或使用 uv
uv tool install autosh
```

## 快速开始

```bash
# 1. 配置 API Key
ah config set api_key <your-api-key>
# 切 provider 会自动匹配模型和地址
ah config set provider deepseek   # 或其他: kimi / minimax / qwen / glm

# 2. 安装 Shell 集成
ah init zsh       # 或 ah init bash

# 3. 重新加载
source ~/.zshrc   # 或 source ~/.bashrc
```

## 命令

| 命令 | 说明 |
|------|------|
| `ah init <zsh\|bash>` | 安装 Shell 集成 |
| `ah config` | 查看当前配置 |
| `ah config set <key> <value>` | 设置配置项（切 provider 一键切模型） |
| `ah suggest <中文描述>` | 直接生成命令建议 |
| `ah doctor` | 检查环境配置 |

## 配置

`~/.autosh/config.yaml`：

```yaml
provider: deepseek
model: deepseek-v4-flash
base_url: https://api.deepseek.com/anthropic
api_key: sk-xxx
```

| 配置项 | 说明 |
|--------|------|
| `provider` | AI 提供商：`deepseek` / `kimi` / `minimax` / `qwen` / `glm` |
| `model` | 模型名称（切 provider 自动更新） |
| `base_url` | API 地址（切 provider 自动更新） |
| `api_key` | API 密钥 |

```bash
ah config set provider kimi      # 切到 Kimi
ah config set provider deepseek  # 切回来
```

## 自定义快捷键

编辑 `~/.autosh/autosh.zsh`：

```zsh
# 极速模式（bindkey '^_'  = Ctrl+/）
bindkey '^_' autosh-fast

# 选择模式（bindkey '^?' = Ctrl+Shift+/）
bindkey '^?' autosh-pick
```

## 原理

读取当前命令行缓冲区 → 发送给 AI API → 模型生成命令 → 替换回命令行。不上传命令历史。

## 环境要求

- Python 3.11+
- zsh 或 bash
- 任一提供商 API Key（DeepSeek / Kimi / MiniMax / Qwen / GLM）

## License

MIT
