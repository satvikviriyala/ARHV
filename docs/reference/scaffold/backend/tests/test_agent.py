"""Offline test of the red-team plumbing with a fake Strands model (no AWS, no Ollama)."""

import secrets
from typing import Any

from pact_agent import models
from pact_agent.solver import parse_answer, solve_round
from pact_core import mdg, png
from strands.models.model import Model


class FakeModel(Model):
    def __init__(self, replies):
        self.replies, self.seen = list(replies), []

    def update_config(self, **kw): ...
    def get_config(self):
        return {}

    async def structured_output(self, *a, **kw):  # pragma: no cover
        raise NotImplementedError
        yield

    async def stream(self, messages, tool_specs=None, system_prompt=None, **kwargs: Any):
        self.seen.append(messages)
        text = self.replies.pop(0)
        yield {"messageStart": {"role": "assistant"}}
        yield {"contentBlockStart": {"start": {}}}
        yield {"contentBlockDelta": {"delta": {"text": text}}}
        yield {"contentBlockStop": {}}
        yield {"messageStop": {"stopReason": "end_turn"}}


def _round():
    ch = mdg.generate_challenge(secrets.token_bytes(32), rounds=1, frames=4)
    r = ch["public"]["rounds"][0]
    frames = mdg.decode_frames(r["frames"])
    return [png.render_frame_png(f) for f in frames], r["options"], ch["answers"][0]


def test_parse_answer_variants():
    opts = ["circle", "star", "heart"]
    assert parse_answer('{"answer": "Star", "confidence": 0.4, "rationale": "x"}', opts)[0] == "star"
    assert parse_answer('```json\n{"answer":"heart"}\n```', opts)[0] == "heart"
    assert parse_answer('I think {"answer": "banana"}', opts)[0] is None
    assert parse_answer("no json here", opts)[0] is None


def test_solve_round_sends_images_and_parses():
    pngs, options, _ = _round()
    fake = FakeModel([f'{{"answer": "{options[2]}", "confidence": 0.3, "rationale": "noise"}}'])
    att = solve_round(fake, pngs, options)
    assert att.valid and att.answer == options[2] and not att.repaired
    blocks = fake.seen[0][0]["content"]
    assert sum(1 for b in blocks if "image" in b) == len(pngs)
    assert all(b["image"]["source"]["bytes"][:4] == b"\x89PNG" for b in blocks if "image" in b)


def test_solve_round_repairs_once_then_gives_up_cleanly():
    pngs, options, _ = _round()
    att = solve_round(FakeModel(["I cannot tell.", f'{{"answer": "{options[0]}"}}']), pngs, options)
    assert att.valid and att.repaired and att.answer == options[0]
    att = solve_round(FakeModel(["nope", "still nope"]), pngs, options)
    assert not att.valid and att.answer is None


def test_alias_parsing():
    assert models.parse_aliases("a=x:1,b=y") == {"a": "x:1", "b": "y"}
    assert models.parse_aliases("") == {}
