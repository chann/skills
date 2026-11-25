import {
  ArrowRight,
  Brain,
  Bug,
  Code,
  Plus,
  Repeat,
  RocketLaunch,
  ShieldCheck,
  TerminalWindow,
} from "@phosphor-icons/react";
import { motion, useReducedMotion } from "motion/react";
import { useEffect, useState } from "react";
import { GitHubMark } from "./components/GitHubMark";
import { LanguageSwitcher } from "./components/LanguageSwitcher";
import { Reveal } from "./components/Reveal";
import { SkillExplorer } from "./components/SkillExplorer";
import { Lines, withFlags } from "./components/Text";
import { TaglineReveal } from "./components/TaglineReveal";
import { agents } from "./data/agents";
import { SupportAgents } from "./components/SupportAgents";
import { ThemeToggle } from "./components/ThemeToggle";
import {
  lifecycleCommands,
  lifecyclePhases,
  playbookCount,
  routerGroups,
  shortInstallCommand,
} from "./data/landing";
import { categoryOrder, type SkillId } from "./data/skills";
import { formatMessage, getContent, getLocalizedSkills } from "./i18n/content";
import type { Locale, ProductPreviewContent } from "./i18n/types";

const repositoryName = "chann/skills";
const benefitIcons = [Repeat, TerminalWindow, Brain] as const;
const routerIcons = [Code, Bug, ShieldCheck, RocketLaunch] as const;

interface ProductPreviewProps {
  content: ProductPreviewContent;
  skillCount: number;
}

