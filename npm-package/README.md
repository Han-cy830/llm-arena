# LLM Arena - Claude Code Skill

一键安装大模型竞技场 Skill 到 Claude Code。

## 安装

```bash
npx llm-arena
```

## 卸载

```bash
npx llm-arena uninstall
```

## 功能

- 50+ API 供应商支持
- 日榜 / 周榜 / 月榜 / 总榜排名
- 用户否决权（强制排名/封禁）
- API 智能路由优先级
- 自定义供应商支持

## 安装后使用

在 Claude Code 中:
- 输入 `/llm-arena` 触发 skill
- 或直接说"帮我切换到 DeepSeek"

CLI 命令:
```bash
python src/cli.py provider list    # 查看供应商
python src/cli.py rank             # 查看排名
python src/cli.py status           # 状态面板
```

## 文档

https://github.com/Han-cy830/llm-arena
