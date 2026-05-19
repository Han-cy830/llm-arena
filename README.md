# LLM Arena - 大模型竞技场

让多个大模型内卷竞争，优胜劣汰！数据驱动排名，用户一票否决。

## 核心特性

- **三维评分**: Token 效率 + 思考速度 + 回答质量
- **多周期排名**: 日榜 / 周榜 / 月榜 / 总榜
- **用户否决权**: 你的排名你做主，无视算法直接指定
- **API 优先级**: 排名最高的模型自动获得更高调用优先级
- **自动路由**: 智能选择最优模型处理请求

## 快速开始

```bash
# 注册模型
python src/arena.py register gpt-4 "GPT-4"
python src/arena.py register claude-sonnet "Claude Sonnet"
python src/arena.py register deepseek-v3 "DeepSeek V3"

# 记录表现 (模型ID token数 耗时秒 质量分0-10)
python src/arena.py record gpt-4 1500 3.2 8.5
python src/arena.py record claude-sonnet 1200 2.8 9.0
python src/arena.py record deepseek-v3 1800 4.1 7.5

# 查看排名
python src/arena.py ranking
```

## 评分机制

| 维度 | 权重 | 规则 |
|------|------|------|
| Token 效率 | 35% | 越少越好，10000 token 为基准 |
| 思考速度 | 30% | 越快越好，60 秒为基准 |
| 回答质量 | 35% | 0-10 分，可自动评估或手动打分 |

**效率分** = 加权平均，决定排名和 API 优先级。

## 用户否决权

用户拥有最高权力，可以直接否决算法排名：

```bash
# 强制指定排名
python src/arena.py veto gpt-4 1       # GPT-4 强制第1名

# 封禁模型
python src/arena.py veto deepseek-v3 ban

# 取消否决
python src/arena.py veto gpt-4 0
```

## 多模型对决

准备 JSON 文件批量记录：

```json
[
  {"model_id": "gpt-4", "tokens": 1500, "think_time": 3.2, "quality": 8.5},
  {"model_id": "claude-sonnet", "tokens": 1200, "think_time": 2.8, "quality": 9.0},
  {"model_id": "deepseek-v3", "tokens": 1800, "think_time": 4.1, "quality": 7.5}
]
```

```bash
python src/arena.py battle match.json
```

## API 路由

```python
from src.arena import LLMArena
from src.api_router import ArenaRouter

router = ArenaRouter()

# 获取最优模型
best = router.get_best_model()

# 获取优先级列表
priority = router.get_priority_list()

# 自动路由调用
result = router.call("你的 prompt")

# 调用并自动评分
result = router.call_and_score("prompt", quality=8.5)
```

## 自动评估器

```python
from src.evaluator import create_evaluator

evaluator = create_evaluator("composite")
quality = evaluator("模型的回答内容")
```

## 权重调整

```bash
# token权重 速度权重 质量权重
python src/arena.py weights 0.4 0.2 0.4
```

## 项目结构

```
llm-arena/
├── src/
│   ├── arena.py          # 核心竞技场引擎
│   ├── api_router.py     # API 路由器
│   └── evaluator.py      # 自动评估器
├── skill/
│   └── SKILL.md          # Claude Code Skill 定义
├── data/                 # 数据存储（自动创建）
│   ├── scores.json
│   ├── overrides.json
│   └── config.json
└── README.md
```

## License

MIT
