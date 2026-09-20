import os
import re

from pact_core import config


def test_account_quota_matches_cedar_policy():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "functions", "authorizer", "cedar", "policies.cedar")
    text = open(path, encoding="utf-8").read()
    match = re.search(r"bookingsToday\s*<\s*(\d+)", text)
    assert match and int(match.group(1)) == config.ACCOUNT_DAILY_QUOTA
