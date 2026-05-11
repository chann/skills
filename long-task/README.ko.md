# long-task

[English](README.md) · [← 메인으로](../README.ko.md)

**여러 마일스톤에 걸친 장시간 작업**을 사람의 개입 없이 몇 시간 ~ 며칠 동안 자율적으로 진행하는 오케스트레이터 스킬입니다. [jthack/claude-goal](https://github.com/jthack/claude-goal)의 `/goal` lifecycle을 worktree 기반 병렬 서브에이전트 오케스트레이터 위에 얹은 형태입니다.

## 주요 기능

- Phase 1(셋업) → Phase 2(오케스트레이션 루프) → Phase 3(완료) 워크플로우로 프로젝트를 처음부터 끝까지 진행
- **격리된 git worktree**에서 병렬 서브에이전트 실행 (최대 5개) 후 검증을 거쳐 merge
- 마일스톤마다 **아키텍처 리뷰 사이클** 강제 (review → fix 서브에이전트 → re-review, 최대 3회)
- `.agent/` 상태 파일을 작업 메모리로 사용하여 컨텍스트 압축/세션 재시작 후에도 진행 상황 보존
- **Stop hook** 으로 long-task 활성 중 Claude 가 멈출 때마다 자동으로 다음 작업을 이어감 (codex `/goal` 스타일)
- codex 스타일 **lifecycle 커맨드**: `/long-task status | pause | resume | clear | complete`
- **completion audit** 게이트: `/long-task complete` 가 acceptance criteria → 실제 증거 매핑 템플릿을 작성
- 실행 중 발생하는 모호함은 자율적으로 해결 — 사용자와의 상호작용은 Phase 1 셋업 단계에서만
- `goal.md`, `plans.md`, `standards.md`, `implement.md`, `progress.md`, `state.md`, `audit.md` 템플릿 포함

## 설치 방법

**권장 (전역 + 자동 승인, 한 방):**

```bash
npx skills add -y -g chann/skills@long-task
```

**프로젝트 로컬:**

```bash
npx skills add chann/skills@long-task
```

**수동 설치:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/long-task/skills/long-task" ~/.claude/skills/long-task
```

### Stop hook 설치

Stop hook 이 자동 이어가기를 책임집니다. **첫 `/long-task` 실행 시 자동 설치** 되며, 이미 설치되어 있으면 skip 합니다.

수동으로 관리할 수도 있습니다:

```bash
# 설치 (이미 있으면 skip)
bash scripts/install.sh

# 기존 항목 덮어쓰기 (예: 레포 위치 변경 후)
bash scripts/install.sh --overwrite

# hook 제거
bash scripts/uninstall.sh
```

`~/.claude/settings.json` 을 안전하게 patch 합니다. hook 은 cwd 에 `.agent/state.md` 가 있고 `status: active` 일 때만 동작하므로 다른 Claude Code 세션은 영향받지 않습니다.

## 사용 방법

*"이 프로젝트 처음부터 끝까지 만들어줘"*, *"자율적으로 진행해"*, *"long task 돌려줘"* 같은 문구로 자동 트리거되거나, 명시적으로 호출할 수 있습니다:

| 커맨드                          | 동작                                                                    |
| ------------------------------- | ----------------------------------------------------------------------- |
| `/long-task <objective>`        | 목표 지정 후 Phase 1 셋업 → 자율 오케스트레이션                          |
| `/long-task`                    | 활성 task 가 있으면 상태 출력, 없으면 Phase 1 인터뷰 시작                |
| `/long-task status`             | 현재 상태, phase, 경과 시간, runaway 카운터, `progress.md` 끝부분 표시   |
| `/long-task pause`              | Stop hook 자동 이어가기 일시 정지                                        |
| `/long-task resume`             | 재개, runaway 카운터 초기화                                              |
| `/long-task clear`              | `.agent/state.md` 만 삭제 (다른 `.agent/*.md` 는 보존)                   |
| `/long-task complete`           | `.agent/audit.md` 템플릿 작성, 완료 표시, Stop hook 해제                 |

**예시:**

```
> /long-task 인증, 게시글, 댓글 기능을 가진 TypeScript Express API 만들어줘
> 처음부터 끝까지 자율적으로 구현해줘. 중간에 질문하지 마
> long task로 이 CLI 전체를 처음부터 만들어줘
> /long-task status
> /long-task pause
> /long-task complete
```

### Runaway 가드

Stop hook 은 기본적으로 **최대 500 회** 자동 이어가기 후 멈춥니다. Claude Code 실행 전 환경 변수로 override:

```bash
export LONG_TASK_MAX_STOP_CONTINUES=1000
```

## 동작 순서

1. **Phase 1 (셋업, 유일한 사용자 상호작용):** 사용자 인터뷰, `.agent/goal.md` 작성, `.agent/plans.md` 마일스톤 설계, `.agent/standards.md` 와 `.agent/implement.md` 정의. 최종 승인. `.agent/state.md` 가 `status: active` 로 생성됨.
2. **Phase 2 (오케스트레이션 루프):** 마일스톤마다 — 상태 재읽기, worktree 에서 병렬 implementer 서브에이전트 디스패치, 검증(test/lint/type), merge, 아키텍처 리뷰어 디스패치, fix 사이클, `progress.md` 업데이트. Stop hook 이 턴 사이마다 자동으로 이어감.
3. **Phase 3 (완료):** 전체 코드베이스 cross-cutting 리뷰, 치명적 이슈 처리, `/long-task complete` 실행 → `.agent/audit.md` 작성 → 사용자에게 보고.

## 상태 파일 (`.agent/`)

| 파일             | 용도                                                | 업데이트 시점                                 |
| ---------------- | --------------------------------------------------- | --------------------------------------------- |
| `state.md`       | lifecycle 상태, phase, runaway 카운터               | 모든 슬래시 커맨드 + Stop hook 발동 시        |
| `goal.md`        | 문제, 결과물, 수용 기준, non-goal                   | 셋업 시 1회                                   |
| `plans.md`       | 아키텍처, 마일스톤, 태스크                          | 셋업 시 1회 + 스코프 발견 시 추가             |
| `standards.md`   | 코드 품질 기준 (모든 서브에이전트가 읽음)           | 1회                                           |
| `implement.md`   | 서브에이전트 워크플로우 (모든 서브에이전트가 읽음)  | 1회                                           |
| `progress.md`    | 현재 상태, 결정 사항, 아키텍처 요약                 | 모든 액션 후                                  |
| `audit.md`       | 완료 audit: acceptance criteria → 실제 증거 매핑    | `/long-task complete` 실행 시 1회             |

## 프로젝트 구조

```
long-task/
├── .claude-plugin/
│   └── plugin.json                        # 플러그인 메타데이터
├── commands/
│   └── long-task.md                       # /long-task 슬래시 커맨드
├── scripts/
│   ├── long_task.py                       # lifecycle helper + Stop hook
│   ├── install.sh                         # 멱등성 Stop hook 설치
│   └── uninstall.sh                       # Stop hook 제거
└── skills/
    └── long-task/
        ├── SKILL.md                       # 스킬 정의 및 워크플로우
        └── references/
            ├── project-templates.md       # `.agent/` 파일 템플릿
            └── completion-audit.md        # 완료 audit 가이드
```

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼 ([Claude Code](https://code.claude.com), Codex, opencode, Copilot CLI 등 — [메인 README](../README.ko.md#다른-에이전트-플랫폼에서-사용) 참조)
- helper 스크립트와 Stop hook 동작을 위한 `python3`
- Git 저장소 (worktree 서브에이전트에 필요)

## 크레딧

lifecycle / Stop hook 설계는 codex `/goal` 을 Claude Code 로 복제한 [github.com/jthack/claude-goal](https://github.com/jthack/claude-goal) 에서 가져왔습니다. 이 플러그인은 그 메커니즘을 다중 마일스톤 오케스트레이션과 결합합니다.

## 라이선스

MIT
