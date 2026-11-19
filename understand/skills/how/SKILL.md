---
name: how
description: Use when the user asks how part of the codebase in front of them works or where something belongs, including "X 어떻게 동작해?", "이 서브시스템 구조 설명해줘", "이건 어디에 둬야 해?", "how does X work", "walk me through this subsystem", "where should this live", "which module owns this", "/how", or "$how". Reads the code without changing it and answers in a fixed shape — overview, key concepts, runtime flow, a file:line map, gotchas — with every claim cited and anything unread marked inferred. For motivation and history use why, for an external library or spec use research-brief, for a change use diff-summary, and for something broken use bug-hunt.
---

# How

Explain how the code in front of you works, from the code. The reader should
finish knowing what the thing is, how a request moves through it, where to edit
it, and what will bite them.

## 1. Pin the scope

State the question as you understand it in one line, then proceed. If the
scope is ambiguous, choose the narrowest reading that would still help and say
which one you chose; the user can redirect. Do not stop to ask.

## 2. Read, widest first

- Start with the entry points and the directory layout, then follow the call
  path of the question. Read the file before you describe it.
- For a large area, send one read-only explorer through the host's subagent tool
  when it has one, and keep only its conclusion with the `file:line` it cites.
  Check the two or three citations that carry the answer yourself. Without a
  subagent tool, read the area yourself.
- Prefer the code to its comments and docs when they disagree, and report the
  disagreement.

## 3. Answer in this shape

1. **Overview** — what it is and what it is for, in two or three sentences a
   senior engineer would say aloud.
2. **Key concepts** — the few terms and types the rest depends on, each with a
   one-line meaning and a `file:line`.
3. **How it works** — the runtime flow in order, one step per line, each step
   cited.
4. **Where things live** — a map of responsibility to `file:line`.
5. **Gotchas** — surprising coupling, hidden state, ordering requirements, and
   things that look changeable but are not.

## 4. Cite or label

- Every claim about the code carries `file:line`. A claim you did not read is
  labelled `inferred`, with the reason.
- Say what you did not read. A confident answer over unread code is the failure
  this skill exists to prevent.
- A placement or ownership question ("where should this live", "which module
  owns this") ends with a recommendation and the reason, citing the neighbouring
  code that sets the convention.

## Refusals

- Do not edit files, run formatters, or commit. This skill is read-only.
- Do not describe behavior from names alone. Read the body or mark it `inferred`.
- Do not explain why something was built that way from the code's shape; that
  is a guess, and `why` answers it from the record.

## Integration

**Pairs with:** `why` when the user then asks about motivation, and
`diff-summary` when the question is about one change.

**Use instead of:** `why` for motivation and history, `research-brief` for an
external library or spec, `diff-summary` for a change, and `bug-hunt` when
something is broken.

**Reply:** the five sections in order, every code claim cited as `file:line`, `inferred` marks where unread, and a closing line naming what was not read.
