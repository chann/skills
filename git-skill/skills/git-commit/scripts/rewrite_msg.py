#!/usr/bin/env python3
"""Map a commit SHA to a new message for `git filter-branch --msg-filter`.

Reads stdin (the original message), looks up `$GIT_COMMIT` in
`/tmp/cc-rewrite-map.tsv` (one line per remapped commit:
`<full-40-char-sha>\\t<new-message-with-\\n-escapes>`), and prints the new
message. Commits absent from the map (or when the map is missing) pass
through unchanged.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

MAP_PATH = Path(os.environ.get("CC_REWRITE_MAP", "/tmp/cc-rewrite-map.tsv"))


def main() -> int:
    original = sys.stdin.read()
    sha = os.environ.get("GIT_COMMIT", "")
    if not sha or not MAP_PATH.exists():
        sys.stdout.write(original)
        return 0

    try:
        with MAP_PATH.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if "\t" not in line:
                    continue
                map_sha, encoded = line.split("\t", 1)
                if map_sha == sha:
                    sys.stdout.write(encoded.replace("\\n", "\n"))
                    return 0
    except OSError:
        pass

    sys.stdout.write(original)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
