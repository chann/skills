# code-review

[English](README.md) · [← 메인으로](../README.ko.md)

git diff를 분석하여 **마크다운 및 HTML 리포트 파일**을 생성하는 자동화된 코드 리뷰 스킬입니다.

## 주요 기능

- 5가지 차원으로 코드 변경사항 분석: 정확성, 보안, 복잡도/일관성, 유지보수성, 언어별 베스트 프랙티스
- `.reviews/` 디렉토리에 날짜+커밋SHA 기반 리포트 생성 (예: `2026-04-08_a1b2c3d.md`)
- 심각도 배지, 접을 수 있는 항목, 사이드바 네비게이션이 포함된 스타일링된 HTML 리포트 옵션
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

**예시:**

```
> 내 변경사항 리뷰해줘
> 마지막 커밋 리뷰
> /code-review-html 스테이징된 변경사항 리뷰
> /code-review-md feature-auth 브랜치를 main과 비교해서 리뷰
```

**리포트 출력 예시:**

```
.reviews/
├── 2026-04-08_a1b2c3d.md
└── 2026-04-08_a1b2c3d.html
```

## 동작 순서

1. 해당 git diff를 수집
2. 언어를 감지하고 적절한 베스트 프랙티스 참조 파일 로드
3. 각 변경된 파일을 5가지 차원으로 분석
4. 대화에서 결과 표시, 또는 리포트 파일 생성 (커맨드에 따라)
5. 핵심 요약 제시

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
│   └── code-review-html.md               # /code-review-html 커맨드
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
│   └── code-review-html/
│       └── SKILL.md                      # HTML 변형 스킬
└── samples/                              # 테스트 샘플 파일
```

## 요구 사항

- [Claude Code](https://code.claude.com) (CLI, 데스크톱 앱, 또는 IDE 확장)
- Git 저장소
- Python 3.10+ (HTML 리포트 생성 시 필요)

## 라이선스

MIT
