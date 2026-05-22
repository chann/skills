# skills

[English](README.md)

소프트웨어 엔지니어링 워크플로우를 위한 실용적인 에이전트 스킬 모음입니다.

## 스킬 목록

| 스킬                                                | 설명                                                                                          |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **[code-review](code-review/README.ko.md)**         | git diff 기반 자동 코드 리뷰 — 심각도 표시가 있는 마크다운 / HTML 리포트, 추가로 HTML diff 뷰어 |
| **[git-skill](git-skill/README.ko.md)**             | Conventional Commits, push, 히스토리 재작성, main/dev 머지, 머지된 로컬 브랜치 정리            |
| **[long-task](long-task/README.ko.md)**             | 멀티 마일스톤 프로젝트 자율 오케스트레이터 — 병렬 worktree 서브에이전트 + 마일스톤 리뷰 사이클  |

## 설치 방법

모든 스킬을 한 번에 전역 설치 (권장):

```bash
npx skills add -y -g chann/skills
```

스킬별 설치 또는 비전역 / 수동 설치는 각 스킬 README 참조:

- [code-review 설치](code-review/README.ko.md#설치-방법)
- [git-skill 설치](git-skill/README.ko.md#설치-방법)
- [long-task 설치](long-task/README.ko.md#설치-방법)

## 빠른 참조

### code-review → [상세](code-review/README.ko.md)

| 커맨드              | 출력                                      |
| ------------------- | ----------------------------------------- |
| `/code-review`      | 대화에서 결과 표시 (파일 생성 안 함)      |
| `/code-review-md`   | `.reviews/`에 마크다운 리포트 파일 생성   |
| `/code-review-html` | `.reviews/`에 마크다운 + HTML 리포트 생성 |
| `/diff-viewer`      | 작업 트리 diff를 `.diffs/` HTML로 렌더링   |

### git-skill → [상세](git-skill/README.ko.md)

| 커맨드                | 동작                                                                            |
| --------------------- | ------------------------------------------------------------------------------- |
| `/git-commit`         | 작업 트리 변경을 Conventional Commits 단위로 분리해 커밋                        |
| `/git-commit-push`    | 위 작업 후 `git push` 까지 진행 (`--force` 안 함)                               |
| `/git-commit-rewrite` | 최근 비순응 커밋 subject 를 Conventional 형식으로 재작성                        |
| `/git-merge-to-main`  | 현재 브랜치를 `main` 으로 머지 후 소스 브랜치를 `git branch -d` 로 삭제         |
| `/git-merge-to-dev`   | 현재 브랜치를 `dev` (없으면 `develop`) 으로 머지 후 소스 브랜치 삭제            |
| `/git-branch-cleanup` | 보호 브랜치에 이미 머지된 모든 로컬 브랜치 삭제                                 |

### long-task → [상세](long-task/README.ko.md)

| 커맨드       | 동작                                                                                          |
| ------------ | --------------------------------------------------------------------------------------------- |
| `/long-task` | 병렬 worktree 서브에이전트 + 마일스톤 리뷰로 프로젝트를 처음부터 끝까지 자율적으로 구현       |

*"이 프로젝트 처음부터 끝까지 만들어줘"*, *"자율적으로 진행해"*, *"long task 돌려줘"* 같은 문구에도 자동 트리거됩니다.

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
- Python 3.10+ (`code-review-html`, `diff-viewer`, `git-commit-rewrite` 사용 시 필요)

## 라이선스

MIT
