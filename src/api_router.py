"""
LLM Arena API Router
根据竞技场排名自动路由 API 调用到最优模型
"""

import json
import time
import importlib
from pathlib import Path
from arena import LLMArena


class ArenaRouter:
    """基于竞技场排名的智能 API 路由器"""

    def __init__(self, arena: LLMArena = None):
        self.arena = arena or LLMArena()
        self._provider_cache = {}

    def get_best_model(self, fallback: str = None) -> str:
        """获取当前排名最高的模型 ID"""
        top = self.arena.get_top_model()
        if top:
            return top
        return fallback

    def get_routing_table(self) -> dict:
        """获取完整路由表（模型ID -> 优先级权重）"""
        priority_list = self.arena.get_priority_list()
        if not priority_list:
            return {}
        n = len(priority_list)
        table = {}
        for i, mid in enumerate(priority_list):
            # 优先级权重：排名越前权重越高
            table[mid] = round((n - i) / n, 3)
        return table

    def call(self, prompt: str, model_id: str = None, **kwargs) -> dict:
        """
        智能调用：自动选择最优模型或指定模型
        返回: {"model_id": str, "response": str, "tokens": int, "think_time": float}
        """
        if model_id is None:
            model_id = self.get_best_model()
            if model_id is None:
                raise ValueError("竞技场中没有可用模型，请先注册")

        start = time.time()

        # 这里是实际调用的接口点
        # 用户需要在此接入自己的 API 调用逻辑
        result = self._dispatch_call(model_id, prompt, **kwargs)

        elapsed = time.time() - start

        return {
            "model_id": model_id,
            "response": result.get("response", ""),
            "tokens": result.get("tokens", 0),
            "think_time": elapsed,
        }

    def call_and_score(self, prompt: str, quality: float,
                       model_id: str = None, **kwargs) -> dict:
        """调用并自动记录评分"""
        result = self.call(prompt, model_id, **kwargs)
        self.arena.record_match(
            model_id=result["model_id"],
            tokens=result["tokens"],
            think_time=result["think_time"],
            quality=quality,
        )
        return result

    def _dispatch_call(self, model_id: str, prompt: str, **kwargs) -> dict:
        """
        实际的 API 调用分发
        用户可覆盖此方法接入自己的 provider
        """
        # 默认实现：返回模板，用户需替换为实际调用
        return {
            "response": f"[请在 _dispatch_call 中接入 {model_id} 的实际 API]",
            "tokens": 0,
        }


class ArenaMiddleware:
    """
    中间件模式：包装现有的 API 调用，自动收集指标
    用法：
        middleware = ArenaMiddleware(your_api_call_func)
        result = middleware.call("hello", model="gpt-4")
    """

    def __init__(self, call_fn, arena: LLMArena = None):
        self.call_fn = call_fn
        self.arena = arena or LLMArena()

    def call(self, prompt: str, model: str, auto_score: bool = True,
             quality_fn=None, **kwargs) -> dict:
        """
        包装调用，自动记录 token 和时间
        quality_fn: 可选的质量评估函数 (response_str) -> float(0-10)
        """
        start = time.time()
        result = self.call_fn(prompt, model=model, **kwargs)
        elapsed = time.time() - start

        tokens = result.get("usage", {}).get("total_tokens", 0)
        response_text = result.get("content", result.get("response", ""))

        quality = 0.0
        if quality_fn:
            quality = quality_fn(response_text)

        if auto_score and quality > 0:
            self.arena.record_match(model, tokens, elapsed, quality)

        return {
            "model_id": model,
            "response": response_text,
            "tokens": tokens,
            "think_time": elapsed,
            "quality": quality,
            "raw": result,
        }
