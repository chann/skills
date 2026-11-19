---
name: interrogate
description: Use when the user asks to review code, changes, a commit, a branch, or a PR, audit code quality or security, or try to break a change, including "review my changes", "코드 리뷰", "check my code", "review the last commit", "code audit", "이 변경 깨뜨려봐", "빈틈 찾아줘", "adversarial review", "stress test this diff", "find blind spots", "/interrogate", or "$interrogate". Tries to break the diff and reports severity-tagged findings, each with its proof level (cited, traced, ran, reproduced) and the proof itself, as Markdown plus a bilingual HTML report under `.reviews/`; `--md`, "markdown only", or "마크다운만" writes Markdown only. Reports; never applies fixes. Use diff-summary to explain a change, blast-radius for what a change breaks outside the diff, and review-me for the decisions in a plan.
---

# Interrogate

Try to break the change. Every finding says how well it is proven and shows the
proof. Report the findings; never apply a fix, even a one-line one.

**Core principle:** diff in → proven, severity-tagged findings out, scoped
strictly to what changed.

## Output modes

| Request | Writes | Browser |
|---|---|---|
| `/interrogate [scope]`, `$interrogate [scope]`, or any review trigger | Korean report, English `.en.md` sibling, one bilingual HTML under `.reviews/` | Opens the HTML |
| `--md`, "markdown only", "마크다운만" | One Markdown report under `.reviews/`, in the prompt's language | None. No HTML is generated |
| "multi-model", "second opinion", "adversarial panel" | Either of the above, with panel findings merged in (step 5) | As above |

An explicit single-language request writes only that file; the generator then
renders a single-language report with no toggle.

## 1. Resolve the scope

Preserve the user's scope exactly; `main..dev` and `main...dev` are different
comparisons and are never rewritten into each other.

| User intent | Git command |
|---|---|
| "review my changes" / no specific scope | `git diff` (unstaged) + `git diff --staged` (staged) |
| "review staged changes" | `git diff --staged` |
| "review last commit" | `git diff HEAD~1..HEAD` |
| "review commit `<sha>`" | `git diff <sha>~1..<sha>` |
| "review last N commits" | `git diff HEAD~N..HEAD` |
| "review branch X" / "compare to main" | `git diff main...<branch>` (three-dot merge-base) |
| "review PR #N" | `gh pr diff N` |

When the intent is ambiguous, review staged + unstaged changes. When there are
no changes, say so and name the likely cause (nothing staged, wrong branch).

State the change's intent in one sentence from the user's message, the commit
messages, and the PR description. A defect is a way the change fails that
intent. Ask only when the intent cannot be inferred and the answer changes a
severity.

Report filename SHA: a commit's short SHA; for a range, the latest commit's;
`staged` or `working` when nothing is committed.

## 2. Gather context and load references

```bash
git diff [range] --numstat | python <skill-path>/scripts/diff_stats.py
```

The JSON names the languages and whether security-sensitive files changed. Load
only what it calls for:

- Always: `references/review-criteria.md` (dimensions and severity detail).
- `.py` → `references/python.md`; `.js`, `.ts`, `.jsx`, `.tsx` →
  `references/javascript-typescript.md`; `go.md`, `rust.md`, `java.md` when they
  exist.
- `has_security_sensitive_files: true` → `references/common-vulnerabilities.md`.
- Before proving anything at `ran`, or when running a panel →
  `references/proof-and-panel.md`.

## 3. Try to break it

For every changed hunk ask how it fails the intent. Attack along five
dimensions: **Correctness** (logic, edge cases, error paths), **Security**
(injection, auth, exposure, crypto, input validation), **Complexity &
Consistency**, **Maintainability**, and **Best Practices** from the loaded
references. Prefer inputs the author did not picture: empty, huge, concurrent,
repeated, malformed, a dependency that fails.

