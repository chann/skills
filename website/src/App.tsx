import {
  ArrowRight,
  CheckCircle,
  GithubLogo,
  GitPullRequest,
  NotePencil,
  ShieldCheck,
  Sparkle,
} from "@phosphor-icons/react";
import { motion, useReducedMotion } from "motion/react";
import { CopyButton } from "./components/CopyButton";
import { Reveal } from "./components/Reveal";
import { SkillExplorer } from "./components/SkillExplorer";
import { ThemeToggle } from "./components/ThemeToggle";

const installCommand =
  "npx skills add chann/skills --skill '*' --agent claude-code codex --global --yes";

const outcomes = [
  {
    title: "변경을 검토한다",
    description: "결함은 review로 찾고, 의도와 구조는 summary로 이해합니다.",
    selector: "$code-review",
    icon: ShieldCheck,
    tone: "blue",
  },
  {
    title: "맥락을 설명한다",
    description: "원본 diff부터 이중언어 보고서와 이해도 퀴즈까지 이어집니다.",
    selector: "$diff-summary",
    icon: NotePencil,
    tone: "plain",
  },
  {
    title: "Git을 안전하게 움직인다",
    description: "명시적 스테이징, 검증, push parity를 하나의 계약으로 묶습니다.",
    selector: "$git-commit-push-realtime",
    icon: GitPullRequest,
    tone: "plain",
  },
  {
    title: "큰 작업을 끝까지 운영한다",
    description: "마일스톤, 작업 분리, 리뷰, 완료 감사를 한 흐름으로 유지합니다.",
    selector: "$long-task",
    icon: Sparkle,
    tone: "muted",
  },
];

