"""Make the Lambda code importable in tests exactly as Lambda sees it.

- pact_core comes from the layer dir (Lambda: /opt/python/pact_core)
- authz / pact_agent come from their function dirs
Handlers are all called app.py, so load them by path with load_handler("api") instead of `import app`.
"""

import importlib.util
import os
import sys

import boto3
import pytest
from moto import mock_aws

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for rel in ("layers/core", "functions/authorizer", "functions/agent_worker"):
    path = os.path.join(BACKEND, rel)
    if path not in sys.path:
        sys.path.insert(0, path)

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")  # moto / never real creds in tests
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")


def load_handler(function_dir: str, module: str = "app"):
    """Import backend/functions/<function_dir>/<module>.py under a unique module name."""
    path = os.path.join(BACKEND, "functions", function_dir, f"{module}.py")
    spec = importlib.util.spec_from_file_location(f"{function_dir}_{module}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def ddb_table(monkeypatch):
    """Moto table matching the deployed single-table key schema."""
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("TABLE_NAME", "pact-test")
    monkeypatch.setenv("PACT_TOKEN_SECRET", "local-test-secret-" + "x" * 48)
    monkeypatch.setenv("STAGE", "test")
    monkeypatch.delenv("PACT_LOCAL_DEV", raising=False)
    from pact_core import store

    store._table.cache_clear()
    with mock_aws():
        table = boto3.resource("dynamodb", region_name="us-east-1").create_table(
            TableName="pact-test",
            BillingMode="PAY_PER_REQUEST",
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}, {"AttributeName": "SK", "KeyType": "RANGE"}],
        )
        yield table
    store._table.cache_clear()
