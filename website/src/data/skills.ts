export const categoryOrder = [
  "mode",
  "understand",
  "design",
  "build",
  "verify",
  "ship",
  "delegate",
  "meta",
] as const;

export type SkillCategory = (typeof categoryOrder)[number];

export type SkillId =
  | "chann-mode"
  | "how"
  | "why"
  | "research-brief"
  | "recall"
  | "ketchup"
  | "diff-summary"
  | "plan-summary"
  | "diff-viewer"
  | "review-me"
  | "arena"
  | "bug-hunt"
  | "gen-docs"
  | "unslop"
  | "build-reinstall"
  | "interrogate"
  | "blast-radius"
  | "git-commit"
  | "git-merge"
  | "git-resolve-conflicts"
  | "git-cleanup"
  | "swarm"
  | "long-task"
  | "handoff"
  | "skill-forge"
  | "skill-audit"
  | "reflect";

export interface SkillDefinition {
  id: SkillId;
  title: string;
  category: SkillCategory;
  example: string;
  claudeSelector: string;
  codexSelector: string;
  aliases?: string[];
  tags: string[];
}

export const skillDefinitions = [
  {
    id: "chann-mode",
    title: "Chann Mode",
    category: "mode",
    example: "$chann-mode this endpoint got slow, find out why and fix it",
    claudeSelector: "/chann-mode",
    codexSelector: "$chann-mode",
    tags: ["router", "playbook", "entry-point", "evidence", "principles"],
  },
  {
    id: "how",
    title: "How",
    category: "understand",
    example: "$how how does the session refresh flow work",
    claudeSelector: "/how",
    codexSelector: "$how",
    tags: ["understand", "code", "architecture", "citation"],
  },
  {
    id: "why",
    title: "Why",
    category: "understand",
    example: "$why why is the retry limit still set to 3",
    claudeSelector: "/why",
    codexSelector: "$why",
    tags: ["understand", "history", "git", "decision"],
  },
  {
    id: "research-brief",
    title: "Research Brief",
    category: "understand",
    example: "$research-brief does Postgres 17 support incremental backups natively",
    claudeSelector: "/research-brief",
    codexSelector: "$research-brief",
    tags: ["research", "citation", "primary-source", "brief"],
  },
  {
    id: "recall",
    title: "Recall",
    category: "understand",
    example: "$recall this week",
    claudeSelector: "/recall",
    codexSelector: "$recall",
    tags: ["report", "history", "claude-code", "codex", "brief"],
  },
  {
    id: "ketchup",
    title: "Ketchup",
    category: "understand",
    example: "$ketchup",
    claudeSelector: "/ketchup",
    codexSelector: "$ketchup",
    tags: ["catch-up", "chat", "decision", "status"],
  },
  {
    id: "diff-summary",
    title: "Diff Summary",
    category: "understand",
    example: "$diff-summary main..dev --quiz",
    claudeSelector: "/diff-summary",
    codexSelector: "$diff-summary",
    tags: ["summary", "diff", "quiz", "html", "markdown"],
  },
  {
    id: "plan-summary",
    title: "Plan Summary",
    category: "understand",
    example: "$plan-summary docs/billing-prd.md --md",
    claudeSelector: "/plan-summary",
    codexSelector: "$plan-summary",
    tags: ["summary", "plan", "prd", "quiz", "bilingual"],
  },
  {
    id: "diff-viewer",
    title: "Diff Viewer",
    category: "understand",
    example: "$diff-viewer",
    claudeSelector: "/diff-viewer",
    codexSelector: "$diff-viewer",
    tags: ["diff", "html", "viewer", "patch"],
  },
  {
    id: "review-me",
    title: "Review Me",
    category: "design",
    example: "$review-me review our billing migration plan",
    claudeSelector: "/review-me",
    codexSelector: "$review-me",
    tags: ["review", "decision", "design", "plan", "interview"],
  },
  {
    id: "arena",
    title: "Arena",
    category: "design",
    example: "$arena give me three landing page hero designs and keep the best one",
    claudeSelector: "/arena",
    codexSelector: "$arena",
    tags: ["design", "compare", "judge", "candidates"],
  },
  {
    id: "bug-hunt",
    title: "Bug Hunt",
    category: "build",
    example: "$bug-hunt the checkout test fails about one run in five",
    claudeSelector: "/bug-hunt",
    codexSelector: "$bug-hunt",
    tags: ["debug", "root-cause", "flaky", "performance"],
  },
  {
    id: "gen-docs",
    title: "Generate Project Docs",
    category: "build",
    example: "$gen-docs",
    claudeSelector: "/gen-docs",
    codexSelector: "$gen-docs",
    tags: ["docs", "readme", "architecture", "usage", "translation"],
  },
  {
    id: "unslop",
    title: "Unslop",
    category: "build",
    example: "$unslop docs/release-notes.md",
    claudeSelector: "/unslop",
    codexSelector: "$unslop",
    tags: ["writing", "korean", "english", "rewrite"],
  },
  {
    id: "build-reinstall",
    title: "Build and Reinstall",
    category: "build",
    example: "$build-reinstall",
    claudeSelector: "/build-reinstall",
    codexSelector: "$build-reinstall",
    tags: ["build", "install", "verify", "sha256"],
  },
  {
    id: "interrogate",
    title: "Interrogate",
    category: "verify",
    example: "$interrogate main..HEAD --md",
    claudeSelector: "/interrogate",
    codexSelector: "$interrogate",
    tags: ["review", "security", "proof", "html", "pr"],
  },
  {
    id: "blast-radius",
    title: "Blast Radius",
    category: "verify",
    example: "$blast-radius the auth middleware change",
    claudeSelector: "/blast-radius",
    codexSelector: "$blast-radius",
    tags: ["impact", "safety", "risk", "merge"],
  },
  {
    id: "git-commit",
    title: "Git Commit",
    category: "ship",
    example: "$git-commit push realtime",
    claudeSelector: "/git-commit",
    codexSelector: "$git-commit",
    aliases: ["/gcr", "$gcr", "/gcpr", "$gcpr", "/gcpd", "$gcpd"],
    tags: ["git", "commit", "push", "deploy", "rewrite"],
  },
  {
    id: "git-merge",
    title: "Git Merge",
    category: "ship",
    example: "$git-merge dev",
    claudeSelector: "/git-merge",
    codexSelector: "$git-merge",
    tags: ["git", "merge", "branch", "safety"],
  },
  {
    id: "git-resolve-conflicts",
    title: "Git Resolve Conflicts",
    category: "ship",
    example: "$git-resolve-conflicts",
    claudeSelector: "/git-resolve-conflicts",
    codexSelector: "$git-resolve-conflicts",
    tags: ["git", "conflict", "merge", "rebase"],
  },
  {
    id: "git-cleanup",
    title: "Git Cleanup",
    category: "ship",
    example: "$git-cleanup",
    claudeSelector: "/git-cleanup",
    codexSelector: "$git-cleanup",
    tags: ["git", "branch", "worktree", "cleanup"],
  },
  {
    id: "swarm",
    title: "Swarm",
    category: "delegate",
    example: "$swarm use subagents to review this diff",
    claudeSelector: "/swarm",
    codexSelector: "$swarm",
    tags: ["subagent", "parallel", "model", "quota", "codex", "claude"],
  },
  {
    id: "long-task",
    title: "Long Task",
    category: "delegate",
    example: "$long-task build the project end to end",
    claudeSelector: "/long-task",
    codexSelector: "$long-task",
    tags: ["orchestration", "milestone", "autonomous", "agent"],
  },
  {
    id: "handoff",
    title: "Handoff",
    category: "delegate",
    example: "$handoff session so a new agent can continue tomorrow",
    claudeSelector: "/handoff",
    codexSelector: "$handoff",
    tags: ["handoff", "frontend", "backend", "session", "resume"],
  },
  {
    id: "skill-forge",
    title: "Skill Forge",
    category: "meta",
    example: "$skill-forge add a skill that triages a failing CI run",
    claudeSelector: "/skill-forge",
    codexSelector: "$skill-forge",
    tags: ["skill", "authoring", "contract", "catalog", "scaffold"],
  },
  {
    id: "skill-audit",
    title: "Skill Audit",
    category: "meta",
    example: "$skill-audit",
    claudeSelector: "/skill-audit",
    codexSelector: "$skill-audit",
    tags: ["skill", "audit", "contract", "lint", "ci"],
  },
  {
    id: "reflect",
    title: "Reflect",
    category: "meta",
    example: "$reflect repo",
    claudeSelector: "/reflect",
    codexSelector: "$reflect",
    tags: ["lessons", "session", "repo", "enforcement"],
  },
] as const satisfies readonly SkillDefinition[];
