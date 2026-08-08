# git-skill

[English](README.md) · [← 메인으로](../README.ko.md)

Git 작업을 위한 스킬 모음입니다. 작업 디렉터리의 변경 사항을 [Conventional Commits](https://www.conventionalcommits.org/) 단위로 나눠 커밋합니다. 한 번만 푸시하거나, 구현 중 검증한 작업 단위마다 계속 푸시하거나, 푸시하지 않고 로컬 커밋만 남길 수 있습니다. 형식에 맞지 않는 커밋 기록을 다시 쓰고, `main` 또는 `dev`에 머지한 뒤 보호 대상이 아닌 소스 브랜치를 삭제하거나 이미 머지된 로컬 브랜치를 한꺼번에 정리하는 기능도 제공합니다.

## 주요 기능

- **커밋 / 푸시 / 작업 중 커밋 / 재작성** — 스테이징 여부와 관계없이 변경을 의미 단위(`feat`, `fix`, `docs` 등)로 묶어 Conventional Commit을 하나씩 생성. 필요하면 푸시하고, 구현 중 검증된 결과마다 커밋해 즉시 푸시하거나 모두 로컬에 유지하며, 형식에 맞지 않는 제목도 재작성
- `git add .`은 사용하지 않고 항상 경로를 직접 지정해 스테이징
- `.env*`, `*_rsa`, `*.pem` 등 비밀 정보가 의심되는 파일은 기본으로 제외하고 경고. 정확한 파일명 `.env.example`은 예외
- `git filter-branch`로 형식에 맞지 않는 커밋 제목만 다시 쓰고 기존 본문은 보존
- 이미 원격에 푸시된 커밋은 기본적으로 재작성하지 않고 선택지 3개를 제시. 단, `force` 키워드로 명시적으로 동의하면 강제로 진행
- **머지 / 정리** — `main` 또는 `dev`/`develop`에 머지한 뒤 보호 브랜치가 아닌 소스 브랜치를 `git branch -d`로 삭제하고, 보호 브랜치에 이미 머지된 로컬 브랜치를 한꺼번에 정리
- 강제 푸시, hook 우회(`--no-verify`), `git branch -D`는 자동으로 실행하지 않음. 단, `/git-commit-rewrite`에 `force` 키워드를 함께 주면 강제 푸시 허용

## 설치 방법

**권장(전역 설치, 자동 승인):**

```bash
npx skills add -y -g chann/skills \
  --skill git-commit \
  --skill git-commit-push \
  --skill git-commit-push-realtime \
  --skill gcpr \
  --skill git-commit-realtime \
  --skill git-commit-rewrite \
  --skill git-merge-to-main \
  --skill git-merge-to-dev \
  --skill git-branch-cleanup
```

**현재 프로젝트에 설치:**

```bash
npx skills add chann/skills \
  --skill git-commit \
  --skill git-commit-push \
  --skill git-commit-push-realtime \
  --skill gcpr \
  --skill git-commit-realtime \
  --skill git-commit-rewrite \
  --skill git-merge-to-main \
  --skill git-merge-to-dev \
  --skill git-branch-cleanup
```

설치할 때는 실제 스킬 이름을 `--skill`로 지정합니다. `git-skill`은 이 Git 워크플로우들을 패키징하는 플러그인 디렉터리 이름입니다.

Codex `$gcpr` selector와 실행에 필요한 워크플로만 추가하려면:

```bash
npx skills add -y -g chann/skills \
  --skill gcpr \
  --skill git-commit-push-realtime \
  --skill git-commit \
  --skill git-commit-push
```

**수동 설치:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/git-skill" ~/.claude/skills/git-skill
```

## 사용 방법

자연어로 요청하면 알맞은 워크플로가 자동으로 실행됩니다. 직접 호출할 때는
Claude Code에서 `/name`, Codex에서 `$name`을 사용합니다:

| Claude Code                     | Codex                        | 동작                                                                           |
| ------------------------------- | ---------------------------- | ------------------------------------------------------------------------------ |
| `/git-commit`                   | `$git-commit`                | 스테이징 여부와 관계없이 변경을 의미 단위로 나눠 Conventional Commit 생성       |
| `/git-commit-push`              | `$git-commit-push`           | 위 작업 후 `git push`까지 진행하며 강제 푸시는 사용하지 않음                    |
| `/git-commit-push-realtime` · `/gcpr` | `$git-commit-push-realtime` · `$gcpr` | 구현 중 검증된 의미 단위가 끝날 때마다 커밋하고 즉시 푸시                |
| `/git-commit-realtime` · `/gcr` | `$git-commit-realtime`       | 구현 중 검증된 의미 단위가 끝날 때마다 로컬에만 커밋 — 푸시하지 않음           |
| `/git-commit-rewrite`           | `$git-commit-rewrite`        | 최근 커밋 중 Conventional 형식에 맞지 않는 제목을 재작성                       |
| `/git-merge-to-main`            | `$git-merge-to-main`         | 현재 브랜치를 `main`으로 머지 후 보호 브랜치가 아니면 소스 브랜치 삭제         |
| `/git-merge-to-dev`             | `$git-merge-to-dev`          | 현재 브랜치를 `dev`(없으면 `develop`)로 머지 후 보호 브랜치가 아니면 삭제      |
| `/git-branch-cleanup`           | `$git-branch-cleanup`        | 보호 브랜치에 이미 머지된 모든 로컬 브랜치 삭제                                |

**예시:**

```
> 변경사항 의미 단위로 커밋해줘
> commit my changes
> /git-commit-push
> 작업 중간중간 의미 있는 단위마다 커밋하고 푸시해줘
> $gcpr
> 푸시 없이 의미 단위마다 커밋만 해줘
> /gcr
> /git-commit-rewrite
> dev에 머지해줘
> 머지된 브랜치 다 정리해줘
```

## 동작 순서

### `/git-commit` (기본)

1. 작업 트리 점검 (`git status --short`, `git diff`, `git diff --cached`)
2. 스테이징 여부와 관계없이 변경을 의미 단위로 묶기(단위마다 Conventional Commit 1개)
3. 커밋 계획을 보여주고 사용자 확인 대기
4. 경로를 직접 지정한 `git add <paths>`로 한 단위씩 커밋
5. `git log --oneline`으로 최종 결과 표시

### `/git-commit-push`

기본 워크플로를 실행한 뒤 `git push`합니다. `--force`와 `--force-with-lease`는 사용하지 않습니다. 푸시가 거부되면(non-fast-forward) 자동으로 해결하려 하지 않고 오류를 사용자에게 알린 뒤 중단합니다.

### `/git-commit-push-realtime` (별칭 `/gcpr`, `$gcpr`)

1. 수정하기 전에 브랜치, upstream, 기존 커밋, 작업 트리와 비밀 정보 경로의 위험 확인
2. 결과를 기준으로 커밋 단위 계획. 경과 시간, 파일 수나 남은 토큰을 기준으로 나누지 않음
3. 서로 밀접한 작업을 하나의 결과로 완성하고 관련 테스트와 저장소 필수 검사 실행
4. 커밋할 경로와 검증 결과를 보여준 뒤 해당 경로만 스테이징하고 정확한 Conventional Commit 생성
5. 바로 푸시하고 다음 작업을 시작하기 전에 `HEAD...@{u}`가 `0 0`인지 확인
6. upstream이 바뀌거나 푸시가 거부되면 중단. pull, merge, rebase나 강제 푸시로 자동 해결하지 않음
7. 전체 범위 검증, 커밋 기록, 로컬과 원격의 일치 상태를 확인하고 종료

### `/git-commit-realtime` (별칭 `/gcr`)

`/git-commit-push-realtime`과 같은 기준을 따르되 원격에는 접근하지 않는 워크플로입니다:

1. 수정하기 전에 브랜치, 기존 커밋, 작업 트리와 비밀 정보 경로의 위험 확인
2. 결과를 기준으로 커밋 단위를 계획하고 서로 밀접한 작업을 하나의 결과로 완성·검증
3. 지정한 경로만 스테이징하고 단위마다 정확한 Conventional Commit 생성
4. 커밋 해시를 기록하고 로컬에만 유지. `git push`, pull, merge, rebase는 실행하지 않음
5. 전체 범위 검증, 커밋 기록, 푸시하지 않은 커밋을 보고하고 종료. 푸시는 별도 요청(`/git-commit-push`, `/gcpr`)으로만 진행

### `/git-commit-rewrite`

1. 재작성 범위 결정(기본: upstream, `main` 또는 `master`와의 merge-base부터 HEAD까지)
2. 안전 검사(작업 트리가 깨끗한지, HEAD가 브랜치에 연결되어 있는지, 범위 안의 커밋이 원격에 없는지)
3. 푸시된 커밋이 있으면 취소, 강제 푸시, 새 브랜치 방식의 선택지 3개를 표시하며 기본값은 취소
4. Conventional Commits 정규식으로 형식에 맞지 않는 커밋을 찾고 머지 커밋은 제외
5. 매핑 표를 바탕으로 새 제목을 만들고 기존 본문은 그대로 보존
6. 기존 제목과 새 제목을 보여준 뒤 명시적인 확인 대기
7. `git filter-branch --msg-filter`로 현재 브랜치에서 재작성하거나 새 브랜치에 cherry-pick
8. 사후 정리

### `/git-merge-to-main`

1. 사전 조건 검사 — Git 저장소인지, HEAD가 브랜치에 연결되어 있는지, 현재 브랜치가 `main`이 아닌지, 작업 트리가 깨끗한지, 로컬에 `main`이 있는지 확인
2. `main..$src` 로그와 삭제 단계를 포함한 계획을 보여주고 명시적인 확인 대기
3. 필요하면 `origin/main`을 fetch하고 로컬 `main`이 뒤처져 있으면 경고하되 자동 pull은 하지 않음
4. `git checkout main` 후 `git merge "$src"` 실행. 가능하면 fast-forward하며, 충돌이 나면 자동으로 해결하지 않고 즉시 중단
5. 소스가 보호 브랜치가 아니면 `git branch -d "$src"`로 삭제하고, 보호 브랜치이면 로컬 삭제를 건너뜀
6. `git log --oneline -5` 출력. 푸시는 사용자가 직접 실행

보호 소스 브랜치: `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`.

### `/git-merge-to-dev`

`/git-merge-to-main`과 같지만 대상 브랜치는 로컬에 `dev`가 있으면 `dev`, 없으면 `develop`을 사용합니다. 둘 다 없으면 중단합니다.

### `/git-branch-cleanup`

1. 로컬에 있는 보호 브랜치 확인: `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`
2. 보호 브랜치와 현재 브랜치를 제외하고, 적어도 하나의 보호 브랜치에 `git merge-base --is-ancestor`로 머지됐음이 확인되는 로컬 브랜치를 후보로 선택
3. 후보마다 어느 보호 브랜치에 머지됐는지와 유지할 브랜치의 이유를 함께 보여주고 명시적인 확인 대기. 기본값은 취소
4. 각 후보를 `git branch -d`로 안전하게 삭제. Git이 거부하면 건너뛰고 보고하며 `-D`로 강제하지 않음
5. 요약

## Conventional Commits 형식

```
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

**허용하는 type:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

**호환성을 깨는 변경** — type/scope 뒤에 `!`를 추가하거나(예: `feat(api)!: drop v1 endpoints`) `BREAKING CHANGE: ...` 푸터를 사용합니다.

**예시:**

```
feat(parser): add ability to parse arrays
fix(ui): correct button alignment
docs: update README with usage instructions
refactor(auth): extract token validation
chore: update dependencies
feat!: send email on registration

BREAKING CHANGE: email service is now required at boot
```

## 안전 보장

스킬은 **절대로**:

- `git add .`이나 `git add -A` 사용(항상 경로를 직접 지정)
- `--no-verify`나 `--no-gpg-sign`으로 hook 우회
- 강제 푸시. `--force-with-lease`도 사용자가 명시적으로 동의한 뒤에만 사용
- 비밀 정보가 의심되는 파일(`.env*` 중 정확한 파일명 `.env.example`은 예외, `credentials.*`, `*_rsa`, `*.pem`, `*.key`, `*.p12`)을 명시적인 허락 없이 커밋
- 깨진 상태, 시간만 기준으로 나눈 상태, 임시 내용뿐인 작업 중간 결과를 푸시
- `feat`와 `fix`를 한 커밋에 합치기
- 선택지 3개를 보여주지 않고 이미 푸시된 커밋 재작성
- `git filter-branch --root` 사용
- 재작성할 때 티켓 참조 누락. 참조는 `Refs:` 푸터로 이동
- `git branch -D`로 강제 삭제. 항상 `git branch -d`로 안전하게 삭제
- 머지 충돌 자동 해결, 머지 후 자동 푸시, 원격 브랜치 자동 삭제
- 보호 브랜치 삭제: `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`

## 프로젝트 구조

```
git-skill/
├── .claude-plugin/
│   └── plugin.json                       # 플러그인 메타데이터
├── commands/
│   ├── git-commit.md                     # /git-commit (기본)
│   ├── git-commit-push.md                # /git-commit-push 커맨드
│   ├── git-commit-push-realtime.md       # /git-commit-push-realtime 커맨드
│   ├── gcpr.md                           # /gcpr — 본문이 같은 짧은 별칭
│   ├── git-commit-realtime.md            # /git-commit-realtime 커맨드
│   ├── gcr.md                            # /gcr — 본문이 같은 짧은 별칭
│   ├── git-commit-rewrite.md             # /git-commit-rewrite 커맨드
│   ├── git-merge-to-main.md              # /git-merge-to-main 커맨드
│   ├── git-merge-to-dev.md               # /git-merge-to-dev 커맨드
│   └── git-branch-cleanup.md             # /git-branch-cleanup 커맨드
└── skills/
    ├── git-commit/                       # 메인 커밋 스킬 — 전체 워크플로우 + 공유 스크립트
    │   ├── SKILL.md
    │   └── scripts/
    │       └── rewrite_msg.py            # rewrite 용 filter-branch 헬퍼
    ├── git-commit-push/                  # push 변형
    │   └── SKILL.md
    ├── git-commit-push-realtime/         # 검증한 작업 단위마다 커밋하고 푸시
    │   ├── SKILL.md
    │   └── evals/evals.json
    ├── gcpr/                             # 얇은 Codex selector 별칭
    │   ├── SKILL.md
    │   └── agents/openai.yaml
    ├── git-commit-realtime/              # 검증한 작업 단위마다 로컬에만 커밋
    │   ├── SKILL.md
    │   └── evals/evals.json
    ├── git-commit-rewrite/               # rewrite 변형
    │   └── SKILL.md
    ├── git-merge-to-main/                # main 으로 머지 후 소스 삭제
    │   └── SKILL.md
    ├── git-merge-to-dev/                 # dev/develop 로 머지 후 소스 삭제
    │   └── SKILL.md
    └── git-branch-cleanup/               # 머지된 로컬 브랜치 일괄 삭제
        └── SKILL.md
```

## 요구 사항

- [Claude Code](https://code.claude.com) (CLI, 데스크톱 앱, 또는 IDE 확장)
- Git 저장소
- Python 3.10+ (`/git-commit-rewrite` 의 `rewrite_msg.py` 실행 시 필요)

## 라이선스

MIT
