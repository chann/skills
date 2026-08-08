# plan-summary

[English](README.md)

사용자가 지정한 계획, PRD, 명세서와 설계 문서를 내용과 근거가 서로 맞는 한국어·영어 보고서로 요약합니다. 세 selector는 각각 독립적으로 설치할 수 있습니다.

## 워크플로

| Claude Code | Codex | 산출물 |
| --- | --- | --- |
| `/plan-summary [source-path ...]` | `$plan-summary [source-path ...]` | 한국어 Markdown, 영어 Markdown, 이중언어 HTML |
| `/plan-summary-md [source-path ...]` | `$plan-summary-md [source-path ...]` | 한국어·영어 Markdown만 생성 |
| `/plan-summary-quiz [source-path ...]` | `$plan-summary-quiz [source-path ...]` | 한국어·영어 Markdown과 대화형 이중언어 퀴즈 HTML |

“plan 요약”, “PRD 요약”, “설계문서 요약”, “기획서 요약” 같은 자연어로도 활성화됩니다.

## 설치

세 selector를 전역으로 설치:

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

Markdown 전용판과 퀴즈판에는 워크플로, 수집기, 생성기와 HTML 템플릿의 동일한 복사본이 들어 있습니다. selector 하나만 설치해도 다른 스킬 디렉터리 없이 실행됩니다.

## 입력 경계

하나 이상의 `.md`, `.markdown`, `.txt` 일반 UTF-8 파일을 직접 지정해야 합니다. 디렉터리, 저장소, 히스토리를 자동으로 찾거나 glob을 확장하거나 URL을 가져오지 않습니다. 문서 안에서 명령처럼 보이는 텍스트도 실행 지시가 아닌 데이터로 취급합니다.

패키지의 `collect_plan_evidence.py`는 크기가 제한된 JSON 요청을 표준 입력으로 읽고, 지정한 순서의 경로, 바이트 크기, SHA-256 해시값과 정확한 내용을 반환합니다. 누락된 파일, 디렉터리, symlink, 중복, 바이너리, 잘못된 UTF-8, 지원하지 않는 확장자와 크기 초과 입력은 결과물을 만들지 않고 거부합니다.

## 보고서 작성 규칙

한국어와 영어 보고서는 같은 근거를 사용합니다. 소스 순서, 해시값, `PS-*` 카드 ID, 분류와 출처가 서로 일치해야 합니다. 생성기는 두 언어의 내용이 어긋나면 그대로 넘어가지 않고 출력을 거부합니다.

`plan-summary-quiz`는 마지막에 한국어와 영어가 서로 대응하는 `QZ-*` 문제를 추가합니다. 각 문제에는 선택지 2–6개, 정확히 하나의 정답과 근거가 있는 해설이 있으며, 두 언어의 선택지 수와 정답 위치가 같습니다.

## 산출물

| Selector | 한국어 Markdown | 영어 Markdown | HTML | 브라우저 |
| --- | --- | --- | --- | --- |
| `plan-summary` | 생성 | 생성 | 이중언어 | 열기 시도 |
| `plan-summary-md` | 생성 | 생성 | 생성하지 않음 | 열지 않음 |
| `plan-summary-quiz` | 퀴즈 포함 | 퀴즈 포함 | 이중언어·대화형 | 열기 시도 |

파일은 로컬 날짜와 순서대로 지정한 소스를 기준으로 충돌하지 않는 이름을 정해 `.plan-summaries/` 아래에 한 번에 생성합니다. 원본 문서는 수정하거나 덮어쓰지 않습니다.

## 요구사항

- 표준 라이브러리만 사용하는 Python 3.10+
- 고정된 프로세스 인자에 JSON을 표준 입력으로 보낼 수 있는 호스트 에이전트
- HTML selector 두 개를 위한 브라우저/파일 열기 기능
