# human-friendly-writing

[English](README.md) · [← 메인으로](../README.ko.md)

AI가 쓴 한국어 텍스트를 사람이 쓴 것처럼 자연스러운 문장으로 다듬는
스킬입니다. 계약(contract), 엔벨로프(envelope), 패리티(parity) 같은 AI 특유의
직역 용어와 "열린 노드가 없습니다"처럼 새어 나온 내부 방법론 용어를 걷어내고,
번역투 리듬을 매만집니다. 내용은 바꾸지 않습니다.

## 절대 바꾸지 않는 것

- 사실, 주장, 수치, 날짜, 고유명사, 코드 식별자, 인용, 링크
- 보존 목록에 있는 표준 기술 용어 (API, 토큰, 프롬프트, 커밋, 멱등 등)
- 이미 자연스러운 문장 — 과윤문하지 않습니다
- 원본 파일 — 파일 입력은 덮어쓰지 않고 형제 파일로 저장합니다

사전에 없는 용어는 3단 판별을 모두 통과할 때만 교체합니다: 영어 개념어의
직역·음차이고, 그 분야 사람들이 실제로 쓰지 않는 말이며, 뜻이 정확히 같은
자연스러운 대안이 있을 때. 하나라도 확신이 없으면 원래 용어를 남깁니다.

## 설치

전역 설치:

```bash
npx skills add -y -g chann/skills --skill human-friendly-writing
```

프로젝트 로컬 설치:

```bash
npx skills add chann/skills --skill human-friendly-writing
```

## 사용법

| Claude Code | Codex | 동작 |
|---|---|---|
| `/human-friendly-writing [텍스트-또는-파일]` | `$human-friendly-writing [텍스트-또는-파일]` | AI가 쓴 한국어를 뜻은 그대로 두고 자연스러운 문장으로 재작성 |

예시:

```text
/human-friendly-writing docs/release-note.ko.md
$human-friendly-writing 이 테스트는 응답 엔벨로프의 계약을 고정한다
```

*"AI 용어 없애줘"*, *"사람답게 다듬어줘"*, *"자연스러운 한국어로 윤문해줘"*
같은 요청으로도 실행됩니다. 인자가 없으면 대화 중인 한국어 텍스트를
다듬습니다. 결과는 재작성된 텍스트와 함께, 무엇을 어떻게 손봤는지 짧고 평이한
설명으로 전달됩니다.

## 패키지 구조

```text
human-friendly-writing/
├── .claude-plugin/plugin.json
├── commands/human-friendly-writing.md
├── skills/human-friendly-writing/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── slop-lexicon.md
│       └── style-rules.md
├── README.md
└── README.ko.md
```

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼
- 한국어 원문 (다른 언어는 범위 밖)

## 라이선스

MIT
