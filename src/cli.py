"""
LLM Arena CLI
统一命令行入口，管理竞技场、供应商切换、排名展示
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from arena_v2 import ArenaV2
from switcher import APISwitcher
from display_v2 import DisplayV2


def print_help():
    print("""
╔════════════════════════════════════════════════════════════════════╗
║         🏆 LLM Arena V2 - 大模型竞技场 (10维评分 + 心情系统)      ║
╚════════════════════════════════════════════════════════════════════╝

供应商管理:
  provider list                      列出所有供应商
  provider switch <id> [model]       切换供应商/模型
  provider active                    查看当前配置
  provider info <id>                 供应商详情
  provider history [limit]           切换历史
  provider env                       生成环境变量配置
  provider add <id> <json>           添加自定义供应商
  provider remove <id>               移除供应商

竞技场 (10维评分):
  arena register <id> [name]         注册模型
  arena record <id> <t> <s> <q>     记录表现 (token/耗时/质量)
  arena battle <json_file>           多模型对决 (自动Elo评级)
  arena veto <id> <rank|ban>         用户否决权 (至高无上)
  arena rate <id> <0-10>             用户满意度评分

排名展示:
  rank                               展示所有排行榜 (含心情)
  rank daily                         日榜
  rank weekly                        周榜
  rank monthly                       月榜
  rank total                         总榜
  rank detail <model_id>             模型详情 (10维雷达)
  rank mood                          心情总览
  rank achievements                  成就殿堂
  rank export [period]               导出 Markdown

快捷操作:
  quick <provider_id>                快速切换并显示配置
  status                             完整状态面板
  help                               显示此帮助

评分维度 (10维):
  ⚡Token效率 ⏱️思考速度 🎯回答质量 📊一致性 🛡️错误率
  💰性价比 📈延迟稳定 🔄进步趋势 ⚔️胜率 ❤️用户满意度
