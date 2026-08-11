# build-reinstall

[English](README.md) · [← 메인으로](../README.ko.md)

현재 프로젝트를 빌드하고, 프로젝트가 정한 명령으로 새 앱이나 CLI를 다시
설치한 뒤 설치된 결과가 새 빌드와 같은지 확인합니다. 사용자가 직접 호출할 때만
실행하며, 다른 작업이 끝났다는 이유만으로 자동 실행되지 않습니다.

## 설치

전역 설치:

```bash
npx skills add -y -g chann/skills --skill build-reinstall
```

현재 프로젝트에 설치:

```bash
npx skills add chann/skills --skill build-reinstall
```

## 사용법

| Claude Code | Codex | 동작 |
| --- | --- | --- |
| `/build-reinstall [프로젝트-루트]` | `$build-reinstall [프로젝트-루트]` | 빌드하고 다시 설치한 뒤 설치 결과 확인 |

프로젝트 루트를 생략하면 현재 저장소를 사용합니다. 스킬은 프로젝트 문서와
스크립트를 먼저 읽고 실행할 명령을 정합니다. 전체 계획을 보여 준 다음 사전
확인, 빌드, 빌드 결과 확인, 재설치, 설치 결과 검증, 결과 보고 순서로 실행합니다.

## 선택형 프로젝트 설정

별도 명령이 필요한 프로젝트는 포함된 예시를 복사해서 사용할 수 있습니다.

```bash
cp build-reinstall/skills/build-reinstall/references/build-reinstall.example.yaml \
  .build-reinstall.yaml
```

스킬을 설치한 뒤에는 스킬 폴더 안의
`references/build-reinstall.example.yaml`을 사용하면 됩니다. 버전 1 설정에는
작업 디렉터리, 빌드·재설치·검증 명령의 실행 순서, 설치 대상, 빌드 파일과 설치
파일의 SHA-256 비교 쌍을 적습니다. 프로젝트 문서만으로 명령과 검증 방법이
분명하면 `.build-reinstall.yaml`은 만들지 않아도 됩니다.

## 안전과 검증

- 빌드가 실패하면 설치된 결과는 건드리지 않습니다.
- 재설치 대상은 프로젝트 문서나 YAML 파일에서 확인되어야 합니다.
- 스킬이 임의로 `sudo`, 강제 옵션, 광범위한 삭제, 릴리스, 배포, 커밋, 푸시를
  추가하지 않습니다.
- 스모크 검사와 빌드·설치 파일의 SHA-256 일치 여부로 완료를 확인합니다.
- GUI, 장치, 서명, 공증, 권한 검증을 할 수 없다면 소스 테스트와 구분해
  알립니다.

## 패키지 구조

```text
build-reinstall/
├── .claude-plugin/plugin.json
├── commands/build-reinstall.md
├── skills/build-reinstall/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/build-reinstall.example.yaml
├── README.md
└── README.ko.md
```

## 요구 사항

- 스킬을 지원하는 에이전트 플랫폼
- 프로젝트가 제공하는 빌드 및 재설치 명령
- 검증할 수 있는 로컬 설치 대상

## 라이선스

MIT
