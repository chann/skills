# all-subagents

[English](README.md) · [← 메인으로](../README.ko.md)

서브에이전트로 돌리라고 한 작업을 다른 코딩 에이전트에게 맡기고, 그 경로를
고른 이유와 결과를 호출 트리로 남깁니다.

## 하는 일

- Codex, Claude Code, OpenCode 2.x, Antigravity가 설치돼 있고 로그인됐는지 확인합니다.
- 고른 이유와 쿼터 출력을 계획 파일에 남깁니다. 없는 숫자를 적거나, 서로 독립인
  확인을 같은 벤더에 몰아 넣으면 계획을 거절합니다.
- 프롬프트 파일과 샌드박스, 필요하면 Git 변경 검사와 함께 고른 CLI를 실행합니다.
- 어떤 에이전트와 모델이 무엇을 했는지, 허용한 경로 안에서 끝났는지를 `report.md`에 남깁니다.

실행 기록은 `$XDG_CACHE_HOME/all-subagents/runs/<run-id>/`에 있습니다.
`XDG_CACHE_HOME`이 없으면 `~/.cache/all-subagents/runs/<run-id>/`입니다.

## 설치 방법

**전역 설치:**

```bash
npx skills add -y -g chann/skills --skill all-subagents
```

**현재 프로젝트에 설치:**

```bash
npx skills add chann/skills --skill all-subagents
```

설치할 때는 실제 스킬 이름을 `--skill`로 지정합니다. 이 플러그인은
`all-subagents` 스킬을 패키징합니다.

**수동 설치:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/all-subagents/skills/all-subagents" ~/.claude/skills/all-subagents
```

## 사용법

| Claude Code | Codex | 하는 일 |
| --- | --- | --- |
| `/all-subagents [작업]` | `$all-subagents [작업]` | 다른 코딩 에이전트에게 작업을 맡기고 호출 트리를 남김 |

예시:

```text
/all-subagents 서브에이전트로 이 리뷰 돌려줘
$all-subagents 서브에이전트 써서 돌려줘
/all-subagents 이 작업 코덱스에 시켜줘
```

여러 날에 걸친 구현은 `/long-task`입니다. 근거를 붙인 조사는
`/research-brief`입니다. 이 세션에서 결함 보고서를 쓰는 일은 `/code-review`입니다.

쓸 수 있는 경로가 하나뿐이고 사용자가 에이전트나 모델을 지정하지 않았다면,
작업은 현재 세션에 남습니다.

## 패키지 구조

```text
all-subagents/
├── .claude-plugin/plugin.json
├── commands/all-subagents.md
└── skills/all-subagents/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── evals/evals.json
    ├── assets/prompts/common.md
    ├── references/
    └── scripts/all_subagents.py
```

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼
- Python 3.10+
- 이 세션 밖으로 작업을 보낼 때는 `codex`, `claude`, OpenCode 2.0.0 이상,
  `agy` 중 하나

## 라이선스

MIT
