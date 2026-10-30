#!/usr/bin/env bash
# Static analysis of a repo. Usage: run_semgrep.sh [repo_path]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REPO="${1:-$ROOT/targets/sample-vulnerable-repo}"
OUT="$ROOT/web-code/evidence/semgrep"; mkdir -p "$OUT"
# Reuses semgrep from the Quinine tools venv; or `pip install semgrep` into any venv.
SEMGREP="${SEMGREP:-/d/Quinine-Security-Assessment/.tools-venv/Scripts/semgrep.exe}"
"$SEMGREP" scan --config p/security-audit --config p/python --oss-only --metrics off \
  --json -o "$OUT/semgrep-sample-repo.json" "$REPO" 2> "$OUT/semgrep.log"
echo "done -> $OUT/semgrep-sample-repo.json"
