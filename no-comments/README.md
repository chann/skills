# no-comments

[한국어](README.ko.md) · [← back to main](../README.md)

Remove comments that only narrate the code. A real constraint becomes a type,
a test, or a lint, and the comment goes with it.

## Why it is different

A comment review that also edits the code will delete the wrong line and call
it cleanup. This skill splits the two. The reviewer prompt in
`references/comment-review.md` reports. The parent applies only the findings
it accepts.

- A comment about an outside rule that cannot be checked is kept and marked
  for review.
- A rejected review does not abort accepted findings.
- The reviewer does not edit application code.

The review runs from that prompt, through a general subagent on Claude Code
or Codex, or inline when the host has no subagent tool.

## Installation

Global:

```bash
npx skills add -y -g chann/skills --skill no-comments
```

Project-local:

```bash
npx skills add chann/skills --skill no-comments
```

## Usage

| Claude Code | Codex | Action |
|---|---|---|
| `/no-comments [files or diff]` | `$no-comments [files or diff]` | Strip narration comments and encode a real constraint when you agree |

Examples:

```text
/no-comments strip the narration comments in this diff
$no-comments 이 파일 주석 정리해줘
/no-comments src/billing/invoice.py
```

With no argument the scope is the current diff against the default branch,
including the working tree. A read-only defect review is `interrogate`. Prose
that is not a code comment is `unslop`.

## What it refuses

- Deleting a kept comment about an outside rule that was not checked
- Letting a rejected finding discard the accepted ones
- Encoding a constraint you have not approved
- Editing application code inside the reviewer pass

## Package layout

```text
no-comments/
├── .claude-plugin/plugin.json
├── commands/no-comments.md
├── skills/no-comments/
│   ├── SKILL.md
│   ├── references/comment-review.md
│   ├── agents/openai.yaml
│   └── evals/evals.json
├── README.md
└── README.ko.md
```

## Requirements

- An agent platform that supports skills

## License

MIT
