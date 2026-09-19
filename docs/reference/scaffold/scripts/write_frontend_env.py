"""Write frontend/.env.production.local (and .env.development.local) from the deployed stack outputs.

These values are public configuration (API URL, Cognito pool/client IDs), not secrets.
Usage: python scripts/write_frontend_env.py [--stack pact-dev] [--region us-east-1] [--local]
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stack_output import get_outputs  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def render(values: dict[str, str]) -> str:
    return "".join(f"{k}={v}\n" for k, v in values.items())


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--stack", default="pact-dev")
    p.add_argument("--region", default="us-east-1")
    p.add_argument("--local", action="store_true", help="point the dev server at sam local (http://127.0.0.1:3000)")
    a = p.parse_args()
    out = get_outputs(a.stack, a.region)
    values = {
        "VITE_API_URL": out["ApiUrl"].rstrip("/"),
        "VITE_REGION": out.get("Region", a.region),
        "VITE_USER_POOL_ID": out["UserPoolId"],
        "VITE_USER_POOL_CLIENT_ID": out["UserPoolClientId"],
        "VITE_STAGE": a.stack.removeprefix("pact-"),
    }
    frontend = os.path.join(ROOT, "frontend")
    with open(os.path.join(frontend, ".env.production.local"), "w", encoding="utf-8") as f:
        f.write(render(values))
    dev = dict(values)
    if a.local:
        dev["VITE_API_URL"] = "http://127.0.0.1:3000"
    with open(os.path.join(frontend, ".env.development.local"), "w", encoding="utf-8") as f:
        f.write(render(dev))
    print("wrote frontend/.env.production.local and frontend/.env.development.local")
    for k, v in values.items():
        print(f"  {k}={v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
