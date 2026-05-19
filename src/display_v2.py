"""
LLM Arena V2 - 排名展示系统
10维评分 + Elo + emoji心情 + 成就展示
"""

import json
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

MEDALS = ["🥇", "🥈", "🥉"]
TROPHY = "🏆"
FIRE = "🔥"
STAR = "⭐"
CROWN = "👑"
BAN = "🚫"
CHART = "📊"
BOLT = "⚡"
TARGET = "🎯"
HEART = "❤️"
SWORD = "⚔️"


def _bar(value: float, max_val: float, width: int = 12) -> str:
    if max_val <= 0:
        return "░" * width
    filled = int((value / max_val) * width)
    filled = min(width, max(0, filled))
    return "█" * filled + "░" * (width - filled)


def _trend_arrow(trend: str) -> str:
    return {"up": "↑", "down": "↓", "stable": "→"}.get(trend, " ")


def _streak_display(streak: int, streak_type: str) -> str:
    if streak_type == "win" and streak >= 3:
        return f"🔥x{streak}"
    elif streak_type == "loss" and streak >= 3:
        return f"💔x{streak}"
    elif streak > 0:
        icon = "W" if streak_type == "win" else "L"
        return f"{icon}x{streak}"
    return ""


class DisplayV2:
    """进化版排名展示"""

    def __init__(self, arena: ArenaV2 = None):
        self.arena = arena or ArenaV2()

    def show_all(self):
        self.show_ranking("daily")
        self.show_ranking("weekly")
        self.show_ranking("monthly")
        self.show_ranking("all")
        self.show_achievements_board()

    def show_ranking(self, period: str = "all"):
        ranking = self.arena.get_ranking(period)

        period_config = {
            "daily":   {"name": "日榜", "emoji": "☀️"},
            "weekly":  {"name": "周榜", "emoji": "📅"},
            "monthly": {"name": "月榜", "emoji": "📆"},
            "all":     {"name": "总榜", "emoji": TROPHY},
        }
        cfg = period_config.get(period, {"name": period, "emoji": CHART})

        print(f"\n{Colors.BOLD}{Colors.CYAN}{'═'*80}{Colors.RESET}")
        print(f"{Colors.BOLD}  {cfg['emoji']}  LLM Arena {cfg['name']}  {cfg['emoji']}{Colors.RESET}")
        print(f"{Colors.CYAN}{'═'*80}{Colors.RESET}")

        if not ranking:
            print(f"\n  {Colors.DIM}暂无数据{Colors.RESET}\n")
            return

        # 表头
        print(f"\n  {'排名':^4} {'心情':^4} {'模型':^22} {'Elo':^6} {'效率分':^7} "
              f"{'Token':^6} {'速度':^6} {'质量':^5} {'一致性':^5} {'胜率':^5} {'趋势':^4} {'连胜':^6}")
        print(f"  {'─'*4} {'─'*4} {'─'*22} {'─'*6} {'─'*7} "
              f"{'─'*6} {'─'*6} {'─'*5} {'─'*5} {'─'*5} {'─'*4} {'─'*6}")

        max_elo = max(r["elo"] for r in ranking) if ranking else 1500

        for i, r in enumerate(ranking):
            # 排名
            if i < 3:
                rank_str = f"{MEDALS[i]}"
            else:
                rank_str = f"{i+1:2d}"

            # 心情
            mood = r.get("mood", {})
            mood_emoji = mood.get("emoji", "😐")

            # 用户否决标记
            override = f" {CROWN}" if r.get("user_override_rank", 0) > 0 else ""

            # Elo 颜色
            elo = r["elo"]
            if elo >= 1400:
                elo_color = Colors.GREEN
            elif elo >= 1200:
                elo_color = Colors.YELLOW
            else:
                elo_color = Colors.RED

            # 效率分颜色
            eff = r["efficiency_score"]
            if eff >= 7:
                eff_color = Colors.GREEN
            elif eff >= 5:
                eff_color = Colors.YELLOW
            else:
                eff_color = Colors.RED

            # 趋势
            trend = _trend_arrow(r["trend"])

            # 连胜
            streak = _streak_display(r["current_streak"], r["streak_type"])

            # 名字截断
            name = r["display_name"][:20]

            # 成就数量
            ach_count = r.get("achievement_count", 0)
            ach_str = f" 🏅{ach_count}" if ach_count > 0 else ""

            print(f"  {rank_str:^4} {mood_emoji:^4} {name:<22s} "
                  f"{elo_color}{elo:5.0f}{Colors.RESET} "
                  f"{eff_color}{eff:5.2f}{Colors.RESET}  "
                  f"{r['avg_tokens']:5.0f} {r['avg_think_time']:4.1f}s "
                  f"{r['avg_quality']:4.1f}  {r['avg_consistency']:4.1f}  "
                  f"{r['win_rate']:4.0f}% {trend}   {streak}{override}{ach_str}")

        print(f"\n  {Colors.DIM}总计 {len(ranking)} 个模型 | "
              f"心情随排名动态变化 | 用户否决权: {CROWN} 至高无上{Colors.RESET}")

        # 被封禁
        banned = [mid for mid, p in self.arena.profiles.items() if p.banned]
        if banned:
            print(f"  {Colors.RED}{BAN} 被封禁: {', '.join(banned)}{Colors.RESET}")
        print()

    def show_model_detail(self, model_id: str):
        if model_id not in self.arena.profiles:
            print(f"❌ 模型 '{model_id}' 不存在")
            return

        p = self.arena.profiles[model_id]
        rank = self.arena._get_rank(model_id)
        mood = {"emoji": "😐", "name": "未知"}

        print(f"\n{Colors.BOLD}{Colors.CYAN}{'═'*65}{Colors.RESET}")
        print(f"  {CHART} {p.display_name} 详细档案")
        print(f"{Colors.CYAN}{'═'*65}{Colors.RESET}")

        # 心情
        ranking = self.arena.get_ranking("all")
        for r in ranking:
            if r["model_id"] == model_id:
                mood = r.get("mood", mood)
                break

        print(f"\n  {mood['emoji']} {mood['name']}  |  排名 #{rank}  |  Elo {p.elo:.0f} (峰值 {p.peak_elo:.0f})")
        print(f"  模型ID:     {p.model_id}")
        print(f"  总场次:     {p.matches}  ({p.wins}W-{p.losses}L)")

        # 10维雷达
        print(f"\n  {Colors.BOLD}10 维评分:{Colors.RESET}")

        dims = [
            ("⚡ Token效率", max(0, 10 - (p.avg_tokens / 1000))),
            ("⏱️  思考速度", max(0, 10 - (p.avg_think_time / 6))),
            ("🎯 回答质量", p.avg_quality),
            ("📊 一致性", p.avg_consistency),
            ("🛡️  错误率", max(0, 10 - p.avg_error_rate)),
            ("💰 性价比", min(10, p.avg_cost_efficiency)),
            ("📈 延迟稳定", p.avg_latency_stability),
            ("🔄 进步趋势", max(0, p.improvement_trend + 5)),
            ("⚔️  胜率", p.win_rate),
            (f"{HEART} 用户满意", p.user_satisfaction),
        ]

        for name, val in dims:
            bar = _bar(val, 10, 15)
            color = Colors.GREEN if val >= 7 else (Colors.YELLOW if val >= 4 else Colors.RED)
            print(f"    {name:12s} {color}{val:5.2f}{Colors.RESET} {bar}")

        # 连胜记录
        print(f"\n  {Colors.BOLD}战斗记录:{Colors.RESET}")
        print(f"    当前连胜: {_streak_display(p.current_streak, p.streak_type)}")
        print(f"    最长连胜: {p.best_win_streak}W")
        print(f"    最长连败: {p.worst_loss_streak}L")
        print(f"    趋势: {p.trend} {_trend_arrow(p.trend)} (强度 {p.trend_strength:.1f})")

        # 成就
        if p.achievements:
            print(f"\n  {Colors.BOLD}成就 ({len(p.achievements)}/{len(ACHIEVEMENTS)}):{Colors.RESET}")
            for aid in p.achievements:
                ach = ACHIEVEMENTS.get(aid, {})
                print(f"    {ach.get('emoji', '?')} {ach.get('name', aid)} — {ach.get('desc', '')}")
        else:
            print(f"\n  {Colors.DIM}暂无成就，继续努力！{Colors.RESET}")

        # 用户否决
        if p.user_override_rank > 0:
            print(f"\n  {CROWN} 用户否决: 强制排名 #{p.user_override_rank}")
        if p.banned:
            print(f"\n  {BAN} 已被封禁")

        # 最近历史
        if p.history:
            print(f"\n  {Colors.BOLD}最近 5 场:{Colors.RESET}")
            for h in p.history[-5:]:
                ts = h["timestamp"][:16]
                err = " ❌" if h.get("error") else ""
                print(f"    {ts} | T:{h['tokens']:5d} | "
                      f"S:{h['think_time']:4.1f}s | Q:{h['quality']:4.1f} | "
                      f"得分:{h['match_score']:.3f}{err}")

        print()

    def show_achievements_board(self):
        """成就总览"""
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'═'*65}{Colors.RESET}")
        print(f"  🏅  成就殿堂")
        print(f"{Colors.MAGENTA}{'═'*65}{Colors.RESET}")

        # 统计每个成就的获得者
        achievement_owners = {}
        for mid, p in self.arena.profiles.items():
            for aid in p.achievements:
                achievement_owners.setdefault(aid, []).append(p.display_name)

        for aid, ach in ACHIEVEMENTS.items():
            owners = achievement_owners.get(aid, [])
            if owners:
                owner_str = ", ".join(owners[:3])
                if len(owners) > 3:
                    owner_str += f" +{len(owners)-3}"
                print(f"  {ach['emoji']} {ach['name']:12s} — {ach['desc']:25s} | {owner_str}")
            else:
                print(f"  {Colors.DIM}{ach['emoji']} {ach['name']:12s} — {ach['desc']}{Colors.RESET}")

        print()

    def show_mood_board(self):
        """心情总览"""
        ranking = self.arena.get_ranking("all")

        print(f"\n{Colors.BOLD}{Colors.CYAN}{'═'*55}{Colors.RESET}")
        print(f"  😊  模型心情总览")
        print(f"{Colors.CYAN}{'═'*55}{Colors.RESET}\n")

        for r in ranking:
            mood = r.get("mood", {})
            streak = _streak_display(r["current_streak"], r["streak_type"])
            print(f"  {mood.get('emoji', '😐')} {r['display_name']:25s} {mood.get('name', '未知'):10s} "
                  f"| Elo {r['elo']:4.0f} | #{r.get('rank', '?')} {streak}")

        print()

    def export_markdown(self, period: str = "all") -> str:
        ranking = self.arena.get_ranking(period)
        period_names = {"daily": "日榜", "weekly": "周榜", "monthly": "月榜", "all": "总榜"}

        lines = [
            f"# LLM Arena {period_names.get(period, period)}排名",
            f"",
            f"> 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"| 排名 | 心情 | 模型 | Elo | 效率分 | 质量 | 胜率 | 趋势 | 成就 |",
            f"|:----:|:----:|------|----:|-------:|-----:|-----:|:----:|-----:|",
        ]

        for i, r in enumerate(ranking):
            medal = MEDALS[i] if i < 3 else f"{i+1}"
            mood = r.get("mood", {}).get("emoji", "😐")
            override = " 👑" if r.get("user_override_rank", 0) > 0 else ""
            trend = _trend_arrow(r["trend"])
            ach = r.get("achievement_count", 0)
            lines.append(
                f"| {medal} | {mood} | {r['display_name']}{override} | "
                f"{r['elo']:.0f} | {r['efficiency_score']:.3f} | "
                f"{r['avg_quality']:.1f} | {r['win_rate']:.0f}% | {trend} | {ach} |"
            )

        return "\n".join(lines)


def main():
    import sys
    display = DisplayV2()

    if len(sys.argv) < 2:
        print("用法: python display_v2.py <command> [args]")
        print("  all              全部排行榜")
        print("  ranking [period] 指定排行榜")
        print("  detail <model>   模型详情")
        print("  mood             心情总览")
        print("  achievements     成就殿堂")
        print("  export [period]  导出 Markdown")
        return

    cmd = sys.argv[1]

    if cmd == "all":
        display.show_all()
    elif cmd in ("daily", "weekly", "monthly", "total", "all"):
        period = "all" if cmd == "total" else cmd
        display.show_ranking(period)
    elif cmd == "ranking":
        period = sys.argv[2] if len(sys.argv) > 2 else "all"
        display.show_ranking(period)
    elif cmd == "detail":
        display.show_model_detail(sys.argv[2])
    elif cmd == "mood":
        display.show_mood_board()
    elif cmd == "achievements":
        display.show_achievements_board()
    elif cmd == "export":
        period = sys.argv[2] if len(sys.argv) > 2 else "all"
        print(display.export_markdown(period))
    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()
