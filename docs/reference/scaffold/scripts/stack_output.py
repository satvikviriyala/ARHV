"""Print one CloudFormation stack output. Usage: python scripts/stack_output.py ApiUrl [--stack pact-dev] [--region us-east-1]"""

import argparse
import sys

import boto3


def get_outputs(stack: str, region: str) -> dict[str, str]:
    cfn = boto3.client("cloudformation", region_name=region)
    stacks = cfn.describe_stacks(StackName=stack)["Stacks"]
    return {o["OutputKey"]: o["OutputValue"] for o in stacks[0].get("Outputs", [])}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("key")
    p.add_argument("--stack", default="pact-dev")
    p.add_argument("--region", default="us-east-1")
    a = p.parse_args()
    outputs = get_outputs(a.stack, a.region)
    if a.key not in outputs:
        print(f"output {a.key!r} not found; have {sorted(outputs)}", file=sys.stderr)
        return 1
    print(outputs[a.key])
    return 0


if __name__ == "__main__":
    sys.exit(main())
