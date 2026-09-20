"""Compile recorded red-team JSONL files and optional API statistics."""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import urllib.request
from collections import defaultdict
from datetime import UTC, datetime
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "backend", "layers", "core"))
from pact_core import stats  # noqa: E402


def get_stats(api: str) -> dict | None:
    if not api:
        return None
    target = f"{api.rstrip('/')}/v1/stats"
    if urlparse(target).scheme not in {"http", "https"}:
        return None
    try:
        with urllib.request.urlopen(target, timeout=10) as response:  # noqa: S310
            return json.loads(response.read())
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="")
    parser.add_argument("--results", default=os.path.join(ROOT, "eval", "results"))
    parser.add_argument("--out", default=os.path.join(ROOT, "eval", "report.md"))
    args = parser.parse_args()
    groups: dict[tuple[str, str, int], list[dict]] = defaultdict(list)
    files = sorted(glob.glob(os.path.join(args.results, "*.jsonl")))
    for path in files:
        with open(path, encoding="utf-8") as source:
            for line in source:
                if not line.strip():
                    continue
                item = json.loads(line)
                groups[(item["backend"], item["model"], int(item["frames"]))].append(item)

    lines = [
        "# ARHV evaluation report",
        "",
        f"Generated: {datetime.now(UTC).isoformat()}",
        "",
        "This report is generated only from recorded JSONL runs. Attempts containing infrastructure errors are excluded from pass and round aggregates.",
        "",
        "## Red-team results",
        "",
        "| Backend | Model | K | Valid N | Passes | Pass rate (95% CI) | Rounds | Round accuracy (95% CI) | Invalid rounds | Mean latency |",
        "|---|---|---:|---:|---:|---|---:|---|---:|---:|",
    ]
    for (backend, model, frames), records in sorted(groups.items()):
        valid = [record for record in records if not any(error for error in record.get("errors", []))]
        attempts = len(valid)
        passes = sum(bool(record.get("passed")) for record in valid)
        rounds = sum(len(record.get("valid", [])) for record in valid)
        correct = sum(int(record.get("roundsCorrect", 0)) for record in valid)
        invalid = sum(1 for record in valid for value in record.get("valid", []) if not value)
        latencies = [value for record in valid for value in record.get("latencyMs", [])]
        p, lo, hi = stats.wilson(passes, attempts)
        rp, rlo, rhi = stats.wilson(correct, rounds)
        lines.append(
            f"| {backend} | {model} | {frames} | {attempts} | {passes} | "
            f"{p:.4f} [{lo:.4f}, {hi:.4f}] | {rounds} | {rp:.4f} [{rlo:.4f}, {rhi:.4f}] | "
            f"{invalid} | {sum(latencies) / len(latencies) if latencies else 0:.0f} ms |"
        )
    if not groups:
        lines.append("| — | No recorded runs | — | 0 | 0 | — | 0 | — | 0 | — |")
    lines.extend(
        [
            "",
            "Chance lines: round accuracy = 1/6 = 0.1667; full-puzzle pass chance = 1/216 = 0.0046.",
            "",
            "## API statistics",
            "",
        ]
    )
    api_stats = get_stats(args.api)
    if api_stats:
        lines.append(f"Family: `{api_stats.get('family', 'unknown')}`")
        lines.append("")
        lines.append("| Cohort | Attempts | Passes | Pass rate | 95% CI | Round accuracy |")
        lines.append("|---|---:|---:|---:|---|---:|")
        for cohort in api_stats.get("cohorts", []):
            lines.append(
                f"| {cohort['cohort']} | {cohort['attempts']} | {cohort['passes']} | "
                f"{cohort['passRate']:.4f} | [{cohort['passCi'][0]:.4f}, {cohort['passCi'][1]:.4f}] | "
                f"{cohort['roundAccuracy']:.4f} |"
            )
    else:
        lines.append("No API statistics were available. The deployed stack was not reachable during this run.")
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- Small samples and self-declared cohorts are directional evidence, not a population study.",
            "- Browser IMU streams are unattested; the physics-consistent simulator is expected to pass.",
            "- A purpose-built optical-flow solver is outside this general-purpose agent benchmark.",
            "",
            "## Reproduce",
            "",
            "```bash",
            "make bench BACKEND=bedrock MODEL=nova-2-lite K=4 N=10",
            "make report",
            "```",
        ]
    )
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as output:
        output.write("\n".join(lines) + "\n")
    print(f"wrote {args.out} from {len(files)} result files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
