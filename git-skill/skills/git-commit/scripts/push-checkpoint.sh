#!/bin/sh
# Arguments are the reviewed remote name, original branch name and full commit ID.
set -eu

fail() { echo "$*" >&2; exit 1; }
[ "$#" -eq 3 ] || fail 'usage: push-checkpoint.sh REMOTE BRANCH COMMIT'
remote=$1
branch=$2
commit=$3
ref="refs/heads/$branch"

[ "$(git symbolic-ref -q HEAD)" = "$ref" ] || fail 'The checked-out branch changed.'
[ "$(git rev-parse HEAD)" = "$commit" ] || fail 'The reviewed commit is no longer HEAD.'
git remote | grep -Fxq -- "$remote" || fail 'Expected a configured remote name.'
[ "$remote" != . ] || fail 'Expected a publishing remote.'
url=$(git remote get-url --push --all -- "$remote")
[ -n "$url" ] || fail 'Missing push destination.'
case "$url" in
  *'
'*) fail 'Expected exactly one push destination.' ;;
esac
[ "$(git config --type=bool --get "remote.$remote.mirror" || :)" != true ] || fail 'Mirror pushes are out of scope.'

git push --no-follow-tags --recurse-submodules=no -- "$remote" "$commit:$ref"
tip=$(git ls-remote --exit-code --refs -- "$url" "$ref" | cut -f1)
[ "$tip" = "$commit" ] || fail 'Push unverified: the remote branch does not match the reviewed commit.'
printf '%s %s %s\n' "$remote" "$ref" "$tip"
