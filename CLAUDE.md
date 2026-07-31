## Deploy Configuration (configured by /setup-deploy)

- Platform: GitHub Pages
- Production URL: https://chann.github.io/skills/
- Deploy workflow: .github/workflows/pages.yml
- Deploy status command: gh run list --workflow pages.yml --limit 1
- Merge method: direct push to main
- Project type: static web app
- Post-deploy health check: https://chann.github.io/skills/

### Custom deploy hooks

- Pre-merge: npm --prefix website run build
- Deploy trigger: automatic on push to main
- Deploy status: gh run list --workflow pages.yml --limit 1
- Health check: curl --fail --silent --show-error https://chann.github.io/skills/