function ProductPreview({ content, skillCount }: ProductPreviewProps) {
  return (
    <div className="product-window">
      <div className="product-window__chrome">
        <span className="window-dots" aria-hidden="true">
          <i />
          <i />
          <i />
        </span>
        <span>{repositoryName} / {content.workspace}</span>
        <code>{content.ready}</code>
      </div>

      <div className="product-window__body">
        <aside className="product-sidebar" aria-label={content.sidebarLabel}>
          <div className="product-sidebar__heading">
            <span>{content.packagedSkills}</span>
            <strong>{skillCount}</strong>
          </div>
          <ul>
            <li className="is-active">
              <span>Chann Mode</span>
              <code>$chann</code>
            </li>
            <li>
              <span>Interrogate</span>
              <code>$interrogate</code>
            </li>
            <li>
              <span>Diff Summary</span>
              <code>$diff-summary</code>
            </li>
            <li>
              <span>Long Task</span>
              <code>$long-task</code>
            </li>
          </ul>
        </aside>

        <div className="product-editor">
          <div className="product-editor__tab">
            <span>chann</span>
            <code>{content.tab}</code>
          </div>
          <div className="product-editor__content">
            <p className="product-kicker">{content.kicker}</p>
            <h2><Lines lines={content.title} /></h2>
            <p className="product-editor__lede">{content.lede}</p>

            <div className="run-card">
              <span className="run-card__prompt">›</span>
              <code>$chann this endpoint got slow, find out why and fix it</code>
            </div>

            <div className="proof-row">
              {content.proof.map((item) => <span key={item}><i /> {item}</span>)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

const navItemIds = ["why", "explore", "faq", "install"] as const;

interface AppProps {
  locale: Locale;
}

export function App({ locale }: AppProps) {
  const content = getContent(locale);
  const skills = getLocalizedSkills(locale);
  const skill = (id: SkillId) => skills.find((item) => item.id === id)!;
  const landing = content.landing;
  const navItems = navItemIds.map((id) => ({ id, label: content.nav.items[id] }));
  const reduceMotion = useReducedMotion();
  const [activeSection, setActiveSection] = useState<string | null>(null);

  useEffect(() => {
    const sections = navItems
      .map((item) => document.getElementById(item.id))
      .filter((el): el is HTMLElement => el !== null);

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
    sections.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  return (
    <>
      <a className="skip-link" href="#main">
        {content.accessibility.skipToMain}
      </a>

      <header className="site-header">
        <div className="site-header__inner">
          <a
            className="brand"
            href="#main"
            aria-label={formatMessage(content.accessibility.home, { repository: repositoryName })}
          >
            <span>{repositoryName}</span>
          </a>

          <nav className="main-navigation" aria-label={content.nav.label}>
            {navItems.map((item) => (
              <a
                key={item.id}
                href={`#${item.id}`}
                aria-current={activeSection === item.id ? "true" : undefined}
              >
                {item.label}
              </a>
            ))}
          </nav>

          <div className="header-actions">
            <LanguageSwitcher locale={locale} labels={content.language} />
            <ThemeToggle content={content.theme} />
            <a
              className="icon-link"
              href="https://github.com/chann/skills"
              target="_blank"
              rel="noreferrer"
              aria-label={content.accessibility.github}
            >
              <GitHubMark size={18} />
            </a>
          </div>
        </div>
      </header>

      <main id="main">
        <section className="hero" aria-labelledby="hero-title">
          <motion.div
            className="hero__copy"
            initial={reduceMotion ? false : { opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              duration: reduceMotion ? 0 : 0.7,
              ease: [0.16, 1, 0.3, 1],
            }}
          >
            <p className="hero__brand">{content.hero.brand}</p>
            <h1 id="hero-title">
              <Lines lines={content.hero.headline} />
            </h1>
            <p className="hero__lede">
              {formatMessage(content.hero.lede, { count: skills.length })}
            </p>
            <div className="hero__actions">
              <a className="button button--primary" href="#explore">
                {formatMessage(content.hero.primaryAction, { count: skills.length })}
                <ArrowRight size={17} weight="bold" aria-hidden="true" />
              </a>
            </div>
            <p className="hero__meta">
              {formatMessage(content.hero.proof, {
                count: skills.length,
                categories: categoryOrder.length,
              })}
            </p>
            <div className="hero-agents">
              <p>{formatMessage(landing.agentsLabel, { agents: agents.length })}</p>
              <ul>
                {agents.map((agent) => (
                  <li key={agent.id}>
                    <img
                      src={`/skills/agents/${agent.id}.${agent.id === "codex" ? "png" : "svg"}`}
                      alt=""
                      width="24"
                      height="24"
                    />
                    {agent.name}
                  </li>
                ))}
              </ul>
            </div>
          </motion.div>

          <motion.div
            className="hero__preview"
            initial={reduceMotion ? false : { opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              duration: reduceMotion ? 0 : 0.8,
              delay: reduceMotion ? 0 : 0.12,
              ease: [0.16, 1, 0.3, 1],
            }}
          >
            <ProductPreview content={content.productPreview} skillCount={skills.length} />
          </motion.div>
        </section>

        <section className="efficiency section" id="why" aria-labelledby="efficiency-title">
          <div className="efficiency-layout">
            <Reveal className="efficiency-intro">
              <span className="section-label">{content.benefits.label}</span>
              <h2 id="efficiency-title">
                <Lines lines={content.benefits.title} />
              </h2>
              <p>{content.benefits.description}</p>
            </Reveal>

            <div className="efficiency-list">
              {content.benefits.items.map((benefit, index) => {
                const Icon = benefitIcons[index];
                return (
                  <Reveal key={benefit.title}>
                    <article className="efficiency-item">
                      <header>
                        <span className="efficiency-item__icon">
                          <Icon size={20} weight="regular" aria-hidden="true" />
                        </span>
                        <span className="efficiency-item__label">
                          {String(index + 1).padStart(2, "0")} · {benefit.label}
                        </span>
                      </header>
                      <h3>{benefit.title}</h3>
                      <p>{benefit.description}</p>
                    </article>
                  </Reveal>
                );
              })}
            </div>
          </div>
        </section>

        <section className="tagline section" aria-labelledby="tagline-title">
          <div className="tagline__inner">
            <Reveal>
              <span className="section-label">{content.tagline.label}</span>
            </Reveal>
            <TaglineReveal
              id="tagline-title"
              lines={content.tagline.lines}
            />
            <Reveal delay={0.05}>
              <dl
                className="tagline-stats"
                aria-label={content.accessibility.repositoryStats}
              >
                <div>
                  <dt>{content.tagline.stats.skills}</dt>
                  <dd>{skills.length}</dd>
                </div>
                <div>
                  <dt>{content.tagline.stats.categories}</dt>
                  <dd>{categoryOrder.length}</dd>
                </div>
                <div>
                  <dt>{content.tagline.stats.platforms}</dt>
                  <dd>{agents.length}</dd>
                </div>
              </dl>
            </Reveal>
          </div>
        </section>

        <section className="workflow section" id="usage" aria-labelledby="workflow-title">
          <Reveal className="section-heading section-heading--center">
            <span className="section-label">{content.workflow.label}</span>
            <h2 id="workflow-title"><Lines lines={content.workflow.title} /></h2>
            <p>{content.workflow.description}</p>
          </Reveal>

          <Reveal className="workflow-window" delay={0.06}>
            <div className="workflow-window__chrome">
              <span className="window-dots" aria-hidden="true">
                <i />
                <i />
                <i />
              </span>
              <span>agent run</span>
              <code>$diff-summary</code>
            </div>
            <ol className="workflow-grid">
              {content.workflow.steps.map((step) => (
                <li className="workflow-step" key={step.number}>
                  <div>
                    <code>{step.number}</code>
                    <span>{step.label}</span>
                  </div>
                  <h3>{step.title}</h3>
                  <p>{step.description}</p>
                </li>
              ))}
            </ol>
            <div className="workflow-window__status">
              <span><i /> {content.workflow.status}</span>
              <code>{content.workflow.artifact}</code>
            </div>
          </Reveal>
        </section>

        <section className="lifecycle section" id="lifecycle" aria-labelledby="lifecycle-title">
          <Reveal className="section-heading section-heading--center">
            <span className="section-label">{landing.lifecycle.label}</span>
            <h2 id="lifecycle-title"><Lines lines={landing.lifecycle.title} /></h2>
            <p>{landing.lifecycle.description}</p>
          </Reveal>

          <Reveal className="workflow-window" delay={0.06}>
            <ol className="lifecycle-flow" aria-label={landing.lifecycle.flowLabel}>
              {lifecyclePhases.map((phase) => (
                <li key={phase.category}>
                  <span>{content.categories[phase.category].label}</span>
                  <div>
                    <strong>{skill(phase.lead).title}</strong>
                    <small>{skill(phase.second).title}</small>
                  </div>
                  <code>{skill(phase.lead).codexSelector}</code>
                </li>
              ))}
            </ol>
            <ul className="lifecycle-commands" aria-label={landing.lifecycle.commandsLabel}>
              {lifecycleCommands.map((id, index) => (
                <li key={id}>
                  <code>{skill(id).codexSelector}</code>
                  <span>{landing.lifecycle.commands[index]}</span>
                  <small>{content.categories[skill(id).category].label}</small>
                </li>
              ))}
            </ul>
          </Reveal>
        </section>

        <section className="explore-section section" id="explore" aria-labelledby="explore-title">
          <Reveal className="section-heading section-heading--center">
            <span className="section-label">{content.catalog.label}</span>
            <h2 id="explore-title"><Lines lines={content.catalog.title} /></h2>
            <p>{withFlags(content.catalog.description)}</p>
          </Reveal>
          <Reveal delay={0.06}>
            <SkillExplorer
              skills={skills}
              categories={content.categories}
              content={content.catalog}
              copyContent={content.copy}
            />
          </Reveal>
        </section>

        <section className="router section" id="router" aria-labelledby="router-title">
          <div className="efficiency-layout">
            <Reveal className="efficiency-intro">
              <span className="section-label">{landing.router.label}</span>
              <h2 id="router-title">
                <Lines lines={landing.router.title} />
              </h2>
              <p>{formatMessage(landing.router.description, { playbooks: playbookCount })}</p>
              <div className="run-card">
                <span className="run-card__prompt">›</span>
                <code>{skill("chann").example}</code>
              </div>
              <a
                className="button button--quiet"
                href={`https://github.com/chann/skills/blob/main/chann-mode/${
                  locale === "ko" ? "README.ko.md#플레이북" : "README.md#playbooks"
                }`}
                target="_blank"
                rel="noreferrer"
              >
                {formatMessage(landing.router.action, { playbooks: playbookCount })}
                <ArrowRight size={17} weight="bold" aria-hidden="true" />
              </a>
            </Reveal>

            <div className="efficiency-list">
              {landing.router.groups.map((group, index) => {
                const Icon = routerIcons[index];
                return (
                  <Reveal key={group.tag}>
                    <article className="efficiency-item">
                      <header>
                        <span className="efficiency-item__icon">
                          <Icon size={20} weight="regular" aria-hidden="true" />
                        </span>
                        <span className="efficiency-item__label">
                          {String(index + 1).padStart(2, "0")} · {group.tag}
                        </span>
                      </header>
                      <h3>{routerGroups[index].join(" · ")}</h3>
                      <p>{group.description}</p>
                    </article>
                  </Reveal>
                );
              })}
            </div>
          </div>
        </section>

        <section className="faq section" id="faq" aria-labelledby="faq-title">
          <Reveal className="section-heading section-heading--center">
            <span className="section-label">{content.faq.label}</span>
            <h2 id="faq-title">{content.faq.title}</h2>
            <p>{content.faq.description}</p>
          </Reveal>
          <Reveal className="faq-list" delay={0.06}>
            {content.faq.items.map((faq) => (
              <details className="faq-item" key={faq.question}>
                <summary>
                  {faq.question}
                  <Plus size={18} weight="bold" aria-hidden="true" />
                </summary>
                <p>{faq.answer}</p>
              </details>
            ))}
          </Reveal>
        </section>

        <section className="install section" id="install" aria-labelledby="install-title">
          <Reveal className="section-heading section-heading--center">
            <span className="section-label">{content.install.label}</span>
            <h2 id="install-title">
              <Lines
                lines={content.install.title.map((line) =>
                  formatMessage(line, { count: skills.length }),
                )}
              />
            </h2>
            <p>{content.install.description}</p>
          </Reveal>

          <Reveal delay={0.06}>
            <SupportAgents
              content={content.platforms}
              install={content.install}
              copy={content.copy}
              skillCount={skills.length}
            />
          </Reveal>

          <Reveal className="install-actions" delay={0.08}>
            <div className="install-actions__buttons">
              <a className="button button--primary" href="#explore">
                {formatMessage(content.install.exploreAction, { count: skills.length })}
                <ArrowRight size={17} weight="bold" aria-hidden="true" />
              </a>
              <a
                className="button button--quiet"
                href="https://github.com/chann/skills"
                target="_blank"
                rel="noreferrer"
              >
                {content.install.githubAction}
              </a>
            </div>
            <span>{content.install.license}</span>
          </Reveal>
        </section>
      </main>

      <footer className="site-footer">
        <div className="site-footer__grid">
          <div>
            <a
              className="brand"
              href="#main"
              aria-label={formatMessage(content.accessibility.home, { repository: repositoryName })}
            >
              <span>{repositoryName}</span>
            </a>
            <p>{content.footer.tagline}</p>
            <code>{shortInstallCommand}</code>
          </div>
          <nav aria-label={landing.footer.product}>
            <h3>{landing.footer.product}</h3>
            {navItems.map((item) => (
              <a key={item.id} href={`#${item.id}`}>
                {item.label}
              </a>
            ))}
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
            <a href="https://github.com/chann/skills" target="_blank" rel="noreferrer">
              {content.footer.github} ↗
            </a>
            <a href="https://github.com/chann/skills/blob/main/USAGE.md" target="_blank" rel="noreferrer">
              {landing.footer.usage} ↗
            </a>
            <a
              href="https://github.com/chann/skills/blob/main/ARCHITECTURE.md"
              target="_blank"
              rel="noreferrer"
            >
              {landing.footer.architecture} ↗
            </a>
            <a
              href="https://github.com/chann/skills/blob/main/skill-forge/skills/skill-forge/references/skill-package-contract.md"
              target="_blank"
              rel="noreferrer"
            >
              {landing.footer.contract} ↗
            </a>
            <a
              href="https://github.com/chann/skills/blob/main/LICENSE"
              target="_blank"
              rel="noreferrer"
            >
              {content.footer.license} ↗
            </a>
          </nav>
        </div>
        <p className="site-footer__legal">
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
