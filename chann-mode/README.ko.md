# chann-mode

[English](README.md) · [← 메인으로](../README.ko.md)

규모 있는 작업을 시작할 때 쓰는 하나의 입구입니다. Claude Code에서는
`/chann <작업>`, Codex에서는 `$chann <작업>`을 입력합니다. 먼저
목표와 그 목표를 채우는 가장 작은 변경을 한 문장씩 정리하고, 작업에 맞는
플레이북을 고른 뒤, 단계마다 그 일을 맡은 카탈로그 스킬에 넘깁니다. 마지막
답변에는 근거가 무엇인지 표시합니다. 다른 워크플로도 그대로 따로 쓸 수
있습니다. 이 스킬은 이름을 외우지 않아도 그 워크플로에 닿게 해 줍니다.

## 대신 정해 주는 것

- **변경 크기.** 작업을 끝까지 해결하는 가장 작은 변경을 고릅니다. 추가보다
  삭제, 새 코드보다 이미 있는 것의 재사용이 먼저입니다. 변경이 닿는 호출부,
  테스트, 문서는 모두 마무리합니다.
- **위임.** 나눌 수 있는 부분이 둘 이상이면 하위 에이전트에 나눠 맡깁니다.
  파일을 고치는 에이전트마다 자기 워크트리와 브랜치, 겹치지 않는 파일
  범위를 받습니다. 브랜치를 합친 뒤 합쳐진 코드에서 프로젝트 검사를
  돌립니다. 하위 에이전트의 보고만으로는 증거가 되지 않습니다.
- **자율성.** 되돌릴 수 있는 작업은 묻지 않고 진행합니다. 강제 푸시, 문서에
  없는 방식의 배포, 데이터 삭제, 세션 밖 사람에게 보내는 메시지 앞에서는
  멈춥니다. "자러 간다"나 "멈추지 마"라고 하면 아무것도 묻지 않고 모든
  결정을 기록하며 끝까지 진행합니다.
- **증거.** 판정은 `VERIFIED`, `NOT VERIFIED`, `INCONCLUSIVE` 셋 중 하나입니다.
  직접 근거가 없는 주장에는 `measured`, `inferred`, `guess` 중 하나를
  붙입니다.
- **답변.** 사용자가 쓴 언어로, 사용자에게 무엇이 달라졌는지부터 말합니다.
  결정을 바꾼 원칙을 밝히고, 확인하지 못한 것과 남은 위험으로 끝냅니다.

## 설치 방법

전역 설치:

```bash
npx skills add -y -g chann/skills --skill chann
```

현재 프로젝트에 설치:

```bash
npx skills add chann/skills --skill chann
```

`chann`만 설치해도 동작합니다. 플레이북마다 직접 따라 할 단계가 들어
있습니다. 카탈로그의 다른 스킬을 함께 설치하면 각 단계가 그 일을 맡은
스킬로 넘어갑니다.

## 사용법

| Claude Code | Codex | 동작 |
|---|---|---|
| `/chann <작업>` | `$chann <작업>` | 플레이북과 담당 스킬로 작업을 진행하고 근거를 표시해 답변 |

예시:

```text
/chann 로그인하면 가끔 500 에러가 나, 원인 찾아서 고쳐줘
$chann this endpoint got slow, find out why and fix it
/chann 자러 간다, 이 마이그레이션 테스트 전부 통과할 때까지 해줘
```

선택자를 입력했을 때만 실행됩니다. 선택자 없이 요청하면 그 일을 맡은 스킬이
바로 처리합니다.

## 플레이북

