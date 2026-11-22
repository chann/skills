import {
  ArrowRight,
  Brain,
  CheckCircle,
  Plus,
  Repeat,
  TerminalWindow,
} from "@phosphor-icons/react";
import { motion, useReducedMotion } from "motion/react";
import { useEffect, useState } from "react";
import { CopyButton } from "./components/CopyButton";
import { GitHubMark } from "./components/GitHubMark";
import { LanguageSwitcher } from "./components/LanguageSwitcher";
import { Reveal } from "./components/Reveal";
import { SkillExplorer } from "./components/SkillExplorer";
import { Lines, withFlags } from "./components/Text";
import { TaglineReveal } from "./components/TaglineReveal";
import { agents, installCommand } from "./data/agents";
import { SupportAgents } from "./components/SupportAgents";
import { ThemeToggle } from "./components/ThemeToggle";
import { categoryOrder } from "./data/skills";
import { formatMessage, getContent, getLocalizedSkills } from "./i18n/content";
import type { Locale, ProductPreviewContent } from "./i18n/types";

const repositoryName = "chann/skills";
const installAllCommand = installCommand(agents.map((agent) => agent.id).join(" "));
const benefitIcons = [Repeat, TerminalWindow, Brain] as const;

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

const navItemIds = ["why", "explore", "agents", "faq", "install"] as const;

interface AppProps {
  locale: Locale;
}

export function App({ locale }: AppProps) {
  const content = getContent(locale);
  const skills = getLocalizedSkills(locale);
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

        <SupportAgents content={content.platforms} copy={content.copy} />

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

          <Reveal className="install-card" delay={0.06}>
            <div className="install-card__heading">
              <span className="install-badge">npm</span>
              <div>
                <h3>{content.install.cardTitle}</h3>
                <p>{content.install.cardDescription}</p>
              </div>
            </div>
            <div className="install-command">
              <span aria-hidden="true">$</span>
              <code tabIndex={0}>{installAllCommand}</code>
              <CopyButton
                value={installAllCommand}
                content={content.copy}
                label={content.install.copyLabel}
              />
            </div>
            <ul className="install-notes" aria-label={content.install.resultsLabel}>
              <li><CheckCircle size={17} weight="fill" aria-hidden="true" /> {formatMessage(content.install.skillResult, { count: skills.length })}</li>
              <li><CheckCircle size={17} weight="fill" aria-hidden="true" /> {content.install.linkResult}</li>
              <li><CheckCircle size={17} weight="fill" aria-hidden="true" /> {content.install.platformsResult}</li>
            </ul>
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
        <div className="site-footer__top">
          <a
            className="brand"
            href="#main"
            aria-label={formatMessage(content.accessibility.home, { repository: repositoryName })}
          >
            <span>{repositoryName}</span>
          </a>
          <p>{content.footer.tagline}</p>
          <div>
            <a
              href="https://github.com/chann/skills/blob/main/LICENSE"
              target="_blank"
              rel="noreferrer"
            >
              {content.footer.license}
            </a>
            <a
              href="https://github.com/chann/skills"
              target="_blank"
              rel="noreferrer"
            >
              {content.footer.github} <ArrowRight size={14} weight="bold" aria-hidden="true" />
            </a>
          </div>
        </div>
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
