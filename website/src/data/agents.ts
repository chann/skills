const sharedDirectory = "~/.agents/skills";

export const agents = [
  { id: "claude-code", name: "Claude Code", directory: "~/.claude/skills", docs: "https://code.claude.com/docs/en/skills" },
  { id: "codex", name: "Codex", directory: sharedDirectory, docs: "https://developers.openai.com/codex/skills/" },
  { id: "antigravity-cli", name: "Antigravity CLI", directory: "~/.gemini/config/skills", docs: "https://antigravity.google/docs/skills" },
  { id: "grok", name: "Grok Build", directory: "~/.grok/skills", docs: "https://docs.x.ai/build/features/skills-plugins-marketplaces" },
  { id: "pi", name: "Pi", directory: sharedDirectory, docs: "https://docs.pi.dev/latest/skills" },
  { id: "gemini-cli", name: "Gemini CLI", directory: sharedDirectory, docs: "https://geminicli.com/docs/cli/skills/" },
  { id: "github-copilot", name: "GitHub Copilot CLI", directory: sharedDirectory, docs: "https://docs.github.com/en/copilot/concepts/agents/about-agent-skills" },
  { id: "opencode", name: "OpenCode", directory: sharedDirectory, docs: "https://opencode.ai/docs/skills/" },
] as const;

export function installCommand(agentIds: string) {
  return `npx skills add chann/skills --skill '*' --agent ${agentIds} --global --yes`;
}
