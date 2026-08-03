import {
  ArrowUpRight,
  MagnifyingGlass,
  X,
} from "@phosphor-icons/react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { useMemo, useRef, useState } from "react";
import { categoryOrder, type SkillCategory } from "../data/skills";
import { formatMessage, type LocalizedSkill } from "../i18n/content";
import type { CatalogContent, SiteContent } from "../i18n/types";
import { CopyButton } from "./CopyButton";

type Filter = "all" | SkillCategory;

interface SkillExplorerProps {
  skills: LocalizedSkill[];
  categories: SiteContent["categories"];
  content: CatalogContent;
  copyContent: SiteContent["copy"];
}

export function SkillExplorer({
  skills,
  categories,
  content,
  copyContent,
}: SkillExplorerProps) {
  const [filter, setFilter] = useState<Filter>("all");
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState<LocalizedSkill["id"]>(skills[0].id);
  const reduceMotion = useReducedMotion();
  const detailRef = useRef<HTMLElement>(null);

  const filtered = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase();
    return skills.filter((skill) => {
      const matchesFilter = filter === "all" || skill.category === filter;
      const haystack = [
        skill.id,
        skill.title,
        skill.summary,
        skill.whenToUse,
        ...skill.tags,
      ]
        .join(" ")
        .toLocaleLowerCase();
      return matchesFilter && (!normalizedQuery || haystack.includes(normalizedQuery));
    });
  }, [filter, query]);

  const selected =
    filtered.find((skill) => skill.id === selectedId) ?? filtered[0] ?? null;

  const selectSkill = (id: LocalizedSkill["id"]) => {
    setSelectedId(id);
    if (!window.matchMedia("(max-width: 767px)").matches) return;

    window.requestAnimationFrame(() => {
      detailRef.current?.scrollIntoView({
        behavior: reduceMotion ? "auto" : "smooth",
        block: "start",
      });
    });
  };

  return (
    <div>
      <div className="category-grid" role="group" aria-label={content.categoryNavigation}>
        {categoryOrder.map((category) => {
          const count = skills.filter((skill) => skill.category === category).length;
          const active = filter === category;
          return (
            <button
              key={category}
              type="button"
              className={`category-card${active ? " is-active" : ""}`}
              onClick={() => setFilter(active ? "all" : category)}
              aria-pressed={active}
            >
              <span className="category-card__head">
                <strong>{categories[category].label}</strong>
                <code>{count}</code>
              </span>
              <span className="category-card__desc">
                {categories[category].description}
              </span>
            </button>
          );
        })}
      </div>

      <div className="explorer">
      <div className="explorer__controls">
        <label className="search-field">
          <span className="sr-only">{content.searchLabel}</span>
          <MagnifyingGlass size={20} aria-hidden="true" />
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={content.searchPlaceholder}
          />
          {query ? (
            <button
              type="button"
              className="search-field__clear"
              onClick={() => setQuery("")}
              aria-label={content.clearSearch}
            >
              <X size={17} weight="bold" aria-hidden="true" />
            </button>
          ) : null}
        </label>

        <div className="filters" role="group" aria-label={content.filtersLabel}>
          <button
            type="button"
            className={filter === "all" ? "is-active" : ""}
            onClick={() => setFilter("all")}
            aria-pressed={filter === "all"}
          >
            {content.all} <span>{skills.length}</span>
          </button>
          {categoryOrder.map((category) => (
            <button
              key={category}
              type="button"
              className={filter === category ? "is-active" : ""}
              onClick={() => setFilter(category)}
              aria-pressed={filter === category}
            >
              {categories[category].label}
              <span>
                {skills.filter((skill) => skill.category === category).length}
              </span>
            </button>
          ))}
        </div>

        <p className="explorer__count" role="status" aria-live="polite">
          {formatMessage(content.count, { count: filtered.length })}
        </p>
      </div>

      {selected ? (
        <div className="explorer__body">
          <div
            className="skill-list"
            id="skill-list"
            role="group"
            aria-label={content.skillList}
          >
            <AnimatePresence initial={false} mode="popLayout">
              {filtered.map((skill) => (
                <motion.button
                  layout={!reduceMotion}
                  key={skill.id}
                  type="button"
                  className={`skill-row${
                    selected.id === skill.id ? " is-selected" : ""
                  }`}
                  onClick={() => selectSkill(skill.id)}
                  initial={reduceMotion ? false : { opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={reduceMotion ? undefined : { opacity: 0, y: -8 }}
                  transition={{ duration: reduceMotion ? 0 : 0.2 }}
                  aria-pressed={selected.id === skill.id}
                  aria-controls="skill-detail"
                >
                  <span className="skill-row__main">
                    <span>{skill.title}</span>
                    <code>{skill.codexSelector}</code>
                  </span>
                  <span className="skill-row__category">
                    {categories[skill.category].label}
                  </span>
                  <ArrowUpRight size={18} aria-hidden="true" />
                </motion.button>
              ))}
            </AnimatePresence>
          </div>

          <AnimatePresence mode="wait">
            <motion.article
              ref={detailRef}
              id="skill-detail"
              key={selected.id}
              className="skill-detail"
              initial={reduceMotion ? false : { opacity: 0, x: 14 }}
              animate={{ opacity: 1, x: 0 }}
              exit={reduceMotion ? undefined : { opacity: 0, x: -10 }}
              transition={{ duration: reduceMotion ? 0 : 0.22 }}
            >
              <div className="skill-detail__header">
                <span className="skill-detail__package">
                  {categories[selected.category].label}
                </span>
                <h3>{selected.title}</h3>
                <p>{selected.summary}</p>
              </div>

              <dl className="skill-detail__facts">
                <div>
                  <dt>{content.whenToUse}</dt>
                  <dd>{selected.whenToUse}</dd>
                </div>
                <div>
                  <dt>{content.result}</dt>
                  <dd>{selected.result}</dd>
                </div>
              </dl>

              <div className="selector-pair">
                <div>
                  <span>Codex</span>
                  <code>{selected.codexSelector}</code>
                </div>
                <CopyButton value={selected.codexSelector} content={copyContent} compact />
              </div>
              <div className="selector-pair">
                <div>
                  <span>Claude Code</span>
                  <code>{selected.claudeSelector}</code>
                </div>
                <CopyButton value={selected.claudeSelector} content={copyContent} compact />
              </div>

              <div className="example-command">
                <span>{content.exampleRequest}</span>
                <code tabIndex={0}>{selected.example}</code>
                <CopyButton
                  value={selected.example}
                  content={copyContent}
                  label={content.exampleCopy}
                />
              </div>

              {selected.aliases?.length ? (
                <p className="skill-detail__alias">
                  {content.aliases}: <code>{selected.aliases.join(", ")}</code>
                </p>
              ) : null}
            </motion.article>
          </AnimatePresence>
        </div>
      ) : (
        <div className="empty-state" role="status">
          <MagnifyingGlass size={28} aria-hidden="true" />
          <h3>{content.emptyTitle}</h3>
          <p>{content.emptyDescription}</p>
          <button
            type="button"
            onClick={() => {
              setQuery("");
              setFilter("all");
            }}
          >
            {content.showAll}
          </button>
        </div>
      )}
      </div>
    </div>
  );
}
