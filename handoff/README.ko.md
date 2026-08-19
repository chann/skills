# handoff

[English](README.md) · [← 메인으로](../README.ko.md)

백엔드, 프론트엔드/클라이언트, 코딩 에이전트 세션 사이에 작업을 넘기기 위한 핸드오프 문서 생성 스킬입니다.

## 주요 기능

- `git diff`, 커밋 범위, 브랜치 비교와 현재 세션 맥락을 근거가 담긴 Markdown 핸드오프로 정리
- `/gen-frontend-handoff`: 프론트엔드, 모바일, SDK 등 클라이언트에 필요한 백엔드 API 변경 사항 전달
- `/gen-backend-handoff`: API 계약, DB 마이그레이션, 백그라운드 작업과 큐, 배포, 검증을 중심으로 백엔드 작업 인계
- `/gen-session-handoff`: 지금 세션을 새 에이전트에게 넘김. 확인된 것과 아닌 것을 나누고, 그대로 붙여 쓸 수 있는 재시작 프롬프트로 끝냄
- `.handoffs/` 아래에 결과 파일 생성
- `main...feature` 같은 사용자가 지정한 범위를 그대로 보존
- 검증하지 않은 테스트, 배포, 런타임 동작은 사실처럼 쓰지 않고 미검증으로 표시
- 한국어 핸드오프는 자연스럽고 구체적으로 쓰며, `human-friendly-writing`이 이미 있으면 마지막에 한 번 더 다듬음

## 설치 방법

**권장 (전역):**

```bash
npx skills add -y -g chann/skills \
  --skill gen-frontend-handoff \
  --skill gen-backend-handoff \
  --skill gen-session-handoff
```

**현재 프로젝트에 설치:**

```bash
npx skills add chann/skills \
  --skill gen-frontend-handoff \
  --skill gen-backend-handoff \
  --skill gen-session-handoff
```

설치할 때는 실제 스킬 이름을 `--skill`로 지정합니다. 이 플러그인은 두 핸드오프 생성기를 함께 패키징합니다.

한 줄 selector 형식: `npx skills add chann/skills --skill gen-frontend-handoff --skill gen-backend-handoff`
백엔드 단독 selector 형식: `npx skills add chann/skills --skill gen-backend-handoff`

각 스킬은 단독으로 작동합니다. `human-friendly-writing`을 설치하거나 요구하지
않으며, 사용할 수 없는 환경에서는 각 스킬에 포함된 문체 규칙만으로 문서를
완성합니다.

## 사용 방법

| Claude Code | Codex | 출력 |
|---|---|---|
| `/gen-frontend-handoff` | `$gen-frontend-handoff` | `.handoffs/<date>_<scope>_frontend.md`에 프론트엔드/클라이언트 핸드오프 생성 |
| `/gen-backend-handoff` | `$gen-backend-handoff` | `.handoffs/<date>_<scope>_backend.md`에 백엔드/서버 핸드오프 생성 |
| `/gen-session-handoff` | `$gen-session-handoff` | `.handoffs/<date>_<slug>_session.md`에 세션 인수인계 문서 생성 |

예시:

```
> /gen-frontend-handoff main...feature-user-api
> /gen-backend-handoff HEAD~5..HEAD
> 현재 백엔드 API diff로 FE 핸드오프 문서 작성
> 현재 Codex 세션 맥락과 Git diff로 백엔드 핸드오프 문서 작성
> /gen-session-handoff
> 내일 다른 에이전트가 이어서 할 수 있게 인수인계 문서 써줘
```

## 범위 규칙

- 지정한 범위 없음: 스테이징되지 않은 변경과 스테이징된 변경을 확인합니다.
- 정확한 범위: 사용자가 지정한 범위를 먼저 사용합니다.
- 브랜치 비교: `main...feature` 같은 비교 표현을 그대로 사용합니다.
- 세션 맥락: 대화에서 제공되었거나 파일과 명령으로 확인한 내용만 사용합니다.
- `gen-session-handoff`는 세션 자체를 넘기므로 범위가 diff가 아니라 대화와 저장소 상태입니다. 동작한다는 주장에는 그것을 확인한 명령을 함께 적고, 나머지는 미검증으로 남깁니다.

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼
- Git 저장소

## 라이선스

MIT
