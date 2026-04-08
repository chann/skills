#!/usr/bin/env python3
"""Extract statistics from git diff --numstat output.

Usage:
    git diff [range] --numstat | python diff_stats.py
    python diff_stats.py < numstat_output.txt
"""

import json
import re
import sys

EXTENSION_TO_LANGUAGE = {
    ".py": "Python",
    ".pyi": "Python",
    ".js": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".c": "C",
    ".h": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".hpp": "C++",
    ".cs": "C#",
    ".scala": "Scala",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".sql": "SQL",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".less": "LESS",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".json": "JSON",
    ".toml": "TOML",
    ".xml": "XML",
    ".md": "Markdown",
    ".r": "R",
    ".R": "R",
    ".dart": "Dart",
    ".lua": "Lua",
    ".ex": "Elixir",
    ".exs": "Elixir",
    ".erl": "Erlang",
    ".zig": "Zig",
    ".nim": "Nim",
    ".tf": "Terraform",
    ".proto": "Protobuf",
    ".graphql": "GraphQL",
    ".gql": "GraphQL",
    ".vue": "Vue",
    ".svelte": "Svelte",
}

SECURITY_PATH_PATTERNS = [
    r"auth", r"login", r"session", r"token", r"jwt",
    r"crypto", r"encrypt", r"decrypt", r"hash",
    r"password", r"passwd", r"credential", r"secret",
    r"permission", r"role", r"access", r"acl",
    r"security", r"oauth", r"saml", r"sso",
    r"sanitiz", r"validat", r"escap",
    r"middleware",
    r"\.env", r"config",
]

SECURITY_PATH_RE = re.compile(
    "|".join(SECURITY_PATH_PATTERNS), re.IGNORECASE
)


def get_extension(path: str) -> str:
    dot = path.rfind(".")
    if dot == -1:
        return ""
    return path[dot:]


def detect_language(path: str) -> str:
    ext = get_extension(path)
    return EXTENSION_TO_LANGUAGE.get(ext, "")


def is_security_sensitive(path: str) -> bool:
    return bool(SECURITY_PATH_RE.search(path))


def is_binary(added: str, deleted: str) -> bool:
    return added == "-" and deleted == "-"


def parse_numstat(lines: list[str]) -> dict:
    files = []
    total_insertions = 0
    total_deletions = 0
    languages = set()
    has_security = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t", 2)
        if len(parts) < 3:
            continue

        added_str, deleted_str, path = parts

        # Handle renames: {old => new} or old => new
        if " => " in path:
            # Extract the new path from rename notation
            rename_match = re.search(r"\{.* => (.*)\}", path)
            if rename_match:
                path = re.sub(r"\{.* => (.*)\}", rename_match.group(1), path)
            else:
                path = path.split(" => ")[-1]

        binary = is_binary(added_str, deleted_str)
        insertions = 0 if binary else int(added_str)
        deletions = 0 if binary else int(deleted_str)

        lang = detect_language(path)
        if lang:
            languages.add(lang)

        sec_sensitive = is_security_sensitive(path)
        if sec_sensitive:
            has_security = True

        # Determine file status from the diff data
        if binary:
            status = "binary"
        elif deletions == 0 and insertions > 0:
            status = "added"
        elif insertions == 0 and deletions > 0:
            status = "deleted"
        else:
            status = "modified"

        files.append({
            "path": path,
            "status": status,
            "insertions": insertions,
            "deletions": deletions,
            "language": lang or "unknown",
            "security_sensitive": sec_sensitive,
        })

        total_insertions += insertions
        total_deletions += deletions

    return {
        "files_changed": len(files),
        "insertions": total_insertions,
        "deletions": total_deletions,
        "files": files,
        "languages": sorted(languages),
        "has_security_sensitive_files": has_security,
    }


def main():
    lines = sys.stdin.read().splitlines()
    result = parse_numstat(lines)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
