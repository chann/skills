import { ArrowUpRight, CheckCircle, TerminalWindow } from "@phosphor-icons/react";
import { useState } from "react";
import { agents, installCommand } from "../data/agents";
import { formatMessage } from "../i18n/content";
import type { SiteContent } from "../i18n/types";
import { CopyButton } from "./CopyButton";

const allAgentIds = agents.map((agent) => agent.id).join(" ");

export function SupportAgents({ content, install, copy, skillCount }: {
  content: SiteContent["platforms"];
  install: SiteContent["install"];
  copy: SiteContent["copy"];
  skillCount: number;
}) {
  const [selected, setSelected] = useState<(typeof agents)[number] | null>(null);
  const command = installCommand(selected?.id ?? allAgentIds);

  return (
    <div className="agents__picker" id="agents">
      <div className="install-card" id="agent-details">
        <div aria-live="polite">
          {selected ? (
            <>
              <div className="agents__heading">
                <h3>{selected.name}</h3>
                <a href={selected.docs}>{content.docs} <ArrowUpRight size={16} aria-hidden="true" /></a>
              </div>
              <p className="agents__directory">{content.directory} <code>{selected.directory}/</code></p>
            </>
          ) : (
            <div className="install-card__heading">
              <h3>{install.cardTitle}</h3>
              <p>{install.cardDescription}</p>
            </div>
          )}
        </div>
        <div className="install-command">
          <span aria-hidden="true">$</span>
          <code tabIndex={0}>{command}</code>
          <CopyButton key={command} value={command} content={copy} label={install.copyLabel} />
        </div>
        {!selected && (
          <ul className="install-notes" aria-label={install.resultsLabel}>
            <li><CheckCircle size={17} weight="fill" aria-hidden="true" /> {formatMessage(install.skillResult, { count: skillCount })}</li>
            <li><CheckCircle size={17} weight="fill" aria-hidden="true" /> {install.linkResult}</li>
            <li><CheckCircle size={17} weight="fill" aria-hidden="true" /> {install.platformsResult}</li>
          </ul>
        )}
      </div>

      <div className="agents__intro">
        <h3 id="agents-title">{content.title}</h3>
        <p>{content.description}</p>
      </div>
      <div className="agents__choices" role="group" aria-labelledby="agents-title">
        <button
          className="agents__all"
          type="button"
          aria-pressed={selected === null}
          aria-controls="agent-details"
          onClick={() => setSelected(null)}
        >
          <TerminalWindow size={24} aria-hidden="true" />
          {content.all}
        </button>
        {agents.map((agent) => (
          <button
            key={agent.id}
            type="button"
            aria-pressed={selected?.id === agent.id}
            aria-controls="agent-details"
            onClick={() => setSelected(agent)}
          >
            <img src={`/skills/agents/${agent.id}.${agent.id === "codex" ? "png" : "svg"}`} alt="" width="40" height="40" />
            {agent.name}
          </button>
        ))}
      </div>
    </div>
  );
}
