# git-skill

[English](README.md) · [← 메인으로](../README.ko.md)

Git 워크플로우 스킬 모음입니다. 작업 디렉터리 변경사항을 [Conventional Commits](https://www.conventionalcommits.org/) 단위로 분리해 커밋하고, 푸시 / 비순응 히스토리 재작성 / `main` 또는 `dev` 브랜치로 머지 후 보호 브랜치가 아닌 소스 브랜치 삭제 / 이미 머지된 로컬 브랜치 일괄 정리까지 지원합니다.

## 주요 기능

- **Commit / Push / Rewrite** — staged + unstaged 변경을 의미 단위(feat / fix / docs / ...)로 그룹핑해 단일 Conventional Commit 생성, 선택적 push, 비순응 subject 재작성
- 절대 `git add .` 사용 안 함, 항상 명시 경로로 staging
- `.env*`, `*_rsa`, `*.pem` 등 비밀 의심 파일은 기본 제외 + 경고
- `git filter-branch` 로 비순응 커밋 subject 만 재작성, 기존 body는 보존
- 이미 원격에 푸시된 커밋의 rewrite는 기본 거부 (대신 3-option 메뉴 표시) — 단, `force` 키워드로 명시 동의 시 강제 진행
- **Merge / Cleanup** — `main` (또는 `dev`/`develop`) 으로 머지 후 보호 브랜치가 아닌 소스 브랜치를 `git branch -d` 로 삭제, 보호 브랜치에 이미 머지된 모든 로컬 브랜치를 일괄 삭제
- force push / hook 우회(`--no-verify`) / `git branch -D` 자동 실행 안 함 (단, `/git-commit-rewrite` `force` 키워드로 명시 동의 시 force push)

## 설치 방법

**권장 (전역 + 자동 승인, 한 방):**

```bash
npx skills add -y -g chann/skills@git-skill
```

**프로젝트 로컬:**

```bash
npx skills add chann/skills@git-skill
```

**수동 설치:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/git-skill" ~/.claude/skills/git-skill
```

## 사용 방법

커밋 / 머지 / 브랜치 정리 작업을 요청하면 자동으로 트리거되거나, 명시적 커맨드를 사용할 수 있습니다:

| 커맨드                  | 스킬                  | 동작                                                                           |
| ----------------------- | --------------------- | ------------------------------------------------------------------------------ |
| `/git-commit`           | `git-commit`          | staged + unstaged 변경을 의미 단위로 분리해 unit 마다 Conventional Commit 생성 |
| `/git-commit-push`      | `git-commit-push`     | 위 작업 후 `git push` 까지 진행 (force 안 함)                                  |
| `/git-commit-rewrite`   | `git-commit-rewrite`  | 최근 비순응 커밋 subject 를 Conventional 형식으로 재작성                       |
| `/git-merge-to-main`    | `git-merge-to-main`   | 현재 브랜치를 `main` 으로 머지 후 보호 브랜치가 아니면 소스 브랜치 삭제        |
| `/git-merge-to-dev`     | `git-merge-to-dev`    | 현재 브랜치를 `dev` (없으면 `develop`) 으로 머지 후 보호 브랜치가 아니면 삭제  |
| `/git-branch-cleanup`   | `git-branch-cleanup`  | 보호 브랜치에 이미 머지된 모든 로컬 브랜치 삭제                                |

**예시:**

```
> 변경사항 의미 단위로 커밋해줘
> commit my changes
> /git-commit-push
> /git-commit-rewrite
> dev에 머지해줘
> 머지된 브랜치 다 정리해줘
```

## 동작 순서

### `/git-commit` (기본)

1. 작업 트리 점검 (`git status --short`, `git diff`, `git diff --cached`)
2. staged + unstaged 변경을 의미 단위로 그룹핑 (unit 마다 Conventional Commit 1개)
3. 커밋 플랜 출력, 사용자 확인 대기
4. 명시 경로 `git add <paths>` 로 한 단위씩 커밋 생성
5. `git log --oneline` 으로 최종 요약 표시

### `/git-commit-push`

기본 워크플로우 실행 후 `git push`. `--force` / `--force-with-lease` 절대 사용 안 함. push 가 거부되면(non-fast-forward) 자동 해결 시도 없이 즉시 에러를 사용자에게 노출하고 중단.

### `/git-commit-rewrite`

1. 재작성 범위 결정 (기본: upstream / `main` / `master` merge-base 부터 HEAD까지)
2. 안전 검사 (작업 트리 깨끗함 / HEAD attached / 범위 내 커밋이 원격에 없음)
3. 푸시된 커밋이 있으면 3-option 메뉴 (Cancel / Force-push / Branch-based) 표시 — 기본 Cancel
4. Conventional Commits regex 로 비순응 커밋 식별 (merge 커밋 제외)
5. 매핑 테이블로 새 subject 생성; 기존 body는 그대로 보존
6. old → new 플랜 출력 후 명시적 확인 대기
7. `git filter-branch --msg-filter` (in-place) 또는 branch-based cherry-pick 적용
8. 사후 정리

### `/git-merge-to-main`

1. 사전조건 검사 — git 저장소, HEAD attached, 현재 브랜치 ≠ `main`, 작업 트리 깨끗함, `main` 로컬 존재
2. 플랜 출력 (`main..$src` 로그 + 삭제 단계) 후 명시적 확인 대기
3. (선택) `origin/main` fetch 후 로컬 `main` 이 뒤처져 있으면 경고 (자동 pull 안 함)
4. `git checkout main` 후 `git merge "$src"` — 가능하면 fast-forward. 충돌 시 즉시 중단, 자동 해결 안 함
5. 소스 브랜치 삭제 또는 유지: 보호 브랜치가 아니면 `git branch -d "$src"` 실행, 보호 브랜치이면 로컬 삭제 스킵
6. `git log --oneline -5` 출력. push 는 사용자가 수동으로

보호 소스 브랜치: `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`.

### `/git-merge-to-dev`

`/git-merge-to-main` 과 동일하지만 타깃 결정 규칙: `dev` 가 로컬에 있으면 `dev`, 없으면 `develop`, 둘 다 없으면 중단.

### `/git-branch-cleanup`

1. 로컬에 존재하는 보호 브랜치(앵커) 확인: `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`
2. 후보 식별 — 보호/현재 브랜치를 제외한 모든 로컬 브랜치 중 적어도 하나의 앵커에 대해 `git merge-base --is-ancestor` 가 참인 브랜치
3. 후보별 "어느 앵커에 머지되어 있는지" 와 함께 플랜 출력, 유지되는 브랜치도 같이 표시. 명시적 확인 대기 (기본: no)
4. 각 후보를 `git branch -d` (안전) 로 삭제. 거부되면 스킵 + 보고, 절대 `-D` 로 강제하지 않음
5. 요약

## Conventional Commits 형식

```
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

**허용 type:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

**Breaking change** — type/scope 뒤에 `!` 추가 (예: `feat(api)!: drop v1 endpoints`) 또는 `BREAKING CHANGE: ...` 푸터 사용.

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

- `git add .` / `git add -A` 사용 안 함 (항상 명시 경로)
- `--no-verify` / `--no-gpg-sign` 으로 hook 우회 안 함
- force push 안 함 (`--force-with-lease` 도 사용자의 명시적 동의 후에만)
- 비밀 의심 파일(`.env*`, `credentials.*`, `*_rsa`, `*.pem`, `*.key`, `*.p12`) 명시적 override 없이 커밋 안 함
- `feat` 와 `fix` 를 한 커밋에 합치지 않음
- 푸시된 커밋을 3-option 메뉴 없이 재작성 안 함
- `git filter-branch --root` 사용 안 함
- 재작성 시 티켓 참조 누락 안 함 (`Refs:` 푸터로 이동)
- `git branch -D` (강제 삭제) 사용 안 함 — 항상 `git branch -d` (안전 삭제)
- 머지 충돌 자동 해결, 머지 후 자동 push, 원격 브랜치 자동 삭제 안 함
- 보호 브랜치 삭제 안 함: `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`

## 프로젝트 구조

```
git-skill/
├── .claude-plugin/
│   └── plugin.json                       # 플러그인 메타데이터
├── commands/
│   ├── git-commit.md                     # /git-commit (기본)
│   ├── git-commit-push.md                # /git-commit-push 커맨드
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
