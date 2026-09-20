"""Wilson confidence intervals and cohort summaries."""

from __future__ import annotations

import math

CHANCE_ROUND = 1 / 6
CHANCE_PASS = CHANCE_ROUND**3


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    if n <= 0:
        return 0.0, 0.0, 0.0
    p = k / n
    denominator = 1 + z * z / n
    centre = p + z * z / (2 * n)
    spread = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)
    return p, max(0.0, (centre - spread) / denominator), min(1.0, (centre + spread) / denominator)


def _r(value: float) -> float:
    return round(value, 4)


def summarize(items: list[dict]) -> list[dict]:
    def order(item: dict) -> tuple[int, str]:
        cohort = str(item.get("cohort", "public"))
        fixed = {"study": 0, "public": 1, "local": 2}
        return fixed.get(cohort, 3), cohort

    result: list[dict] = []
    for item in sorted(items, key=order):
        attempts = int(item.get("attempts", 0))
        passes = int(item.get("passes", 0))
        round_total = int(item.get("roundsTotal", 0))
        round_correct = int(item.get("roundsCorrect", 0))
        duration = int(item.get("durationMsTotal", 0))
        pass_rate, pass_lo, pass_hi = wilson(passes, attempts)
        round_rate, round_lo, round_hi = wilson(round_correct, round_total)
        result.append(
            {
                "cohort": str(item.get("cohort", "public")),
                "attempts": attempts,
                "passes": passes,
                "passRate": _r(pass_rate),
                "passCi": [_r(pass_lo), _r(pass_hi)],
                "roundAccuracy": _r(round_rate),
                "roundCi": [_r(round_lo), _r(round_hi)],
                "meanMs": int(duration / attempts) if attempts else 0,
            }
        )
    return result
