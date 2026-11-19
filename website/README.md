# skills website

`chann/skills`의 에이전트 워크플로 27개를 검색하고 비교하고 설치하는 다국어
정적 웹사이트입니다.

공개 경로:

- 한국어: <https://chann.github.io/skills/>
- English: <https://chann.github.io/skills/en/>
- 日本語: <https://chann.github.io/skills/jp/>
- 简体中文: <https://chann.github.io/skills/cn/>

루트 경로는 브라우저 언어와 관계없이 항상 한국어를 표시합니다.

## 로컬 개발

저장소 루트에서 실행:

```bash
npm --prefix website ci
npm --prefix website run dev
```

Vite가 출력한 로컬 URL을 브라우저에서 엽니다.

## 검증

```bash
npm --prefix website run verify:catalog
npm --prefix website run verify:landing
npm --prefix website run verify:locales
npm --prefix website run verify:social-cards
npm --prefix website run typecheck
npm --prefix website run build
```

`verify:catalog`은 저장소의 모든 `*/skills/*/SKILL.md` frontmatter 이름과
[`src/data/skills.ts`](src/data/skills.ts)의 카탈로그 ID를 비교합니다. 새 스킬을
추가한 뒤 웹사이트 카탈로그를 갱신하지 않으면 프로덕션 빌드가 실패합니다.
`verify:locales`는 콘텐츠 파일 4개의 키, 스킬 ID 27개, 필수 배열 길이와 번역하지
않은 한국어가 남았는지 확인합니다. `verify:social-cards`는 PNG 4개의 형식과
1200×630 크기를 확인합니다. 전체 빌드는 Vite 결과물에서 언어별 정적 페이지,
메타데이터와 FAQ JSON-LD까지 검사합니다.

## 구성

| 경로 | 역할 |
| --- | --- |
| `src/data/skills.ts` | 언어와 무관한 스킬 ID, 이름, selector, 예시, 태그 |
| `src/i18n/content/*.json` | 언어별 UI, FAQ, 분류와 스킬 설명 |
| `src/i18n/locales.ts` | 공개 경로, 언어 코드와 해시 보존 규칙 |
| `src/components/SkillExplorer.tsx` | 검색, 패키지 필터와 상세 보기 |
| `src/components/LanguageSwitcher.tsx` | 언어 선택 메뉴와 정적 경로 이동 |
| `src/components/CopyButton.tsx` | 클립보드 복사 성공·실패 안내 |
| `src/components/ThemeToggle.tsx` | OS 설정 기반 초기 테마와 light/dark 선택 저장 |
| `src/styles.css` | 반응형 화면, 테마 값과 모션 줄이기 규칙 |
| `public/assets/` | 언어별 1200×630 PNG 소셜 카드 |
| `scripts/verify-catalog.mjs` | 패키지와 카탈로그 일치 검사 |
| `scripts/generate-localized-pages.mjs` | 언어별 정적 HTML과 메타데이터 생성 |
| `scripts/verify-built-locales.mjs` | 최종 HTML 경로, 메타데이터와 FAQ 검사 |

## GitHub Pages

```bash
npm --prefix website run build
```

`main` 브랜치에 푸시하면
[`pages.yml`](../.github/workflows/pages.yml)이 카탈로그 일치 여부와 TypeScript를
검사하고 `website/dist/`을 빌드한 뒤 GitHub Pages에 배포합니다.

이 저장소는 프로젝트 사이트이므로 Vite 기본 경로를 `/skills/`로 설정합니다.
다른 경로에 배포하려면 [`vite.config.ts`](vite.config.ts)의 `base`도 함께
변경해야 합니다.

## 콘텐츠 관리

1. 해당 `SKILL.md`와 `agents/openai.yaml`에 정의된 현재 동작을 확인합니다.
2. 이름, selector, 예시처럼 언어에 무관한 값은 `src/data/skills.ts`에서
   갱신합니다.
3. UI와 요약, 사용 조건, 결과물은 `src/i18n/content/ko.json`, `en.json`,
   `jp.json`, `cn.json`을 모두 갱신합니다.
4. `npm --prefix website run verify:locales`와 전체 빌드로 키와 정적 결과물을
   확인합니다.
5. light, dark, 320px, 390px와 데스크톱 화면에서 주요 흐름을 확인합니다.

## 소셜 카드

언어별 소셜 카드는 저장소에 커밋된 빌드 입력입니다. ImageMagick과
Fontconfig의 `fc-match`가 설치된 환경에서 다음 명령으로 다시 생성합니다.

```bash
node website/scripts/generate-social-cards.mjs
npm --prefix website run verify:social-cards
```

생성기는 한국어, 영어, 일본어, 중국어 시스템 글꼴을 찾아 동일한 1200×630
구성으로 PNG를 만듭니다. 생성한 뒤 이미지 4개를 눈으로 확인하고 전체 빌드를
실행합니다.
