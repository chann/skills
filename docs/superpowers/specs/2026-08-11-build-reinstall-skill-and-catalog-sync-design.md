# Build and reinstall skill with website sync — design

Date: 2026-08-11
Status: approved by the user

## Goals

1. Add an explicitly invoked `build-reinstall` skill that builds the current
   project, reinstalls the newly built result, and verifies the installed copy.
2. Expose the same workflow as `/build-reinstall` in Claude Code and
   `$build-reinstall` in Codex.
3. Publish the new workflow in the multilingual website catalog.
4. Add a root `AGENTS.md` rule so later skill additions, changes, and removals
   update the website and its checks in the same change.
5. Ship a copyable example `.build-reinstall.yaml` for projects that need an
   explicit workflow.

## Invocation and scope

The skill runs only after a user explicitly invokes `/build-reinstall` or
`$build-reinstall`. It does not run automatically when another task finishes,
and `AGENTS.md` does not turn it into a completion hook.

The workflow supports desktop apps, CLI tools, and other locally installed
software without assuming one framework. It discovers project-specific
commands from repository evidence and treats a project-owned
`.build-reinstall.yaml` as the highest-priority optional configuration.

The skill builds and reinstalls only. It does not commit, push, publish a
release, deploy a service, change versions, or rewrite project configuration
unless the user separately requests that work.

## Package structure

Create one repository plugin named `build-reinstall` using the existing package
layout:

```text
build-reinstall/
├── .claude-plugin/plugin.json
├── commands/build-reinstall.md
├── README.md
├── README.ko.md
└── skills/build-reinstall/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/build-reinstall.example.yaml
```

The Claude command is a thin selector that routes to the packaged skill. Codex
reads the same `SKILL.md`; `agents/openai.yaml` provides the display name,
short description, and a default prompt containing `$build-reinstall`.

No executable helper is needed. Choosing and running project commands requires
repository context and agent judgment, while a framework detector would be
brittle and would duplicate project-owned build logic.

## Workflow discovery

Resolve the repository root and inspect evidence in this order:

1. `.build-reinstall.yaml` at the repository root.
2. Applicable `AGENTS.md` and `CLAUDE.md` instructions.
3. Project documentation such as `README.md`, `USAGE.md`, and contributor docs.
4. Declared commands in `package.json`, Makefiles, task runners, Xcode/Tauri
   configuration, Cargo metadata, and project scripts.
5. Existing CI, packaging, and smoke-test workflows as supporting evidence.

Do not invent commands from a framework name alone. When two sources conflict,
prefer the more specific project instruction. If the build command, install
target, or verification method remains ambiguous, stop and ask the user before
changing the installed copy.

Before execution, show a compact plan containing:

- repository root and working directory;
- exact build commands;
- exact reinstall commands and target paths;
- exact verification commands and artifact comparisons;
- any unavailable proof or expected permission boundary.

The explicit invocation authorizes the displayed build and reinstall plan. It
does not authorize `sudo`, a release, deployment, broad deletion, or commands
outside the current project and resolved install target.

## Optional YAML configuration

The packaged reference file is named `build-reinstall.example.yaml`. Users can
copy it to `<repository-root>/.build-reinstall.yaml` and replace the example
values. Version 1 has this shape:

```yaml
version: 1
working_directory: "."

build:
  commands:
    - "pnpm build"

reinstall:
  commands:
    - "pnpm install:app"
  targets:
    - "/Applications/Example.app"

verify:
  commands:
    - "pnpm smoke:app"
  artifacts:
    - built: "src-tauri/target/release/bundle/macos/Example.app/Contents/MacOS/Example"
      installed: "/Applications/Example.app/Contents/MacOS/Example"
      compare: "sha256"
```

Rules:

- `version` must be `1`.
- `working_directory` is relative to the repository root and must stay inside
  it. The default is `.`.
- `build.commands`, `reinstall.commands`, and `verify.commands` preserve order.
- `reinstall.targets` lists every path that the reinstall commands may replace.
- `verify.artifacts` pairs a built result with its installed copy. Version 1
  supports `sha256` comparison.
- Unknown keys are not silently interpreted. Report them and ask before
  continuing if they could affect execution.
- Display all resolved values before running commands. Never interpolate
  untrusted repository text into a second command.
- The example contains no real project name, secret, credential, or privileged
  command.