""")


def cmd_provider(args):
    switcher = APISwitcher()

    if not args:
        print("用法: provider <list|switch|active|info|history|env|add|remove>")
        return

    sub = args[0]

    if sub == "list":
        providers = switcher.list_providers()
        print(f"\n  {'可用供应商':^20} ({len(providers)} 个)")
        print(f"  {'─'*65}")

        # 按是否配置了 key 分组
        with_key = [p for p in providers if p["has_key"]]
        without_key = [p for p in providers if not p["has_key"]]

        if with_key:
            print(f"\n  ✅ 已配置 API Key:")
            for p in with_key:
                active = " ← 当前" if p["active"] else ""
                print(f"     🔑 {p['id']:25s} {p['name']:25s}{active}")
                if p["active"]:
                    print(f"        └─ 模型: {p['default_model']}")

        if without_key:
            print(f"\n  ❌ 未配置 API Key:")
            for p in without_key:
                active = " ← 当前" if p["active"] else ""
                print(f"     ❌ {p['id']:25s} {p['name']:25s}{active}")

        print()

    elif sub == "switch":
        if len(args) < 2:
            print("用法: provider switch <provider_id> [model_id]")
            return
        result = switcher.switch(args[1], args[2] if len(args) > 2 else None)
        if result.get("error"):
            print(f"❌ {result['error']}")
        else:
            print(f"✅ 已切换到: {result['provider']} / {result['model']}")

    elif sub == "active":
        config = switcher.get_active_config()
        if "error" in config:
            print(f"❌ {config['error']}")
        else:
            print(f"\n  当前活跃配置:")
            print(f"  {'─'*40}")
            print(f"  供应商: {config['provider_name']}")
            print(f"  模型:   {config['model']}")
            print(f"  URL:    {config['base_url']}")
            print(f"  类型:   {config['api_type']}")

    elif sub == "info":
        if len(args) < 2:
            print("用法: provider info <provider_id>")
            return
        info = switcher.get_provider_info(args[1])
        if "error" in info:
            print(f"❌ {info['error']}")
        else:
            print(f"\n  {info['name']} ({info['id']})")
            print(f"  URL:  {info['base_url']}")
            print(f"  类型: {info['api_type']}")
            print(f"  Key:  {info['env_key']} {'✅' if info['has_key'] else '❌'}")
            print(f"  模型:")
            for m in info["models"]:
                default = " (默认)" if m == info["default_model"] else ""
                print(f"    - {m}{default}")

    elif sub == "history":
        limit = int(args[1]) if len(args) > 1 else 20
        history = switcher.get_switch_history(limit)
        if not history:
            print("暂无切换历史")
        else:
            print(f"\n  最近 {len(history)} 次切换:")
            for h in history:
                ts = h["timestamp"][:19]
                frm = f"{h['from']['provider']}/{h['from']['model']}"
                to = f"{h['to']['provider']}/{h['to']['model']}"
                print(f"    {ts}  {frm} → {to}")

    elif sub == "env":
        result = switcher.apply_to_claude_code()
        if "error" in result:
            print(f"❌ {result['error']}")
        else:
            print(f"\n  📋 环境变量配置 ({result['provider']}):")
            print(f"\n{result['shell_export']}")
            print(f"\n  💡 将上述命令添加到 ~/.bashrc 或 ~/.zshrc")

    elif sub == "add":
        if len(args) < 3:
            print("用法: provider add <id> <json_file>")
            return
        with open(args[2], "r", encoding="utf-8") as f:
            config = json.load(f)
        result = switcher.add_provider(args[1], config)
        if result.get("error"):
            print(f"❌ {result['error']}")
        else:
            print(f"✅ 已添加: {result['provider']}")

    elif sub == "remove":
        if len(args) < 2:
            print("用法: provider remove <id>")
            return
        result = switcher.remove_provider(args[1])
        if result.get("error"):
            print(f"❌ {result['error']}")
        else:
            print(f"✅ 已移除: {result['removed']}")

    else:
        print(f"未知子命令: {sub}")


def cmd_arena(args):
    arena = ArenaV2()

    if not args:
        print("用法: arena <register|record|battle|veto|rate|weights>")
        return

    sub = args[0]

    if sub == "register":
        if len(args) < 2:
            print("用法: arena register <model_id> [display_name]")
            return
        arena.register(args[1], args[2] if len(args) > 2 else "")
        print(f"✅ 模型 [{args[1]}] 已注册")

    elif sub == "record":
        if len(args) < 5:
            print("用法: arena record <model_id> <tokens> <think_time> <quality> [error]")
            return
        error = args[5].lower() in ("true", "1", "yes") if len(args) > 5 else False
        score = arena.record_match(args[1], int(args[2]), float(args[3]), float(args[4]), error=error)
        print(f"📊 记录完成，本次效率分: {score:.3f}")

    elif sub == "battle":
        if len(args) < 2:
            print("用法: arena battle <json_file>")
            return
        with open(args[1], "r", encoding="utf-8") as f:
            data = json.load(f)
        winner, results = arena.record_battle(data)
        print(f"\n🏆 胜者: {winner}")
        for mid, sc in results:
            p = arena.profiles.get(mid)
            if p:
                elo = p.elo
                print(f"  {mid}: {sc:.3f} (Elo: {elo:.0f})")

    elif sub == "veto":
        if len(args) < 3:
            print("用法: arena veto <model_id> <rank_number|ban>")
            return
        val = args[2]
        if val == "ban":
            arena.user_veto(args[1], banned=True)
        else:
            arena.user_veto(args[1], rank=int(val))

    elif sub == "rate":
        if len(args) < 3:
            print("用法: arena rate <model_id> <0-10>")
            return
        rating = float(args[2])
        arena.user_veto(args[1], user_rating=rating)
        print(f"❤️ 用户满意度评分: {args[1]} = {rating}/10")

    elif sub == "weights":
        if len(args) < 4:
            print("用法: arena weights <token> <speed> <quality>")
            return
        arena.set_weights(
            token_efficiency=float(args[1]),
            think_speed=float(args[2]),
            quality=float(args[3]),
        )
        print(f"⚖️ 权重已更新")

    else:
        print(f"未知子命令: {sub}")


def cmd_rank(args):
    display = DisplayV2()

    if not args:
        display.show_all()
        return

    sub = args[0]

    if sub in ("daily", "weekly", "monthly", "total", "all"):
        period = "all" if sub == "total" else sub
        display.show_ranking(period)
    elif sub == "detail":
        if len(args) < 2:
            print("用法: rank detail <model_id>")
            return
        display.show_model_detail(args[1])
    elif sub == "mood":
        display.show_mood_board()
    elif sub == "achievements":
        display.show_achievements_board()
    elif sub == "summary":
        display.show_ranking("all")
    elif sub == "export":
        period = args[1] if len(args) > 1 else "all"
        print(display.export_markdown(period))
    else:
        print(f"未知子命令: {sub}")


def cmd_quick(args):
    """快速切换并显示配置"""
    if not args:
        print("用法: quick <provider_id>")
        return

    switcher = APISwitcher()
    result = switcher.switch(args[0])
    if result.get("error"):
        print(f"❌ {result['error']}")
        return

    print(f"✅ 已切换到: {result['provider']} / {result['model']}")

    env_result = switcher.apply_to_claude_code()
    if "error" not in env_result:
        print(f"\n📋 环境变量:")
        print(env_result["shell_export"])


def cmd_status(args=None):
    """完整状态面板"""
    switcher = APISwitcher()
    arena = ArenaV2()
    display = DisplayV2(arena)

    # 当前配置
    config = switcher.get_active_config()
    print(f"\n{'═'*65}")
    print(f"  🏆 LLM Arena V2 状态面板")
    print(f"{'═'*65}")

    if "error" not in config:
        print(f"\n  📡 当前供应商: {config['provider_name']}")
        print(f"     模型: {config['model']}")
    else:
        print(f"\n  📡 未设置活跃供应商")

    # 竞技场排名
    display.show_ranking("all")
    display.show_mood_board()


def main():
    if len(sys.argv) < 2:
        print_help()
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "provider": cmd_provider,
        "arena": cmd_arena,
        "rank": cmd_rank,
        "quick": cmd_quick,
        "status": cmd_status,
        "help": lambda _: print_help(),
    }

    handler = commands.get(cmd)
    if handler:
        handler(args)
    else:
        print(f"未知命令: {cmd}")
        print_help()


if __name__ == "__main__":
    main()
