---
name: unslop
description: Use when AI-written text needs to read like a person wrote it. Korean text with AI-flavored jargon such as 계약(contract), 엔벨로프(envelope), 패리티(parity), leaked framework vocabulary like "열린 노드가 없습니다", or translation-ese rhythm; English text with filler openers, inflated vocabulary, "not just X but Y", forced lists of three, or dash and bold overuse. Trigger on "AI 용어 없애줘", "사람답게 다듬어줘", "AI 슬롭 제거", "자연스러운 한국어로 윤문해줘", "unslop this", "make this sound human", "remove the AI tells", "/unslop", or "$unslop". Returns the rewritten text and a short note on what kind of change was made. Not a spell-checker, not a translator, never changes content.
---

# Unslop

Rewrite AI-written text so it reads like a fluent person wrote it. One pass
replaces AI-flavored vocabulary, a second smooths AI-typical style. The meaning
never moves.

## Hard rules

- Never add, remove, or reorder facts, claims, numbers, dates, proper nouns,
  code identifiers, commands, quotes, or links.
- Established technical terms are never replaced. The Korean keep list in
  [`references/slop-lexicon.md`](references/slop-lexicon.md) — API, 토큰,
  프롬프트, 커밋, 멱등 and the rest — and the English keep list in
  [`references/english-rules.md`](references/english-rules.md) both apply.
  Replacing one is a defect, not an improvement.
- When unsure whether a term is slop, keep the term and mention it in the
  final reply.
- No over-editing: a sentence that already sounds natural stays exactly as it
  was. If you cannot say why a change helps, do not make it.
- Never translate. Korean stays Korean and English stays English, including
  inside mixed text.
- Never overwrite a source file. When the input was a file, save the rewrite as
  a sibling file (for example `notes.md` → `notes.unslop.md`).

## Choose the rules per passage

Detect the language of each passage — a sentence, bullet, or paragraph — not of
the whole document.

| Passage | Rules |
| --- | --- |
| Korean | [`references/slop-lexicon.md`](references/slop-lexicon.md) and [`references/style-rules.md`](references/style-rules.md) |
| English | [`references/english-rules.md`](references/english-rules.md) |
| Mixed | Each sentence gets its own language's rules; a Korean sentence with an English term keeps the term if it is on the keep list |
| Neither, or code | Leave it exactly as it is |

## Workflow

1. Read the entire text once before editing anything.
2. For Korean passages, scan for slop vocabulary with the lexicon — listed terms
   plus unlisted ones caught by the three-part test below. For English passages,
   scan for the rule patterns in `english-rules.md`.
3. Rewrite the affected sentences, then apply the style rules for that language
   to the whole passage.
4. Long input (over roughly 4,000 characters): run steps 2–3 as two separate
   passes — vocabulary first, then style.
5. Run the self-check at the end of `style-rules.md` (Korean) or
   `english-rules.md` (English).

## The three-part test for unlisted Korean terms

Replace a term only when all three hold:

1. It is a literal translation or one-off transliteration of an English
   concept word — 계약 ← contract, 엔벨로프 ← envelope, 패리티 ← parity.
2. A Korean practitioner in that field would not say it in conversation or
   write it in a blog post.
3. A natural everyday replacement exists that preserves the exact meaning.

Any doubt on any of the three → keep the term and mention it in the reply.

## Never leak method vocabulary

Internal framework words from a writing or review process — 렌즈, 노드, 리프,
프런티어, 게이트, 감사, 마감 기록, 아티팩트, and in English lens, node, gate,
frontier, artifact when used as process metaphors — must not appear in text
addressed to readers who never adopted that vocabulary. Translate the method's
metaphors into the reader's language.

전: 모든 렌즈 감사가 끝났고, 열린 노드가 없습니다. 마감 기록을 제시합니다.
후: 확인할 항목은 모두 살펴봤고, 남은 결정도 없습니다. 정리한 결과는 아래와
같습니다.

Every 전/후 pair in this skill shows a direction, not a fixed phrase — fit the
replacement to the surrounding sentences instead of copying it verbatim.

This rule binds the skill's own replies too: report what changed in plain
language, never in this skill's internal terms.

## Out of scope

- Spelling-and-grammar-only proofreading, translation between languages, and
  rewrites that add or drop content are different tasks.
- Languages other than Korean and English.

**Reply:** the rewritten text, in the language of each passage, followed by a
short plain-language list of what kind of change was made (for example
"vocabulary in six places, rhythm in three"), written in the user's language;
add the rule ids from `english-rules.md` only when the user asks for them. If
the text was already fine, say so and change almost nothing.
