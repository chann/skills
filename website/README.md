# skills website

`chann/skills`의 20개 에이전트 워크플로를 검색하고 비교하고 설치하는 다국어
정적 웹사이트입니다.

공개 경로:

- 한국어: <https://chann.github.io/skills/>
- English: <https://chann.github.io/skills/en/>
- 日本語: <https://chann.github.io/skills/jp/>
- 简体中文: <https://chann.github.io/skills/cn/>

루트 경로는 브라우저 언어와 관계없이 항상 한국어를 표시합니다.

## Local development

저장소 루트에서 실행:

```bash
npm --prefix website ci
npm --prefix website run dev
```

Vite가 출력한 로컬 URL을 브라우저에서 엽니다.

## Verification

```bash
npm --prefix website run verify:catalog
npm --prefix website run verify:landing
npm --prefix website run verify:locales
npm --prefix website run verify:social-cards
npm --prefix website run typecheck
npm --prefix website run build
```

`verify:catalog`은 저장소의 모든 `*/skills/*/SKILL.md` frontmatter 이름과
[`src/data/skills.ts`](src/data/skills.ts)의 catalog ID를 비교합니다. 새 스킬을
추가하고 website catalog를 갱신하지 않으면 production build가 실패합니다.
`verify:locales`는 네 콘텐츠 파일의 키, 20개 스킬 ID, 필수 배열 길이와 미번역
한국어 잔존 여부를 확인합니다. `verify:social-cards`는 네 PNG의 형식과
1200×630 크기를 확인합니다. 전체 build는 Vite 산출물에서 언어별 정적 페이지와
metadata, FAQ JSON-LD까지 검증합니다.

## Structure

| Path | Responsibility |
| --- | --- |
| `src/data/skills.ts` | 언어 불변 스킬 ID, 이름, selector, 예시, tag |
| `src/i18n/content/*.json` | 언어별 UI, FAQ, category와 스킬 설명 |
| `src/i18n/locales.ts` | 공개 경로, 언어 코드, hash 보존 계약 |
| `src/components/SkillExplorer.tsx` | 검색, package filter, detail view |
| `src/components/LanguageSwitcher.tsx` | 언어 disclosure와 정적 경로 이동 |
| `src/components/CopyButton.tsx` | clipboard success and error feedback |
| `src/components/ThemeToggle.tsx` | system, light, dark theme persistence |
| `src/styles.css` | responsive layout, theme tokens, reduced-motion rules |
| `public/assets/` | 언어별 1200×630 PNG social card |
| `scripts/verify-catalog.mjs` | package and catalog parity gate |
| `scripts/generate-localized-pages.mjs` | 언어별 정적 HTML과 metadata 생성 |
| `scripts/verify-built-locales.mjs` | 최종 HTML 경로, metadata, FAQ 검증 |

## GitHub Pages

```bash
npm --prefix website run build
```

`main` 브랜치에 푸시하면
[`pages.yml`](../.github/workflows/pages.yml)이 catalog 일치 여부와 TypeScript를
검사하고 `website/dist/`을 빌드한 뒤 GitHub Pages에 배포합니다.

이 저장소는 프로젝트 사이트이므로 Vite base path를 `/skills/`로 설정합니다.
다른 경로에 배포하려면 [`vite.config.ts`](vite.config.ts)의 `base`도 함께
변경해야 합니다.

## Content maintenance

1. 해당 `SKILL.md`와 `agents/openai.yaml`의 현재 계약을 확인합니다.
2. 이름, selector, 예시처럼 언어에 무관한 값은 `src/data/skills.ts`에서
   갱신합니다.
3. UI와 summary, 사용 조건, 산출물은 `src/i18n/content/ko.json`, `en.json`,
   `jp.json`, `cn.json`을 모두 갱신합니다.
4. `npm --prefix website run verify:locales`와 전체 build로 키와 정적 출력을
   확인합니다.
5. light, dark, 320px, 390px, desktop viewport에서 핵심 flow를 확인합니다.

## Social cards

언어별 social card는 저장소에 커밋된 build 입력입니다. ImageMagick과
Fontconfig의 `fc-match`가 설치된 환경에서 다음 명령으로 다시 생성합니다.

```bash
node website/scripts/generate-social-cards.mjs
npm --prefix website run verify:social-cards
```

생성기는 한국어, 영어, 일본어, 중국어 시스템 글꼴을 찾아 동일한 1200×630
구성으로 PNG를 만듭니다. 생성 후 네 이미지를 눈으로 확인하고 전체 build를
실행합니다.
