#!/bin/bash
# Push the committed STATUS.md alone, on top of origin/main. Other unpushed commits stay local.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

git diff --quiet HEAD -- STATUS.md || { echo "Commit STATUS.md first." >&2; exit 1; }
git fetch -q origin main
base=$(git merge-base HEAD origin/main)
if ! git diff --quiet "$base" origin/main -- STATUS.md; then
    echo "STATUS.md changed on origin: git pull --rebase, redo your edit, run this again." >&2
    exit 1
fi
if git diff --quiet origin/main HEAD -- STATUS.md; then
    echo "STATUS.md already up to date on origin."
    exit 0
fi

tmp=$(mktemp -d)
trap 'git worktree remove --force "$tmp/w" 2>/dev/null || true; rm -rf "$tmp"' EXIT
git worktree add -q --detach "$tmp/w" origin/main
git show HEAD:STATUS.md > "$tmp/w/STATUS.md"
git -C "$tmp/w" add STATUS.md
git -C "$tmp/w" commit -q -m "STATUS.md update"
git -C "$tmp/w" push -q origin HEAD:main
echo "Pushed STATUS.md."
