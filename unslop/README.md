# human-friendly-writing

[한국어](README.ko.md) · [← back to main](../README.md)

Rewrite AI-written Korean text into natural, human-sounding prose. The skill
replaces AI-flavored jargon — 계약(contract), 엔벨로프(envelope),
패리티(parity), leaked framework vocabulary like "열린 노드가 없습니다" — and
smooths translation-ese rhythm, without changing what the text says.

## What it never changes

- Facts, claims, numbers, dates, proper nouns, code identifiers, quotes, links
- Established technical terms on the keep list (API, 토큰, 프롬프트, 커밋,
  멱등, …)
- Sentences that already sound natural — no over-editing
- Source files: a file input is rewritten to a sibling file, never overwritten

Unlisted terms are replaced only when a three-part judgment test passes:
the word is a literal translation or one-off transliteration of an English
concept word, practitioners would not actually say it, and a natural
replacement preserves the exact meaning. Any doubt keeps the original term.

## Installation

Global:

```bash
npx skills add -y -g chann/skills --skill human-friendly-writing
```

Project-local:

```bash
npx skills add chann/skills --skill human-friendly-writing
```

## Usage

| Claude Code | Codex | Action |
|---|---|---|
| `/human-friendly-writing [text-or-file]` | `$human-friendly-writing [text-or-file]` | Rewrite AI-written Korean text into natural prose without changing meaning |

Examples:

```text
/human-friendly-writing docs/release-note.ko.md
$human-friendly-writing 이 테스트는 응답 엔벨로프의 계약을 고정한다
```

Also triggers on phrases like *"AI 용어 없애줘"*, *"사람답게 다듬어줘"*, and
*"자연스러운 한국어로 윤문해줘"*. With no argument, the skill rewrites the
Korean text already under discussion. The reply is the rewritten text plus a
short plain-language note on what changed.

## Package layout

```text
human-friendly-writing/
├── .claude-plugin/plugin.json
├── commands/human-friendly-writing.md
├── skills/human-friendly-writing/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── slop-lexicon.md
│       └── style-rules.md
├── README.md
└── README.ko.md
```

## Requirements

- An agent platform that supports skills
- Korean source text (other languages are out of scope)

## License

MIT
