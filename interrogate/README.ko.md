# code-review

[English](README.md) · [← 메인으로](../README.ko.md)

Git diff의 변경 내용을 설명하고 결함을 검토하거나, 원본 패치를 브라우저에서 볼 수 있게 만드는 플러그인입니다.

## 주요 기능

- 정확성, 보안, 복잡도와 일관성, 유지보수성, 언어별 권장 방식의 5가지 관점에서 코드 변경 사항 분석
- `.reviews/` 디렉터리에 날짜와 커밋 SHA를 조합한 보고서 생성(예: `2026-04-08_a1b2c3d.md`)
- 기본으로 자체 완결형 **이중언어** HTML 보고서 생성. 한국어를 먼저 보여주고 페이지 전체를 영어로 바꿀 수 있으며, 심각도 배지, light/dark/auto 테마, 코드 문법 색상 선택, 접을 수 있는 작은 사이드바, 항목별 Markdown 복사와 댓글, 댓글을 반영해 리뷰를 다시 만드는 "피드백 복사" 기능 제공
- 코드, 동작, 아키텍처, 패턴, API 계약, 테스트와 운영 변경을 근거와 함께 설명하는 `/diff-summary` 제공. 내용과 근거를 맞춘 한국어·영어 Markdown과 대화형 이중언어 HTML을 만들며, `/diff-summary-md`는 Markdown만, `/diff-summary-quiz`는 서로 대응하는 이해도 퀴즈까지 생성
- 리뷰 분석 없이 현재 작업 트리 diff를 브라우저용 HTML로 보여주는 `/diff-viewer` 포함
- 다양한 리뷰 범위 지원: 스테이징된 변경, 특정 커밋, 커밋 범위, 브랜치 비교, PR
- Python, JavaScript/TypeScript 권장 방식 참조 가이드 포함

## 설치 방법

**권장(전역 설치, 자동 승인):**

```bash
npx skills add -y -g chann/skills \
  --skill code-review \
  --skill code-review-md \
  --skill diff-summary \
  --skill diff-summary-md \
  --skill diff-summary-quiz \
  --skill diff-viewer
```

**현재 프로젝트에 설치:**

```bash
npx skills add chann/skills \
  --skill code-review \
  --skill code-review-md \
  --skill diff-summary \
  --skill diff-summary-md \
  --skill diff-summary-quiz \
  --skill diff-viewer
```

설치할 때는 실제 스킬 이름을 `--skill`로 지정합니다. 이 플러그인에는 각각 따로 찾을 수 있는 스킬 6개가 들어 있습니다. 각 diff-summary selector에는 필요한 워크플로와 실행 파일이 함께 들어 있어 `diff-summary-md`나 `diff-summary-quiz`만 설치해도 실행할 수 있습니다. 설치 전에 `npx skills add chann/skills -l --full-depth`로 selector를 확인할 수 있습니다.

**수동 설치:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/code-review" ~/.claude/skills/code-review
```

## 사용 방법

설치 후 자연어로 요청하면 알맞은 스킬이 자동으로 실행됩니다. 직접 호출할
때는 Claude Code의 슬래시 selector나 Codex의 달러 selector를 사용합니다:

| Claude Code                     | Codex                        | 출력                                                                    |
| ------------------------------- | ---------------------------- | ----------------------------------------------------------------------- |
| `/code-review [scope]`          | `$code-review [scope]`       | `.reviews/`에 마크다운 + 자체 완결형 이중언어 HTML 리뷰                  |
| `/code-review-md [scope]`       | `$code-review-md [scope]`    | `.reviews/<YYYY-MM-DD>_<short-sha>.md`에 마크다운만 생성                 |
| `/diff-summary [scope]`         | `$diff-summary [scope]`      | `.diff-summaries/`에 한국어·영어 Markdown + 이중언어 HTML 요약           |
| `/diff-summary-md [scope]`      | `$diff-summary-md [scope]`   | `.diff-summaries/`에 한국어·영어 Markdown만 (HTML 없음)                  |
| `/diff-summary-quiz [scope]`    | `$diff-summary-quiz [scope]` | 이중언어 결과물과 서로 대응하는 `## Quiz` 이해도 섹션                    |
| `/diff-viewer`                  | `$diff-viewer`               | `.diffs/<YYYY-MM-DD>_<tag>.html`에 HTML diff viewer                     |

