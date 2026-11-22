# interrogate

[한국어](README.ko.md) · [← back to main](../README.md)

Try to break a change before it ships, and show how well each claim is proven.

| Skill | Question it answers |
|---|---|
| `interrogate` | What is wrong **inside** this diff? |
| `blast-radius` | What could this change break **outside** the diff? |

## Why it is different

A review that sounds right reads exactly like one that is right. So every
finding here carries its proof level and the proof itself, on one ladder,
weakest first:

| Level | Means |
|---|---|
| `said` | Claimed. Never reported as a finding |
| `cited` | A real changed `file:line` shows it |
| `traced` | The failing path walked step by step, each step citing a line |
| `ran` | A command or test printed the failure; the command and its output are pasted |
| `reproduced` | Seen in the running product |

- Findings that never reach `cited` are dropped and only counted.
- CRITICAL and HIGH findings are pushed to `traced` or `ran`; one that stays at
  `cited` is labelled `cited, not traced`.
- Proof runs are read-only on the reviewed tree: the project's tests, or a
  repro script in a temporary directory outside the repository. No edits, no
  destructive commands, no repository content sent to the network.
- The review reports. It never applies fixes.

## Installation

Global:

```bash
npx skills add -y -g chann/skills --skill interrogate --skill blast-radius
```

Project-local:

```bash
npx skills add chann/skills --skill interrogate --skill blast-radius
```

Each skill works when installed alone.

## Usage

| Claude Code | Codex | Output |
|---|---|---|
| `/interrogate [scope]` | `$interrogate [scope]` | Korean + English Markdown and one bilingual HTML under `.reviews/`, opened in a browser |
| `/interrogate [scope] --md` | `$interrogate [scope] --md` | One Markdown report under `.reviews/`; no HTML, no browser |
| `/blast-radius [scope]` | `$blast-radius [scope]` | A reply: the safety fact with its proof, risks, what was cleared, and the cheapest pre-merge check |

Examples:

```text
> review my changes
> 이 변경 깨뜨려봐
> /interrogate main..dev
> /interrogate review PR #42 --md
> adversarial multi-model review of the last commit
> /blast-radius
> 이거 바꾸면 뭐가 깨져?
```

An explicit range is preserved exactly: `main..dev` and `main...dev` are
different comparisons and are never rewritten into each other. Supported scopes
are current, staged, or unstaged changes; the last commit or last N commits; a
commit, range, or branch comparison; and a PR.

### Optional adversary panel

Ask for a multi-model, second-opinion, or adversarial panel and, when the
`swarm` skill is installed, `interrogate` hands one brief to adversaries on
different vendors. It reruns every returned command itself, keeps only findings
whose output shows the failure, merges findings with one root cause, and counts
unverified ones per adversary under **Dropped**. Without `swarm` it reviews in
the current session and says the panel was not run.

### Choose the right workflow

| Goal | Workflow |
|---|---|
| Find defects, regressions, and vulnerabilities in the diff | `interrogate` |
| Find what the change breaks elsewhere and prove why it is safe | `blast-radius` |
| Explain what changed and why | `diff-summary` |
| Weigh the decisions in a plan | `review-me` |

## How `interrogate` works

1. Resolve the scope and state the change's intent in one sentence.
2. Run `diff_stats.py` and load only the reference guides the languages need.
3. Attack the diff along correctness, security, complexity, maintainability,
   and best practice, and assign severities.
4. Push each finding down the proof ladder; drop what never reaches `cited`.
5. Optionally merge a verified adversary panel.
6. Write the report; without `--md`, write the English sibling, generate the
   HTML, and open it.

## Report format

Findings follow **observed behavior → practical consequence → smallest
justified correction**, each with an `**Evidence:**` line:

```markdown
#### [CR-001] Cache returns stale rows after invalidate
**File:** `src/cache.py` (lines 42-58)
**Category:** Correctness
**Evidence:** ran — `python3 /tmp/cr-001/repro.py` printed:
```

