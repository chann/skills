# doc-skill

[English](README.md) · [← 메인으로](../README.ko.md)

모든 소프트웨어 프로젝트에서 `README.md`, `README.ko.md`, `ARCHITECTURE.md`, `USAGE.md` 네 문서를 생성하거나 갱신하는 스킬입니다.

## 주요 기능

- `README.md`는 개요, 사용법, 아키텍처를 한데 모으지 않고 프로젝트를 소개하는 짧은 문서로 유지
- `README.ko.md`는 영어 README와 내용이 일치하는 한국어 문서로 유지
- 자세한 명령, 옵션, 설정, 예제, 문제 해결은 `USAGE.md`로 분리
- 구성 요소, 데이터 흐름, 디렉토리 구조, 설계 결정은 `ARCHITECTURE.md`로 분리
- 제목을 기준으로 기존 내용을 갱신하고 `<!-- doc-skill:keep -->`이 있는 사람이 쓴 섹션은 보존
- 새로 쓰는 한국어는 자연스럽고 구체적으로 작성하며, `human-friendly-writing`이 있으면 마지막에 한 번 더 다듬음
- 파일별 diff와 확인을 받은 뒤에만 작성

## 설치

**권장(전역 설치, 자동 승인):**

```bash
npx skills add -y -g chann/skills --skill gen-docs
```

**현재 프로젝트에 설치:**

```bash
npx skills add chann/skills --skill gen-docs
```

설치 선택자는 실제 스킬 이름인 `gen-docs`입니다. `doc-skill`은 이 스킬을 패키징하는 플러그인 디렉터리 이름입니다.

**수동 설치:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/doc-skill/skills/gen-docs" ~/.claude/skills/gen-docs
```

## 빠른 시작

| Claude Code | Codex |
|---|---|
| `/gen-docs [project-root]` | `$gen-docs [project-root]` |

프로젝트 루트에서:

```text
> /gen-docs
```

다른 프로젝트를 대상으로 할 때:

```text
> /gen-docs ../my-project
```

스킬은 프로젝트를 분석해 문서 초안을 만들고 diff를 보여준 뒤, 확인받은 파일만 작성합니다.
`gen-docs`만 설치해도 모든 기능을 쓸 수 있습니다. `human-friendly-writing`을
설치하거나 요구하지 않으며, 이미 사용할 수 있을 때만 새로 쓴 한국어를 diff
표시 전에 한 번 더 다듬습니다.

## 자세한 문서

- [사용법](USAGE.md) - 호출 방식, 워크플로, 업데이트 규칙, 안전 수칙
- [아키텍처](ARCHITECTURE.md) - 플러그인 구조, 스킬 경계, 설계 결정

## 라이선스

MIT