**예시:**

```
> 내 변경사항 리뷰해줘
> 마지막 커밋 리뷰
> /code-review 스테이징된 변경사항 리뷰
> /code-review-md feature-auth 브랜치를 main과 비교해서 리뷰
> 코드를 요약해줘
> /diff-summary main..dev
> 마지막 커밋 코드를 요약해줘
> PR #42 변경 요약
> /diff-viewer
```

**보고서 출력 예시:**

```
.reviews/
├── 2026-04-08_a1b2c3d.md       # 한국어 보고서 (메인)
├── 2026-04-08_a1b2c3d.en.md    # 영문 보고서 (번역, HTML 전용)
└── 2026-04-08_a1b2c3d.html     # 병합된 이중언어 HTML
.diff-summaries/
├── 2026-04-08_main-dot2-dev-<hash12>.md   # 근거 기반 변경 요약
└── 2026-04-08_main-dot2-dev-<hash12>.html # 대화형 오프라인 요약
.diffs/
└── 2026-04-08_working.html
```

지정한 범위는 그대로 유지됩니다. `main..dev`와 `main...dev`는 서로 다른 비교이므로 한쪽으로 바꾸지 않습니다. 현재 변경, 스테이징된 변경, 스테이징하지 않은 변경, 마지막 커밋이나 최근 N개 커밋, 특정 커밋·범위·브랜치 비교와 PR을 지원합니다.

### 목적에 맞는 워크플로우

| 목적 | 워크플로우 | 결과 |
|---|---|---|
| 무엇이 왜 바뀌었고 코드, 아키텍처, 패턴, API 계약, 테스트, 운영이 어떻게 연결되는지 설명 | `diff-summary` | 심각도 분류 없이 근거를 담은 요약 카드 |
| 같은 설명을 HTML·브라우저 없이 Markdown으로만 저장 | `diff-summary-md` | 검증된 한국어·영어 Markdown 파일 |
| 변경을 설명하고 이해도를 확인 | `diff-summary-quiz` | 한국어·영어 Markdown 정답지 + 대화형 오프라인 HTML 퀴즈 |
| 결함, 회귀, 취약점, 권장 수정 사항 탐색 | `code-review` 또는 `code-review-md` | 심각도별 발견 사항 |
| 분석 없이 패치 자체 확인 | `diff-viewer` | 통합 또는 분할 보기 방식의 원본 diff HTML |

요약과 리뷰를 함께 요청하면 두 워크플로를 모두 실행하고 설명 카드와 결함 발견 사항을 별도 섹션으로 나눕니다.

## 동작 순서

1. 대상 Git diff 수집
2. 언어를 감지하고 알맞은 권장 방식 참조 파일 불러오기
3. 각 변경된 파일을 5가지 차원으로 분석
4. Markdown 보고서를 작성하고 기본 이중언어 HTML에 쓸 영문 파일 생성
5. `/code-review-md`가 아니면 HTML 보고서를 만들고 브라우저에서 열기

`/diff-viewer`는 별도로 동작합니다. `git diff HEAD`를 캡처해 통합 보기와 분할 보기를 지원하는 HTML diff 뷰어를 만들고 브라우저에서 열며, 코드는 분석하지 않습니다. 다른 보고서와 마찬가지로 한국어와 영어를 전환할 수 있어 모든 라벨, 파일 상태, 요약 문구와 내보낸 Markdown 제목이 함께 바뀝니다. diff 본문은 코드이므로 번역하지 않습니다.

`/diff-summary`는 별도의 설명형 흐름을 따릅니다:

1. 요청 범위와 정확한 `..`/`...` 문법을 그대로 검증 및 보존
2. 저장소와 범위를 JSON으로 패키지의 `collect_diff_evidence.py` 표준 입력에 전달하며, 이 수집기만 Git/GitHub를 실행
3. 크기가 제한된 JSON 결과를 실행하지 않는 데이터로 다루고, 같은 `DS-001` ID를 쓰는 한국어·영어 Markdown 작성
4. 두 보고서를 이중언어 JSON으로 `generate_summary_report.py`의 표준 입력에 보내 내용이 서로 맞는지 확인하고, 두 원본과 HTML 하나를 한 번에 기록
5. 자체 완결형 HTML 보고서를 브라우저에서 열기

