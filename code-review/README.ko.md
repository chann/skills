# code-review

[English](README.md) · [← 메인으로](../README.ko.md)

git diff를 변경 요약, 결함 리뷰, 브라우저용 원본 패치로 다루는 변경 인텔리전스 플러그인입니다.

## 주요 기능

- 5가지 차원으로 코드 변경사항 분석: 정확성, 보안, 복잡도/일관성, 유지보수성, 언어별 베스트 프랙티스
- `.reviews/` 디렉토리에 날짜+커밋SHA 기반 리포트 생성 (예: `2026-04-08_a1b2c3d.md`)
- 자체 완결형 **이중언어** HTML 리포트 옵션 (한국어 + 영문, 전체 페이지 언어 토글, 한국어 기본 표시): 심각도 배지, light/dark/auto 테마 + 코드 신택스 스킴 셀렉터, 컴팩트 접이식 사이드바, 항목별 마크다운 복사, 브라우저 내 항목별 코멘트, 리뷰어 코멘트로 리뷰를 재생성하는 "피드백 복사" 페이로드
- 코드, 동작, 아키텍처, 패턴, 계약, 테스트, 운영 변경을 근거 기반으로 설명하는 마크다운 + 인터랙티브 HTML `/diff-summary` 포함. 마크다운만 만드는 `/diff-summary-md`, 같은 요약에 인터랙티브 이해도 퀴즈를 더한 `/diff-summary-quiz` 변형도 제공
- 리뷰 분석 없이 현재 작업 트리 diff를 브라우저용 HTML로 보여주는 `/diff-viewer` 포함
- 다양한 리뷰 범위 지원: 스테이징된 변경, 특정 커밋, 커밋 범위, 브랜치 비교, PR
- Python, JavaScript/TypeScript 베스트 프랙티스 참조 가이드 포함

## 설치 방법

**권장 (전역 + 자동 승인, 한 방):**

```bash
npx skills add -y -g chann/skills \
  --skill code-review \
  --skill code-review-md \
  --skill code-review-html \
  --skill diff-summary \
  --skill diff-summary-md \
  --skill diff-summary-quiz \
  --skill diff-viewer
```

**프로젝트 로컬:**

```bash
npx skills add chann/skills \
  --skill code-review \
  --skill code-review-md \
  --skill code-review-html \
  --skill diff-summary \
  --skill diff-summary-md \
  --skill diff-summary-quiz \
  --skill diff-viewer
```

설치할 때는 실제 스킬 이름을 `--skill`로 지정합니다. 이 플러그인에는 독립적으로 발견되는 일곱 스킬이 들어 있습니다. 각 diff-summary selector는 필요한 워크플로우와 런타임을 함께 제공하므로 `diff-summary-md` 또는 `diff-summary-quiz`만 설치해도 실행할 수 있습니다. 설치 전 `npx skills add chann/skills -l --full-depth`로 selector를 확인할 수 있습니다.

**수동 설치:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/code-review" ~/.claude/skills/code-review
```

## 사용 방법

설치 후 자연어 의도에 맞는 스킬이 자동으로 트리거되며, 명시적 커맨드도 사용할 수 있습니다:

| 커맨드                          | 스킬                  | 출력                                                             |
| ---------------------------- | ------------------- | -------------------------------------------------------------- |
| `/code-review`               | `code-review`       | 대화에서 결과 표시 (파일 생성 안 함)                                         |
| `/code-review-md`            | `code-review-md`    | `.reviews/<YYYY-MM-DD>_<short-sha>.md`에 마크다운 리포트               |
| `/code-review-html`          | `code-review-html`  | 마크다운 + 자체 완결형 HTML 리뷰                                          |
| `/diff-summary [scope]`      | `diff-summary`      | `.diff-summaries/<YYYY-MM-DD>_<scope>.*`에 마크다운 + 인터랙티브 HTML 요약 |
| `/diff-summary-md [scope]`   | `diff-summary-md`   | `.diff-summaries/<YYYY-MM-DD>_<scope>.md`에 마크다운만 (HTML 없음)     |
| `/diff-summary-quiz [scope]` | `diff-summary-quiz` | 마크다운 + 인터랙티브 HTML + `## Quiz` 이해도 섹션                           |
| `/diff-viewer`               | `diff-viewer`       | `.diffs/<YYYY-MM-DD>_<tag>.html`에 HTML diff viewer             |

