#!/bin/sh
# Build the site from the pushed main branch and publish it as the next commit
# on gh-pages, the branch GitHub Pages serves. Run: npm --prefix website run deploy
set -eu

fail() { echo "$*" >&2; exit 1; }
cd "$(git rev-parse --show-toplevel)"

[ -z "$(git status --porcelain)" ] || fail 'Commit or stash your changes first: the site is built from HEAD.'
git fetch --quiet origin main
commit=$(git rev-parse HEAD)
[ "$commit" = "$(git rev-parse FETCH_HEAD)" ] || fail 'HEAD must be the pushed tip of origin/main.'

npm --prefix website ci
npm --prefix website run build

# Commit dist on top of gh-pages through a scratch index, without checking the branch out.
parent=$(git ls-remote origin refs/heads/gh-pages | cut -f1)
[ -z "$parent" ] || git fetch --quiet origin gh-pages
scratch=$(mktemp -d)
GIT_INDEX_FILE="$scratch/index" git --work-tree=website/dist add --all
tree=$(GIT_INDEX_FILE="$scratch/index" git write-tree)
if [ -n "$parent" ] && [ "$tree" = "$(git rev-parse "$parent^{tree}")" ]; then
  echo "gh-pages already holds this build of $commit."
  exit 0
fi
published=$(git commit-tree "$tree" ${parent:+-p "$parent"} -m "deploy: $commit")
git push --quiet origin "$published:refs/heads/gh-pages"
echo "Published $commit as $published on gh-pages."