중요한 추론과 확인하지 않은 런타임, 테스트, 마이그레이션, 배포 결과는 사실처럼 단정하지 않고 명시적으로 구분합니다.

## 코드 리뷰 보고서 구조

### 근거 우선 문체

리뷰에서 찾은 내용은 **관찰 → 영향 → 수정** 순서로 작성합니다. 확인된 사실에는 변경된 경로와 줄 범위를 적습니다. 중요한 추론은 추론이라고 밝히고 근거를 덧붙입니다. 일반적인 칭찬, 상투적인 도입부, 템플릿을 채우기 위한 내용은 넣지 않습니다.

### 조건부 섹션

보고서의 기본 정보와 조치할 수 있는 발견 사항은 항상 제공합니다. `Decision Summary`, `Positive Observations`, `Open Questions`, `File Summary`는 판단에 도움이 되는 별도 정보가 있을 때만 표시합니다. 조치할 내용이 없으면 이를 직접 밝히고, 남아 있는 중요한 위험이나 확인하지 못한 부분만 적습니다.

## HTML 보고서

`/code-review`는 한국어 보고서와 영문 번역을 하나의 자체 완결형 HTML로 합치며 다음 기능을 제공합니다:

- **언어 전환** — 한국어를 기본으로 보여주며 전체 페이지를 영어로 바꿀 수 있습니다. 번역이 없으면 언어 전환 버튼을 숨기고 한 언어만 표시합니다.
- **테마와 코드 색상** — light/dark/auto 페이지 테마와 GitHub, Monokai, Dracula, Nord 등 8가지 문법 강조 색상을 제공합니다. diff와 코드 블록도 선택한 색상에 맞춰 바뀝니다.
- **작은 사이드바** — 접거나 드래그해 크기를 바꿀 수 있으며 섹션 탐색과 댓글 패널이 들어 있습니다.
- **항목별 "Markdown 복사"** — 발견 사항 하나의 Markdown만 복사합니다.
- **항목별 댓글** — 발견 사항마다 리뷰 댓글을 작성합니다. 브라우저에 발견 사항 ID별로 저장되므로 언어를 바꿔도 유지됩니다.
- **"피드백 복사"** — 원본 발견 사항 Markdown과 작성한 댓글을 묶어 다시 작성할 때 쓸 내용을 만듭니다. 새 `/code-review` 실행에 붙여 넣으면 피드백을 반영해 리뷰를 다시 작성합니다.

### Diff summary HTML

각 `/diff-summary` HTML 보고서는 서버, 네트워크 요청, 패키지 설치나 JavaScript 빌드 없이 로컬 `file://` URL에서 바로 동작합니다.

- **보고서 전체 언어 전환** — 한국어가 기본이며, 영어로 바꾸면 기본 정보, 목차, 카드, 퀴즈, 댓글, 복사 기능과 코드 복사 라벨이 제자리에서 함께 바뀝니다.
- **일관된 요약 카드** — 각 `DS-*` 카드에 분류, 영향도, 파일 근거와 정확한 Markdown 원본이 들어 있습니다.
- **카드별 댓글** — 보고서 내용별 댓글을 브라우저에 저장하며 추가, 수정, 삭제, 전체 삭제와 카드 이동을 지원합니다.
- **Markdown 복사** — 카드 하나, 원본 보고서 전체 또는 카드와 댓글을 묶은 피드백 내용을 복사합니다.
- **오프라인 탐색** — 접거나 크기를 바꿀 수 있는 사이드바, light/dark/system 테마, 반응형 화면과 인쇄 스타일을 단일 HTML에 담았습니다.

