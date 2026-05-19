# LLM Arena - 大模型竞技场

让 50+ 个大模型供应商内卷竞争，优胜劣汰！数据驱动排名，用户一票否决。

---

## 安装方式

### 方式一：npx 一键安装（推荐）

```bash
npx github:Han-cy830/llm-arena
```

自动完成所有配置，无需手动操作。

### 方式二：Git 克隆

```bash
git clone https://github.com/Han-cy830/llm-arena.git ~/.agents/skills/llm-arena
```

然后创建 Claude Code 链接：

```bash
# Windows (CMD)
mklink /J "%APPDATA%\claude\skills\llm-arena" "%USERPROFILE%\.agents\skills\llm-arena"

# Windows (PowerShell)
New-Item -ItemType Junction -Path "$env:APPDATA\claude\skills\llm-arena" -Target "$env:USERPROFILE\.agents\skills\llm-arena"

# macOS / Linux
ln -s ~/.agents/skills/llm-arena ~/.claude/skills/llm-arena
```

### 方式三：下载 ZIP

1. 打开 https://github.com/Han-cy830/llm-arena
2. 点击绿色 **Code** 按钮 → **Download ZIP**
3. 解压到以下目录之一：

```
# Windows
%USERPROFILE%\.agents\skills\llm-arena

# macOS / Linux
~/.agents/skills/llm-arena
```

4. 创建 Claude Code 链接（同方式二的链接命令）

### 方式四：curl 下载安装脚本

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/Han-cy830/llm-arena/master/bin/setup.js | node
```

```bash
# Windows (PowerShell)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Han-cy830/llm-arena/master/bin/setup.js" -OutFile "$env:TEMP\llm-arena-setup.js"; node "$env:TEMP\llm-arena-setup.js"
```

### 方式五：npm 全局安装（即将上线）

```bash
npm install -g llm-arena
llm-arena install
```

---

## 安装步骤详解

### 前置要求

| 依赖 | 必需 | 安装命令 |
|------|:----:|---------|
| **Node.js 16+** | ✅ | [nodejs.org](https://nodejs.org) 或 `winget install OpenJS.NodeJS.LTS` |
| **Git** | ✅ | [git-scm.com](https://git-scm.com) 或 `winget install Git.Git` |
| **Python 3.10+** | 可选 | [python.org](https://python.org) 或 `winget install Python.Python.3.12` |

> Python 仅用于 CLI 命令行工具，skill 本身不依赖 Python。

### 步骤 1：安装

选择上面任意一种安装方式。推荐 npx：

```bash
npx github:Han-cy830/llm-arena
```

安装成功后会看到：

```
✅ Skill 文件下载完成
✅ Claude Code skill 链接创建成功

🏆 LLM Arena Skill 安装成功!
```

### 步骤 2：配置 API Key

选择你要使用的供应商，设置对应的环境变量：

```bash
# Claude Official
export ANTHROPIC_API_KEY="sk-ant-xxx"

# DeepSeek
export DEEPSEEK_API_KEY="sk-xxx"

# OpenRouter
export OPENROUTER_API_KEY="sk-or-xxx"

# 火山引擎
export VOLC_API_KEY="xxx"

# 百炼
export DASHSCOPE_API_KEY="sk-xxx"
```

Windows 用户：
```powershell
# PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-xxx"
# 或永久设置
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-xxx", "User")
```

### 步骤 3：验证安装

```bash
# 查看供应商列表（确认 skill 已加载）
python src/cli.py provider list

# 切换到你想用的供应商
python src/cli.py provider switch deepseek

# 查看当前配置
python src/cli.py provider active