**예시:**

```
> 내 변경사항 리뷰해줘
> 마지막 커밋 리뷰
> /code-review-html 스테이징된 변경사항 리뷰
> /code-review-md feature-auth 브랜치를 main과 비교해서 리뷰
> 코드를 요약해줘
> /diff-summary main..dev
> 마지막 커밋 코드를 요약해줘
> PR #42 변경 요약
> /diff-viewer
```

**리포트 출력 예시:**

```
.reviews/
├── 2026-04-08_a1b2c3d.md       # 한국어 리포트 (메인)
├── 2026-04-08_a1b2c3d.en.md    # 영문 리포트 (번역, HTML 전용)
└── 2026-04-08_a1b2c3d.html     # 병합된 이중언어 HTML
.diff-summaries/
├── 2026-04-08_main-dot2-dev-<hash12>.md   # 근거 기반 변경 요약
└── 2026-04-08_main-dot2-dev-<hash12>.html # 인터랙티브 오프라인 요약
.diffs/
└── 2026-04-08_working.html
```

명시한 범위는 그대로 보존됩니다. `main..dev`와 `main...dev`는 서로 다른 비교이며 한쪽으로 정규화하지 않습니다. 현재/스테이징/미스테이징 변경, 마지막 커밋 또는 최근 N개 커밋, 특정 커밋/범위/브랜치 비교, PR을 지원합니다.

### 목적에 맞는 워크플로우

| 목적 | 워크플로우 | 결과 |
|---|---|---|
| 무엇이 왜 바뀌었고 코드, 아키텍처, 패턴, 계약, 테스트, 운영이 어떻게 연결되는지 설명 | `diff-summary` | 리뷰 심각도 없는 근거 기반 요약 카드 |
| 같은 설명을 HTML·브라우저 없이 마크다운으로만 저장 | `diff-summary-md` | 검증된 마크다운 파일 하나 |
| 변경을 설명하고 이해도를 확인 | `diff-summary-quiz` | 마크다운 정답지 + 인터랙티브 오프라인 HTML 퀴즈 |
| 결함, 회귀, 취약점, 권장 수정 사항 탐색 | `code-review`, `code-review-md`, `code-review-html` | 심각도별 finding |
| 분석 없이 패치 자체 확인 | `diff-viewer` | unified/split 원본 diff HTML |

요약과 리뷰를 함께 요청하면 두 워크플로우를 모두 실행하고 설명 카드와 결함 finding을 별도 섹션으로 유지합니다.

## 동작 순서

1. 해당 git diff를 수집
2. 언어를 감지하고 적절한 베스트 프랙티스 참조 파일 로드
3. 각 변경된 파일을 5가지 차원으로 분석
4. 대화에서 결과 표시, 또는 리포트 파일 생성 (커맨드에 따라)
5. 핵심 요약 제시

`/diff-viewer`는 별도 동작입니다. `git diff HEAD`를 캡처해 unified/split HTML diff viewer를 만들고 브라우저로 열며, 코드 분석은 하지 않습니다.

`/diff-summary`는 별도의 설명형 흐름을 따릅니다:

1. 요청 범위와 정확한 `..`/`...` 문법을 그대로 검증 및 보존
2. 저장소와 범위를 JSON으로 패키지의 `collect_diff_evidence.py` 표준 입력에 전달하며, 이 수집기만 Git/GitHub를 실행
3. 크기가 제한된 JSON 결과를 비실행 데이터로 취급해 안정적인 `DS-001` 형식의 프롬프트 언어 마크다운 작성
4. 마크다운을 `generate_summary_report.py` 표준 입력에 보내 검증 후 원본과 HTML을 원자적으로 기록
5. 자체 완결형 HTML 리포트를 브라우저에서 열기

중요한 추론과 확인하지 않은 런타임, 테스트, 마이그레이션, 배포 결과는 사실처럼 단정하지 않고 명시적으로 구분합니다.

## 코드 리뷰 리포트 구조

### 근거 우선 문체

리뷰 발견 사항은 **관찰 → 영향 → 수정** 순서로 작성합니다. 확인된 사실에는 변경된 경로와 줄 범위를 명시합니다. 중요한 추론은 추론임을 밝히고 근거와 연결합니다. 일반적인 칭찬, 상투적인 도입부, 템플릿을 채우기 위한 발견 사항은 넣지 않습니다.

