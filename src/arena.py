"""
LLM Arena - 大模型竞技场
让多个大模型内卷竞争，优胜劣汰！
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

DATA_DIR = Path(__file__).parent.parent / "data"
SCORES_FILE = DATA_DIR / "scores.json"
OVERRIDES_FILE = DATA_DIR / "overrides.json"
CONFIG_FILE = DATA_DIR / "config.json"


@dataclass
class ModelScore:
    model_id: str
    display_name: str
    total_score: float = 0.0
    matches: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    avg_tokens: float = 0.0
    avg_think_time: float = 0.0
    avg_quality: float = 0.0
    # 权重分 = 综合效率分，越高 API 优先级越高
    efficiency_score: float = 0.0
    # 用户否决排名 (-1 = 被ban, 0 = 正常, 1~N = 强制指定排名)
    user_override_rank: int = 0
    history: list = field(default_factory=list)


@dataclass
class MatchResult:
    timestamp: str
    round_name: str  # "daily" / "weekly" / "monthly"
    models: list
    winner: str
    scores: dict  # model_id -> {tokens, think_time, quality, total}


def _load_json(path: Path, default=None):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default if default is not None else {}


def _save_json(path: Path, data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class LLMArena:
    """大模型竞技场核心引擎"""

    # 评分权重配置
    DEFAULT_WEIGHTS = {
        "token_efficiency": 0.35,   # token 消耗越少越好
        "think_speed": 0.30,        # 思考时间越短越好
        "quality": 0.35,            # 回答质量越高越好
    }

    def __init__(self):
        self.scores = self._load_scores()
        self.overrides = _load_json(OVERRIDES_FILE, {})
        self.config = _load_json(CONFIG_FILE, {"weights": self.DEFAULT_WEIGHTS})
        self.weights = self.config.get("weights", self.DEFAULT_WEIGHTS)

    def _load_scores(self) -> dict:
        raw = _load_json(SCORES_FILE, {})
        result = {}
        for mid, data in raw.items():
            score = ModelScore(**data)
            result[mid] = score
        return result

    def _save_scores(self):
        raw = {mid: asdict(s) for mid, s in self.scores.items()}
        _save_json(SCORES_FILE, raw)

    def register_model(self, model_id: str, display_name: str = ""):
        """注册一个新模型到竞技场"""
        if model_id not in self.scores:
            self.scores[model_id] = ModelScore(
                model_id=model_id,
                display_name=display_name or model_id,
            )
            self._save_scores()
            print(f"✅ 模型 [{display_name or model_id}] 已注册到竞技场")
        else:
            print(f"ℹ️  模型 [{model_id}] 已存在")

    def record_match(self, model_id: str, tokens: int, think_time: float,
                     quality: float, round_name: str = "daily"):
        """
        记录一次模型表现
        tokens: 消耗的 token 数量
        think_time: 思考时间（秒）
        quality: 质量评分 0-10（可由用户或自动评估）
        """
        if model_id not in self.scores:
            self.register_model(model_id)

        s = self.scores[model_id]
        s.matches += 1

        # 累积平均
        n = s.matches
        s.avg_tokens = ((n - 1) * s.avg_tokens + tokens) / n
        s.avg_think_time = ((n - 1) * s.avg_think_time + think_time) / n
        s.avg_quality = ((n - 1) * s.avg_quality + quality) / n

        # 计算单次效率分
        # token 效率：越少越好，归一化到 0-10（假设 10000 token 为基准）
        token_score = max(0, 10 - (tokens / 1000))
        # 速度分：越快越好，归一化到 0-10（假设 60 秒为基准）
        speed_score = max(0, 10 - (think_time / 6))
        # 质量分直接用
        quality_score = min(10, max(0, quality))

        match_score = (
            token_score * self.weights["token_efficiency"] +
            speed_score * self.weights["think_speed"] +
            quality_score * self.weights["quality"]
        )

        s.total_score += match_score
        s.efficiency_score = s.total_score / n

        # 记录历史
        s.history.append({
            "timestamp": datetime.now().isoformat(),
            "tokens": tokens,
            "think_time": think_time,
            "quality": quality,
            "match_score": round(match_score, 3),
            "round": round_name,
        })

        self._save_scores()
        return match_score

    def record_battle(self, models_data: list, round_name: str = "daily"):
        """
        记录一场多模型对决
        models_data: [{"model_id": str, "tokens": int, "think_time": float, "quality": float}, ...]
        """
        results = []
        for m in models_data:
            score = self.record_match(
                m["model_id"], m["tokens"], m["think_time"], m["quality"], round_name
            )
            results.append((m["model_id"], score))

        # 选出赢家
        results.sort(key=lambda x: x[1], reverse=True)
        winner = results[0][0]
        self.scores[winner].wins += 1

        # 记录胜负
        for mid, _ in results[1:]:
            self.scores[mid].losses += 1

        self._save_scores()
        return winner, results

    def get_ranking(self, period: str = "all") -> list:
        """
        获取排名
        period: "daily" / "weekly" / "monthly" / "all"
        """
        ranked = []

        for mid, s in self.scores.items():
            # 检查用户否决
            override = self.overrides.get(mid, {})
            if override.get("banned"):
                continue

            # 按时间段过滤历史
            if period == "all":
                filtered = s.history
            else:
                filtered = self._filter_by_period(s.history, period)

            if not filtered and period != "all":
                continue

            entry = {
                "model_id": mid,
                "display_name": s.display_name,
                "matches": len(filtered) if period != "all" else s.matches,
                "wins": s.wins,
                "losses": s.losses,
                "avg_tokens": round(s.avg_tokens, 1),
                "avg_think_time": round(s.avg_think_time, 2),
                "avg_quality": round(s.avg_quality, 2),
                "efficiency_score": round(s.efficiency_score, 3),
                "user_override_rank": override.get("rank", 0),
            }
            ranked.append(entry)

        # 排序：用户强制排名优先，然后按效率分
        def sort_key(x):
            uor = x["user_override_rank"]
            if uor > 0:
                return (0, uor)  # 强制排名排最前
            return (1, -x["efficiency_score"])  # 按效率分降序

        ranked.sort(key=sort_key)
        return ranked

    def _filter_by_period(self, history: list, period: str) -> list:
        now = datetime.now()
        if period == "daily":
            cutoff = now - timedelta(days=1)
        elif period == "weekly":
            cutoff = now - timedelta(weeks=1)
        elif period == "monthly":
            cutoff = now - timedelta(days=30)
        else:
            return history

        cutoff_str = cutoff.isoformat()
        return [h for h in history if h.get("timestamp", "") >= cutoff_str]

    def user_veto(self, model_id: str, rank: int = 0, banned: bool = False):
        """
        用户否决权：直接调整模型排名或封禁
        rank: 0=取消强制排名, 1~N=强制指定排名
        banned: True=封禁该模型
        """
        self.overrides[model_id] = {
            "rank": rank,
            "banned": banned,
            "timestamp": datetime.now().isoformat(),
        }
        _save_json(OVERRIDES_FILE, self.overrides)
        if banned:
            print(f"🚫 模型 [{model_id}] 已被封禁")
        elif rank > 0:
            print(f"👑 模型 [{model_id}] 被强制指定为第 {rank} 名")
        else:
            print(f"♻️  模型 [{model_id}] 的否决已取消")

    def get_top_model(self) -> Optional[str]:
        """获取当前排名第一的模型 ID（用于 API 路由优先级）"""
        ranking = self.get_ranking("all")
        if ranking:
            return ranking[0]["model_id"]
        return None

    def get_priority_list(self) -> list:
        """获取 API 调用优先级列表（按排名排序的模型 ID）"""
        ranking = self.get_ranking("all")
        return [r["model_id"] for r in ranking]

    def set_weights(self, token_eff: float = None, speed: float = None,
                    quality: float = None):
        """调整评分权重"""
        if token_eff is not None:
            self.weights["token_efficiency"] = token_eff
        if speed is not None:
            self.weights["think_speed"] = speed
        if quality is not None:
            self.weights["quality"] = quality
        self.config["weights"] = self.weights
        _save_json(CONFIG_FILE, self.config)
        print(f"⚖️  权重已更新: {self.weights}")

    def display_ranking(self, period: str = "all"):
        """漂亮的排名展示"""
        ranking = self.get_ranking(period)
        period_names = {
            "daily": "日榜", "weekly": "周榜",
            "monthly": "月榜", "all": "总榜"
        }

        print(f"\n{'='*60}")
        print(f"🏆 LLM Arena {period_names.get(period, period)} 排名")
        print(f"{'='*60}")

        if not ranking:
            print("  暂无数据")
            return

        medals = {0: "🥇", 1: "🥈", 2: "🥉"}
        for i, r in enumerate(ranking):
            medal = medals.get(i, f"#{i+1}")
            override_mark = " 👑" if r["user_override_rank"] > 0 else ""
            print(f"\n  {medal} {r['display_name']}{override_mark}")
            print(f"     效率分: {r['efficiency_score']:.3f}")
            print(f"     平均Token: {r['avg_tokens']:.0f} | "
                  f"平均耗时: {r['avg_think_time']:.1f}s | "
                  f"平均质量: {r['avg_quality']:.1f}/10")
            print(f"     战绩: {r['wins']}胜 {r['losses']}负 "
                  f"({r['matches']}场)")

        print(f"\n{'='*60}\n")


# CLI 入口
def main():
    import sys

    arena = LLMArena()

    if len(sys.argv) < 2:
        print("用法: python arena.py <command> [args]")
        print("命令:")
        print("  register <model_id> [display_name]  注册模型")
        print("  record <model_id> <tokens> <time> <quality>  记录表现")
        print("  battle <json_file>  多模型对决")
        print("  ranking [daily|weekly|monthly|all]  查看排名")
        print("  veto <model_id> <rank|ban>  用户否决")
        print("  priority  查看 API 优先级列表")
        print("  weights <token> <speed> <quality>  调整权重")
        return

    cmd = sys.argv[1]

    if cmd == "register":
        mid = sys.argv[2]
        name = sys.argv[3] if len(sys.argv) > 3 else ""
        arena.register_model(mid, name)

    elif cmd == "record":
        mid = sys.argv[2]
        tokens = int(sys.argv[3])
        ttime = float(sys.argv[4])
        quality = float(sys.argv[5])
        score = arena.record_match(mid, tokens, ttime, quality)
        print(f"📊 记录完成，本次得分: {score:.3f}")

    elif cmd == "battle":
        with open(sys.argv[2], "r", encoding="utf-8") as f:
            data = json.load(f)
        winner, results = arena.record_battle(data)
        print(f"\n🏆 胜者: {winner}")
        for mid, sc in results:
            print(f"  {mid}: {sc:.3f}")

    elif cmd == "ranking":
        period = sys.argv[2] if len(sys.argv) > 2 else "all"
        arena.display_ranking(period)

    elif cmd == "veto":
        mid = sys.argv[2]
        val = sys.argv[3]
        if val == "ban":
            arena.user_veto(mid, banned=True)
        else:
            arena.user_veto(mid, rank=int(val))

    elif cmd == "priority":
        plist = arena.get_priority_list()
        print("📡 API 调用优先级:")
        for i, mid in enumerate(plist):
            print(f"  {i+1}. {mid}")

    elif cmd == "weights":
        arena.set_weights(
            token_eff=float(sys.argv[2]),
            speed=float(sys.argv[3]),
            quality=float(sys.argv[4]),
        )

    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()
