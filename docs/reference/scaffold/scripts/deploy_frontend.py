"""Build the frontend and publish it to Amplify Hosting via a manual (zip) deployment.

Flow: npm run build -> zip frontend/dist (index.html at zip root) -> CreateDeployment -> HTTP PUT the zip
to zipUploadUrl -> StartDeployment -> poll the job until SUCCEED/FAILED.
Requires scripts/bootstrap_amplify.py to have run once (.pact/amplify.json).
Usage: python scripts/deploy_frontend.py [--region us-east-1] [--skip-build]
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

import boto3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, ".pact", "amplify.json")


def upload(url: str, path: str, content_type: str | None) -> None:
    with open(path, "rb") as f:
        data = f.read()
    req = urllib.request.Request(url, data=data, method="PUT")
    if content_type:
        req.add_header("Content-Type", content_type)
    with urllib.request.urlopen(req, timeout=120) as resp:
        if resp.status not in (200, 201, 204):
            raise RuntimeError(f"upload failed: HTTP {resp.status}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--region", default=None)
    p.add_argument("--skip-build", action="store_true")
    a = p.parse_args()
    if not os.path.exists(STATE):
        print("missing .pact/amplify.json - run: python scripts/bootstrap_amplify.py", file=sys.stderr)
        return 1
    state = json.load(open(STATE, encoding="utf-8"))
    region = a.region or state["region"]
    frontend = os.path.join(ROOT, "frontend")
    if not a.skip_build:
        if not os.path.exists(os.path.join(frontend, ".env.production.local")):
            print("missing frontend/.env.production.local - run: make web-env", file=sys.stderr)
            return 1
        subprocess.run(["npm", "run", "build"], cwd=frontend, check=True)
    dist = os.path.join(frontend, "dist")
    if not os.path.exists(os.path.join(dist, "index.html")):
        print("frontend/dist/index.html not found - build failed?", file=sys.stderr)
        return 1

    tmp = tempfile.mkdtemp()
    zip_path = shutil.make_archive(os.path.join(tmp, "web"), "zip", root_dir=dist)  # index.html at zip root
    amp = boto3.client("amplify", region_name=region)
    dep = amp.create_deployment(appId=state["appId"], branchName=state["branch"])
    try:
        upload(dep["zipUploadUrl"], zip_path, "application/zip")
    except Exception as e:  # presigned URL may not include Content-Type in its signature
        print(f"upload with Content-Type failed ({e}); retrying without it")
        upload(dep["zipUploadUrl"], zip_path, None)
    amp.start_deployment(appId=state["appId"], branchName=state["branch"], jobId=dep["jobId"])
    print(f"deployment job {dep['jobId']} started")
    for _ in range(90):
        job = amp.get_job(appId=state["appId"], branchName=state["branch"], jobId=dep["jobId"])["job"]["summary"]
        status = job["status"]
        if status in ("SUCCEED", "FAILED", "CANCELLED"):
            print(f"job {dep['jobId']}: {status}")
            if status == "SUCCEED":
                print(f"live at {state['url']}")
                return 0
            return 1
        time.sleep(4)
    print("timed out waiting for Amplify job", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
