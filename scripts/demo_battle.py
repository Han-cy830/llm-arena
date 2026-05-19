"""
生成演示对决数据 - 模拟真实场景下多模型对决
用于 Reddit/HN 帖子素材
"""

import sys
import json
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from arena_v2 import ArenaV2

# 真实模型配置（基于公开 benchmark 的大致水平）
MODELS = {
    "claude-opus-4":     {"name": "Claude Opus 4",     "tokens": (800, 1500), "time": (2.0, 5.0), "quality": (9.0, 9.8)},
    "claude-sonnet-4":   {"name": "Claude Sonnet 4",   "tokens": (900, 1600), "time": (1.5, 3.5), "quality": (8.5, 9.3)},
    "claude-haiku-3.5":  {"name": "Claude Haiku 3.5",  "tokens": (600, 1200), "time": (0.5, 1.5), "quality": (7.5, 8.5)},
    "gpt-4o":            {"name": "GPT-4o",             "tokens": (1000, 2000), "time": (2.0, 4.0), "quality": (8.0, 9.0)},
    "gpt-4o-mini":       {"name": "GPT-4o Mini",        "tokens": (500, 1000), "time": (0.5, 1.5), "quality": (7.0, 8.0)},
    "o3":                {"name": "o3",                  "tokens": (1500, 3000), "time": (5.0, 15.0), "quality": (9.0, 9.7)},
    "o4-mini":           {"name": "o4-mini",             "tokens": (1000, 2000), "time": (3.0, 8.0), "quality": (8.5, 9.2)},
    "deepseek-v3":       {"name": "DeepSeek V3",        "tokens": (700, 1400), "time": (1.0, 2.5), "quality": (8.0, 9.0)},
    "deepseek-r1":       {"name": "DeepSeek R1",        "tokens": (1200, 2500), "time": (3.0, 8.0), "quality": (8.5, 9.3)},
    "gemini-2.5-pro":    {"name": "Gemini 2.5 Pro",     "tokens": (900, 1800), "time": (1.5, 4.0), "quality": (8.5, 9.2)},
    "gemini-2.5-flash":  {"name": "Gemini 2.5 Flash",   "tokens": (500, 1000), "time": (0.3, 1.0), "quality": (7.5, 8.5)},
    "qwen-max":          {"name": "Qwen Max",           "tokens": (800, 1500), "time": (1.5, 3.0), "quality": (8.0, 8.8)},
    "glm-4-plus":        {"name": "GLM-4 Plus",         "tokens": (900, 1600), "time": (1.5, 3.5), "quality": (7.5, 8.5)},
    "kimi-k2":           {"name": "Kimi K2",            "tokens": (800, 1500), "time": (1.0, 2.5), "quality": (8.0, 8.8)},
    "mistral-large":     {"name": "Mistral Large",      "tokens": (900, 1700), "time": (1.5, 3.0), "quality": (8.0, 8.7)},
    "llama-4-maverick":  {"name": "Llama 4 Maverick",   "tokens": (1000, 2000), "time": (2.0, 4.0), "quality": (8.0, 8.8)},
}


def simulate_battle(arena, model_ids, num_battles=200):
    """模拟多轮对决"""
    for i in range(num_battles):
        # 随机选 2-3 个模型对决
        k = random.choice([2, 2, 2, 3])
        fighters = random.sample(model_ids, min(k, len(model_ids)))

        battle_data = []
        for mid in fighters:
            cfg = MODELS[mid]
            tokens = random.randint(*cfg["tokens"])
            time_s = round(random.uniform(*cfg["time"]), 2)
            quality = round(random.uniform(*cfg["quality"]), 1)
            error = random.random() < 0.02  # 2% 错误率
            battle_data.append({
                "model_id": mid,
                "tokens": tokens,
                "think_time": time_s,
                "quality": quality,
                "error": error,
            })

        arena.record_battle(battle_data)

        if (i + 1) % 50 == 0:
            print(f"  已完成 {i + 1} 场对决...")


def main():
    arena = ArenaV2()
    model_ids = list(MODELS.keys())

    # 注册所有模型
    print("注册模型...")
    for mid, cfg in MODELS.items():
        arena.register(mid, cfg["name"])

    # 模拟 200 场对决
    print("开始模拟对决...")
    simulate_battle(arena, model_ids, num_battles=200)

    # 生成排名报告
    print("\n对决完成！生成排名报告...\n")
    ranking = arena.get_ranking("all")

    print("=" * 70)
    print(f"  {'Rank':<5} {'Model':<22} {'Elo':>6} {'Score':>7} {'W-L':>7} {'Q':>5}")
    print("=" * 70)
    for i, r in enumerate(ranking[:16]):
        print(f"  {i+1:<5} {r['display_name']:<22} {r['elo']:>6.0f} {r['efficiency_score']:>7.3f} {r['wins']}-{r['losses']:>4} {r['avg_quality']:>5.1f}")
    print("=" * 70)

    # 导出为 markdown
    md = f"# LLM Arena - 200 Battle Results\n\n"
    md += f"| Rank | Model | Elo | Score | W-L | Quality |\n"
    md += f"|------|-------|-----|-------|-----|----------|\n"
    for i, r in enumerate(ranking[:16]):
        md += f"| {i+1} | {r['display_name']} | {r['elo']:.0f} | {r['efficiency_score']:.3f} | {r['wins']}-{r['losses']} | {r['avg_quality']:.1f} |\n"

    out = Path(__file__).parent.parent / "data" / "demo_results.md"
    out.write_text(md, encoding="utf-8")
    print(f"\n报告已保存: {out}")


if __name__ == "__main__":
    main()
