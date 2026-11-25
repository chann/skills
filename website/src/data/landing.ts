import type { SkillCategory, SkillId } from "./skills";

/** Number of files in chann-mode/skills/chann/playbooks; verify:landing checks it. */
export const playbookCount = 30;

export const shortInstallCommand = "npx skills add chann/skills";

/** One node per phase of the flow diagram: the category and the two skills shown in it. */
export const lifecyclePhases: ReadonlyArray<{
  category: SkillCategory;
  lead: SkillId;
  second: SkillId;
}> = [
  { category: "understand", lead: "how", second: "why" },
  { category: "design", lead: "review-me", second: "arena" },
  { category: "build", lead: "bug-hunt", second: "unslop" },
  { category: "verify", lead: "interrogate", second: "blast-radius" },
  { category: "ship", lead: "git-commit", second: "git-merge" },
  { category: "delegate", lead: "swarm", second: "handoff" },
];

/** Rows of the command table, in the order of `landing.lifecycle.commands`. */
export const lifecycleCommands: readonly SkillId[] = [
  "chann",
  "how",
  "review-me",
  "bug-hunt",
  "interrogate",
  "git-commit",
  "long-task",
  "handoff",
];

/** Playbook names per router card, in the order of `landing.router.groups`. */
export const routerGroups: ReadonlyArray<readonly string[]> = [
  ["spec", "feature", "api-design", "ui"],
  ["bug-fix", "perf", "runtime-forensics", "trace-forensics"],
  ["review", "security", "eval"],
  ["ci", "launch", "shipping", "migration"],
];
