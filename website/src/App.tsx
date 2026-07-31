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

const heroRails = [
  { selector: "$code-review", tone: "sky" },
  { selector: "$diff-summary", tone: "violet" },
  { selector: "$gen-docs", tone: "coral" },
  { selector: "$git-commit", tone: "amber" },
  { selector: "$gen-frontend-handoff", tone: "mint" },
  { selector: "$long-task", tone: "rose" },
  { selector: "$diff-viewer", tone: "blue" },
  { selector: "$git-commit-realtime", tone: "lime" },
];

const outcomes = [
  {
    title: "변경을 검토한다",
    description: "결함은 review로 찾고, 의도와 구조는 summary로 이해합니다.",
    selector: "$code-review",
    icon: ShieldCheck,
    tone: "sky",
  },
  {
    title: "맥락을 설명한다",
    description: "원본 diff부터 이중언어 보고서와 이해도 퀴즈까지 이어집니다.",
    selector: "$diff-summary",
    icon: NotePencil,
    tone: "violet",
  },
  {
    title: "Git을 안전하게 움직인다",
    description: "명시적 스테이징, 검증, push parity를 하나의 계약으로 묶습니다.",
    selector: "$git-commit-push-realtime",
    icon: GitPullRequest,
    tone: "coral",
  },
  {
    title: "큰 작업을 끝까지 운영한다",
    description: "마일스톤, 작업 분리, 리뷰, 완료 감사를 한 흐름으로 유지합니다.",
    selector: "$long-task",
    icon: Sparkle,
    tone: "mint",
  },
];

const workflowSteps = [
  {
    number: "01",
    title: "요청을 말한다.",
    description: "마지막 커밋을 리뷰하고 HTML 보고서로 보여줘.",
  },
  {
    number: "02",
    title: "계약을 읽는다.",
    description: "스킬이 범위, 안전 규칙, 도구와 결과 형식을 불러옵니다.",
  },
  {
    number: "03",
    title: "결과로 증명한다.",
    description: "보고서, 커밋, 핸드오프와 검증 로그를 확인할 수 있습니다.",
  },
];

