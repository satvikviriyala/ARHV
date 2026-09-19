"""Solve one PACT round with a Strands Agent and parse the answer robustly."""

from __future__ import annotations

import json
import re
import time
from dataclasses import asdict, dataclass

from .prompts import SYSTEM_PROMPT, build_round_content, repair_prompt


@dataclass
class RoundAttempt:
    answer: str | None  # None => invalid / unparseable (scored as wrong)
    confidence: float | None
    rationale: str
    raw: str  # model's final text (truncated), kept for the trace
    valid: bool
    latency_ms: int
    repaired: bool = False
    error: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def parse_answer(text: str, options: list[str]) -> tuple[str | None, float | None, str]:
    """Accept the first JSON object whose "answer" is one of the options (case-insensitive)."""
    lookup = {o.lower(): o for o in options}
    for m in re.finditer(r"\{[^{}]*\}", text, re.S):
        try:
            obj = json.loads(m.group(0))
        except json.JSONDecodeError:
            continue
        ans = str(obj.get("answer", "")).strip().lower()
        if ans in lookup:
            conf = obj.get("confidence")
            conf = float(conf) if isinstance(conf, (int, float)) else None
            return lookup[ans], conf, str(obj.get("rationale", ""))[:300]
    return None, None, ""


def solve_round(model, pngs: list[bytes], options: list[str], *, frame_ms: int = 33) -> RoundAttempt:
    from strands import Agent  # imported lazily so the API Lambda never loads Strands

    agent = Agent(model=model, system_prompt=SYSTEM_PROMPT, callback_handler=None)  # fresh context per round
    t0 = time.perf_counter()
    try:
        text = str(agent(build_round_content(pngs, options, frame_ms)))
        answer, conf, why = parse_answer(text, options)
        repaired = False
        if answer is None:  # one self-repair attempt, same conversation
            text = str(agent(repair_prompt(options)))
            answer, conf, why = parse_answer(text, options)
            repaired = True
        return RoundAttempt(
            answer=answer,
            confidence=conf,
            rationale=why,
            raw=text[:600],
            valid=answer is not None,
            latency_ms=int((time.perf_counter() - t0) * 1000),
            repaired=repaired,
        )
    except Exception as e:  # model/network errors are recorded, never crash the run
        return RoundAttempt(
            answer=None,
            confidence=None,
            rationale="",
            raw="",
            valid=False,
            latency_ms=int((time.perf_counter() - t0) * 1000),
            error=f"{type(e).__name__}: {e}"[:300],
        )
