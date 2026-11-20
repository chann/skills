# no-comments

[English](README.md) · [← 메인으로](../README.ko.md)

코드를 다시 말하는 주석을 지웁니다. 진짜 제약은 타입, 테스트, 린트로 옮기고
주석은 그다음에 지웁니다.

## 무엇이 다른가요?

주석을 검토하면서 코드까지 고치면, 지워서는 안 되는 줄을 정리라고 부르게
됩니다. 이 스킬은 둘을 나눕니다. `references/comment-review.md`의 검토
프롬프트는 보고만 합니다. 부모가 받아들인 항목만 적용합니다.

- 확인해 볼 수 없는 바깥 규칙을 말하는 주석은 남기고 검토로 표시합니다.
- 거절된 검토가 받아들인 항목을 버리지 않습니다.
- 검토자는 애플리케이션 코드를 고치지 않습니다.

검토는 그 프롬프트로 돕니다. Claude Code와 Codex에서는 일반 서브에이전트가
읽고, 서브에이전트 도구가 없으면 같은 프롬프트를 그 자리에서 한 번 더
읽습니다.

## 설치 방법

전역 설치:

```bash
npx skills add -y -g chann/skills --skill no-comments
```

현재 프로젝트에 설치:

```bash
npx skills add chann/skills --skill no-comments
```

## 사용법

| Claude Code | Codex | 하는 일 |
|---|---|---|
| `/no-comments [파일 또는 diff]` | `$no-comments [파일 또는 diff]` | 설명용 주석을 지우고, 동의하면 제약을 코드로 옮김 |

예시:

```text
/no-comments 이 diff의 설명 주석을 지워줘
$no-comments strip the narration comments in this diff
/no-comments src/billing/invoice.py
```

인자가 없으면 기본 브랜치 대비 현재 diff와 작업 트리가 범위입니다. 읽기 전용
결함 검토는 `interrogate`입니다. 코드 주석이 아닌 글은 `unslop`입니다.

## 하지 않는 일

- 확인하지 못한 바깥 규칙 주석을 지우기
- 거절된 항목 때문에 받아들인 항목까지 버리기
- 동의 없이 제약을 코드로 옮기기
- 검토 패스 안에서 애플리케이션 코드를 고치기

## 패키지 구조

```text
no-comments/
├── .claude-plugin/plugin.json
├── commands/no-comments.md
├── skills/no-comments/
│   ├── SKILL.md
│   ├── references/comment-review.md
│   ├── agents/openai.yaml
│   └── evals/evals.json
├── README.md
└── README.ko.md
```

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼

## 라이선스

MIT