The header carries `**Findings:**` counts and a `**Dropped:**` count.
`Decision Summary`, `Positive Observations`, `Open Questions`, and
`File Summary` appear only when they add distinct, decision-relevant
information. When there are no actionable findings, the report says so.

## HTML report

The default mode merges the Korean report and its English translation into one
self-contained HTML file with:

- **Proof pills** — each finding's level (`cited`, `traced`, `ran`,
  `reproduced`) on its card and next to its evidence; `cited, not traced` is
  highlighted as a warning.
- **Language toggle** — Korean by default; falls back to one language when no
  translation exists.
- **Theme and code scheme** — light/dark/auto plus eight syntax schemes.
- **Compact sidebar** — collapsible and resizable, with section nav and a
  comments panel.
- **Per-finding "Copy Markdown" and comments** — comments are stored in the
  browser and keyed by finding ID, so they survive a language switch.
- **"Copy feedback"** — a payload to paste into a new `/interrogate` run.

The report runs offline. It embeds the browser bundle and selected themes from
`@highlightjs/cdn-assets@11.11.1` with their license and blocks external resources.

## Severity levels

| Level    | Meaning                                                       |
| -------- | ------------------------------------------------------------- |
| CRITICAL | Data loss, security breach, or crash in production — must fix |
| HIGH     | Bug, vulnerability, or serious design flaw — should fix       |
| MEDIUM   | Code smell, inconsistency, or moderate risk — recommended fix |
| LOW      | Style, naming, minor improvement — nice to have               |
| INFO     | Verified context that affects a decision; no code change required |

## How `blast-radius` works

1. Read the change, including the behavior it changes without saying so.
2. Name the one or two facts the change is safe because of.
3. Look where a symbol search stops: the pinned library's own source, timing
   and teardown, serialized shapes, flags and config, and code several hops
   downstream.
4. Prove each fact as far down the ladder as is cheap, usually one script in a
   temporary directory that imports the shipped code.
5. Reply with the safety fact and its proof (or "unproven"), risks with
   `file:line`, what was cleared, and the cheapest check before merging.

It never invents a caller; "searched, found nothing" is a valid result.

## Package layout

```text
interrogate/
├── .claude-plugin/plugin.json
├── commands/
│   ├── interrogate.md
│   └── blast-radius.md
├── skills/
│   ├── interrogate/
│   │   ├── SKILL.md
│   │   ├── agents/openai.yaml
│   │   ├── evals/evals.json
│   │   ├── scripts/
│   │   │   ├── diff_stats.py             # git diff --numstat -> JSON
│   │   │   └── generate_html_report.py   # Markdown -> bilingual HTML
│   │   ├── references/
│   │   │   ├── review-criteria.md
│   │   │   ├── proof-and-panel.md
│   │   │   ├── common-vulnerabilities.md
│   │   │   ├── python.md
│   │   │   └── javascript-typescript.md
│   │   └── assets/report-template.html
│   └── blast-radius/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       └── evals/evals.json
├── README.md
├── README.ko.md
└── .snyk
```

Intentionally vulnerable sample fixtures live outside this plugin, at the
repo-root [`samples/code-review/`](../samples/code-review/).

## Requirements

- Git repository
- Python 3.10+ for `interrogate` report generation (standard library only)
- Permission to run the project's own tests when a finding is proven at `ran`

## Security notes

- **Fence-language attribute XSS (fixed):** fence language tokens are
  whitelisted to `[A-Za-z0-9._+-]{0,32}` by `safe_lang()`, so a malicious
  fence cannot break out of the `class` attribute.
- **`html.escape(quote=False)` (false positive):** the result only goes into
  element bodies; attribute values are hard-coded class names, fixed proof
  level words, or `slugify()` output.
- **Raw Markdown embed:** the source is embedded in a
  `<script type="application/json">` block with `</` escaped to `<\/`.
- **Path arguments (false positive):** the script reads and writes paths the
  user passed on the command line.
- **Fixtures:** vulnerable samples are kept outside the plugin, and `.snyk`
  excludes `samples/**` if a scanner descends here.

## License

MIT
