#!/usr/bin/env python3
"""Stop hook: keep MEMORY.md honest.

If any tracked source/doc file changed after MEMORY.md was last written, block the stop
ONCE (exit 2, reason on stderr) and ask Claude to update MEMORY.md. It never blocks twice
for the same state, so it cannot loop. Any internal error -> allow the stop (exit 0).
"""
import hashlib
import json
import os
import sys

ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
SKIP_DIRS = {".git", "node_modules", ".aws-sam", "dist", "build", "__pycache__", ".pytest_cache",
             ".ruff_cache", ".mypy_cache", ".claude", "eval", "coverage", ".localstack"}
WATCH_EXT = {".py", ".ts", ".tsx", ".js", ".jsx", ".css", ".html", ".yaml", ".yml", ".toml", ".json",
             ".cedar", ".cedarschema", ".sh", ".md"}


def newest_change() -> tuple[float, str]:
    newest, newest_path = 0.0, ""
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith((".venv", "venv"))]
        for name in filenames:
            if name == "MEMORY.md" or os.path.splitext(name)[1] not in WATCH_EXT:
                continue
            path = os.path.join(dirpath, name)
            try:
                mtime = os.path.getmtime(path)
            except OSError:
                continue
            if mtime > newest:
                newest, newest_path = mtime, path
    return newest, newest_path


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    if payload.get("stop_hook_active"):
        return 0
    memory = os.path.join(ROOT, "MEMORY.md")
    if not os.path.exists(memory):
        return 0
    mem_mtime = os.path.getmtime(memory)
    newest, newest_path = newest_change()
    if not newest_path or newest <= mem_mtime + 1.0:
        return 0
    state_dir = os.path.join(ROOT, ".claude", "state")
    os.makedirs(state_dir, exist_ok=True)
    signature = hashlib.sha1(f"{mem_mtime}|{newest_path}|{newest}".encode()).hexdigest()
    marker = os.path.join(state_dir, "memory_guard.last")
    try:
        with open(marker, encoding="utf-8") as f:
            if f.read().strip() == signature:
                return 0                      # already asked once for this exact state
    except FileNotFoundError:
        pass
    with open(marker, "w", encoding="utf-8") as f:
        f.write(signature)
    rel = os.path.relpath(newest_path, ROOT)
    sys.stderr.write(
        f"MEMORY.md is stale: '{rel}' changed after MEMORY.md was last updated. Before you stop: "
        "append a Log entry (what changed, which verification you ran and its result, commit hash), "
        "refresh Snapshot and Next Steps, and record any error under Errors & Fixes.\n")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
