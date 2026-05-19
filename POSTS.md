# Social Media Posts

## Reddit r/LocalLLaMA

**Title:** I built an Arena that makes 50+ LLMs fight each other — here are the results after 200 battles

**Body:**

Hey r/LocalLLaMA!

I've been running a tool I built called **LLM Arena .skill** — a Claude Code skill that makes 50+ LLM providers compete against each other in a tournament-style system. I ran 200 simulated battles and wanted to share the results.

**How it works:**
- Each model gets scored on 10 dimensions (token efficiency, speed, quality, consistency, error rate, cost-efficiency, latency stability, improvement trend, win rate, user satisfaction)
- Elo rating system (like chess, K=32) — beat a strong model, gain more points
- Emoji mood system that changes dynamically (Champion, Dark Horse, Overconfident, Losing Streak...)
- 19 achievements (First Blood, Penta Kill, Giant Slayer, Comeback King...)
- **User veto power** — you can override any ranking

**Top 8 after 200 battles:**

| Rank | Model | Elo | Quality |
|------|-------|-----|---------|
| 1 | Claude Opus 4 | 1490 | 9.4 |
| 2 | DeepSeek V3 | 1470 | 8.5 |
| 3 | Claude Sonnet 4 | 1442 | 8.9 |
| 4 | Kimi K2 | 1352 | 8.4 |
| 5 | Gemini 2.5 Flash | 1329 | 8.0 |
| 6 | Qwen Max | 1298 | 8.3 |
| 7 | Claude Haiku 3.5 | 1233 | 8.1 |
| 8 | GPT-4o Mini | 1183 | 7.4 |

**Surprises:**
- DeepSeek V3 punches way above its weight — great efficiency
- Gemini 2.5 Flash's speed gives it a huge advantage in the efficiency dimension
- o3's high quality is offset by its slow speed and high token usage

**Why I built this:** I was tired of manually switching between APIs and never knowing which model was actually performing best for my use cases. Now I just let them compete and the best one gets higher API priority automatically.

It's a Claude Code skill, so one command installs it:
```bash
npx github:Han-cy830/llm-arena
```

GitHub: https://github.com/Han-cy830/llm-arena

Would love to hear your thoughts — what dimensions am I missing? Any models I should add?

---

## Hacker News (Show HN)

**Title:** Show HN: LLM Arena – Make 50+ LLMs compete with Elo ratings and 10-dimension scoring

**Body:**

I built a tool that pits 50+ LLM providers against each other in a tournament system.

It started as a way to stop manually switching between APIs. Now it's a full competition system:

- **10-dimension scoring**: not just quality/speed, but token efficiency, consistency, error rate, cost-efficiency, latency stability, improvement trend
- **Elo rating**: chess-style rating system. Beat a strong model = big gain. Lose to a weak model = big loss.
- **Blind battles**: inspired by Chatbot Arena — vote without knowing which model is which
- **Tier system**: Legend / Diamond / Gold / Silver / Bronze / Iron
- **Achievements**: 19 types including "First Blood", "Penta Kill", "Giant Slayer"
- **User veto**: override any ranking manually. Your word > algorithm.

It's a Claude Code skill (`.skill`), installable with one command:
```
npx github:Han-cy830/llm-arena
```

Supports: Claude, GPT-4o, DeepSeek, Gemini, OpenRouter, Kimi, Qwen, GLM, Mistral, Llama, and 40+ more providers.

After running 200 battles, Claude Opus 4 leads with 1490 Elo, followed closely by DeepSeek V3 (1470) — its efficiency score is remarkable.

GitHub: https://github.com/Han-cy830/llm-arena
Demo: https://han-cy830.github.io/llm-arena

---

## 即刻 / 微博

做了个大模型竞技场 skill，让 50+ 个大模型内卷竞争 🏆

跑了 200 场对决的结果：
🥇 Claude Opus 4 (Elo 1490)
🥈 DeepSeek V3 (Elo 1470) — 性价比之王
🥉 Claude Sonnet 4 (Elo 1442)

最好玩的是心情系统：
😎 王者、🤡 飘了、😢 连败、🦄 黑马

10 维评分 + Elo 评级 + 盲测对决 + 段位系统
用户否决权至高无上，你说了算 👑

一条命令: npx github:Han-cy830/llm-arena

#LLM #AI #Claude #DeepSeek #Gemini
