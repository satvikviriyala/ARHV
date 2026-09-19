#!/usr/bin/env python3
"""SessionStart hook: re-inject live project state from MEMORY.md into Claude's context.

Fires on startup, resume, /clear and after auto-compaction. For SessionStart, plain stdout
is added to Claude's context, so a fresh or compacted session always knows where it is.
"""
import os
import re
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
SECTIONS = (("Snapshot", 45), ("Next Steps", 25), ("Open Issues", 20), ("Human-Blocked", 15))


def section(text: str, name: str) -> str:
    m = re.search(rf"^## {re.escape(name)}[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1).strip() if m else ""


def main() -> int:
    try:
        text = open(os.path.join(ROOT, "MEMORY.md"), encoding="utf-8").read()
    except FileNotFoundError:
        print("PACT: MEMORY.md is missing. Recreate it from the template described in CLAUDE.md before any other work.")
        return 0
    out = ["=== PACT live state (auto-injected from MEMORY.md by .claude/hooks/session_context.py) ==="]
    for name, limit in SECTIONS:
        body = section(text, name)
        if body:
            out.append(f"## {name}\n" + "\n".join(body.splitlines()[:limit]))
    out.append("Protocol: CLAUDE.md rules -> the current docs/phases/ file -> implement -> verify (docs/TESTING.md) "
               "-> update MEMORY.md (Log + Snapshot + Next Steps) -> commit. Errors: docs/SELF_CORRECTION.md.")
    print("\n\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