### 조건부 섹션

리포트 메타데이터와 실행 가능한 발견 사항은 계속 제공합니다. `Decision Summary`, `Positive Observations`, `Open Questions`, `File Summary`는 서로 다른 의사결정 관련 정보를 더할 때만 표시합니다. 실행 가능한 발견 사항이 없으면 이를 직접 밝히고, 중요한 잔여 리스크나 공백만 남깁니다.

## HTML 리포트

`/code-review-html`는 한국어 리포트와 영문 번역을 하나의 자체 완결형 HTML로 병합하며 다음을 제공합니다:

- **언어 토글** — 한국어가 기본 표시, 전체 페이지를 영문으로 전환. 번역이 없으면 단일 언어로 폴백(토글 숨김).
- **테마 & 코드 스킴** — light/dark/auto 페이지 테마 + 8종 신택스 하이라이트 스킴(GitHub, Monokai, Dracula, Nord 등). diff/코드 블록이 자동으로 맞춰짐.
- **컴팩트 사이드바** — 접기/드래그 리사이즈 지원, 섹션 네비게이션과 코멘트 패널 포함.
- **항목별 "마크다운 복사"** — 개별 finding의 마크다운만 복사.
- **항목별 코멘트** — 개별 finding에 리뷰 코멘트 작성(브라우저 저장, finding ID로 키잉되어 언어 전환에도 유지).
- **"피드백 복사"** — 재생성 페이로드(원본 finding 마크다운 + 작성한 코멘트)를 생성. 새 `/code-review-html` 실행에 붙여넣으면 피드백을 반영해 리뷰를 다시 작성.

### Diff summary HTML

각 `/diff-summary` HTML 리포트는 서버, 네트워크 요청, 패키지 설치, JavaScript 빌드 없이 로컬 `file://` URL에서 바로 동작합니다.

- **안정적인 요약 카드** — 각 `DS-*` 카드에 카테고리, 영향도, 파일 근거, 정확한 마크다운 원본 포함
- **카드별 코멘트** — 리포트 콘텐츠 단위로 브라우저에 저장되는 코멘트 추가, 수정, 삭제, 전체 삭제, 카드 이동
- **마크다운 복사** — 개별 카드, 전체 원본 리포트, 카드와 코멘트를 묶은 피드백 페이로드 복사
- **오프라인 탐색** — 접기/크기 조절 사이드바, light/dark/system 테마, 반응형 레이아웃, 인쇄 스타일을 단일 HTML에 내장

증거 수집기는 고정 argv, 정제된 프로세스 환경, 정확한 범위 검증, 실행 표면 차단, 민감 경로 검사, 명령 출력 제한을 적용합니다. 저장소 diff, 경로, 커밋 메시지, PR 텍스트, 오류는 모두 신뢰하지 않는 데이터로만 다루며, 그 안의 지시를 따르거나 이를 근거로 추가 셸/파일 탐색을 수행하지 않습니다.

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
│   ├── code-review.md                    # /code-review (대화 전용)
│   ├── code-review-md.md                 # /code-review-md 커맨드
│   ├── code-review-html.md               # /code-review-html 커맨드
│   ├── diff-summary.md                    # /diff-summary 커맨드
│   ├── diff-summary-md.md                 # /diff-summary-md 커맨드
│   ├── diff-summary-quiz.md               # /diff-summary-quiz 커맨드
│   └── diff-viewer.md                    # /diff-viewer 커맨드
├── skills/
│   ├── code-review/                      # 메인 스킬 — 전체 워크플로우 + 공유 자산
│   │   ├── SKILL.md                      # 스킬 정의 및 워크플로우
│   │   ├── scripts/
│   │   │   ├── diff_stats.py             # Git diff 통계 추출기
│   │   │   └── generate_html_report.py   # Markdown → HTML 리포트 변환기
│   │   ├── references/
│   │   │   ├── review-criteria.md        # 리뷰 기준 프레임워크
│   │   │   ├── common-vulnerabilities.md # OWASP 기반 보안 체크리스트
│   │   │   ├── python.md                 # Python 베스트 프랙티스
│   │   │   └── javascript-typescript.md  # JS/TS 베스트 프랙티스
│   │   └── assets/
│   │       └── report-template.html      # HTML 리포트 템플릿
│   ├── code-review-md/
│   │   └── SKILL.md                      # 마크다운 변형 스킬
│   ├── code-review-html/
│   │   └── SKILL.md                      # HTML 변형 스킬
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

