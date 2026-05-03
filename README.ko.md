# skills

[English](README.md)

소프트웨어 엔지니어링 워크플로우를 위한 실용적인 에이전트 스킬 모음입니다.

## 스킬 목록

| 스킬                                                | 설명                                                                                          |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **[code-review](code-review/README.ko.md)**         | git diff 기반 자동 코드 리뷰 — 심각도 표시가 있는 마크다운 / HTML 리포트                       |
| **[conventional-commit](conventional-commit/README.ko.md)** | 변경사항을 Conventional Commits 단위로 분리, 선택적 push, 또는 어수선한 커밋 히스토리 재작성 |

## 설치 방법

모든 스킬을 한 번에 전역 설치 (권장):

```bash
npx skills add -y -g chann/skills
```

스킬별 설치 또는 비전역 / 수동 설치는 각 스킬 README 참조:

- [code-review 설치](code-review/README.ko.md#설치-방법)
- [conventional-commit 설치](conventional-commit/README.ko.md#설치-방법)

## 빠른 참조

### code-review → [상세](code-review/README.ko.md)

| 커맨드              | 출력                                      |
| ------------------- | ----------------------------------------- |
| `/code-review`      | 대화에서 결과 표시 (파일 생성 안 함)      |
| `/code-review-md`   | `.reviews/`에 마크다운 리포트 파일 생성   |
| `/code-review-html` | `.reviews/`에 마크다운 + HTML 리포트 생성 |

### conventional-commit → [상세](conventional-commit/README.ko.md)

| 커맨드                         | 동작                                                              |
| ------------------------------ | ----------------------------------------------------------------- |
| `/conventional-commit`         | 작업 트리 변경을 Conventional Commits 단위로 분리해 커밋          |
| `/conventional-commit-push`    | 위 작업 후 `git push` 까지 진행 (`--force` 안 함)                 |
| `/conventional-commit-rewrite` | 최근 비순응 커밋 subject 를 Conventional 형식으로 재작성          |

## 요구 사항

- [Claude Code](https://code.claude.com) (CLI, 데스크톱 앱, 또는 IDE 확장)
- Git 저장소
- Python 3.10+ (`code-review-html`, `conventional-commit-rewrite` 사용 시 필요)

## 라이선스

MIT
