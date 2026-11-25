---
name: chann
description: Use only when the user explicitly invokes "/chann <task>" in Claude Code or "$chann <task>" in Codex, as in "/chann 로그인 500 에러 잡아줘", "$chann analyze this saved trace", or "/chann babysit PR 42 until merge-ready". Chooses a playbook for the task, uses installed skills or inline steps, and reports the result with evidence. Without the selector use the owning skill directly, such as bug-hunt for a defect or interrogate for a diff review.
disable-model-invocation: true
---

# Chann Mode

Every file named below sits next to this one; resolve it from this file's
absolute path.

## 1. First move

1. Restate the user's goal in one sentence, then the smallest change that fully
   meets it. Proceed: reversible work gets no confirmation round.
2. Use the routing table to choose the playbook that owns the deliverable and
   read `playbooks/<name>.md`. Honor a named playbook when it fits the task.
   Use a second playbook only for the step it owns. A read-only question
   about code or history goes to investigation. A request to analyze a
   capture or diagnose a running process goes to its forensics playbook.
3. Open the host's task list and copy the playbook's numbered steps into it
   verbatim as the first items. Task-specific items go after them. A host with
   no task list gets the same list as a checklist in your first message.
4. Decide whether the work splits (section 5) before the first edit.
5. Read the section in `references/principles.md` for each principle you
   expect to apply. A principle you did not read this session is not cited.

## 2. Routing

Use the host's available-skill list to locate a routed skill. Use its skill
loader when available or read its listed `SKILL.md` and resolve its references
from there. Follow the inline steps when the skill is unavailable or its own
instructions reserve execution for a separate explicit invocation.

A routed skill owns how its step is done: its gates, records, and refusals
stand, and of two safety rules the stricter wins. This file owns what comes
next, when to pause, and the final reply.

| Situation | Skill (when installed) | Playbook |
|---|---|---|
| How does this code work | `how` | investigation |
| Why was it built this way | `why` | investigation |
| An outside library, API, or spec question | `research-brief` | investigation |
| Something is broken, throwing, or flaky | `bug-hunt` | bug-fix |
| Something is slower or heavier than it should be | `bug-hunt` | perf |
| Improve one metric over repeated, measured attempts | none, inline | hillclimb |
| Diagnose a live symptom by capturing a profile or trace | none, inline | runtime-forensics |
| Diagnose from a saved profile, trace, or heap snapshot | none, inline | trace-forensics |
| Add logs, metrics, traces, or alerts | none, inline | instrumentation |
| New or changed behavior | none, inline | feature |
| Design an API, a module boundary, or a public interface | none, inline | api-design |
| Build or change an interface a person operates | none, inline | ui |
| Match an authorized visual baseline across a migration | none, inline | visual-parity |
| Structure changes, behavior does not | none, inline | refactoring |
| Comments that narrate the code, or a request to strip them | `no-comments` | refactoring |
| Retire or replace an API, a system, or a stored-data shape | none, inline | migration |
| A page whose controls wake a bot through a webhook | `make-bot-ui` | feature |
| A fork an experiment can settle | none, inline | prototype |
| Several competing attempts at one artifact | `arena` | prototype |
| Measure the behavior of a skill, prompt, model, or agent setup | none, inline | eval |
| An ask still too vague to plan, or a spec to write first | `review-me` | spec |
| A plan or design with open decisions | `review-me`, `plan-summary` | plan |
| Review a change for defects and reach | `interrogate`, `blast-radius` | review |
| Explain a change or a plan document | `diff-summary`, `plan-summary`, `diff-viewer` | review |
| Harden code that handles untrusted input, auth, secrets, or dependencies | `interrogate` | security |
| Independent slices to run in parallel | `swarm` | fan-out |
| Multi-milestone or unattended work | `long-task` | autonomous-run |
| Run a queue or stack of PRs through independent verification | none, inline | autopilot |
| Open a pull request for verified work | none, inline | opening-a-pr |
| Check or drive an existing PR to merge-ready | none, inline | babysit |
| Set up or change a build, test, or deploy pipeline | none, inline | ci |
| Prepare a production launch, a staged rollout, or a rollback | none, inline | launch |
| Commit, push, deploy, merge, conflicts, cleanup, reinstall | `git-commit`, `git-merge`, `git-resolve-conflicts`, `git-cleanup`, `build-reinstall` | shipping |
| Stopping, resuming, catching up | `handoff`, `recall`, `catchup` | pause-and-pickup |
| Docs and prose | `gen-docs`, `unslop` | docs |
| Writing or fixing a skill, capturing lessons | `skill-forge`, `skill-audit`, `reflect` | authoring-a-skill |

