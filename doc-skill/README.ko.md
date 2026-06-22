# doc-skill

[English](README.md) · [← 메인으로](../README.ko.md)

모든 소프트웨어 프로젝트에 대해 `README.md`, `README.ko.md`, `ARCHITECTURE.md`, `USAGE.md` 네 파일로 된 깔끔한 문서 세트를 생성하거나 갱신하는 스킬입니다.

## 주요 기능

- `README.md`를 개요, 사용법, 아키텍처를 모두 담는 큰 문서가 아니라 짧은 front door로 유지
- `README.ko.md`를 영어 README의 충실한 한국어 미러로 동기화
- 자세한 명령, 옵션, 설정, 예제, 문제 해결은 `USAGE.md`로 분리
- 구성 요소, 데이터 흐름, 디렉토리 구조, 설계 결정은 `ARCHITECTURE.md`로 분리
- heading-aware update-in-place 규칙과 `<!-- doc-skill:keep -->`으로 사람이 쓴 섹션 보존
- 파일별 diff와 확인을 받은 뒤에만 작성

## 설치

**권장 (전역 + 자동 승인, 한 방):**

```bash
npx skills add -y -g chann/skills@doc-skill
```

**프로젝트 로컬:**

```bash
npx skills add chann/skills@doc-skill
```

**수동 설치:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/doc-skill/skills/gendoc" ~/.claude/skills/gendoc
```

## 빠른 시작

프로젝트 루트에서:

```text
> /gendoc
```

다른 프로젝트를 대상으로 할 때:

```text
> /gendoc ../my-project
```

스킬은 프로젝트를 분석하고 후보 문서를 렌더링한 뒤 diff를 보여주며, 확인을 받은 파일만 작성합니다.

## 자세한 문서

- [사용법](USAGE.md) - 호출 방식, 워크플로우, 업데이트 규칙, 안전 노트
- [아키텍처](ARCHITECTURE.md) - 플러그인 구조, 스킬 경계, 설계 결정

## 라이선스

MIT
