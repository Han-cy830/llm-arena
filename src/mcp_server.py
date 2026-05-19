"""
LLM Arena MCP Server
任何 AI 工具（Claude Code、Cursor、Claude Desktop）都能通过 MCP 协议调用
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp.server.fastmcp import FastMCP
from arena_v2 import ArenaV2
from switcher import APISwitcher
from battle_arena import BattleArena

mcp = FastMCP(
    "llm-arena",
    instructions="LLM Arena - 50+ LLM provider competition system with 10-dimension scoring, Elo ratings, emoji moods, and achievements.",
)

arena = ArenaV2()
switcher = APISwitcher()
battle = BattleArena(arena)


# ═══════════════════════════════════════════════
# Tools
# ═══════════════════════════════════════════════

@mcp.tool()
def register_model(model_id: str, display_name: str = "") -> str:
    """Register a new model in the arena.

    Args:
        model_id: Unique model identifier (e.g., 'gpt-4o', 'claude-sonnet')
        display_name: Human-readable name (e.g., 'GPT-4o', 'Claude Sonnet 4')
    """
    try:
        profile = arena.register(model_id, display_name)
        return json.dumps({
            "success": True,
            "model_id": profile.model_id,
            "display_name": profile.display_name,
            "elo": profile.elo,
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def record_match(
    model_id: str,
    tokens: int,
    think_time: float,
    quality: float,
    error: bool = False,
    user_rating: float = -1,
) -> str:
    """Record a single model performance match.

    Args:
        model_id: The model identifier
        tokens: Number of tokens used
        think_time: Response time in seconds
        quality: Quality score (0-10)
        error: Whether an error occurred
        user_rating: User satisfaction rating (0-10), -1 if not set
    """
    try:
        score = arena.record_match(
            model_id, tokens, think_time, quality,
            error=error,
            user_rating=user_rating if user_rating >= 0 else None,
        )
        p = arena.profiles.get(model_id)
        return json.dumps({
            "success": True,
            "efficiency_score": round(score, 3),
            "elo": round(p.elo, 0) if p else None,
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def record_battle(models_data: str, round_name: str = "daily") -> str:
    """Record a multi-model battle. Models compete and Elo ratings update.

    Args:
        models_data: JSON string, list of dicts with keys: model_id, tokens, think_time, quality, error (optional)
        round_name: Round type - 'daily', 'weekly', 'monthly'
    """
    try:
        data = json.loads(models_data)
        winner, results = arena.record_battle(data, round_name)
        return json.dumps({
            "success": True,
            "winner": winner,
            "results": {mid: round(sc, 3) for mid, sc in results},
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_ranking(period: str = "all") -> str:
    """Get model rankings for a given period.

    Args:
        period: 'daily', 'weekly', 'monthly', or 'all'
    """
    try:
        ranking = arena.get_ranking(period)
        return json.dumps(ranking, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_top_model() -> str:
    """Get the current top-ranked model."""
    try:
        top = arena.get_top_model()
        if top:
            p = arena.profiles[top]
            return json.dumps({
                "model_id": top,
                "display_name": p.display_name,
                "elo": round(p.elo, 0),
                "efficiency_score": round(p.efficiency_score, 3),
            })
        return json.dumps({"model_id": None})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def user_veto(
    model_id: str,
    rank: int = 0,
    banned: bool = False,
    user_rating: float = -1,
) -> str:
    """User veto power - override rankings, ban models, or set satisfaction rating. Supreme authority.

    Args:
        model_id: The model to apply veto to
        rank: Force this model to this rank (0 = no change)
        banned: Ban this model from competition
        user_rating: Set user satisfaction rating (0-10), -1 if not set
    """
    try:
        arena.user_veto(
            model_id,
            rank=rank if rank > 0 else 0,
            banned=banned,
            user_rating=user_rating if user_rating >= 0 else None,
        )
        action = []
        if rank > 0:
            action.append(f"forced to rank {rank}")
        if banned:
            action.append("banned")
        if user_rating >= 0:
            action.append(f"rated {user_rating}/10")
        return json.dumps({
            "success": True,
            "model_id": model_id,
            "action": ", ".join(action) if action else "veto cleared",
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def set_weights(
    token_efficiency: float = -1,
    think_speed: float = -1,
    quality: float = -1,
    consistency: float = -1,
    error_rate: float = -1,
    cost_efficiency: float = -1,
    latency_stability: float = -1,
    improvement_trend: float = -1,
    win_rate: float = -1,
    user_satisfaction: float = -1,
) -> str:
    """Adjust scoring weights for the 10-dimension system. Use -1 to keep current value.

    Args:
        token_efficiency: Weight for token efficiency (default 0.15)
        think_speed: Weight for thinking speed (default 0.10)
        quality: Weight for response quality (default 0.20)
        consistency: Weight for consistency (default 0.10)
        error_rate: Weight for error rate (default 0.08)
        cost_efficiency: Weight for cost efficiency (default 0.10)
        latency_stability: Weight for latency stability (default 0.07)
        improvement_trend: Weight for improvement trend (default 0.05)
        win_rate: Weight for win rate (default 0.10)
        user_satisfaction: Weight for user satisfaction (default 0.05)
    """
    try:
        kwargs = {}
        for name, val in [
            ("token_efficiency", token_efficiency),
            ("think_speed", think_speed),
            ("quality", quality),
            ("consistency", consistency),
            ("error_rate", error_rate),
            ("cost_efficiency", cost_efficiency),
            ("latency_stability", latency_stability),
            ("improvement_trend", improvement_trend),
            ("win_rate", win_rate),
            ("user_satisfaction", user_satisfaction),
        ]:
            if val >= 0:
                kwargs[name] = val
        if kwargs:
            arena.set_weights(**kwargs)
        return json.dumps({"success": True, "updated": kwargs})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def list_providers() -> str:
    """List all 50+ API providers with their status."""
    try:
        providers = switcher.list_providers()
        return json.dumps(providers, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def switch_provider(provider_id: str, model_id: str = "") -> str:
    """Switch to a different API provider.

    Args:
        provider_id: Provider identifier (e.g., 'deepseek', 'openai')
        model_id: Specific model (optional, uses provider default if empty)
    """
    try:
        result = switcher.switch(provider_id, model_id if model_id else None)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def get_active_config() -> str:
    """Get the current active provider configuration."""
    try:
        config = switcher.get_active_config()
        return json.dumps(config, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def vote_battle(model_a: str, model_b: str, winner: str) -> str:
    """Vote on a blind battle result.

    Args:
        model_a: First model ID
        model_b: Second model ID
        winner: 'a' if model_a won, 'b' if model_b won, 'draw' for tie
    """
    try:
        result = battle.vote(model_a, model_b, winner)
        return json.dumps({"success": True, "result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def compare_models(model_a: str, model_b: str) -> str:
    """Compare two models across all 10 dimensions. Returns structured data.

    Args:
        model_a: First model ID
        model_b: Second model ID
    """
    try:
        pa = arena.profiles.get(model_a)
        pb = arena.profiles.get(model_b)
        if not pa or not pb:
            return json.dumps({"error": "Model not found"})

        def get_values(p):
            return {
                "token_efficiency": round(max(0, 10 - (p.avg_tokens / 1000)), 2),
                "think_speed": round(max(0, 10 - (p.avg_think_time / 6)), 2),
                "quality": round(min(10, p.avg_quality), 2),
                "consistency": round(p.avg_consistency, 2),
                "error_rate": round(max(0, 10 - p.avg_error_rate), 2),
                "cost_efficiency": round(min(10, p.avg_cost_efficiency), 2),
                "latency_stability": round(p.avg_latency_stability, 2),
                "improvement_trend": round(max(0, p.improvement_trend + 5), 2),
                "win_rate": round(p.win_rate, 2),
                "user_satisfaction": round(p.user_satisfaction, 2),
            }

        return json.dumps({
            model_a: {"display_name": pa.display_name, "elo": round(pa.elo), "dimensions": get_values(pa)},
            model_b: {"display_name": pb.display_name, "elo": round(pb.elo), "dimensions": get_values(pb)},
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


# ═══════════════════════════════════════════════
# Resources
# ═══════════════════════════════════════════════

@mcp.resource("arena://ranking/{period}")
def resource_ranking(period: str) -> str:
    """Get model rankings. period: daily, weekly, monthly, all."""
    try:
        ranking = arena.get_ranking(period)
        return json.dumps(ranking, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.resource("arena://providers")
def resource_providers() -> str:
    """List all API providers."""
    try:
        return json.dumps(switcher.list_providers(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.resource("arena://config")
def resource_config() -> str:
    """Current active provider configuration."""
    try:
        return json.dumps(switcher.get_active_config(), ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.resource("arena://mood")
def resource_mood() -> str:
    """All models with their current emoji mood."""
    try:
        ranking = arena.get_ranking("all")
        moods = [
            {
                "model_id": r["model_id"],
                "display_name": r["display_name"],
                "mood": r.get("mood", {}),
                "elo": r["elo"],
                "streak_type": r.get("streak_type", ""),
                "current_streak": r.get("current_streak", 0),
            }
            for r in ranking
        ]
        return json.dumps(moods, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.resource("arena://achievements")
def resource_achievements() -> str:
    """All achievements with their owners."""
    try:
        from arena_v2 import ACHIEVEMENTS
        result = []
        for ach_id, ach_info in ACHIEVEMENTS.items():
            owners = [
                {"model_id": mid, "display_name": p.display_name}
                for mid, p in arena.profiles.items()
                if ach_id in p.achievements
            ]
            result.append({
                "id": ach_id,
                "emoji": ach_info["emoji"],
                "name": ach_info["name"],
                "description": ach_info["description"],
                "owners": owners,
            })
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ═══════════════════════════════════════════════
# Prompts
# ═══════════════════════════════════════════════

@mcp.prompt()
def battle_setup(model_a: str, model_b: str) -> str:
    """Set up a blind battle between two models."""
    return f"""You are running a blind LLM battle between two models.

