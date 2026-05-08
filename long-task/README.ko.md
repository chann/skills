# long-task

[English](README.md) · [← 메인으로](../README.ko.md)

**여러 마일스톤에 걸친 장시간 작업**을 사람의 개입 없이 몇 시간 ~ 며칠 동안 자율적으로 진행하는 오케스트레이터 스킬입니다.

## 주요 기능

- Phase 1(셋업) → Phase 2(오케스트레이션 루프) → Phase 3(완료) 워크플로우로 프로젝트를 처음부터 끝까지 진행
- **격리된 git worktree**에서 병렬 서브에이전트 실행 (최대 5개) 후 검증을 거쳐 merge
- 마일스톤마다 **아키텍처 리뷰 사이클** 강제 (review → fix 서브에이전트 → re-review, 최대 3회)
- `.agent/` 상태 파일을 작업 메모리로 사용하여 컨텍스트 압축/세션 재시작 후에도 진행 상황 보존
- 실행 중 발생하는 모호함은 자율적으로 해결 — 사용자와의 상호작용은 Phase 1 셋업 단계에서만
- `goal.md`, `plans.md`, `standards.md`, `implement.md`, `progress.md` 커스터마이즈 가능한 템플릿 포함

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

## 사용 방법

*"이 프로젝트 처음부터 끝까지 만들어줘"*, *"자율적으로 진행해"*, *"long task 돌려줘"* 같은 문구로 자동 트리거되거나, 명시적으로 호출할 수 있습니다:

| 커맨드       | 동작                                                                          |
| ------------ | ----------------------------------------------------------------------------- |
| `/long-task` | Phase 1 셋업 인터뷰 시작 후 자율 오케스트레이션 루프 진입                     |

**예시:**

```
> /long-task 인증, 게시글, 댓글 기능을 가진 TypeScript Express API 만들어줘
> 처음부터 끝까지 자율적으로 구현해줘. 중간에 질문하지 마
> long task로 이 CLI 전체를 처음부터 만들어줘
```

## 동작 순서

1. **Phase 1 (셋업, 유일한 사용자 상호작용):** 사용자 인터뷰, `.agent/goal.md` 작성, `.agent/plans.md`에 마일스톤 설계, `.agent/standards.md` 와 `.agent/implement.md` 정의. 최종 승인 받기.
2. **Phase 2 (오케스트레이션 루프):** 마일스톤마다 — 상태 재읽기, worktree에서 병렬 implementer 서브에이전트 디스패치, 검증(test/lint/type), merge, 아키텍처 리뷰어 디스패치, fix 사이클 실행, `progress.md` 업데이트. 모든 마일스톤이 끝날 때까지 반복.
3. **Phase 3 (완료):** 전체 코드베이스에 최종 cross-cutting 리뷰, 치명적 이슈 처리, `progress.md`에 최종 요약 작성, 사용자에게 보고.

## 상태 파일 (`.agent/`)

| 파일             | 용도                                                | 업데이트 시점                          |
| ---------------- | --------------------------------------------------- | -------------------------------------- |
| `goal.md`        | 문제, 결과물, 수용 기준, non-goal                   | 셋업 시 1회                            |
| `plans.md`       | 아키텍처, 마일스톤, 태스크                          | 셋업 시 1회 + 스코프 발견 시 추가      |
| `standards.md`   | 코드 품질 기준 (모든 서브에이전트가 읽음)           | 1회                                    |
| `implement.md`   | 서브에이전트 워크플로우 (모든 서브에이전트가 읽음)  | 1회                                    |
| `progress.md`    | 현재 상태, 결정 사항, 아키텍처 요약                 | 모든 액션 후                           |

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
        └── references/
            └── project-templates.md       # 커스터마이즈 가능한 .agent/ 파일 템플릿
```

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼 ([Claude Code](https://code.claude.com), Codex, opencode, Copilot CLI 등 — [메인 README](../README.ko.md#다른-에이전트-플랫폼에서-사용) 참조)
- Git 저장소 (worktree 서브에이전트에 필요)

## 라이선스

MIT