| Severity | Meaning | Action required |
|----------|---------|-----------------|
| **CRITICAL** | Data loss, security breach, or crash in production | Must fix before merge |
| **HIGH** | Bug, vulnerability, or serious design flaw | Should fix before merge |
| **MEDIUM** | Code smell, inconsistency, moderate risk | Recommended fix |
| **LOW** | Style, naming, minor improvement | Nice to have |
| **INFO** | Verified context that materially affects a review decision but requires no code change | No action needed |

Never use INFO solely for uncertainty or praise. Missing evidence belongs under one specific **Open Questions** item only when it changes severity or action; otherwise omit it.

**Every finding needs a stable ID** in its title: `#### [CR-001] ...`,
`[CR-002]`, and so on. The HTML keys per-finding comments to this ID, so the
same ID marks the same finding in both language files; never renumber between
languages.

## 4. Prove each finding

Grade every finding on this ladder, weakest first, and push it as far as is
cheap:

| Level | Means | The proof you paste |
|---|---|---|
| `said` | Claimed, nothing more | — (never reported) |
| `cited` | A real changed `file:line` shows it | the `file:line` |
| `traced` | The failing path walked step by step, each step citing a line | the numbered walk |
| `ran` | A command or test printed the failure | the exact command and the output it printed |
| `reproduced` | Seen in the running product | the steps and what was observed |

- **Dropped findings.** A finding that cannot reach `cited` is dropped. It is
  never shown as a finding; it only adds to the `**Dropped:**` count in the
  report header.
- **Top two severities.** Before reporting a CRITICAL or HIGH finding, push it
  to `traced` or `ran`. If it stays at `cited`, keep it and write its level as
  `cited, not traced` so the reader knows.
- **Safe proof only.** Proof commands are read-only with respect to the
  reviewed tree: run the project's existing tests, or a small repro script in a
  temporary directory outside the repository that imports the changed code.
  Never mutate the reviewed tree (no edits, no checkout, no install into it),
  never run destructive commands, and never send repository content to the
  network. Compare `git status --porcelain` before and after each proof run; if
  it changed, report that and stop proving.
- A command that needs the network, credentials, or a destructive step is not
  run; the finding stays at the level it reached and says why.

## 5. Optional adversary panel

Run a panel only when the user asks for a multi-model review, a second opinion,
or an adversarial panel. When the `swarm` skill is installed, use it to hand the
same brief (scope, intent, and the proof rules above) to adversaries on
different vendors. Then, in this session:

1. Rerun each returned finding's command under the safe-proof rules. Keep it
   only when the output shows the failure and the failure breaks the intent.
2. Merge findings that share a root cause into one, naming every adversary that
   found it.
3. Count each adversary's unverified findings under `**Dropped:**`, per
   adversary, with the reason.

Without `swarm`, review in this session and say in the reply that the panel was
not run. `references/proof-and-panel.md` carries the brief.

## Evidence-first writing contract

This contract is authoritative for every output mode.

- For every actionable finding, write in this order: **observed behavior** → **practical consequence** → **smallest justified correction**.
- Cite the changed path and line before making the claim, and quote only the smallest excerpt needed to establish the evidence.
- State verified facts directly. Prefix a consequential inference with `Inference:` and tie it to the cited evidence.
- Keep prose proportional to the evidence. Do not restate code, repeat a conclusion, manufacture INFO items, or add generic praise such as "solid", "robust", "clean", or "well-structured".
- When there are no actionable findings, state that directly and include only material residual risks or verification gaps.
- Do not add an announcement, generic preface, congratulations, or an overall-quality claim.
- Start the report with its title and parser-significant metadata, then present findings.

### Conditional sections

- **Decision Summary:** Include only when a cross-cutting risk needs one non-repeated decision statement.
- **Positive Observations:** Include only when a concrete, evidenced pattern lowers risk or review effort.
- **Open Questions:** Include only when missing evidence changes severity or action; keep it to one specific item for that gap.
- **File Summary:** Include only when multi-file navigation helps the reader without repeating findings.

Omit filler, empty headings, and any conclusion already stated in a finding.

## 6. Write the Markdown report

