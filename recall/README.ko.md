# recall

[English](README.md) · [← 메인으로](../README.ko.md)

따라잡기를 돕는 스킬 두 개입니다. `recall`은 Claude Code, Codex, opencode,
agy가 로컬에 남긴 세션 기록에서 두 가지 형태로 답합니다. 날짜 범위의 Markdown
작업 보고서, 또는 어떤 주제가 지금 어디까지 와 있는지 정리한 짧은 브리프입니다.
`ketchup`은 지금 이 대화만 다룹니다. 마지막으로 쓴 메시지 이후 무엇이 바뀌었고
내가 해야 할 일이 무엇인지 알려 줍니다.

> **`work-summary`에서 이름이 바뀌었습니다.** 보고서 동작은 그대로이고,
> 저장 폴더 이름 `.work-summaries/`도 그대로라서 기존 무시 규칙이 계속
> 적용됩니다.

## 무엇이 다른가요?

`recall`은 기억이 아니라 기록으로 답합니다. 모든 프로젝트, 수치, 인용된 요청은
각 도구의 실제 기록에서 나오며, 원본을 바꾸지 않고 로컬에서만 읽습니다. 기록
속 문장은 데이터로만 보고 지시로 따르지 않습니다. 브리프는 언급하는 브랜치,
PR, 파일을 쓰기 전에 실제 `git` 상태와 대조하므로 `[open PR #12]`라고 적힌
작업은 지금 정말 열려 있습니다. `ketchup`은 쉬운 말로 답하고, 답하기 전에 현재
상태를 확인하며, 아무것도 바꾸지 않습니다.

## 설치 방법

전역 설치:

```bash
npx skills add -y -g chann/skills --skill recall
npx skills add -y -g chann/skills --skill ketchup
```

현재 프로젝트에 설치:

```bash
npx skills add chann/skills --skill recall
npx skills add chann/skills --skill ketchup
```

## 사용법

| Claude Code | Codex | 동작 |
|---|---|---|
| `/recall [날짜-범위]` | `$recall [날짜-범위]` | **보고서:** 오늘·어제 또는 주간·월간·분기·연간·직접 지정한 범위의 Markdown 작업 보고서 |
| `/recall [주제]` | `$recall [주제]` | **브리프:** 작업을 시작하거나 이어 가기 위한 주제의 현재 상태 |
| `/ketchup` | `$ketchup` | 마지막 메시지 이후 이 대화에서 바뀐 것 |

예시:

```text
/recall this week
$recall last quarter detailed
$recall billing migration
오늘 뭐 했는지 요약해줘
인증 리팩터링 어디까지 했지?
/ketchup
```

인자가 없으면 `recall`은 오늘 작업을 요약합니다. "상세"를 요청하면 타임라인과
요청 로그가 추가됩니다. 보고서 저장을 요청하면 `.work-summaries/` 아래의
`daily`, `weekly`, `monthly`, `quarterly`, `yearly`, `custom` 폴더로 나눠
저장하며, 경로를 직접 지정했다면 그 경로를 우선합니다.

### 브리프

브리프는 먼저 범위를 정하고 되짚어 말합니다. 기간(기본 최근 7일, "전부"를
조용히 "최근"으로 줄이지 않음), 주제, 작업 공간(요청이 없으면 다른 프로젝트
기록은 읽지 않음)입니다. 결과는 최대 다섯 줄의 요약, 상태 태그가 정확히 하나씩
붙은 작업 줄(`[merged]`, `[open PR #N]`, `[in flight <branch>]`,
`[verified, uncommitted]`, `[reverted]`, `[planned, not started]`), 반복된
문제 최대 다섯 개, 그리고 구체적인 다음 한 걸음입니다. 대화로만 답하고, 요청할
때만 저장합니다.

### ketchup

`ketchup`은 내가 해야 할 일을 한 문장으로 먼저 말하고, 무슨 일이 있었는지
100단어 안팎으로 정리한 뒤, 내 결정이 필요한 항목을 하나씩 답변만 보고도 정할
수 있게 적습니다. 마지막 한 줄은 에이전트가 혼자 계속할 수 있는 일입니다.

## 동작 원칙

- 모든 에이전트 기록 저장소를 읽기 전용으로 사용하며, `ketchup`은 무엇도 바꾸지 않음
- 로컬 전용: 기록 내용은 머신 밖으로 나가지 않음
- 사용자의 로컬 시간대를 기준으로 묶고 한 주는 월요일부터 계산
- 기록된 사실만 보고 — 활동 없는 기간은 없다고 표시
- 한국어는 자연스럽고 구체적으로 쓰며, `unslop`이 이미 있으면 마지막에 한 번 더 다듬음
- 기본은 대화 응답, 파일은 요청 시에만 생성하고 커밋하지 않음

각 스킬은 하나만 설치해도 모든 기능을 쓸 수 있습니다. `recall`은 `unslop`을
설치하거나 요구하지 않으며, 사용할 수 없을 때는 스킬에 포함된 문체 규칙만으로
답을 완성합니다.

## 패키지 구조

```text
recall/
├── .claude-plugin/plugin.json
├── commands/
│   ├── recall.md
│   └── ketchup.md
├── skills/
│   ├── recall/
│   │   ├── SKILL.md
│   │   ├── agents/openai.yaml
│   │   ├── evals/evals.json
│   │   └── references/agent-history-stores.md
│   └── ketchup/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       └── evals/evals.json
├── README.md
└── README.ko.md
```

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼
- 로컬 에이전트 기록 스토어에 대한 읽기 권한
- 브리프 확인용 `git`, 가능하면 PR 상태용 `gh`
- 임시 조회용 `jq` / `sqlite3` / Python 3 (기본 macOS/Linux 도구)

## 라이선스

MIT
