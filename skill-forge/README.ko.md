# skill-forge

[English](README.md) · [← 메인으로](../README.ko.md)

스킬 패키지를 하나의 규칙에 맞춰 만들고, 이미 있는 스킬들이 그 규칙을 지키고
있는지 확인합니다. `skill-forge`가 패키지를 쓰고, `skill-audit`이 검사합니다.

## 무엇이 다른가요?

스킬은 시작하기 쉽고 어중간하게 끝나기도 쉽습니다. `SKILL.md`는 잘 써 놓고
Codex 설명 파일이 빠지거나, 슬래시 명령을 안 만들거나, 웹사이트 카탈로그에는
예전 이름이 남아 있거나, 특정 언어 설명만 실제로 없는 기능을 소개하는 식입니다.

이 플러그인은 그런 상태를 눈에 보이게 만듭니다. 이름, 호출 문법, Codex 설명
파일, 슬래시 명령, eval, 카탈로그와 4개 언어 동기화, 플러그인 매니페스트, 루트
문서에 적힌 개수까지 규칙 9개로 확인합니다.
[`skill-package-contract.md`](skills/skill-forge/references/skill-package-contract.md)에
규칙을 적어 두었고,
[`audit_skills.py`](skills/skill-audit/scripts/audit_skills.py)가 그 규칙을
실행합니다. 위반이 있으면 0이 아닌 종료 코드를 돌려주므로 머지 전 검사로 바로
쓸 수 있습니다.

## 설치 방법

전역 설치:

```bash
npx skills add -y -g chann/skills --skill skill-forge --skill skill-audit
```

현재 프로젝트에 설치:

```bash
npx skills add chann/skills --skill skill-forge --skill skill-audit
```

## 사용법

| Claude Code | Codex | 하는 일 |
|---|---|---|
| `/skill-forge [요청]` | `$skill-forge [요청]` | 스킬 패키지를 만들거나 고치고, 공개 문서까지 맞춘 뒤 검사로 확인 |
| `/skill-audit [스킬 또는 경로]` | `$skill-audit [스킬 또는 경로]` | 규칙을 어긴 스킬 패키지를 모두 보고 |

예시:

```text
/skill-forge CI 실패 로그를 트리아지 메모로 바꾸는 스킬 추가해줘
$skill-forge gen-docs를 project-docs로 이름 바꿔줘
/skill-audit
$skill-audit diff-summary
```

CI에서 검사만 돌리려면 스크립트를 직접 실행합니다.

```bash
python3 skill-forge/skills/skill-audit/scripts/audit_skills.py --root .
python3 skill-forge/skills/skill-audit/scripts/audit_skills.py --format markdown
```

## 규칙

| 규칙 | 확인하는 것 |
|---|---|
| C1 | 디렉터리, 경로, frontmatter 이름이 같은지 |
| C2 | 설명이 정해진 문장으로 시작하고 실제 트리거와 selector 두 개를 담았는지 |
| C3 | `Use only when`과 `disable-model-invocation: true`가 짝을 이루는지 |
| C4 | Codex 설명 파일이 완전하고 `$name`을 호출하는지 |
| C5 | 설명이 있는 슬래시 명령이 있는지 |
| C6 | eval이 3개 이상이고 각각 검증 항목이 2개 이상인지 |
| C7 | 웹사이트 카탈로그와 4개 언어에 모두 들어 있는지 |
| C8 | 플러그인 매니페스트에 이름, 설명, 버전이 있는지 |
| C9 | 루트 문서에 적힌 개수가 실제 트리와 같은지 |

## 패키지 구조

```text
skill-forge/
├── .claude-plugin/plugin.json
├── commands/skill-forge.md
├── commands/skill-audit.md
├── skills/skill-forge/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── evals/evals.json
│   └── references/
│       ├── skill-package-contract.md
│       └── description-grammar.md
├── skills/skill-audit/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── evals/evals.json
│   └── scripts/audit_skills.py
├── README.md
└── README.ko.md
```

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼
- 검사 스크립트 실행에 필요한 `python3` (표준 라이브러리만 사용)

## 라이선스

MIT