근거 수집기는 정해진 인자, 정제된 프로세스 환경, 정확한 범위 검사, 저장소 설정을 통한 추가 코드 실행 차단, 민감한 경로 검사와 명령 출력 제한을 적용합니다. 저장소 diff, 경로, 커밋 메시지, PR 텍스트와 오류는 모두 신뢰하지 않는 데이터로만 다룹니다. 그 안의 지시를 따르거나 그 내용을 바탕으로 셸 명령이나 파일 탐색을 추가로 실행하지 않습니다.

스킬은 대상 저장소의 `.gitignore`에 `.diff-summaries/` 추가를 제안하지만 자동으로 수정하지 않습니다.

## 심각도 수준

| 수준     | 의미                                                |
| -------- | --------------------------------------------------- |
| CRITICAL | 데이터 손실, 보안 침해, 프로덕션 장애 — 반드시 수정 |
| HIGH     | 버그, 취약점, 심각한 설계 결함 — 수정 권장          |
| MEDIUM   | 코드 스멜, 불일치, 중간 리스크 — 개선 권장          |
| LOW      | 스타일, 네이밍, 사소한 개선 — 하면 좋음             |
| INFO     | 의사결정에 영향을 주지만 코드 변경은 필요하지 않은 확인된 맥락 |

## 프로젝트 구조

```
code-review/
├── .claude-plugin/
│   └── plugin.json                       # 플러그인 메타데이터
├── commands/
│   ├── code-review.md                    # /code-review 마크다운 + HTML 커맨드
│   ├── code-review-md.md                 # /code-review-md 커맨드
│   ├── diff-summary.md                    # /diff-summary 커맨드
│   ├── diff-summary-md.md                 # /diff-summary-md 커맨드
│   ├── diff-summary-quiz.md               # /diff-summary-quiz 커맨드
│   └── diff-viewer.md                    # /diff-viewer 커맨드
├── skills/
│   ├── code-review/                      # 메인 스킬 — 전체 워크플로우 + 공유 자산
│   │   ├── SKILL.md                      # 스킬 정의 및 워크플로우
│   │   ├── scripts/
│   │   │   ├── diff_stats.py             # Git diff 통계 추출기
│   │   │   └── generate_html_report.py   # Markdown → HTML 보고서 변환기
│   │   ├── references/
│   │   │   ├── review-criteria.md        # 코드 리뷰 기준
│   │   │   ├── common-vulnerabilities.md # OWASP 기반 보안 체크리스트
│   │   │   ├── python.md                 # Python 권장 방식
│   │   │   └── javascript-typescript.md  # JS/TS 권장 방식
│   │   └── assets/
│   │       └── report-template.html      # HTML 보고서 템플릿
│   ├── code-review-md/
│   │   └── SKILL.md                      # 마크다운 변형 스킬
│   ├── diff-summary/                      # 설명형 마크다운 + HTML 변경 요약
│   │   ├── SKILL.md
│   │   ├── agents/openai.yaml
│   │   ├── scripts/
│   │   │   ├── collect_diff_evidence.py   # 강화된 Git/GitHub -> 제한된 JSON
│   │   │   └── generate_summary_report.py # 검증된 마크다운 -> 오프라인 HTML
│   │   └── assets/summary-template.html
│   ├── diff-summary-md/                  # 독립 설치 가능한 마크다운 전용 패키지
│   │   ├── SKILL.md
│   │   ├── references/diff-summary-workflow.md
│   │   ├── scripts/                      # 동기화된 런타임
│   │   │   ├── collect_diff_evidence.py
│   │   │   └── generate_summary_report.py
│   │   └── assets/summary-template.html
│   ├── diff-summary-quiz/                # 독립 설치 가능한 퀴즈 패키지
│   │   ├── SKILL.md
│   │   ├── references/diff-summary-workflow.md
│   │   ├── scripts/                      # 동기화된 런타임
│   │   │   ├── collect_diff_evidence.py
│   │   │   └── generate_summary_report.py
│   │   └── assets/summary-template.html
│   └── diff-viewer/
│       ├── SKILL.md                      # HTML diff viewer 워크플로우
│       ├── scripts/
│       │   └── generate_diff_report.py   # Git diff -> HTML 변환기
│       └── assets/
│           └── diff-template.html        # Diff viewer 템플릿
└── .snyk                                 # 샘플 fixture용 SAST exclude 정책
```

