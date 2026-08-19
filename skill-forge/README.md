# skill-forge

[한국어](README.ko.md) · [← back to main](../README.md)

Author skill packages against one contract, and prove every packaged skill still
satisfies it. `skill-forge` writes the package; `skill-audit` checks it.

## Why it is different

A skill is easy to start and easy to leave half-finished. The `SKILL.md` reads
well, and then the Codex descriptor is missing, the slash command was never
added, the website catalog still lists the old name, and one locale describes a
capability the skill does not have.

This plugin makes that state detectable. Nine rules cover naming, the invocation
grammar, the Codex descriptor, the slash command, evals, catalog and locale
parity, the plugin manifest, and the counts published in the root documentation.
[`skill-package-contract.md`](skills/skill-forge/references/skill-package-contract.md)
states them; [`audit_skills.py`](skills/skill-audit/scripts/audit_skills.py) is
their executable form and exits non-zero, so it works as a merge gate.

## Installation

Global:

```bash
npx skills add -y -g chann/skills --skill skill-forge --skill skill-audit
```

Project-local:

```bash
npx skills add chann/skills --skill skill-forge --skill skill-audit
```

## Usage

| Claude Code | Codex | Action |
|---|---|---|
| `/skill-forge [request]` | `$skill-forge [request]` | Create or repair a skill package, then publish and prove it |
| `/skill-audit [skill or path]` | `$skill-audit [skill or path]` | Report every packaged skill that violates the contract |

Examples:

```text
/skill-forge add a skill that turns a failing CI run into a triage note
$skill-forge rename gen-docs to project-docs
/skill-audit
$skill-audit diff-summary
```

Run the auditor directly when you want it in CI:

```bash
python3 skill-forge/skills/skill-audit/scripts/audit_skills.py --root .
python3 skill-forge/skills/skill-audit/scripts/audit_skills.py --format markdown
```

## The contract

| Rule | What it holds |
|---|---|
| C1 | Directory, path, and frontmatter name agree |
| C2 | The description opens correctly, names real triggers, and carries both selectors |
| C3 | `Use only when` and `disable-model-invocation: true` imply each other |
| C4 | The Codex descriptor is complete and invokes `$name` |
| C5 | A slash command exists with a description |
| C6 | Evals ship with at least three cases and two assertions each |
| C7 | The website catalog and all four locales carry the skill |
| C8 | The plugin manifest has a name, description, and version |
| C9 | Root documentation publishes the same counts as the tree |

## Package layout

```text
skill-forge/
├── .claude-plugin/plugin.json
├── commands/skill-forge.md
├── commands/skill-audit.md
├── skills/skill-forge/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── evals/evals.json
│   └── references/
│       ├── skill-package-contract.md
│       └── description-grammar.md
├── skills/skill-audit/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── evals/evals.json
│   └── scripts/audit_skills.py
├── README.md
└── README.ko.md
```

## Requirements

- An agent platform that supports skills
- `python3` for the auditor (standard library only)

## License

MIT
