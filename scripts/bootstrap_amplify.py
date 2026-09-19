"""One-time: create the Amplify Hosting app + 'main' branch for MANUAL (zip) deployments.

Prints the public URL and patches backend/samconfig.toml so CORS allows that origin.
Idempotent: re-running finds the existing app by name. State is kept in .pact/amplify.json (gitignored).
Usage: python scripts/bootstrap_amplify.py [--name pact-web] [--region us-east-1]
"""

import argparse
import json
import os
import re
import sys

import boto3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, ".pact", "amplify.json")
SPA_REWRITE = [
    {
        # Serve index.html for client-side routes; keep real files (js/css/png/...) untouched.
        "source": "</^[^.]+$|\\.(?!(css|gif|ico|jpg|jpeg|js|png|txt|svg|woff|woff2|ttf|map|json|webp|webmanifest)$)([^.]+$)/>",
        "target": "/index.html",
        "status": "200",
    }
]


def patch_allowed_origins(cfg: str, origins: str) -> str | None:
    """Set AllowedOrigins inside the parameter_overrides line, keeping every other parameter (e.g. AgentModels)."""
    m = re.search(r"^parameter_overrides\s*=\s*\"(.*)\"\s*$", cfg, flags=re.M)
    if not m:
        return None
    body = m.group(1)
    item = f'AllowedOrigins=\\"{origins}\\"'
    if re.search(r'AllowedOrigins=\\"[^"\\]*\\"', body):
        body = re.sub(r'AllowedOrigins=\\"[^"\\]*\\"', lambda _m: item, body)
    else:
        body = f"{body} {item}".strip()
    return cfg[: m.start()] + f'parameter_overrides = "{body}"' + cfg[m.end() :]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--name", default="pact-web")
    p.add_argument("--branch", default="main")
    p.add_argument("--region", default="us-east-1")
    a = p.parse_args()
    amp = boto3.client("amplify", region_name=a.region)

    app = next((x for x in amp.list_apps(maxResults=100)["apps"] if x["name"] == a.name), None)
    if app is None:
        app = amp.create_app(name=a.name, platform="WEB", customRules=SPA_REWRITE)["app"]
        print(f"created Amplify app {app['appId']}")
    else:
        amp.update_app(appId=app["appId"], customRules=SPA_REWRITE)
        print(f"found Amplify app {app['appId']}")
    branches = [b["branchName"] for b in amp.list_branches(appId=app["appId"])["branches"]]
    if a.branch not in branches:
        amp.create_branch(appId=app["appId"], branchName=a.branch, stage="PRODUCTION")
        print(f"created branch {a.branch}")

    url = f"https://{a.branch}.{app['defaultDomain']}"
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump({"appId": app["appId"], "branch": a.branch, "url": url, "region": a.region}, f, indent=2)

    cfg_path = os.path.join(ROOT, "backend", "samconfig.toml")
    with open(cfg_path, encoding="utf-8") as f:
        cfg = f.read()
    patched = patch_allowed_origins(cfg, f"http://localhost:5173,{url}")
    if patched is None:
        print(
            "WARNING: no parameter_overrides line in backend/samconfig.toml; set AllowedOrigins manually",
            file=sys.stderr,
        )
    else:
        with open(cfg_path, "w", encoding="utf-8") as f:
            f.write(patched)
        print(f"patched backend/samconfig.toml AllowedOrigins -> http://localhost:5173,{url} (run `make deploy`)")
    print(f"Amplify URL: {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
