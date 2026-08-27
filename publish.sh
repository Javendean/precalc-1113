#!/usr/bin/env bash
# Publish dist/ to GitHub Pages.
#
# Refuses to publish a build made from the synthetic bank. That bank exists only
# to shake out the pipeline; its questions are arithmetically trivial and
# pedagogically worthless, and shipping it to a real student would be worse than
# shipping nothing.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f dist/index.html ]; then
  echo "no dist/index.html -- run: cd build && python build.py" >&2
  exit 1
fi

if grep -q '"synthetic":true' dist/index.html; then
  echo "REFUSING: dist/ was built from the synthetic bank." >&2
  echo "Rebuild from the real one:  cd build && python build.py" >&2
  exit 1
fi

ITEMS=$(grep -o '"items":\[' dist/index.html | wc -l)
echo "publishing dist/ ($(wc -c < dist/index.html) bytes)"

git add -A dist
git diff --cached --quiet || git commit -q -m "Publish: rebuild dist/"
git push -q origin master
git subtree push --prefix dist origin gh-pages
echo "pushed. live shortly at https://javendean.github.io/precalc-1113/"
