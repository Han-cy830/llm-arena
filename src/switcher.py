"""
LLM Arena API Switcher
灵活切换供应商和模型，管理 API 配置
"""

import json
import os
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
PROVIDERS_FILE = DATA_DIR / "providers.json"


def _load_providers() -> dict:
    if PROVIDERS_FILE.exists():
        with open(PROVIDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"providers": {}, "active_provider": None, "active_model": None, "switch_history": []}


def _save_providers(data: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROVIDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class APISwitcher:
    """API 供应商切换器"""

    def __init__(self):
        self.data = _load_providers()
        self.providers = self.data.get("providers", {})
        self.active_provider = self.data.get("active_provider")
        self.active_model = self.data.get("active_model")

    def list_providers(self) -> list:
        """列出所有可用供应商"""
        result = []
        for pid, p in self.providers.items():
            has_key = self._check_env_key(p)
            result.append({
                "id": pid,
                "name": p["display_name"],
                "active": pid == self.active_provider,
                "has_key": has_key,
                "models": p.get("models", []),
                "default_model": p.get("default_model", ""),
            })
        return result

    def switch(self, provider_id: str, model_id: str = None) -> dict:
        """切换到指定供应商和模型"""
        if provider_id not in self.providers:
            return {"error": f"供应商 '{provider_id}' 不存在"}

        provider = self.providers[provider_id]

        if model_id and model_id not in provider.get("models", []):
            return {"error": f"模型 '{model_id}' 不在 {provider['display_name']} 的支持列表中"}

        old_provider = self.active_provider
        old_model = self.active_model

        self.active_provider = provider_id
        self.active_model = model_id or provider.get("default_model", "")

        # 记录切换历史
        self.data.setdefault("switch_history", []).append({
            "timestamp": datetime.now().isoformat(),
            "from": {"provider": old_provider, "model": old_model},
            "to": {"provider": provider_id, "model": self.active_model},
        })

        self.data["active_provider"] = self.active_provider
        self.data["active_model"] = self.active_model
        _save_providers(self.data)

        return {
            "success": True,
            "provider": provider["display_name"],
            "model": self.active_model,
            "base_url": provider["base_url"],
        }

    def get_active_config(self) -> dict:
        """获取当前活跃配置"""
        if not self.active_provider or self.active_provider not in self.providers:
            return {"error": "未设置活跃供应商"}

        p = self.providers[self.active_provider]
        return {
            "provider_id": self.active_provider,
            "provider_name": p["display_name"],
            "model": self.active_model or p.get("default_model", ""),
            "base_url": p["base_url"],
            "api_type": p["api_type"],
            "env_key": p["env_key"],
            "max_tokens": p.get("max_tokens", 4096),
            "supports_streaming": p.get("supports_streaming", False),
            "supports_thinking": p.get("supports_thinking", False),
        }

    def get_provider_info(self, provider_id: str) -> dict:
        """获取供应商详情"""
        if provider_id not in self.providers:
            return {"error": f"供应商 '{provider_id}' 不存在"}
        p = self.providers[provider_id]
        return {
            "id": provider_id,
            "name": p["display_name"],
            "base_url": p["base_url"],
            "models": p.get("models", []),
            "default_model": p.get("default_model", ""),
            "api_type": p["api_type"],
            "env_key": p["env_key"],
            "has_key": self._check_env_key(p),
            "max_tokens": p.get("max_tokens", 4096),
        }

    def add_provider(self, provider_id: str, config: dict) -> dict:
        """添加自定义供应商"""
        required = ["display_name", "base_url", "default_model", "api_type", "env_key"]
        for field in required:
            if field not in config:
                return {"error": f"缺少必填字段: {field}"}

        self.providers[provider_id] = config
        self.data["providers"] = self.providers
        _save_providers(self.data)
        return {"success": True, "provider": config["display_name"]}

    def remove_provider(self, provider_id: str) -> dict:
        """移除供应商"""
        if provider_id not in self.providers:
            return {"error": f"供应商 '{provider_id}' 不存在"}
        name = self.providers[provider_id]["display_name"]
        del self.providers[provider_id]
        self.data["providers"] = self.providers
        if self.active_provider == provider_id:
            self.active_provider = None
            self.active_model = None
            self.data["active_provider"] = None
            self.data["active_model"] = None
        _save_providers(self.data)
        return {"success": True, "removed": name}

    def _check_env_key(self, provider: dict) -> bool:
        """检查环境变量中是否有对应的 API Key"""
        env_key = provider.get("env_key", "")
        return bool(os.environ.get(env_key))

    def get_switch_history(self, limit: int = 20) -> list:
        """获取切换历史"""
        history = self.data.get("switch_history", [])
        return history[-limit:]

    def apply_to_claude_code(self) -> dict:
        """
        生成 Claude Code 环境变量配置
        用户可以将输出添加到 .claude/settings.json 或 shell profile
        """
        config = self.get_active_config()
        if "error" in config:
            return config

        env_vars = {}
        api_type = config["api_type"]

        if api_type == "anthropic":
            env_vars["ANTHROPIC_BASE_URL"] = config["base_url"]
            env_vars["ANTHROPIC_API_KEY"] = f"${{{config['env_key']}}}"
        elif api_type == "openai":
            env_vars["OPENAI_BASE_URL"] = config["base_url"]
            env_vars["OPENAI_API_KEY"] = f"${{{config['env_key']}}}"
        elif api_type == "google":
            env_vars["GOOGLE_API_KEY"] = f"${{{config['env_key']}}}"
        elif api_type == "bedrock":
            env_vars["AWS_ACCESS_KEY_ID"] = f"${{{config['env_key']}}}"
        elif api_type == "bedrock-apikey":
            env_vars["AWS_BEARER_TOKEN_BEDROCK"] = f"${{{config['env_key']}}}"

        return {
            "provider": config["provider_name"],
            "model": config["model"],
            "env_vars": env_vars,
            "shell_export": self._generate_shell_export(env_vars),
        }

    def _generate_shell_export(self, env_vars: dict) -> str:
        """生成 shell export 命令"""
        lines = []
        for k, v in env_vars.items():
            lines.append(f"export {k}=\"{v}\"")
        return "\n".join(lines)


# CLI 入口
def main():
    import sys

    switcher = APISwitcher()

    if len(sys.argv) < 2:
        print("用法: python switcher.py <command> [args]")
        print("命令:")
        print("  list                          列出所有供应商")
        print("  switch <provider> [model]     切换供应商/模型")
        print("  active                        查看当前配置")
        print("  info <provider>               供应商详情")
        print("  history [limit]               切换历史")
        print("  env                           生成环境变量配置")
        print("  add <id> <json_file>          添加自定义供应商")
        print("  remove <id>                   移除供应商")
        return

    cmd = sys.argv[1]

    if cmd == "list":
        providers = switcher.list_providers()
        print(f"\n{'='*70}")
        print(f"  可用供应商 ({len(providers)} 个)")
        print(f"{'='*70}")
        for p in providers:
            active_mark = " ✅" if p["active"] else ""
            key_mark = "🔑" if p["has_key"] else "❌"
            print(f"  {key_mark} {p['id']:25s} {p['name']:25s}{active_mark}")
            if p["active"]:
                print(f"     └─ 当前模型: {p['active'] if isinstance(p.get('active'), str) else p['default_model']}")
        print()

    elif cmd == "switch":
        pid = sys.argv[2]
        model = sys.argv[3] if len(sys.argv) > 3 else None
        result = switcher.switch(pid, model)
        if result.get("error"):
            print(f"❌ {result['error']}")
        else:
            print(f"✅ 已切换到: {result['provider']} / {result['model']}")
            print(f"   Base URL: {result['base_url']}")

    elif cmd == "active":
        config = switcher.get_active_config()
        if "error" in config:
            print(f"❌ {config['error']}")
        else:
            print(f"\n当前活跃配置:")
            print(f"  供应商: {config['provider_name']}")
            print(f"  模型:   {config['model']}")
            print(f"  URL:    {config['base_url']}")
            print(f"  类型:   {config['api_type']}")
            print(f"  Key:    {'✅ 已配置' if os.environ.get(config['env_key']) else '❌ 未配置'}")

    elif cmd == "info":
        info = switcher.get_provider_info(sys.argv[2])
        if "error" in info:
            print(f"❌ {info['error']}")
        else:
            print(f"\n{info['name']} ({info['id']})")
            print(f"  URL:     {info['base_url']}")
            print(f"  类型:    {info['api_type']}")
            print(f"  Key环境: {info['env_key']}")
            print(f"  Key状态: {'✅' if info['has_key'] else '❌'}")
            print(f"  模型:")
            for m in info["models"]:
                default = " (默认)" if m == info["default_model"] else ""
                print(f"    - {m}{default}")

    elif cmd == "history":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        history = switcher.get_switch_history(limit)
        if not history:
            print("暂无切换历史")
        else:
            print(f"\n最近 {len(history)} 次切换:")
            for h in history:
                ts = h["timestamp"][:19]
                frm = f"{h['from']['provider']}/{h['from']['model']}"
                to = f"{h['to']['provider']}/{h['to']['model']}"
                print(f"  {ts}  {frm} → {to}")

    elif cmd == "env":
        result = switcher.apply_to_claude_code()
        if "error" in result:
            print(f"❌ {result['error']}")
        else:
            print(f"\n📋 环境变量配置 ({result['provider']}):")
            print(f"\n{result['shell_export']}")
            print(f"\n💡 将上述命令添加到 ~/.bashrc 或 ~/.zshrc")

    elif cmd == "add":
        pid = sys.argv[2]
        with open(sys.argv[3], "r", encoding="utf-8") as f:
            config = json.load(f)
        result = switcher.add_provider(pid, config)
        if result.get("error"):
            print(f"❌ {result['error']}")
        else:
            print(f"✅ 已添加: {result['provider']}")

    elif cmd == "remove":
        result = switcher.remove_provider(sys.argv[2])
        if result.get("error"):
            print(f"❌ {result['error']}")
        else:
            print(f"✅ 已移除: {result['removed']}")

    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()
