# handoff

[English](README.md) · [← 메인으로](../README.ko.md)

대상을 인자로 고르는 핸드오프 스킬 하나입니다. 클라이언트 개발자, 서버 개발자, 이 세션을 이어받을 사람이나 에이전트에게 작업을 넘깁니다.

## 주요 기능

- `git diff`, 커밋 범위, 브랜치 비교와 현재 세션 맥락을 근거가 담긴 Markdown 핸드오프로 정리
- `frontend`: 프론트엔드, 모바일, SDK 등 클라이언트에 필요한 백엔드 API 변경 사항 전달. 클라이언트에 보이는 변경이 없으면 `client action 없음`으로 적음
- `backend`: API 계약, DB 마이그레이션, 백그라운드 작업과 큐, 배포, 검증을 중심으로 백엔드 작업 인계
- `session`: 지금 세션을 새 에이전트에게 넘김. 확인된 것과 아닌 것을 나누고, 그대로 붙여 쓸 수 있는 재시작 프롬프트로 끝냄
- 대상은 인자, 요청 문구, diff 순서로 정하고 무엇을 왜 골랐는지 첫 줄에 밝힘
- `.handoffs/` 아래에 결과 파일 생성
- `main...feature` 같은 사용자가 지정한 범위를 그대로 보존
- 검증하지 않은 테스트, 배포, 런타임 동작은 사실처럼 쓰지 않고 미검증으로 표시
- 인용한 명령과 로그에서 비밀 값을 지우고, 커밋이나 푸시는 하지 않음
- 한국어 핸드오프는 자연스럽고 구체적으로 쓰며, `unslop`이 이미 있으면 마지막에 한 번 더 다듬음

## 설치 방법

**권장 (전역):**

```bash
npx skills add -y -g chann/skills --skill handoff
```

**현재 프로젝트에 설치:**

```bash
npx skills add chann/skills --skill handoff
```

한 줄 selector 형식: `npx skills add chann/skills --skill handoff`

이 스킬은 단독으로 작동합니다. `unslop`을 설치하거나 요구하지 않으며, 사용할 수 없는 환경에서는 스킬에 포함된 문체 규칙만으로 문서를 완성합니다.

## 사용 방법

| Claude Code | Codex | 출력 |
|---|---|---|
| `/handoff frontend [범위]` | `$handoff frontend [범위]` | `.handoffs/<date>_<scope>_frontend.md`에 프론트엔드/클라이언트 핸드오프 생성 |
| `/handoff backend [범위]` | `$handoff backend [범위]` | `.handoffs/<date>_<scope>_backend.md`에 백엔드/서버 핸드오프 생성 |
| `/handoff session [메모]` | `$handoff session [메모]` | `.handoffs/<date>_<slug>_session.md`에 세션 인수인계 문서 생성 |
| `/handoff [범위]` | `$handoff [범위]` | 요청 문구나 diff로 대상을 정함. diff에 둘 다 필요하면 문서를 둘 다 작성 |

예시:

```
> /handoff frontend main...feature-user-api
> /handoff backend HEAD~5..HEAD
> /handoff session
> 현재 백엔드 API diff로 FE 핸드오프 문서 작성
> 내일 다른 에이전트가 이어서 할 수 있게 인수인계 문서 써줘
```

### 기존 스킬 세 개에서 옮겨 가기

| 이전 | 이후 |
|---|---|
| `/gen-frontend-handoff [범위]` | `/handoff frontend [범위]` |
| `/gen-backend-handoff [범위]` | `/handoff backend [범위]` |
| `/gen-session-handoff [메모]` | `/handoff session [메모]` |
| `$gen-frontend-handoff`, `$gen-backend-handoff`, `$gen-session-handoff` | `$handoff frontend`, `$handoff backend`, `$handoff session` |

출력 경로와 파일 이름은 그대로입니다.

## 범위 규칙

- 지정한 범위 없음: 스테이징되지 않은 변경과 스테이징된 변경을 확인합니다.
- 정확한 범위: 사용자가 지정한 범위를 먼저 사용합니다.
- 브랜치 비교: `main...feature` 같은 비교 표현을 그대로 사용합니다.
- 세션 맥락: 대화에서 제공되었거나 파일과 명령으로 확인한 내용만 사용합니다.
- `session`은 세션 자체를 넘기므로 범위가 diff가 아니라 대화와 저장소 상태입니다. 동작한다는 주장에는 그것을 확인한 명령을 함께 적고, 나머지는 미검증으로 남깁니다.

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼
- Git 저장소

## 라이선스

MIT
