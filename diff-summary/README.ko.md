# diff-summary

[English](README.md) · [← 메인으로](../README.ko.md)

Git diff를 한국어·영어 보고서로 설명하거나, 원본 패치를 브라우저에서 보여주는 플러그인입니다. 요약 스킬 하나가 옵션으로 세 가지 출력을 맡고, `diff-viewer`는 분석 없이 패치만 보여주므로 따로 둡니다.

## 주요 기능

- `/diff-summary`는 무엇이 왜 바뀌었고 코드, 아키텍처, 패턴, API 계약, 테스트, 운영이 어떻게 연결되는지 설명합니다. 내용과 근거를 맞춘 한국어·영어 Markdown과 자체 완결형 이중언어 대화형 HTML을 `.diff-summaries/`에 만듭니다.
- `--md`는 Markdown 두 개만 남깁니다. HTML도 브라우저도 없습니다.
- `--quiz`는 두 보고서에 서로 대응하는 `## Quiz`를 붙이고 HTML에 대화형 퀴즈를 넣습니다.
- `/diff-viewer`는 현재 작업 트리 diff를 통합·분할 보기 HTML로 보여주며, 한국어/영어 전환을 지원합니다. 코드를 분석하지는 않습니다.
- 현재, 스테이징된, 스테이징하지 않은 변경, 마지막 커밋이나 최근 N개 커밋, 특정 커밋, 범위나 브랜치 비교, PR을 지원합니다.

## 설치 방법

**권장(전역 설치, 자동 승인):**

```bash
npx skills add -y -g chann/skills \
  --skill diff-summary \
  --skill diff-viewer
```

**현재 프로젝트에 설치:**

```bash
npx skills add chann/skills \
  --skill diff-summary \
  --skill diff-viewer
```

두 스킬은 각각 따로 설치할 수 있습니다. `diff-summary`에는 수집기, 생성기, HTML 템플릿이 함께 들어 있어 `diff-viewer` 없이도 실행됩니다. 설치 전에 `npx skills add chann/skills -l --full-depth`로 selector를 확인할 수 있습니다.

**수동 설치:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/diff-summary" ~/.claude/skills/diff-summary
```

## 사용 방법

자연어로 요청하면 알맞은 스킬이 자동으로 실행됩니다. 직접 호출할 때는 Claude Code의 슬래시 selector나 Codex의 달러 selector를 사용합니다:

| Claude Code | Codex | 출력 |
| --- | --- | --- |
| `/diff-summary [scope]` | `$diff-summary [scope]` | `.diff-summaries/`에 한국어·영어 Markdown + 이중언어 HTML |
| `/diff-summary [scope] --md` | `$diff-summary [scope] --md` | 한국어·영어 Markdown만 |
| `/diff-summary [scope] --quiz` | `$diff-summary [scope] --quiz` | 기본 결과물에 서로 대응하는 `## Quiz` 섹션과 대화형 퀴즈 추가 |
| `/diff-viewer` | `$diff-viewer` | `.diffs/<YYYY-MM-DD>_<tag>.html`에 HTML diff viewer |

"마크다운만", "markdown only"는 `--md`로, "퀴즈", "quiz me"는 `--quiz`로 인식합니다.

`--md --quiz`를 함께 쓰면 퀴즈 섹션이 들어간 Markdown 두 개만 만들고 HTML은 만들지 않습니다. 생성기가 Markdown 전용 모드에서도 `## Quiz` 섹션을 검증하며, HTML과 브라우저 여부는 `--md`가 정합니다.

**예시:**

```
> 코드를 요약해줘
> /diff-summary main..dev
> 마지막 커밋 코드를 요약해줘
> PR #42 변경 요약
> /diff-summary HEAD~3..HEAD --md
> 마지막 커밋 diff 퀴즈 만들어줘
> /diff-viewer
```

**출력 예시:**

```
.diff-summaries/
├── 2026-04-08_main-dot2-dev-<hash12>.md     # 한국어 보고서
├── 2026-04-08_main-dot2-dev-<hash12>.en.md  # 영어 보고서
└── 2026-04-08_main-dot2-dev-<hash12>.html   # 이중언어 대화형 페이지 (--md에서는 만들지 않음)
.diffs/
└── 2026-04-08_working.html
```

지정한 범위는 그대로 유지됩니다. `main..dev`와 `main...dev`는 서로 다른 비교이므로 한쪽으로 바꾸지 않습니다.

### 목적에 맞는 워크플로우

| 목적 | 워크플로우 | 결과 |
|---|---|---|
| 무엇이 왜 바뀌었고 어떻게 연결되는지 설명 | `diff-summary` | 심각도 분류 없이 근거를 담은 요약 카드 |
| 같은 설명을 Markdown으로만 저장 | `diff-summary --md` | 검증된 한국어·영어 Markdown |
| 변경을 설명하고 이해도를 확인 | `diff-summary --quiz` | Markdown 정답지 + 오프라인 HTML 퀴즈 |
| 결함, 회귀, 취약점 탐색 | `interrogate` | 심각도가 붙은 발견 사항 |
| 기존 코드가 어떻게 동작하는지 이해 | `how` | 코드를 따라가며 쓴 설명 |
| 분석 없이 패치 자체 확인 | `diff-viewer` | 통합 또는 분할 보기 방식의 원본 diff HTML |

요약과 리뷰를 함께 요청하면 두 워크플로를 모두 실행하고 설명 카드와 결함 발견 사항을 별도 섹션으로 나눕니다.

## 동작 순서

