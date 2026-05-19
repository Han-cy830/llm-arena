"""
LLM Arena 排名展示系统
漂亮的日榜、周榜、月榜、总榜展示
"""

import json
from datetime import datetime
from pathlib import Path
from arena import LLMArena

DATA_DIR = Path(__file__).parent.parent / "data"

# ANSI 颜色代码
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
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"

MEDALS = ["🥇", "🥈", "🥉"]
TROPHY = "🏆"
FIRE = "🔥"
STAR = "⭐"
CROWN = "👑"
BAN = "🚫"
CHART = "📊"
CLOCK = "⏱️"
BOLT = "⚡"
TARGET = "🎯"


def _bar(value: float, max_val: float, width: int = 20) -> str:
    """生成进度条"""
    if max_val <= 0:
        return "░" * width
    filled = int((value / max_val) * width)
    filled = min(width, max(0, filled))
    return "█" * filled + "░" * (width - filled)


def _trend(history: list, field: str) -> str:
    """计算趋势箭头"""
    if len(history) < 2:
        return "  "
    recent = [h.get(field, 0) for h in history[-5:]]
    if len(recent) < 2:
        return "  "
    avg_recent = sum(recent[-3:]) / min(3, len(recent[-3:]))
    avg_older = sum(recent[:2]) / min(2, len(recent[:2]))
    if avg_recent > avg_older * 1.05:
        return " ↑"
    elif avg_recent < avg_older * 0.95:
        return " ↓"
    return " →"


