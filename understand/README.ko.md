# understand

[English](README.md) · [← 메인으로](../README.ko.md)

코드베이스에 대한 읽기 전용 질문 두 가지를 일부러 나눠 둔 플러그인입니다. `how`는
코드를 보고 어떻게 동작하는지 설명하고, `why`는 기록을 보고 왜 그렇게 되어 있는지
설명합니다.

## 무엇이 다른가요?

에이전트에게 "이거 왜 이렇게 만들었지?"라고 물으면 보통 코드 생김새를 보고 확신에
차서 대답합니다. 추측이 역사처럼 들리는 셈입니다. 이 두 스킬은 질문을 답의 출처에
따라 나눕니다.

- **`how`는 코드를 읽습니다.** 코드에 대한 모든 주장에 `file:line`을 붙이고, 읽지
  않은 부분은 `inferred`로 표시하며, 읽지 않은 범위를 항상 밝힙니다.
- **`why`는 기록을 읽습니다.** 커밋, blame, 풀 리퀘스트와 이슈 토론, 설계 문서를
  봅니다. 작성자가 쓴 말을 인용하고, 자기 해석은 따로 표시하고, 기록이 답하지
  못하는 부분은 그대로 말합니다.

둘 다 읽기 전용이고, 서로가 없어도 동작합니다.

## 설치 방법

전역 설치:

```bash
npx skills add -y -g chann/skills --skill how --skill why
```

현재 프로젝트에 설치:

```bash
npx skills add chann/skills --skill how --skill why
```

## 사용 방법

| Claude Code | Codex | 동작 |
|---|---|---|
| `/how <질문>` | `$how <질문>` | 코드베이스의 한 부분이 어떻게 동작하는지 `file:line` 근거와 함께 설명 |
| `/why <질문>` | `$why <질문>` | 왜 그렇게 만들어졌는지 인용이 담긴 결정 타임라인으로 설명 |

예시:

```text
/how 작업 스케줄러가 다음 태스크를 어떻게 고르지
$how 새 재시도 헬퍼는 어디에 둬야 해
/why 왜 Redis 대신 Postgres advisory lock을 골랐지
$why 이 플래그 왜 아직 꺼져 있어?
```

## 답변 구성

| 스킬 | 구성 |
|---|---|
| `how` | 개요 · 핵심 개념 · 동작 흐름 · 파일 위치 · 주의할 점 |
| `why` | 확신 정도가 붙은 짧은 답 · 결정 타임라인(커밋 또는 PR, 날짜, 인용) · 추론 표시 · 기록이 답하지 못하는 것 |

## 하지 않는 일

- 파일 수정, 커밋, 댓글 작성
- 이름만 보고 코드를 설명하거나, 코드 생김새로 동기를 설명하는 일
- 커밋, 풀 리퀘스트, 이슈, 문서 어디에도 없는 이유를 사실처럼 말하는 일

## 어떤 스킬을 쓸까요?

| 원하는 것 | 사용할 스킬 |
|---|---|
| 지금 어떻게 동작하는지 | `how` |
| 왜 그렇게 되어 있는지 | `why` |
| 외부 라이브러리나 스펙 | `research-brief` |
| 변경 하나가 한 일 | `diff-summary` |
| 뭔가 고장 났을 때 | `bug-hunt` |
| 내 이전 세션 기록 | `recall` |

## 패키지 구조

```text
understand/
├── .claude-plugin/plugin.json
├── commands/how.md
├── commands/why.md
├── skills/how/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── evals/evals.json
├── skills/why/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── evals/evals.json
├── README.md
└── README.ko.md
```

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼
- `git`. `gh`는 선택 사항이며 `why`가 읽을 수 있는 범위를 넓혀 줍니다.

## 라이선스

MIT
