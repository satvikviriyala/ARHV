"""Create the PACT DynamoDB table in a local emulator (DynamoDB Local or LocalStack). Idempotent.

Usage: python scripts/local_bootstrap.py [--profile ddb|localstack] [--table pact-local]
"""

import argparse
import sys
import time

import boto3
from botocore.exceptions import ClientError

ENDPOINTS = {"ddb": "http://127.0.0.1:8000", "localstack": "http://127.0.0.1:4566"}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--profile", choices=sorted(ENDPOINTS), default="ddb")
    p.add_argument("--table", default="pact-local")
    a = p.parse_args()
    ddb = boto3.client(
        "dynamodb",
        region_name="us-east-1",
        endpoint_url=ENDPOINTS[a.profile],
        aws_access_key_id="test",
        aws_secret_access_key="test",  # noqa: S106 - dummy creds for local emulators
    )
    for _ in range(30):  # emulator may still be starting
        try:
            ddb.list_tables()
            break
        except Exception:
            time.sleep(1)
    else:
        print(f"no DynamoDB emulator at {ENDPOINTS[a.profile]} - did you run `make local-up`?", file=sys.stderr)
        return 1
    try:
        ddb.create_table(
            TableName=a.table,
            BillingMode="PAY_PER_REQUEST",
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            KeySchema=[{"AttributeName": "PK", "KeyType": "HASH"}, {"AttributeName": "SK", "KeyType": "RANGE"}],
        )
        ddb.get_waiter("table_exists").wait(TableName=a.table)
        print(f"created table {a.table} at {ENDPOINTS[a.profile]}")
    except ClientError as e:
        if e.response["Error"]["Code"] != "ResourceInUseException":
            raise
        print(f"table {a.table} already exists at {ENDPOINTS[a.profile]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
