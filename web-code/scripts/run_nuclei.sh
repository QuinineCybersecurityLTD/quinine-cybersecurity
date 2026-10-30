#!/usr/bin/env bash
# Scan a running web app with Nuclei templates. Usage: run_nuclei.sh [target_url]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TARGET="${1:-http://127.0.0.1:3000}"
OUT="$ROOT/web-code/evidence/nuclei"; mkdir -p "$OUT"
"$ROOT/web-code/tools/nuclei/nuclei.exe" -u "$TARGET" \
  -tags exposure,misconfig,tech,cve,default-login -severity info,low,medium,high,critical \
  -jsonl -o "$OUT/nuclei-juiceshop.jsonl" -stats 2> "$OUT/nuclei.log" || true
echo "findings: $(wc -l < "$OUT/nuclei-juiceshop.jsonl" 2>/dev/null || echo 0)  ->  $OUT/"
