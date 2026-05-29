#!/usr/bin/env bash
# Dependency vulnerability audit (H.5). Scans the backend's pinned deps with
# pip-audit. Run from the repo root: ./scripts/security_audit.sh
set -euo pipefail

cd "$(dirname "$0")/../backend"

if ! command -v pip-audit >/dev/null 2>&1; then
  echo "Installing pip-audit..."
  pip install --quiet pip-audit
fi

echo "Auditing backend/requirements.txt for known vulnerabilities..."
pip-audit -r requirements.txt
