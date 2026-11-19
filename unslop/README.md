# unslop

[한국어](README.ko.md) · [← back to main](../README.md)

Rewrite AI-written Korean or English text so it reads like a person wrote it.
In Korean the skill replaces AI-flavored jargon (계약(contract), 엔벨로프(envelope),
패리티(parity), leaked framework vocabulary like "열린 노드가 없습니다") and
smooths translation-ese rhythm. In English it removes the usual tells: filler
openers, inflated vocabulary, "not just X but Y", forced lists of three, and
dash and bold overuse. It never changes what the text says.

> **Renamed from `human-friendly-writing`**, which handled Korean only. The
> Korean behavior is unchanged; English rules are new.

## What it never changes

- Facts, claims, numbers, dates, proper nouns, code identifiers, quotes, links
- Established technical terms on the keep lists (API, 토큰, 프롬프트, 커밋,
  멱등, latency, cache, …)
- Sentences that already sound natural: no over-editing
- The language of any passage: it never translates
- Source files: a file input is rewritten to a sibling file, never overwritten

Unlisted Korean terms are replaced only when a three-part judgment test passes:
the word is a literal translation or one-off transliteration of an English
concept word, practitioners would not actually say it, and a natural
replacement preserves the exact meaning. Any doubt keeps the original term.

## How it picks rules

Language is detected per passage. Korean sentences get the Korean lexicon and
style rules; English sentences get a numbered rule list (`E1`–`E21`) whose ids
stay stable so other skills and replies can cite them. Mixed text is handled
sentence by sentence.

## Installation

Global:

```bash
npx skills add -y -g chann/skills --skill unslop
```

Project-local:

```bash
npx skills add chann/skills --skill unslop
```

## Usage

| Claude Code | Codex | Action |
|---|---|---|
| `/unslop [text-or-file]` | `$unslop [text-or-file]` | Rewrite AI-written Korean or English text into natural prose without changing meaning |

Examples:

```text
/unslop docs/release-note.ko.md
$unslop 이 테스트는 응답 엔벨로프의 계약을 고정한다
$unslop unslop this README intro
```

Also triggers on phrases like *"AI 용어 없애줘"*, *"사람답게 다듬어줘"*,
*"make this sound human"*, and *"remove the AI tells"*. With no argument, the
skill rewrites the text already under discussion. The reply is the rewritten
text plus a short plain-language list of what kind of change was made, with rule
ids when asked.

## Package layout

```text
unslop/
├── .claude-plugin/plugin.json
├── commands/unslop.md
├── skills/unslop/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── evals/evals.json
│   └── references/
│       ├── english-rules.md
│       ├── slop-lexicon.md
│       └── style-rules.md
├── README.md
└── README.ko.md
```

## Requirements

- An agent platform that supports skills
- Korean or English source text (other languages are out of scope)

## License

MIT
