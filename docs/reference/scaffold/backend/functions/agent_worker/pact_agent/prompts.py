"""Prompt for the red-team agent. Deliberately generous (Kerckhoffs): the attacker is told exactly how
the puzzle works and gets consecutive frames 33 ms apart - more than a real browser agent would capture."""

from __future__ import annotations

SYSTEM_PROMPT = (
    "You are a careful, capable vision agent attempting a human-verification puzzle. "
    "Answer as accurately as you can. Reply with ONLY a JSON object, no prose, no code fences."
)


def round_instructions(options: list[str], n_frames: int, frame_ms: int = 33) -> str:
    return (
        "This is one round of a CAPTCHA called PACT. The canvas shows ~600 small white dots on black. "
        "A shape is hidden in the dots: every dot inside the shape drifts together in one direction, while dots "
        "outside drift in a clearly different direction; about 15% of dots are re-drawn at random each frame. "
        "Any single frame looks like uniform noise - the shape is only visible through motion between frames. "
        f"You are given {n_frames} consecutive frame(s), {frame_ms} ms apart (dots move ~1 canvas px per frame; "
        "frames are rendered at 3x scale). "
        f"Which shape is hidden? Options: {', '.join(options)}.\n"
        'Reply with ONLY: {"answer": "<exactly one option>", "confidence": <number 0..1>, '
        '"rationale": "<at most 25 words>"}'
    )


def build_round_content(pngs: list[bytes], options: list[str], frame_ms: int = 33) -> list[dict]:
    """Strands/Bedrock Converse content blocks: instructions, then labelled frames (raw PNG bytes)."""
    content: list[dict] = [{"text": round_instructions(options, len(pngs), frame_ms)}]
    for i, png in enumerate(pngs):
        content.append({"text": f"Frame {i + 1} of {len(pngs)} (t = {i * frame_ms} ms):"})
        content.append({"image": {"format": "png", "source": {"bytes": png}}})
    return content


def repair_prompt(options: list[str]) -> str:
    return (
        "Your previous reply was not valid. Reply with ONLY this JSON and nothing else: "
        f'{{"answer": "<one of: {", ".join(options)}>", "confidence": <0..1>, "rationale": "<short>"}}'
    )
