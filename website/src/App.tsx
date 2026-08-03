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
import { Reveal } from "./components/Reveal";
import { SkillExplorer } from "./components/SkillExplorer";
import { TaglineReveal } from "./components/TaglineReveal";
import { ThemeToggle } from "./components/ThemeToggle";
import { categoryOrder, skills } from "./data/skills";

const repositoryName = "chann/skills";
const installCommand =
  "npx skills add chann/skills --skill '*' --agent claude-code codex --global --yes";
const updateCommand = "npx skills update chann/skills";

const efficiencyBenefits = [
  {
    label: "Reusable instructions",
    title: "같은 지침을 다시 만들지 않습니다.",
    description:
      "실행 순서와 예시, 안전 규칙을 안정된 SKILL.md로 유지합니다. 반복 요청에서 동일한 앞부분이 유지되므로 지원되는 모델의 프롬프트 캐시를 활용하기 좋은 구조가 됩니다.",
    icon: Repeat,
  },
  {
    label: "Deterministic scripts",
    title: "정해진 일은 스크립트가 처리합니다.",
    description:
      "파일 탐색, 형식 검사, 데이터 동기화처럼 결과가 명확한 단계는 스크립트로 실행합니다. 모델이 같은 절차를 매번 다시 추론하지 않게 해 LLM 사용 범위를 줄입니다.",
    icon: TerminalWindow,
  },
  {
    label: "Focused judgment",
    title: "LLM은 판단에 집중합니다.",
    description:
      "요구사항 해석, 코드 검토, 위험 판단처럼 문맥이 필요한 부분에 모델을 사용하고, 실행 순서와 완료 조건은 스킬이 고정합니다.",
    icon: Brain,
  },
];

const workflowSteps = [
  {
    number: "01",
    label: "Capture",
    title: "반복을 포착합니다",
    description: "자주 되풀이하는 요청과 산출물을 찾습니다.",
  },
  {
    number: "02",
    label: "Define",
    title: "기준을 고정합니다",
    description: "실행 순서, 안전 규칙과 완료 조건을 스킬에 남깁니다.",
  },
  {
    number: "03",
    label: "Separate",
    title: "역할을 나눕니다",
    description: "판단은 LLM이 맡고, 결과가 정해진 단계는 스크립트가 실행합니다.",
  },
];

const faqs = [
  {
    q: "스킬이 정확히 뭔가요?",
    a: "에이전트가 특정 작업을 어떻게 수행할지 정의한 SKILL.md 문서입니다. 실행 순서, 안전 규칙, 결과 형식까지 담고 있어 같은 요청이 항상 같은 기준으로 처리됩니다.",
  },
  {
    q: "일반 프롬프트와 뭐가 다른가요?",
    a: "프롬프트는 대화가 끝나면 사라지지만 스킬은 파일로 남습니다. 버전 관리되고, 팀과 공유되고, $review-me처럼 이름으로 다시 호출할 수 있습니다.",
  },
  {
    q: "스킬을 쓰면 토큰이 항상 줄어드나요?",
    a: "항상 보장되지는 않습니다. 프롬프트 캐시는 사용하는 모델과 지침 길이, 동일한 앞부분의 유지 여부에 따라 달라집니다. 다만 스킬은 반복 지침을 안정된 형태로 재사용하고, 스크립트로 처리할 단계를 분리해 불필요한 LLM 작업을 줄이도록 설계됩니다.",
  },
  {
    q: "어떤 작업을 스크립트로 처리하나요?",
    a: "입력과 결과를 규칙으로 확인할 수 있는 작업입니다. 파일 검색, 형식 검사, 카탈로그 동기화와 테스트 실행은 스크립트에 맡기고, 해석과 검토가 필요한 작업은 LLM이 담당합니다.",
  },
  {
    q: "어떤 에이전트에서 쓸 수 있나요?",
    a: "Claude Code와 Codex를 기본 지원합니다. 같은 SKILL.md를 Codex는 $이름, Claude Code는 /이름으로 호출합니다. 설치 도구는 Gemini CLI, GitHub Copilot CLI 같은 다른 에이전트도 지원합니다.",
  },
  {
    q: "설치하면 내 컴퓨터에 무엇이 생기나요?",
    a: "npx skills add가 저장소를 내려받고 각 에이전트가 같은 원본을 읽도록 연결합니다. 원본은 한 곳에 유지되며, 연결만 지우면 깔끔하게 제거됩니다.",
  },
  {
    q: "스킬이 마음대로 커밋하거나 푸시하지 않나요?",
    a: "각 스킬에는 안전 규칙이 분명히 적혀 있습니다. 예를 들어 git 스킬은 명시적 스테이징만 사용하고 force push를 금지하며, 푸시가 거부되면 멈추고 보고합니다.",
  },
  {
    q: "일부 스킬만 설치할 수 있나요?",
    a: "네. 설치 명령의 --skill '*' 자리에 원하는 스킬 이름만 지정하면 됩니다. 각 스킬의 README에 개별 설치 방법이 있습니다.",
  },
  {
    q: "업데이트는 어떻게 하나요?",
    a: `${updateCommand} 명령을 실행하면 설치된 스킬을 최신 버전으로 업데이트합니다.`,
  },
  {
    q: "비용이나 라이선스 제한이 있나요?",
    a: "없습니다. 전체가 MIT 라이선스 오픈소스입니다. 저장소를 포크해서 팀 규칙에 맞게 고쳐 써도 됩니다.",
  },
];