The YAML file is optional. Projects whose documented scripts already provide a
clear build, reinstall, and verification path do not need it.

## Build, reinstall, and verification sequence

1. **Preflight:** confirm the project root, read applicable instructions, record
   the current installed target when one exists, and reject unresolved paths or
   privilege requirements.
2. **Build:** run the configured or discovered build commands. Stop on the first
   failure and leave the installed copy untouched.
3. **Resolve output:** prove that the expected build result exists and was
   produced by the successful build. Do not reinstall a stale or missing
   output.
4. **Reinstall:** run only the displayed project-owned reinstall commands. Do
   not add `sudo`, force flags, broad recursive deletion, or guessed cleanup.
5. **Verify:** run configured smoke checks and compare each declared built and
   installed artifact with SHA-256. For bundles or directories, compare the
   declared executable or another stable file rather than directory metadata.
6. **Report:** list commands and results, installed targets, comparison proof,
   and any verification that could not be performed.

A successful build does not prove a successful reinstall. A successful install
command does not prove that the installed result matches the new build. The
skill reports success only when the configured verification passes; otherwise
it reports the exact incomplete or failed evidence.

## Safety and failure handling

- Never use `sudo` or request elevated access unless the user explicitly
  authorizes the exact command after seeing why it is required.
- Never remove a broad path, user home, repository root, `/Applications`, or an
  unresolved variable or glob.
- Preserve unrelated installed applications, user data, caches, and settings.
- Stop before reinstalling when the target path is missing from evidence or
  differs from the displayed plan.
- Stop on build failure without changing the installed copy.
- Stop on reinstall failure and report whether the old installation still
  exists; do not claim an automatic rollback unless the project command proves
  one occurred.
- Treat smoke-test failure or artifact mismatch as a failed reinstall even when
  the installer exits successfully.
- Do not hide unavailable GUI, device, signing, notarization, or permission
  checks behind source-level tests.

## Website and repository documentation

Add `build-reinstall` to `website/src/data/skills.ts` under the automation
category with exact `/build-reinstall` and `$build-reinstall` selectors. Add
localized summary, use case, and result text to Korean, English, Japanese, and
Simplified Chinese content files.

Update all public workflow, selector, plugin, and category counts affected by
the new package. Update the repository README files, `USAGE.md`,
`ARCHITECTURE.md`, the website README, generated social-card copy and any tests
that intentionally pin those counts.

Create root `AGENTS.md` with a skill lifecycle rule:

- adding a packaged `*/skills/*/SKILL.md` requires a matching website catalog
  entry and all four locale entries;
- changing a skill's name, purpose, selectors, aliases, example, category, or
  user-visible behavior requires the matching website copy and metadata to be
  reviewed in the same change;
- removing a skill requires removing every website catalog and locale entry;
- pinned counts and public docs must be updated when totals change;
- run `npm --prefix website run verify:catalog`,
  `npm --prefix website run verify:locales`, and
  `npm --prefix website run build` before completion.

The existing catalog verifier remains the automated structural check. The
`AGENTS.md` rule covers semantic changes that cannot be derived safely from
`SKILL.md` prose.

## Verification

Add focused package tests that prove:

- required plugin, command, skill, metadata, README, and example YAML files
  exist;
- Claude and Codex selectors both route to the same skill;
- the YAML example has version 1 and all documented sections;
- the skill requires build success before reinstall, installed-artifact proof,
  explicit targets, and safe failure behavior;
- installation documentation uses the exact `build-reinstall` selector;
- website catalog and locale entries include the new workflow;
- `AGENTS.md` covers add, change, and removal paths plus required website checks.

Run the focused tests, the complete Python suite, the skill validator, the
website catalog and locale checks, the production website build, and
`git diff --check`. After each complete checkpoint, create a Conventional
Commit, push it normally, and prove local/upstream parity is `0 0`.

## Alternatives considered

### Mandatory project YAML

This would make execution predictable but would require configuration in every
repository, including projects that already expose clear build and install
scripts. The YAML therefore stays optional.

### Framework detection script

A detector could recognize Tauri, Xcode, Cargo, or npm, but a framework rarely
determines the project's real install target and smoke checks. Guessing here is
more dangerous than reading project-owned instructions, so version 1 does not
ship a detector.

### Automatic execution after every task

Automatic reinstall would turn an ordinary coding task into an implicit local
machine change. The user selected explicit invocation, so no hook or global
completion rule is added.
