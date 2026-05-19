"""
LLM Arena 自动评估器
自动评估模型回答质量，支持多种评估策略
"""

import re
from typing import Callable


class AutoEvaluator:
    """自动质量评估器"""

    @staticmethod
    def length_based(response: str) -> float:
        """基于长度的简单评估（适中长度得分高）"""
        length = len(response)
        if length < 10:
            return 2.0
        elif length < 50:
            return 5.0
        elif length < 500:
            return 8.0
        elif length < 2000:
            return 9.0
        else:
            return 7.0  # 太长扣分

    @staticmethod
    def completeness(response: str, expected_keywords: list = None) -> float:
        """基于完整性的评估"""
        score = 5.0
        if not response or not response.strip():
            return 0.0

        # 有结构化内容加分
        if re.search(r'```', response):
            score += 1.0
        if re.search(r'^\s*[-*]\s', response, re.MULTILINE):
            score += 0.5
        if re.search(r'^\s*\d+\.\s', response, re.MULTILINE):
            score += 0.5

        # 包含预期关键词加分
        if expected_keywords:
            found = sum(1 for kw in expected_keywords if kw.lower() in response.lower())
            score += (found / len(expected_keywords)) * 3.0

        return min(10.0, score)

    @staticmethod
    def error_check(response: str) -> float:
        """检查回答是否包含错误标志"""
        score = 10.0
        error_patterns = [
            r"I don't know",
            r"I'm not sure",
            r"I can't",
            r"sorry.*can't",
            r"error",
            r"failed",
        ]
        for pat in error_patterns:
            if re.search(pat, response, re.IGNORECASE):
                score -= 2.0
        return max(0.0, score)

    @staticmethod
    def composite(response: str, expected_keywords: list = None) -> float:
        """综合评估"""
        scores = [
            AutoEvaluator.length_based(response) * 0.3,
            AutoEvaluator.completeness(response, expected_keywords) * 0.4,
            AutoEvaluator.error_check(response) * 0.3,
        ]
        return round(sum(scores), 2)


def create_evaluator(strategy: str = "composite",
                     **kwargs) -> Callable[[str], float]:
    """创建评估函数"""
    if strategy == "length":
        return AutoEvaluator.length_based
    elif strategy == "completeness":
        return lambda r: AutoEvaluator.completeness(r, kwargs.get("keywords"))
    elif strategy == "error":
        return AutoEvaluator.error_check
    else:
        return lambda r: AutoEvaluator.composite(r, kwargs.get("keywords"))
