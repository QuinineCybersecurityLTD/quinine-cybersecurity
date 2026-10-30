#!/usr/bin/env bash
# Start OWASP Juice Shop on 127.0.0.1:3000 (loopback). Needs: targets/juice-shop installed.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT/targets/juice-shop"
exec node build/app.js   # or: npm start
