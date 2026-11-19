# git-skill

[English](README.md) · [← 메인으로](../README.ko.md)

보수적인 안전 규칙을 지키는 Git 작업 스킬 모음입니다. `git-commit` 하나로 변경 사항을 [Conventional Commits](https://www.conventionalcommits.org/) 단위로 한 번에 커밋하거나, 커밋 후 푸시하거나, 작업하는 동안 검증한 단위마다 커밋(로컬 유지, 푸시, 배포까지)하거나, 형식에 맞지 않는 커밋 제목을 다시 씁니다. `git-merge`는 `main`, `dev` 또는 원하는 로컬 브랜치로 머지하고, `git-resolve-conflicts`는 멈춘 머지나 rebase를 마무리하며, `git-cleanup`은 끝난 워크트리와 머지된 브랜치를 정리합니다.

## 주요 기능

- **커밋 모드** — `git-commit`은 스테이징 여부와 관계없이 변경을 의미 단위로 묶어 단위마다 Conventional Commit을 하나씩 만듭니다. `push`는 일반 푸시를 더하고, `realtime`은 작업하는 동안 검증된 결과마다 커밋하며, `push realtime`은 그때마다 푸시하고 upstream과 같은 상태인지 확인합니다. `deploy`는 `AGENTS.md`에 이미 적힌 배포 설정으로 체크포인트마다 배포하고, 배포가 확인된 뒤에 다음 단위로 넘어갑니다. `rewrite`는 형식에 맞지 않는 제목을 고칩니다
- 스테이징은 항상 경로를 직접 지정합니다. `git add .`은 쓰지 않습니다
- `.env*`, `*_rsa`, `*.pem` 등 비밀 정보로 보이는 파일은 기본으로 제외하고 경고합니다. 정확한 파일명 `.env.example`은 예외입니다
- `git filter-branch`로 커밋 제목만 다시 쓰고 본문은 그대로 둡니다. 이미 푸시된 커밋이 있으면 선택지 3개를 보여 주고, `force` 키워드로 직접 동의한 경우에만 바로 진행합니다
- **머지** — 현재 브랜치를 정해진 대상 브랜치에 머지한 뒤, 보호 브랜치가 아니면 소스 브랜치를 `git branch -d`로 삭제합니다
- **정리** — 깨끗하고 잠기지 않았으며 머지가 끝난 연결 워크트리를 제거하고, 보호 브랜치에 이미 머지된 로컬 브랜치를 삭제합니다
- 강제 푸시(`rewrite force`를 직접 지정한 경우 제외), hook 우회, `git branch -D`, `git worktree remove --force`는 쓰지 않습니다

## 설치 방법

**권장(전역 설치, 자동 승인):**

```bash
npx skills add -y -g chann/skills \
  --skill git-commit \
  --skill gcr \
  --skill gcpr \
  --skill gcpd \
  --skill git-merge \
  --skill git-resolve-conflicts \
  --skill git-cleanup
```

**프로젝트 로컬 설치:**

```bash
npx skills add chann/skills \
  --skill git-commit \
  --skill gcr \
  --skill gcpr \
  --skill gcpd \
  --skill git-merge \
  --skill git-resolve-conflicts \
  --skill git-cleanup
```

`--skill`에는 스킬 이름을 씁니다. `git-skill`은 플러그인 디렉터리 이름입니다. 별칭은 `git-commit`이 함께 설치되어 있어야 하며, 없으면 실행하지 않고 멈춥니다.

```bash
npx skills add -y -g chann/skills --skill git-commit --skill gcpr
```

**수동 설치:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/git-skill" ~/.claude/skills/git-skill
```

## 사용법

자연어로 요청하면 맞는 스킬과 모드가 선택됩니다. 직접 호출할 때는 Claude Code에서 `/name`, Codex에서 `$name`을 씁니다.

| Claude Code | Codex | 동작 |
| --- | --- | --- |
| `/git-commit` | `$git-commit` | 현재 변경을 Conventional Commit 단위로 한 번 커밋 |
| `/git-commit push` | `$git-commit push` | 위와 같이 커밋한 뒤 일반 `git push` (강제 푸시 없음) |
| `/git-commit realtime` · `/gcr` | `$git-commit realtime` · `$gcr` | 작업하는 동안 검증된 결과마다 커밋하고 모두 로컬에 유지 |
| `/git-commit push realtime` · `/gcpr` | `$git-commit push realtime` · `$gcpr` | 검증된 결과마다 커밋하고 바로 푸시한 뒤 upstream과 같은지 확인 |
| `/git-commit deploy` · `/gcpd` | `$git-commit deploy` · `$gcpd` | 저장소에 적힌 설정으로 결과마다 커밋·푸시·배포하고 배포를 확인 |
| `/git-commit rewrite [range] [force]` | `$git-commit rewrite [range] [force]` | 최근 커밋 중 형식에 맞지 않는 제목을 다시 작성 |
| `/git-merge [main \| dev \| <branch>]` | `$git-merge` | 현재 브랜치를 대상에 머지하고, 보호 브랜치가 아니면 소스 삭제 |
| `/git-resolve-conflicts` | `$git-resolve-conflicts` | 충돌로 멈춘 merge, rebase, cherry-pick, revert를 중단하지 않고 마무리 |
| `/git-cleanup` | `$git-cleanup` | 끝난 워크트리를 제거하고 보호 브랜치에 머지된 로컬 브랜치를 삭제 |

`gcr`, `gcpr`, `gcpd`는 직접 호출할 때만 동작하는 별칭입니다. 자연어 요청으로는 시작되지 않고, 설치된 `git-commit`을 정해진 모드로 실행합니다.

**예시:**

```
> commit my changes
> 변경사항 의미 단위로 커밋해줘
> 커밋하고 푸시해줘
> 작업 중간중간 커밋 푸시해줘
> $gcpr
> 의미 있는 단위마다 배포해줘
> /git-commit rewrite HEAD~5
> dev에 머지해줘
> 머지된 브랜치랑 끝난 워크트리 정리해줘
```

### 0.x에서 옮겨 오기

| 이전 selector | 새 호출 방법 |
| --- | --- |
| `/git-commit-push` | `/git-commit push` |
| `/git-commit-realtime` | `/git-commit realtime` 또는 `/gcr` |
| `/git-commit-push-realtime` | `/git-commit push realtime` 또는 `/gcpr` |
| `/git-commit-push-deploy` | `/git-commit deploy` 또는 `/gcpd` |
| `/git-commit-rewrite` | `/git-commit rewrite` |
| `/git-merge-to-main` | `/git-merge main` |
| `/git-merge-to-dev` | `/git-merge dev` |
| `/git-branch-cleanup` | `/git-cleanup` |

Codex의 `$name` selector도 같은 방식으로 바뀝니다.

## 동작 방식

### `git-commit`

1. 인자나 요청 문장에서 모드를 정하고, Git 명령을 실행하기 전에 그 모드를 밝힙니다. 요청이 모호하면 영향 범위가 작은 모드를 고르며, `push`나 `deploy`는 요청에 없으면 추측하지 않습니다
2. 작업 트리를 살펴 변경을 의도별로 묶고, 비밀 정보로 보이는 파일을 제외한 뒤 커밋 계획을 보여 줍니다
3. 경로를 직접 지정해 스테이징하고 단위마다 Conventional Commit을 만듭니다. hook이 실패하면 우회하지 않고 원인을 고칩니다
4. `push`: `git push`를 실행합니다(upstream이 없으면 `-u`). 거부되면 멈추고 어떻게 맞출지 묻습니다

**체크포인트 모드**(`realtime`, `push realtime`, `deploy`)는 시간이나 파일 수가 아니라 완성된 결과를 기준으로 체크포인트를 나누고, 관련된 가장 좁은 검사와 `git diff --check`로 확인한 뒤 커밋합니다. `realtime`은 모든 체크포인트를 로컬에 둡니다. `push realtime`은 체크포인트마다 푸시하고 다음 단위로 가기 전에 `HEAD...@{u}`가 `0 0`인지 확인합니다. `deploy`는 첫 체크포인트 전에 저장소 문서에서 배포 대상, 경로, 소스, 확인 방법을 정하고, 푸시한 바로 그 리비전을 배포하며, 배포와 필수 health check가 확인될 때까지 다음 작업을 시작하지 않습니다. 끝나면 전체 범위를 다시 검증합니다.

**rewrite**는 범위를 정하고 작업 트리가 깨끗한지, HEAD가 브랜치에 붙어 있는지, 이미 푸시된 커밋이 있는지 확인합니다(취소 / force-with-lease / 새 브랜치 선택지, 기본값은 취소). 본문은 그대로 두고 티켓 접두어는 `Refs:` footer로 옮긴 새 제목을 제안하며, 확인을 받은 뒤 적용합니다. `force` 키워드를 주면 확인 단계와 선택지를 건너뛰고, 푸시된 커밋을 다시 썼다면 마지막에 `git push --force`를 실행합니다.

### `git-merge`

1. 대상을 정합니다. 인자가 있으면 그대로 따르고, `dev`는 없으면 `develop`을 씁니다. 인자가 없으면 `origin/HEAD`의 기본 브랜치, 그것도 없으면 `main`입니다. 대상은 로컬에 있어야 합니다
2. detached HEAD, 정리되지 않은 작업 트리, 대상과 같은 소스 브랜치에서는 실행하지 않습니다
3. 정한 대상을 포함한 계획을 보여 주고 확인을 기다립니다(기본값은 아니오)
4. 일반 `git merge`를 실행하고, 충돌이 나면 멈추고 알립니다
5. 보호 브랜치가 아니면 소스를 `git branch -d`로 삭제합니다. `-D`와 푸시는 하지 않습니다

보호 브랜치: `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`.

### `git-cleanup`

1. 로컬에 있는 보호 브랜치(기준 브랜치)를 찾습니다
2. 워크트리: `git worktree list --porcelain`에서 메인 워크트리나 현재 워크트리가 아니고, 잠겨 있지 않으며, `git status --short`가 비어 있고, 보호 대상이 아닌 브랜치의 끝 커밋이 기준 브랜치에 포함된 연결 워크트리만 제거 대상입니다
3. 브랜치: 보호 브랜치도 현재 브랜치도 아니면서 끝 커밋이 기준 브랜치에 포함된 브랜치가 삭제 대상입니다
4. 둘을 한 계획으로 보여 줍니다. 항목마다 근거가 된 기준 브랜치와 남겨 두는 이유를 적고 확인을 기다립니다
5. `git worktree remove`(`--force` 없음), `git worktree prune`, `git branch -d`(`-D` 없음) 순서로 실행합니다. Git이 거부하면 그대로 두고 알립니다

### `git-resolve-conflicts`

1. 어떤 작업이 왜 멈췄는지 확인합니다. rebase에서는 ours와 theirs가 뒤바뀝니다
2. `--diff-filter=U`로 충돌 경로를 모으고 `--conflict=zdiff3`로 기준 버전을 함께 봅니다
3. 경로마다 종류를 나눕니다. lockfile과 생성된 파일은 손으로 합치지 않고 다시 생성합니다
4. 양쪽이 왜 그렇게 고쳤는지 먼저 확인하고, 함께 살릴 수 있으면 둘 다 살리며, 버린 쪽은 기록합니다
5. 프로젝트의 검사를 실행한 뒤 `--continue`로 마무리합니다. `--abort`, `--skip`, 푸시는 하지 않습니다

## 안전 장치

이 스킬들은 다음을 **하지 않습니다**.

- `git add .` 또는 `git add -A`
- `--no-verify`, `--no-gpg-sign`으로 hook 우회
- 강제 푸시(`rewrite force` 제외). `--force-with-lease`는 `rewrite`에서 사용자가 직접 동의한 경우에만 사용
- 비밀 정보로 보이는 파일(`.env*`, 단 정확한 파일명 `.env.example`은 예외, `credentials.*`, `*_rsa`, `*.pem`, `*.key`, `*.p12`)을 명시적 동의 없이 커밋
- 깨진 상태나 시간 기준, 자리만 채운 체크포인트를 커밋하거나 푸시
- 저장소 문서에 없는 대상에 배포하거나, 배포가 확인되기 전에 체크포인트를 배포 완료로 보고
- 선택지 없이 푸시된 커밋을 다시 쓰기, `git filter-branch --root` 사용, 티켓 참조 삭제
- `git branch -D` 또는 `git worktree remove --force`
- 충돌 자동 해결, 머지 후 자동 푸시, 원격 브랜치 삭제
- 보호 브랜치 삭제: `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`

## 프로젝트 구조

```
git-skill/
├── .claude-plugin/plugin.json
├── commands/                    # 스킬마다 /name 명령 하나
└── skills/
    ├── git-commit/
    │   ├── SKILL.md             # 모드, 형식, 기본 흐름, 안전 규칙
    │   ├── references/
    │   │   ├── checkpoints.md   # realtime, push realtime, deploy 진행 방식
    │   │   ├── deploy.md        # 문서화된 설정, 배포 경로, 확인 단계
    │   │   └── rewrite.md       # 커밋 기록 재작성과 force 모드
    │   └── scripts/rewrite_msg.py
    ├── gcr/ · gcpr/ · gcpd/     # 모드가 고정된 직접 호출 전용 별칭
    ├── git-merge/
    ├── git-resolve-conflicts/
    └── git-cleanup/
```

모든 스킬에는 `agents/openai.yaml`과 `evals/evals.json`이 들어 있습니다.

## 요구 사항

- Claude Code 또는 Codex
- Git 저장소
- Python 3.10+ (`/git-commit rewrite`에서 쓰는 `rewrite_msg.py`용)

## 라이선스

MIT
