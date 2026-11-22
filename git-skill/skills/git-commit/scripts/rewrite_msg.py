#!/usr/bin/env python3
"""Replace one Git commit message using an explicit, private JSON map."""

from __future__ import annotations

import json
import os
import re
import stat
import sys
from pathlib import Path


def validate_messages(pairs: list[tuple[str, object]]) -> dict[str, str]:
    messages: dict[str, str] = {}
    for oid, message in pairs:
        if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", oid):
            raise ValueError("invalid commit ID in rewrite map")
        if oid in messages:
            raise ValueError("duplicate commit ID in rewrite map")
        if not isinstance(message, str) or not message.strip() or "\x00" in message:
            raise ValueError("invalid commit message in rewrite map")
        messages[oid] = message
    return messages


def main() -> int:
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_absolute():
        print("Expected an absolute rewrite-map path", file=sys.stderr)
        return 1
    oid = os.environ.get("GIT_COMMIT", "")
    if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", oid):
        print("Missing or invalid GIT_COMMIT", file=sys.stderr)
        return 1

    try:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        descriptor = os.open(sys.argv[1], flags)
        with os.fdopen(descriptor, encoding="utf-8") as source:
            mode = os.fstat(source.fileno()).st_mode
            if not stat.S_ISREG(mode) or mode & 0o077:
                raise ValueError("rewrite map must be a private regular file")
            messages = json.load(source, object_pairs_hook=validate_messages)
        if not isinstance(messages, dict):
            raise ValueError("expected a JSON object in the rewrite map")
        original = sys.stdin.buffer.read()
        message = messages[oid].encode("utf-8") if oid in messages else original
        sys.stdout.buffer.write(message)
    except (OSError, ValueError) as error:
        print(f"Cannot apply rewrite map ({type(error).__name__})", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