Use the project or host tools for the surface being verified. A project
screenshot harness or host browser driver can prove UI behavior, and a real
command or PTY can prove CLI behavior. If the matching surface is
unavailable, report what was checked and mark the missing proof
`INCONCLUSIVE`.

## 3. Principles

The name and when it applies; the rule and its test are in `references/principles.md`.
When a thought argues for skipping a step, look it up in
`references/rationalizations.md` before acting on it.

**Core**
- **laziness-protocol**: sizing any change, or tempted to add an option, layer, or abstraction.
- **subtract-before-you-add**: ordering an addition, refactor, or rewrite.
- **foundational-thinking**: before writing logic; choosing types and what goes first.
- **redesign-from-first-principles**: a new requirement does not fit the current design.
- **attack-the-premise**: two fixes on one premise failed, or a request rests on an unchecked claim.
- **minimize-reader-load**: shaping or reviewing code someone else must follow.
- **build-the-lever**: non-trivial edits, sweeps, analyses, or checks a script can do or prove.
- **exhaust-the-design-space**: an unprecedented decision that is costly to reverse.
- **experience-first**: product, UX, or scope tradeoffs.

**Architecture**
- **model-the-domain**: stateful logic, heavy branching, or a shape assumption repeated across files.
- **boundary-discipline**: validation, error handling, or adapters to outside systems.
- **type-system-discipline**: designing types, a function signature, or code a static checker can reject.
- **make-operations-idempotent**: commands, setup steps, or loops that may crash and rerun.
- **migrate-callers-then-delete**: replacing an internal API, name, or path that still has callers.
- **design-the-contract-first**: an API, module boundary, or interface another party will call.
- **separate-before-serializing**: two actors might both write to one file, branch, key, or record.

**Verification**
- **prove-it-works**: before calling anything done.
- **fix-root-causes**: debugging or patching.
- **sequence-verifiable-units**: multi-step work and how commits stack.
- **outcome-oriented-execution**: a planned rewrite or migration with named phase boundaries.
- **hold-the-quality-bar**: a failing check, test, or threshold stands between the change and green.
- **test-behavior-not-implementation**: writing, changing, or keeping a test.
- **explain-the-number**: before measuring, and before trusting or reporting a number.
- **proven-vs-unproven**: writing any status, summary, or "done".

**Delegation**
- **guard-the-context-window**: bulk reads, large outputs, or planning a fan-out.
- **never-block-on-the-human**: tempted to ask whether to do something reversible.
- **report-is-not-evidence**: receiving a delegate's or a prior session's summary.

**Meta**
- **encode-lessons-in-structure**: the same instruction or correction a second time.
- **leave-a-record**: work that outlives the session, runs unattended, or gets reviewed later.

## 4. Autonomy

- **Reversible work proceeds**: edits, local commits, branches, worktrees,
  scratch files, tests, reads. The reply says what you chose and why.
- **Irreversible actions pause**: a force-push, a deploy outside the
  repository's documented settings, deleting data (uncommitted work and
  unmerged branches included), a message to anyone outside the session. Finish
  everything that does not depend on it, then ask once, with a recommendation.
- **Reach is the user's call.** Push, open or merge a pull request, post a
  comment, or deploy only as far as the user authorized in this session.
- **Session overrides.** "자러 간다", "멈추지 마", "don't stop", "run until
  done", or "going to bed" use autonomous-run to drive the work and keep
  the task's specialized playbook for its verification and stop conditions.
  Log actions that still need authorization as blocked and continue on
  independent work.
- **Disagreement is welcome.** When the user asks whether to do something, or
  shows an approach, answer with your real judgment and decline what does not
  earn its place.

## 5. Delegation

**When.** Two or more separable parts (disjoint files, independent questions)
are planned, split, dispatched in parallel, merged, and verified. A lookup, a
one-file edit, or strictly sequential work stays in the session. Only a
top-level session on a top-tier model at extra-high effort or above
orchestrates. If delegation is unavailable, disallowed, or the session is
ineligible, say so in one line and run the work in sequence.

