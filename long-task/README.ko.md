# long-task

[English](README.md) · [← 메인으로](../README.ko.md)

**여러 마일스톤에 걸친 장시간 작업**을 사람의 개입 없이 몇 시간에서 며칠 동안 자율적으로 진행하는 스킬입니다. 멈췄다 이어갈 수 있는 실행 흐름과 Git worktree에서 돌아가는 병렬 서브에이전트를 결합했습니다.

## 주요 기능

- Phase 1(준비) → Phase 2(실행 반복) → Phase 3(완료) 순서로 프로젝트를 처음부터 끝까지 진행
- **격리된 Git worktree**에서 서브에이전트를 최대 5개까지 병렬로 실행하고, 검증한 뒤 머지
- 마일스톤마다 아키텍처를 리뷰하고 수정 전담 서브에이전트를 실행한 뒤 다시 리뷰하며, 최대 3회 반복
- `.agent/` 상태 파일을 작업 메모리로 사용해 대화 맥락이 압축되거나 세션이 다시 시작돼도 진행 상황을 보존
- long-task가 활성화된 동안 Claude가 멈출 때마다 **Stop hook**이 다음 작업을 자동으로 이어서 실행
- Codex 방식의 **상태 관리 명령**: `/long-task status | pause | resume | clear | complete`
- `/long-task complete`가 완료 기준과 실제 근거를 연결하는 `.agent/audit.md` 템플릿을 작성
- 실행 중 생기는 모호함은 자율적으로 해결하며, 사용자와는 Phase 1 준비 단계에서만 상호작용
- `goal.md`, `plans.md`, `standards.md`, `implement.md`, `progress.md`, `state.md`, `audit.md` 템플릿 포함

## 설치 방법

**권장(전역 설치, 자동 승인):**

```bash
npx skills add -y -g chann/skills --skill long-task
```

**현재 프로젝트에 설치:**

```bash
npx skills add chann/skills --skill long-task
```

설치할 때는 실제 스킬 이름을 `--skill`로 지정합니다. 이 플러그인은 `long-task` 스킬을 패키징합니다.

