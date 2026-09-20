"""Token-signing-key lookup.

Cloud Lambdas read the generated Secrets Manager value. Local development and tests
must explicitly provide ``PACT_TOKEN_SECRET``; no cloud secret is copied into the repo.
"""

from __future__ import annotations

import os
from functools import lru_cache

import boto3


@lru_cache(maxsize=1)
def token_secret() -> str:
    local = os.environ.get("PACT_TOKEN_SECRET")
    if local:
        return local
    client = boto3.client("secretsmanager", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    response = client.get_secret_value(SecretId=os.environ["TOKEN_SECRET_ARN"])
    return str(response["SecretString"])
