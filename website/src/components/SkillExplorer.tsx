import {
  ArrowUpRight,
  MagnifyingGlass,
  X,
} from "@phosphor-icons/react";
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { useMemo, useRef, useState } from "react";
import {
  categoryMeta,
  categoryOrder,
  skills,
  type SkillCategory,
} from "../data/skills";
import { CopyButton } from "./CopyButton";

type Filter = "all" | SkillCategory;

export function SkillExplorer() {
  const [filter, setFilter] = useState<Filter>("all");
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState(skills[0].id);
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

  const selectSkill = (id: string) => {
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
      <div className="category-grid" role="group" aria-label="분류별 바로가기">
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
                <strong>{categoryMeta[category].label}</strong>
                <code>{count}</code>
              </span>
              <p>{categoryMeta[category].description}</p>
            </button>
          );
        })}
      </div>

      <div className="explorer">
      <div className="explorer__controls">
        <label className="search-field">
          <span className="sr-only">스킬 검색</span>
          <MagnifyingGlass size={20} aria-hidden="true" />
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="작업, 산출물, 스킬 이름 검색"
          />
          {query ? (
            <button
              type="button"
              className="search-field__clear"
              onClick={() => setQuery("")}
              aria-label="검색어 지우기"
            >
              <X size={17} weight="bold" aria-hidden="true" />
            </button>
          ) : null}
        </label>

        <div className="filters" role="group" aria-label="스킬 분류">
          <button
            type="button"
            className={filter === "all" ? "is-active" : ""}
            onClick={() => setFilter("all")}
            aria-pressed={filter === "all"}
          >
            전체 <span>{skills.length}</span>
          </button>
          {categoryOrder.map((category) => (
            <button
              key={category}
              type="button"
              className={filter === category ? "is-active" : ""}
              onClick={() => setFilter(category)}
              aria-pressed={filter === category}
            >
              {categoryMeta[category].label}
              <span>
                {skills.filter((skill) => skill.category === category).length}
              </span>
            </button>
          ))}
        </div>

        <p className="explorer__count" role="status" aria-live="polite">
          <strong>{filtered.length}</strong>개 스킬
        </p>
      </div>

      {selected ? (
        <div className="explorer__body">
          <div
            className="skill-list"
            id="skill-list"
            role="group"
            aria-label="스킬 목록"
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
                    {categoryMeta[skill.category].label}
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
                  {categoryMeta[selected.category].label}
                </span>
                <h3>{selected.title}</h3>
                <p>{selected.summary}</p>
              </div>

              <dl className="skill-detail__facts">
                <div>
                  <dt>이럴 때</dt>
                  <dd>{selected.whenToUse}</dd>
                </div>
                <div>
                  <dt>결과</dt>
                  <dd>{selected.result}</dd>
                </div>
              </dl>

              <div className="selector-pair">
                <div>
                  <span>Codex</span>
                  <code>{selected.codexSelector}</code>
                </div>
                <CopyButton value={selected.codexSelector} compact />
              </div>
              <div className="selector-pair">
                <div>
                  <span>Claude Code</span>
                  <code>{selected.claudeSelector}</code>
                </div>
                <CopyButton value={selected.claudeSelector} compact />
              </div>

              <div className="example-command">
                <span>예시 요청</span>
                <code tabIndex={0}>{selected.example}</code>
                <CopyButton value={selected.example} label="예시 복사" />
              </div>

              {selected.aliases?.length ? (
                <p className="skill-detail__alias">
                  별칭: <code>{selected.aliases.join(", ")}</code>
                </p>
              ) : null}
            </motion.article>
          </AnimatePresence>
        </div>
      ) : (
        <div className="empty-state" role="status">
          <MagnifyingGlass size={28} aria-hidden="true" />
          <h3>일치하는 스킬이 없습니다</h3>
          <p>검색어를 줄이거나 다른 분류를 선택해보세요.</p>
          <button
            type="button"
            onClick={() => {
              setQuery("");
              setFilter("all");
            }}
          >
            전체 스킬 보기
          </button>
        </div>
      )}
      </div>
    </div>
  );
}