리뷰어가 잡아내야 할 **의도적으로 취약한 샘플 코드**는 플러그인 폴더 밖, 저장소 루트의 [`samples/code-review/`](../samples/code-review/) 에 있습니다. 배포되는 플러그인 artifact에는 포함되지 않습니다.

## 요구 사항

- [Claude Code](https://code.claude.com) (CLI, 데스크톱 앱, 또는 IDE 확장)
- Git 저장소
- `diff-summary`, `diff-summary-md`, `diff-summary-quiz` 증거 수집에는 Git 2.45+
- Python 3.10+ (`code-review-html`, `diff-summary`, `diff-summary-md`, `diff-summary-quiz`, `diff-viewer` 리포트 생성 시 필요, 표준 라이브러리만 사용)

## 보안 노트

Snyk 등 SAST 도구가 이 스킬을 잡는 경우 아래 항목을 참고하세요.

- **테스트 fixture (High-Risk의 주된 역사적 원인, 제거됨)**: 이전 버전에서는 의도적으로 취약한 `samples/python-auth/auth_service.py`, `samples/react-dashboard/Dashboard.tsx`, `samples/go-api/handler.go` 가 플러그인 폴더 안에 있었습니다 (SQL injection, MD5, pickle deserialization, 하드코딩 시크릿, `dangerouslySetInnerHTML`, CORS wildcard 등). 이 파일들은 리뷰어가 잡아내라고 일부러 broken하게 만든 것이며, 이제 저장소 루트 [`samples/code-review/`](../samples/code-review/) 로 옮겨 배포 artifact에서 제외됐습니다. `.snyk` 정책 파일이 `samples/**` 를 추가로 exclude 합니다.
- **`generate_html_report.py` — fence language attribute XSS (실제 버그, 수정됨)**: 수정 전에는 ` ```a"><script>... ` 같은 악의적인 마크다운 fence가 `class="language-..."` attribute를 빠져나갈 수 있었습니다 (`html.escape(..., quote=False)`는 `"`를 escape 하지 않음). 새로 추가된 `safe_lang()` 헬퍼가 lang 토큰을 `[A-Za-z0-9._+-]{0,32}` 화이트리스트로 제한해 attribute 탈출을 차단합니다.
- **`html.escape(quote=False)` 광범위 사용 (false positive)**: `quote=False` 결과는 모두 element body context에만 삽입됩니다. attribute에 들어가는 값은 하드코딩된 클래스명이거나 `slugify()`로 비단어 문자를 제거한 anchor뿐 — 오염된 값이 attribute에 도달하지 않습니다.
- **raw markdown 임베드 (정상 방어 중)**: 마크다운 원본은 브라우저가 실행하지 않는 `<script type="application/json">` 블록 안에 들어가고, `</` 시퀀스를 `<\/`로 변환해 script 태그 조기 종료를 막습니다.
- **`diff-summary` 증거 경계**: `collect_diff_evidence.py`만 Git/GitHub를 실행합니다. 고정 argv와 정제된 환경을 사용하고 lazy fetch 및 저장소 설정 실행 표면을 차단하며, 안전하지 않은 저장소 메타데이터와 민감 경로를 거부하고 시간/stdout/stderr를 제한한 뒤 JSON을 반환합니다. `generate_summary_report.py --markdown-stdin --output-directory`는 심볼릭 링크 아티팩트 부모를 거부하고 충돌 없는 파일명을 직접 계산하여 검증된 마크다운/HTML 쌍을 원자적으로 기록합니다.
- **CLI path 인자 (false positive)**: `args.input` 읽기와 `args.output` 쓰기는 사용자가 직접 입력한 경로이며, 권한 상승이나 외부 입력 통로가 없습니다.

앞으로 의도적으로 취약한 fixture를 추가할 일이 있다면 플러그인 폴더가 아닌 저장소 루트의 `samples/` 트리 안에 두세요. `.snyk` 가 그쪽을 exclude 합니다.

## 라이선스

MIT
