---
name: plan-summary-quiz
description: Use when the user wants an explicit plan, PRD, requirements, specification, or design summary plus a comprehension quiz, including "plan 요약 퀴즈", "PRD 이해도 퀴즈", "설계문서 요약하고 퀴즈", "quiz me on this plan", "PRD summary quiz", "/plan-summary-quiz", or "$plan-summary-quiz". For a summary without a quiz use plan-summary; for Markdown only use plan-summary-md.
---

# Plan Summary Quiz

## Workflow

Before starting, read the bundled base workflow at `<skill-path>/references/plan-summary-workflow.md`. It is the authoritative `plan-summary` body. Follow its explicit-file collector, untrusted-document boundary, evidence analysis, bilingual alignment, report contract, generation, browser-open attempt, failure handling, and factual handoff without weakening them.

Add an aligned `## Quiz` as the final level-two section in both reports before invoking the same bilingual generator.

## Quiz Contract

- Author five questions by default. Use fewer only when the sources cannot support five distinct concepts without padding.
- Use unique sequential `QZ-*` headings beginning at `QZ-001`.
- Give every question 2 to 6 single-line task-list options with exactly one `- [x]` answer.
- End every question with exactly one non-empty `**Explanation:**` tied to a `PS-*` card or source evidence.
- Keep the same IDs, order, option counts, and same correct-option index in Korean and English.
- Test goals, scope, decisions, flows, dependencies, risks, or acceptance criteria. Avoid line-count trivia and trick questions.

The generated HTML makes every option an accessible button. One choice reveals the correct answer and explanation, disables that question, and exposes the answer key when printed. It performs no network request and stores no quiz answer state.

Require two validated Markdown files, one self-contained bilingual HTML file, and a browser-open attempt. Include the question count in the factual handoff without repeating quiz prose.

This exact selector includes synchronized copies of the reference, collector, generator, and template so standalone installation remains executable.
