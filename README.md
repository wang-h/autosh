# AutoSH / ah

<p align="center">
<pre>
   ▄▄▄      █    █▄▄▄▄ ▄▄▄▄▄
  █   █    █ █   █  ▄▄ █
  █▀▀▀█   █   █  █▄▄█  █▄▄▄▄
  █   █  █     █ █         █
  █   █  █▄▄▄▄▄█ █▄▄▄▄ █▄▄▄█
</pre>
</p>

<p align="center">
  <a href="https://github.com/wang-h/autosh/stargazers"><img src="https://img.shields.io/github/stars/wang-h/autosh?style=flat-square&color=24ff24" alt="stars"></a>
  <img src="https://img.shields.io/badge/python-3.11+-24ff24?style=flat-square" alt="python">
  <img src="https://img.shields.io/badge/zsh-✓-24ff24?style=flat-square" alt="zsh">
  <img src="https://img.shields.io/badge/bash-✓-24ff24?style=flat-square" alt="bash">
  <img src="https://img.shields.io/badge/license-MIT-24ff24?style=flat-square" alt="license">
  <img src="https://img.shields.io/github/last-commit/wang-h/autosh?style=flat-square&color=24ff24" alt="updated">
</p>

> 卧槽，命令忘了怎么办！
>
> 别急：**一句中文，秒出命令**。

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
$ docker 清理无用镜像         # ← 在终端里直接写中文
# 按 Ctrl+/ → 直接变成:
$ docker system prune -f      # ← 回车就跑
```

## 安装

**一键安装：**

```bash
curl -fsSL https://wang-h.github.io/autosh/install.sh | bash
```

**从 GitHub 安装：**

```bash
uv tool install git+https://github.com/wang-h/autosh.git
# 或: pip install git+https://github.com/wang-h/autosh.git
```

然后配 Key + 切模型 + 注入 Shell：

```bash
ah config set api_key <your-api-key>
ah config set provider deepseek   # 支持: kimi / minimax / qwen / glm
ah init zsh                       # 或 ah init bash
source ~/.zshrc
```

装完就可以在终端里用了——**zsh 和 bash 都支持**，`ah init` 会自动识别。

## 使用

装完就能用，**zsh 和 bash 都行**。直接在终端里写中文，按快捷键：

```bash
# Ctrl+/ → 极速，直接出
$ docker 清理无用镜像        # 你写的
$ docker system prune -f     # ah 替换的，回车就跑

# Ctrl+Shift+/ → 三选一，带解释
$ git 回退上一次提交
  [1] git reset --soft HEAD~1  撤销提交但保留修改
  [2] git reset --mixed HEAD~1  撤销提交和暂存
  [3] git revert HEAD           生成新提交来撤销
  Pick [1-3]: █                 # 回车默认选 1
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
