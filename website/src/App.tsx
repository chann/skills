import {
  ArrowDown,
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
  },
  {
    title: "맥락을 설명한다",
    description: "원본 diff부터 이중언어 보고서와 이해도 퀴즈까지 이어집니다.",
    selector: "$diff-summary",
    icon: NotePencil,
  },
  {
    title: "Git을 안전하게 움직인다",
    description: "명시적 스테이징, 검증, push parity를 하나의 계약으로 묶습니다.",
    selector: "$git-commit-push-realtime",
    icon: GitPullRequest,
  },
  {
    title: "큰 작업을 끝까지 운영한다",
    description: "마일스톤, 작업 분리, 리뷰, 완료 감사를 한 흐름으로 유지합니다.",
    selector: "$long-task",
    icon: Sparkle,
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
            <GithubLogo size={20} weight="bold" aria-hidden="true" />
          </a>
        </div>
      </header>

      <main id="main">
        <section className="hero" aria-labelledby="hero-title">
          <motion.div
            className="hero__copy"
            initial={reduceMotion ? false : { opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              duration: reduceMotion ? 0 : 0.72,
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
                <ArrowDown size={18} weight="bold" aria-hidden="true" />
              </a>
              <a className="button button--secondary" href="#install">
                설치하기
              </a>
            </div>
          </motion.div>

          <motion.figure
            className="hero__visual"
            initial={reduceMotion ? false : { opacity: 0, scale: 0.97, x: 24 }}
            animate={{ opacity: 1, scale: 1, x: 0 }}
            transition={{
              duration: reduceMotion ? 0 : 0.9,
              delay: reduceMotion ? 0 : 0.08,
              ease: [0.16, 1, 0.3, 1],
            }}
          >
            <img
              src="./assets/skill-system-hero.webp"
              srcSet="./assets/skill-system-hero-768.webp 768w, ./assets/skill-system-hero.webp 1536w"
              sizes="(max-width: 767px) calc(100vw - 32px), 58vw"
              alt="코발트색 실로 연결된 종이 모듈과 금속 클립"
              width="1536"
              height="1024"
              fetchPriority="high"
            />
          </motion.figure>
        </section>

        <section className="outcomes section" aria-labelledby="outcomes-title">
          <Reveal className="section-heading section-heading--stacked">
            <h2 id="outcomes-title">도구가 아니라, 끝낼 일을 고르세요.</h2>
            <p>
              각 스킬은 한 가지 결과를 약속합니다. 호출 조건, 안전 규칙,
              산출물이 SKILL.md에 함께 들어 있습니다.
            </p>
          </Reveal>

          <div className="outcome-grid">
            {outcomes.map((outcome, index) => {
              const Icon = outcome.icon;
              return (
                <Reveal
                  key={outcome.title}
                  className="outcome"
                  delay={index * 0.06}
                >
                  <Icon size={26} weight="duotone" aria-hidden="true" />
                  <h3>{outcome.title}</h3>
                  <p>{outcome.description}</p>
                  <code>{outcome.selector}</code>
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
          <Reveal className="section-heading section-heading--stacked">
            <h2 id="explore-title">18개 스킬을 한 자리에서.</h2>
            <p>
              작업 이름으로 검색하거나 패키지로 좁힌 뒤, 플랫폼에 맞는 selector를
              복사하세요.
            </p>
          </Reveal>
          <Reveal delay={0.08}>
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
              src="./assets/workflow-trays.webp"
              alt="초안에서 정리된 카드와 완성 문서로 이어지는 세 개의 작업 트레이"
              width="1126"
              height="1408"
              loading="lazy"
            />
          </Reveal>

          <div className="usage__content">
            <Reveal className="section-heading section-heading--stacked">
              <h2 id="usage-title">평소 말하듯 요청하세요.</h2>
              <p>
                명시적으로 selector를 쓰면 정확하고, 자연어로 말하면 조건에 맞는
                스킬이 선택됩니다.
              </p>
            </Reveal>

            <div className="usage-flow">
              <Reveal className="usage-flow__item" delay={0.06}>
                <span>요청을 말한다</span>
                <p>“마지막 커밋을 리뷰하고 HTML 보고서로 보여줘.”</p>
              </Reveal>
              <Reveal className="usage-flow__item" delay={0.12}>
                <span>스킬이 계약을 읽는다</span>
                <p>범위, 안전 규칙, 도구, 결과 형식을 SKILL.md에서 불러옵니다.</p>
              </Reveal>
              <Reveal className="usage-flow__item" delay={0.18}>
                <span>산출물로 증명한다</span>
                <p>보고서, 커밋, 핸드오프, 검증 로그처럼 확인 가능한 결과를 남깁니다.</p>
              </Reveal>
            </div>
          </div>
        </section>

        <section className="selectors section" aria-labelledby="selectors-title">
          <Reveal className="section-heading section-heading--stacked">
            <h2 id="selectors-title">플랫폼마다 표기만 다릅니다.</h2>
            <p>같은 스킬 이름 앞에 Codex는 $, Claude Code는 /를 붙입니다.</p>
          </Reveal>

          <div className="selector-showcase">
            <Reveal className="selector-showcase__item">
              <span>Codex</span>
              <code tabIndex={0}>$diff-summary main..dev</code>
              <CopyButton value="$diff-summary main..dev" />
            </Reveal>
            <Reveal className="selector-showcase__connector" delay={0.06}>
              <ArrowRight size={28} aria-hidden="true" />
              <span>동일한 워크플로</span>
            </Reveal>
            <Reveal className="selector-showcase__item" delay={0.12}>
              <span>Claude Code</span>
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
            <div className="section-heading section-heading--stacked">
              <h2 id="install-title">한 번 설치하고, 필요한 순간 호출하세요.</h2>
              <p>
                공식 installer의 symlink 방식으로 Claude Code와 Codex에 함께
                연결합니다.
              </p>
            </div>

            <div className="install-command">
              <span>Terminal</span>
              <code tabIndex={0}>{installCommand}</code>
              <CopyButton value={installCommand} label="명령 복사" />
            </div>

            <div className="install-notes">
              <p>
                <CheckCircle size={19} weight="fill" aria-hidden="true" />
                모든 18개 스킬 설치
              </p>
              <p>
                <CheckCircle size={19} weight="fill" aria-hidden="true" />
                전역 symlink 유지
              </p>
              <p>
                <CheckCircle size={19} weight="fill" aria-hidden="true" />
                Claude Code와 Codex 명시
              </p>
            </div>
          </Reveal>

          <Reveal className="install__image" delay={0.1}>
            <img
              src="./assets/installation-rail.webp"
              alt="다섯 장의 빈 카드가 코발트색 실과 금속 레일로 연결된 모습"
              width="1254"
              height="1254"
              loading="lazy"
            />
          </Reveal>
        </section>

        <section className="closing section" aria-labelledby="closing-title">
          <Reveal>
            <h2 id="closing-title">반복하지 말고, 호출하세요.</h2>
            <p>
              매번 다시 설명하던 팀의 기준을 설치 가능한 워크플로로 바꿔보세요.
            </p>
            <a
              className="button button--primary"
              href="https://github.com/chann/skills"
              target="_blank"
              rel="noreferrer"
            >
              GitHub에서 보기
              <ArrowRight size={18} weight="bold" aria-hidden="true" />
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
          <ArrowRight size={16} weight="bold" aria-hidden="true" />
        </a>
      </footer>

      <div className="sr-only" aria-live="polite" aria-atomic="true" />
    </>
  );
}
