"""
LLM Arena - 对战竞技场
借鉴 lmarena Chatbot Arena，增强竞争表现性
盲测投票 / 雷达图 / 对战动画 / 模型人格 / 排行榜可视化
"""

import json
import math
import random
from datetime import datetime
from pathlib import Path
from arena_v2 import ArenaV2, ACHIEVEMENTS

DATA_DIR = Path(__file__).parent.parent / "data"


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_BLUE = "\033[44m"


# ═══════════════════════════════════════════════
# 模型人格系统（借鉴 Chatbot Arena 的趣味性）
# ═══════════════════════════════════════════════

MODEL_PERSONALITY = {
    "trash_talk": {
        "winning": [
            "就这？我还以为多强呢 😏",
            "承让承让，下次还赢 💅",
            "我不是针对谁，我是说在座的各位都是垃圾 🗑️",
            "赢麻了，已经没有挑战性了 😴",
            "这就是你们吹的最强模型？",
        ],
        "losing": [
            "这次是我发挥失常，下次一定！😤",
            "你别得意，我只是热身而已 💢",
            "等着，我记住你了...",
            "这局不算！我要求重赛！",
            "哼，不过是暂时的落后罢了",
        ],
        "new_champion": [
            "新王登基！旧秩序已死！👑",
            "从今天起，这个位置是我的 🔥",
            "终于等到这一天了！",
        ],
        "dethroned": [
            "可恶...我的王座...😢",
            "不可能！我怎么会输！",
            "这一定是数据出了问题！",
        ],
    },
    "pre_battle": [
        "放马过来！💪",
        "今天就让你见识什么叫实力",
        "我已经准备好了，开始吧",
        "对手？我只看到待宰的羔羊 🐑",
        "来吧，让我证明谁才是最强的",
    ],
    "post_battle": {
        "winner": [
            "谢谢参与，下次加油 👋",
            "GG",
            "这就是差距",
        ],
        "loser": [
            "下次一定...",
            "回去修炼了 🧘",
            "我会回来的！",
        ],
    },
}

# ═══════════════════════════════════════════════
# 雷达图生成器（终端 ASCII）
# ═══════════════════════════════════════════════

