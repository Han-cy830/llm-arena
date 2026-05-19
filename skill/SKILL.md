---
name: llm-arena
description: Use when evaluating multiple LLMs, comparing model performance, switching API providers, managing model rankings, or routing API calls to the best model. Supports 50+ providers with 10-dimension scoring, Elo ratings, emoji moods, achievements, blind battles, and user veto power.
---

# LLM Arena V2 - 大模型竞技场

## Overview

50+ 供应商大模型内卷竞技场。10维评分 + Elo评级 + emoji心情 + 成就系统 + 盲测对决 + 段位系统。用户否决权至高无上。

## When to Use

- 切换 API 供应商或模型
- 对比多个大模型表现（雷达图、双模型对比）
- 查看模型排名（日/周/月/总榜、段位系统）
- 盲测对决投票
- 管理 API 优先级
- 添加自定义供应商

## Quick Start

```bash
python src/cli.py provider list          # 查看所有供应商
python src/cli.py provider switch deepseek  # 切换到 DeepSeek
python src/cli.py rank                    # 查看所有排行榜
python src/cli.py battle leaderboard      # 增强排行榜 (段位)
python src/cli.py battle fame             # 荣誉殿堂
python src/cli.py status                  # 完整状态面板
```

## CLI Commands

### 供应商管理
| 命令 | 说明 |
|------|------|
| `provider list` | 列出 50+ 供应商 |
| `provider switch <id> [model]` | 切换供应商/模型 |
| `provider active` | 当前配置 |
| `provider env` | 生成环境变量 |
| `provider add <id> <json>` | 添加自定义供应商 |

### 竞技场
| 命令 | 说明 |
|------|------|
| `arena register <id> [name]` | 注册模型 |
| `arena record <id> <t> <s> <q>` | 记录表现 (token/耗时/质量) |
| `arena battle <json>` | 多模型对决 |
| `arena veto <id> <rank\|ban>` | 用户否决权 |
| `arena rate <id> <0-10>` | 用户满意度 |

### 对战竞技场
| 命令 | 说明 |
|------|------|
| `battle blind <a> <b>` | 盲测对决 (隐藏身份) |
| `battle vote <a> <b> <w>` | 投票 (w=a/b/draw) |
| `battle radar <model>` | 10维雷达图 |
| `battle compare <a> <b>` | 双模型对比 |
| `battle leaderboard [period]` | 段位排行榜 |
| `battle fame` | 荣誉殿堂 |
| `battle shame` | 耻辱墙 |
| `battle weekly` | 本周奖项 |

### 排名
| 命令 | 说明 |
|------|------|
| `rank [daily\|weekly\|monthly\|all]` | 排行榜 |
| `rank detail <model>` | 模型详情 |
| `rank mood` | 心情总览 |
| `rank achievements` | 成就殿堂 |

## Scoring (10维)

| 维度 | 权重 | 说明 |
|------|------|------|
| Token 效率 | 15% | 越少越好 |
| 思考速度 | 10% | 越快越好 |
| 回答质量 | 20% | 越高越好 |
| 一致性 | 10% | 稳定性 |
| 错误率 | 8% | 越低越好 |
| 性价比 | 10% | 质量/token |
| 延迟稳定 | 7% | P95/P50 |
| 进步趋势 | 5% | 近期vs历史 |
| 胜率 | 10% | 对决胜率 |
| 用户满意 | 5% | 手动评分 |

## User Veto

- `arena veto <model> 1` — 强制第1名
- `arena veto <model> ban` — 封禁
- `arena veto <model> 0` — 取消否决