function ProductPreview() {
  return (
    <div className="product-window">
      <div className="product-window__chrome">
        <span className="window-dots" aria-hidden="true">
          <i />
          <i />
          <i />
        </span>
        <span>{repositoryName} / workspace</span>
        <code>ready</code>
      </div>

      <div className="product-window__body">
        <aside className="product-sidebar" aria-label="스킬 예시 목록">
          <div className="product-sidebar__heading">
            <span>Packaged skills</span>
            <strong>{skills.length}</strong>
          </div>
          <ul>
            <li className="is-active">
              <span>Review Me</span>
              <code>$review-me</code>
            </li>
            <li>
              <span>Code Review</span>
              <code>$code-review</code>
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
            <span>review-me</span>
            <code>SKILL.md</code>
          </div>
          <div className="product-editor__content">
            <p className="product-kicker">DECISION REVIEW</p>
            <h2>계획의 모든 선택을<br />끝까지 검토합니다.</h2>
            <p className="product-editor__lede">
              전제부터 마지막 선택지까지 추적하고, 확인된 근거와 남은 위험을
              분리해 보여줍니다.
            </p>

            <div className="run-card">
              <span className="run-card__prompt">›</span>
              <code>$review-me review our billing migration plan</code>
            </div>

            <div className="proof-row">
              <span><i /> 12 decisions traced</span>
              <span><i /> 3 risks surfaced</span>
              <span><i /> report ready</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

const navItems = [
  { id: "why", label: "소개" },
  { id: "explore", label: "스킬 찾기" },
  { id: "faq", label: "FAQ" },
  { id: "install", label: "설치" },
];

export function App() {
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
        본문으로 건너뛰기
      </a>

      <header className="site-header">
        <div className="site-header__inner">
          <a className="brand" href="#main" aria-label={`${repositoryName} 홈`}>
            <span>{repositoryName}</span>
          </a>

          <nav aria-label="주요 메뉴">
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
            <ThemeToggle />
            <a
              className="icon-link"
              href="https://github.com/chann/skills"
              target="_blank"
              rel="noreferrer"
              aria-label="GitHub에서 보기"
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
            <p className="hero__brand">{repositoryName}</p>
            <h1 id="hero-title">
              <span>어제의 반복이,</span>
              <span>오늘의 스킬로.</span>
            </h1>
            <p className="hero__lede">
              Claude Code와 Codex에서 되풀이하던 소프트웨어 작업을 검증 가능한
              {` ${skills.length}개의 `}워크플로로 바꿨습니다. 반복 지침은
              캐시하기 좋은 형태로 재사용하고, 결과가 정해진 단계는 스크립트에
              맡겨 LLM이 필요한 판단에 집중하게 합니다.
            </p>
            <div className="hero__actions">
              <a className="button button--primary" href="#explore">
                {skills.length}개 스킬 살펴보기
                <ArrowRight size={17} weight="bold" aria-hidden="true" />
              </a>
            </div>
            <p className="hero__meta">
              {skills.length} packaged skills · {categoryOrder.length} categories ·
              Claude Code + Codex · MIT
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
            <ProductPreview />
          </motion.div>
        </section>

        <section className="efficiency section" id="why" aria-labelledby="efficiency-title">
          <div className="efficiency-layout">
            <Reveal className="efficiency-intro">
              <span className="section-label">Why skills</span>
              <h2 id="efficiency-title">반복할수록,<br />덜 설명하고 더 선명하게.</h2>
              <p>
                스킬은 반복 지침을 재사용하고, 정해진 절차를 스크립트에 맡겨
                모델이 꼭 필요한 판단에 집중하게 합니다.
              </p>
              <dl className="efficiency-stats" aria-label="스킬 저장소 현황">
                <div><dt>Skills</dt><dd>{skills.length}</dd></div>
                <div><dt>Categories</dt><dd>{categoryOrder.length}</dd></div>
                <div><dt>Platforms</dt><dd>2</dd></div>
              </dl>
            </Reveal>

            <div className="efficiency-list">
              {efficiencyBenefits.map((benefit, index) => {
                const Icon = benefit.icon;
                return (
                  <Reveal key={benefit.title}>
                    <article className="efficiency-item">
                      <span className="efficiency-item__icon">
                        <Icon size={22} weight="regular" aria-hidden="true" />
                      </span>
                      <div>
                        <span>{String(index + 1).padStart(2, "0")} · {benefit.label}</span>
                        <h3>{benefit.title}</h3>
                        <p>{benefit.description}</p>
                      </div>
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
              <span className="section-label">Repeatable by design</span>
            </Reveal>
            <TaglineReveal
              id="tagline-title"
              lines={[
                "좋은 프롬프트는 한 번 쓰고 사라집니다.",
                "하지만 스킬로 만들면 기본기가 됩니다.",
              ]}
            />
            <Reveal delay={0.05}>
              <dl className="tagline-stats">
                <div>
                  <dt>Packaged skills</dt>
                  <dd>{skills.length}</dd>
                </div>
                <div>
                  <dt>Categories</dt>
                  <dd>{categoryOrder.length}</dd>
                </div>
                <div>
                  <dt>Platforms</dt>
                  <dd>2</dd>
                </div>
              </dl>
            </Reveal>
          </div>
        </section>

        <section className="workflow section" id="usage" aria-labelledby="workflow-title">
          <Reveal className="section-heading section-heading--center">
            <span className="section-label">How it works</span>
            <h2 id="workflow-title">반복 작업이 스킬이 되는,<br />세 단계.</h2>
            <p>반복을 포착하고 기준을 고정한 뒤, LLM과 스크립트의 역할을 나눕니다.</p>
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
              {workflowSteps.map((step) => (
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
              <span><i /> completed</span>
              <code>report.html · tests passed · push confirmed</code>
            </div>
          </Reveal>
        </section>

        <section className="explore-section section" id="explore" aria-labelledby="explore-title">
          <Reveal className="section-heading section-heading--center">
            <span className="section-label">Skill catalog</span>
            <h2 id="explore-title">필요한 워크플로를<br />한 자리에서.</h2>
            <p>작업이나 산출물로 검색하고, 플랫폼에 맞는 호출 명령을 바로 복사하세요.</p>
          </Reveal>
          <Reveal delay={0.06}>
            <SkillExplorer />
          </Reveal>
        </section>

        <section className="platforms section" aria-labelledby="platforms-title">
          <Reveal className="platforms__copy">
            <span className="section-label">One skill, two commands</span>
            <h2 id="platforms-title">같은 스킬,<br />호출 방법만 다르게.</h2>
            <p>
              하나의 SKILL.md를 두 도구가 같은 방식으로 읽습니다. Codex는
              <code>$</code>, Claude Code는 <code>/</code>를 이름 앞에 붙입니다.
            </p>
          </Reveal>

          <Reveal className="platform-window" delay={0.08}>
            <div className="platform-window__chrome">
              <span>diff-summary</span>
              <code>SKILL.md</code>
            </div>
            <div className="platform-contract">
              <span>Shared instructions</span>
              <strong>diff-summary</strong>
              <p>원본 근거에서 이중언어 보고서와 이해도 확인까지.</p>
            </div>
            <div className="platform-targets">
              <div className="platform-node">
                <div>
                  <span>Codex</span>
                  <code>$diff-summary</code>
                </div>
                <CopyButton value="$diff-summary" compact />
              </div>
              <div className="platform-node">
                <div>
                  <span>Claude Code</span>
                  <code>/diff-summary</code>
                </div>
                <CopyButton value="/diff-summary" compact />
              </div>
            </div>
          </Reveal>
        </section>

        <section className="faq section" id="faq" aria-labelledby="faq-title">
          <Reveal className="section-heading section-heading--center">
            <span className="section-label">FAQ</span>
            <h2 id="faq-title">자주 묻는 질문</h2>
            <p>설치 전에 확인할 것들을 모았습니다.</p>
          </Reveal>
          <Reveal className="faq-list" delay={0.06}>
            {faqs.map((faq) => (
              <details className="faq-item" key={faq.q}>
                <summary>
                  {faq.q}
                  <Plus size={18} weight="bold" aria-hidden="true" />
                </summary>
                <p>{faq.a}</p>
              </details>
            ))}
          </Reveal>
        </section>

        <section className="install section" id="install" aria-labelledby="install-title">
          <Reveal className="section-heading section-heading--center">
            <span className="section-label">Get skills</span>
            <h2 id="install-title">{skills.length}개 스킬을,<br />한 명령으로.</h2>
            <p>공식 설치 도구가 Claude Code와 Codex에서 바로 쓸 수 있게 연결합니다.</p>
          </Reveal>

          <Reveal className="install-card" delay={0.06}>
            <div className="install-card__heading">
              <span className="install-badge">npm</span>
              <div>
                <h3>두 플랫폼에 함께 설치</h3>
                <p>원본 저장소를 유지한 채 각 에이전트의 스킬 폴더에 연결합니다.</p>
              </div>
            </div>
            <div className="install-command">
              <span aria-hidden="true">$</span>
              <code tabIndex={0}>{installCommand}</code>
              <CopyButton value={installCommand} label="명령 복사" />
            </div>
            <ul className="install-notes" aria-label="설치 결과">
              <li><CheckCircle size={17} weight="fill" aria-hidden="true" /> {skills.length}개 스킬</li>
              <li><CheckCircle size={17} weight="fill" aria-hidden="true" /> 언제든 제거할 수 있는 전역 연결</li>
              <li><CheckCircle size={17} weight="fill" aria-hidden="true" /> Claude Code + Codex</li>
            </ul>
          </Reveal>

          <Reveal className="install-actions" delay={0.08}>
            <div className="install-actions__buttons">
              <a className="button button--primary" href="#explore">
                {skills.length}개 스킬 탐색
                <ArrowRight size={17} weight="bold" aria-hidden="true" />
              </a>
              <a
                className="button button--quiet"
                href="https://github.com/chann/skills"
                target="_blank"
                rel="noreferrer"
              >
                GitHub에서 보기
              </a>
            </div>
            <span>MIT License · open source</span>
          </Reveal>
        </section>
      </main>

      <footer className="site-footer">
        <div className="site-footer__top">
          <a className="brand" href="#main" aria-label={`${repositoryName} 홈`}>
            <span>{repositoryName}</span>
          </a>
          <p>Practical agent workflows for software engineering.</p>
          <div>
            <a
              href="https://github.com/chann/skills/blob/main/LICENSE"
              target="_blank"
              rel="noreferrer"
            >
              MIT License
            </a>
            <a
              href="https://github.com/chann/skills"
              target="_blank"
              rel="noreferrer"
            >
              GitHub <ArrowRight size={14} weight="bold" aria-hidden="true" />
            </a>
          </div>
        </div>
        <div className="site-footer__word" aria-hidden="true">
          {repositoryName.split("").map((letter, index) => (
            <motion.span
              key={index}
              initial={reduceMotion ? false : { y: "0.42em", opacity: 0 }}
              whileInView={{ y: 0, opacity: 1 }}
              viewport={{ once: true, amount: 0.2 }}
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
