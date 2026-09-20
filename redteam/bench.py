"""Run the Strands vision red team against the public challenge API."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend", "layers", "core"))
sys.path.insert(0, os.path.join(ROOT, "backend", "functions", "agent_worker"))

from pact_agent import models  # noqa: E402
from pact_agent.solver import solve_round  # noqa: E402
from pact_core import mdg, png, stats  # noqa: E402


def post(api: str, path: str, body: dict, headers: dict[str, str] | None = None) -> tuple[int, dict]:
    target = f"{api.rstrip('/')}{path}"
    if urlparse(target).scheme not in {"http", "https"}:
        raise ValueError("API URL must use http or https")
    req = urllib.request.Request(  # noqa: S310
        target,
        data=json.dumps(body).encode(),
        method="POST",
        headers={"content-type": "application/json", **(headers or {})},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:  # noqa: S310
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", required=True)
    parser.add_argument("--backend", choices=("bedrock", "ollama"), required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--frames", type=int, choices=(1, 4, 8), default=4)
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--ollama-host", default=None)
    parser.add_argument("--out", default=os.path.join(ROOT, "eval", "results"))
    parser.add_argument("--sleep", type=float, default=0.5)
    args = parser.parse_args()
    label = args.model if args.backend == "bedrock" else f"ollama-{args.model}".replace(":", "-")
    cohort = f"agent:{label}:k{args.frames}"
    model = models.build_model(args.backend, args.model, region=args.region, ollama_host=args.ollama_host)
    model_id = models.resolve(args.model)[1] if args.backend == "bedrock" else args.model
    os.makedirs(args.out, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output_path = os.path.join(args.out, f"{timestamp}_{label.replace(':', '-')}_k{args.frames}.jsonl")
    valid_results: list[dict] = []
    infra_errors = 0
    for attempt in range(args.n):
        status, challenge = post(args.api, "/v1/challenges", {}, {"x-pact-cohort": cohort})
        if status != 201:
            infra_errors += 1
            result = {
                "ts": datetime.now(UTC).isoformat(),
                "api": args.api,
                "backend": args.backend,
                "model": args.model,
                "modelId": model_id,
                "frames": args.frames,
                "challengeId": None,
                "answers": [],
                "passed": False,
                "roundsCorrect": 0,
                "valid": [],
                "repaired": [],
                "latencyMs": [],
                "errors": [f"challenge_http_{status}"],
            }
        else:
            answers: list[str] = []
            valids: list[bool] = []
            repaired: list[bool] = []
            latencies: list[int] = []
            errors: list[str | None] = []
            for round_data in challenge.get("rounds", []):
                frames = mdg.decode_frames(round_data["frames"])[: args.frames]
                rendered = [png.render_frame_png(frame, scale=3) for frame in frames]
                outcome = solve_round(model, rendered, round_data["options"])
                answers.append(outcome.answer or "")
                valids.append(outcome.valid)
                repaired.append(outcome.repaired)
                latencies.append(outcome.latency_ms)
                errors.append(outcome.error)
            answer_status, response = post(
                args.api,
                f"/v1/challenges/{challenge['challengeId']}/answers",
                {"answers": answers, "timingsMs": latencies},
            )
            if answer_status != 200 or any(errors):
                infra_errors += 1 if any(errors) or answer_status != 200 else 0
            result = {
                "ts": datetime.now(UTC).isoformat(),
                "api": args.api,
                "backend": args.backend,
                "model": args.model,
                "modelId": model_id,
                "frames": args.frames,
                "challengeId": challenge["challengeId"],
                "answers": answers,
                "passed": bool(response.get("passed")) if answer_status == 200 else False,
                "roundsCorrect": int(response.get("roundsCorrect", 0)) if answer_status == 200 else 0,
                "valid": valids,
                "repaired": repaired,
                "latencyMs": latencies,
                "errors": errors if answer_status == 200 else [f"answer_http_{answer_status}"],
            }
        with open(output_path, "a", encoding="utf-8") as output:
            output.write(json.dumps(result, separators=(",", ":")) + "\n")
        if not result["errors"] or all(error is None for error in result["errors"]):
            valid_results.append(result)
        print(
            f"attempt {attempt + 1}/{args.n}: {'infra-error' if result['errors'] and any(result['errors']) else 'recorded'}"
        )
        if args.sleep:
            time.sleep(args.sleep)

    attempts = len(valid_results)
    passes = sum(bool(item["passed"]) for item in valid_results)
    rounds = sum(len(item["valid"]) for item in valid_results)
    correct = sum(int(item["roundsCorrect"]) for item in valid_results)
    p, lo, hi = stats.wilson(passes, attempts)
    rp, rlo, rhi = stats.wilson(correct, rounds)
    latencies = [value for item in valid_results for value in item["latencyMs"]]
    invalid = sum(1 for item in valid_results for valid in item["valid"] if not valid)
    print(f"results: {attempts} valid attempts, {passes}/{attempts} pass ({p:.4f}, CI {lo:.4f}-{hi:.4f})")
    print(f"rounds: {correct}/{rounds} ({rp:.4f}, CI {rlo:.4f}-{rhi:.4f}); chance 0.1667; pass chance 0.0046")
    print(f"invalid: {invalid}/{rounds}; mean latency {sum(latencies) / len(latencies) if latencies else 0:.0f} ms")
    print(f"infra errors excluded: {infra_errors}; output: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
