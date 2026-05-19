---
name: llm-arena
description: Use when evaluating multiple LLMs, comparing model performance, managing model rankings, or routing API calls to the best model
---

# LLM Arena - 大模型竞技场

## Overview

让多个大模型内卷竞争的竞技场系统。通过 token 效率、思考速度、回答质量三个维度自动评分，优胜者获得更高 API 调用优先级。

**核心原则:** 数据驱动，用户至上。用户的否决权高于一切算法排名。

## When to Use

- 需要对比多个大模型的表现
- 想要自动选择最优模型进行 API 调用
- 管理模型排名和优先级
- 记录和分析模型性能数据

## Quick Start

```bash
# 注册模型
python src/arena.py register gpt-4 "GPT-4"
python src/arena.py register claude-sonnet "Claude Sonnet"
python src/arena.py register deepseek-v3 "DeepSeek V3"

# 记录单次表现
python src/arena.py record gpt-4 1500 3.2 8.5

# 多模型对决（准备 JSON 文件）
python src/arena.py battle match_data.json

# 查看排名
python src/arena.py ranking          # 总榜
python src/arena.py ranking daily    # 日榜
python src/arena.py ranking weekly   # 周榜
python src/arena.py ranking monthly  # 月榜

# 用户否决权
python src/arena.py veto gpt-4 1     # 强制第1名
python src/arena.py veto deepseek-v3 ban  # 封禁

# API 优先级
python src/arena.py priority
```

## Scoring System

三个维度，总分 0-10：

| 维度 | 默认权重 | 说明 |
|------|----------|------|
| Token 效率 | 35% | 消耗越少得分越高 |
| 思考速度 | 30% | 响应越快得分越高 |
| 回答质量 | 35% | 质量越高得分越高 |

效率分 = 加权平均分，用于排名和 API 优先级。

## Ranking Periods

- **日榜** (daily): 最近 24 小时表现
- **周榜** (weekly): 最近 7 天表现
- **月榜** (monthly): 最近 30 天表现
- **总榜** (all): 全部历史表现

## User Veto Power

用户拥有绝对否决权：

- `veto <model> <rank>` — 强制指定排名（无视算法）
- `veto <model> ban` — 封禁模型（不参与排名和路由）
- `veto <model> 0` — 取消否决

## API Routing

```python
from src.api_router import ArenaRouter

router = ArenaRouter()
best = router.get_best_model()  # 当前最优模型
table = router.get_routing_table()  # 完整路由表
result = router.call("你的 prompt")  # 自动路由调用
```

## Weights Tuning

```bash
# 调整权重（三个值之和建议为 1.0）
python src/arena.py weights 0.4 0.2 0.4  # 更重视质量和token
```

## Data Storage

所有数据存储在 `data/` 目录：
- `scores.json` — 模型分数和历史
- `overrides.json` — 用户否决记录
- `config.json` — 权重配置
