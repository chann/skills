# hol-guard

[English](README.md) · [← 메인으로](../README.ko.md)

위험한 도구 실행 전에 지원되는 로컬 코딩 에이전트 세션을 HOL Guard로
보호합니다. 런타임에서 정확한 지원 하네스를 감지하고 Guard를 초기화한 뒤 보호된
실행 경로를 검증하며, 보호를 입증할 수 없으면 보호되지 않은 에이전트로 우회하지
않고 중단합니다.

## 설치

전역 설치:

```bash
npx skills add -y -g chann/skills --skill hol-guard
```

현재 프로젝트에 설치:

```bash
npx skills add chann/skills --skill hol-guard
```

HOL Guard 런타임은 격리된 Python 앱 환경에 설치합니다.

```bash
pipx install hol-guard
```

## 사용법

| Claude Code | Codex | 동작 |
| --- | --- | --- |
| `/hol-guard` | `$hol-guard` | 위험한 도구 실행 전에 감지된 로컬 코딩 에이전트 하네스를 보호 |

스킬은 `hol-guard detect --json` 결과를 정확한 하네스 식별자의 기준으로 사용하고
`bootstrap → install → dry-run → doctor → run` 순서를 따릅니다. 거부, 검토 필요,
Guard 오류, 타임아웃, 런타임 사용 불가 상태에서는 보호되지 않은 에이전트로
우회하지 않습니다.

## 보안 경계

HOL Guard는 지원되는 로컬 코딩 에이전트 하네스를 보호합니다. 대상 서비스의
인증, 권한, 확인 절차, 리뷰 또는 서버 측 제어를 대체하지 않습니다.

## 라이선스

MIT