export function App() {
  const reduceMotion = useReducedMotion();

  return (
    <>
      <a className="skip-link" href="#main">
        본문으로 건너뛰기
      </a>

      <header className="site-header">
        <a className="brand" href="#" aria-label="skills 홈">
          <span className="brand__mark" aria-hidden="true">
            <span />
            <span />
            <span />
          </span>
          <span>skills</span>
        </a>

        <nav aria-label="주요 메뉴">
          <a href="#explore">스킬 찾기</a>
          <a href="#usage">사용법</a>
          <a href="#install">설치</a>
        </nav>

        <div className="header-actions">
          <ThemeToggle />
          <a
            className="github-link"
            href="https://github.com/chann/skills"
            target="_blank"
            rel="noreferrer"
            aria-label="GitHub에서 보기"
          >
            <GithubLogo size={19} weight="bold" aria-hidden="true" />
          </a>
        </div>
      </header>

      <main id="main">
        <section className="hero" aria-labelledby="hero-title">
          <motion.div
            className="hero__copy"
            initial={reduceMotion ? false : { opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              duration: reduceMotion ? 0 : 0.6,
              ease: [0.16, 1, 0.3, 1],
            }}
          >
            <p className="eyebrow">Reusable agent workflows</p>
            <h1 id="hero-title">
              반복 작업을,
              <br />
              이름 있는 스킬로.
            </h1>
            <p className="hero__lede">
              리뷰부터 Git 정리까지. 검증된 18개 워크플로를 필요한 순간 바로
              호출하세요.
            </p>
            <div className="hero__actions">
              <a className="button button--primary" href="#explore">
                스킬 찾기
                <ArrowRight size={17} weight="bold" aria-hidden="true" />
              </a>
              <a className="button button--secondary" href="#install">
                설치
              </a>
            </div>
          </motion.div>

          <motion.figure
            className="hero__visual"
            initial={reduceMotion ? false : { opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{
              duration: reduceMotion ? 0 : 0.72,
              delay: reduceMotion ? 0 : 0.06,
              ease: [0.16, 1, 0.3, 1],
            }}
          >
            <img
              src="./assets/catalog-hero-minimal.webp"
              srcSet="./assets/catalog-hero-minimal-768.webp 768w, ./assets/catalog-hero-minimal.webp 1536w"
              sizes="(max-width: 767px) calc(100vw - 32px), 56vw"
              alt="빈 종이 카드와 금속 클립을 잇는 잿빛 파란 실"
              width="1536"
              height="1024"
              fetchPriority="high"
            />
          </motion.figure>
        </section>

        <section className="outcomes section" aria-labelledby="outcomes-title">
          <Reveal className="section-heading">
            <h2 id="outcomes-title">도구보다, 끝낼 일을 고르세요.</h2>
            <p>
              각 스킬은 호출 조건, 안전 규칙, 확인 가능한 산출물을 하나의 계약으로
              묶습니다.
            </p>
          </Reveal>

          <div className="outcome-grid">
            {outcomes.map((outcome, index) => {
              const Icon = outcome.icon;
              return (
                <Reveal
                  key={outcome.title}
                  className={`outcome outcome--${outcome.tone}`}
                  delay={index * 0.05}
                >
                  <div className="outcome__top">
                    <Icon size={24} weight="duotone" aria-hidden="true" />
                    <code>{outcome.selector}</code>
                  </div>
                  <div>
                    <h3>{outcome.title}</h3>
                    <p>{outcome.description}</p>
                  </div>
                </Reveal>
              );
            })}
          </div>
        </section>

        <section
          className="explore-section section"
          id="explore"
          aria-labelledby="explore-title"
        >
          <Reveal className="section-heading">
            <h2 id="explore-title">18개 스킬을, 한 자리에서.</h2>
            <p>
              작업이나 산출물로 검색하고, 플랫폼에 맞는 selector를 바로
              복사하세요.
            </p>
          </Reveal>
          <Reveal delay={0.06}>
            <SkillExplorer />
          </Reveal>
        </section>

        <section
          className="usage section"
          id="usage"
          aria-labelledby="usage-title"
        >
          <Reveal className="usage__image">
            <img
              src="./assets/workflow-trays-minimal.webp"
              alt="빈 메모, 정리된 카드, 완성 문서가 차례로 놓인 세 개의 종이 트레이"
              width="1122"
              height="1402"
              loading="lazy"
            />
          </Reveal>

          <div className="usage__content">
            <Reveal className="section-heading">
              <h2 id="usage-title">평소 말하듯 요청하세요.</h2>
              <p>
                selector를 쓰면 정확하고, 자연어로 말하면 조건에 맞는 스킬이
                선택됩니다.
              </p>
            </Reveal>

            <div className="usage-flow">
              <Reveal className="usage-flow__item" delay={0.04}>
                <span>요청을 말한다</span>
                <p>“마지막 커밋을 리뷰하고 HTML 보고서로 보여줘.”</p>
              </Reveal>
              <Reveal className="usage-flow__item" delay={0.08}>
                <span>계약을 읽는다</span>
                <p>범위, 안전 규칙, 도구, 결과 형식을 SKILL.md에서 불러옵니다.</p>
              </Reveal>
              <Reveal className="usage-flow__item" delay={0.12}>
                <span>결과로 증명한다</span>
                <p>보고서, 커밋, 핸드오프, 검증 로그처럼 확인 가능한 결과를 남깁니다.</p>
              </Reveal>
            </div>
          </div>
        </section>

        <section className="selectors section" aria-labelledby="selectors-title">
          <Reveal className="section-heading">
            <h2 id="selectors-title">이름은 같고, prefix만 다릅니다.</h2>
            <p>Codex는 $, Claude Code는 /를 스킬 이름 앞에 붙입니다.</p>
          </Reveal>

          <div className="selector-ledger">
            <Reveal className="selector-ledger__row">
              <div>
                <span>Codex</span>
                <strong>$</strong>
              </div>
              <code tabIndex={0}>$diff-summary main..dev</code>
              <CopyButton value="$diff-summary main..dev" />
            </Reveal>
            <Reveal className="selector-ledger__row" delay={0.06}>
              <div>
                <span>Claude Code</span>
                <strong>/</strong>
              </div>
              <code tabIndex={0}>/diff-summary main..dev</code>
              <CopyButton value="/diff-summary main..dev" />
            </Reveal>
          </div>
        </section>

        <section
          className="install section"
          id="install"
          aria-labelledby="install-title"
        >
          <Reveal className="install__content">
            <div className="section-heading">
              <h2 id="install-title">한 번 설치하고, 바로 호출하세요.</h2>
              <p>
                installer의 symlink 방식으로 Claude Code와 Codex에 함께
                연결합니다.
              </p>
            </div>

            <div className="install-command">
              <span>Terminal</span>
              <code tabIndex={0}>{installCommand}</code>
              <CopyButton value={installCommand} label="명령 복사" />
            </div>

            <ul className="install-notes" aria-label="설치 결과">
              <li>
                <CheckCircle size={18} weight="fill" aria-hidden="true" />
                18개 스킬
              </li>
              <li>
                <CheckCircle size={18} weight="fill" aria-hidden="true" />
                전역 symlink
              </li>
              <li>
                <CheckCircle size={18} weight="fill" aria-hidden="true" />
                두 플랫폼
              </li>
            </ul>
          </Reveal>

          <Reveal className="install__image" delay={0.08}>
            <img
              src="./assets/installation-rail-minimal.webp"
              alt="금속 레일과 잿빛 파란 끈으로 연결된 다섯 장의 빈 카드"
              width="1254"
              height="1254"
              loading="lazy"
            />
          </Reveal>
        </section>

        <section className="closing section" aria-labelledby="closing-title">
          <Reveal>
            <h2 id="closing-title">반복하지 말고, 호출하세요.</h2>
            <p>팀의 기준을 설치 가능한 워크플로로 남겨두세요.</p>
            <a
              className="button button--primary"
              href="https://github.com/chann/skills"
              target="_blank"
              rel="noreferrer"
            >
              GitHub에서 보기
              <ArrowRight size={17} weight="bold" aria-hidden="true" />
            </a>
          </Reveal>
        </section>
      </main>

      <footer className="site-footer">
        <a className="brand" href="#" aria-label="skills 홈">
          <span className="brand__mark" aria-hidden="true">
            <span />
            <span />
            <span />
          </span>
          <span>skills</span>
        </a>
        <p>Practical agent workflows for software engineering.</p>
        <a
          href="https://github.com/chann/skills"
          target="_blank"
          rel="noreferrer"
        >
          GitHub에서 보기
          <ArrowRight size={15} weight="bold" aria-hidden="true" />
        </a>
      </footer>
    </>
  );
}
