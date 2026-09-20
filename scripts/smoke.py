"""Small end-to-end smoke test for the deployed or local API.

The script deliberately never prints challenge answers or humanity tokens.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

import boto3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "backend", "layers", "core"))
from redteam import imu_sim  # noqa: E402


def request(
    api: str, method: str, path: str, body: dict | None = None, headers: dict[str, str] | None = None
) -> tuple[int, dict]:
    payload = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        f"{api.rstrip('/')}{path}",
        data=payload,
        method=method,
        headers={"content-type": "application/json", **(headers or {})},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def table_for(args: argparse.Namespace):
    endpoint = None
    if args.local:
        endpoint = "http://127.0.0.1:4566" if args.profile == "localstack" else "http://127.0.0.1:8000"
    cfn = boto3.client("cloudformation", region_name=args.region)
    if args.local:
        table_name = "pact-local"
    else:
        outputs = {
            item["OutputKey"]: item["OutputValue"]
            for item in cfn.describe_stacks(StackName=args.stack)["Stacks"][0].get("Outputs", [])
        }
        table_name = outputs["TableName"]
    return boto3.resource("dynamodb", region_name=args.region, endpoint_url=endpoint).Table(table_name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", required=True)
    parser.add_argument("--stack", default="pact-dev")
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--local", action="store_true")
    parser.add_argument("--profile", choices=("ddb", "localstack"), default="ddb")
    parser.add_argument("--no-agent", action="store_true")
    args = parser.parse_args()
    failures = 0

    def check(label: str, passed: bool) -> None:
        nonlocal failures
        print(f"{label}: {'OK' if passed else 'FAIL'}")
        failures += not passed

    status, health = request(args.api, "GET", "/v1/health")
    check("health", status == 200 and health.get("ok") is True)
    status, public = request(
        args.api, "POST", "/v1/challenges", {}, {"x-pact-cohort": "local" if args.local else "public"}
    )
    check(
        "mdg create",
        status == 201
        and len(public.get("rounds", [])) == 3
        and all(key not in public for key in ("answers", "specs", "seed")),
    )
    status, wrong = request(
        args.api,
        "POST",
        f"/v1/challenges/{public.get('challengeId', 'bad')}/answers",
        {"answers": ["not-a-shape"] * 3},
    )
    check("mdg wrong answers", status == 200 and wrong.get("passed") is False)

    status, challenge = request(args.api, "POST", "/v1/challenges", {})
    table = table_for(args)
    record = table.get_item(Key={"PK": f"CH#{challenge['challengeId']}", "SK": "META"})["Item"]
    status, passed = request(
        args.api,
        "POST",
        f"/v1/challenges/{challenge['challengeId']}/answers",
        {"answers": record["answers"], "timingsMs": [100, 100, 100]},
    )
    token = passed.get("token", "")
    check("mdg pass", status == 200 and passed.get("passed") is True and bool(token))
    status, _ = request(args.api, "POST", "/v1/demo/bookings")
    check("booking without header", status == 401)
    status, _ = request(args.api, "POST", "/v1/demo/bookings", headers={"x-pact-token": "garbage"})
    check("booking garbage token", status == 403)
    status, booking = request(args.api, "POST", "/v1/demo/bookings", headers={"x-pact-token": token})
    check("mdg booking", status == 201 and booking.get("policy") == "permit-motion-book")
    status, _ = request(args.api, "POST", "/v1/demo/bookings", headers={"x-pact-token": token})
    check("mdg replay", status == 403)
    status, explain = request(args.api, "POST", "/v1/authz/explain", {"token": token})
    check(
        "mdg replay explain",
        status == 200 and explain.get("decision") == "DENY" and "forbid-token-replay" in explain.get("policies", []),
    )
    status, stats = request(args.api, "GET", "/v1/stats")
    check("mdg stats", status == 200 and stats.get("cohorts"))

    status, imu_challenge = request(args.api, "POST", "/v1/challenges", {"family": "imu-v1"})
    trace = imu_sim.physical_trace(imu_challenge, imu_challenge["challengeId"])
    status, physical = request(
        args.api,
        "POST",
        f"/v1/challenges/{imu_challenge['challengeId']}/answers",
        {"trace": trace},
    )
    physical_token = physical.get("token", "")
    check("imu pass", status == 200 and physical.get("passed") is True and bool(physical_token))
    status, booking = request(args.api, "POST", "/v1/demo/bookings", headers={"x-pact-token": physical_token})
    check("imu booking", status == 201 and booking.get("policy") == "permit-physical-book")
    status, _ = request(args.api, "POST", "/v1/demo/bookings", headers={"x-pact-token": physical_token})
    check("imu replay", status == 403)
    status, explain = request(args.api, "POST", "/v1/authz/explain", {"token": physical_token})
    check("imu replay explain", status == 200 and explain.get("decision") == "DENY")

    status, fresh = request(args.api, "POST", "/v1/challenges", {"family": "imu-v1"})
    spoof = imu_sim.orientation_only_spoof(imu_sim.physical_trace(fresh, fresh["challengeId"]))
    status, result = request(
        args.api,
        "POST",
        f"/v1/challenges/{fresh['challengeId']}/answers",
        {"trace": spoof},
    )
    check(
        "imu orientation spoof", status == 200 and not result.get("passed") and "gravity" in result.get("reasons", [])
    )

    if not args.no_agent:
        status, _ = request(args.api, "POST", "/v1/agent-runs", {"frames": 1})
        check("agent route", status in {202, 501})
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