Create `.reviews/` at the repository root if missing. Omit zero-finding
severity headings.

```markdown
# Code Review Report

**Date:** YYYY-MM-DD
**Reviewer:** automated review
**Scope:** [e.g., "Staged changes", "Commits a1b2c3d..f4e5d6a on branch feature-auth"]
**Repository:** [repo name]
**Language:** en
**Risk:** LOW / MEDIUM / HIGH / CRITICAL
**Findings:** N critical, N high, N medium, N low, N info
**Dropped:** N (below `cited`)

## Findings

### HIGH

#### [CR-001] Short title describing the finding
**File:** `path/to/file.py` (lines 42-58)
**Category:** Security | Correctness | Complexity | Maintainability | Best Practice
**Evidence:** ran — `python3 /tmp/cr-001/repro.py` printed:

\```text
AssertionError: expected 2 rows, got 1
\```

**Observed behavior:** [What the changed code demonstrably does.]
**Practical consequence:** [The concrete failure mode, risk, or maintenance cost.]
**Smallest justified correction:** [The narrowest change supported by the evidence.]
```

`**Evidence:**` opens with the level word, then the proof: the `file:line` for
`cited`, the numbered walk for `traced`, the command and its output for `ran`.

Save to `.reviews/<YYYY-MM-DD>_<short-sha>.md`. Large diffs (over 1000 lines):
spend the proof budget on CRITICAL and HIGH and group similar MEDIUM/LOW
findings by pattern.

## 7. Generate HTML (skip with `--md`)

Write the Korean primary and the English sibling with identical structure —
same headings, IDs, code blocks, and `**Evidence:**` lines — then:

```bash
python <skill-path>/scripts/generate_html_report.py .reviews/<YYYY-MM-DD>_<short-sha>.md
open .reviews/<YYYY-MM-DD>_<short-sha>.html
```

The generator finds the `.en.md` sibling, renders the proof level of each
finding as a pill on its card, and produces one self-contained file with a
language toggle (Korean by default), theme and code-scheme selectors, a
collapsible sidebar, per-finding "Copy Markdown" and browser-stored comments,
and a "Copy feedback" payload to paste into a new `/interrogate` run. `--alt
<path>` names a translation explicitly; `--theme` and `--code-scheme` change
defaults.

## 8. Finish

Reply with facts only: finding counts by severity, the dropped count, overall
risk, generated artifact paths, the proof commands that ran and whether the
tree stayed clean, fresh verification, the panel result or "panel not run", and
the browser-open result or warning (default mode only). Do not repeat report
prose or promise a fixed finding count. Only when artifacts were generated and
`.reviews/` is not ignored, suggest adding it to `.gitignore`.

## Report language

Write the report in the same language as the user's prompt; default to English
when ambiguous. Translate narrative headings, finding descriptions, conditional prose, and table headers or values when appropriate.

Keep these parser-significant metadata keys exactly in English: `Date`, `Reviewer`, `Scope`, `Repository`, and `Language`. Translate their values when appropriate, and set `**Language:** ko` for a Korean report (BCP 47: `en`, `ko`, `ja`, `zh`).

Also always English: the `Evidence` and `Dropped` keys and the level words
(`cited`, `traced`, `ran`, `reproduced`, `cited, not traced`), finding IDs
(`CR-001`), severity labels, code, file paths, and identifiers.

## Never

- Apply a fix, edit the reviewed tree, or run a destructive or network-bound
  proof command.
- Show a finding below `cited`, or report CRITICAL/HIGH at `cited` without
  marking it `cited, not traced`.
- Generate HTML or open a browser in `--md` mode.
- Modify `.gitignore` (suggest only).
- Comment on code outside the diff; a request to review untouched code is named
  and declined.
- Manufacture findings to fill space, or use INFO as a substitute for evidence.

**Reply:** finding counts by severity, dropped count, risk, artifact paths, proof commands run with a clean-tree check, fresh verification, panel status, and the browser-open result unless `--md`.
