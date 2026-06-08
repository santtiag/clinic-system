#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICES=(
  identity-service
  scheduling-service
  billing-service
  medical-record-service
  reporting-service
  admin-panel
)

for service in "${SERVICES[@]}"; do
  echo "==> Running tests for ${service}"
  (
    cd "${ROOT_DIR}/services/${service}"
    pip install -q -r requirements-dev.txt
    pytest -v
  )
done
