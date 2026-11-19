# Agent History Stores

A field map of the local session stores this skill mines, verified on macOS
(2026-08). Treat it as a starting map, not a schema guarantee: check that a
path exists before mining it, probe one record when a query returns nothing,
and skip absent stores silently. Everything here is read-only.

## Claude Code

- Prompt index: `~/.claude/history.jsonl` — one JSON object per submitted
  prompt: `display` (prompt text), `timestamp` (epoch **milliseconds**),
  `project` (absolute cwd), `sessionId` (missing on old lines).
- Transcripts: `~/.claude/projects/<munged-cwd>/<session-uuid>.jsonl` — the
  directory name munges `/` and other characters to `-` lossily; read the
  real path from each record's `cwd` field instead of decoding the name.
  Session dirs may also nest `<session-uuid>/subagents/**.jsonl` (subagent
  and workflow traffic, all `isSidechain: true`) — glob transcripts at depth
  1 only.
- Record fields: conversation records carry `type` (`user`, `assistant`,
  `system`, …), an ISO-8601 UTC `timestamp`, `cwd`, `gitBranch`, and
  `message`. Real user prompts have `type == "user"`,
  `userType == "external"`, no `isMeta: true`, and string `message.content`.
  Assistant output is the `{"type": "text"}` blocks in `message.content`.
  Exclude `isSidechain: true` (subagent traffic) and `isMeta: true` records.
  That filter still matches slash-command and notification wrappers whose
  content starts with `<command-name>`, `<local-command-stdout>`, or
  `<task-notification>` — do not count them as prompts. Count prompts and
  sessions from `history.jsonl` (it indexes only submitted prompts; note
  `/clear` rotates the session id, so the index and transcript filenames can
  disagree) and use transcripts for outcomes.
- Cheap filter: pre-select session files by mtime >= range start, then filter
  records by `timestamp`. Filenames are UUIDs — useless for dating.
- Example:
  `jq -r 'select(.timestamp >= 1785600000000) | .project + "\t" + .display' ~/.claude/history.jsonl`

## Codex CLI

- Sessions: `~/.codex/sessions/YYYY/MM/DD/rollout-<local-start>-<uuid>.jsonl`
  (plus `~/.codex/archived_sessions/`). The date path and filename use
  **local** time while records inside carry ISO UTC `timestamp` — pad path
  globs by ±1 day around the range before record-level filtering.
- Every line is `{"timestamp": <ISO UTC>, "type", "payload"}`. User prompts:
  `type == "event_msg"` with `payload.type == "user_message"` →
  `payload.message`. Assistant output: `payload.type == "agent_message"`.
  The cwd comes from the first record whose **top-level**
  `type == "session_meta"` (read its `payload.cwd`) or from the per-turn
  `turn_context`. Skip `developer`-role response items — injected
  instructions, not the user.
- Prompt index: `~/.codex/history.jsonl` — `{session_id, ts (epoch
  **seconds**), text}`; it has no cwd, so join `session_id` to the rollout
  file's `session_meta` when the project matters.

## opencode

- Current storage is SQLite: `~/.local/share/opencode/opencode.db`.
  `session` rows: `id`, `directory` (cwd), `title`, and `time_created` /
  `time_updated` (epoch **milliseconds**). `message` rows: `session_id`,
  `time_created`, and `data` (JSON with `role`). `part` rows hold the actual
  text — `data` JSON `{"type": "text", "text": …}` — for both user prompts
  and assistant replies.
- Query pattern:
  `sqlite3 ~/.local/share/opencode/opencode.db "SELECT directory, title FROM session WHERE time_updated BETWEEN <start_ms> AND <end_ms>"`
- Older installs used a JSON tree at `~/.local/share/opencode/storage/session/`
  with the same field shapes; fall back to globbing it when the DB is absent.

## agy (Antigravity CLI)

- Data lives under `~/.gemini/antigravity-cli/`, not `~/.agy`.
- Prompt index: `history.jsonl` — `{display, timestamp (epoch
  **milliseconds**), workspace}` — text, time, and project in one place.
- `conversation_summaries.db` (SQLite table `conversation_summaries`) adds
  per-conversation `title`, `preview`, and `last_modified_time` (local-time
  DATETIME text) for headline material — but `title`/`preview` are often
  blank, so fall back to `history.jsonl` text.
- Skip conversations flagged `is_internal` in
  `cache/conversation_metadata.json`. The step payloads inside
  `conversations/<uuid>.db` are protobuf blobs — do not mine them.

## Other stores worth probing

- GitHub Copilot CLI: `~/.copilot/session-store.db` (SQLite `sessions` with
  `cwd` and `repository`, plus `turns`).
- amp: `~/.local/share/amp/threads/T-*.json` (`created` epoch milliseconds,
  `messages`).
- Any store the user names follows the same rules: read-only, timestamps from
  the records, silent skip when absent.

## Date bucketing rules

- Normalize everything to the user's local timezone before bucketing into
  days, weeks, or months; record timestamps are UTC.
- Epoch units by store: Claude Code, opencode, and agy use milliseconds;
  Codex `history.jsonl` uses seconds.
- File mtime is a pre-filter only (`mtime >= range start` keeps sessions that
  started before the range); the record timestamp decides membership.
- Codex path dates and agy `last_modified_time` are local time — widen glob
  windows by a day, then trust record timestamps.