`/diff-summary`:

1. 요청 범위와 정확한 `..`/`...` 문법을 그대로 검증 및 보존
2. 저장소와 범위를 JSON으로 패키지의 `collect_diff_evidence.py` 표준 입력에 전달. 이 수집기만 Git/GitHub를 실행
3. 크기가 제한된 JSON 결과를 실행하지 않는 데이터로 다루고, 같은 `DS-001` ID를 쓰는 한국어·영어 Markdown 작성(`--quiz`이면 `QZ-001` 문항 포함)
4. 두 보고서를 이중언어 JSON으로 `generate_summary_report.py`의 표준 입력에 보내 내용이 서로 맞는지 확인하고, 두 원본과 HTML 하나를 한 번에 기록(`--markdown-only`는 원본만 기록)
5. `--md`가 아니면 자체 완결형 HTML을 브라우저에서 열기

중요한 추론과 확인하지 않은 런타임, 테스트, 마이그레이션, 배포 결과는 사실처럼 단정하지 않고 명시적으로 구분합니다.

`/diff-viewer`는 별도로 동작합니다. `git diff HEAD`를 캡처해 통합 보기와 분할 보기 HTML을 만들고 브라우저에서 열며, 코드는 분석하지 않습니다. 한국어/영어 전환으로 모든 라벨, 파일 상태, 요약 문구, 내보낸 Markdown 제목이 함께 바뀝니다. diff 본문은 코드이므로 번역하지 않습니다.

### Diff summary HTML

각 보고서는 서버, 네트워크 요청, 패키지 설치나 JavaScript 빌드 없이 로컬 `file://` URL에서 바로 동작합니다.

- **보고서 전체 언어 전환** — 한국어가 기본이며, 영어로 바꾸면 기본 정보, 목차, 카드, 퀴즈, 댓글, 복사 기능과 코드 복사 라벨이 제자리에서 함께 바뀝니다.
- **일관된 요약 카드** — 각 `DS-*` 카드에 분류, 영향도, 파일 근거와 정확한 Markdown 원본이 들어 있습니다.
- **카드별 댓글** — 보고서 내용별 댓글을 브라우저에 저장하며 추가, 수정, 삭제, 전체 삭제와 카드 이동을 지원합니다.
- **Markdown 복사** — 카드 하나, 원본 보고서 전체 또는 카드와 댓글을 묶은 피드백 내용을 복사합니다.
- **퀴즈** — `--quiz`이면 선택지를 한 번 누르는 것으로 정오답과 해설이 나오고, 인쇄하면 정답지가 됩니다.
- **오프라인 탐색** — 접거나 크기를 바꿀 수 있는 사이드바, light/dark/system 테마, 반응형 화면과 인쇄 스타일을 단일 HTML에 담았습니다.

### Diff viewer

- **한국어/영어 전환**, 줄 안의 단어 단위 diff 강조, 줄 번호를 끌어 범위를 골라 다는 댓글, 접고 크기를 바꿀 수 있는 사이드바, light/dark/auto 테마, 8가지 문법 색상(GitHub, Atom One, Monokai, Dracula, Nord, Tokyo Night, Solarized, Gruvbox)을 제공합니다.
- **Markdown 복사**로 현재 리뷰 스레드를 Markdown 보고서로 복사합니다.
- 옵션: `-o output.html`, `--view unified|split`, `--theme auto|light|dark`, `--language auto|en|ko`, `--code-scheme <scheme>`.

## 안전 경계

근거 수집기는 정해진 인자, 정제된 프로세스 환경, 정확한 범위 검사, 저장소 설정을 통한 추가 코드 실행 차단, 민감한 경로 검사와 명령 출력 제한을 적용합니다. 저장소 diff, 경로, 커밋 메시지, PR 텍스트와 오류는 모두 신뢰하지 않는 데이터로만 다룹니다. 그 안의 지시를 따르거나 그 내용을 바탕으로 셸 명령이나 파일 탐색을 추가로 실행하지 않습니다. 생성기는 심볼릭 링크인 출력 디렉터리를 거부하고 충돌하지 않는 파일명을 직접 정합니다.

스킬은 대상 저장소의 `.gitignore`에 `.diff-summaries/`와 `.diffs/` 추가를 제안하지만 자동으로 수정하지 않습니다.

## 프로젝트 구조

```
diff-summary/
├── .claude-plugin/
│   └── plugin.json                        # 플러그인 메타데이터
├── commands/
│   ├── diff-summary.md                    # /diff-summary [scope] [--md] [--quiz]
│   └── diff-viewer.md                     # /diff-viewer
└── skills/
    ├── diff-summary/
    │   ├── SKILL.md
    │   ├── agents/openai.yaml
    │   ├── evals/evals.json
    │   ├── scripts/
    │   │   ├── collect_diff_evidence.py   # 강화된 Git/GitHub -> 제한된 JSON
    │   │   └── generate_summary_report.py # 검증된 Markdown -> 오프라인 HTML
    │   └── assets/summary-template.html
    └── diff-viewer/
        ├── SKILL.md
        ├── scripts/generate_diff_report.py
        └── assets/diff-template.html
```

## 요구 사항

- [Claude Code](https://code.claude.com)(CLI, 데스크톱 앱, IDE 확장) 또는 Codex
- Git 저장소
- `diff-summary` 증거 수집에는 Git 2.45+
- Python 3.10+ (`diff-summary`와 `diff-viewer` 보고서 생성 시 필요, 표준 라이브러리만 사용)

## 라이선스

MIT
