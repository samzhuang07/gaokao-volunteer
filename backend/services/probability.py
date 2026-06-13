import math


class ProbabilityCalculator:
    """Calculate admission probability based on rank comparison with historical data."""

    def calculate_all(self, matches: list, user_rank: int) -> list:
        results = []
        for m in matches:
            results.append(self._calculate_single(m, user_rank))
        return results

    def _calculate_single(self, match: dict, user_rank: int) -> dict:
        avg_rank = match.get("avg_rank", 0)

        if not avg_rank or avg_rank <= 0:
            match["category"] = "unknown"
            match["probability"] = 0
            match["label"] = "数据不足"
            return match

        ratio = user_rank / avg_rank

        # Sigmoid-based probability: smooth transition across rank ratios
        # k controls steepness: steeper = sharper transition
        k = 3.5
        # Clamp exponent to prevent overflow for extreme ratios
        exp_arg = max(-50, min(50, -k * (1 - ratio)))
        prob = round(100 / (1 + math.exp(exp_arg)))

        # Category based on wider thresholds
        if ratio >= 1.10:
            category = "reach"
            label = "冲刺"
        elif ratio <= 0.88:
            category = "safety"
            label = "保底"
        else:
            category = "match"
            label = "稳妥"

        prob = max(1, min(99, prob))

        match["category"] = category
        match["probability"] = prob
        match["label"] = label
        match["rank_ratio"] = round(ratio, 3)
        return match
