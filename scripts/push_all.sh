#!/usr/bin/env bash
# Push the whole project to GitHub in three commits, one authored by each member,
# so the history shows everyone contributing (R10). Khalil runs this once.
#
# BEFORE running: set each member's GitHub e-mail below so GitHub links the commits
# to their profiles. Use the e-mail each person signs in to GitHub with (or their
# github "noreply" e-mail from https://github.com/settings/emails).
set -euo pipefail
cd "$(dirname "$0")/.."

KHALIL="Khalil Zakout <zakoutkhalil@gmail.com>"
MONIR="Monir Skaik <mnyrskyk@gmail.com>"
ABDULAZIZ="Abdulaziz Debs <Abdulazez.debs@gmail.com>"

if printf '%s\n' "$KHALIL" "$MONIR" "$ABDULAZIZ" | grep -q REPLACE_; then
  echo "Edit scripts/push_all.sh and set the three GitHub e-mails first." >&2; exit 1
fi

name()  { printf '%s' "${1% <*}"; }
email() { printf '%s' "${1#*<}" | tr -d '>'; }

git add -A

# Monir — Engine black-box suite + performance tests
git -c user.name="$(name "$MONIR")" -c user.email="$(email "$MONIR")" \
    commit -q -m "Engine black-box contract suite and performance tests" \
    -- tests/api tests/performance

# Abdulaziz — security/access tests, system reproductions, AI-eval harness
git -c user.name="$(name "$ABDULAZIZ")" -c user.email="$(email "$ABDULAZIZ")" \
    commit -q -m "Security and access tests, system reproductions, AI-eval harness" \
    -- tests/ai-eval tests/system/reproduce.py \
       portal/src/test/java/com/halcyon/uniplace/qa/SecurityAccessTest.java

# Khalil — everything else (strategy, test cases, reports, scripts, Applications & Offers tests)
git -c user.name="$(name "$KHALIL")" -c user.email="$(email "$KHALIL")" \
    commit -q -m "Test strategy, test cases, defect reports, scripts, Applications & Offers white-box tests" \
    -- .

git branch -M main
git push -u origin main
echo "Pushed. Check the history: git log --pretty='%an  %s'"