Setup:
1. Ask the user the same question using both models
2. Present the responses as "Response A" and "Response B" (hide model identities)
3. Ask the user to vote: which response is better?
4. After voting, use the vote_battle tool to record the result

Models to battle: {model_a} vs {model_b}
Use the vote_battle tool with winner='a', 'b', or 'draw' after the user decides."""


@mcp.prompt()
def analyze_model(model_id: str) -> str:
    """Analyze a model's performance profile."""
    try:
        p = arena.profiles.get(model_id)
        if not p:
            return f"Model '{model_id}' not found. Use register_model to add it first."
        return f"""Analyze the performance of {p.display_name} ({model_id}):

Stats:
- Elo: {p.elo:.0f} (peak: {p.peak_elo:.0f})
- Matches: {p.matches} (W:{p.wins} L:{p.losses} D:{p.draws})
- Win Rate: {p.win_rate:.1%}
- Avg Quality: {p.avg_quality:.1f}/10
- Avg Tokens: {p.avg_tokens:.0f}
- Avg Speed: {p.avg_think_time:.2f}s
- Streak: {p.current_streak} ({p.streak_type})
- Trend: {p.trend}
- Achievements: {len(p.achievements)}

Please analyze strengths, weaknesses, and suggest improvements."""
    except Exception as e:
        return f"Error: {e}"


@mcp.prompt()
def compare_prompt(model_a: str, model_b: str) -> str:
    """Generate a comparison prompt for two models."""
    return f"""Compare these two LLM models: {model_a} vs {model_b}

Steps:
1. Use compare_models tool to get their 10-dimension scores
2. Analyze which model excels in which dimensions
3. Give a recommendation based on use case (coding, writing, analysis, etc.)
4. Note any surprising findings

Focus on practical differences that matter for real usage."""


# ═══════════════════════════════════════════════
# Entrypoint
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="LLM Arena MCP Server")
    parser.add_argument("--http", action="store_true", help="Use streamable-http transport")
    parser.add_argument("--port", type=int, default=8000, help="Port for HTTP transport")
    args = parser.parse_args()

    if args.http:
        mcp.run(transport="streamable-http", port=args.port)
    else:
        mcp.run(transport="stdio")
