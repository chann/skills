# skills

[English](README.md)

소프트웨어 엔지니어링을 위한 27개의 실용적인 에이전트 워크플로와 30개의 설치 가능한 Codex selector를 17개 플러그인으로 제공합니다.

## Website

[배포된 대화형 카탈로그](https://chann.github.io/skills/)에서 모든 스킬의
역할을 살펴보고, Claude Code와 Codex selector 및 설치 명령을 바로 복사할 수
있습니다. 소스와 관리 방법은 [`website/`](website/README.md)에 있습니다.

```bash
npm --prefix website ci
npm --prefix website run dev
```

`main` 브랜치에 푸시하면 `website/dist/` 번들을 GitHub Pages에 배포합니다.

## 시작하기

입구는 `chann` 하나입니다. 작업을 주면 목표와 그 목표를 채우는 가장 작은
변경을 먼저 정리하고, 플레이북을 고른 뒤, 단계마다 그 일을 맡은 스킬이
설치되어 있으면 그 스킬에 넘깁니다. 마지막 답변에는 근거를 표시합니다.
`chann`은 자기 selector로만 실행됩니다. 나머지 스킬은 필요한 상황에서
쓰는 도구입니다. 모드가 알아서 연결해 주고, 직접 호출해도 됩니다.

```text
/chann 로그인하면 가끔 500 에러가 나, 원인 찾아서 고쳐줘
$chann this endpoint got slow, find out why and fix it
/chann 자러 간다, 이 마이그레이션 테스트 전부 통과할 때까지 해줘
```

## 스킬 목록

8개 단계로 나누고, 워크플로마다 한 줄씩 적었습니다. 이름을 누르면 해당
플러그인 README로 이동합니다.

| 단계 | 스킬 | 설명 |
| --- | --- | --- |
| mode | **[chann](chann-mode/README.ko.md)** | 직접 호출할 때만 실행되는 입구. 목표를 정리하고 14개 플레이북 중 하나를 고른 뒤, 단계마다 맡은 스킬로 넘기고 근거를 표시해 답함 |
| understand | **[how](understand/README.ko.md)** | 코드가 어떻게 동작하는지 코드를 읽고 설명. 모든 주장에 `file:line`을 달고 파일은 고치지 않음 |
| understand | **[why](understand/README.ko.md)** | 코드가 왜 이렇게 만들어졌는지 커밋, blame, PR·이슈 논의, 설계 노트에서 찾아 작성자의 말을 인용해 설명 |
| understand | **[research-brief](research-brief/README.ko.md)** | 기술 질문을 1차 출처로 확인하고 출처 등급과 확인 버전을 붙인 조사 문서를 남김 |
| understand | **[recall](recall/README.ko.md)** | Claude Code, Codex, opencode, agy 로컬 기록에서 지난 작업을 보고서로 만들거나, 주제의 현재 상태를 짧게 정리 |
| understand | **[catchup](recall/README.ko.md)** | 이 대화에서 내 마지막 메시지 이후 달라진 것과 내가 결정해야 할 것을 정리 |
| understand | **[diff-summary](diff-summary/README.ko.md)** | diff, 브랜치, 커밋, PR을 한국어·영어 Markdown과 대화형 HTML로 설명. `--md`는 Markdown만, `--quiz`는 퀴즈 추가 |
| understand | **[plan-summary](plan-summary/README.ko.md)** | 지정한 계획·PRD·명세·설계를 같은 방식으로 요약. `--md`, `--quiz` 지원 |
| understand | **[diff-viewer](diff-summary/README.ko.md)** | 작업 트리의 원본 diff를 분석 없이 브라우저용 HTML로 렌더링 |
| design | **[review-me](review-me/README.ko.md)** | 계획과 설계의 결정을 한 번에 하나씩 끝까지 검토. 직접 호출할 때만 실행 |
| design | **[arena](swarm/README.ko.md)** | 하나의 산출물에 여러 시안을 경쟁시키고, 다른 벤더의 심사자가 점수를 매기면 가장 좋은 시안에 나머지의 장점을 옮겨 붙임 |
| build | **[bug-hunt](bug-hunt/README.ko.md)** | 버그를 재현하고 가설을 반증하며 원인을 좁힌 뒤, 먼저 실패한 검사로 수정을 고정 |
| build | **[gen-docs](doc-skill/README.ko.md)** | README, 한국어 README, 아키텍처, 사용법 문서를 기존 문체를 유지하며 생성하거나 갱신 |
| build | **[unslop](unslop/README.ko.md)** | AI가 쓴 한국어·영어 글을 뜻은 그대로 두고 사람이 쓴 것처럼 고쳐 씀 |
| build | **[build-reinstall](build-reinstall/README.ko.md)** | 프로젝트를 빌드하고 새 결과를 다시 설치한 뒤 설치 파일이 빌드와 같은지 확인 |
| verify | **[interrogate](interrogate/README.ko.md)** | diff를 깨뜨려 보고, 입증 수준을 붙인 심각도별 결과를 Markdown과 이중언어 HTML로 보고 |
| verify | **[blast-radius](interrogate/README.ko.md)** | 변경이 diff 밖에서 무엇을 깨뜨릴 수 있는지 확인하고, 안전하다는 근거를 직접 실행해 입증 |
| ship | **[git-commit](git-skill/README.ko.md)** | Conventional Commits를 한 번에, 푸시까지, 검증한 단위마다, 단위마다 배포까지, 또는 제목 재작성. 별칭은 `gcr`, `gcpr`, `gcpd` |
| ship | **[git-merge](git-skill/README.ko.md)** | 현재 브랜치를 `main`, `dev`, 다른 로컬 브랜치에 머지하고, 보호 브랜치가 아니면 `git branch -d`로 원본을 삭제 |
| ship | **[git-resolve-conflicts](git-skill/README.ko.md)** | 충돌로 멈춘 머지, 리베이스, 체리픽, 되돌리기를 중단하지 않고 끝냄 |
| ship | **[git-cleanup](git-skill/README.ko.md)** | 끝난 워크트리를 지우고, 보호 브랜치에 이미 머지된 로컬 브랜치를 삭제 |
| delegate | **[swarm](swarm/README.ko.md)** | 작업을 서브에이전트나 설치된 다른 코딩 에이전트에게 나눠 맡기고, 고른 이유와 호출 트리를 하나의 보고서로 정리 |
| delegate | **[long-task](long-task/README.ko.md)** | 여러 마일스톤에 걸친 프로젝트를 병렬 worktree 서브에이전트와 마일스톤별 리뷰로 자율 진행 |
| delegate | **[handoff](handoff/README.ko.md)** | 프론트엔드·백엔드·세션 인수인계 문서를 작성하고, 확인한 상태와 확인하지 못한 상태를 나눠 적음 |
| meta | **[skill-forge](skill-forge/README.ko.md)** | 스킬 패키지를 하나의 규칙에 맞춰 만들거나 고치고, 필요한 공개 문서까지 함께 갱신 |
| meta | **[skill-audit](skill-forge/README.ko.md)** | 규칙을 어긴 스킬 패키지를 모두 보고. 위반이 있으면 0이 아닌 종료 코드를 돌려줌 |
| meta | **[reflect](skill-forge/README.ko.md)** | 세션이나 저장소에서 배운 것을 승인을 받은 뒤 실제 장치로 바꿈 |

## 설치 방법

Claude Code, Codex, Antigravity CLI, Grok Build, Pi, Gemini CLI, GitHub
Copilot CLI, OpenCode에 모든 스킬을 전역으로 설치하려면 다음 명령을 사용합니다
(권장).

```bash
npx skills add chann/skills \
  --skill '*' \
  --agent claude-code codex antigravity-cli grok pi gemini-cli \
    github-copilot opencode \
  --global \
  --yes
```

에이전트 목록은 의도적으로 직접 지정했습니다. `skills@1.5.19`에서 `--agent`
없이 `--global --yes`를 쓰면 프로젝트 설치만 지원하는 PromptScript 어댑터가
자동으로 추가될 수 있습니다. 그러면 지원하는 에이전트에는 정상적으로
설치되어도 스킬마다 실패가 하나씩 표시됩니다.

위 명령은 모든 스킬을 선택하되 지원하지 않는 PromptScript는 제외합니다.
`--copy`를 쓰지 않으므로 기본 symlink 방식도 유지됩니다. 전역 설치를 지원하는
다른 에이전트가 필요하면 ID를 추가하세요. 다만 이 CLI 버전이 copy 방식으로
바뀌지 않도록 `--agent` 뒤의 대상 목록은 계속 직접 적어야 합니다.
[업스트림 수정](https://github.com/vercel-labs/skills/pull/1561)이 반영되기
전까지 이 목록이 필요합니다.

깨끗한 임시 `HOME`에서 `skills@1.9.0`으로 확인했습니다. 설치 도구는 사본을
`~/.agents/skills/<이름>/`에 한 번만 쓰고, Codex, Pi, Gemini CLI, GitHub Copilot
CLI, OpenCode는 이 경로를 직접 읽습니다. 자체 디렉토리를 쓰는 에이전트에는 이
사본으로 symlink를 만듭니다.

| 에이전트 | `--agent` ID | 전역 경로 |
|---|---|---|
| Claude Code | `claude-code` | `~/.claude/skills/<이름>` (symlink) |
| Codex | `codex` | `~/.agents/skills/<이름>` |
| Antigravity CLI | `antigravity-cli` | `~/.gemini/config/skills/<이름>` (symlink) |
| Grok Build | `grok` | `~/.grok/skills/<이름>` (symlink) |
| Pi | `pi` | `~/.agents/skills/<이름>` |
| Gemini CLI | `gemini-cli` | `~/.agents/skills/<이름>` |
| GitHub Copilot CLI | `github-copilot` | `~/.agents/skills/<이름>` |
| OpenCode | `opencode` | `~/.agents/skills/<이름>` |

`--global`을 빼면 현재 프로젝트에 설치합니다. 에이전트 ID와 경로는 설치 도구의
[지원 에이전트 목록](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)을
따르며 릴리스마다 바뀔 수 있습니다. 현재 목록은 `npx skills --help`로 확인하세요.

필요한 것만 설치하려면 `--skill <이름>`을 씁니다. 모든 스킬은 혼자 설치해도
작동합니다. 별칭 `gcr`, `gcpr`, `gcpd`만 예외로, 옆에 `git-commit`이 있어야
합니다.

- 입구만 설치: `npx skills add chann/skills --skill chann`
- 코드베이스 이해: `npx skills add chann/skills --skill how --skill why`
- 변경 검토: `npx skills add chann/skills --skill interrogate --skill blast-radius`
- 변경 설명: `npx skills add chann/skills --skill diff-summary --skill diff-viewer`
- 짧은 별칭을 포함한 Git 워크플로: `npx skills add chann/skills --skill git-commit --skill gcr --skill gcpr --skill gcpd --skill git-merge --skill git-resolve-conflicts --skill git-cleanup`
- handoff만 설치: `npx skills add chann/skills --skill handoff`
- 서브에이전트와 시안 경쟁: `npx skills add chann/skills --skill swarm --skill arena`
- 지난 작업 정리와 따라잡기: `npx skills add chann/skills --skill recall --skill catchup`
- 자연스러운 문장: `npx skills add chann/skills --skill unslop`
- 스킬 작성: `npx skills add chann/skills --skill skill-forge --skill skill-audit --skill reflect`

설치 가능한 이름을 먼저 보려면 `npx skills add chann/skills -l --full-depth`를 실행하세요.
플러그인마다 전역 설치와 프로젝트 설치 방법이 각 README에 있습니다.

## 빠른 참조

Claude Code에서는 `/스킬-이름`, Codex에서는 `$스킬-이름`으로 직접 호출합니다.
아래 표에 두 플랫폼의 selector를 인자와 함께 모두 정리했습니다. 예전의 변형
명령은 이제 인자입니다. `/diff-summary --md`, `/git-commit push realtime`,
`/handoff session`처럼 씁니다.

### chann-mode → [상세](chann-mode/README.ko.md)

| Claude Code | Codex | 동작 |
| --- | --- | --- |
| `/chann <작업>` | `$chann <작업>` | 플레이북, 연결된 스킬, 근거를 표시한 답변으로 작업을 진행 |

### understand → [상세](understand/README.ko.md)

| Claude Code | Codex | 동작 |
| --- | --- | --- |
| `/how <질문>` | `$how <질문>` | 코드가 어떻게 동작하는지 `file:line` 인용과 함께 설명 |
| `/why <질문>` | `$why <질문>` | 왜 이렇게 만들어졌는지 작성자의 말을 인용한 결정 타임라인으로 설명 |

### research-brief → [상세](research-brief/README.ko.md)

| Claude Code | Codex | 동작 |
| --- | --- | --- |
| `/research-brief [질문]` | `$research-brief [질문]` | 기술 질문을 1차 출처로 확인해 `.research/`에 출처가 붙은 조사 문서를 작성 |

### recall → [상세](recall/README.ko.md)

| Claude Code | Codex | 동작 |
| --- | --- | --- |
| `/recall [주제 \| 날짜-범위]` | `$recall [주제 \| 날짜-범위]` | 날짜 범위의 Markdown 작업 보고서, 또는 주제가 어디까지 왔는지 정리한 요약 |
| `/catchup` | `$catchup` | 내 마지막 메시지 이후 이 대화에서 달라진 것 |

### diff-summary → [상세](diff-summary/README.ko.md)

| Claude Code | Codex | 출력 |
| --- | --- | --- |
| `/diff-summary [범위]` | `$diff-summary [범위]` | `.diff-summaries/`에 한국어·영어 Markdown과 이중언어 대화형 HTML 한 개 |
| `/diff-summary [범위] --md` | `$diff-summary [범위] --md` | 한국어·영어 Markdown만. HTML도 브라우저도 없음 |
| `/diff-summary [범위] --quiz` | `$diff-summary [범위] --quiz` | 같은 산출물에 서로 대응하는 이해도 퀴즈 추가 |
| `/diff-viewer` | `$diff-viewer` | 작업 트리 원본 diff를 `.diffs/` HTML로 렌더링 |

지정한 `..`와 `...` 범위는 그대로 보존합니다. 결함을 찾으려면 `interrogate`,
원본 패치를 보려면 `diff-viewer`를 사용하세요.

### plan-summary → [상세](plan-summary/README.ko.md)

| Claude Code | Codex | 출력 |
| --- | --- | --- |
| `/plan-summary <경로 ...>` | `$plan-summary <경로 ...>` | `.plan-summaries/`에 한국어·영어 Markdown과 이중언어 HTML |
| `/plan-summary <경로 ...> --md` | `$plan-summary <경로 ...> --md` | 한국어·영어 Markdown만 |
| `/plan-summary <경로 ...> --quiz` | `$plan-summary <경로 ...> --quiz` | 이중언어 보고서에 `QZ-*` 이해도 퀴즈 추가 |

지정한 `.md`, `.markdown`, `.txt` UTF-8 파일만 읽습니다. 문서를 자동으로 찾지
않습니다.

### review-me → [상세](review-me/README.ko.md)

| Claude Code | Codex | 동작 |
| --- | --- | --- |
| `/review-me [주제]` | `$review-me [주제]` | 중요한 계획·설계 결정이 모두 정리될 때까지 따라가며 검토 |

`review-me`는 자기 selector로만 실행됩니다. 질문을 한 번에 하나씩, 추천 답과
함께 던지고, 모든 결정을 기록하고 확인받을 때까지 읽기 전용으로 둡니다.

### swarm → [상세](swarm/README.ko.md)

| Claude Code | Codex | 동작 |
| --- | --- | --- |
| `/swarm <작업>` | `$swarm <작업>` | 작업을 서브에이전트나 다른 코딩 에이전트에게 나눠 맡기고 호출 트리와 함께 보고 |
| `/arena <작업>` | `$arena <작업>` | 하나의 산출물에 여러 시안을 경쟁시키고 교차 심사한 뒤 장점을 옮겨 붙임 |

### bug-hunt → [상세](bug-hunt/README.ko.md)

| Claude Code | Codex | 동작 |
| --- | --- | --- |
| `/bug-hunt [증상-또는-실패하는-명령]` | `$bug-hunt [증상-또는-실패하는-명령]` | 재현하고 가설을 반증하며 수정을 고정한 뒤 `.bug-hunts/`에 기록을 남김 |

### doc-skill → [상세](doc-skill/README.ko.md)

| Claude Code | Codex | 동작 |
| --- | --- | --- |
| `/gen-docs [프로젝트-루트]` | `$gen-docs [프로젝트-루트]` | README, 한국어 README, 아키텍처, 사용법 문서를 생성하거나 갱신 |

### unslop → [상세](unslop/README.ko.md)

| Claude Code | Codex | 동작 |
| --- | --- | --- |
| `/unslop [텍스트-또는-파일]` | `$unslop [텍스트-또는-파일]` | AI가 쓴 한국어·영어 글을 뜻은 그대로 두고 자연스러운 문장으로 고쳐 씀 |

### build-reinstall → [상세](build-reinstall/README.ko.md)

| Claude Code | Codex | 동작 |
| --- | --- | --- |
| `/build-reinstall [프로젝트-루트]` | `$build-reinstall [프로젝트-루트]` | 빌드하고 다시 설치한 뒤 설치된 결과를 확인 |

`build-reinstall`은 직접 요청했을 때만 실행됩니다.

### interrogate → [상세](interrogate/README.ko.md)

| Claude Code | Codex | 출력 |
| --- | --- | --- |
| `/interrogate [범위]` | `$interrogate [범위]` | `.reviews/`에 한국어·영어 Markdown과 이중언어 HTML 한 개 |
| `/interrogate [범위] --md` | `$interrogate [범위] --md` | `.reviews/`에 Markdown 한 개. HTML도 브라우저도 없음 |
| `/blast-radius [범위]` | `$blast-radius [범위]` | 답변으로 제공: 안전하다는 근거와 입증, 위험, 확인을 마친 항목, 머지 전 가장 싼 확인 |

모든 결과에는 입증 수준이 붙습니다. 약한 것부터 `said`, `cited`, `traced`,
`ran`, `reproduced` 순서입니다. `cited`에도 이르지 못한 결과는 버리고 개수만
셉니다. 리뷰는 보고만 하고 수정은 적용하지 않습니다.

### git-skill → [상세](git-skill/README.ko.md)

| Claude Code | Codex | 동작 |
| --- | --- | --- |
| `/git-commit` | `$git-commit` | 작업 트리 변경을 Conventional Commits로 한 번에 묶어 커밋 |
| `/git-commit push` | `$git-commit push` | 같은 작업 뒤 일반 `git push`까지 실행 (`--force` 없음) |
| `/git-commit realtime` · `/gcr` | `$git-commit realtime` · `$gcr` | 검증한 단위마다 커밋. 모든 체크포인트는 로컬에만 남음 |
| `/git-commit push realtime` · `/gcpr` | `$git-commit push realtime` · `$gcpr` | 검증한 단위마다 커밋하고 바로 푸시해 업스트림과 같은지 확인 |
| `/git-commit deploy` · `/gcpd` | `$git-commit deploy` · `$gcpd` | 단위마다 커밋, 푸시, 배포하고 저장소에 문서화된 설정으로 확인 |
| `/git-commit rewrite [범위] [force]` | `$git-commit rewrite [범위] [force]` | Conventional Commits 형식이 아닌 최근 커밋 제목을 다시 씀 |
| `/git-merge [main \| dev \| <브랜치>]` | `$git-merge [main \| dev \| <브랜치>]` | 현재 브랜치를 대상에 머지하고, 보호 브랜치가 아니면 원본을 삭제 |
| `/git-resolve-conflicts` | `$git-resolve-conflicts` | 충돌로 멈춘 머지, 리베이스, 체리픽, 되돌리기를 중단하지 않고 끝냄 |
| `/git-cleanup` | `$git-cleanup` | 끝난 워크트리를 지우고, 보호 브랜치에 이미 머지된 로컬 브랜치를 삭제 |

`/gcr`, `/gcpr`, `/gcpd`와 각각의 `$` 형태는 세 체크포인트 모드의 별칭이며
직접 호출할 때만 실행됩니다. `git-commit`이 설치되어 있어야 하고, 없으면
실행을 거부합니다.

### long-task → [상세](long-task/README.ko.md)

| Claude Code | Codex | 동작 |
| --- | --- | --- |
| `/long-task [status\|pause\|resume\|clear\|complete] <목표>` | `$long-task [status\|pause\|resume\|clear\|complete] <목표>` | 병렬 worktree 서브에이전트와 마일스톤별 리뷰로 프로젝트를 처음부터 끝까지 자율 진행 |

### handoff → [상세](handoff/README.ko.md)

| Claude Code | Codex | 동작 |
| --- | --- | --- |
| `/handoff frontend [범위]` | `$handoff frontend [범위]` | 백엔드 API diff, 범위, 세션 맥락에서 클라이언트용 인수인계 문서 작성 |
| `/handoff backend [범위]` | `$handoff backend [범위]` | 코드, API, DB, 잡, 롤아웃 변경에서 서버용 인수인계 문서 작성 |
| `/handoff session [메모]` | `$handoff session [메모]` | 이 세션을 새 에이전트에게 넘김: 확인한 상태와 못 한 상태, 결정, 다음 작업, 이어받기 프롬프트 |
| `/handoff [범위]` | `$handoff [범위]` | 표현이나 diff를 보고 누구를 위한 문서인지 판단 |

### skill-forge → [상세](skill-forge/README.ko.md)

| Claude Code | Codex | 동작 |
| --- | --- | --- |
| `/skill-forge [스킬-이름-또는-요청]` | `$skill-forge [스킬-이름-또는-요청]` | 스킬 패키지를 만들거나 고치고 공개 문서까지 함께 갱신 |
| `/skill-audit [스킬-또는-경로]` | `$skill-audit [스킬-또는-경로]` | 규칙을 어긴 스킬 패키지를 모두 보고 |
| `/reflect [session \| repo]` | `$reflect [session \| repo]` | 배운 것을 스크립트, 테스트, 훅, 스킬 수정으로 바꿈. 승인을 받은 뒤 적용 |

이 저장소의 모든 스킬은 같은 규칙 9개를 지킵니다. 이름 일치, 설명 문법, 호출
방식 선언, Codex 설명 파일, 슬래시 명령, eval, 카탈로그와 4개 언어 동기화,
플러그인 매니페스트, 문서에 적힌 개수입니다. `skill-audit`은 위반이 있으면 0이
아닌 종료 코드를 돌려주므로 머지 전 검사로 바로 쓸 수 있습니다.

## 이전 구성에서 옮겨 오기

변형 selector는 하나의 대표 스킬에 붙는 인자가 되었습니다. Codex의 `$이름`
selector에도 같은 대응이 적용됩니다.

| 이전 | 지금 |
| --- | --- |
| `code-review`, `code-review-md` | `interrogate` (Markdown만 필요하면 `--md`) |
| `diff-summary-md`, `diff-summary-quiz` | `diff-summary --md`, `diff-summary --quiz` |
| `plan-summary-md`, `plan-summary-quiz` | `plan-summary --md`, `plan-summary --quiz` |
| `human-friendly-writing` | `unslop` |
| `git-commit-push` | `git-commit push` |
| `git-commit-realtime` (`gcr`) | `git-commit realtime` (`gcr`) |
| `git-commit-push-realtime` (`gcpr`) | `git-commit push realtime` (`gcpr`) |
| `git-commit-push-deploy` (`gcpd`) | `git-commit deploy` (`gcpd`) |
| `git-commit-rewrite` | `git-commit rewrite` |
| `git-merge-to-main`, `git-merge-to-dev` | `git-merge main`, `git-merge dev` |
| `git-branch-cleanup` | `git-cleanup` |
| `gen-frontend-handoff`, `gen-backend-handoff`, `gen-session-handoff` | `handoff frontend`, `handoff backend`, `handoff session` |
| `all-subagents` | `swarm` |
| `work-summary` | `recall` |
| `chann-mode`, `ketchup` (잠시 쓰인 이름) | `chann`, `catchup` |

### 예전 스킬 한 번에 지우기

새 구성을 설치해도 예전 이름은 지워지지 않아, 두 세트가 함께 남습니다.
아래 명령 하나로 없어진 이름을 모두 지운 뒤 설치 명령을 다시 실행하세요.

```bash
npx skills remove \
  code-review code-review-md \
  diff-summary-md diff-summary-quiz \
  plan-summary-md plan-summary-quiz \
  human-friendly-writing \
  git-commit-push git-commit-realtime git-commit-push-realtime \
  git-commit-push-deploy git-commit-rewrite \
  git-merge-to-main git-merge-to-dev git-branch-cleanup \
  gen-frontend-handoff gen-backend-handoff gen-session-handoff \
  all-subagents work-summary \
  chann-mode ketchup \
  --global --yes
```

- 설치되어 있지 않은 이름은 건너뛰므로, 목록 전체를 그대로 실행해도 됩니다.
- `--agent`를 주지 않으면 모든 에이전트의 연결을 함께 정리합니다. 프로젝트
  안에 설치했다면 `--global`을 빼세요.
- 이름으로만 지웁니다. 같은 이름의 스킬을 다른 곳에서 설치했다면 그 이름은
  목록에서 빼세요.

## 문서

- [사용법](USAGE.md) — 설치, 전체 명령 레퍼런스, 설정, 예제, 문제 해결
- [아키텍처](ARCHITECTURE.md) — 구성 요소, 데이터 흐름, 디렉토리 맵, 설계 결정

## 다른 에이전트 플랫폼에서 사용

이 저장소의 모든 `SKILL.md`는 표준 스킬 형식을 따르며 Claude Code 전용 도구를 참조하지 않습니다. 따라서 스킬을 지원하는 모든 에이전트 플랫폼에서 사용할 수 있습니다:

| 플랫폼 | 설치 방법 |
|---|---|
| **[Claude Code](https://code.claude.com)**, **[Codex](https://github.com/openai/codex)**, Antigravity CLI, Grok Build, Pi, Gemini CLI, GitHub Copilot CLI, **[OpenCode](https://github.com/sst/opencode)** | [설치 방법](#설치-방법)의 `npx skills add` 명령. 에이전트별 전역 디렉토리는 설치 도구가 처리합니다 |
| [설치 도구 목록](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)의 다른 에이전트 | 위 명령에 해당 `--agent` ID를 추가 |
| 설치 도구가 지원하지 않는 에이전트 | 각 플랫폼 문서에 따라 스킬 로더가 `<plugin>/skills/<name>/`(`SKILL.md`가 있는 폴더)을 가리키게 설정 |

플랫폼 공통 요소와 Claude Code 전용 요소:

- **플랫폼 공통** — 모든 `SKILL.md` 본문과 `references/`입니다. 자연어 문구만으로 어떤 플랫폼에서도 실행할 수 있습니다.
- **Claude Code 전용** — `.claude-plugin/plugin.json` 래퍼와 슬래시 커맨드(`/interrogate`, `/git-commit`, `/long-task` 등)입니다. Codex는 `$이름` selector를 쓰고, 다른 플랫폼에서는 자연어나 플랫폼 자체의 호출 방식으로 실행합니다. `npx skills` 설치 도구는 Claude 전용이 아닙니다.

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼 (Claude Code, Codex, Antigravity CLI, Grok Build, Pi, Gemini CLI, GitHub Copilot CLI, OpenCode 등)
- Git 저장소
- `diff-summary` 사용 시 Git 2.45+
- Python 3.10+ (`interrogate`, `diff-summary`, `diff-viewer`, `plan-summary`, `git-commit rewrite`, `swarm`, `long-task`, `skill-audit` 사용 시 필요. 표준 라이브러리만 사용)

## 라이선스

MIT
