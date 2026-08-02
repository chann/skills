# work-summary

[English](README.md) · [← 메인으로](../README.ko.md)

Claude Code, Codex, opencode, agy 같은 코딩 에이전트가 로컬에 남긴 세션
기록에서 날짜 범위 작업 보고서를 만드는 스킬입니다. 오늘, 이번 주, 이번 달,
혹은 명시적 기간을 지정하면 무엇을 요청했고 무엇이 진행됐는지를 요약 또는
상세 리포트로 정리합니다.

## 무엇이 다른가요?

`work-summary`는 기억이 아니라 기록으로 보고합니다. 보고서의 모든 프로젝트,
수치, 인용된 요청은 각 스토어의 실제 레코드에서 나오며, 읽기 전용으로
수집되어 로컬에만 남습니다. 설치되지 않은 도구는 조용히 건너뛰고, 활동이
없는 기간은 없다고 정직하게 보고하며, 보고서를 커밋하거나 외부로 보내지
않습니다.

## 설치 방법

전역 설치:

```bash
npx skills add -y -g chann/skills --skill work-summary
```

프로젝트 로컬 설치:

```bash
npx skills add chann/skills --skill work-summary
```

## 사용법

| Claude Code | Codex | 동작 |
|---|---|---|
| `/work-summary [범위]` | `$work-summary [범위]` | 오늘·어제·이번 주·이번 달 또는 `YYYY-MM-DD..YYYY-MM-DD` 범위의 Markdown 작업 보고서 |

예시:

```text
/work-summary this week
$work-summary 2026-07-01..2026-07-31 상세 리포트
오늘 뭐 했는지 요약해줘
```

인자가 없으면 오늘을 요약 깊이로 보고합니다. "상세"를 요청하면 타임라인과
요청 로그가 추가되고, 파일 저장을 요청하면 `.work-summaries/` 아래에
저장합니다.

## 대화 계약

- 모든 에이전트 기록 스토어에 대해 읽기 전용
- 로컬 전용: 기록 내용은 머신 밖으로 나가지 않음
- 사용자 로컬 타임존 기준 버킷팅, 주는 월요일 시작
- 기록된 사실만 보고 — 활동 없는 기간은 없다고 표시
- 기본은 대화 응답, 파일은 요청 시에만 생성하고 커밋하지 않음

## 패키지 구조

```text
work-summary/
├── .claude-plugin/plugin.json
├── commands/work-summary.md
├── skills/work-summary/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── evals/evals.json
│   └── references/agent-history-stores.md
├── README.md
└── README.ko.md
```

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼
- 로컬 에이전트 기록 스토어에 대한 읽기 권한
- 임시 조회용 `jq` / `sqlite3` / Python 3 (기본 macOS/Linux 도구)

## 라이선스

MIT
