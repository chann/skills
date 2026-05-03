# conventional-commit

[English](README.md) · [← 메인으로](../README.ko.md)

작업 디렉터리(working tree)의 변경사항을 의미 단위로 분리하여 [Conventional Commits](https://www.conventionalcommits.org/) 규약에 맞춘 커밋을 만들어 주는 스킬입니다. 커밋 후 push까지 실행하거나, 비순응 커밋 히스토리를 재작성할 수도 있습니다.

## 주요 기능

- staged + unstaged 변경을 의미 단위(feat / fix / docs / ...)로 그룹핑하여 unit 별로 단일 커밋 생성
- 절대 `git add .` 사용하지 않고 항상 명시 경로로 staging
- `.env*`, `*_rsa`, `*.pem` 등 비밀 의심 파일은 기본 제외 + 경고
- `git filter-branch` 로 비순응 커밋 subject 만 재작성, 기존 body는 보존
- 이미 원격에 푸시된 커밋의 rewrite는 기본 거부 (대신 3-option 메뉴 표시)
- force push / hook 우회(`--no-verify`) 자동 실행 안 함

## 설치 방법

**권장 (전역 + 자동 승인, 한 방):**

```bash
npx skills add -y -g chann/skills@conventional-commit
```

**프로젝트 로컬:**

```bash
npx skills add chann/skills@conventional-commit
```

**수동 설치:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/conventional-commit" ~/.claude/skills/conventional-commit
```

## 사용 방법

커밋 작성을 요청하면 자동으로 트리거되거나, 명시적 커맨드를 사용할 수 있습니다:

| 커맨드                         | 스킬                           | 동작                                                                           |
| ------------------------------ | ------------------------------ | ------------------------------------------------------------------------------ |
| `/conventional-commit`         | `conventional-commit`          | staged + unstaged 변경을 의미 단위로 분리해 unit 마다 Conventional Commit 생성 |
| `/conventional-commit-push`    | `conventional-commit-push`     | 위 작업 후 `git push` 까지 진행 (force 안 함)                                  |
| `/conventional-commit-rewrite` | `conventional-commit-rewrite`  | 최근 비순응 커밋 subject 를 Conventional 형식으로 재작성                       |

**예시:**

```
> 변경사항 의미 단위로 커밋해줘
> commit my changes
> /conventional-commit-push
> /conventional-commit-rewrite
```

## 동작 순서

### `/conventional-commit` (기본)

1. 작업 트리 점검 (`git status --short`, `git diff`, `git diff --cached`)
2. staged + unstaged 변경을 의미 단위로 그룹핑 (unit 마다 Conventional Commit 1개)
3. 커밋 플랜 출력, 사용자 확인 대기
4. 명시 경로 `git add <paths>` 로 한 단위씩 커밋 생성
5. `git log --oneline` 으로 최종 요약 표시

### `/conventional-commit-push`

기본 워크플로우 실행 후 `git push`. `--force` / `--force-with-lease` 절대 사용 안 함. push 가 거부되면(non-fast-forward) 자동 해결 시도 없이 즉시 에러를 사용자에게 노출하고 중단.

### `/conventional-commit-rewrite`

1. 재작성 범위 결정 (기본: upstream / `main` / `master` merge-base 부터 HEAD까지)
2. 안전 검사 (작업 트리 깨끗함 / HEAD attached / 범위 내 커밋이 원격에 없음)
3. 푸시된 커밋이 있으면 3-option 메뉴 (Cancel / Force-push / Branch-based) 표시 — 기본 Cancel
4. Conventional Commits regex 로 비순응 커밋 식별 (merge 커밋 제외)
5. 매핑 테이블로 새 subject 생성; 기존 body는 그대로 보존
6. old → new 플랜 출력 후 명시적 확인 대기
7. `git filter-branch --msg-filter` (in-place) 또는 branch-based cherry-pick 적용
8. 사후 정리

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

## 프로젝트 구조

```
conventional-commit/
├── .claude-plugin/
│   └── plugin.json                       # 플러그인 메타데이터
├── commands/
│   ├── conventional-commit.md            # /conventional-commit (기본)
│   ├── conventional-commit-push.md       # /conventional-commit-push 커맨드
│   └── conventional-commit-rewrite.md    # /conventional-commit-rewrite 커맨드
└── skills/
    ├── conventional-commit/              # 메인 스킬 — 전체 워크플로우 + 공유 스크립트
    │   ├── SKILL.md                      # 스킬 정의 및 워크플로우
    │   └── scripts/
    │       └── rewrite_msg.py            # rewrite 용 filter-branch 헬퍼
    ├── conventional-commit-push/
    │   └── SKILL.md                      # push 변형 스킬
    └── conventional-commit-rewrite/
        └── SKILL.md                      # rewrite 변형 스킬
```

## 요구 사항

- [Claude Code](https://code.claude.com) (CLI, 데스크톱 앱, 또는 IDE 확장)
- Git 저장소
- Python 3.10+ (`/conventional-commit-rewrite` 의 `rewrite_msg.py` 실행 시 필요)

## 라이선스

MIT
