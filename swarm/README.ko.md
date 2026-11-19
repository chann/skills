# swarm

[English](README.md) · [← 메인으로](../README.ko.md)

여러 에이전트에게 일을 맡기는 방법 두 가지를 담았습니다.

- **`swarm`**은 한 작업을 서브에이전트나 설치된 다른 코딩 에이전트에게 나눠
  맡기고, 경로를 고른 이유를 남기고, 결과를 하나하나 읽은 뒤 호출 트리와 함께
  보고서 하나로 돌려줍니다.
- **`arena`**는 같은 작업을 후보 여러 개에게 따로 시키고, 다른 벤더의 심사자가
  점수를 매기게 한 다음, 가장 나은 안을 바탕으로 다른 안의 좋은 부분을 옮겨
  붙입니다.

> 1.0.0부터 `all-subagents`의 이름이 `swarm`으로 바뀌었습니다.

## `swarm`이 하는 일

- **범위 정하기:** 끝났다고 볼 조건과 돌려줄 결과물 하나를 먼저 적고, 일을
  겹치지 않게 나눌지(`partition`), 같은 지시를 여러 경로에 동시에 줄지(`race`),
  섞을지 정합니다. `race`는 시작 전에 고르는 규칙을 정해 둡니다.
- **나눠 맡기기:** Codex, Claude Code, OpenCode 2.x, Antigravity가 설치돼 있고
  로그인됐는지 확인하고, 고른 이유와 쿼터 출력을 계획 파일에 남깁니다. 없는
  숫자를 적거나 서로 독립인 단계를 같은 벤더에 몰면 계획을 거절합니다.
- **결과 모으기:** `PASS`, `ISSUES`, `BLOCKED` 결과를 직접 읽습니다. 요구한
  내용이 빠진 결과는 한 번 다시 돌리고, 그래도 빠지면 통과가 아니라 빈칸으로
  남깁니다.
- **보고:** 판정, 문제, 빈칸을 담은 표 하나와 `report.md`의 호출 트리를 보여
  줍니다.

실행 기록은 `$XDG_CACHE_HOME/swarm/runs/<run-id>/`에 있습니다.
`XDG_CACHE_HOME`이 없으면 `~/.cache/swarm/runs/<run-id>/`입니다.

## `arena`가 하는 일

- 만들 결과물을 정하고, 후보에게는 보여 주지 않는 채점 기준 3~6개를 적고,
  모든 후보에게 같은 지시와 각자의 출력 위치를 줍니다.
- `swarm`이 설치돼 있으면 그걸 거쳐 후보를 서로 다른 벤더에 앉힙니다.
- 읽기 전용 심사자 하나가 모델 이름 없이 A, B, C 같은 이름표만 보고 채점하고,
  바탕으로 쓸 안은 모든 후보를 끝까지 직접 읽은 뒤에 고릅니다.
- 나머지 후보에서 한두 가지를 손으로 옮겨 붙이고 결과를 검증합니다.

## 설치 방법

**전역 설치:**

```bash
npx skills add -y -g chann/skills --skill swarm
npx skills add -y -g chann/skills --skill arena
```

**현재 프로젝트에 설치:**

```bash
npx skills add chann/skills --skill swarm
npx skills add chann/skills --skill arena
```

설치할 때는 실제 스킬 이름을 `--skill`로 지정합니다. 이 플러그인은 `swarm`과
`arena` 스킬을 패키징합니다.

**수동 설치:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/swarm/skills/swarm" ~/.claude/skills/swarm
ln -s "$(pwd)/skills/swarm/skills/arena" ~/.claude/skills/arena
```

## 사용법

| Claude Code | Codex | 하는 일 |
| --- | --- | --- |
| `/swarm <작업>` | `$swarm <작업>` | 서브에이전트나 다른 코딩 에이전트에게 나눠 맡기고 호출 트리와 함께 보고 |
| `/arena <작업>` | `$arena <작업>` | 결과물 하나를 여러 후보가 경쟁해 만들고, 심사 뒤 가장 나은 안에 좋은 부분을 합침 |

예시:

```text
/swarm 서브에이전트로 이 리뷰 돌려줘
$swarm 병렬로 나눠서 돌려줘
/swarm 이 작업 코덱스에 시켜줘
/arena 설정 로더 API 시안 세 개 만들어서 제일 나은 걸로 골라줘
$arena 여러 안 만들어서 비교해줘
```

여러 날에 걸친 구현은 `/long-task`입니다. 근거를 붙인 조사는
`/research-brief`입니다. 이 세션에서 결함 보고서를 쓰는 일은 `/interrogate`
입니다. 계획의 결정을 하나씩 묻는 인터뷰는 `/review-me`입니다.

쓸 수 있는 경로가 하나뿐이고 사용자가 에이전트나 모델을 지정하지 않았다면,
`swarm`은 작업을 현재 세션에 남깁니다. 모양이 이미 정해진 기계적인 작업이면
`arena`는 경쟁을 돌리지 않고 한 번만 합니다.

## 패키지 구조

```text
swarm/
├── .claude-plugin/plugin.json
├── commands/
│   ├── swarm.md
│   └── arena.md
└── skills/
    ├── swarm/
    │   ├── SKILL.md
    │   ├── agents/openai.yaml
    │   ├── evals/evals.json
    │   ├── assets/prompts/common.md
    │   ├── references/
    │   └── scripts/swarm.py
    └── arena/
        ├── SKILL.md
        ├── agents/openai.yaml
        └── evals/evals.json
```

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼
- `swarm`을 쓰려면 Python 3.10+
- 이 세션 밖으로 작업을 보낼 때는 `codex`, `claude`, OpenCode 2.0.0 이상,
  `agy` 중 하나

## 라이선스

MIT