export function App() {
  const reduceMotion = useReducedMotion();

  return (
    <>
      <a className="skip-link" href="#main">
        본문으로 건너뛰기
      </a>

      <aside className="announcement" aria-label="프로젝트 안내">
        <p>
          <span>Open source</span>
          Claude Code와 Codex를 위한 18개 packaged workflow
        </p>
        <a
          href="https://github.com/chann/skills"
          target="_blank"
          rel="noreferrer"
        >
          GitHub에서 보기
          <ArrowRight size={14} weight="bold" aria-hidden="true" />
        </a>
      </aside>

      <header className="site-header">
        <a className="brand" href="#main" aria-label="skills 홈">
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
          <a className="header-install" href="#install">
            설치
          </a>
        </div>
      </header>

      <main id="main">
        <section className="hero" aria-labelledby="hero-title">
          <motion.div
            className="hero-spectrum"
            aria-hidden="true"
            initial={reduceMotion ? false : { opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: reduceMotion ? 0 : 0.45 }}
          >
            {heroRails.map((rail, index) => (
              <motion.div
                key={rail.selector}
                className={`hero-rail hero-rail--${rail.tone}`}
                initial={reduceMotion ? false : { opacity: 0, y: -44 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{
                  duration: reduceMotion ? 0 : 0.72,
                  delay: reduceMotion ? 0 : index * 0.045,
                  ease: [0.16, 1, 0.3, 1],
                }}
              >
                <span />
                <span />
                <span />
                <code>{rail.selector}</code>
              </motion.div>
            ))}
          </motion.div>

          <motion.div
            className="hero__copy"
            initial={reduceMotion ? false : { opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              duration: reduceMotion ? 0 : 0.68,
              delay: reduceMotion ? 0 : 0.18,
              ease: [0.16, 1, 0.3, 1],
            }}
          >
            <p className="eyebrow">Reusable agent workflows</p>
            <h1 id="hero-title">
              <span>반복 작업을,</span>
              <span>이름 있는 스킬로.</span>
            </h1>
            <p className="hero__lede">
              리뷰부터 Git 정리까지. 검증된 워크플로를 필요한 순간 바로
              호출하세요.
            </p>
            <div className="hero__actions">
              <a className="button button--primary" href="#explore">
                18개 스킬 탐색
                <ArrowRight size={17} weight="bold" aria-hidden="true" />
              </a>
              <a className="text-link" href="#install">
                설치 명령 보기
              </a>
            </div>
          </motion.div>

          <ul className="hero__facts" aria-label="카탈로그 요약">
            <li>
              <strong>18</strong>
              packaged skills
            </li>
            <li>
              <strong>2</strong>
              agent platforms
            </li>
            <li>
              <strong>1</strong>
              install command
            </li>
          </ul>
        </section>

        <section className="outcomes section" aria-labelledby="outcomes-title">
          <Reveal className="section-heading section-heading--wide">
            <span className="section-label section-label--spectrum">
              Packaged workflows
            </span>
            <h2 id="outcomes-title">반복 지시를, 호출 가능한 계약으로.</h2>
            <p>
              각 스킬은 언제 불러야 하는지, 어떻게 안전하게 실행하는지, 무엇을
              남겨야 하는지를 함께 정의합니다.
            </p>
          </Reveal>

          <div
            className="outcome-track"
            role="region"
            aria-label="워크플로 결과 카드"
            tabIndex={0}
          >
            {outcomes.map((outcome, index) => {
              const Icon = outcome.icon;
              return (
                <Reveal
                  key={outcome.title}
                  className={`outcome outcome--${outcome.tone}`}
                  delay={index * 0.04}
                >
                  <div className="outcome__top">
                    <Icon size={22} weight="duotone" aria-hidden="true" />
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
          className="workflow section"
          id="usage"
          aria-labelledby="workflow-title"
        >
          <Reveal className="workflow__heading">
            <span className="section-label section-label--rose">How it works</span>
            <h2 id="workflow-title">요청부터 증명까지, 세 단계.</h2>
            <p>
              사람은 목표를 말하고, 스킬은 반복 가능한 실행 계약을 적용합니다.
            </p>
          </Reveal>

          <div className="workflow-grid">
            {workflowSteps.map((step, index) => (
              <Reveal
                key={step.number}
                className="workflow-step"
                delay={index * 0.05}
              >
                <code>{step.number}</code>
                <h3>{step.title}</h3>
                <p>{step.description}</p>
              </Reveal>
            ))}
          </div>
        </section>

        <section
          className="explore-section section"
          id="explore"
          aria-labelledby="explore-title"
        >
          <Reveal className="section-heading section-heading--wide">
            <span className="section-label section-label--mint">Skill catalog</span>
            <h2 id="explore-title">필요한 워크플로를 한 자리에서.</h2>
            <p>
              작업이나 산출물로 검색하고, 플랫폼에 맞는 selector를 바로
              복사하세요.
            </p>
          </Reveal>
          <Reveal delay={0.06}>
            <SkillExplorer />
          </Reveal>
        </section>

        <section className="platforms section" aria-labelledby="platforms-title">
          <Reveal className="platforms__copy">
            <span className="section-label section-label--violet">
              One contract, two selectors
            </span>
            <h2 id="platforms-title">같은 스킬, 다른 prefix.</h2>
            <p>
              하나의 SKILL.md를 두 플랫폼이 같은 규칙으로 읽습니다. Codex는
              $, Claude Code는 /를 이름 앞에 붙입니다.
            </p>
          </Reveal>

          <Reveal className="platform-map" delay={0.08}>
            <div className="platform-map__contract">
              <span>shared contract</span>
              <strong>diff-summary</strong>
              <code>SKILL.md</code>
            </div>
            <div className="platform-map__line" aria-hidden="true" />
            <div className="platform-map__targets">
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

        <section
          className="install section"
          id="install"
          aria-labelledby="install-title"
        >
          <Reveal className="install__content">
            <span className="section-label section-label--amber">
              One command setup
            </span>
            <h2 id="install-title">18개 스킬을, 한 명령으로.</h2>
            <p>
              공식 installer의 symlink 방식으로 Claude Code와 Codex에 함께
              연결합니다.
            </p>
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

          <Reveal className="install-command" delay={0.08}>
            <div className="install-command__chrome">
              <span>Terminal</span>
              <span>ready</span>
            </div>
            <code tabIndex={0}>{installCommand}</code>
            <CopyButton value={installCommand} label="명령 복사" />
          </Reveal>
        </section>

        <section className="closing section" aria-labelledby="closing-title">
          <Reveal>
            <span className="section-label section-label--spectrum">Open source</span>
            <h2 id="closing-title">팀의 기준을, 다시 부를 수 있게.</h2>
            <p>반복되는 작업 방식을 설치 가능한 워크플로로 남겨두세요.</p>
            <div className="closing__actions">
              <a
                className="button button--primary"
                href="https://github.com/chann/skills"
                target="_blank"
                rel="noreferrer"
              >
                GitHub에서 보기
                <ArrowRight size={17} weight="bold" aria-hidden="true" />
              </a>
              <a className="text-link" href="#explore">
                스킬 다시 보기
              </a>
            </div>
          </Reveal>
        </section>
      </main>

      <footer className="site-footer">
        <a className="brand" href="#main" aria-label="skills 홈">
          <span className="brand__mark" aria-hidden="true">
            <span />
            <span />
            <span />
          </span>
          <span>skills</span>
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
            GitHub
            <ArrowRight size={15} weight="bold" aria-hidden="true" />
          </a>
        </div>
      </footer>
    </>
  );
}
