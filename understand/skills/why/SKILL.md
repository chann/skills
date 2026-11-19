---
name: why
description: Use when the user asks why code is built the way it is, from the record rather than the code, including "왜 이렇게 되어 있어?", "이거 왜 이렇게 만들었지?", "이 플래그 왜 아직 꺼져 있어?", "why does X work this way", "why did we pick Y", "what was the reason for this change", "/why", or "$why". Reads git history, blame, pull-request and issue discussion, and design notes, and answers with a decision timeline that quotes the authors, marks inference, and states what the record does not answer. For runtime behavior use how, for external sources use research-brief, and for the user's own session history use recall.
---

# Why

Answer why something is the way it is from what its authors wrote down, not
from what the code looks like. The code shows what was decided. Only the record
shows what was weighed.

## 1. Find the target's history

Locate the line, flag, file, or behavior the question is about, then read every
step of its history:

- `git log -S<text>` and `git log -G<regex>` for when it appeared or vanished;
  `git log --follow -- <file>` across renames.
- `git blame -w -C` for the commit behind each current line, then the full
  message of that commit and of the ones that touched it afterward.
- The pull request and issue behind each commit, through `gh` when it is
  available and authenticated: the description, review threads, and linked
  issues. Read only; never comment.
- Design notes in the repository: ADRs, `docs/`, changelogs, READMEs, TODOs.

When that trail is thin — squashed history, a message that says "fix", no linked
discussion — say so, then widen to other sources the user has, such as a
tracker, chat, or a person to ask. Do not fill the gap yourself.

## 2. Answer with a timeline

Start with a short answer and your confidence in it (`high`, `medium`, `low`),
then a decision timeline, one row per step:

| Stage | Commit or PR | Date | What the author wrote |
|---|---|---|---|
| introduced | `abc1234` / #12 | 2025-03-02 | "…" |
| changed | … | … | … |
| current | … | … | … |

## 3. Quote, then label

- Quote what the authors wrote. Put your own reading in a separate line marked
  `inferred`.
- Never present a guess from the code's shape as the reason. If no author
  explained it, say the record does not say.
- End with **What the record does not answer** and who or where could.

## Refusals

- Do not edit files, commit, or post comments or reviews. This skill is read-only.
- Do not state a reason that no commit, PR, issue, or note gives.
- Do not rewrite history, check out old commits in the working tree, or run
  `git bisect` here; read history with `git show` and `git log`.

## Integration

**Pairs with:** `how` for what the code does today, and `recall` when the
reason may live in the user's own earlier sessions.

**Use instead of:** `how` for runtime behavior, `research-brief` for external
sources, and `recall` for the user's own session history.

**Reply:** the short answer with its confidence, the timeline with a commit or PR and date on every row, the inferences marked `inferred`, and what the record does not answer.
