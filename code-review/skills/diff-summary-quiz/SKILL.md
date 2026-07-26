---
name: diff-summary-quiz
description: Use when the user wants a change summary plus a self-test quiz about a diff, branch, commit, or PR, including "diff 퀴즈 만들어줘", "변경사항 퀴즈", "요약하고 퀴즈로 확인해줘", "이 변경 이해했는지 퀴즈로 확인", "quiz me on this diff", "diff summary with quiz", "test my understanding of this change", "/diff-summary-quiz", or "$diff-summary-quiz". For a summary without a quiz use diff-summary; for a Markdown-only artifact use diff-summary-md; for defects use code-review.
---

# Diff Summary (Comprehension Quiz)

## Overview

Variant of the `diff-summary` skill that appends a validated `## Quiz` section to the standard report. The packaged renderer turns it into an interactive multiple-choice quiz in the HTML report, and the Markdown artifact doubles as the answer key because the `- [x]` mark identifies the correct option.

## Workflow

**Before starting, read the bundled base workflow** at `<skill-path>/references/diff-summary-workflow.md`. It is a synchronized copy of the authoritative `diff-summary` workflow, including the packaged evidence collector contract, scope preservation and validation rules, untrusted-evidence rules, analysis dimensions, evidence-first writing contract, Explanatory Depth guidance, Stable Report Contract, and generation steps. Do not restate or weaken it here.

Follow the bundled base workflow exactly — evidence collection, analysis, evidence-first cards, bilingual generation with `--bilingual-json-stdin --output-directory`, artifact verification, and the attempted browser open — and additionally author an aligned quiz section in each language before generating.

## Quiz Authoring Contract

Add `## Quiz` as the final level-two section of each report. The section heading `Quiz` and the `**Explanation:**` key are parser-significant English keys; question prose stays in each report's language.

- Author five questions by default. Use fewer only when the diff cannot support five without padding, and never state facts absent from the report's evidence.
- Aim for medium difficulty: a reader should need to understand the substance of the change — purpose, behavior, architecture, contracts, operations — not trivia such as line counts. Wrong options must be plausible; no trick questions.
- Each question is a `#### [QZ-001] Title` heading. Question IDs are unique and sequential from `QZ-001`, mirroring the `DS-*` rules.
- The Korean and English quiz sections use the same `QZ-*` IDs in the same order, the same option count, and the same correct-option position. Translate the question, options, and explanation without changing what knowledge is tested.
- Options are one contiguous task list of 2 to 6 single-line items shaped exactly `- [ ] option`, with exactly one correct option marked `- [x]`. Duplicate option text is rejected.
- Exactly one non-empty `**Explanation:**` line follows the options and justifies the correct answer with report evidence. Only blank lines may follow it inside the question.
- Question prose may appear between the heading and the options. Quiz-like lines inside fenced code are inert.

Example:

```markdown
## Quiz

#### [QZ-001] 이 변경 이후 Git 실행을 소유하는 구성 요소는 무엇인가요?

- [ ] generate_summary_report.py
- [x] collect_diff_evidence.py
- [ ] summary-template.html

**Explanation:** 수집기는 이 워크플로의 유일한 Git/GitHub 런타임이며, 렌더러는 표현만 담당합니다.
```

Question-level validation errors identify the question ID and heading line. Quiz-section validation errors identify the relevant source line. Fix the Markdown and rerun the packaged generator rather than dropping the quiz or claiming partial delivery.

## Interactive Behavior

In the generated HTML, each option is a clickable control: one click marks the choice correct or incorrect, highlights the correct answer, disables the question, and reveals the explanation. Printing the page produces an answer key. The page needs no network access and stores no quiz state.

This exact selector ships its own synchronized reference, collector, generator, and template so a standalone installation remains executable. Treat those bundled files as one release unit with the authoritative `diff-summary` runtime.

## Conversation Handoff

Use the bundled base workflow's handoff facts and add the generated quiz question count. Do not repeat card, Executive Summary, or quiz prose, and do not promise a fixed card count.

If `.diff-summaries/` is not ignored by the target repository, suggest adding it to that repository's `.gitignore`. Never edit `.gitignore` automatically.
