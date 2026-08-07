# skills

[English](README.md)

소프트웨어 엔지니어링을 위한 24개의 실용적인 에이전트 워크플로와 25개의 설치 가능한 Codex selector를 9개 plugin으로 제공합니다.

## Website

[배포된 대화형 카탈로그](https://chann.github.io/skills/)에서 모든 스킬의
역할을 살펴보고, Claude Code와 Codex selector 및 설치 명령을 바로 복사할 수
있습니다. 소스와 관리 방법은 [`website/`](website/README.md)에 있습니다.

```bash
npm --prefix website ci
npm --prefix website run dev
```

`main` 브랜치에 푸시하면 `website/dist/` 번들을 GitHub Pages에 배포합니다.

## 스킬 목록

| 스킬                                                | 설명                                                                                          |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **[code-review](code-review/README.ko.md)**         | git 변경 인텔리전스 — 설명형 diff 요약, 심각도 기반 리뷰, 원본 HTML diff 뷰어                    |
| **[review-me](review-me/README.ko.md)**             | 계획과 설계를 한 번에 결정 하나씩 검토해 모든 중요한 leaf를 닫음                                |
| **[doc-skill](doc-skill/README.ko.md)**             | README, 한국어 README, 아키텍처, 사용법 문서를 기존 prose 보존하며 생성 또는 갱신              |
| **[git-skill](git-skill/README.ko.md)**             | Conventional Commits, realtime checkpoint 커밋·푸시, 히스토리 재작성, main/dev 머지, 로컬 브랜치 정리    |
| **[handoff](handoff/README.ko.md)**                 | git diff, 범위, 세션 컨텍스트에서 프론트엔드/백엔드 핸드오프 문서 생성                         |
| **[long-task](long-task/README.ko.md)**             | 멀티 마일스톤 프로젝트 자율 오케스트레이터 — 병렬 worktree 서브에이전트 + 마일스톤 리뷰 사이클  |
| **[work-summary](work-summary/README.ko.md)**       | Claude Code, Codex, opencode, agy 로컬 기록에서 날짜 범위 작업 보고서를 Markdown으로 생성       |
| **[plan-summary](plan-summary/README.ko.md)**       | 명시한 plan·PRD·명세·설계를 한·영으로 요약하고 Markdown 전용·퀴즈 변형 제공                    |
| **[human-friendly-writing](human-friendly-writing/README.ko.md)** | AI가 쓴 한국어를 뜻은 그대로 두고 사람이 쓴 것 같은 자연스러운 문장으로 재작성                 |

## 설치 방법

Claude Code, Codex, Antigravity CLI, Gemini CLI, GitHub Copilot CLI,
OpenCode에 모든 스킬을 설치 도구의 symlink 방식으로 전역 설치 (권장):

```bash
npx skills add chann/skills \
  --skill '*' \
  --agent claude-code codex antigravity-cli gemini-cli \
    github-copilot opencode \
  --global \
  --yes
```

에이전트 목록은 의도적으로 명시했습니다. `skills@1.5.19`에서
`--agent` 없이 `--global --yes`를 사용하면 프로젝트 설치만 지원하는
PromptScript 어댑터가 암묵적으로 추가될 수 있습니다. 이 경우 지원 대상에는
정상 설치됐는데도 스킬마다 실패가 하나씩 표시됩니다. 위 명령은 모든 스킬을
선택하고 기본 symlink 방식(`--copy`를 추가하지 않음)을 유지하면서 해당 비지원
대상을 제외합니다. 다른 전역 설치 지원 에이전트가 필요하면 ID를 추가하되,
이 CLI 버전이 copy 방식으로 전환하지 않도록 명시한 대상 목록은 유지하세요.
[업스트림 수정](https://github.com/vercel-labs/skills/pull/1561)이 반영될 때까지
이 명시적 대상 목록이 필요합니다.

스킬별 설치 또는 비전역 / 수동 설치는 각 스킬 README 참조:

- [code-review 설치](code-review/README.ko.md#설치-방법)
- [review-me 설치](review-me/README.ko.md#설치-방법)
- [doc-skill 설치](doc-skill/README.ko.md#설치)
- [git-skill 설치](git-skill/README.ko.md#설치-방법)
- [handoff 설치](handoff/README.ko.md#설치-방법)
- [long-task 설치](long-task/README.ko.md#설치-방법)
- [work-summary 설치](work-summary/README.ko.md#설치-방법)
- [plan-summary 설치](plan-summary/README.ko.md#설치)
- [human-friendly-writing 설치](human-friendly-writing/README.ko.md#설치)

handoff만 설치하는 예: `npx skills add chann/skills --skill gen-frontend-handoff --skill gen-backend-handoff`
백엔드 handoff만 설치: `npx skills add chann/skills --skill gen-backend-handoff`
diff-summary만 설치: `npx skills add chann/skills --skill diff-summary`
review-me만 설치: `npx skills add chann/skills --skill review-me`
work-summary만 설치: `npx skills add chann/skills --skill work-summary`
plan-summary 제품군 설치: `npx skills add chann/skills --skill plan-summary --skill plan-summary-md --skill plan-summary-quiz`
human-friendly-writing만 설치: `npx skills add chann/skills --skill human-friendly-writing`
Codex `$gcpr` 설치: `npx skills add chann/skills --skill gcpr --skill git-commit-push-realtime --skill git-commit --skill git-commit-push`

## 빠른 참조

Claude Code에서는 `/스킬-이름`, Codex에서는 `$스킬-이름`으로 명시 호출합니다.
아래 표는 모든 스킬의 두 플랫폼 selector를 함께 표시합니다.

### code-review → [상세](code-review/README.ko.md)

| Claude Code                      | Codex                        | 출력                                                                        |
| -------------------------------- | ---------------------------- | --------------------------------------------------------------------------- |
| `/code-review [scope]`           | `$code-review [scope]`       | `.reviews/`에 마크다운 + 이중언어 HTML 리뷰 생성                            |
| `/code-review-md [scope]`        | `$code-review-md [scope]`    | `.reviews/`에 마크다운 리뷰만 생성                                          |
| `/diff-summary [scope]`          | `$diff-summary [scope]`      | `.diff-summaries/`에 정렬된 한·영 마크다운 + 이중언어 HTML 요약 생성        |
| `/diff-summary-md [scope]`       | `$diff-summary-md [scope]`   | `.diff-summaries/`에 정렬된 한·영 마크다운만 생성 (HTML·브라우저 없음)      |
| `/diff-summary-quiz [scope]`     | `$diff-summary-quiz [scope]` | `/diff-summary`에 한·영 정렬 이해도 퀴즈를 추가                             |
| `/diff-viewer`                   | `$diff-viewer`               | 작업 트리 원본 diff를 `.diffs/` HTML로 렌더링                               |

`diff-summary`는 “코드를 요약해줘”, “마지막 커밋 코드를 요약해줘”, “main..dev 변경 요약” 같은 요청에도 자동으로 활성화됩니다. 기본 출력은 한국어를 먼저 보여주는 정렬된 한·영 보고서이며, 한 언어만 명시적으로 요청하면 단일 언어 모드를 사용합니다. “마크다운 요약만 저장”은 `diff-summary-md`, “이 변경 이해했는지 퀴즈로 확인”은 `diff-summary-quiz`로 연결됩니다. 세 스킬 모두 명시한 `..`/`...` 범위를 정확히 보존합니다. 결함 탐색은 `code-review`, 원본 패치 확인은 `diff-viewer`를 사용하세요.

리뷰·요약·퀴즈·원본 diff HTML 보고서는 하나의 인터페이스를 공유합니다. 한국어/영어 토글, 밝게·어둡게·시스템 테마와 인쇄용 밝은 팔레트, 두 테마 모두 WCAG AA를 지키는 단일 의미 색상 팔레트, 어절 단위로 줄을 바꾸는 한글 타이포그래피, 건너뛰기 링크와 라이브 리전을 갖춘 키보드 지원이 모두 들어 있습니다. 보고서는 서버나 네트워크 없이 열리는 단일 파일입니다.

### review-me → [상세](review-me/README.ko.md)

| Claude Code | Codex | 동작 |
| ----------- | ----- | ---- |
| `/review-me [주제]` | `$review-me [주제]` | 계획이나 설계의 모든 중요한 하위 결정을 따라가 leaf-complete 기록을 확인 |

`review-me`는 한 번에 결정 하나만 질문하고 구체적인 권장안을 제시하며, 각
답변에서 생긴 하위 선택을 재귀적으로 추적합니다. 확인 가능한 사실은 직접
조사하고 최종 결정 기록이 확인될 때까지 읽기 전용 리뷰를 유지합니다.

### doc-skill → [상세](doc-skill/README.ko.md)

| Claude Code | Codex       | 동작                                                              |
| ----------- | ----------- | ----------------------------------------------------------------- |
| `/gen-docs` | `$gen-docs` | README, 한국어 README, 아키텍처, 사용법 문서를 생성 또는 갱신      |

### git-skill → [상세](git-skill/README.ko.md)

| Claude Code                    | Codex                       | 동작                                                                            |
| ------------------------------ | --------------------------- | ------------------------------------------------------------------------------- |
| `/git-commit`                  | `$git-commit`               | 작업 트리 변경을 Conventional Commits 단위로 분리해 커밋                        |
| `/git-commit-push`             | `$git-commit-push`          | 위 작업 후 `git push`까지 진행 (`--force` 안 함)                                |
| `/git-commit-push-realtime` · `/gcpr` | `$git-commit-push-realtime` · `$gcpr` | 구현 중 검증된 의미 단위가 끝날 때마다 커밋하고 즉시 푸시                |
| `/git-commit-realtime` · `/gcr` | `$git-commit-realtime` | 구현 중 검증된 의미 단위가 끝날 때마다 로컬에만 커밋 (푸시 안 함)               |
| `/git-commit-rewrite`          | `$git-commit-rewrite`       | 최근 비순응 커밋 subject를 Conventional 형식으로 재작성                         |
| `/git-merge-to-main`           | `$git-merge-to-main`        | 현재 브랜치를 `main`으로 머지 후 소스 브랜치를 `git branch -d`로 삭제           |
| `/git-merge-to-dev`            | `$git-merge-to-dev`         | 현재 브랜치를 `dev`(없으면 `develop`)로 머지 후 소스 브랜치 삭제                |
| `/git-branch-cleanup`          | `$git-branch-cleanup`       | 보호 브랜치에 이미 머지된 모든 로컬 브랜치 삭제                                 |

### long-task → [상세](long-task/README.ko.md)

| Claude Code  | Codex        | 동작                                                                                          |
| ------------ | ------------ | --------------------------------------------------------------------------------------------- |
| `/long-task` | `$long-task` | 병렬 worktree 서브에이전트 + 마일스톤 리뷰로 프로젝트를 처음부터 끝까지 자율적으로 구현       |

*"이 프로젝트 처음부터 끝까지 만들어줘"*, *"자율적으로 진행해"*, *"long task 돌려줘"* 같은 문구에도 자동 트리거됩니다.

### handoff → [상세](handoff/README.ko.md)

| Claude Code               | Codex                    | 동작                                                                                 |
| ------------------------- | ------------------------ | ------------------------------------------------------------------------------------ |
| `/gen-frontend-handoff`   | `$gen-frontend-handoff`  | 백엔드 API diff, 범위, 세션 컨텍스트에서 프론트엔드/클라이언트 핸드오프 작성        |
| `/gen-backend-handoff`    | `$gen-backend-handoff`   | 코드, API, DB, job, rollout 변경사항에서 백엔드/서버 핸드오프 작성                  |

### work-summary → [상세](work-summary/README.ko.md)

| Claude Code | Codex | 동작 |
| ----------- | ----- | ---- |
| `/work-summary [범위]` | `$work-summary [범위]` | 오늘, 이번 주, 이번 달 또는 사용자 지정 기간의 작업 내역을 Markdown 보고서로 생성 |

`work-summary`는 Claude Code, Codex, opencode, agy가 로컬에 남긴 세션 기록을
읽기 전용으로 수집해 로컬 타임존 기준으로 정리합니다. 기본은 요약이고, 요청
시 타임라인과 요청 로그가 있는 상세 리포트를 만듭니다. *"오늘 작업 요약해줘"*,
*"이번주에 뭐 했는지 정리해줘"* 같은 문구에도 자동 트리거됩니다.

### plan-summary → [상세](plan-summary/README.ko.md)

| Claude Code | Codex | 출력 |
| --- | --- | --- |
| `/plan-summary [source-path ...]` | `$plan-summary [source-path ...]` | `.plan-summaries/`에 정렬된 한·영 Markdown과 이중언어 HTML 생성 |
| `/plan-summary-md [source-path ...]` | `$plan-summary-md [source-path ...]` | 정렬된 한·영 Markdown만 생성 |
| `/plan-summary-quiz [source-path ...]` | `$plan-summary-quiz [source-path ...]` | 이중언어 보고서와 정렬된 `QZ-*` 이해도 퀴즈 생성 |

세 selector는 사용자가 명시한 `.md`, `.markdown`, `.txt` UTF-8 파일만 읽고 문서를 자동 탐색하지 않습니다. 보고서는 소스 순서·digest와 `PS-*` 근거 카드를 공유합니다. Markdown 전용 selector는 HTML을 만들지 않고, 퀴즈 selector는 접근 가능한 오프라인 상호작용을 추가합니다.

### human-friendly-writing → [상세](human-friendly-writing/README.ko.md)

| Claude Code | Codex | 동작 |
| ----------- | ----- | ---- |
| `/human-friendly-writing [텍스트-또는-파일]` | `$human-friendly-writing [텍스트-또는-파일]` | AI가 쓴 한국어를 뜻은 그대로 두고 자연스러운 문장으로 재작성 |

`human-friendly-writing`은 계약(contract)·엔벨로프(envelope)·패리티(parity)
같은 AI 특유의 직역 용어와 새어 나온 내부 방법론 용어를 걷어내고 번역투를
매만집니다. 사실·수치·표준 기술 용어는 그대로 둡니다. *"AI 용어 없애줘"*,
*"사람답게 다듬어줘"* 같은 문구에도 자동 트리거됩니다.

## 문서

- [사용법](USAGE.md) — 설치, 전체 명령 레퍼런스, 설정, 예제, 문제 해결
- [아키텍처](ARCHITECTURE.md) — 구성 요소, 데이터 흐름, 디렉토리 맵, 설계 결정

## 다른 에이전트 플랫폼에서 사용

이 저장소의 모든 `SKILL.md` 파일은 표준 스킬 포맷을 따르고 Claude-Code 전용 툴을 참조하지 않으므로, 스킬을 지원하는 모든 에이전트 플랫폼에서 동작합니다:

| 플랫폼                                                  | 설치 방법                                                                                       |
| ------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| **[Claude Code](https://code.claude.com)**              | `npx skills add chann/skills` — 전체 플러그인 설치 (스킬 + 슬래시 커맨드)                       |
| **[Codex](https://github.com/openai/codex)**            | `<plugin>/skills/<name>/` 를 Codex 스킬 디렉토리(`~/.agents/skills/` 등)에 심볼릭 링크          |
| **[opencode](https://github.com/sst/opencode)**         | 스킬 디렉토리를 opencode 의 스킬 경로에 배치                                                    |
| **Copilot CLI / Gemini CLI / 기타**                     | 플랫폼별 스킬 로더가 `<plugin>/skills/<name>/SKILL.md` 를 가리키도록 설정 (각 플랫폼 문서 참조) |

이식 가능한 것 vs 그렇지 않은 것:

- **이식 가능** — 모든 `SKILL.md` 본문과 `references/`. 자연어 문구만으로 어떤 플랫폼에서든 트리거됩니다.
- **Claude Code 전용** — `.claude-plugin/plugin.json` 래퍼, `npx skills` 설치 도구, 슬래시 커맨드(`/code-review`, `/git-commit`, `/long-task` 등). 다른 플랫폼에서는 자연어 또는 자체 활성화 메커니즘으로 호출합니다.

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼 (Claude Code, Codex, opencode, Copilot CLI, Gemini CLI 등)
- Git 저장소
- `diff-summary`, `diff-summary-md`, `diff-summary-quiz` 사용 시 Git 2.45+
- Python 3.10+ (`code-review`, `diff-summary`, `diff-summary-md`, `diff-summary-quiz`, `diff-viewer`, `plan-summary`, `plan-summary-md`, `plan-summary-quiz`, `git-commit-rewrite` 사용 시 필요)

## 라이선스

MIT
