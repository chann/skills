export const categoryOrder = [
  "review",
  "docs",
  "git",
  "handoff",
  "automation",
  "authoring",
  "report",
] as const;

export type SkillCategory = (typeof categoryOrder)[number];

export type SkillId =
  | "review-me"
  | "code-review"
  | "code-review-md"
  | "diff-summary"
  | "diff-summary-md"
  | "diff-summary-quiz"
  | "diff-viewer"
  | "gen-docs"
  | "plan-summary"
  | "plan-summary-md"
  | "plan-summary-quiz"
  | "human-friendly-writing"
  | "git-commit"
  | "git-commit-push"
  | "git-commit-push-realtime"
  | "git-commit-realtime"
  | "git-commit-rewrite"
  | "git-merge-to-main"
  | "git-merge-to-dev"
  | "git-branch-cleanup"
  | "gen-frontend-handoff"
  | "gen-backend-handoff"
  | "long-task"
  | "build-reinstall"
  | "skill-forge"
  | "skill-audit"
  | "work-summary";

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
    id: "review-me",
    title: "Review Me",
    category: "review",
    example: "$review-me review our billing migration plan",
    claudeSelector: "/review-me",
    codexSelector: "$review-me",
    tags: ["review", "decision", "design", "plan", "interview"],
  },
  {
    id: "code-review",
    title: "Code Review",
    category: "review",
    example: "$code-review review the last commit",
    claudeSelector: "/code-review",
    codexSelector: "$code-review",
    tags: ["review", "security", "html", "pr"],
  },
  {
    id: "code-review-md",
    title: "Markdown Code Review",
    category: "review",
    example: "$code-review-md review staged changes",
    claudeSelector: "/code-review-md",
    codexSelector: "$code-review-md",
    tags: ["review", "markdown", "pr"],
  },
  {
    id: "diff-summary",
    title: "Diff Summary",
    category: "review",
    example: "$diff-summary main..dev",
    claudeSelector: "/diff-summary",
    codexSelector: "$diff-summary",
    tags: ["summary", "diff", "html", "architecture"],
  },
  {
    id: "diff-summary-md",
    title: "Markdown Diff Summary",
    category: "review",
    example: "$diff-summary-md HEAD~3..HEAD",
    claudeSelector: "/diff-summary-md",
    codexSelector: "$diff-summary-md",
    tags: ["summary", "diff", "markdown"],
  },
  {
    id: "diff-summary-quiz",
    title: "Diff Summary Quiz",
    category: "review",
    example: "$diff-summary-quiz feature...main",
    claudeSelector: "/diff-summary-quiz",
    codexSelector: "$diff-summary-quiz",
    tags: ["summary", "quiz", "learning", "diff"],
  },
  {
    id: "diff-viewer",
    title: "Diff Viewer",
    category: "review",
    example: "$diff-viewer",
    claudeSelector: "/diff-viewer",
    codexSelector: "$diff-viewer",
    tags: ["diff", "viewer", "html", "git"],
  },
  {
    id: "gen-docs",
    title: "Generate Project Docs",
    category: "docs",
    example: "$gen-docs",
    claudeSelector: "/gen-docs",
    codexSelector: "$gen-docs",
    tags: ["docs", "readme", "architecture", "usage"],
  },
  {
    id: "plan-summary",
    title: "Plan Summary",
    category: "docs",
    example: "$plan-summary docs/plan.md docs/design.md",
    claudeSelector: "/plan-summary",
    codexSelector: "$plan-summary",
    tags: ["plan", "prd", "design", "spec", "summary", "bilingual"],
  },
  {
    id: "plan-summary-md",
    title: "Plan Summary Markdown",
    category: "docs",
    example: "$plan-summary-md docs/plan.md",
    claudeSelector: "/plan-summary-md",
    codexSelector: "$plan-summary-md",
    tags: ["plan", "prd", "design", "markdown", "summary", "bilingual"],
  },
  {
    id: "plan-summary-quiz",
    title: "Plan Summary Quiz",
    category: "docs",
    example: "$plan-summary-quiz docs/prd.md",
    claudeSelector: "/plan-summary-quiz",
    codexSelector: "$plan-summary-quiz",
    tags: ["plan", "prd", "design", "quiz", "summary", "bilingual"],
  },
  {
    id: "human-friendly-writing",
    title: "Human Friendly Writing",
    category: "docs",
    example: "$human-friendly-writing docs/release-note.ko.md",
    claudeSelector: "/human-friendly-writing",
    codexSelector: "$human-friendly-writing",
    tags: ["korean", "writing", "humanize", "de-jargon", "style", "rewrite"],
  },
  {
    id: "git-commit",
    title: "Git Commit",
    category: "git",
    example: "$git-commit",
    claudeSelector: "/git-commit",
    codexSelector: "$git-commit",
    tags: ["git", "commit", "conventional"],
  },
  {
    id: "git-commit-push",
    title: "Git Commit and Push",
    category: "git",
    example: "$git-commit-push",
    claudeSelector: "/git-commit-push",
    codexSelector: "$git-commit-push",
    tags: ["git", "commit", "push"],
  },
  {
    id: "git-commit-push-realtime",
    title: "Git Commit and Push Realtime",
    category: "git",
    example: "$git-commit-push-realtime",
    claudeSelector: "/git-commit-push-realtime",
    codexSelector: "$git-commit-push-realtime",
    aliases: ["/gcpr", "$gcpr"],
    tags: ["git", "commit", "push", "realtime", "checkpoint"],
  },
  {
    id: "git-commit-realtime",
    title: "Git Commit Realtime",
    category: "git",
    example: "$git-commit-realtime",
    claudeSelector: "/git-commit-realtime",
    codexSelector: "$git-commit-realtime",
    aliases: ["/gcr"],
    tags: ["git", "commit", "realtime", "checkpoint"],
  },
  {
    id: "git-commit-rewrite",
    title: "Git Commit Rewrite",
    category: "git",
    example: "$git-commit-rewrite",
    claudeSelector: "/git-commit-rewrite",
    codexSelector: "$git-commit-rewrite",
    tags: ["git", "history", "commit", "rewrite"],
  },
  {
    id: "git-merge-to-main",
    title: "Git Merge to Main",
    category: "git",
    example: "$git-merge-to-main",
    claudeSelector: "/git-merge-to-main",
    codexSelector: "$git-merge-to-main",
    tags: ["git", "merge", "main", "branch"],
  },
  {
    id: "git-merge-to-dev",
    title: "Git Merge to Dev",
    category: "git",
    example: "$git-merge-to-dev",
    claudeSelector: "/git-merge-to-dev",
    codexSelector: "$git-merge-to-dev",
    tags: ["git", "merge", "dev", "branch"],
  },
  {
    id: "git-branch-cleanup",
    title: "Git Branch Cleanup",
    category: "git",
    example: "$git-branch-cleanup",
    claudeSelector: "/git-branch-cleanup",
    codexSelector: "$git-branch-cleanup",
    tags: ["git", "branch", "cleanup", "safe"],
  },
  {
    id: "gen-frontend-handoff",
    title: "Generate Frontend Handoff",
    category: "handoff",
    example: "$gen-frontend-handoff main...feature-api",
    claudeSelector: "/gen-frontend-handoff",
    codexSelector: "$gen-frontend-handoff",
    tags: ["handoff", "frontend", "api", "client"],
  },
  {
    id: "gen-backend-handoff",
    title: "Generate Backend Handoff",
    category: "handoff",
    example: "$gen-backend-handoff HEAD~5..HEAD",
    claudeSelector: "/gen-backend-handoff",
    codexSelector: "$gen-backend-handoff",
    tags: ["handoff", "backend", "api", "database"],
  },
  {
    id: "long-task",
    title: "Long Task",
    category: "automation",
    example: "$long-task build the project end to end",
    claudeSelector: "/long-task",
    codexSelector: "$long-task",
    tags: ["automation", "orchestration", "milestone", "agent"],
  },
  {
    id: "build-reinstall",
    title: "Build and Reinstall",
    category: "automation",
    example: "$build-reinstall",
    claudeSelector: "/build-reinstall",
    codexSelector: "$build-reinstall",
    tags: ["automation", "build", "install", "verify", "sha256"],
  },
  {
    id: "skill-forge",
    title: "Skill Forge",
    category: "authoring",
    example: "$skill-forge add a skill that triages a failing CI run",
    claudeSelector: "/skill-forge",
    codexSelector: "$skill-forge",
    tags: ["skill", "authoring", "contract", "catalog", "scaffold"],
  },
  {
    id: "skill-audit",
    title: "Skill Audit",
    category: "authoring",
    example: "$skill-audit",
    claudeSelector: "/skill-audit",
    codexSelector: "$skill-audit",
    tags: ["skill", "audit", "contract", "lint", "ci"],
  },
  {
    id: "work-summary",
    title: "Work Summary",
    category: "report",
    example: "$work-summary this week",
    claudeSelector: "/work-summary",
    codexSelector: "$work-summary",
    tags: ["report", "summary", "history", "claude-code", "codex"],
  },
] as const satisfies readonly SkillDefinition[];
