import {
  ArrowRight,
  ArrowUpRight,
  ListChecks,
  Lock,
  Plus,
  SealCheck,
  ShieldCheck,
} from "@phosphor-icons/react";
import { motion, useReducedMotion } from "motion/react";
import { useEffect, useMemo, useState } from "react";
import { CopyButton } from "../components/CopyButton";
import { GitHubMark } from "../components/GitHubMark";
import { LanguageSwitcher } from "../components/LanguageSwitcher";
import { Reveal } from "../components/Reveal";
import { SupportAgents } from "../components/SupportAgents";
import { Lines, withFlags } from "../components/Text";
import { ThemeToggle } from "../components/ThemeToggle";
import { agents } from "../data/agents";
import { categoryOrder, type SkillCategory, type SkillId } from "../data/skills";
import { formatMessage, getContent, getLocalizedSkills } from "../i18n/content";
import type { Locale, SiteContent } from "../i18n/types";
import {
  featuredSkills,
  lifecycleCommands,
  lifecyclePhases,
  playbookCount,
  repositoryUrl,
  routerGroups,
  shortInstallCommand,
} from "./data";

const repositoryName = "chann/skills";
const navIds = ["lifecycle", "catalog", "why", "router", "faq"] as const;
const mechanismIcons = [SealCheck, ListChecks, Lock, ShieldCheck] as const;

function BrandMark() {
  return (
    <svg className="n-brand__mark" viewBox="0 0 32 32" width="22" height="22" aria-hidden="true">
      <rect x="7" y="16" width="4" height="9" rx="2" />
      <rect x="14" y="7" width="4" height="18" rx="2" />
      <rect x="21" y="12" width="4" height="13" rx="2" />
    </svg>
  );
}

function CommandLine({ command, label, copy }: {
  command: string;
  label: string;
  copy: SiteContent["copy"];
}) {
  return (
    <div className="n-command" role="group" aria-label={label}>
      <span aria-hidden="true">$</span>
      <code tabIndex={0}>{command}</code>
      <CopyButton value={command} content={copy} compact />
    </div>
  );
}

function SectionHead({ index, label, title, description, id }: {
  index: number;
  label: string;
  title: readonly string[];
  description: string;
  id: string;
}) {
  return (
    <Reveal className="n-head">
      <p className="n-eyebrow">
        <span>{String(index).padStart(2, "0")}</span> {label}
      </p>
      <h2 id={id}>
        <Lines lines={title} />
      </h2>
      <p className="n-head__lede">{description}</p>
    </Reveal>
  );
}

interface NewAppProps {
  locale: Locale;
}