def render_radar(values: list, labels: list, size: int = 10) -> str:
    """生成 ASCII 雷达图"""
    n = len(values)
    if n < 3:
        return "  (数据不足，无法生成雷达图)"

    cx, cy = size, size
    radius = size - 2
    lines = []

    # 创建画布
    canvas = [[' ' for _ in range(size * 2 + 1)] for _ in range(size * 2 + 1)]

    # 绘制同心圆
    for r in [radius // 3, radius * 2 // 3, radius]:
        for angle_deg in range(360):
            angle = math.radians(angle_deg)
            x = int(cx + r * math.cos(angle))
            y = int(cy + r * math.sin(angle))
            if 0 <= x < size * 2 + 1 and 0 <= y < size * 2 + 1:
                canvas[y][x] = '·'

    # 绘制轴线和标签
    for i in range(n):
        angle = math.radians(90 + i * 360 / n)
        # 轴线
        for r in range(radius + 1):
            x = int(cx + r * math.cos(angle))
            y = int(cy + r * math.sin(angle))
            if 0 <= x < size * 2 + 1 and 0 <= y < size * 2 + 1:
                canvas[y][x] = '·'

    # 绘制数据多边形
    points = []
    for i in range(n):
        angle = math.radians(90 + i * 360 / n)
        r = (values[i] / 10) * radius
        x = int(cx + r * math.cos(angle))
        y = int(cy + r * math.sin(angle))
        points.append((x, y))

    # 填充多边形（简化：画点）
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        # 画线
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        for s in range(steps + 1):
            t = s / steps
            x = int(x1 + (x2 - x1) * t)
            y = int(y1 + (y2 - y1) * t)
            if 0 <= x < size * 2 + 1 and 0 <= y < size * 2 + 1:
                canvas[y][x] = '█'

    # 标记数据点
    for x, y in points:
        if 0 <= x < size * 2 + 1 and 0 <= y < size * 2 + 1:
            canvas[y][x] = '★'

    # 转为字符串
    for row in canvas:
        lines.append('  ' + ''.join(row))

    # 添加标签
    label_lines = []
    for i in range(n):
        val = values[i]
        label = labels[i][:6]
        label_lines.append(f"  {label}: {val:.1f}")

    return '\n'.join(lines) + '\n' + '\n'.join(label_lines)


def render_bar_chart(values: list, labels: list, width: int = 30) -> str:
    """生成水平条形图"""
    max_val = max(values) if values else 1
    lines = []
    for label, val in zip(labels, values):
        bar_len = int((val / max_val) * width) if max_val > 0 else 0
        bar = '█' * bar_len + '░' * (width - bar_len)
        lines.append(f"  {label:>8s} │{bar}│ {val:.2f}")
    return '\n'.join(lines)


# ═══════════════════════════════════════════════
# 对战系统
# ═══════════════════════════════════════════════

class BattleArena:
    """对战竞技场 - 增强竞争表现性"""

    def __init__(self, arena: ArenaV2 = None):
        self.arena = arena or ArenaV2()

    # ─────────────────────────────────────────
    # 盲测模式（借鉴 Chatbot Arena）
    # ─────────────────────────────────────────

    def blind_battle(self, model_a: str, model_b: str):
        """
        盲测对决 - 隐藏模型身份，让用户投票
        借鉴 lmarena 的核心机制
        """
        pa = self.arena.profiles.get(model_a)
        pb = self.arena.profiles.get(model_b)

        if not pa or not pb:
            print("❌ 模型未注册")
            return

        print(f"\n{Colors.BOLD}{Colors.CYAN}{'═'*60}{Colors.RESET}")
        print(f"  {Colors.BOLD}⚔️  盲测对决 - 你来投票！{Colors.RESET}")
        print(f"{Colors.CYAN}{'═'*60}{Colors.RESET}")
        print()
        print(f"  模型 A 和模型 B 将回答同一个问题")
        print(f"  你不知道谁是谁，投票选出更好的回答")
        print()
        print(f"  {Colors.DIM}输入 1 = A更好, 2 = B更好, 0 = 平局{Colors.RESET}")
        print()

        # 展示匿名对战信息
        print(f"  {Colors.BOLD}模型 A{Colors.RESET}")
        print(f"    Elo: ???  心情: ???  排名: ???")
        print()
        print(f"  {Colors.BOLD}模型 B{Colors.RESET}")
        print(f"    Elo: ???  心情: ???  排名: ???")
        print()
        print(f"  {Colors.YELLOW}请在外部完成对决后回来投票{Colors.RESET}")
        print(f"  {Colors.DIM}对决完成后输入投票结果:{Colors.RESET}")

        return {
            "model_a": model_a,
            "model_b": model_b,
            "type": "blind",
        }

    def vote(self, model_a: str, model_b: str, winner: str,
             user_score_a: float = None, user_score_b: float = None):
        """
        投票结果
        winner: "a" / "b" / "draw"
        """
        if winner == "a":
            self.arena.profiles[model_a].wins += 1
            self.arena.profiles[model_b].losses += 1
            self._update_streak(model_a, "win")
            self._update_streak(model_b, "loss")
            result_text = f"{self.arena.profiles[model_a].display_name} 胜出！"
        elif winner == "b":
            self.arena.profiles[model_b].wins += 1
            self.arena.profiles[model_a].losses += 1
            self._update_streak(model_b, "win")
            self._update_streak(model_a, "loss")
            result_text = f"{self.arena.profiles[model_b].display_name} 胜出！"
        else:
            self.arena.profiles[model_a].draws += 1
            self.arena.profiles[model_b].draws += 1
            result_text = "平局！"

        # 用户满意度
        if user_score_a is not None:
            n = self.arena.profiles[model_a].matches
            self.arena.profiles[model_a].user_satisfaction = (
                (n * self.arena.profiles[model_a].user_satisfaction + user_score_a) / (n + 1)
            )
        if user_score_b is not None:
            n = self.arena.profiles[model_b].matches
            self.arena.profiles[model_b].user_satisfaction = (
                (n * self.arena.profiles[model_b].user_satisfaction + user_score_b) / (n + 1)
            )

        self.arena._save()
        return result_text

    def _update_streak(self, model_id: str, result: str):
        p = self.arena.profiles[model_id]
        if p.streak_type == result:
            p.current_streak += 1
        else:
            p.streak_type = result
            p.current_streak = 1
        if result == "win":
            p.best_win_streak = max(p.best_win_streak, p.current_streak)
        else:
            p.worst_loss_streak = max(p.worst_loss_streak, p.current_streak)

    # ─────────────────────────────────────────
    # 对战动画
    # ─────────────────────────────────────────

    def battle_animation(self, model_a: str, model_b: str, winner: str):
        """对战结果动画"""
        pa = self.arena.profiles.get(model_a)
        pb = self.arena.profiles.get(model_b)
        if not pa or not pb:
            return

        mood_a = self.arena.get_ranking("all")
        mood_b = self.arena.get_ranking("all")
        mood_a_emoji = "😐"
        mood_b_emoji = "😐"
        for r in mood_a:
            if r["model_id"] == model_a:
                mood_a_emoji = r.get("mood", {}).get("emoji", "😐")
            if r["model_id"] == model_b:
                mood_b_emoji = r.get("mood", {}).get("emoji", "😐")

        print(f"\n{Colors.BOLD}{Colors.CYAN}{'═'*60}{Colors.RESET}")
        print(f"  {Colors.BOLD}⚔️  对战结果{Colors.RESET}")
        print(f"{Colors.CYAN}{'═'*60}{Colors.RESET}")
        print()

        if winner == "a":
            print(f"  {Colors.GREEN}🏆 {pa.display_name} {mood_a_emoji} 胜出！{Colors.RESET}")
            print(f"  {Colors.RED}   {pb.display_name} {mood_b_emoji} 惜败{Colors.RESET}")
            # trash talk
            talk = random.choice(MODEL_PERSONALITY["trash_talk"]["winning"])
            print(f"\n  {pa.display_name}: \"{talk}\"")
            talk2 = random.choice(MODEL_PERSONALITY["trash_talk"]["losing"])
            print(f"  {pb.display_name}: \"{talk2}\"")
        elif winner == "b":
            print(f"  {Colors.GREEN}🏆 {pb.display_name} {mood_b_emoji} 胜出！{Colors.RESET}")
            print(f"  {Colors.RED}   {pa.display_name} {mood_a_emoji} 惜败{Colors.RESET}")
            talk = random.choice(MODEL_PERSONALITY["trash_talk"]["winning"])
            print(f"\n  {pb.display_name}: \"{talk}\"")
            talk2 = random.choice(MODEL_PERSONALITY["trash_talk"]["losing"])
            print(f"  {pa.display_name}: \"{talk2}\"")
        else:
            print(f"  {Colors.YELLOW}🤝 平局！{Colors.RESET}")

        # 显示双方数据对比
        print(f"\n  {'─'*50}")
        self._show_comparison(pa, pb)
        print()

    def _show_comparison(self, pa, pb):
        """双模型数据对比"""
        dims = [
            ("Token", pa.avg_tokens, pb.avg_tokens, True),   # 越低越好
            ("速度", pa.avg_think_time, pb.avg_think_time, True),
            ("质量", pa.avg_quality, pb.avg_quality, False),
            ("一致性", pa.avg_consistency, pb.avg_consistency, False),
            ("Elo", pa.elo, pb.elo, False),
        ]

        print(f"\n  {'指标':^8} {'─'*8} {pa.display_name[:12]:^12} {'─'*4} {pb.display_name[:12]:^12}")
        for name, va, vb, lower_better in dims:
            if lower_better:
                a_color = Colors.GREEN if va < vb else Colors.RED
                b_color = Colors.GREEN if vb < va else Colors.RED
            else:
                a_color = Colors.GREEN if va > vb else Colors.RED
                b_color = Colors.GREEN if vb > va else Colors.RED

            print(f"  {name:^8}   {a_color}{va:>8.2f}{Colors.RESET}     {b_color}{vb:>8.2f}{Colors.RESET}")

    # ─────────────────────────────────────────
    # 雷达图对比
    # ─────────────────────────────────────────

    def show_radar(self, model_id: str):
        """显示单模型雷达图"""
        p = self.arena.profiles.get(model_id)
        if not p:
            print(f"❌ 模型 '{model_id}' 不存在")
            return

        labels = ["Token", "速度", "质量", "一致性", "错误率", "性价比", "延迟", "趋势", "胜率", "满意"]
        values = [
            max(0, 10 - (p.avg_tokens / 1000)),
            max(0, 10 - (p.avg_think_time / 6)),
            min(10, p.avg_quality),
            p.avg_consistency,
            max(0, 10 - p.avg_error_rate),
            min(10, p.avg_cost_efficiency),
            p.avg_latency_stability,
            max(0, p.improvement_trend + 5),
            p.win_rate,
            p.user_satisfaction,
        ]

        print(f"\n{Colors.BOLD}{Colors.CYAN}{'═'*50}{Colors.RESET}")
        print(f"  📊 {p.display_name} - 10维雷达图")
        print(f"{Colors.CYAN}{'═'*50}{Colors.RESET}")
        print()
        print(render_bar_chart(values, labels, width=25))
        print()

    def show_radar_compare(self, model_a: str, model_b: str):
        """双模型雷达图对比"""
        pa = self.arena.profiles.get(model_a)
        pb = self.arena.profiles.get(model_b)
        if not pa or not pb:
            print("❌ 模型不存在")
            return

        labels = ["Token", "速度", "质量", "一致性", "错误率", "性价比", "延迟", "趋势", "胜率", "满意"]

        def get_values(p):
            return [
                max(0, 10 - (p.avg_tokens / 1000)),
                max(0, 10 - (p.avg_think_time / 6)),
                min(10, p.avg_quality),
                p.avg_consistency,
                max(0, 10 - p.avg_error_rate),
                min(10, p.avg_cost_efficiency),
                p.avg_latency_stability,
                max(0, p.improvement_trend + 5),
                p.win_rate,
                p.user_satisfaction,
            ]

        va = get_values(pa)
        vb = get_values(pb)

        print(f"\n{Colors.BOLD}{Colors.CYAN}{'═'*60}{Colors.RESET}")
        print(f"  📊 {pa.display_name} vs {pb.display_name}")
        print(f"{Colors.CYAN}{'═'*60}{Colors.RESET}")
        print()

        # 并排条形图
        max_val = max(max(va), max(vb))
        width = 20
        for i, label in enumerate(labels):
            bar_a = int((va[i] / max_val) * width) if max_val > 0 else 0
            bar_b = int((vb[i] / max_val) * width) if max_val > 0 else 0

            color_a = Colors.GREEN if va[i] >= vb[i] else Colors.DIM
            color_b = Colors.GREEN if vb[i] >= va[i] else Colors.DIM

            print(f"  {label:>6s} │{color_a}{'█' * bar_a}{'░' * (width - bar_a)}{Colors.RESET}│"
                  f" {va[i]:5.2f}  │{color_b}{'█' * bar_b}{'░' * (width - bar_b)}{Colors.RESET}│ {vb[i]:5.2f}")

        print(f"\n  {'':>6s}  {pa.display_name[:20]:^{width+2}s}    {pb.display_name[:20]:^{width+2}s}")
        print()

    # ─────────────────────────────────────────
    # 排行榜可视化（增强版）
    # ─────────────────────────────────────────

    def show_leaderboard(self, period: str = "all"):
        """增强版排行榜"""
        ranking = self.arena.get_ranking(period)

        period_config = {
            "daily":   {"name": "日榜", "emoji": "☀️"},
            "weekly":  {"name": "周榜", "emoji": "📅"},
            "monthly": {"name": "月榜", "emoji": "📆"},
            "all":     {"name": "总榜", "emoji": "🏆"},
        }
        cfg = period_config.get(period, {"name": period, "emoji": "📊"})

        print(f"\n{Colors.BOLD}{Colors.CYAN}{'═'*80}{Colors.RESET}")
        print(f"  {cfg['emoji']}  LLM Arena {cfg['name']}  {cfg['emoji']}")
        print(f"{Colors.CYAN}{'═'*80}{Colors.RESET}")

        if not ranking:
            print(f"\n  {Colors.DIM}暂无数据{Colors.RESET}\n")
            return

        # 段位系统（借鉴游戏排名）
        tiers = [
            (0.1, "🏆 传奇", Colors.YELLOW),
            (0.2, "💎 钻石", Colors.CYAN),
            (0.4, "🥇 黄金", Colors.GREEN),
            (0.6, "🥈 白银", Colors.WHITE),
            (0.8, "🥉 青铜", Colors.DIM),
            (1.0, "⬜ 黑铁", Colors.RED),
        ]

        def get_tier(rank, total):
            ratio = rank / total
            for threshold, name, color in tiers:
                if ratio <= threshold:
                    return name, color
            return tiers[-1][1], tiers[-1][2]

        total = len(ranking)
        max_elo = max(r["elo"] for r in ranking) if ranking else 1500

        for i, r in enumerate(ranking):
            rank = i + 1
            mood = r.get("mood", {}).get("emoji", "😐")
            tier_name, tier_color = get_tier(rank, total)
            override = " 👑" if r.get("user_override_rank", 0) > 0 else ""

            # Elo 条形图
            elo_bar_len = int((r["elo"] / max_elo) * 15) if max_elo > 0 else 0
            elo_bar = '█' * elo_bar_len + '░' * (15 - elo_bar_len)

            # 连胜
            streak = ""
            if r["streak_type"] == "win" and r["current_streak"] >= 3:
                streak = f" 🔥x{r['current_streak']}"
            elif r["streak_type"] == "loss" and r["current_streak"] >= 3:
                streak = f" 💔x{r['current_streak']}"

            # 成就
            ach = r.get("achievement_count", 0)
            ach_str = f" 🏅{ach}" if ach > 0 else ""

            # 排名标记
            if rank <= 3:
                medal = ["🥇", "🥈", "🥉"][rank - 1]
            else:
                medal = f"{rank:2d}"

            name = r["display_name"][:20]
            elo = r["elo"]
            eff = r["efficiency_score"]

            print(f"  {medal} {mood} {tier_color}{tier_name:6s}{Colors.RESET} "
                  f"{name:<20s} {elo_bar} {elo:4.0f}  "
                  f"效率:{eff:5.2f}  Q:{r['avg_quality']:.1f}"
                  f"{streak}{ach_str}{override}")

        # 段位分布
        print(f"\n  {Colors.BOLD}段位分布:{Colors.RESET}")
        for threshold, name, color in tiers:
            count = sum(1 for i in range(total) if (i + 1) / total <= threshold)
            print(f"    {color}{name}{Colors.RESET}: {count} 个模型")

        print()

    # ─────────────────────────────────────────
    # 荣誉殿堂 / 耻辱墙
    # ─────────────────────────────────────────

    def show_hall_of_fame(self):
        """荣誉殿堂"""
        ranking = self.arena.get_ranking("all")

        print(f"\n{Colors.BOLD}{Colors.YELLOW}{'═'*55}{Colors.RESET}")
        print(f"  {Colors.YELLOW}👑  荣誉殿堂{Colors.RESET}")
        print(f"{Colors.YELLOW}{'═'*55}{Colors.RESET}")

        # 冠军
        if ranking:
            c = ranking[0]
            mood = c.get("mood", {}).get("emoji", "😐")
            print(f"\n  {Colors.YELLOW}👑 当前冠军: {c['display_name']} {mood}{Colors.RESET}")
            print(f"     Elo: {c['elo']:.0f}  效率分: {c['efficiency_score']:.3f}")

        # 最佳连胜
        best_streak = max(
            ((p.best_win_streak, mid) for mid, p in self.arena.profiles.items()),
            default=(0, "")
        )
        if best_streak[0] > 0:
            p = self.arena.profiles.get(best_streak[1])
            if p:
                print(f"\n  🔥 最长连胜: {p.display_name} ({best_streak[0]} 连胜)")

        # 最多成就
        most_ach = max(
            ((len(p.achievements), mid) for mid, p in self.arena.profiles.items()),
            default=(0, "")
        )
        if most_ach[0] > 0:
            p = self.arena.profiles.get(most_ach[1])
            if p:
                print(f"  🏅 最多成就: {p.display_name} ({most_ach[0]} 个)")

        # 最高 Elo
        peak = max(
            ((p.peak_elo, mid) for mid, p in self.arena.profiles.items()),
            default=(0, "")
        )
        if peak[0] > 0:
            p = self.arena.profiles.get(peak[1])
            if p:
                print(f"  ♟️  最高 Elo: {p.display_name} ({peak[0]:.0f})")

        # 用户最爱
        for mid, p in self.arena.profiles.items():
            if p.user_override_rank == 1:
                print(f"  ❤️  用户最爱: {p.display_name}")
                break

        print()

    def show_wall_of_shame(self):
        """耻辱墙"""
        ranking = self.arena.get_ranking("all")

        print(f"\n{Colors.BOLD}{Colors.RED}{'═'*55}{Colors.RESET}")
        print(f"  {Colors.RED}💀  耻辱墙{Colors.RESET}")
        print(f"{Colors.RED}{'═'*55}{Colors.RESET}")

        if not ranking:
            print(f"\n  {Colors.DIM}暂无数据{Colors.RESET}\n")
            return

        # 最后一名
        last = ranking[-1]
        mood = last.get("mood", {}).get("emoji", "😐")
        print(f"\n  {Colors.RED}💀 垫底: {last['display_name']} {mood}{Colors.RESET}")
        print(f"     Elo: {last['elo']:.0f}  效率分: {last['efficiency_score']:.3f}")

        # 最长连败
        worst_streak = max(
            ((p.worst_loss_streak, mid) for mid, p in self.arena.profiles.items()),
            default=(0, "")
        )
        if worst_streak[0] > 0:
            p = self.arena.profiles.get(worst_streak[1])
            if p:
                print(f"  💔 最长连败: {p.display_name} ({worst_streak[0]} 连败)")

        # 最低 Elo
        lowest = min(
            ((p.elo, mid) for mid, p in self.arena.profiles.items()),
            default=(9999, "")
        )
        if lowest[0] < 1200:
            p = self.arena.profiles.get(lowest[1])
            if p:
                print(f"  📉 最低 Elo: {p.display_name} ({lowest[0]:.0f})")

        # 被封禁
        banned = [p.display_name for p in self.arena.profiles.values() if p.banned]
        if banned:
            print(f"  🚫 被封禁: {', '.join(banned)}")

        print()

    # ─────────────────────────────────────────
    # 周期性奖项
    # ─────────────────────────────────────────

    def show_weekly_awards(self):
        """周度奖项"""
        ranking = self.arena.get_ranking("weekly")

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'═'*55}{Colors.RESET}")
        print(f"  {Colors.MAGENTA}⭐  本周奖项{Colors.RESET}")
        print(f"{Colors.MAGENTA}{'═'*55}{Colors.RESET}")

        if not ranking:
            print(f"\n  {Colors.DIM}本周暂无数据{Colors.RESET}\n")
            return

        # MVP
        mvp = ranking[0]
        print(f"\n  🌟 本周之星: {mvp['display_name']}")
        print(f"     Elo: {mvp['elo']:.0f}  效率分: {mvp['efficiency_score']:.3f}")

        # 进步最大
        improvers = sorted(ranking, key=lambda x: x.get("improvement_trend", 0), reverse=True)
        if improvers and improvers[0].get("improvement_trend", 0) > 0:
            print(f"  📈 进步之星: {improvers[0]['display_name']}")

        # 最活跃
        most_active = sorted(ranking, key=lambda x: x.get("matches", 0), reverse=True)
        if most_active:
            print(f"  ⚙️ 最活跃: {most_active[0]['display_name']} ({most_active[0]['matches']} 场)")

        print()


def main():
    import sys
    battle = BattleArena()

    if len(sys.argv) < 2:
        print("用法: python battle_arena.py <command> [args]")
        print("  blind <a> <b>        盲测对决")
        print("  vote <a> <b> <w>     投票 (w=a/b/draw)")
        print("  radar <model>        雷达图")
        print("  compare <a> <b>      双模型对比")
        print("  leaderboard [period] 增强排行榜")
        print("  fame                 荣誉殿堂")
        print("  shame                耻辱墙")
        print("  weekly               本周奖项")
        return

    cmd = sys.argv[1]

    if cmd == "blind":
        battle.blind_battle(sys.argv[2], sys.argv[3])
    elif cmd == "vote":
        battle.vote(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "radar":
        battle.show_radar(sys.argv[2])
    elif cmd == "compare":
        battle.show_radar_compare(sys.argv[2], sys.argv[3])
    elif cmd == "leaderboard":
        period = sys.argv[2] if len(sys.argv) > 2 else "all"
        battle.show_leaderboard(period)
    elif cmd == "fame":
        battle.show_hall_of_fame()
    elif cmd == "shame":
        battle.show_wall_of_shame()
    elif cmd == "weekly":
        battle.show_weekly_awards()
    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()
