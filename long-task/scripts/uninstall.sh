#!/usr/bin/env bash
# Remove the long-task Stop hook from ~/.claude/settings.json.
#
# Usage:
#   bash uninstall.sh

set -euo pipefail

SETTINGS="${CLAUDE_SETTINGS:-$HOME/.claude/settings.json}"

if [ ! -f "$SETTINGS" ]; then
    echo "No settings file at $SETTINGS — nothing to do."
    exit 0
fi

python3 - "$SETTINGS" <<'PY'
import json
import os
import sys
from pathlib import Path

settings_path = Path(sys.argv[1])
text = settings_path.read_text(encoding="utf-8").strip()
if not text:
    print("Settings file is empty — nothing to do.")
    sys.exit(0)

try:
    data = json.loads(text)
except json.JSONDecodeError as exc:
    print(f"Refusing to patch malformed JSON at {settings_path}: {exc}", file=sys.stderr)
    sys.exit(1)

stop_hooks = data.get("hooks", {}).get("Stop", []) or []

removed = 0
new_groups = []
for item in stop_hooks:
    kept_hooks = []
    for hook in item.get("hooks", []) or []:
        if "long_task.py" in (hook.get("command") or ""):
            removed += 1
            continue
        kept_hooks.append(hook)
    if kept_hooks:
        item["hooks"] = kept_hooks
        new_groups.append(item)

if removed == 0:
    print("No long-task Stop hook found — nothing removed.")
    sys.exit(0)

if new_groups:
    data["hooks"]["Stop"] = new_groups
else:
    data.get("hooks", {}).pop("Stop", None)
    if not data.get("hooks"):
        data.pop("hooks", None)

# Atomic write to avoid corrupting settings if the process dies mid-write.
serialized = json.dumps(data, indent=2) + "\n"
tmp_path = settings_path.with_suffix(settings_path.suffix + ".tmp")
try:
    with open(tmp_path, "w", encoding="utf-8") as fh:
        fh.write(serialized)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp_path, settings_path)
finally:
    if tmp_path.exists():
        try:
            tmp_path.unlink()
        except OSError:
            pass

print(f"Removed {removed} long-task Stop hook entr{'y' if removed == 1 else 'ies'}.")
PY

echo "Done."
