# code-review

[English](README.md) · [← 메인으로](../README.ko.md)

git diff를 분석하여 **마크다운 및 HTML 리포트 파일**을 생성하는 자동화된 코드 리뷰 스킬입니다.

## 주요 기능

- 5가지 차원으로 코드 변경사항 분석: 정확성, 보안, 복잡도/일관성, 유지보수성, 언어별 베스트 프랙티스
- `.reviews/` 디렉토리에 날짜+커밋SHA 기반 리포트 생성 (예: `2026-04-08_a1b2c3d.md`)
- 심각도 배지, 접을 수 있는 항목, 사이드바 네비게이션이 포함된 스타일링된 HTML 리포트 옵션
- 리뷰 분석 없이 현재 작업 트리 diff를 브라우저용 HTML로 보여주는 `/diff-viewer` 포함
- 다양한 리뷰 범위 지원: 스테이징된 변경, 특정 커밋, 커밋 범위, 브랜치 비교, PR
- Python, JavaScript/TypeScript 베스트 프랙티스 참조 가이드 포함

## 설치 방법

**권장 (전역 + 자동 승인, 한 방):**

```bash
npx skills add -y -g chann/skills@code-review
```

**프로젝트 로컬:**

```bash
npx skills add chann/skills@code-review
```

**수동 설치:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/code-review" ~/.claude/skills/code-review
```

## 사용 방법

설치 후 Claude Code에 코드 리뷰를 요청하면 자동으로 트리거되거나, 명시적 커맨드를 사용할 수 있습니다:

| 커맨드              | 스킬               | 출력                                                       |
| ------------------- | ------------------ | ---------------------------------------------------------- |
| `/code-review`      | `code-review`      | 대화에서 결과 표시 (파일 생성 안 함)                       |
| `/code-review-md`   | `code-review-md`   | `.reviews/<YYYY-MM-DD>_<short-sha>.md` 에 마크다운 리포트  |
| `/code-review-html` | `code-review-html` | 마크다운 + 자체 완결형 HTML 리포트                         |
| `/diff-viewer`      | `diff-viewer`      | `.diffs/<YYYY-MM-DD>_<tag>.html` 에 HTML diff viewer 생성  |

**예시:**

```
> 내 변경사항 리뷰해줘
> 마지막 커밋 리뷰
> /code-review-html 스테이징된 변경사항 리뷰
> /code-review-md feature-auth 브랜치를 main과 비교해서 리뷰
> /diff-viewer
```

**리포트 출력 예시:**

```
.reviews/
├── 2026-04-08_a1b2c3d.md
└── 2026-04-08_a1b2c3d.html
.diffs/
└── 2026-04-08_working.html
```

## 동작 순서

1. 해당 git diff를 수집
2. 언어를 감지하고 적절한 베스트 프랙티스 참조 파일 로드
3. 각 변경된 파일을 5가지 차원으로 분석
4. 대화에서 결과 표시, 또는 리포트 파일 생성 (커맨드에 따라)
5. 핵심 요약 제시

`/diff-viewer`는 별도 동작입니다. `git diff HEAD`를 캡처해 unified/split HTML diff viewer를 만들고 브라우저로 열며, 코드 분석은 하지 않습니다.

## 리포트 구조

각 리포트에는 다음이 포함됩니다:

- **Executive Summary** — 변경된 파일 수, 추가/삭제 라인, 발견 사항 수, 전체 리스크 수준
- **Findings** — 심각도별 그룹핑 (CRITICAL / HIGH / MEDIUM / LOW), 파일 참조, 코드 스니펫, 수정 제안 포함
- **Positive Observations** — 코드에서 잘된 점
- **File-by-File Summary** — 변경된 파일별 상태와 리스크 레벨 요약 테이블

## 심각도 수준

| 수준     | 의미                                                |
| -------- | --------------------------------------------------- |
| CRITICAL | 데이터 손실, 보안 침해, 프로덕션 장애 — 반드시 수정 |
| HIGH     | 버그, 취약점, 심각한 설계 결함 — 수정 권장          |
| MEDIUM   | 코드 스멜, 불일치, 중간 리스크 — 개선 권장          |
| LOW      | 스타일, 네이밍, 사소한 개선 — 하면 좋음             |
| INFO     | 긍정적 관찰 또는 참고 사항                          |

## 프로젝트 구조

```
code-review/
├── .claude-plugin/
│   └── plugin.json                       # 플러그인 메타데이터
├── commands/
│   ├── code-review.md                    # /code-review (대화 전용)
│   ├── code-review-md.md                 # /code-review-md 커맨드
│   ├── code-review-html.md               # /code-review-html 커맨드
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
- Python 3.10+ (HTML 리포트 생성 시 필요)

## 보안 노트

Snyk 등 SAST 도구가 이 스킬을 잡는 경우 아래 항목을 참고하세요.

- **테스트 fixture (High-Risk의 주된 역사적 원인, 제거됨)**: 이전 버전에서는 의도적으로 취약한 `samples/python-auth/auth_service.py`, `samples/react-dashboard/Dashboard.tsx`, `samples/go-api/handler.go` 가 플러그인 폴더 안에 있었습니다 (SQL injection, MD5, pickle deserialization, 하드코딩 시크릿, `dangerouslySetInnerHTML`, CORS wildcard 등). 이 파일들은 리뷰어가 잡아내라고 일부러 broken하게 만든 것이며, 이제 저장소 루트 [`samples/code-review/`](../samples/code-review/) 로 옮겨 배포 artifact에서 제외됐습니다. `.snyk` 정책 파일이 `samples/**` 를 추가로 exclude 합니다.
- **`generate_html_report.py` — fence language attribute XSS (실제 버그, 수정됨)**: 수정 전에는 ` ```a"><script>... ` 같은 악의적인 마크다운 fence가 `class="language-..."` attribute를 빠져나갈 수 있었습니다 (`html.escape(..., quote=False)`는 `"`를 escape 하지 않음). 새로 추가된 `safe_lang()` 헬퍼가 lang 토큰을 `[A-Za-z0-9._+-]{0,32}` 화이트리스트로 제한해 attribute 탈출을 차단합니다.
- **`html.escape(quote=False)` 광범위 사용 (false positive)**: `quote=False` 결과는 모두 element body context에만 삽입됩니다. attribute에 들어가는 값은 하드코딩된 클래스명이거나 `slugify()`로 비단어 문자를 제거한 anchor뿐 — 오염된 값이 attribute에 도달하지 않습니다.
- **raw markdown 임베드 (정상 방어 중)**: 마크다운 원본은 브라우저가 실행하지 않는 `<script type="application/json">` 블록 안에 들어가고, `</` 시퀀스를 `<\/`로 변환해 script 태그 조기 종료를 막습니다.
- **CLI path 인자 (false positive)**: `args.input` 읽기와 `args.output` 쓰기는 사용자가 직접 입력한 경로이며, 권한 상승이나 외부 입력 통로가 없습니다.

앞으로 의도적으로 취약한 fixture를 추가할 일이 있다면 플러그인 폴더가 아닌 저장소 루트의 `samples/` 트리 안에 두세요. `.snyk` 가 그쪽을 exclude 합니다.

## 라이선스

MIT