# 查看排名（首次为空，使用后会自动积累数据）
python src/cli.py rank
```

### 步骤 4：在 Claude Code 中使用

重新打开 Claude Code，输入以下任意内容即可触发 skill：

- `/llm-arena`
- "帮我切换到 DeepSeek"
- "查看模型排名"
- "哪个模型最好"

---

## 核心特性

- **50+ 供应商**: Claude Official、胜算云、火山、DeepSeek、Gemini、OpenRouter 等全覆盖
- **灵活切换**: 一键切换 API 供应商和模型
- **三维评分**: Token 效率 + 思考速度 + 回答质量
- **四榜排名**: 日榜 / 周榜 / 月榜 / 总榜
- **用户否决权**: 你的排名你做主，无视算法直接指定
- **API 优先级**: 排名最高的模型自动获得更高调用优先级
- **自定义供应商**: 支持添加任意 OpenAI 兼容 API

## 支持的供应商 (50+)

| 类别 | 供应商 |
|------|--------|
| 官方 API | Claude Official, Codex, GitHub Copilot, Gemini Native, DeepSeek |
| 国内大厂 | 火山 Agentplan, BytePlus, DouBaoSeed, 百度千帆, 百炼, Kimi, 阶跃星辰 |
| 云服务 | AWS Bedrock (AKSK/API Key), Nvidia |
| 中转平台 | 胜算云, PatewayAI, AiHubMix, DMXAPI, OpenRouter, TheRouter, Novita AI |
| 编码专用 | 百炼 Coding, Kimi Coding, KAT-Coder, PackyCode, RelaxyCode, 优云智算 Coding |
| 国内平台 | Zhipu GLM, MiniMax, SiliconFlow, ModelScope, Xiaomi MiMo, Longcat, BaiLing |
| 其他 20+ | ClaudeAPI, ClaudeCN, RunAPI, Cubence, AIGoCode, RightCode, AICodeMirror, AICoding, CrazyRouter, SSSAiCode, 优云智算, Micu, CTok.ai, E-FlowCode, LionCCAPI, PIPELLM, LemonData 等 |

## CLI 命令大全

### 供应商管理

```bash
provider list                      # 列出所有供应商
provider switch <id> [model]       # 切换供应商/模型
provider active                    # 查看当前配置
provider info <id>                 # 供应商详情
provider history [limit]           # 切换历史
provider env                       # 生成环境变量配置
provider add <id> <json_file>      # 添加自定义供应商
provider remove <id>               # 移除供应商
```

### 竞技场

```bash
arena register <id> [name]         # 注册模型
arena record <id> <tokens> <time> <quality>  # 记录表现
arena battle <json_file>           # 多模型对决
arena veto <id> <rank|ban>         # 用户否决权
arena weights <token> <speed> <quality>  # 调整权重
```

### 排名展示

```bash
rank                               # 展示所有排行榜
rank daily                         # 日榜
rank weekly                        # 周榜
rank monthly                       # 月榜
rank total                         # 总榜
rank detail <model_id>             # 模型详情
rank summary                       # 竞技场概览
rank export [period]               # 导出 Markdown
```

### 快捷操作

```bash
quick <provider_id>                # 快速切换并显示配置
status                             # 完整状态面板
```

## 评分机制

| 维度 | 权重 | 说明 |
|------|------|------|
| Token 效率 | 35% | 越少越好，10000 token 为基准 |
| 思考速度 | 30% | 越快越好，60 秒为基准 |
| 回答质量 | 35% | 0-10 分，自动或手动评估 |

**效率分** = 加权平均，决定排名和 API 优先级。

## 用户否决权

```bash
# 强制指定排名（无视算法）
arena veto gpt-4 1

# 封禁模型
arena veto deepseek ban

# 取消否决
arena veto gpt-4 0
```

## 自定义供应商

创建 JSON 文件：

```json
{
  "display_name": "My Custom API",
  "base_url": "https://my-api.com/v1",
  "default_model": "my-model",
  "models": ["my-model", "my-model-v2"],
  "api_type": "openai",
  "env_key": "MY_API_KEY",
  "max_tokens": 4096,
  "supports_streaming": true
}
```

```bash
provider add my-api my-api.json
```

## 项目结构

```
llm-arena/
├── bin/
│   └── setup.js          # npx 安装脚本
├── src/
│   ├── cli.py            # 统一 CLI 入口
│   ├── arena.py          # 核心竞技场引擎
│   ├── switcher.py       # API 供应商切换器
│   ├── api_router.py     # API 智能路由器
│   ├── evaluator.py      # 自动评估器
│   └── display.py        # 排名展示系统
├── data/
│   ├── providers.json    # 50+ 供应商配置
│   ├── scores.json       # 模型分数（自动）
│   ├── overrides.json    # 用户否决（自动）
│   └── config.json       # 权重配置（自动）
├── skill/
│   └── SKILL.md          # Claude Code Skill 定义
├── package.json          # npx 包配置
└── README.md
```

## 常见问题

### npx 命令找不到

```bash
# 安装 Node.js
winget install OpenJS.NodeJS.LTS
```

### Python 命令找不到

```bash
# 安装 Python
winget install Python.Python.3.12
```

### 安装后 Claude Code 中无法触发

1. 确认链接存在：
```bash
# Windows
dir "%APPDATA%\claude\skills\llm-arena"

# macOS / Linux
ls -la ~/.claude/skills/llm-arena
```

2. 重启 Claude Code

### 如何更新

```bash
# 重新运行 npx 安装即可覆盖更新
npx github:Han-cy830/llm-arena
```

### 如何卸载

```bash
npx github:Han-cy830/llm-arena uninstall
```

## License

MIT