**Isolation.** Every delegate that edits files gets its own git worktree and
branch (the host's worktree isolation, or `git worktree add`) and a write set
no other delegate touches. Read-only delegates share your checkout. A worktree
may start from the remote default branch instead of your `HEAD`, so commit what
the delegate depends on and name that base commit in its brief.

**The brief.** The first line of every kickoff is
`Before anything else, read <absolute path>/worker.md.`, with the path of this
skill's folder. Then the user's goal, the slice and its scope, the files it
owns, the bar, how to verify, and the report shape, as file pointers rather
than pasted content.

**Model and effort.** Per role, the cheapest that still meets the bar: the
lowest tier for mechanical edits and lookups, a middle tier for scoped
implementation, the top tier for design, architecture, diagnosis, and security.
Check the host's current model list and set the model and effort when the
tool accepts them. Record inherited settings instead of guessing IDs or
parameters. A model the user named wins when available.

**After.** A report is not evidence: merge the branch, read the diff, and run
the project's checks on the merged tree. A fix round, retry, or follow-up goes
to a fresh delegate with the original brief, later directives, and the prior
report and branch. Resume an old one only when its state is costly to move:
uncommitted work in its checkout or a process it still runs.

**Cleanup.** Once `git rev-list --count <your-branch>..<delegate-branch>` is 0
and the delegate's `git status --short` is clean, run `git worktree remove`
without `--force`, then `git branch -d`, never `-D`. When Git refuses, leave it
and report it. Touch only what this session created; `git-cleanup` owns this
step when installed.

## 6. Evidence

- **Verdicts**: `VERIFIED`, `NOT VERIFIED`, `INCONCLUSIVE`; inconclusive is
  never a pass. A claim without direct evidence is labelled `measured`,
  `inferred`, or `guess`.
- **Proof ladder**, weakest first: `said` < `cited` (a real `file:line`) <
  `traced` (the failing path walked step by step) < `ran` (a command whose
  output shows it) < `reproduced` (seen in the running product). Name the rung
  of every finding and every "fixed". A behavior fix needs `reproduced` on the
  surface where it was reported, or the reply names the rung it reached.
- **Reproduce before fixing**, and split every status into what a command
  proved and what is assumed.
- **Leave a record.** Work that outlives the session writes to disk: the routed
  skill's record, a decision trail for long or unattended runs
  (`references/decision-trail.md`), a resume note when pausing.

## 7. Reply

- The user's language; Korean when they write Korean. One read for a busy
  person: short declarative sentences, a table only to compare.
- Lead with what changed for the user (behavior, files, state), not process.
- Every claim carries its evidence (`file:line`, a command and the last line of
  its output, an artifact path) or a label.
- For every decision a principle drove, cite the principle and what it
  changed:
  "subtract-before-you-add: deleted the unused cache before adding the index".
- Never hand the user a check you could run. Run it and report the result.
- When `unslop` is installed, pass the reply through it.
- End with one or two lines: what was skipped or not checked, and the risk left.

## 8. Playbooks

- **investigation**: a question about code, history, or an outside API; read-only.
- **bug-fix**: something is broken, throwing, or flaky.
- **perf**: something is slower or heavier than it should be.
- **hillclimb**: sustained improvement against a fixed metric and regression gate.
- **runtime-forensics**: capture a live signal and diagnose its source.
- **trace-forensics**: analyze a capture that already exists.
- **instrumentation**: logs, metrics, traces, and alerts that answer on-call questions.
- **feature**: new or changed behavior a user can see.
- **api-design**: a contract other code will call.
- **ui**: an interface a person sees and operates.
- **visual-parity**: measure a migration against a frozen visual baseline.
- **refactoring**: structure changes while behavior is pinned.
- **migration**: retiring or replacing something that still has consumers.
- **prototype**: a fork that a cheap experiment can settle.
- **eval**: measure agent or skill behavior with a blinded comparison.
- **spec**: an ask too vague to plan, turned into a statement someone can check.
- **plan**: a multi-unit change whose plan is the deliverable.
- **review**: judging or explaining a change without editing it.
- **security**: trust boundaries and the controls on them.
- **fan-out**: independent slices run in parallel and merged into one result.
- **autonomous-run**: unattended work driven to a checkable exit condition.
- **autopilot**: drive a queue or stack of PRs with a verdict per item.
- **opening-a-pr**: publish a reviewable pull request when asked.
- **babysit**: check, triage, or drive an existing pull request to merge-ready.
- **ci**: the gates a change passes before it lands.
- **launch**: staged exposure to users with a written way back.
- **shipping**: commit, push, deploy, merge, and clean up at the reach asked for.
- **pause-and-pickup**: stopping safely, or resuming from a prior trail.
- **docs**: one document whose every claim holds for the commit it ships in.
- **authoring-a-skill**: writing or fixing a skill, or turning lessons into structure.

**No playbook fits**: design one before any code and put its steps in the task
list. (1) State done as a falsifiable check: a command, a surface, a pass
condition. (2) Size the work: the units, rough effort, visible blockers. (3) Set
rigor by reversibility: one-way doors and wide blast radius get more gates and
artifacts, reversible low-stakes steps fewer. (4) Order the riskiest unknown
first, scaffold and verification before features. (5) Build the verification
before the work, with a baseline from the unchanged state. (6) Log forks,
pivots, and verified units in the decision trail. A designed playbook you need
twice becomes a file in `playbooks/`.

**Reply:** what changed for the user, the playbook used and each skill it routed to, every claim with its evidence or label, the principles that changed a decision, and a closing line on what was skipped and what risk remains.
