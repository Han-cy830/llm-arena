"""
LLM Arena V2 - 进化竞争算法
10维评分 + Elo评级 + 连胜衰减 + emoji心情 + 成就系统
用户否决权至高无上
"""

import json
import math
import os
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

DATA_DIR = Path(__file__).parent.parent / "data"
SCORES_FILE = DATA_DIR / "scores_v2.json"
OVERRIDES_FILE = DATA_DIR / "overrides.json"
CONFIG_FILE = DATA_DIR / "config_v2.json"
HISTORY_FILE = DATA_DIR / "battle_history.json"


def _load_json(path, default=None):
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default if default is not None else {}


def _save_json(path, data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════
# Emoji 心情系统
# ═══════════════════════════════════════════════

MOOD_SYSTEM = {
    # 排名相关心情
    "champion":    {"emoji": "😎", "name": "王者", "condition": "rank == 1"},
    "top3":        {"emoji": "😤", "name": "志在必得", "condition": "rank <= 3"},
    "rising":      {"emoji": "🔥", "name": "势头正猛", "condition": "trend == up"},
    "stable_high": {"emoji": "😏", "name": "稳坐钓鱼台", "condition": "rank <= 5 and stable"},
    "fighting":    {"emoji": "💪", "name": "奋起直追", "condition": "improving"},
    "nervous":     {"emoji": "😰", "name": "压力山大", "condition": "rank dropping"},
    "struggling":  {"emoji": "😩", "name": "苦苦挣扎", "condition": "rank > 10"},
    "losing_streak": {"emoji": "😢", "name": "连败中", "condition": "losses >= 3"},
    "winning_streak": {"emoji": "🥳", "name": "连胜中", "condition": "wins >= 3"},
    "newbie":      {"emoji": "🐣", "name": "新来的", "condition": "matches < 3"},
    "banned":      {"emoji": "💀", "name": "已被封禁", "condition": "banned"},
    "idle":        {"emoji": "😴", "name": "摸鱼中", "condition": "no recent activity"},
    "comeback":    {"emoji": "🦅", "name": "涅槃重生", "condition": "was low, now rising"},
    "overconfident": {"emoji": "🤡", "name": "飘了", "condition": "was top, quality dropping"},
    "grinding":    {"emoji": "⚙️", "name": "疯狂内卷", "condition": "high activity + improving"},
    "slacking":    {"emoji": "🦥", "name": "摆烂了", "condition": "low activity + declining"},
    "dark_horse":  {"emoji": "🦄", "name": "黑马", "condition": "new + high score"},
    "veteran":     {"emoji": "🧓", "name": "老将", "condition": "matches > 50"},
    "rookie_king": {"emoji": "👑", "name": "新人王", "condition": "new + top 5"},
}


def get_mood(model_data: dict, rank: int, all_ranks: list) -> dict:
    """根据模型状态动态计算心情"""
    matches = model_data.get("matches", 0)
    wins = model_data.get("wins", 0)
    losses = model_data.get("losses", 0)
    streak = model_data.get("current_streak", 0)
    streak_type = model_data.get("streak_type", "")
    elo = model_data.get("elo", 1200)
    history = model_data.get("history", [])
    banned = model_data.get("banned", False)
    efficiency = model_data.get("efficiency_score", 0)
    trend = model_data.get("trend", "stable")

    if banned:
        return MOOD_SYSTEM["banned"]

    if matches < 3:
        if rank <= 5 and matches > 0:
            return MOOD_SYSTEM["dark_horse"]
        return MOOD_SYSTEM["newbie"]

    # 连胜/连败
    if streak_type == "win" and streak >= 5:
        return MOOD_SYSTEM["winning_streak"]
    if streak_type == "loss" and streak >= 5:
        return MOOD_SYSTEM["losing_streak"]

    # 趋势判断
    if trend == "up" and matches > 5:
        if rank > 10:
            return MOOD_SYSTEM["comeback"]
        return MOOD_SYSTEM["grinding"]

    if trend == "down":
        if rank <= 3:
            return MOOD_SYSTEM["overconfident"]
        return MOOD_SYSTEM["nervous"]

    # 排名相关
    if rank == 1:
        return MOOD_SYSTEM["champion"]
    if rank <= 3:
        return MOOD_SYSTEM["top3"]
    if rank <= 5:
        if trend == "stable":
            return MOOD_SYSTEM["stable_high"]
        return MOOD_SYSTEM["fighting"]
    if rank <= 10:
        return MOOD_SYSTEM["fighting"]

    # 活跃度判断
    if len(history) > 0:
        last_ts = history[-1].get("timestamp", "")
        if last_ts:
            try:
                last_time = datetime.fromisoformat(last_ts)
                hours_ago = (datetime.now() - last_time).total_seconds() / 3600
                if hours_ago > 72:
                    return MOOD_SYSTEM["slacking"]
                if hours_ago > 24:
                    return MOOD_SYSTEM["idle"]
            except:
                pass

    if matches > 50:
        return MOOD_SYSTEM["veteran"]

    return MOOD_SYSTEM["struggling"]


# ═══════════════════════════════════════════════
# 成就系统
# ═══════════════════════════════════════════════

ACHIEVEMENTS = {
    "first_blood":    {"emoji": "🩸", "name": "首战告捷", "desc": "赢得第一场对决"},
    "hat_trick":      {"emoji": "🎩", "name": "帽子戏法", "desc": "连胜3场"},
    "penta_kill":     {"emoji": "💀", "name": "五杀", "desc": "连胜5场"},
    "unstoppable":    {"emoji": "🌪️", "name": "势不可挡", "desc": "连胜10场"},
    "godlike":        {"emoji": "⚡", "name": "超神", "desc": "连胜20场"},
    "iron_man":       {"emoji": "🦾", "name": "铁人", "desc": "参与100场对决"},
    "perfectionist":  {"emoji": "💎", "name": "完美主义", "desc": "单次质量评分10分"},
    "speed_demon":    {"emoji": "⏱️", "name": "极速恶魔", "desc": "响应时间<1秒"},
    "penny_pincher":  {"emoji": "💰", "name": "省钱达人", "desc": "Token效率分>9"},
    "comeback_king":  {"emoji": "👑", "name": "逆袭之王", "desc": "从排名10+升到前3"},
    "consistency":    {"emoji": "📊", "name": "稳如老狗", "desc": "连续10场质量>8"},
    "giant_killer":   {"emoji": "🗡️", "name": "屠龙勇士", "desc": "击败排名高于自己5位以上的对手"},
    "marathon":       {"emoji": "🏃", "name": "马拉松选手", "desc": "连续7天每天都有对决"},
    "flawless":       {"emoji": "✨", "name": "零失误", "desc": "连续20场无错误"},
    "improver":       {"emoji": "📈", "name": "进步之星", "desc": "效率分提升超过2分"},
    "champion":       {"emoji": "🏆", "name": "冠军", "desc": "登上总榜第一"},
    "monthly_mvp":    {"emoji": "🌟", "name": "月度MVP", "desc": "月榜排名第一"},
    "weekly_mvp":     {"emoji": "⭐", "name": "周度之星", "desc": "周榜排名第一"},
    "user_favorite":  {"emoji": "❤️", "name": "用户最爱", "desc": "被用户强制指定为第一名"},
}


# ═══════════════════════════════════════════════
# 模型数据
# ═══════════════════════════════════════════════

@dataclass
class ModelProfile:
    model_id: str
    display_name: str
    # 基础数据
    matches: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    # Elo 评级
    elo: float = 1200.0
    peak_elo: float = 1200.0
    # 10维评分
    avg_tokens: float = 0.0
    avg_think_time: float = 0.0
    avg_quality: float = 0.0
    avg_consistency: float = 0.0
    avg_error_rate: float = 0.0
    avg_cost_efficiency: float = 0.0
    avg_latency_stability: float = 0.0
    improvement_trend: float = 0.0
    win_rate: float = 0.0
    user_satisfaction: float = 0.0
    # 效率分
    efficiency_score: float = 0.0
    # 连胜连败
    current_streak: int = 0
    streak_type: str = ""  # "win" / "loss" / ""
    best_win_streak: int = 0
    worst_loss_streak: int = 0
    # 趋势
    trend: str = "stable"  # "up" / "down" / "stable"
    trend_strength: float = 0.0
    # 成就
    achievements: list = field(default_factory=list)
    # 用户否决
    user_override_rank: int = 0
    banned: bool = False
    # 历史
    history: list = field(default_factory=list)
    # 活跃度
    last_active: str = ""
    daily_matches: dict = field(default_factory=dict)


# ═══════════════════════════════════════════════
# 评分权重（10维）
# ═══════════════════════════════════════════════

DEFAULT_WEIGHTS = {
    "token_efficiency":     0.15,  # Token 效率
    "think_speed":          0.10,  # 思考速度
    "quality":              0.20,  # 回答质量
    "consistency":          0.10,  # 一致性
    "error_rate":           0.08,  # 错误率（越低越好）
    "cost_efficiency":      0.10,  # 性价比
    "latency_stability":    0.07,  # 延迟稳定性
    "improvement_trend":    0.05,  # 进步趋势
    "win_rate":             0.10,  # 胜率
    "user_satisfaction":    0.05,  # 用户满意度
}


class ArenaV2:
    """进化版竞技场引擎"""

    def __init__(self):
        self.profiles = self._load_profiles()
        self.overrides = _load_json(OVERRIDES_FILE, {})
        self.config = _load_json(CONFIG_FILE, {"weights": DEFAULT_WEIGHTS})
        self.weights = self.config.get("weights", DEFAULT_WEIGHTS)
        self.battle_history = _load_json(HISTORY_FILE, {"battles": []})

    def _load_profiles(self) -> dict:
        raw = _load_json(SCORES_FILE, {})
        result = {}
        for mid, data in raw.items():
            # 兼容旧数据
            if "model_id" not in data:
                data["model_id"] = mid
            result[mid] = ModelProfile(**{k: v for k, v in data.items()
                                          if k in ModelProfile.__dataclass_fields__})
        return result

    def _save(self):
        raw = {mid: asdict(p) for mid, p in self.profiles.items()}
        _save_json(SCORES_FILE, raw)
        _save_json(CONFIG_FILE, {"weights": self.weights})
        _save_json(HISTORY_FILE, self.battle_history)

    # ─────────────────────────────────────────
    # 注册
    # ─────────────────────────────────────────

    def register(self, model_id: str, display_name: str = ""):
        if model_id not in self.profiles:
            self.profiles[model_id] = ModelProfile(
                model_id=model_id,
                display_name=display_name or model_id,
            )
            self._save()
        return self.profiles[model_id]

    # ─────────────────────────────────────────
    # 记录对决
    # ─────────────────────────────────────────

    def record_match(self, model_id: str, tokens: int, think_time: float,
                     quality: float, error: bool = False,
                     user_rating: float = None, round_name: str = "daily"):
        """记录单次表现（10维数据采集）"""
        if model_id not in self.profiles:
            self.register(model_id)

        p = self.profiles[model_id]
        p.matches += 1
        n = p.matches

        # ── 维度1: Token 效率 ──
        p.avg_tokens = ((n - 1) * p.avg_tokens + tokens) / n

        # ── 维度2: 思考速度 ──
        p.avg_think_time = ((n - 1) * p.avg_think_time + think_time) / n

        # ── 维度3: 回答质量 ──
        p.avg_quality = ((n - 1) * p.avg_quality + quality) / n

        # ── 维度4: 一致性（质量的稳定性，用滑动窗口方差） ──
        recent_qualities = [h.get("quality", 0) for h in p.history[-9:]] + [quality]
        if len(recent_qualities) > 1:
            avg_q = sum(recent_qualities) / len(recent_qualities)
            variance = sum((q - avg_q) ** 2 for q in recent_qualities) / len(recent_qualities)
            consistency = max(0, 10 - math.sqrt(variance))
        else:
            consistency = 5.0
        p.avg_consistency = ((n - 1) * p.avg_consistency + consistency) / n

        # ── 维度5: 错误率 ──
        if n == 1:
            p.avg_error_rate = 0.0 if not error else 10.0
        else:
            error_val = 10.0 if error else 0.0
            p.avg_error_rate = ((n - 1) * p.avg_error_rate + error_val) / n

        # ── 维度6: 性价比（质量/token * 1000） ──
        cost_eff = (quality / max(1, tokens)) * 1000
        p.avg_cost_efficiency = ((n - 1) * p.avg_cost_efficiency + cost_eff) / n

        # ── 维度7: 延迟稳定性（P95/P50 比值越接近1越好） ──
        recent_times = [h.get("think_time", 0) for h in p.history[-9:]] + [think_time]
        if len(recent_times) >= 3:
            sorted_times = sorted(recent_times)
            p50 = sorted_times[len(sorted_times) // 2]
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            stability = max(0, 10 - (p95 / max(0.01, p50) - 1) * 5)
        else:
            stability = 5.0
        p.avg_latency_stability = ((n - 1) * p.avg_latency_stability + stability) / n

        # ── 维度8: 进步趋势（最近5场 vs 之前5场的效率分趋势） ──
        if len(p.history) >= 5:
            old_scores = [h.get("match_score", 0) for h in p.history[-10:-5]]
            new_scores = [h.get("match_score", 0) for h in p.history[-5:]]
            if old_scores and new_scores:
                old_avg = sum(old_scores) / len(old_scores)
                new_avg = sum(new_scores) / len(new_scores)
                p.improvement_trend = (new_avg - old_avg) / max(0.01, old_avg) * 10
                p.improvement_trend = max(-10, min(10, p.improvement_trend))

        # ── 维度9: 胜率 ──
        if p.wins + p.losses > 0:
            p.win_rate = p.wins / (p.wins + p.losses) * 10

        # ── 维度10: 用户满意度（如有手动评分） ──
        if user_rating is not None:
            p.user_satisfaction = ((n - 1) * p.user_satisfaction + user_rating) / n

        # ── 计算综合效率分 ──
        token_score = max(0, 10 - (p.avg_tokens / 1000))
        speed_score = max(0, 10 - (p.avg_think_time / 6))
        error_score = max(0, 10 - p.avg_error_rate)

        match_score = (
            token_score              * self.weights["token_efficiency"] +
            speed_score              * self.weights["think_speed"] +
            min(10, p.avg_quality)   * self.weights["quality"] +
            p.avg_consistency        * self.weights["consistency"] +
            error_score              * self.weights["error_rate"] +
            min(10, p.avg_cost_efficiency) * self.weights["cost_efficiency"] +
            p.avg_latency_stability  * self.weights["latency_stability"] +
            max(0, p.improvement_trend + 5) * self.weights["improvement_trend"] +
            p.win_rate               * self.weights["win_rate"] +
            p.user_satisfaction      * self.weights["user_satisfaction"]
        )

        p.efficiency_score = match_score

        # ── 活跃度统计 ──
        today = datetime.now().strftime("%Y-%m-%d")
        p.daily_matches[today] = p.daily_matches.get(today, 0) + 1
        p.last_active = datetime.now().isoformat()

        # ── 记录历史 ──
        p.history.append({
            "timestamp": datetime.now().isoformat(),
            "tokens": tokens,
            "think_time": think_time,
            "quality": quality,
            "error": error,
            "consistency": round(consistency, 2),
            "cost_efficiency": round(cost_eff, 3),
            "latency_stability": round(stability, 2),
            "match_score": round(match_score, 3),
            "round": round_name,
        })

        # ── 检查成就 ──
        self._check_achievements(p)

        self._save()
        return match_score

    # ─────────────────────────────────────────
    # 对决系统（带 Elo）
    # ─────────────────────────────────────────

    def record_battle(self, models_data: list, round_name: str = "daily"):
        """
        多模型对决 + Elo 评级更新
        models_data: [{"model_id": str, "tokens": int, "think_time": float, "quality": float, "error": bool}, ...]
        """
        results = []
        for m in models_data:
            score = self.record_match(
                m["model_id"], m["tokens"], m["think_time"],
                m.get("quality", 5), m.get("error", False),
                user_rating=m.get("user_rating"),
                round_name=round_name
            )
            results.append((m["model_id"], score))

        results.sort(key=lambda x: x[1], reverse=True)
        winner_id = results[0][0]

        # 更新胜负和 Elo
        for i, (mid, _) in enumerate(results):
            p = self.profiles[mid]
            if i == 0:
                p.wins += 1
                p.streak_type = "win"
                p.current_streak = p.current_streak + 1 if p.streak_type == "win" else 1
                p.best_win_streak = max(p.best_win_streak, p.current_streak)
            else:
                p.losses += 1
                if p.streak_type == "loss":
                    p.current_streak += 1
                else:
                    p.streak_type = "loss"
                    p.current_streak = 1
                p.worst_loss_streak = max(p.worst_loss_streak, p.current_streak)

        # Elo 更新（只在2+模型对决时生效）
        if len(results) >= 2:
            self._update_elo(results)

        # 更新趋势
        self._update_trends()

        # 记录对决历史
        self.battle_history.setdefault("battles", []).append({
            "timestamp": datetime.now().isoformat(),
            "round": round_name,
            "participants": [r[0] for r in results],
            "winner": winner_id,
            "scores": {r[0]: round(r[1], 3) for r in results},
        })

        # 检查成就
        winner = self.profiles[winner_id]
        self._check_achievements(winner)
        # 检查屠龙勇士
        winner_rank = self._get_rank(winner_id)
        for mid, _ in results[1:]:
            loser_rank = self._get_rank(mid)
            if winner_rank > loser_rank + 5:
                self._grant_achievement(winner_id, "giant_killer")

        self._save()
        return winner_id, results

    def _update_elo(self, results: list, k: int = 32):
        """Elo 评级更新"""
        n = len(results)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                mid_i, score_i = results[i]
                mid_j, score_j = results[j]
                p_i = self.profiles[mid_i]
                p_j = self.profiles[mid_j]

                # 期望胜率
                expected_i = 1 / (1 + 10 ** ((p_j.elo - p_i.elo) / 400))
                # 实际结果
                actual_i = 1.0 if score_i > score_j else (0.5 if score_i == score_j else 0.0)

                # 更新（分摊到所有对手）
                delta = k * (actual_i - expected_i) / (n - 1)
                p_i.elo += delta

                # 更新峰值
                p_i.peak_elo = max(p_i.peak_elo, p_i.elo)

    def _update_trends(self):
        """更新所有模型的趋势"""
        for mid, p in self.profiles.items():
            if len(p.history) < 5:
                p.trend = "stable"
                continue

            recent5 = [h.get("match_score", 0) for h in p.history[-5:]]
            prev5 = [h.get("match_score", 0) for h in p.history[-10:-5]] if len(p.history) >= 10 else recent5

            avg_recent = sum(recent5) / len(recent5)
            avg_prev = sum(prev5) / len(prev5)
            diff = avg_recent - avg_prev

            if diff > 0.5:
                p.trend = "up"
                p.trend_strength = min(10, diff)
            elif diff < -0.5:
                p.trend = "down"
                p.trend_strength = min(10, abs(diff))
            else:
                p.trend = "stable"
                p.trend_strength = 0

    def _get_rank(self, model_id: str) -> int:
        """获取模型排名"""
        ranking = self.get_ranking("all")
        for i, r in enumerate(ranking):
            if r["model_id"] == model_id:
                return i + 1
        return len(ranking) + 1

    # ─────────────────────────────────────────
    # 成就系统
    # ─────────────────────────────────────────

    def _check_achievements(self, p: ModelProfile):
        """检查并授予成就"""
        if p.wins == 1 and "first_blood" not in p.achievements:
            self._grant_achievement(p.model_id, "first_blood")

        if p.current_streak >= 3 and p.streak_type == "win" and "hat_trick" not in p.achievements:
            self._grant_achievement(p.model_id, "hat_trick")
        if p.current_streak >= 5 and p.streak_type == "win" and "penta_kill" not in p.achievements:
            self._grant_achievement(p.model_id, "penta_kill")
        if p.current_streak >= 10 and p.streak_type == "win" and "unstoppable" not in p.achievements:
            self._grant_achievement(p.model_id, "unstoppable")
        if p.current_streak >= 20 and p.streak_type == "win" and "godlike" not in p.achievements:
            self._grant_achievement(p.model_id, "godlike")

        if p.matches >= 100 and "iron_man" not in p.achievements:
            self._grant_achievement(p.model_id, "iron_man")

        if any(h.get("quality", 0) == 10 for h in p.history) and "perfectionist" not in p.achievements:
            self._grant_achievement(p.model_id, "perfectionist")

        if any(h.get("think_time", 999) < 1 for h in p.history) and "speed_demon" not in p.achievements:
            self._grant_achievement(p.model_id, "speed_demon")

        if p.avg_tokens > 0 and max(0, 10 - (p.avg_tokens / 1000)) > 9 and "penny_pincher" not in p.achievements:
            self._grant_achievement(p.model_id, "penny_pincher")

        if p.avg_quality > 8 and len(p.history) >= 10:
            recent10 = p.history[-10:]
            if all(h.get("quality", 0) > 8 for h in recent10) and "consistency" not in p.achievements:
                self._grant_achievement(p.model_id, "consistency")

        if p.improvement_trend > 2 and "improver" not in p.achievements:
            self._grant_achievement(p.model_id, "improver")

        # 连续7天活跃
        if len(p.daily_matches) >= 7:
            dates = sorted(p.daily_matches.keys())[-7:]
            all_active = all(p.daily_matches.get(d, 0) > 0 for d in dates)
            if all_active and "marathon" not in p.achievements:
                self._grant_achievement(p.model_id, "marathon")

    def _grant_achievement(self, model_id: str, achievement_id: str):
        """授予成就"""
        if model_id in self.profiles and achievement_id not in self.profiles[model_id].achievements:
            self.profiles[model_id].achievements.append(achievement_id)

    # ─────────────────────────────────────────
    # 用户否决权（至高无上）
    # ─────────────────────────────────────────

    def user_veto(self, model_id: str, rank: int = 0, banned: bool = False,
                  user_rating: float = None):
        """
        用户否决权 - 至高无上
        rank: 0=取消, 1~N=强制排名
        banned: True=封禁
        user_rating: 用户满意度评分 0-10
        """
        if model_id not in self.profiles:
            self.register(model_id)

        p = self.profiles[model_id]

        if banned:
            p.banned = True
            p.user_override_rank = 0
        elif rank > 0:
            p.user_override_rank = rank
            p.banned = False
            if rank == 1:
                self._grant_achievement(model_id, "user_favorite")
            self._grant_achievement(model_id, "user_favorite")
        else:
            p.user_override_rank = 0
            p.banned = False

        if user_rating is not None:
            p.user_satisfaction = user_rating

        self.overrides[model_id] = {
            "rank": p.user_override_rank,
            "banned": p.banned,
            "user_satisfaction": p.user_satisfaction,
            "timestamp": datetime.now().isoformat(),
        }
        _save_json(OVERRIDES_FILE, self.overrides)
        self._save()

    # ─────────────────────────────────────────
    # 排名系统
    # ─────────────────────────────────────────

    def get_ranking(self, period: str = "all") -> list:
        ranked = []
        for mid, p in self.profiles.items():
            if p.banned:
                continue

            entry = {
                "model_id": mid,
                "display_name": p.display_name,
                "elo": round(p.elo, 0),
                "peak_elo": round(p.peak_elo, 0),
                "matches": p.matches,
                "wins": p.wins,
                "losses": p.losses,
                "win_rate": round(p.win_rate, 1),
                "efficiency_score": round(p.efficiency_score, 3),
                # 10维数据
                "avg_tokens": round(p.avg_tokens, 0),
                "avg_think_time": round(p.avg_think_time, 2),
                "avg_quality": round(p.avg_quality, 2),
                "avg_consistency": round(p.avg_consistency, 2),
                "avg_error_rate": round(p.avg_error_rate, 2),
                "avg_cost_efficiency": round(p.avg_cost_efficiency, 3),
                "avg_latency_stability": round(p.avg_latency_stability, 2),
                "improvement_trend": round(p.improvement_trend, 2),
                "user_satisfaction": round(p.user_satisfaction, 1),
                # 连胜
                "current_streak": p.current_streak,
                "streak_type": p.streak_type,
                "best_win_streak": p.best_win_streak,
                # 趋势
                "trend": p.trend,
                "trend_strength": round(p.trend_strength, 1),
                # 成就
                "achievements": p.achievements,
                "achievement_count": len(p.achievements),
                # 用户否决
                "user_override_rank": p.user_override_rank,
                # 心情（稍后计算）
                "mood": {},
            }
            ranked.append(entry)

        # 计算心情
        for i, entry in enumerate(ranked):
            entry["mood"] = get_mood(entry, i + 1, ranked)

        # 排序：用户强制排名优先，然后按 Elo
        def sort_key(x):
            uor = x["user_override_rank"]
            if uor > 0:
                return (0, uor, -x["elo"])
            return (1, 0, -x["elo"])

        ranked.sort(key=sort_key)

        # 重新计算心情（排序后）
        for i, entry in enumerate(ranked):
            entry["rank"] = i + 1
            entry["mood"] = get_mood(entry, i + 1, ranked)

        return ranked

    def get_top_model(self) -> Optional[str]:
        ranking = self.get_ranking("all")
        return ranking[0]["model_id"] if ranking else None

    def get_priority_list(self) -> list:
        return [r["model_id"] for r in self.get_ranking("all")]

    # ─────────────────────────────────────────
    # 权重调整
    # ─────────────────────────────────────────

    def set_weights(self, **kwargs):
        for k, v in kwargs.items():
            if k in self.weights:
                self.weights[k] = v
        self.config["weights"] = self.weights
        _save_json(CONFIG_FILE, self.config)