리뷰어가 찾아내야 할 **의도적으로 취약한 샘플 코드**는 플러그인 폴더 밖인 저장소 루트의 [`samples/code-review/`](../samples/code-review/)에 있습니다. 배포되는 플러그인에는 포함되지 않습니다.

## 요구 사항

- [Claude Code](https://code.claude.com) (CLI, 데스크톱 앱, 또는 IDE 확장)
- Git 저장소
- `diff-summary`, `diff-summary-md`, `diff-summary-quiz` 증거 수집에는 Git 2.45+
- Python 3.10+ (`code-review`, `diff-summary`, `diff-summary-md`, `diff-summary-quiz`, `diff-viewer` 보고서 생성 시 필요, 표준 라이브러리만 사용)

## 보안 노트

Snyk 등 SAST 도구가 이 스킬을 잡는 경우 아래 항목을 참고하세요.

- **테스트 fixture(과거 High-Risk 판정의 주된 원인, 제거됨)**: 이전 버전에서는 의도적으로 취약한 `samples/python-auth/auth_service.py`, `samples/react-dashboard/Dashboard.tsx`, `samples/go-api/handler.go`가 플러그인 폴더 안에 있었습니다(SQL injection, MD5, pickle 역직렬화, 하드코딩된 비밀 정보, `dangerouslySetInnerHTML`, CORS wildcard 등). 이 파일들은 리뷰어가 문제를 찾도록 일부러 망가뜨린 샘플입니다. 이제 저장소 루트의 [`samples/code-review/`](../samples/code-review/)로 옮겨 배포 플러그인에서 제외했으며, `.snyk` 정책 파일도 `samples/**`를 검사에서 제외합니다.
- **`generate_html_report.py` — 코드 블록 언어 속성 XSS(실제 버그, 수정됨)**: 수정 전에는 ` ```a"><script>... ` 같은 악의적인 Markdown 코드 블록이 `class="language-..."` 속성을 빠져나갈 수 있었습니다. `html.escape(..., quote=False)`가 `"`를 이스케이프하지 않기 때문입니다. 새 `safe_lang()` 도우미는 언어 토큰을 `[A-Za-z0-9._+-]{0,32}` 허용 목록으로 제한해 속성을 빠져나가지 못하게 합니다.
- **`html.escape(quote=False)`의 광범위한 사용(오탐)**: `quote=False`의 결과는 모두 HTML 요소 본문에만 넣습니다. 속성에 들어가는 값은 하드코딩된 클래스명이나 `slugify()`로 단어 문자가 아닌 값을 제거한 anchor뿐이므로 오염된 값이 속성에 도달하지 않습니다.
- **원본 Markdown 삽입(정상적으로 방어 중)**: Markdown 원본은 브라우저가 실행하지 않는 `<script type="application/json">` 블록 안에 넣고, `</`를 `<\/`로 바꿔 script 태그가 일찍 닫히지 않게 합니다.
- **`diff-summary` 근거 처리 범위**: `collect_diff_evidence.py`만 Git/GitHub를 실행합니다. 정해진 인자와 정제된 환경을 사용하고, lazy fetch와 저장소 설정을 통한 추가 코드 실행을 막습니다. 안전하지 않은 저장소 정보와 민감한 경로를 거부하고 실행 시간과 stdout/stderr 크기를 제한한 뒤 JSON을 반환합니다. `generate_summary_report.py --bilingual-json-stdin --output-directory`는 심볼릭 링크인 출력 디렉터리를 거부하고 충돌하지 않는 파일명을 직접 정합니다. 한국어와 영어 보고서가 서로 맞는지 확인한 뒤 Markdown 두 개와 이중언어 HTML 하나를 한 번에 기록합니다.
- **CLI 경로 인자(오탐)**: `args.input`으로 읽고 `args.output`으로 쓰는 경로는 사용자가 직접 입력합니다. 권한을 높이거나 외부 입력을 받는 통로는 없습니다.

앞으로 의도적으로 취약한 fixture를 추가한다면 플러그인 폴더가 아니라 저장소 루트의 `samples/` 안에 두세요. `.snyk`도 이 경로를 검사에서 제외합니다.

## 라이선스

MIT
