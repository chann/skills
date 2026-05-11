#!/usr/bin/env bash
# Install the long-task Stop hook into ~/.claude/settings.json.
#
# Usage:
#   bash install.sh             # install if missing, skip if already installed
#   bash install.sh --overwrite # update the command path if already installed
#
# Safe to run repeatedly. JSON patching is delegated to python3 so existing
# unrelated settings.json content is preserved.

set -euo pipefail

OVERWRITE=0
for arg in "$@"; do
    case "$arg" in
        --overwrite) OVERWRITE=1 ;;
        -h|--help)
            sed -n '2,12p' "$0"
            exit 0 ;;
        *)
            echo "Unknown argument: $arg" >&2
            echo "Run with --help for usage." >&2
            exit 2 ;;
    esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="$REPO_ROOT/scripts/long_task.py"
SETTINGS="${CLAUDE_SETTINGS:-$HOME/.claude/settings.json}"

if [ ! -f "$SCRIPT" ]; then
    echo "long_task.py not found at $SCRIPT" >&2
    exit 1
fi

chmod +x "$SCRIPT"

python3 - "$SETTINGS" "$SCRIPT" "$OVERWRITE" <<'PY'
import json
import os
import sys
from pathlib import Path

settings_path = Path(sys.argv[1])
script_path = Path(sys.argv[2])
overwrite = sys.argv[3] == "1"

settings_path.parent.mkdir(parents=True, exist_ok=True)

if settings_path.exists():
    text = settings_path.read_text(encoding="utf-8").strip()
    data = json.loads(text) if text else {}
else:
    data = {}

hooks = data.setdefault("hooks", {})
stop_hooks = hooks.setdefault("Stop", [])

command = f"python3 {script_path} stop-hook"

existing = None
for item in stop_hooks:
    for hook in item.get("hooks", []) or []:
        if "long_task.py" in (hook.get("command") or ""):
            existing = (item, hook)
            break
    if existing:
        break

if existing:
    if overwrite:
        existing[1]["command"] = command
        action = "updated"
    else:
        print("long-task Stop hook already installed. Use --overwrite to update.")
        sys.exit(0)
else:
    stop_hooks.append({
        "matcher": "",
        "hooks": [{"type": "command", "command": command}],
    })
    action = "installed"

settings_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print(f"long-task Stop hook {action}.")
print(f"  Command:  {command}")
print(f"  Settings: {settings_path}")
PY

echo "Done."
