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

`chann`을 설치하면 플레이북 30개가 함께 설치됩니다. Claude Code와 Codex에서
같은 파일을 사용합니다. 각 단계는 설치된 스킬을 불러오거나, 필요하면 스킬 파일을
직접 읽습니다. 해당 스킬을 쓸 수 없으면 플레이북에 적힌 단계대로 진행합니다.

## 사용법

| Claude Code | Codex | 동작 |
|---|---|---|
| `/chann <작업>` | `$chann <작업>` | 플레이북과 담당 스킬로 작업을 진행하고 근거를 표시해 답변 |

예시:

```text
/chann 로그인하면 가끔 500 에러가 나, 원인 찾아서 고쳐줘
$chann this endpoint got slow, find out why and fix it
/chann 자러 간다, 이 마이그레이션 테스트 전부 통과할 때까지 해줘
$chann captures/startup.cpuprofile에서 시작 지연 원인 찾아줘
/chann PR 42 머지할 수 있을 때까지 봐줘
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
| hillclimb | 한 지표를 반복 실험으로 개선 | 고정된 측정 조건과 시도별 기록 |
| runtime-forensics | 실행 중인 프로세스 진단 | 직접 수집한 프로파일과 근거 |
| trace-forensics | 저장된 트레이스나 프로파일 분석 | 캡처에 근거한 진단 |
| visual-parity | 승인된 기준 화면을 마이그레이션 뒤에도 유지 | 재현 가능한 이미지 비교 |
| eval | 스킬이나 에이전트 동작 평가 | 블라인드 채점과 관찰 근거 |
| autopilot | PR 대기열이나 의존 스택 운영 | 각 PR의 검증 결과 |
| opening-a-pr | 요청받은 PR 열기 | 검토 가능한 PR |
| babysit | PR 상태 확인 또는 머지 준비 | 충돌, 리뷰, CI 상태 |
| shipping | 커밋, 푸시, 배포, 병합, 정리 | 무엇이 어디까지 반영되는지 |
| pause-and-pickup | 안전하게 멈추기, 이어서 하기 | 재개 지점 |
| docs | 문서 하나 | 반영되는 커밋 시점에 사실인 내용 |
| authoring-a-skill | 스킬 작성과 수정 | 에이전트가 읽는 모든 문장 |
| spec | 아직 계획하기엔 모호한 요청 | 무엇을 만들고 완료를 어떻게 확인하는지 적은 문서 |
| api-design | API, 모듈 경계, 공개 인터페이스 설계 | 호출하는 쪽이 보는 계약 |
| ui | 사람이 조작하는 화면 | 사람이 보고 듣고 조작하는 것 전부 |
| security | 신뢰할 수 없는 입력, 인증, 비밀 값, 의존성 | 신뢰 경계와 그 위의 통제 |
| instrumentation | 로그, 메트릭, 트레이스, 알림 | 실행 중인 시스템이 스스로 답할 수 있는 질문 |
| migration | 사용처가 남아 있는 것을 없애거나 바꾸기 | 새 형태로 가는 경로와 옛 형태의 제거 |
| ci | 빌드, 테스트, 배포 파이프라인 | 모든 변경이 통과하는 관문 |
| launch | 프로덕션 출시와 단계적 공개 | 공개 결정과 되돌리는 방법 |

`babysit`은 PR 상태 조회, 리뷰 스레드 대응, 머지 준비 중 요청받은
범위를 맡습니다. `autopilot-stack`은 PR을 각각 검증한 뒤 돌려줍니다.
실제 머지까지 맡길 때는 대상 PR과 머지 권한을 요청에 포함하면 됩니다.
머지 직전에는 검증 당시의 head와 base가 그대로인지 확인합니다.

Lauren Tan의 [pstack 플레이북 22개(c3464c11)](https://github.com/backnotprop/pstack/tree/c3464c11c60b1352d5e8f5f0428a3a6943837568/skills/poteto-mode/playbooks)를
바탕으로 작성했습니다(MIT). 각 플레이북이 이 패키지 어디에 반영됐는지는
[대응표 테스트](../tests/test_upstream_skill_disposition.py)에서 확인할 수 있습니다.

spec, api-design, ui, security, instrumentation, migration, ci, launch
플레이북과 `design-the-contract-first`, `hold-the-quality-bar` 원칙,
`references/rationalizations.md`는 Addy Osmani의
[agent-skills(e997ac5b)](https://github.com/addyosmani/agent-skills/tree/e997ac5b9a74eab332d5e9793bb38a38c8cfdd74/skills)를
바탕으로 작성했습니다(MIT). 그 스킬 26개가 각각 여기 어느 파일에 반영됐는지,
또는 이미 어느 스킬이 맡고 있었는지는
[대응표 테스트](../tests/test_agent_skills_disposition.py)에 있습니다.

## 라우팅

| 상황 | 스킬 (설치된 경우) | 플레이북 |
|---|---|---|
| 이 코드가 어떻게 동작하는지 | `how` | investigation |
| 왜 이렇게 만들었는지 | `why` | investigation |
| 외부 라이브러리, API, 명세 질문 | `research-brief` | investigation |
| 고장, 예외, 간헐적 실패 | `bug-hunt` | bug-fix |
| 기대보다 느리거나 무거움 | `bug-hunt` | perf |
| 한 지표를 여러 번 측정하며 개선 | 없음, 직접 진행 | hillclimb |
| 프로파일이나 트레이스를 수집해 실행 중인 문제 진단 | 없음, 직접 진행 | runtime-forensics |
| 저장된 프로파일, 트레이스, 힙 스냅샷 진단 | 없음, 직접 진행 | trace-forensics |
| 로그, 메트릭, 트레이스, 알림 추가 | 없음, 직접 진행 | instrumentation |
| 새 동작이나 바뀐 동작 | 없음, 직접 진행 | feature |
| API, 모듈 경계, 공개 인터페이스 설계 | 없음, 직접 진행 | api-design |
| 사람이 조작하는 화면을 만들거나 바꾸기 | 없음, 직접 진행 | ui |
| 마이그레이션 전후 화면 일치 검증 | 없음, 직접 진행 | visual-parity |
| 구조만 바꾸고 동작은 그대로 | 없음, 직접 진행 | refactoring |
| 코드를 다시 말하는 주석, 또는 주석을 지워 달라는 요청 | `no-comments` | refactoring |
| API, 시스템, 저장 데이터 형태를 없애거나 교체 | 없음, 직접 진행 | migration |
| 웹훅으로 봇을 깨우는 페이지 | `make-bot-ui` | feature |
| 실험으로 정할 수 있는 갈림길 | 없음, 직접 진행 | prototype |
| 같은 결과물을 두고 경쟁하는 여러 시도 | `arena` | prototype |
| 스킬, 프롬프트, 모델, 에이전트 구성 평가 | 없음, 직접 진행 | eval |
| 계획하기엔 아직 모호한 요청, 또는 먼저 써야 하는 스펙 | `review-me` | spec |
| 열린 결정이 남은 계획이나 설계 | `review-me`, `plan-summary` | plan |
| 변경의 결함과 영향 범위 리뷰 | `interrogate`, `blast-radius` | review |
| 변경이나 계획 문서 설명 | `diff-summary`, `plan-summary`, `diff-viewer` | review |
| 신뢰할 수 없는 입력, 인증, 비밀 값, 의존성을 다루는 코드 보강 | `interrogate` | security |
| 병렬로 돌릴 독립 조각 | `swarm` | fan-out |
| 여러 마일스톤이나 무인 작업 | `long-task` | autonomous-run |
| PR 대기열이나 스택의 독립 검증 | 없음, 직접 진행 | autopilot |
| 검증한 변경으로 PR 열기 | 없음, 직접 진행 | opening-a-pr |
| 기존 PR 상태 확인 또는 머지 준비 | 없음, 직접 진행 | babysit |
| 빌드, 테스트, 배포 파이프라인 구성과 변경 | 없음, 직접 진행 | ci |
| 프로덕션 출시, 단계적 공개, 롤백 준비 | 없음, 직접 진행 | launch |
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
│   ├── playbooks/<name>.md          # 플레이북 30개
│   ├── references/principles.md     # 원칙 29개와 각 원칙의 점검 질문
│   ├── references/rationalizations.md # 단계를 건너뛰려는 핑계와 그에 답하는 원칙
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