export function NewApp({ locale }: NewAppProps) {
  const content = getContent(locale);
  const landing = content.landing;
  const skills = getLocalizedSkills(locale);
  const reduceMotion = useReducedMotion();
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [category, setCategory] = useState<SkillCategory | "all">("all");
  const [expanded, setExpanded] = useState(false);

  const skillById = useMemo(() => new Map(skills.map((skill) => [skill.id, skill])), [skills]);
  const skill = (id: SkillId) => skillById.get(id)!;
  const selectorCount = useMemo(
    () =>
      skills.length +
      new Set(skills.flatMap((item) => (item.aliases ?? []).map((alias) => alias.slice(1)))).size,
    [skills],
  );
  const counts = {
    count: skills.length,
    selectors: selectorCount,
    agents: agents.length,
    playbooks: playbookCount,
    categories: categoryOrder.length,
  };
  const visibleSkills =
    category !== "all"
      ? skills.filter((item) => item.category === category)
      : expanded
        ? skills
        : featuredSkills.map(skill);

  useEffect(() => {
    const sections = navIds
      .map((id) => document.getElementById(id))
      .filter((element): element is HTMLElement => element !== null);
    const observer = new IntersectionObserver(
      (entries) => {
        const leaving = entries
          .filter((entry) => !entry.isIntersecting)
          .map((entry) => entry.target.id);
        const entering = entries.find((entry) => entry.isIntersecting)?.target.id;
        setActiveSection((current) =>
          entering ?? (current && leaving.includes(current) ? null : current),
        );
      },
      { rootMargin: "-40% 0px -55% 0px" },
    );
    sections.forEach((element) => observer.observe(element));
    return () => observer.disconnect();
  }, []);

  const homeLabel = formatMessage(content.accessibility.home, { repository: repositoryName });
  const playbooksUrl = `${repositoryUrl}/blob/main/chann-mode/${
    locale === "ko" ? "README.ko.md#플레이북" : "README.md#playbooks"
  }`;

  return (
    <>
      <a className="skip-link" href="#main">
        {content.accessibility.skipToMain}
      </a>

      <header className="n-header">
        <div className="n-header__inner">
          <a className="n-brand" href="#main" aria-label={homeLabel}>
            <BrandMark />
            <span>
              chann<i>/skills</i>
            </span>
          </a>

          <nav className="n-nav" aria-label={content.nav.label}>
            {navIds.map((id) => (
              <a
                key={id}
                href={`#${id}`}
                aria-current={activeSection === id ? "true" : undefined}
              >
                {landing.nav[id]}
              </a>
            ))}
          </nav>

          <div className="n-header__actions">
            <LanguageSwitcher locale={locale} labels={content.language} preview />
            <ThemeToggle content={content.theme} />
            <a
              className="n-icon-link"
              href={repositoryUrl}
              target="_blank"
              rel="noreferrer"
              aria-label={content.accessibility.github}
            >
              <GitHubMark size={18} />
            </a>
            <a className="n-button n-button--primary n-button--small" href="#install">
              {landing.nav.cta}
            </a>
          </div>
        </div>
      </header>

      <main id="main">
        <section className="n-hero" aria-labelledby="hero-title">
          <div className="n-hero__backdrop" aria-hidden="true" />
          <motion.div
            className="n-hero__inner"
            initial={reduceMotion ? false : { opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: reduceMotion ? 0 : 0.7, ease: [0.16, 1, 0.3, 1] }}
          >
            <a className="n-badge" href={repositoryUrl} target="_blank" rel="noreferrer">
              <i aria-hidden="true" />
              {formatMessage(landing.hero.badge, counts)}
              <ArrowUpRight size={13} weight="bold" aria-hidden="true" />
            </a>
            <h1 id="hero-title">
              <Lines lines={content.hero.headline} />
            </h1>
            <p className="n-hero__lede">{formatMessage(content.hero.lede, counts)}</p>
            <CommandLine
              command={shortInstallCommand}
              label={landing.hero.commandLabel}
              copy={content.copy}
            />
            <div className="n-actions">
              <a className="n-button n-button--primary" href="#install">
                {landing.hero.primaryAction}
                <ArrowRight size={16} weight="bold" aria-hidden="true" />
              </a>
              <a className="n-button" href="#catalog">
                {formatMessage(content.hero.primaryAction, counts)}
              </a>
            </div>
            <div className="n-agents">
              <p>{formatMessage(landing.hero.agentsLabel, counts)}</p>
              <ul>
                {agents.map((agent) => (
                  <li key={agent.id}>
                    <img
                      src={`/skills/agents/${agent.id}.${agent.id === "codex" ? "png" : "svg"}`}
                      alt=""
                      width="22"
                      height="22"
                    />
                    {agent.name}
                  </li>
                ))}
              </ul>
            </div>
          </motion.div>
        </section>

        <section className="n-section" id="lifecycle" aria-labelledby="lifecycle-title">
          <SectionHead
            index={1}
            id="lifecycle-title"
            label={landing.lifecycle.label}
            title={landing.lifecycle.title}
            description={landing.lifecycle.description}
          />
          <Reveal delay={0.06}>
            <ol className="n-flow" aria-label={landing.lifecycle.flowLabel}>
              {lifecyclePhases.map((phase) => (
                <li key={phase.category}>
                  <span className="n-flow__phase">{content.categories[phase.category].label}</span>
                  <div className="n-flow__node">
                    <strong>{skill(phase.lead).title}</strong>
                    <span>{skill(phase.second).title}</span>
                  </div>
                  <code>{skill(phase.lead).claudeSelector}</code>
                </li>
              ))}
            </ol>
          </Reveal>
          <Reveal delay={0.1}>
            <ul className="n-commands" aria-label={landing.lifecycle.commandsLabel}>
              {lifecycleCommands.map((id, index) => (
                <li key={id}>
                  <code>{skill(id).claudeSelector}</code>
                  <span>{landing.lifecycle.commands[index]}</span>
                  <small>{content.categories[skill(id).category].label}</small>
                </li>
              ))}
            </ul>
          </Reveal>
        </section>

        <section className="n-section" id="catalog" aria-labelledby="catalog-title">
          <div className="n-head-row">
            <SectionHead
              index={2}
              id="catalog-title"
              label={content.catalog.label}
              title={content.catalog.title}
              description={formatMessage(landing.catalog.selectors, counts)}
            />
            {category === "all" ? (
              <button
                className="n-button"
                type="button"
                aria-expanded={expanded}
                aria-controls="catalog-grid"
                onClick={() => setExpanded((value) => !value)}
              >
                {expanded ? landing.catalog.showLess : content.catalog.showAll}
                <ArrowRight size={16} weight="bold" aria-hidden="true" />
              </button>
            ) : null}
          </div>

          <div className="n-chips" role="group" aria-label={content.catalog.filtersLabel}>
            <button type="button" aria-pressed={category === "all"} onClick={() => setCategory("all")}>
              {content.catalog.all}
            </button>
            {categoryOrder.map((item) => (
              <button
                key={item}
                type="button"
                aria-pressed={category === item}
                onClick={() => setCategory(item)}
              >
                {content.categories[item].label}
              </button>
            ))}
          </div>

          <ul className="n-cards" id="catalog-grid" aria-label={content.catalog.skillList}>
            {visibleSkills.map((item) => (
              <li className="n-card" key={item.id} data-category={item.category}>
                <div className="n-card__top">
                  <span className="n-pill">
                    <i aria-hidden="true" />
                    {content.categories[item.category].label}
                  </span>
                  <code>{item.claudeSelector}</code>
                </div>
                <h3>{item.id}</h3>
                <p className="n-card__summary">{withFlags(item.summary)}</p>
                <div className="n-card__foot">
                  <p>{item.whenToUse}</p>
                  <CopyButton
                    value={item.example}
                    content={content.copy}
                    label={content.catalog.exampleCopy}
                    compact
                  />
                </div>
              </li>
            ))}
          </ul>
        </section>

        <section className="n-section" id="why" aria-labelledby="why-title">
          <SectionHead
            index={3}
            id="why-title"
            label={landing.why.label}
            title={landing.why.title}
            description={landing.why.description}
          />
          <div className="n-mechanisms">
            {landing.why.items.map((item, index) => {
              const Icon = mechanismIcons[index];
              return (
                <Reveal key={item.label} delay={index * 0.04}>
                  <article className="n-mechanism">
                    <header>
                      <span className="n-mechanism__icon">
                        <Icon size={18} weight="regular" aria-hidden="true" />
                      </span>
                      <span className="n-mechanism__label">{item.label}</span>
                    </header>
                    <h3>{item.title}</h3>
                    <p>{item.description}</p>
                  </article>
                </Reveal>
              );
            })}
          </div>
        </section>

        <section className="n-section n-router" id="router" aria-labelledby="router-title">
          <Reveal className="n-router__copy">
            <p className="n-eyebrow">
              <span>04</span> {landing.router.label}
            </p>
            <h2 id="router-title">
              <Lines lines={landing.router.title} />
            </h2>
            <p className="n-head__lede">{formatMessage(landing.router.description, counts)}</p>
            <div className="n-run">
              <span aria-hidden="true">›</span>
              <code>{skill("chann").example}</code>
            </div>
            <a className="n-button" href={playbooksUrl} target="_blank" rel="noreferrer">
              {formatMessage(landing.router.action, counts)}
              <ArrowRight size={16} weight="bold" aria-hidden="true" />
            </a>
          </Reveal>
          <div className="n-router__groups">
            {landing.router.groups.map((group, index) => (
              <Reveal key={group.tag} delay={index * 0.04}>
                <article className="n-group">
                  <header>
                    <span className="n-group__index">{String(index + 1).padStart(2, "0")}</span>
                    <strong>{group.tag}</strong>
                  </header>
                  <ul>
                    {routerGroups[index].map((name) => (
                      <li key={name}>
                        <code>{name}</code>
                      </li>
                    ))}
                  </ul>
                  <p>{group.description}</p>
                </article>
              </Reveal>
            ))}
          </div>
        </section>

        <section className="n-section n-faq" id="faq" aria-labelledby="faq-title">
          <Reveal className="n-faq__copy">
            <p className="n-eyebrow">
              <span>05</span> {content.faq.label}
            </p>
            <h2 id="faq-title">{content.faq.title}</h2>
            <p className="n-head__lede">{content.faq.description}</p>
          </Reveal>
          <Reveal className="n-faq__list" delay={0.06}>
            {content.faq.items.map((faq) => (
              <details key={faq.question}>
                <summary>
                  {faq.question}
                  <Plus size={16} weight="bold" aria-hidden="true" />
                </summary>
                <p>{faq.answer}</p>
              </details>
            ))}
          </Reveal>
        </section>

        <section className="n-install" id="install" aria-labelledby="install-title">
          <div className="n-install__glow" aria-hidden="true" />
          <Reveal className="n-install__head">
            <h2 id="install-title">
              <Lines lines={landing.cta.title} />
            </h2>
            <p>{formatMessage(landing.cta.description, counts)}</p>
          </Reveal>
          <Reveal delay={0.06}>
            <SupportAgents
              content={content.platforms}
              install={content.install}
              copy={content.copy}
              skillCount={skills.length}
            />
          </Reveal>
          <Reveal className="n-actions" delay={0.08}>
            <a className="n-button n-button--primary" href="#catalog">
              {formatMessage(content.install.exploreAction, counts)}
              <ArrowRight size={16} weight="bold" aria-hidden="true" />
            </a>
            <a className="n-button" href={repositoryUrl} target="_blank" rel="noreferrer">
              <GitHubMark size={16} />
              {content.install.githubAction}
            </a>
          </Reveal>
        </section>
      </main>

      <footer className="n-footer">
        <div className="n-footer__grid">
          <div className="n-footer__brand">
            <a className="n-brand" href="#main" aria-label={homeLabel}>
              <BrandMark />
              <span>
                chann<i>/skills</i>
              </span>
            </a>
            <p>{content.footer.tagline}</p>
            <code>{shortInstallCommand}</code>
          </div>
          <nav aria-label={landing.footer.product}>
            <h3>{landing.footer.product}</h3>
            {navIds.map((id) => (
              <a key={id} href={`#${id}`}>
                {landing.nav[id]}
              </a>
            ))}
            <a href="#install">{content.nav.items.install}</a>
          </nav>
          <nav aria-label={landing.footer.setup}>
            <h3>{landing.footer.setup}</h3>
            {agents.map((agent) => (
              <a key={agent.id} href={agent.docs} target="_blank" rel="noreferrer">
                {agent.name}
              </a>
            ))}
          </nav>
          <nav aria-label={landing.footer.resources}>
            <h3>{landing.footer.resources}</h3>
            <a href={repositoryUrl} target="_blank" rel="noreferrer">
              {content.footer.github} ↗
            </a>
            <a href={`${repositoryUrl}/blob/main/USAGE.md`} target="_blank" rel="noreferrer">
              {landing.footer.usage} ↗
            </a>
            <a href={`${repositoryUrl}/blob/main/ARCHITECTURE.md`} target="_blank" rel="noreferrer">
              {landing.footer.architecture} ↗
            </a>
            <a
              href={`${repositoryUrl}/blob/main/skill-forge/skills/skill-forge/references/skill-package-contract.md`}
              target="_blank"
              rel="noreferrer"
            >
              {landing.footer.contract} ↗
            </a>
            <a href={`${repositoryUrl}/blob/main/LICENSE`} target="_blank" rel="noreferrer">
              {content.footer.license} ↗
            </a>
          </nav>
        </div>
        <p className="n-footer__legal">
          {formatMessage(landing.footer.copyright, { year: new Date().getFullYear() })}
        </p>
        <div className="site-footer__word" aria-hidden="true">
          {repositoryName.split("").map((letter, index) => (
            <motion.span
              key={index}
              initial={reduceMotion ? false : { y: "0.42em", opacity: 0 }}
              whileInView={{ y: 0, opacity: 1 }}
              viewport={{ once: false, amount: 0.2 }}
              transition={{
                duration: reduceMotion ? 0 : 0.8,
                delay: reduceMotion ? 0 : index * 0.055,
                ease: [0.16, 1, 0.3, 1],
              }}
            >
              {letter}
            </motion.span>
          ))}
        </div>
      </footer>
    </>
  );
}
