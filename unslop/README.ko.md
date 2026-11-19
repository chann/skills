# unslop

[English](README.md) · [← 메인으로](../README.ko.md)

AI가 쓴 한국어·영어 텍스트를 사람이 쓴 것처럼 자연스러운 문장으로 다듬는
스킬입니다. 한국어에서는 계약(contract), 엔벨로프(envelope), 패리티(parity) 같은
AI 특유의 직역 용어와 "열린 노드가 없습니다"처럼 새어 나온 내부 방법론 용어를
걷어내고, 번역투 리듬을 매만집니다. 영어에서는 군더더기 첫 문장, 부풀린 어휘,
"not just X but Y", 억지 3항 나열, 대시와 굵은 글씨 남용 같은 흔한 티를
지웁니다. 내용은 바꾸지 않습니다.

> **`human-friendly-writing`에서 이름이 바뀌었습니다.** 예전에는 한국어만
> 다뤘습니다. 한국어 동작은 그대로이고 영어 규칙이 새로 들어왔습니다.

## 절대 바꾸지 않는 것

- 사실, 주장, 수치, 날짜, 고유명사, 코드 식별자, 인용, 링크
- 보존 목록에 있는 표준 기술 용어 (API, 토큰, 프롬프트, 커밋, 멱등, latency,
  cache 등)
- 이미 자연스러운 문장 — 과윤문하지 않습니다
- 글의 언어 — 번역하지 않습니다
- 원본 파일 — 파일 입력은 덮어쓰지 않고 형제 파일로 저장합니다

사전에 없는 한국어 용어는 다음 세 조건을 모두 만족할 때만 교체합니다. 영어
개념어를 직역하거나 음차한 말이고, 그 분야 사람들이 실제로 쓰지 않으며, 뜻이
정확히 같은 자연스러운 대안이 있어야 합니다. 하나라도 확신이 없으면 원래
용어를 남깁니다.

## 규칙을 고르는 방식

언어는 글 전체가 아니라 문장 단위로 판단합니다. 한국어 문장에는 한국어 사전과
문체 규칙을, 영어 문장에는 번호가 붙은 영어 규칙(`E1`~`E21`)을 적용합니다.
규칙 번호는 바뀌지 않아서 다른 스킬이나 답변에서 인용할 수 있습니다. 두 언어가
섞인 글은 문장마다 따로 처리합니다.

## 설치

전역 설치:

```bash
npx skills add -y -g chann/skills --skill unslop
```

현재 프로젝트에 설치:

```bash
npx skills add chann/skills --skill unslop
```

## 사용법

| Claude Code | Codex | 동작 |
|---|---|---|
| `/unslop [텍스트-또는-파일]` | `$unslop [텍스트-또는-파일]` | AI가 쓴 한국어·영어를 뜻은 그대로 두고 자연스러운 문장으로 재작성 |

예시:

```text
/unslop docs/release-note.ko.md
$unslop 이 테스트는 응답 엔벨로프의 계약을 고정한다
$unslop unslop this README intro
```

*"AI 용어 없애줘"*, *"사람답게 다듬어줘"*, *"make this sound human"*,
*"remove the AI tells"* 같은 요청으로도 실행됩니다. 인자가 없으면 대화 중인
텍스트를 다듬습니다. 결과는 재작성된 텍스트와, 어떤 종류의 손질을 했는지 짧고
평이하게 정리한 목록이며, 요청하면 규칙 번호도 함께 알려 줍니다.

## 패키지 구조

```text
unslop/
├── .claude-plugin/plugin.json
├── commands/unslop.md
├── skills/unslop/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── evals/evals.json
│   └── references/
│       ├── english-rules.md
│       ├── slop-lexicon.md
│       └── style-rules.md
├── README.md
└── README.ko.md
```

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼
- 한국어 또는 영어 원문 (다른 언어는 범위 밖)

## 라이선스

MIT
