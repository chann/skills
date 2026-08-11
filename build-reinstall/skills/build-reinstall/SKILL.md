---
name: build-reinstall
description: Build the current project, reinstall the newly built local app or CLI with project-owned commands, and verify that the installed copy matches the build. Use only when the user explicitly invokes /build-reinstall or $build-reinstall, or explicitly asks to build and reinstall after completing development work.
---

# Build and Reinstall

Build first, reinstall only the proven output, then verify the installed result.
Do not treat a successful build or install command as end-to-end proof.

Run this workflow only after an explicit request. Do not turn it into an
automatic completion hook.

## Discovery and configuration

Resolve the repository root before choosing commands. Use evidence in this
order:

1. `<repository-root>/.build-reinstall.yaml` when it exists.
2. Applicable `AGENTS.md` and `CLAUDE.md` files.
3. `README.md`, `USAGE.md`, contributor docs, and other project instructions.
4. Declared commands in `package.json`, Makefiles, task runners, project
   scripts, Cargo metadata, Xcode/Tauri configuration, and packaging files.
5. CI, packaging, and smoke workflows as supporting evidence.

Do not guess an install command or target from a framework name alone. Prefer
the most specific project-owned instruction when sources differ. If commands,
targets, or proof remain ambiguous, ask before changing the installed copy.

When `.build-reinstall.yaml` exists, require `version: 1`. Resolve
`working_directory` relative to the repository root and reject it if the
canonical path escapes that root. Preserve command order. Require every
replaced path under `reinstall.targets`, and support only `compare: "sha256"`
under `verify.artifacts`. Report unknown keys instead of inventing behavior.

Read [`references/build-reinstall.example.yaml`](references/build-reinstall.example.yaml)
when the user asks how to configure the workflow or when validating a project
configuration.

Before running anything, show:

- repository root and working directory;
- exact build commands;
- expected build outputs;
- exact reinstall commands and resolved target paths;
- smoke commands and built/installed artifact comparisons;
- required permissions and any proof that will remain unavailable.

The explicit invocation authorizes that displayed build and reinstall plan. It
does not authorize `sudo`, releases, deployments, version changes, commits,
pushes, force flags, broad recursive deletion, or commands outside the current
project and resolved install targets.

## 1. Preflight

Read all applicable instructions and configuration. Confirm that each command
comes from project evidence. Canonicalize the working directory, build-output
paths, and install targets without relying on unresolved variables, command
substitution, or globs.

Record whether every target exists and the evidence used to identify it. If an
install target is ambiguous, outside the displayed plan, or requires an
unapproved privilege boundary, stop before mutation. Never remove a repository
root, user home, `/Applications`, `/`, or another broad path.

## 2. Build

Run the displayed build commands in order from the resolved working directory.
Stop on the first non-zero exit. On build failure, report the failing command
and leave the installed copy untouched.

Do not clean, delete caches, change versions, fetch private dependencies, or
add flags unless project instructions or the user explicitly require them.

## 3. Resolve the build output

After every build command succeeds, prove that each expected output exists and
is the output selected by the project workflow. Record the built path, type,
size, modification time, version when available, and SHA-256 for each declared
file artifact.

Do not reinstall a missing, unresolved, or known-stale output. For an app
bundle or directory, use a stable declared executable or file for artifact
comparison; directory metadata is not binary equality proof.

## 4. Reinstall

Recheck every resolved target immediately before the change. Run only the
displayed project-owned reinstall commands, in order. Do not synthesize `sudo`,
force flags, broad recursive deletion, or guessed cleanup around them.

Stop on the first failure. Report whether the previous installed target still
exists. Do not claim rollback unless the project-owned installer proves that a
rollback completed.

## 5. Verify the installed result

Run every configured smoke command in order. For each `verify.artifacts` pair,
resolve the built and installed files, calculate SHA-256 independently, and
require the digests to match. Also record version and path evidence when the
project exposes them.

Treat a missing installed target, failed smoke check, or artifact mismatch as a
failed reinstall even when the install command returned zero. Source tests do
not replace installed-app proof. Keep unavailable GUI, device, signing,
notarization, and permission verification separate from checks that passed.

If project evidence defines no reliable installed-result check, say that the
reinstall is unverified. Do not report full success merely because no check was
available.

## 6. Report

Return a compact record with:

- build commands and outcomes;
- build outputs and SHA-256 values;
- reinstall commands and target paths;
- smoke results;
- built/installed artifact digest pairs;
- overall result: verified, failed, or unverified;
- exact missing proof and the safe next action when incomplete.

Do not commit, push, publish, deploy, or change project configuration unless the
user separately requested that action.
