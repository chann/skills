# skills website

`chann/skills`의 18개 에이전트 워크플로를 검색하고 비교하고 설치하는 정적
웹사이트입니다.

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
npm --prefix website run typecheck
npm --prefix website run build
```

`verify:catalog`은 저장소의 모든 `*/skills/*/SKILL.md` frontmatter 이름과
[`src/data/skills.ts`](src/data/skills.ts)의 catalog ID를 비교합니다. 새 스킬을
추가하고 website catalog를 갱신하지 않으면 production build가 실패합니다.

## Structure

| Path | Responsibility |
| --- | --- |
| `src/data/skills.ts` | 스킬 이름, selector, 사용 조건, 산출물 |
| `src/components/SkillExplorer.tsx` | 검색, package filter, detail view |
| `src/components/CopyButton.tsx` | clipboard success and error feedback |
| `src/components/ThemeToggle.tsx` | system, light, dark theme persistence |
| `src/styles.css` | responsive layout, theme tokens, reduced-motion rules |
| `public/assets/` | generated editorial WebP artwork |
| `scripts/verify-catalog.mjs` | package and catalog parity gate |

## Static hosting

```bash
npm --prefix website run build
```

`website/dist/`은 base path에 의존하지 않는 정적 bundle입니다. GitHub Pages,
Cloudflare Pages, Netlify, Vercel의 static output으로 배포할 수 있습니다.

## Content maintenance

1. 해당 `SKILL.md`와 `agents/openai.yaml`의 현재 계약을 확인합니다.
2. `src/data/skills.ts`의 설명, selector, 예시를 갱신합니다.
3. `npm --prefix website run verify:catalog`으로 누락과 중복을 검사합니다.
4. light, dark, 320px, 390px, desktop viewport에서 핵심 flow를 확인합니다.
