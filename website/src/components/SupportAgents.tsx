import { ArrowUpRight } from "@phosphor-icons/react";
import { useState } from "react";
import { agents, installCommand } from "../data/agents";
import type { SiteContent } from "../i18n/types";
import { CopyButton } from "./CopyButton";

export function SupportAgents({ content, copy }: {
  content: SiteContent["platforms"];
  copy: SiteContent["copy"];
}) {
  const [selected, setSelected] = useState<(typeof agents)[number]>(agents[0]);
  const command = installCommand(selected.id);

  return (
    <section className="section agents" id="agents" aria-labelledby="agents-title">
      <div className="section-heading section-heading--center">
        <h2 id="agents-title">{content.title}</h2>
        <p>{content.description}</p>
      </div>
      <div className="agents__picker">
        <div className="agents__choices" role="group" aria-labelledby="agents-title">
          {agents.map((agent) => (
            <button
              key={agent.id}
              type="button"
              aria-pressed={selected.id === agent.id}
              aria-controls="agent-details"
              onClick={() => setSelected(agent)}
            >
              <img src={`/skills/agents/${agent.id}.${agent.id === "codex" ? "png" : "svg"}`} alt="" width="40" height="40" />
              {agent.name}
            </button>
          ))}
        </div>
        <div className="agents__details" id="agent-details" aria-live="polite">
          <div className="agents__heading">
            <h3>{selected.name}</h3>
            <a href={selected.docs}>{content.docs} <ArrowUpRight aria-hidden="true" /></a>
          </div>
          <dl>
            <dt>{content.directory}</dt>
            <dd><code>{selected.directory}/</code></dd>
            <dt>{content.install}</dt>
            <dd className="install-command">
              <span aria-hidden="true">$</span>
              <code tabIndex={0}>{command}</code>
              <CopyButton key={command} value={command} content={copy} />
            </dd>
          </dl>
        </div>
      </div>
    </section>
  );
}