**수동 설치:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/long-task/skills/long-task" ~/.claude/skills/long-task
```

### Stop hook 설치

별도 설치 스크립트는 필요하지 않습니다. 도우미는 설치되는 스킬 폴더 안에 있으며, `/long-task`를 처음 실행할 때 Stop hook을 설치하거나 기존 경로를 갱신합니다.

도우미는 `~/.claude/settings.json`을 안전하게 수정하며 멱등적으로 동작합니다. 현재 작업 디렉터리에 `.agent/state.md`가 있고 `status: active`일 때만 hook이 동작하므로 다른 Claude Code 세션에는 영향을 주지 않습니다. 특정 프로젝트에서 자동 실행을 멈추려면 `/long-task pause`, `/long-task clear` 또는 `/long-task complete`를 실행하세요.

## 사용 방법

*"이 프로젝트 처음부터 끝까지 만들어줘"*, *"자율적으로 진행해"*,
*"long task 돌려줘"* 같은 요청에도 자동으로 실행됩니다. 직접 호출할 때는 다음
selector를 사용합니다:

| Claude Code                  | Codex                     | 동작                                                                   |
| ---------------------------- | ------------------------- | ---------------------------------------------------------------------- |
| `/long-task <objective>`     | `$long-task <objective>`  | 목표를 지정하고 Phase 1 준비를 거쳐 자율 실행 시작                      |
| `/long-task`                 | `$long-task`              | 진행 중인 작업이 있으면 상태를 표시하고, 없으면 Phase 1 인터뷰 시작     |
| `/long-task status`          | `$long-task status`       | 현재 상태, 단계, 경과 시간, 연속 실행 횟수, `progress.md` 끝부분 표시   |
| `/long-task pause`           | `$long-task pause`        | Stop hook 자동 이어가기 일시 정지                                       |
| `/long-task resume`          | `$long-task resume`       | 자동 실행을 재개하고 연속 실행 횟수 초기화                              |
| `/long-task clear`           | `$long-task clear`        | `.agent/state.md`만 삭제 (다른 `.agent/*.md`는 보존)                    |
| `/long-task complete`        | `$long-task complete`     | `.agent/audit.md` 템플릿 작성, 완료 표시, Stop hook 해제                |

**예시:**

```
> /long-task 인증, 게시글, 댓글 기능을 가진 TypeScript Express API 만들어줘
> 처음부터 끝까지 자율적으로 구현해줘. 중간에 질문하지 마
> long task로 이 CLI 전체를 처음부터 만들어줘
> /long-task status
> /long-task pause
> /long-task complete
```

### 연속 실행 제한

Stop hook은 기본적으로 **최대 500회**까지 자동으로 이어서 실행한 뒤 멈춥니다. 횟수를 바꾸려면 Claude Code를 실행하기 전에 환경 변수를 설정합니다:

```bash
export LONG_TASK_MAX_STOP_CONTINUES=1000
```

## 동작 순서

1. **Phase 1(준비, 사용자와 상호작용하는 유일한 단계):** 사용자를 인터뷰하고 `.agent/goal.md`를 작성합니다. `.agent/plans.md`에 마일스톤을 설계하고 `.agent/standards.md`와 `.agent/implement.md`를 정한 뒤 최종 승인을 받습니다. 이어서 `status: active`인 `.agent/state.md`를 만듭니다.
2. **Phase 2(실행 반복):** 마일스톤마다 상태를 다시 읽고, worktree에서 구현 서브에이전트를 병렬로 실행합니다. 테스트, 린트, 타입 검사를 거쳐 머지한 뒤 아키텍처를 리뷰하고 필요한 수정을 반복하며 `progress.md`를 갱신합니다. Stop hook이 대화가 끝날 때마다 다음 작업을 이어갑니다.
3. **Phase 3(완료):** 전체 코드베이스에 걸친 내용을 리뷰하고 치명적인 문제를 처리합니다. `/long-task complete`로 `.agent/audit.md`를 작성한 뒤 사용자에게 결과를 보고합니다.

## 상태 파일 (`.agent/`)

| 파일             | 용도                                                | 업데이트 시점                                 |
| ---------------- | --------------------------------------------------- | --------------------------------------------- |
| `state.md`       | 진행 상태, 단계, 연속 실행 횟수                     | 모든 슬래시 커맨드와 Stop hook 실행 시        |
| `goal.md`        | 문제, 결과물, 수용 기준, 제외할 목표                | 준비 단계에서 1회                             |
| `plans.md`       | 아키텍처, 마일스톤, 작업                            | 준비 단계에서 1회 작성하고 범위가 늘면 추가   |
| `standards.md`   | 코드 품질 기준 (모든 서브에이전트가 읽음)           | 1회                                           |
| `implement.md`   | 서브에이전트 워크플로우 (모든 서브에이전트가 읽음)  | 1회                                           |
| `progress.md`    | 현재 상태, 결정 사항, 아키텍처 요약                 | 모든 작업 후                                  |
| `audit.md`       | 완료 기준과 실제 근거의 연결                        | `/long-task complete` 실행 시 1회             |

## 프로젝트 구조

```
long-task/
├── .claude-plugin/
│   └── plugin.json                        # 플러그인 메타데이터
├── commands/
│   └── long-task.md                       # /long-task 슬래시 커맨드
└── skills/
    └── long-task/
        ├── SKILL.md                       # 스킬 정의 및 워크플로우
        ├── scripts/
        │   └── long_task.py               # lifecycle helper + Stop hook
        └── references/
            ├── project-templates.md       # `.agent/` 파일 템플릿
            └── completion-audit.md        # 완료 확인 가이드
```

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼 ([Claude Code](https://code.claude.com), Codex, opencode, Copilot CLI 등 — [메인 README](../README.ko.md#다른-에이전트-플랫폼에서-사용) 참조)
- 도우미 스크립트와 Stop hook 실행에 필요한 `python3`
- Git 저장소 (worktree 서브에이전트에 필요)

## 라이선스

MIT
