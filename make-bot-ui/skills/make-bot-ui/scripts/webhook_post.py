"""Build a bot-UI page and the server-side webhook POST.

The page has no way to receive the sender key or the webhook URL. The local
server loads both from a config file and is the only caller that POSTs.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlsplit


class KeyLeak(Exception):
    """The sender key or the webhook host reached a surface that must not have it."""


class ConfigError(ValueError):
    """The server config is missing a usable URL or key."""


def load_server_config(path: Path) -> dict[str, str]:
    """Read `{url, key}` from the server config. The page never calls this."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ConfigError("server config must be a JSON object")
    url = raw.get("url")
    key = raw.get("key")
    if not isinstance(url, str) or urlsplit(url).scheme != "https" or not urlsplit(url).netloc:
        raise ConfigError("url must be an https webhook URL")
    if not isinstance(key, str) or not key.strip():
        raise ConfigError("key must be a non-empty string")
    return {"url": url, "key": key}


def render_page(title: str, controls: list[dict[str, str]]) -> str:
    """Return HTML whose buttons post to this computer. No key parameter exists."""
    if not isinstance(title, str) or not title.strip() or any(char in title for char in "<>&"):
        raise ValueError("title must be plain text")
    parts = [f"<h1>{title}</h1>"]
    seen: set[str] = set()
    for control in controls:
        control_id = control["id"]
        label = control["label"]
        if not _slug(control_id) or control_id in seen:
            raise ValueError("control id must be a unique short slug")
        if not isinstance(label, str) or not label.strip() or any(char in label for char in "<>&"):
            raise ValueError("label must be plain text")
        seen.add(control_id)
        parts.append(
            f'<form method="post" action="/send/{control_id}">'
            f'<button type="submit">{label}</button></form>'
        )
    return "<!DOCTYPE html>\n" + "\n".join(parts) + "\n"


def reject_page(html: str, *, key: str, webhook_url: str) -> None:
    """Fail when the page contains the key or the webhook host."""
    if key and key in html:
        raise KeyLeak("page contains the sender key")
    host = urlsplit(webhook_url).netloc
    if host and host in html:
        raise KeyLeak("page contains the webhook host")


def build_server_post(config: dict[str, str], payload: dict) -> dict:
    """The POST the local server sends. The key is a header, never the body."""
    url = config["url"]
    key = config["key"]
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    if key in url or key in body:
        raise KeyLeak("sender key leaked into the webhook URL or body")
    return {
        "method": "POST",
        "url": url,
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + key,
        },
        "body": body,
        "timeout_seconds": 8,
        "retries": 0,
    }


def refuse_pasted_key(message: str, key: str) -> str:
    """Return a refusal that does not repeat the key. Empty when nothing was pasted."""
    if key and key in message:
        return (
            "Refused. A sender key pasted in chat is not stored. "
            "Put it only in the server config file."
        )
    return ""


def _slug(value: object) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if not value[0].isalpha() or len(value) > 40:
        return False
    return all(char.islower() or char.isdigit() or char == "-" for char in value)
