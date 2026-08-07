---
name: human-friendly-writing
description: Use when AI-written Korean text needs to read like a person wrote it — it contains AI-flavored jargon such as 계약(contract), 엔벨로프(envelope), 패리티(parity), leaked framework vocabulary like "열린 노드가 없습니다", or translation-ese rhythm. Trigger on "AI 용어 없애줘", "사람답게 다듬어줘", "AI 슬롭 제거", "자연스러운 한국어로 윤문해줘", "/human-friendly-writing", or "$human-friendly-writing". Korean text only; not a spell-checker, not a translator, never changes content.
---

# Human Friendly Writing

Rewrite AI-written Korean text so it reads like a fluent person wrote it.
Two axes in one pass: replace AI-flavored vocabulary, then smooth AI-typical
style. The meaning never moves.

## Hard rules

- Never add, remove, or reorder facts, claims, numbers, dates, proper nouns,
  code identifiers, commands, quotes, or links.
- Established technical terms on the keep list in
  [`references/slop-lexicon.md`](references/slop-lexicon.md) — API, 토큰,
  프롬프트, 커밋, 멱등 and the rest — are never replaced. Replacing one is a
  defect, not an improvement.
- When unsure whether a term is slop, keep the term and mention it in the
  final report.
- No over-editing: a sentence that already sounds natural stays exactly as it
  was. If you cannot say why a change helps, do not make it.
- Never overwrite a source file. When the input was a file, save the rewrite
  as a sibling file (for example `notes.md` → `notes.human.md`).

## Workflow

1. Read the entire text once before editing anything.
2. Scan for slop vocabulary with
   [`references/slop-lexicon.md`](references/slop-lexicon.md) — listed terms
   plus unlisted ones caught by the three-part test below.
3. Rewrite the affected sentences, then apply
   [`references/style-rules.md`](references/style-rules.md) to the whole text.
4. Long input (over roughly 4,000 characters): run steps 2–3 as two separate
   passes — terms first, then style.
5. Run the self-check checklist at the end of `style-rules.md`.
6. Reply with the rewritten text plus two or three plain sentences about what
   changed — "용어 여섯 곳과 문장 리듬 세 곳을 손봤습니다" 수준이면 충분하다.
   If the text was already fine, say so and change almost nothing.

## The three-part test for unlisted terms

Replace a term only when all three hold:

1. It is a literal translation or one-off transliteration of an English
   concept word — 계약 ← contract, 엔벨로프 ← envelope, 패리티 ← parity.
2. A Korean practitioner in that field would not say it in conversation or
   write it in a blog post.
3. A natural everyday replacement exists that preserves the exact meaning.

Any doubt on any of the three → keep the term and mention it in the report.

## Never leak method vocabulary

Internal framework words from a writing or review process — 렌즈, 노드, 리프,
프런티어, 게이트, 감사, 마감 기록, 아티팩트 — must not appear in text addressed
to readers who never adopted that vocabulary. Translate the method's metaphors
into the reader's language.

전: 모든 렌즈 감사가 끝났고, 열린 노드가 없습니다. 마감 기록을 제시합니다.
후: 확인할 항목은 모두 살펴봤고, 남은 결정도 없습니다. 정리한 결과는 아래와
같습니다.

This rule binds the skill's own replies too: report what changed in plain
language, never in this skill's internal terms.

## Out of scope

- Spelling-and-grammar-only proofreading, translation, and rewrites that add
  or drop content are different tasks.
- Non-Korean source text.
