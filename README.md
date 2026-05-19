# LLM Arena V2 - 大模型竞技场

> 让 50+ 个大模型供应商内卷竞争，优胜劣汰！

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-16+-blue.svg)](https://nodejs.org)
[![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg)](https://python.org)
[![npx](https://img.shields.io/badge/npx-install-orange.svg)](https://github.com/Han-cy830/llm-arena)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Han-cy830/llm-arena/pulls)

**10维评分** | **Elo 评级** | **emoji 心情** | **成就系统** | **用户否决权至高无上**

```bash
npx github:Han-cy830/llm-arena  # 一键安装
```

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
- **10维评分**: Token效率/思考速度/回答质量/一致性/错误率/性价比/延迟稳定/进步趋势/胜率/用户满意度
- **Elo 评级**: 国际象棋级 Elo 评分系统，K=32
- **emoji 心情**: 19种心情动态变化 (😎王者/😤志在必得/🔥势头正猛/🦄黑马/🤡飘了/😢连败中...)
- **成就系统**: 19种成就 (🩸首战告捷/💀五杀/🌪️势不可挡/👑逆袭之王/🗡️屠龙勇士...)
- **四榜排名**: 日榜 / 周榜 / 月榜 / 总榜
- **连胜追踪**: 连胜🔥连败💔动态展示，最佳连胜记录
- **用户否决权**: 你的排名你做主，无视算法直接指定，至高无上
- **用户满意度**: 直接给模型打分 (arena rate)
- **API 优先级**: 排名最高的模型自动获得更高调用优先级
- **盲测对决**: 借鉴 Chatbot Arena，隐藏模型身份让用户投票
- **段位系统**: 传奇/钻石/黄金/白银/青铜/黑铁，游戏化排名
- **模型人格**: trash talk 系统，对战后互相嘲讽
- **荣誉殿堂 / 耻辱墙**: 冠军荣耀 vs 垫底耻辱
- **10维雷达图**: ASCII 终端可视化，直观对比模型实力

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

### 竞技场 (10维评分 + Elo)

```bash
arena register <id> [name]         # 注册模型
arena record <id> <t> <s> <q>     # 记录表现 (token/耗时/质量)
arena battle <json_file>           # 多模型对决 (自动Elo评级)
arena veto <id> <rank|ban>         # 用户否决权 (至高无上)
arena rate <id> <0-10>             # 用户满意度评分
arena weights <t> <s> <q>         # 调整权重
```

### 对战竞技场 (借鉴 Chatbot Arena)

```bash
battle blind <a> <b>               # 盲测对决 (隐藏身份投票)
battle vote <a> <b> <winner>       # 投票 (winner=a/b/draw)
battle radar <model_id>            # 10维雷达图
battle compare <a> <b>             # 双模型对比
battle leaderboard [period]        # 增强排行榜 (段位系统)
battle fame                        # 荣誉殿堂
battle shame                       # 耻辱墙
battle weekly                      # 本周奖项
```

### 排名展示 (含心情)

```bash
rank                               # 展示所有排行榜 (含emoji心情)
rank daily                         # 日榜
rank weekly                        # 周榜
rank monthly                       # 月榜
rank total                         # 总榜
rank detail <model_id>             # 模型详情 (10维雷达)
rank mood                          # 心情总览
rank achievements                  # 成就殿堂
rank export [period]               # 导出 Markdown
```

### 快捷操作

```bash
quick <provider_id>                # 快速切换并显示配置
status                             # 完整状态面板
```

## 评分机制 (10维)

| 维度 | 权重 | 说明 |
|------|------|------|
| ⚡ Token 效率 | 15% | 越少越好，10000 token 为基准 |
| ⏱️ 思考速度 | 10% | 越快越好，60 秒为基准 |
| 🎯 回答质量 | 20% | 0-10 分，自动或手动评估 |
| 📊 一致性 | 10% | 多次调用的稳定性 |
| 🛡️ 错误率 | 8% | 越低越好 |
| 💰 性价比 | 10% | 质量/token 比值 |
| 📈 延迟稳定 | 7% | P95/P50 比值越接近1越好 |
| 🔄 进步趋势 | 5% | 最近表现 vs 之前表现 |
| ⚔️ 胜率 | 10% | 对决胜率 |
| ❤️ 用户满意 | 5% | 用户手动评分 |

### Elo 评级

国际象棋级 Elo 评分系统，初始 1200 分，K=32。击败强敌涨分多，输给弱敌扣分多。

### emoji 心情系统 (19种)

| 心情 | emoji | 触发条件 |
|------|-------|---------|
| 王者 | 😎 | 排名第一 |
| 志在必得 | 😤 | 前三名 |
| 黑马 | 🦄 | 新模型高分 |
| 势头正猛 | 🔥 | 趋势上升 |
| 疯狂内卷 | ⚙️ | 高频使用+进步 |
| 稳坐钓鱼台 | 😏 | 前五且稳定 |
| 奋起直追 | 💪 | 排名中游 |
| 压力山大 | 😰 | 排名下降 |
| 连胜中 | 🥳 | 连胜5+ |
| 连败中 | 😢 | 连败5+ |
| 逆袭重生 | �🦅 | 从低谷回升 |
| 飘了 | 🤡 | 曾经领先但质量下降 |
| 摸鱼中 | 😴 | 长时间无活动 |
| 摆烂了 | 🦥 | 活跃度低+下降 |
| 新来的 | 🐣 | 不足3场 |
| 老将 | 🧓 | 50+场对决 |
| 已封禁 | 💀 | 被用户封禁 |

### 成就系统 (19种)

| 成就 | emoji | 条件 |
|------|-------|------|
| 首战告捷 | 🩸 | 赢得第一场 |
| 帽子戏法 | 🎩 | 连胜3场 |
| 五杀 | 💀 | 连胜5场 |
| 势不可挡 | 🌪️ | 连胜10场 |
| 超神 | ⚡ | 连胜20场 |
| 铁人 | 🦾 | 参与100场 |
| 完美主义 | 💎 | 单次质量10分 |
| 极速恶魔 | ⏱️ | 响应<1秒 |
| 省钱达人 | 💰 | Token效率>9 |
| 逆袭之王 | 👑 | 从10+升到前3 |
| 稳如老狗 | 📊 | 连续10场质量>8 |
| 屠龙勇士 | 🗡️ | 击败高5位以上的对手 |
| 马拉松选手 | 🏃 | 连续7天每天活跃 |
| 零失误 | ✨ | 连续20场无错误 |
| 进步之星 | 📈 | 效率分提升>2 |
| 冠军 | 🏆 | 总榜第一 |
| 月度MVP | 🌟 | 月榜第一 |
| 周度之星 | ⭐ | 周榜第一 |
| 用户最爱 | ❤️ | 被用户强制第一 |

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
│   ├── mcp_server.py     # MCP Server (任何 AI 工具可用)
│   ├── arena_v2.py       # V2 竞技场引擎 (10维+Elo+心情+成就)
│   ├── display_v2.py     # V2 排名展示 (emoji心情)
│   ├── battle_arena.py   # 对战竞技场 (盲测/段位/雷达图)
│   ├── arena.py          # V1 竞技场引擎 (兼容)
│   ├── switcher.py       # API 供应商切换器
│   ├── api_router.py     # API 智能路由器
│   ├── evaluator.py      # 自动评估器
│   └── display.py        # V1 排名展示 (兼容)
├── vscode-extension/     # VS Code 扩展
│   ├── src/
│   │   ├── extension.ts  # 扩展入口
│   │   ├── ArenaCli.ts   # CLI 执行器
│   │   ├── RankingsPanel.ts
│   │   └── ModelTreeProvider.ts
│   ├── package.json
│   └── media/
├── data/
│   ├── providers.json    # 50+ 供应商配置
│   ├── scores_v2.json    # V2 模型数据（自动）
│   ├── battle_history.json # 对决历史（自动）
│   ├── config_v2.json    # V2 权重配置（自动）
│   ├── overrides.json    # 用户否决（自动）
│   └── scores.json       # V1 数据（兼容)
├── skill/
│   └── SKILL.md          # Claude Code Skill 定义
├── requirements.txt      # Python 依赖 (mcp)
├── package.json          # npx 包配置
└── README.md
```

## MCP Server

任何 AI 工具（Claude Code、Cursor、Claude Desktop）都能通过 MCP 协议调用 LLM Arena。

### 安装

```bash
pip install mcp
```

### 使用

```bash
# stdio 模式（本地客户端）
python src/mcp_server.py

# HTTP 模式（远程访问）
python src/mcp_server.py --http --port 8000
```

### Claude Code 配置

在项目根目录创建 `.mcp.json`：

```json
{
  "mcpServers": {
    "llm-arena": {
      "command": "python",
      "args": ["src/mcp_server.py"]
    }
  }
}
```

### Claude Desktop 配置

编辑 `claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "llm-arena": {
      "command": "python",
      "args": ["/path/to/llm-arena/src/mcp_server.py"]
    }
  }
}
```

### 可用工具 (12个)

| 工具 | 说明 |
|------|------|
| `register_model` | 注册模型 |
| `record_match` | 记录单次表现 |
| `record_battle` | 多模型对决 |
| `get_ranking` | 获取排名 |
| `get_top_model` | 获取最佳模型 |
| `user_veto` | 用户否决权 |
| `set_weights` | 调整评分权重 |
| `list_providers` | 列出供应商 |
| `switch_provider` | 切换供应商 |
| `get_active_config` | 当前配置 |
| `vote_battle` | 盲测投票 |
| `compare_models` | 双模型对比 |

### 可用资源 (5个)

| 资源 | 说明 |
|------|------|
| `arena://ranking/{period}` | 排名数据 |
| `arena://providers` | 供应商列表 |
| `arena://config` | 当前配置 |
| `arena://mood` | 心情总览 |
| `arena://achievements` | 成就数据 |

## VS Code Extension

在 VS Code 中直接查看排名、记录对决、切换供应商。

### 安装

```bash
cd vscode-extension
npm install
npm run compile
# 按 F5 启动调试
```

### 功能

- **侧边栏模型树** — 排名、Elo、心情 emoji、效率分
- **排名面板** — 日/周/月/总榜，可刷新
- **记录对决** — 输入框记录模型表现
- **切换供应商** — 快速选择 50+ 供应商
- **模型详情** — 点击查看 10 维数据
- **状态栏** — 快速访问排名

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

## 为什么用 LLM Arena？

| 痛点 | 解决方案 |
|------|---------|
| 不知道哪个模型最好 | 10维评分 + Elo 自动排名 |
| 手动切换 API 太麻烦 | 50+ 供应商一键切换 |
| 排名太死板 | emoji 心情动态变化，成就系统 |
| 算法排名不靠谱 | 用户否决权至高无上 |
| 只看质量不看成本 | Token效率 + 性价比纳入评分 |
| 不知道模型在进步还是退步 | 趋势分析 + 进步趋势维度 |

## 贡献

欢迎贡献！查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Han-cy830/llm-arena&type=Date)](https://star-history.com/#Han-cy830/llm-arena&Date)

## License

MIT
