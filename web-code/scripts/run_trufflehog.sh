#!/usr/bin/env bash
# Scan a repo's FULL git history for secrets. Usage: run_trufflehog.sh [repo_path]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REPO="${1:-$ROOT/targets/sample-vulnerable-repo}"
OUT="$ROOT/web-code/evidence/trufflehog"
mkdir -p "$OUT"
TRUFFLEHOG_NO_UPDATE=1 "$ROOT/web-code/tools/trufflehog/trufflehog.exe" \
  git "file://$REPO" --no-update --json \
  > "$OUT/trufflehog-sample-repo.json" 2> "$OUT/trufflehog.log" || true
echo "hits: $(grep -c DetectorName "$OUT/trufflehog-sample-repo.json" || echo 0)  ->  $OUT/"
