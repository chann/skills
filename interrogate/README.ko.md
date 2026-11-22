# interrogate

[English](README.md) · [← 메인으로](../README.ko.md)

배포 전에 변경을 깨뜨려 보고, 주장마다 얼마나 증명됐는지 함께 보여 줍니다.

| 스킬 | 답하는 질문 |
|---|---|
| `interrogate` | 이 diff **안에** 무엇이 잘못됐나요? |
| `blast-radius` | 이 변경이 diff **밖에서** 무엇을 깨뜨릴 수 있나요? |

## 무엇이 다른가요?

그럴듯한 리뷰는 맞는 리뷰와 똑같이 읽힙니다. 그래서 여기서는 모든 발견 사항에
증명 수준과 증거를 함께 적습니다. 수준은 약한 것부터 이렇게 나뉩니다.

| 수준 | 뜻 |
|---|---|
| `said` | 주장만 있음. 발견 사항으로 보고하지 않습니다 |
| `cited` | 바뀐 코드의 실제 `file:line`이 보여 줍니다 |
| `traced` | 실패 경로를 한 단계씩 따라가며 단계마다 줄을 짚었습니다 |
| `ran` | 명령이나 테스트가 실패를 출력했습니다. 명령과 출력을 그대로 붙입니다 |
| `reproduced` | 실행 중인 제품에서 직접 봤습니다 |

- `cited`에 못 미친 발견 사항은 버리고 개수만 셉니다.
- CRITICAL과 HIGH는 `traced`나 `ran`까지 밀어 붙입니다. 끝내 `cited`에 머물면
  `cited, not traced`라고 표시합니다.
- 증명은 리뷰 대상 트리를 건드리지 않습니다. 프로젝트 테스트를 돌리거나,
  저장소 밖 임시 디렉터리에서 작은 재현 스크립트를 실행합니다. 수정도, 파괴적인
  명령도, 저장소 내용을 네트워크로 보내는 일도 없습니다.
- 리뷰는 보고만 합니다. 수정은 적용하지 않습니다.

## 설치 방법

전역 설치:

```bash
npx skills add -y -g chann/skills --skill interrogate --skill blast-radius
```

현재 프로젝트에 설치:

```bash
npx skills add chann/skills --skill interrogate --skill blast-radius
```

두 스킬은 각각 따로 설치해도 동작합니다.

## 사용 방법

| Claude Code | Codex | 결과 |
|---|---|---|
| `/interrogate [scope]` | `$interrogate [scope]` | `.reviews/`에 한국어·영어 마크다운과 이중 언어 HTML 하나를 만들고 브라우저로 엽니다 |
| `/interrogate [scope] --md` | `$interrogate [scope] --md` | `.reviews/`에 마크다운 보고서 하나만 만듭니다. HTML도 브라우저도 없습니다 |
| `/blast-radius [scope]` | `$blast-radius [scope]` | 안전 근거와 그 증거, 위험, 확인 후 문제없던 항목, 머지 전 가장 싼 확인 방법을 답합니다 |

예시:

```text
> 코드 리뷰해줘
> 이 변경 깨뜨려봐
> 빈틈 찾아줘. 마크다운만
> /interrogate main..dev
> /blast-radius
> 영향 범위 확인해줘
```

지정한 범위는 그대로 씁니다. `main..dev`와 `main...dev`는 서로 다른 비교라서
한쪽으로 바꾸지 않습니다. 현재·스테이징·스테이징 전 변경, 마지막 커밋이나 최근
N개 커밋, 커밋·범위·브랜치 비교, PR을 지원합니다.

### 선택: 여러 모델로 공격하기

여러 모델 리뷰, 두 번째 의견, 공격 패널을 요청하고 `swarm` 스킬이 설치돼
있으면, `interrogate`는 같은 지시를 서로 다른 회사의 모델들에게 보냅니다.
돌아온 명령은 직접 다시 실행해서 출력에 실패가 보이는 것만 남기고, 원인이 같은
것은 하나로 합치고, 확인되지 않은 것은 모델별로 **Dropped**에 셉니다. `swarm`이
없으면 지금 세션에서 리뷰하고 패널은 돌리지 않았다고 알려 줍니다.

### 어떤 스킬을 써야 하나요?

| 목적 | 스킬 |
|---|---|
| diff 안의 결함, 회귀, 취약점 찾기 | `interrogate` |
| 변경이 다른 곳에서 깨뜨리는 것과 안전한 이유 증명 | `blast-radius` |
| 무엇이 왜 바뀌었는지 설명 | `diff-summary` |
| 계획 속 결정 따져 보기 | `review-me` |

## `interrogate` 진행 순서

1. 범위를 정하고 변경의 의도를 한 문장으로 적습니다.
2. `diff_stats.py`를 돌리고 해당 언어의 참고 문서만 읽습니다.
3. 정확성, 보안, 복잡도, 유지보수성, 언어별 관례 기준으로 diff를 공격하고
   심각도를 매깁니다.
