# LLM Arena - 大模型竞技场

让 50+ 个大模型供应商内卷竞争，优胜劣汰！数据驱动排名，用户一票否决。

## 一键安装

```bash
npx github:Han-cy830/llm-arena
```

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
| 中转平台 | 胜算云, PatewayAI, AiHubMix, DMXAPI, OpenRouter, TheRouter |
| 编码专用 | 百炼 Coding, Kimi Coding, KAT-Coder, PackyCode, RelaxyCode |
| 国内平台 | Zhipu GLM, MiniMax, SiliconFlow, ModelScope, 优云智算, CTok.ai |
| 其他 | ClaudeAPI, ClaudeCN, RunAPI, Cubence, AIGoCode, RightCode, AICodeMirror 等 |

## 快速开始

```bash
# 查看所有供应商
python src/cli.py provider list

# 切换到 DeepSeek
python src/cli.py provider switch deepseek

# 切换到 OpenRouter 并指定模型
python src/cli.py provider switch openrouter "anthropic/claude-sonnet-4"

# 查看当前配置
python src/cli.py provider active

# 生成环境变量
python src/cli.py provider env
```

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

## API 路由

```python
from src.arena import LLMArena
from src.api_router import ArenaRouter

router = ArenaRouter()
best = router.get_best_model()       # 当前最优模型
priority = router.get_priority_list() # 完整优先级列表
result = router.call("你的 prompt")   # 自动路由调用
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
│   └── SKILL.md          # Claude Code Skill
└── README.md
```

## License

MIT
