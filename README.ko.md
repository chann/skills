# skills

[English](README.md)

소프트웨어 엔지니어링 워크플로우를 위한 실용적인 에이전트 스킬 모음입니다.

## 스킬 목록

### code-review

git diff를 분석하여 **마크다운 및 HTML 리포트 파일**을 생성하는 자동화된 코드 리뷰 스킬입니다.

**주요 기능:**

- 5가지 차원으로 코드 변경사항 분석: 정확성, 보안, 복잡도/일관성, 유지보수성, 언어별 베스트 프랙티스
- `.reviews/` 디렉토리에 날짜+커밋SHA 기반 리포트 생성 (예: `2026-04-08_a1b2c3d.md`)
- 심각도 배지, 접을 수 있는 항목, 사이드바 네비게이션이 포함된 스타일링된 HTML 리포트 옵션
- 다양한 리뷰 범위 지원: 스테이징된 변경, 특정 커밋, 커밋 범위, 브랜치 비교, PR
- Python, JavaScript/TypeScript 베스트 프랙티스 참조 가이드 포함

**리포트 출력 예시:**

```
.reviews/
├── 2026-04-08_a1b2c3d.md
└── 2026-04-08_a1b2c3d.html
```

## 설치 방법

### [skills.sh](https://skills.sh) 사용 (권장)

```bash
npx skills add chann/skills
```

전역 설치 (모든 프로젝트에서 사용 가능):

```bash
npx skills add -g chann/skills
```

### 수동 설치

저장소를 클론하고 Claude Code 스킬 디렉토리에 심볼릭 링크를 생성합니다:

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/code-review" ~/.claude/skills/code-review
```

## 사용 방법

설치 후 Claude Code에 코드 리뷰를 요청하면 자동으로 트리거됩니다:

```
> 내 변경사항 리뷰해줘
> 마지막 커밋 리뷰
> 스테이징된 변경사항 리뷰
> 최근 3개 커밋 코드 리뷰
> feature-auth 브랜치를 main과 비교해서 리뷰
> PR #42 리뷰
> 코드 리뷰하고 HTML 리포트 생성해줘
```

스킬은 다음 순서로 동작합니다:

1. 해당 git diff를 수집
2. 언어를 감지하고 적절한 베스트 프랙티스 참조 파일 로드
3. 각 변경된 파일을 분석하여 이슈 탐지
4. `.reviews/`에 구조화된 마크다운 리포트 작성
5. 요청 시 HTML 리포트 생성
6. 대화에서 핵심 요약 제시

### 리포트 구조

각 리포트에는 다음이 포함됩니다:

- **Executive Summary** — 변경된 파일 수, 추가/삭제 라인, 발견 사항 수, 전체 리스크 수준
- **Findings** — 심각도별 그룹핑 (CRITICAL / HIGH / MEDIUM / LOW), 파일 참조, 코드 스니펫, 수정 제안 포함
- **Positive Observations** — 코드에서 잘된 점
- **File-by-File Summary** — 변경된 파일별 상태와 리스크 레벨 요약 테이블

### 심각도 수준

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
├── SKILL.md                          # 스킬 정의 및 워크플로우
├── scripts/
│   ├── diff_stats.py                 # Git diff 통계 추출기
│   └── generate_html_report.py       # Markdown → HTML 리포트 변환기
├── references/
│   ├── review-criteria.md            # 리뷰 기준 프레임워크
│   ├── common-vulnerabilities.md     # OWASP 기반 보안 체크리스트
│   ├── python.md                     # Python 베스트 프랙티스
│   └── javascript-typescript.md      # JS/TS 베스트 프랙티스
└── assets/
    └── report-template.html          # HTML 리포트 템플릿
```

## 요구 사항

- [Claude Code](https://code.claude.com) (CLI, 데스크톱 앱, 또는 IDE 확장)
- Git 저장소
- Python 3.10+ (HTML 리포트 생성 시 필요)

## 라이선스

MIT
