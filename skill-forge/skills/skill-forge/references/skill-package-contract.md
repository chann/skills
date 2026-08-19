# Skill Package Contract

Every packaged skill in this repository obeys the same nine rules. They exist so
a user can predict how any skill is invoked, what it ships, and where it is
documented, without reading its source. `skill-audit` is the executable form of
this document; when the two disagree, fix both in the same change.

A **plugin** is a top-level directory with `.claude-plugin/plugin.json`. A
**skill** is a directory under `<plugin>/skills/`. A plugin may own many skills.

## C1 — Names agree

A skill lives at `<plugin>/skills/<name>/SKILL.md`, and its frontmatter `name`
equals the directory name. The name is the selector: `/<name>` in Claude Code,
`$<name>` in Codex. Use lowercase kebab-case.

## C2 — Description grammar

`description` is one paragraph, at most 1024 characters, that:

- opens with `Use when` or `Use only when`;
- names at least one natural-language trigger a user would actually type;
- contains both the `/<name>` and `$<name>` selector tokens; and
- disambiguates from sibling skills when a near neighbour exists
  (`For a Markdown-only artifact use diff-summary-md`).

The description is the only text the model sees before deciding to load the
skill. `references/description-grammar.md` covers how to write one that fires on
the right requests and stays quiet on the wrong ones.

## C3 — Invocation mode is declared

The opening clause and the frontmatter flag must agree:

| Opening | `disable-model-invocation` | Meaning |
|---|---|---|
| `Use when` | omitted | The model may choose this skill from the user's phrasing. |
| `Use only when` | `true` | The skill runs on its explicit selector and nothing else. |

Reserve `Use only when` for selector aliases and workflows that must never start
on their own. A skill that accepts any natural-language trigger is `Use when`,
even when that trigger requires an explicit request.

## C4 — Codex descriptor

`skills/<name>/agents/openai.yaml` publishes the Codex interface:

```yaml
interface:
  display_name: "Title Case Name"
  short_description: "One line, at most 90 characters, no trailing period"
  default_prompt: "Use $<name> to ..."
```

`default_prompt` must contain `$<name>`; it is what a user runs when they pick
the skill from a list with no other context.

## C5 — Slash command

`<plugin>/commands/<name>.md` exists with a `description` in its frontmatter,
and adds `argument-hint` when the skill takes an argument. The body tells the
agent which skill to use and restates the constraints that must survive the
command layer. A command file may be a selector alias for another skill; when it
is, it names that skill in its first line.

## C6 — Evals

`skills/<name>/evals/evals.json` ships with the skill:

```json
{
  "skill_name": "<name>",
  "evals": [
    {
      "id": 1,
      "prompt": "what a user would type",
      "expected_output": "what a correct run produces",
      "files": [],
      "assertions": ["one checkable behavior", "another checkable behavior"]
    }
  ]
}
```

At least three evals, each with at least two assertions. Write assertions about
behavior that would break if the skill were followed sloppily — the gates,
refusals, and orderings — not about prose the model happens to emit. Cover the
happy path, one boundary or refusal case, and one case where a sibling skill
would be the wrong choice.

## C7 — Catalog and locales

The name appears in `website/src/data/skills.ts`, either as a catalog `id` or in
another skill's `aliases`. Every catalog id has `summary`, `whenToUse`, and
`result` in all four locale files: `ko`, `en`, `jp`, `cn`.

Translate presentation copy. Never let a locale describe a capability or an
invocation rule the skill does not have.

## C8 — Plugin manifest

`<plugin>/.claude-plugin/plugin.json` carries `name` (equal to the directory),
`description`, and `version`. Bump the version when the plugin's skills change
behavior.

## C9 — Published counts

Root `README.md`, `README.ko.md`, `USAGE.md`, and `ARCHITECTURE.md` publish the
same two numbers as the tree:

- **workflows** — catalog ids in `website/src/data/skills.ts`;
- **selectors** — `SKILL.md` files under `*/skills/*/`.

Selector aliases raise the selector count without raising the workflow count.
`website/scripts/verify-catalog.mjs` and
`website/scripts/generate-social-cards.mjs` carry the same numbers.

## Running the audit

```bash
python3 skill-forge/skills/skill-audit/scripts/audit_skills.py --root .
python3 skill-forge/skills/skill-audit/scripts/audit_skills.py --skill diff-summary
python3 skill-forge/skills/skill-audit/scripts/audit_skills.py --format markdown
```

The script exits non-zero when any rule fails, so it works as a pre-merge gate.
`tests/test_skill_contract.py` runs it over this repository.
