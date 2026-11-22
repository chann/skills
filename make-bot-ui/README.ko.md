# make-bot-ui

[English](README.md) · [← 메인으로](../README.ko.md)

직접 준 웹훅으로 봇을 깨우는 페이지를 만듭니다. 발신 키는 서버에만 있습니다.
브라우저는 웹훅을 호출하지 않습니다.

## 무엇이 다른가요?

버튼이 발신 키를 들고 있으면 그 키는 페이지와 로그, 그리고 페이지를 만든
대화에 남습니다. 이 스킬은 그 모양을 거절합니다.

- 웹훅 URL은 사용자가 줍니다.
- 발신 키는 서버 설정에만 있습니다. 대화에 붙여 넣은 키는 거절합니다.
- 키를 페이지나 대화 기록에 넣지 않습니다.
- POST는 브라우저가 아니라 로컬 서버가 보냅니다.

`scripts/webhook_post.py`가 페이지를 만들고, 키나 웹훅 호스트가 들어간
페이지를 거절하고, 서버가 보낼 POST 하나를 만듭니다.

## 설치 방법

전역 설치:

```bash
npx skills add -y -g chann/skills --skill make-bot-ui
```

현재 프로젝트에 설치:

```bash
npx skills add chann/skills --skill make-bot-ui
```

## 사용법

| Claude Code | Codex | 하는 일 |
|---|---|---|
| `/make-bot-ui [웹훅 URL]` | `$make-bot-ui [웹훅 URL]` | 웹훅으로 봇을 깨우는 페이지를 만듦 |

예시:

```text
/make-bot-ui https://hooks.example.test/wake
$make-bot-ui 핑 버튼이 있는 페이지를 만들어줘. 웹훅 주소는 내가 줄게
/make-bot-ui 이 웹훅으로 봇을 깨우는 버튼 페이지를 만들어줘
```

발신 키는 서버 설정 파일에 직접 적습니다. 웹훅 API가 무엇을 하는지가
질문이면 `research-brief`입니다.

## 하지 않는 일

- 대화에 붙여 넣은 발신 키를 받기
- 키나 웹훅 호스트가 들어 있는 페이지를 두기
- 브라우저가 웹훅으로 POST하게 두기
- 실패한 POST를 다시 보내기
- 사용자가 주지 않은 웹훅 URL을 만들어 내기

## 패키지 구조

```text
make-bot-ui/
├── .claude-plugin/plugin.json
├── commands/make-bot-ui.md
├── skills/make-bot-ui/
│   ├── SKILL.md
│   ├── scripts/webhook_post.py
│   ├── agents/openai.yaml
│   └── evals/evals.json
├── README.md
└── README.ko.md
```

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼
- `scripts/webhook_post.py`를 위한 Python 3.10+ (표준 라이브러리만 사용)

## 라이선스

MIT