| 플레이북 | 쓰는 때 | 책임지는 것 |
|---|---|---|
| investigation | 코드, 변경 이력, 외부 API에 대한 질문 | 답변. 저장소는 바꾸지 않음 |
| bug-fix | 고장, 예외, 간헐적 실패 | 근본 원인과 고쳐졌다는 증거 |
| perf | 측정해 보니 느려진 것 | 기준값, 병목, 해결책, 증거 |
| feature | 새 동작이나 바뀐 동작 | 설계와 사용자가 보는 동작 |
| refactoring | 동작은 고정하고 구조만 바꾸기 | 동작 계약 |
| prototype | 실험 한 번으로 정할 수 있는 갈림길 | 결정 하나 |
| plan | 계획 자체가 결과물인 여러 단위 변경 | 코드가 아닌 계획 |
| review | 변경을 판정하거나 설명하기 | 발견 사항과 그 근거 |
| fan-out | 서로 독립적인 조각을 병렬로 | 완료 조건과 합쳐진 결과 |
| autonomous-run | 사람 없이 끝까지 돌리는 작업 | 종료 조건 |
| shipping | 커밋, 푸시, 배포, 병합, 정리 | 무엇이 어디까지 반영되는지 |
| pause-and-pickup | 안전하게 멈추기, 이어서 하기 | 재개 지점 |
| docs | 문서 하나 | 반영되는 커밋 시점에 사실인 내용 |
| authoring-a-skill | 스킬 작성과 수정 | 에이전트가 읽는 모든 문장 |

## 라우팅

| 상황 | 스킬 (설치된 경우) | 플레이북 |
|---|---|---|
| 이 코드가 어떻게 동작하는지 | `how` | investigation |
| 왜 이렇게 만들었는지 | `why` | investigation |
| 외부 라이브러리, API, 명세 질문 | `research-brief` | investigation |
| 고장, 예외, 간헐적 실패 | `bug-hunt` | bug-fix |
| 측정해 보니 느려짐 | `bug-hunt` | perf |
| 새 동작이나 바뀐 동작 | 없음, 직접 진행 | feature |
| 구조만 바꾸고 동작은 그대로 | 없음, 직접 진행 | refactoring |
| 코드를 다시 말하는 주석, 또는 주석을 지워 달라는 요청 | `no-comments` | refactoring |
| 웹훅으로 봇을 깨우는 페이지 | `make-bot-ui` | feature |
| 실험으로 정할 수 있는 갈림길 | 없음, 직접 진행 | prototype |
| 같은 결과물을 두고 경쟁하는 여러 시도 | `arena` | prototype |
| 열린 결정이 남은 계획이나 설계 | `review-me`, `plan-summary` | plan |
| 변경의 결함과 영향 범위 리뷰 | `interrogate`, `blast-radius` | review |
| 변경이나 계획 문서 설명 | `diff-summary`, `plan-summary`, `diff-viewer` | review |
| 병렬로 돌릴 독립 조각 | `swarm` | fan-out |
| 여러 마일스톤이나 무인 작업 | `long-task` | autonomous-run |
| 커밋, 푸시, 배포, 병합, 충돌, 정리, 재설치 | `git-commit`, `git-merge`, `git-resolve-conflicts`, `git-cleanup`, `build-reinstall` | shipping |
| 멈추기, 이어 하기, 따라잡기 | `handoff`, `recall`, `catchup` | pause-and-pickup |
| 문서와 글 | `gen-docs`, `unslop` | docs |
| 스킬 작성, 수정, 교훈 정리 | `skill-forge`, `skill-audit`, `reflect` | authoring-a-skill |

## 패키지 구조

```text
chann-mode/
├── .claude-plugin/plugin.json
├── commands/chann.md
├── skills/chann/
│   ├── SKILL.md                     # 첫 동작, 라우팅, 원칙 목록, 자율성, 위임, 증거, 답변
│   ├── worker.md                    # 모든 하위 에이전트가 먼저 읽는 규칙
│   ├── playbooks/<name>.md          # 플레이북 14개
│   ├── references/principles.md     # 원칙 27개와 각 원칙의 점검 질문
│   ├── references/decision-trail.md # 길거나 무인으로 도는 작업의 결정 기록 형식
│   ├── agents/openai.yaml
│   └── evals/evals.json
├── README.md
└── README.ko.md
```

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼
- 워크트리 격리와 결정 기록을 위한 Git

## 라이선스

MIT
