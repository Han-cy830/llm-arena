# LLM Arena V2 - 大模型竞技场

让 50+ 个大模型供应商内卷竞争，优胜劣汰！10维评分 + Elo评级 + emoji心情 + 成就系统，用户一票否决。

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
│   ├── arena_v2.py       # V2 竞技场引擎 (10维+Elo+心情+成就)
│   ├── display_v2.py     # V2 排名展示 (emoji心情)
│   ├── arena.py          # V1 竞技场引擎 (兼容)
│   ├── switcher.py       # API 供应商切换器
│   ├── api_router.py     # API 智能路由器
│   ├── evaluator.py      # 自动评估器
│   └── display.py        # V1 排名展示 (兼容)
├── data/
│   ├── providers.json    # 50+ 供应商配置
│   ├── scores_v2.json    # V2 模型数据（自动）
│   ├── battle_history.json # 对决历史（自动）
│   ├── config_v2.json    # V2 权重配置（自动）
│   ├── overrides.json    # 用户否决（自动）
│   └── scores.json       # V1 数据（兼容）
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
