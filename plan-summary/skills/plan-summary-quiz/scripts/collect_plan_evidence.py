#!/usr/bin/env python3
"""Collect bounded UTF-8 plan documents from an exact JSON request."""

from __future__ import annotations

import errno
import hashlib
import json
import os
import stat
import sys
from pathlib import Path


ALLOWED_SUFFIXES = frozenset({".md", ".markdown", ".txt"})
MAX_FILES = 16
MAX_FILE_BYTES = 1 * 1024 * 1024
MAX_TOTAL_BYTES = 4 * 1024 * 1024
MAX_REQUEST_BYTES = 64 * 1024
MAX_PATH_CHARACTERS = 4096


class CollectionError(ValueError):
    """Raised when the request cannot be collected without broadening scope."""


def parse_request(raw: bytes) -> list[str]:
    """Validate the fixed JSON request and return exact path strings."""
    if not raw or len(raw) > MAX_REQUEST_BYTES:
        raise CollectionError("request must be non-empty and at most 65536 bytes")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CollectionError("request must be one valid UTF-8 JSON object") from error
    if not isinstance(payload, dict):
        raise CollectionError("request must be a JSON object")

    unsupported = sorted(set(payload) - {"paths"})
    if unsupported:
        raise CollectionError(f"unsupported request field: {unsupported[0]}")

    paths = payload.get("paths")
    if not isinstance(paths, list) or not paths:
        raise CollectionError("paths must be a non-empty list")
    if len(paths) > MAX_FILES:
        raise CollectionError(f"at most {MAX_FILES} source files are allowed")

    validated: list[str] = []
    for index, raw_path in enumerate(paths, start=1):
        if not isinstance(raw_path, str) or not raw_path:
            raise CollectionError(f"path {index} must be a non-empty string")
        if len(raw_path) > MAX_PATH_CHARACTERS:
            raise CollectionError(
                f"path {index} exceeds {MAX_PATH_CHARACTERS} characters"
            )
        if "\x00" in raw_path or any(ord(character) < 32 for character in raw_path):
            raise CollectionError(f"path {index} contains a control character")
        if "://" in raw_path:
            raise CollectionError(f"path {index} must not be a remote URL")
        validated.append(raw_path)
    return validated


def _display_path(resolved: Path, cwd: Path) -> str:
    try:
        return resolved.relative_to(cwd.resolve()).as_posix()
    except ValueError:
        return str(resolved)


def _read_regular_file(path: Path) -> tuple[bytes, os.stat_result]:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except FileNotFoundError as error:
        raise CollectionError("source does not exist") from error
    except OSError as error:
        if error.errno == errno.ELOOP:
            raise CollectionError("source must not be a symbolic link") from error
        raise CollectionError(f"source could not be opened: {error.strerror}") from error

    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise CollectionError("source must be a regular file")
        if metadata.st_size > MAX_FILE_BYTES:
            raise CollectionError(f"source exceeds {MAX_FILE_BYTES} bytes")

        chunks: list[bytes] = []
        remaining = MAX_FILE_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, min(64 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        content = b"".join(chunks)
        if len(content) > MAX_FILE_BYTES:
            raise CollectionError(f"source exceeds {MAX_FILE_BYTES} bytes")
        return content, metadata
    finally:
        os.close(descriptor)


def collect_document(raw_path: str, cwd: Path) -> dict[str, object]:
    """Read one explicit document without expanding or executing its path."""
    candidate = Path(raw_path)
    lexical = candidate if candidate.is_absolute() else cwd / candidate

    if lexical.suffix.lower() not in ALLOWED_SUFFIXES:
        allowed = ", ".join(sorted(ALLOWED_SUFFIXES))
        raise CollectionError(f"unsupported source extension; expected one of {allowed}")

    try:
        lexical_metadata = lexical.lstat()
    except FileNotFoundError as error:
        raise CollectionError("source does not exist") from error
    except OSError as error:
        raise CollectionError(f"source metadata could not be read: {error.strerror}") from error

    if stat.S_ISLNK(lexical_metadata.st_mode):
        raise CollectionError("source must not be a symbolic link")
    if not stat.S_ISREG(lexical_metadata.st_mode):
        raise CollectionError("source must be a regular file")

    try:
        resolved = lexical.resolve(strict=True)
    except OSError as error:
        raise CollectionError(f"source could not be resolved: {error.strerror}") from error

    content_bytes, metadata = _read_regular_file(lexical)
    if b"\x00" in content_bytes:
        raise CollectionError("source must be UTF-8 text, not binary data")
    try:
        content = content_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise CollectionError("source must be valid UTF-8") from error

    return {
        "input_path": raw_path,
        "resolved_path": str(resolved),
        "display_path": _display_path(resolved, cwd),
        "size_bytes": len(content_bytes),
        "sha256": hashlib.sha256(content_bytes).hexdigest(),
        "content": content,
        "_identity": [metadata.st_dev, metadata.st_ino],
    }


def collect_documents(paths: list[str], cwd: Path) -> dict[str, object]:
    """Collect every validated source atomically into one response object."""
    documents: list[dict[str, object]] = []
    identities: set[tuple[int, int]] = set()
    total_bytes = 0

    for index, raw_path in enumerate(paths, start=1):
        try:
            document = collect_document(raw_path, cwd)
        except CollectionError as error:
            raise CollectionError(f"source {index} {raw_path!r}: {error}") from error

        raw_identity = document.pop("_identity")
        identity = tuple(raw_identity) if isinstance(raw_identity, list) else ()
        if len(identity) != 2 or not all(isinstance(value, int) for value in identity):
            raise CollectionError(f"source {index} {raw_path!r}: invalid file identity")
        typed_identity = (identity[0], identity[1])
        if typed_identity in identities:
            raise CollectionError(f"source {index} {raw_path!r}: duplicate source")
        identities.add(typed_identity)

        size_bytes = document["size_bytes"]
        if not isinstance(size_bytes, int):
            raise CollectionError(f"source {index} {raw_path!r}: invalid file size")
        total_bytes += size_bytes
        if total_bytes > MAX_TOTAL_BYTES:
            raise CollectionError(f"sources exceed {MAX_TOTAL_BYTES} bytes in total")
        documents.append(document)

    return {
        "version": 1,
        "documents": documents,
        "total_bytes": total_bytes,
    }


def main() -> int:
    """Run the JSON-stdin collector."""
    try:
        paths = parse_request(sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1))
        response = collect_documents(paths, Path.cwd())
    except CollectionError as error:
        sys.stderr.write(f"plan-summary collector: {error}\n")
        return 2
    except BrokenPipeError:
        return 1

    try:
        sys.stdout.write(
            json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n"
        )
        sys.stdout.flush()
    except BrokenPipeError:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
