# handoff

[English](README.md) · [← 메인으로](../README.ko.md)

백엔드, 프론트엔드/클라이언트, 코딩 에이전트 세션 사이에 작업을 넘기기 위한 핸드오프 문서 생성 스킬입니다.

## 주요 기능

- git diff, 커밋 범위, 브랜치 비교, 현재 세션 컨텍스트를 근거 기반 마크다운 핸드오프로 정리
- `/gen-frontend-handoff`: 프론트엔드, 모바일, SDK 등 클라이언트가 소비해야 하는 백엔드 API 변경사항 전달
- `/gen-backend-handoff`: API 계약, database migrations, jobs/queues, rollout, verification 중심의 백엔드 작업 인계
- `.handoffs/` 아래에 결과 파일 생성
- `main...feature` 같은 사용자 지정 scope를 그대로 보존
- 검증하지 않은 테스트, 배포, 런타임 동작은 사실처럼 쓰지 않고 미검증으로 표시

## 설치 방법

**권장 (전역):**

```bash
npx skills add -y -g chann/skills \
  --skill gen-frontend-handoff \
  --skill gen-backend-handoff
```

**프로젝트 로컬:**

```bash
npx skills add chann/skills \
  --skill gen-frontend-handoff \
  --skill gen-backend-handoff
```

설치할 때는 실제 스킬 이름을 `--skill`로 지정합니다. 이 플러그인은 두 핸드오프 생성기를 함께 패키징합니다.

한 줄 selector 형식: `npx skills add chann/skills --skill gen-frontend-handoff --skill gen-backend-handoff`
백엔드 단독 selector 형식: `npx skills add chann/skills --skill gen-backend-handoff`

## 사용 방법

| 커맨드 | 스킬 | 출력 |
|---|---|---|
| `/gen-frontend-handoff` | `gen-frontend-handoff` | `.handoffs/<date>_<scope>_frontend.md`에 프론트엔드/클라이언트 핸드오프 생성 |
| `/gen-backend-handoff` | `gen-backend-handoff` | `.handoffs/<date>_<scope>_backend.md`에 백엔드/서버 핸드오프 생성 |

예시:

```
> /gen-frontend-handoff main...feature-user-api
> /gen-backend-handoff HEAD~5..HEAD
> 현재 백엔드 API diff로 FE 핸드오프 문서 작성
> 현재 Codex 세션 컨텍스트와 git diff로 백엔드 핸드오프 문서 작성
```

## Scope 규칙

- 명시적 scope 없음: unstaged/staged 변경사항을 확인합니다.
- 정확한 범위: 사용자가 지정한 range를 먼저 사용합니다.
- 브랜치 비교: `main...feature` 같은 비교 표현을 그대로 사용합니다.
- 세션 컨텍스트: 대화에서 제공되었거나 파일/명령으로 검증한 내용만 사용합니다.

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼
- Git 저장소

## 라이선스

MIT
