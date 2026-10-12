#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8080}"

cleanup() {
  docker compose down -v >/dev/null 2>&1 || true
}

trap cleanup EXIT

docker compose down -v >/dev/null 2>&1 || true
docker compose up -d --build

for _ in {1..30}; do
  if curl -fsS "${BASE_URL}/health" >/dev/null; then
    break
  fi
  sleep 1
done

health_payload="$(curl -fsS "${BASE_URL}/health")"
first_word_payload="$(curl -fsS "${BASE_URL}/word")"
refreshed_word_payload="$(curl -fsS -X POST "${BASE_URL}/word/new")"

echo "Health: ${health_payload}"
echo "First word: ${first_word_payload}"
echo "Refreshed word: ${refreshed_word_payload}"

python - <<'PY' "${first_word_payload}" "${refreshed_word_payload}"
import json
import sys

first = json.loads(sys.argv[1])
second = json.loads(sys.argv[2])

if first["word_id"] == second["word_id"]:
    raise SystemExit("refresh did not produce a new word_id")

print("PASS: refresh changed word_id")
PY

echo "PASS: container API smoke test completed"
