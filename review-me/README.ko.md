# review-me

[English](README.md) · [← 메인으로](../README.ko.md)

계획, 설계와 중요한 결정에서 확인해야 할 선택을 끝까지 따라가는 읽기 전용
리뷰입니다. 한 번에 질문 하나만 제시하고 구체적인 권장안을 함께 보여줍니다.
답변에서 새로운 선택이 생기면 이어서 확인하고, 모든 결정이 기록되고 확인된
뒤에 끝냅니다.

## 무엇이 다른가요?

`review-me`는 “주제를 이야기했다”와 “결정을 끝냈다”를 구분합니다. 정확한
선택, 경계, 다른 선택지, 여러 부분에 미치는 영향, 확인 가능한 검증 기준이
모두 명시되어야 결정이 끝납니다. 마지막에는 빠뜨린 관점이 없는지 확인한
뒤에만 완료를 선언합니다.

Matt Pocock의
[`grill-me`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me)와
[`grilling`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling)
스킬을 참고했습니다. 인터뷰 과정을 스킬 안에 담고, 답변에서 새로 드러난
결정을 계속 따라가며 세부 내용의 누락을 확인하고, 마지막 기록을 사용자에게
확인받도록 확장했습니다.

## 설치 방법

전역 설치:

```bash
npx skills add -y -g chann/skills --skill review-me
```

현재 프로젝트에 설치:

```bash
npx skills add chann/skills --skill review-me
```

## 사용법

| Claude Code | Codex | 동작 |
|---|---|---|
| `/review-me [주제]` | `$review-me [주제]` | 한 번에 결정 하나를 검토하며 관련된 선택을 모두 확정 |

예시:

```text
/review-me 팀 초대 기능 계획
$review-me 방금 논의한 캐시 설계를 리뷰해줘
```

인자가 있으면 그 내용을, 없으면 현재 대화를 리뷰합니다. 확인 가능한 사실은
환경과 저장소에서 직접 조사하고, 결과를 바꾸는 선택만 사용자에게 질문합니다.

## 대화 방식

- 매번 질문은 하나만 제시
- 모든 질문에 구체적인 권장안과 핵심 장단점 포함
- 의존성이 앞선 결정부터 살펴보고, 앞선 결정이 바뀌면 영향을 받는 선택을 다시 확인
- 모든 결정에서 선택, 경계, 다른 선택지, 결과에 미치는 영향, 검증 방법 확인
- 해결, 해당 없음, 의도적 보류 항목을 마지막에 모두 정리
- 최종 결정 기록을 확인받을 때까지 내용을 바꾸지 않고 검토만 진행

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
