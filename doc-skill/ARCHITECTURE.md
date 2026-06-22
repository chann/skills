# doc-skill Architecture

## Overview

`doc-skill` is a Claude Code plugin wrapper around one portable skill, `gen-docs`. The skill does not ship a generator binary in v1. It gives an agent a deterministic process for analyzing a project, building a documentation model, rendering four standard Markdown files, and merging them without clobbering human prose.

## Components

| Component | Responsibility |
|---|---|
| `.claude-plugin/plugin.json` | Declares the installable plugin name, description, and version |
| `commands/gen-docs.md` | Routes `/gen-docs` invocations to the `gen-docs` skill and resolves the target root |
| `skills/gen-docs/SKILL.md` | Defines the workflow, document contracts, update-in-place merge rules, and safety boundaries |
| `skills/gen-docs/templates/` | Stores canonical section order for the four target documents |
| `README.md` / `README.ko.md` | Front-door docs for the plugin itself |
| `ARCHITECTURE.md` / `USAGE.md` | Dogfooded deeper docs for this plugin |

## Data flow

1. The user invokes `/gen-docs` with an optional project root.
2. The command activates `gen-docs`.
3. `gen-docs` reads project manifests, existing docs, top-level structure, license, CI files, and remote metadata.
4. For larger projects, the main agent dispatches parallel Explore subagents for components, entrypoints, configuration, and examples. For small projects it performs the same probes inline.
5. The agent synthesizes one project model.
6. Templates produce candidate `README.md`, `README.ko.md`, `ARCHITECTURE.md`, and `USAGE.md`.
7. Existing docs are merged by heading with keep-marker support.
8. The agent shows diffs and writes only confirmed files.

## Directory structure

```
doc-skill/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   └── gen-docs.md
├── skills/
│   └── gen-docs/
│       ├── SKILL.md
│       └── templates/
│           ├── ARCHITECTURE.md.tmpl
│           ├── README.ko.md.tmpl
│           ├── README.md.tmpl
│           └── USAGE.md.tmpl
├── ARCHITECTURE.md
├── README.ko.md
├── README.md
└── USAGE.md
```

## Design decisions

- **Process skill, not generator script:** v1 optimizes agent behavior and safety. A runtime generator can be added later if repeated manual steps become mechanical.
- **README as front door:** deep reference content belongs in `USAGE.md` and `ARCHITECTURE.md`, keeping README scannable.
- **Only README is bilingual:** `README.ko.md` mirrors `README.md`; architecture and usage remain English-only for v1.
- **Diff-confirmed writes:** generated docs are still user-facing product text, so the skill requires reviewable diffs before writing.
- **Preserve unknown prose:** the update-in-place merge protects hand-written sections and supports `<!-- doc-skill:keep -->` for explicit freezes.
