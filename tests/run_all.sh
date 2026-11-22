#!/usr/bin/env bash
# One-command run of the Python test suites (black-box Engine, performance, AI properties).
# The Portal JUnit suite runs separately with Maven: cd portal && ./mvnw test
# Needs the system running: ./start.sh   (Engine 8081, Portal 8080)
set -u
cd "$(dirname "$0")"
fails=0

echo "== Engine contract (tests/api) =="
( cd api && python3 -m unittest -v ) || fails=$((fails+1))

echo; echo "== Engine rank latency (tests/performance) =="
( cd performance && python3 engine_rank_latency.py ) || fails=$((fails+1))

echo; echo "== Portal list pages (tests/performance) =="
( cd performance && python3 portal_pages.py ) || fails=$((fails+1))

echo; echo "== AI prompt properties (tests/ai-eval) =="
( cd ai-eval && python3 -m unittest -v test_prompt_properties.py ) || fails=$((fails+1))

echo
echo "Suites with failures (each failure is a documented defect): $fails"
echo "Run the Portal white-box suite with: cd portal && ./mvnw test"