class RankingDisplay:
    """排名展示器"""

    def __init__(self, arena: LLMArena = None):
        self.arena = arena or LLMArena()

    def show_all_rankings(self):
        """展示所有排行榜"""
        self.show_ranking("daily")
        self.show_ranking("weekly")
        self.show_ranking("monthly")
        self.show_ranking("all")

    def show_ranking(self, period: str = "all"):
        """展示单个排行榜"""
        ranking = self.arena.get_ranking(period)

        period_config = {
            "daily":   {"name": "日榜", "emoji": "☀️", "desc": "最近 24 小时"},
            "weekly":  {"name": "周榜", "emoji": "📅", "desc": "最近 7 天"},
            "monthly": {"name": "月榜", "emoji": "📆", "desc": "最近 30 天"},
            "all":     {"name": "总榜", "emoji": TROPHY, "desc": "全部历史"},
        }

        cfg = period_config.get(period, {"name": period, "emoji": CHART, "desc": period})

        print(f"\n{Colors.BOLD}{Colors.CYAN}{'═'*72}{Colors.RESET}")
        print(f"{Colors.BOLD}  {cfg['emoji']}  LLM Arena {cfg['name']}  —  {cfg['desc']}{Colors.RESET}")
        print(f"{Colors.CYAN}{'═'*72}{Colors.RESET}")

        if not ranking:
            print(f"\n  {Colors.DIM}暂无数据{Colors.RESET}\n")
            return

        # 表头
        print(f"\n  {Colors.DIM}{'排名':^6} {'模型':^28} {'效率分':^8} {'Token':^8} {'耗时':^8} {'质量':^8} {'战绩':^12}{Colors.RESET}")
        print(f"  {Colors.DIM}{'─'*6} {'─'*28} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*12}{Colors.RESET}")

        max_score = max(r["efficiency_score"] for r in ranking) if ranking else 1

        for i, r in enumerate(ranking):
            # 排名标记
            if i < 3:
                rank_str = f" {MEDALS[i]} "
            else:
                rank_str = f" {i+1:2d} "

            # 用户否决标记
            override_mark = f" {CROWN}" if r.get("user_override_rank", 0) > 0 else ""

            # 效率分颜色
            score = r["efficiency_score"]
            if score >= max_score * 0.8:
                score_color = Colors.GREEN
            elif score >= max_score * 0.5:
                score_color = Colors.YELLOW
            else:
                score_color = Colors.RED

            # 质量颜色
            quality = r["avg_quality"]
            if quality >= 8:
                q_color = Colors.GREEN
            elif quality >= 6:
                q_color = Colors.YELLOW
            else:
                q_color = Colors.RED

            # 战绩
            wins = r["wins"]
            losses = r["losses"]
            winrate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
            record = f"{wins}W-{losses}L {winrate:.0f}%"

            # 效率分进度条
            bar = _bar(score, max_score, 8)

            name = r["display_name"][:26]
            print(f"  {rank_str}  {name:<28s} {score_color}{score:6.2f}{Colors.RESET} "
                  f"{bar} {r['avg_tokens']:6.0f}  {r['avg_think_time']:5.1f}s "
                  f"{q_color}{r['avg_quality']:5.1f}{Colors.RESET}  {record}{override_mark}")

        print(f"\n  {Colors.DIM}总计 {len(ranking)} 个模型参与竞争{Colors.RESET}")

        # 显示被封禁的模型
        banned = [mid for mid, data in self.arena.overrides.items() if data.get("banned")]
        if banned:
            print(f"  {Colors.RED}{BAN} 被封禁: {', '.join(banned)}{Colors.RESET}")

        print()

    def show_model_detail(self, model_id: str):
        """展示单个模型详细数据"""
        if model_id not in self.arena.scores:
            print(f"❌ 模型 '{model_id}' 不存在")
            return

        s = self.arena.scores[model_id]

        print(f"\n{Colors.BOLD}{Colors.CYAN}{'═'*60}{Colors.RESET}")
        print(f"  {CHART} {s.display_name} 详细数据")
        print(f"{Colors.CYAN}{'═'*60}{Colors.RESET}")

        print(f"\n  模型ID:     {s.model_id}")
        print(f"  总场次:     {s.matches}")
        print(f"  战绩:       {s.wins}胜 {s.losses}负 {s.draws}平")
        print(f"  总得分:     {s.total_score:.2f}")
        print(f"  效率分:     {s.efficiency_score:.3f}")
        print(f"  平均Token:  {s.avg_tokens:.0f}")
        print(f"  平均耗时:   {s.avg_think_time:.2f}s")
        print(f"  平均质量:   {s.avg_quality:.2f}/10")

        # 效率分解
        print(f"\n  {Colors.BOLD}效率分解:{Colors.RESET}")
        token_score = max(0, 10 - (s.avg_tokens / 1000))
        speed_score = max(0, 10 - (s.avg_think_time / 6))
        quality_score = s.avg_quality

        print(f"    {BOLT} Token效率: {token_score:.1f}/10  {_bar(token_score, 10, 15)}")
        print(f"    {CLOCK} 速度得分: {speed_score:.1f}/10  {_bar(speed_score, 10, 15)}")
        print(f"    {TARGET} 质量得分: {quality_score:.1f}/10  {_bar(quality_score, 10, 15)}")

        # 最近历史
        if s.history:
            print(f"\n  {Colors.BOLD}最近表现 (最多显示10条):{Colors.RESET}")
            for h in s.history[-10:]:
                ts = h["timestamp"][:19]
                print(f"    {ts} | T:{h['tokens']:5d} | "
                      f"S:{h['think_time']:5.1f}s | Q:{h['quality']:4.1f} | "
                      f"得分:{h['match_score']:.3f} [{h.get('round', '?')}]")

        # 用户否决状态
        override = self.arena.overrides.get(model_id, {})
        if override:
            print(f"\n  {CROWN} 用户否决:")
            if override.get("banned"):
                print(f"    {BAN} 已被封禁")
            elif override.get("rank", 0) > 0:
                print(f"    强制排名: 第 {override['rank']} 名")

        print()

    def show_summary(self):
        """展示竞技场概览"""
        ranking = self.arena.get_ranking("all")

        print(f"\n{Colors.BOLD}{Colors.CYAN}{'═'*60}{Colors.RESET}")
        print(f"  {TROPHY}  LLM Arena 竞技场概览")
        print(f"{Colors.CYAN}{'═'*60}{Colors.RESET}")

        total_models = len(self.arena.scores)
        total_matches = sum(s.matches for s in self.arena.scores.values())

        print(f"\n  注册模型: {total_models}")
        print(f"  总对决数: {total_matches}")

        if ranking:
            top = ranking[0]
            print(f"\n  {STAR} 当前冠军: {top['display_name']}")
            print(f"     效率分: {top['efficiency_score']:.3f}")
            print(f"     战绩: {top['wins']}W-{top['losses']}L")

            if len(ranking) > 1:
                runner = ranking[1]
                print(f"\n  {FIRE} 挑战者: {runner['display_name']}")
                print(f"     效率分: {runner['efficiency_score']:.3f} "
                      f"(差距: {top['efficiency_score'] - runner['efficiency_score']:.3f})")

        # API 优先级
        priority = self.arena.get_priority_list()
        if priority:
            print(f"\n  {BOLT} API 调用优先级:")
            for i, mid in enumerate(priority[:5]):
                name = self.arena.scores[mid].display_name if mid in self.arena.scores else mid
                print(f"     {i+1}. {name}")
            if len(priority) > 5:
                print(f"     ... 共 {len(priority)} 个模型")

        print()

    def export_markdown(self, period: str = "all") -> str:
        """导出为 Markdown 格式（可用于 README 或分享）"""
        ranking = self.arena.get_ranking(period)

        period_names = {
            "daily": "日榜", "weekly": "周榜",
            "monthly": "月榜", "all": "总榜"
        }

        lines = [
            f"# LLM Arena {period_names.get(period, period)}排名",
            f"",
            f"> 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"| 排名 | 模型 | 效率分 | 平均Token | 平均耗时 | 平均质量 | 战绩 |",
            f"|:----:|------|-------:|----------:|---------:|--------:|------|",
        ]

        for i, r in enumerate(ranking):
            medal = MEDALS[i] if i < 3 else f"{i+1}"
            override = " 👑" if r.get("user_override_rank", 0) > 0 else ""
            record = f"{r['wins']}W-{r['losses']}L"
            lines.append(
                f"| {medal} | {r['display_name']}{override} | "
                f"{r['efficiency_score']:.3f} | {r['avg_tokens']:.0f} | "
                f"{r['avg_think_time']:.1f}s | {r['avg_quality']:.1f} | {record} |"
            )

        lines.append("")
        return "\n".join(lines)


def main():
    import sys
    display = RankingDisplay()

    if len(sys.argv) < 2:
        print("用法: python display.py <command> [args]")
        print("命令:")
        print("  all                  展示所有排行榜")
        print("  ranking [period]     展示指定排行榜 (daily/weekly/monthly/all)")
        print("  detail <model_id>    模型详细数据")
        print("  summary              竞技场概览")
        print("  export [period]      导出 Markdown")
        return

    cmd = sys.argv[1]

    if cmd == "all":
        display.show_all_rankings()
    elif cmd == "ranking":
        period = sys.argv[2] if len(sys.argv) > 2 else "all"
        display.show_ranking(period)
    elif cmd == "detail":
        display.show_model_detail(sys.argv[2])
    elif cmd == "summary":
        display.show_summary()
    elif cmd == "export":
        period = sys.argv[2] if len(sys.argv) > 2 else "all"
        print(display.export_markdown(period))
    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()
