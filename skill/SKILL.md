---
name: llm-arena
description: Use when evaluating multiple LLMs, comparing model performance, switching API providers, managing model rankings, or routing API calls to the best model. Supports 50+ providers with 10-dimension scoring, Elo ratings, emoji moods, achievements, blind battles, and user veto power. Also available as MCP server for any AI tool.
---

# LLM Arena V2 - 大模型竞技场

## Overview

50+ 供应商大模型内卷竞技场。10维评分 + Elo评级 + emoji心情 + 成就系统 + 盲测对决 + 段位系统。用户否决权至高无上。

支持 CLI、MCP Server、VS Code Extension 三种使用方式。

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

## MCP Server

任何 AI 工具都能通过 MCP 协议调用 LLM Arena。

```bash
# 启动 MCP Server (stdio)
python src/mcp_server.py

# 启动 MCP Server (HTTP)
python src/mcp_server.py --http --port 8000
```

配置 `.mcp.json`:
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

### MCP Tools (12个)
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

### MCP Resources (5个)
| 资源 | 说明 |
|------|------|
| `arena://ranking/{period}` | 排名数据 |
| `arena://providers` | 供应商列表 |
| `arena://config` | 当前配置 |
| `arena://mood` | 心情总览 |
| `arena://achievements` | 成就数据 |

## CLI Commands

### 供应商管理
| 命令 | 说明 |
|------|------|
| `provider list [--json]` | 列出 50+ 供应商 |
| `provider switch <id> [model]` | 切换供应商/模型 |
| `provider active [--json]` | 当前配置 |
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
| `rank json [period]` | JSON 格式排名 |
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
