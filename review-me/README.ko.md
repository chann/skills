# review-me

[English](README.md) · [← 메인으로](../README.ko.md)

계획, 설계, 중요한 결정을 적용 가능한 모든 leaf까지 따라가는 읽기 전용 결정
트리 리뷰입니다. 한 번에 질문 하나만 제시하고, 구체적인 권장안을 함께 보여주며,
각 답변에서 생기는 후속 결정을 다시 추적한 뒤 확인된 closure record로 끝냅니다.

## 무엇이 다른가요?

`review-me`는 “주제를 이야기했다”와 “결정이 완성됐다”를 구분합니다. 정확한
선택, 경계, 변형 경로, 횡단 관심사, 관찰 가능한 검증 기준이 모두 명시되어야
leaf가 닫힙니다. 마지막에는 적용 가능한 모든 lens를 감사한 뒤에만 완료를
선언합니다.

Matt Pocock의
[`grill-me`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me)와
[`grilling`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling)
스킬을 참고했습니다. 인터뷰 루프를 스킬 안에 내재화하고, 재귀적인 decision
frontier, leaf closure 테스트, lens별 누락 감사, 최종 확인 기록을 추가했습니다.

## 설치 방법

전역 설치:

```bash
npx skills add -y -g chann/skills --skill review-me
```

프로젝트 로컬 설치:

```bash
npx skills add chann/skills --skill review-me
```

## 사용법

| Claude Code | Codex | 동작 |
|---|---|---|
| `/review-me [주제]` | `$review-me [주제]` | 한 번에 결정 하나를 검토하고 적용 가능한 모든 leaf를 닫음 |

예시:

```text
/review-me 팀 초대 기능 계획
$review-me 방금 논의한 캐시 설계를 리뷰해줘
```

인자가 있으면 그 내용을, 없으면 현재 대화를 리뷰합니다. 확인 가능한 사실은
환경과 저장소에서 직접 조사하고, 결과를 바꾸는 선택만 사용자에게 질문합니다.

## 대화 계약

- 매 턴 활성 질문 하나
- 모든 질문에 구체적인 권장안과 핵심 tradeoff 포함
- 의존성 순서로 탐색하고 상위 결정이 바뀌면 영향받는 하위 노드를 다시 엶
- 모든 leaf에 선택, 경계, 변형 경로, 결과 영향, 검증의 다섯 closure 테스트
- resolved, not applicable, deliberately deferred 상태를 모두 포함하는 최종 감사
- closure record가 확인될 때까지 읽기 전용 리뷰 유지

계획, 설계, 제품 동작, 아키텍처와 기타 의사결정을 위한 스킬입니다. Git diff의
결함을 찾을 때는 `/code-review` 또는 `$code-review`를 사용하세요.

## 패키지 구조

```text
review-me/
├── .claude-plugin/plugin.json
├── commands/review-me.md
├── skills/review-me/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── evals/evals.json
│   └── references/review-lenses.md
├── README.md
└── README.ko.md
```

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼
- 리뷰 범위에 포함된 근거에 대한 읽기 권한

## 라이선스

MIT
