---
name: llm-arena
description: Use when evaluating multiple LLMs, comparing model performance, switching API providers, managing model rankings, or routing API calls to the best model. Supports 50+ providers with daily/weekly/monthly rankings and user veto power.
---

# LLM Arena - 大模型竞技场

## Overview

50+ 供应商大模型内卷竞技场。三维评分（Token效率/速度/质量），四榜排名（日/周/月/总），用户否决权一票制，API 智能路由。

## When to Use

- 切换 API 供应商或模型
- 对比多个大模型表现
- 查看模型排名（日/周/月/总榜）
- 管理 API 优先级
- 添加自定义供应商

## Quick Start

```bash
python src/cli.py provider list          # 查看所有供应商
python src/cli.py provider switch deepseek  # 切换到 DeepSeek
python src/cli.py rank                    # 查看所有排行榜
python src/cli.py status                  # 完整状态面板
```

## CLI Commands

| 命令 | 说明 |
|------|------|
| `provider list` | 列出 50+ 供应商 |
| `provider switch <id> [model]` | 切换供应商/模型 |
| `provider active` | 当前配置 |
| `provider env` | 生成环境变量 |
| `provider add <id> <json>` | 添加自定义供应商 |
| `rank [daily\|weekly\|monthly\|all]` | 排行榜 |
| `rank detail <model>` | 模型详情 |
| `arena record <id> <t> <s> <q>` | 记录表现 |
| `arena veto <id> <rank\|ban>` | 用户否决 |
| `quick <provider>` | 快速切换+显示配置 |
| `status` | 完整状态面板 |

## Scoring

| 维度 | 权重 | 说明 |
|------|------|------|
| Token 效率 | 35% | 越少越好 |
| 思考速度 | 30% | 越快越好 |
| 回答质量 | 35% | 越高越好 |

## User Veto

- `arena veto <model> 1` — 强制第1名
- `arena veto <model> ban` — 封禁
- `arena veto <model> 0` — 取消否决
