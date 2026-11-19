# Routes, models, and quota

A route id is `agent/provider/model`. Agents are `codex`, `claude-code`,
`opencode`, and `antigravity`. Provider and model come from the CLI that is
actually logged in. The same model on two agents is two routes because the
quota buckets are not the same.

Run `probe --check-auth` first. Then collect models and quota with the commands
below. Save each transcript to a file and point `quota_source` at it. If the
command fails, the output is empty, or the shape does not match, set
`quota_note` to the literal `unknown`. A number that is not in that file will
be rejected.

Do not call provider HTTP APIs with tokens taken from CLI auth files. Do not
print those files. Do not write them into the cache.

## Codex

Models and the weekly bucket come from `codex app-server` over stdin, as
JSON-RPC: `initialize`, then `initialized`, then `model/list`, then
`account/rateLimits/read`. `model/list` returns `result.data[].id`. The rate
limit payload's `primary.usedPercent` and `primary.resetsAt` are the quota
facts. `codex debug models` is an acceptable model list when the app-server
schema has changed. If both fail, models stay unknown and the only legal route
is one the user named.

## Claude Code

Zero-token model discovery is one initialize control request:

```bash
printf '%s\n' '{"type":"control_request","request_id":"init","request":{"subtype":"initialize"}}' \
  | claude --print --input-format stream-json --output-format stream-json \
      --verbose --no-session-persistence
```

`--verbose` is required with `stream-json`. Read `models[].resolvedModel` from
the control response. Drop the commands, skills, and agents arrays before
saving any of that output.

Quota:

```bash
claude -p "/usage" --output-format json --no-session-persistence
```

Pass the `.result` text through:

```bash
python3 <skill-dir>/scripts/swarm.py parse-usage --agent claude-code --file <usage.txt>
```

`status: unknown` means no usable line was found. Do not treat that as 0%.
A Fable weekly bucket at 100% removes Fable routes only. Other Claude models
stay eligible while their own bucket has room.

## OpenCode

`opencode models` lists authenticated models. There is no single quota command.
Start each provider bucket as `unknown`. After a run fails with HTTP 429 or an
exhausted-quota message on stderr, record that observation in the next plan's
`quota_note` and keep the stderr path as `quota_source`. Exhausting one
provider does not exhaust the others.

## Antigravity

`agy models` lists the models on that subscription. Infer the vendor from the
model id when the CLI does not print one: Claude ids are `anthropic`, Gemini
ids are `google`, GPT ids are `openai`. Quota that `agy` does not print is
`unknown`.

## What gets stored

`probe.json` stores the binary path, version, usable flag, and `auth_ok`.
It does not store the auth status email, org, or token. Quota transcripts may
contain account percentages. They must not contain secrets. The helper redacts
values that follow `api_key`, `access_token`, `authorization`, `bearer`, or a
`sk-` token before it writes a file.
