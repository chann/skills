## Deploy Configuration (configured by /setup-deploy)

- Platform: GitHub Pages, served from the `gh-pages` branch
- Production URL: https://chann.github.io/skills/
- Deploy command: npm --prefix website run deploy
- Deploy status command: gh api repos/chann/skills/pages/builds/latest --jq '{status, commit}'
- Merge method: direct push to main
- Project type: static web app
- Post-deploy health check: https://chann.github.io/skills/

### Custom deploy hooks

- Pre-merge: npm --prefix website run build
- Deploy trigger: manual. Run `npm --prefix website run deploy` from a clean checkout of the pushed `main`; it builds locally and pushes the result to `gh-pages`. No GitHub Actions workflow is involved.
- Deploy status: gh api repos/chann/skills/pages/builds/latest --jq '{status, commit}' reports `built` for the `gh-pages` tip
- Health check: curl --fail --silent --show-error https://chann.github.io/skills/
