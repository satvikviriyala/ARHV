"""Print the Cedar decision table for the PACT policies (Build It demo, runs fully offline).

Usage: python scripts/cedar_demo.py   (uses backend/functions/authorizer/{authz.py,cedar/})
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.environ.get("AUTHZ_DIR", os.path.join(ROOT, "backend", "functions", "authorizer")))
import authz  # noqa: E402

CASES = [
    ("passed motion challenge", "motion", False, 0),
    ("same token replayed", "motion", True, 0),
    ("passed phone-tilt challenge (physical)", "physical", False, 0),
    ("verified account, 0 bookings today", "account", False, 0),
    ("verified account, 1 booking today", "account", False, 1),
    ("verified account, quota used (2)", "account", False, 2),
    ("unknown assurance", "none", False, 0),
]


def main() -> int:
    print(f"{'scenario':38} {'assurance':9} {'replay':6} {'today':5}  decision  policy")
    print("-" * 100)
    for label, assurance, replayed, today in CASES:
        out = authz.decide(
            sub="demo-visitor", assurance=assurance, action="BookTicket", token_replayed=replayed, bookings_today=today
        )
        pol = ", ".join(out["policies"]) or "(default deny)"
        print(f"{label:38} {assurance:9} {str(replayed):6} {today:<5}  {out['decision']:8}  {pol}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