4. 발견 사항마다 증명 수준을 끌어올리고, `cited`에 못 미친 것은 버립니다.
5. 요청이 있으면 검증된 패널 결과를 합칩니다.
6. 보고서를 씁니다. `--md`가 없으면 영어 보고서와 HTML까지 만들고 엽니다.

## 보고서 형식

발견 사항은 **관찰한 동작 → 실제 결과 → 근거가 허락하는 가장 작은 수정** 순서로
쓰고, 항목마다 `**Evidence:**` 줄이 있습니다. 머리말에는 `**Findings:**` 개수와
`**Dropped:**` 개수가 들어갑니다. `Evidence`, `Dropped` 키와 수준 단어는 한국어
보고서에서도 영어로 둡니다. `Decision Summary`, `Positive Observations`,
`Open Questions`, `File Summary`는 판단에 꼭 필요할 때만 넣습니다.

## HTML 보고서

기본 모드는 한국어 보고서와 영어 번역을 HTML 파일 하나로 합칩니다.

- **증명 수준 표시** — 카드 제목과 증거 줄 옆에 `cited`, `traced`, `ran`,
  `reproduced`를 표시하고, `cited, not traced`는 경고색으로 보여 줍니다.
- **언어 전환** — 기본은 한국어이고, 번역이 없으면 한 언어로 보여 줍니다.
- **테마와 코드 색상** — 라이트·다크·자동, 코드 색상 여덟 가지.
- **사이드바** — 접고 폭을 바꿀 수 있고, 목차와 댓글 목록이 있습니다.
- **발견 사항별 복사와 댓글** — 댓글은 브라우저에 저장되고 ID로 묶여서 언어를
  바꿔도 그대로 붙어 있습니다.
- **피드백 복사** — 새 `/interrogate` 실행에 붙여 넣을 내용을 만들어 줍니다.

보고서는 오프라인에서 열립니다. 코드 강조에 쓰는
`@highlightjs/cdn-assets@11.11.1`과 라이선스를 HTML에 담고, 외부 리소스 로드를 차단합니다.

## 심각도

| 수준 | 의미 |
| -------- | ------------------------------------------------------------- |
| CRITICAL | 데이터 손실, 보안 침해, 운영 중 장애. 반드시 고칩니다 |
| HIGH | 버그, 취약점, 심각한 설계 결함. 머지 전에 고칩니다 |
| MEDIUM | 냄새나는 코드, 불일치, 중간 위험. 고치기를 권합니다 |
| LOW | 스타일, 이름, 작은 개선 |
| INFO | 판단에 영향을 주는 확인된 사실. 코드 수정은 필요 없습니다 |

## `blast-radius` 진행 순서

1. 변경을 읽습니다. diff에 드러나지 않는 동작 변화까지 적습니다.
2. 이 변경이 안전한 이유가 되는 사실 한두 개를 찾습니다.
3. 심볼 검색이 닿지 않는 곳을 봅니다. 고정된 라이브러리 버전의 실제 소스,
   실행 순서와 정리 순서, 직렬화된 형태(API 응답, DB 컬럼, 다른 언어가 읽는
   같은 바이트), 기능 플래그와 설정, 몇 단계 떨어진 하위 코드입니다.
4. 각 사실을 감당할 수 있는 만큼 증명합니다. 대개 임시 디렉터리에서 실제
   코드를 불러오는 스크립트 하나면 됩니다.
5. 안전 근거와 증거(증명 못 했으면 "unproven"), `file:line`이 붙은 위험, 확인
   후 문제없던 항목, 머지 전 가장 싼 확인 방법을 답합니다.

호출하는 곳을 지어내지 않습니다. "찾아봤는데 없음"도 답입니다.

## 패키지 구조

```text
interrogate/
├── .claude-plugin/plugin.json
├── commands/
│   ├── interrogate.md
│   └── blast-radius.md
├── skills/
│   ├── interrogate/
│   │   ├── SKILL.md
│   │   ├── agents/openai.yaml
│   │   ├── evals/evals.json
│   │   ├── scripts/
│   │   │   ├── diff_stats.py
│   │   │   └── generate_html_report.py
│   │   ├── references/
│   │   └── assets/report-template.html
│   └── blast-radius/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       └── evals/evals.json
├── README.md
├── README.ko.md
└── .snyk
```

일부러 취약하게 만든 예제는 플러그인 밖, 저장소 루트의
[`samples/code-review/`](../samples/code-review/)에 있습니다.

## 요구 사항

- Git 저장소
- `interrogate` 보고서 생성용 Python 3.10 이상(표준 라이브러리만 사용)
- `ran` 수준 증명 시 프로젝트 테스트를 실행할 권한

## 라이선스

MIT
