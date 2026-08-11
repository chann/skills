# build-reinstall

[한국어](README.ko.md) · [← back to main](../README.md)

Build the current project, reinstall the newly built local app or CLI with the
project's own commands, and verify that the installed copy matches the build.
The workflow is explicit-only: finishing another task never triggers it
automatically.

## Installation

Global:

```bash
npx skills add -y -g chann/skills --skill build-reinstall
```

Project-local:

```bash
npx skills add chann/skills --skill build-reinstall
```

## Usage

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/build-reinstall [project-root]` | `$build-reinstall [project-root]` | Build, reinstall, and verify the installed result |

If no project root is supplied, the current repository is used. The skill
reads project instructions and scripts before it chooses commands, shows the
complete plan, and then runs six stages: preflight, build, output resolution,
reinstall, installed-result verification, and reporting.

## Optional project configuration

Projects with custom commands can copy the packaged example:

```bash
cp build-reinstall/skills/build-reinstall/references/build-reinstall.example.yaml \
  .build-reinstall.yaml
```

When the skill is installed, use its own
`references/build-reinstall.example.yaml` path instead. The version 1 file
defines the working directory, ordered build/reinstall/verify commands,
explicit install targets, and built/installed SHA-256 comparison pairs. The
file is optional when project documentation already provides unambiguous
commands and verification.

## Safety and proof

- Build failure leaves the installed copy untouched.
- Reinstall targets must come from project evidence or the YAML file.
- The skill does not add `sudo`, force flags, broad deletion, releases,
  deployments, commits, or pushes.
- Smoke checks and built/installed SHA-256 equality provide completion proof.
- Missing GUI, device, signing, notarization, or permission proof is reported
  separately rather than hidden behind source tests.

## Package layout

```text
build-reinstall/
├── .claude-plugin/plugin.json
├── commands/build-reinstall.md
├── skills/build-reinstall/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/build-reinstall.example.yaml
├── README.md
└── README.ko.md
```

## Requirements

- An agent platform that supports skills
- Project-owned build and reinstall commands
- A local install target that can be verified

## License

MIT
