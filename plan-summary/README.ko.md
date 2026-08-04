# plan-summary

[English](README.md)

사용자가 명시한 plan, PRD, 명세서, 설계문서를 서로 정렬된 한국어·영어 보고서로 요약합니다. 세 selector는 각각 독립 설치할 수 있습니다.

## 워크플로

| Claude Code | Codex | 산출물 |
| --- | --- | --- |
| `/plan-summary [source-path ...]` | `$plan-summary [source-path ...]` | 한국어 Markdown, 영어 Markdown, 이중언어 HTML |
| `/plan-summary-md [source-path ...]` | `$plan-summary-md [source-path ...]` | 한국어·영어 Markdown만 생성 |
| `/plan-summary-quiz [source-path ...]` | `$plan-summary-quiz [source-path ...]` | 한국어·영어 Markdown과 대화형 이중언어 퀴즈 HTML |

“plan 요약”, “PRD 요약”, “설계문서 요약”, “기획서 요약” 같은 자연어로도 활성화됩니다.

## 설치

세 selector를 전역 설치:

```bash
npx skills add chann/skills \
  --skill plan-summary \
  --skill plan-summary-md \
  --skill plan-summary-quiz \
  --agent claude-code codex \
  --global --yes
```

세 selector를 현재 프로젝트에 설치:

```bash
npx skills add chann/skills \
  --skill plan-summary \
  --skill plan-summary-md \
  --skill plan-summary-quiz
```

필요한 selector 하나만 설치할 수도 있습니다:

```bash
npx skills add chann/skills --skill plan-summary
npx skills add chann/skills --skill plan-summary-md
npx skills add chann/skills --skill plan-summary-quiz
```

Markdown·퀴즈 변형은 workflow, collector, generator, HTML template의 동기화된 복사본을 자체 포함합니다. 단독 exact-selector 설치가 형제 스킬 디렉터리에 의존하지 않습니다.

## 입력 경계

하나 이상의 명시적 `.md`, `.markdown`, `.txt` 일반 UTF-8 파일만 전달합니다. 디렉터리·저장소·히스토리를 자동 탐색하거나 glob을 확장하거나 URL을 가져오지 않습니다. 문서 안의 명령처럼 보이는 텍스트도 실행 지시가 아니라 데이터로 취급합니다.

패키지의 `collect_plan_evidence.py`는 표준 입력의 제한된 JSON 요청을 읽고, 순서가 보존된 경로·바이트 크기·SHA-256 digest·정확한 내용을 반환합니다. 누락 파일, 디렉터리, symlink, 중복, 바이너리, 잘못된 UTF-8, 미지원 확장자, 크기 초과는 산출물 없이 거부합니다.

## 보고서 계약

한국어와 영어 보고서는 하나의 근거 지도에서 작성합니다. 소스 순서, digest, `PS-*` 카드 ID, category, 출처 참조가 서로 일치해야 합니다. generator는 번역 간 불일치를 묵인하지 않고 출력을 거부합니다.

`plan-summary-quiz`는 마지막에 정렬된 `QZ-*` 문제를 추가합니다. 각 문제는 2–6개 선택지, 정확히 하나의 정답, 근거가 있는 해설을 가지며 한·영 선택지 수와 정답 위치가 같습니다.

## 산출물

| Selector | 한국어 Markdown | 영어 Markdown | HTML | 브라우저 |
| --- | --- | --- | --- | --- |
| `plan-summary` | 생성 | 생성 | 이중언어 | 열기 시도 |
| `plan-summary-md` | 생성 | 생성 | 생성하지 않음 | 열지 않음 |
| `plan-summary-quiz` | 퀴즈 포함 | 퀴즈 포함 | 이중언어·대화형 | 열기 시도 |

파일은 로컬 날짜와 정렬된 소스 identity에서 만든 충돌 방지 이름으로 `.plan-summaries/` 아래에 원자적으로 생성됩니다. 원본 문서는 수정하거나 덮어쓰지 않습니다.

## 요구사항

- 표준 라이브러리만 사용하는 Python 3.10+
- 고정된 process argv에 JSON 표준 입력을 보낼 수 있는 호스트 에이전트
- HTML selector 두 개를 위한 브라우저/파일 열기 기능
