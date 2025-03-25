#!/bin/bash

set -o errexit  # Exit on command failure
set -o pipefail # Exit on pipe failure
set -o nounset  # Exit on undefined variable usage

start_app() {
  local args=(--no-proxy-headers --no-access-log --no-use-colors \
              --no-server-header --no-date-header --host 0.0.0.0 --port 80)

  if [[ "${DEVELOPMENT:-false}" == "true" ]]; then
    uvicorn apps.web:app --reload "${args[@]}"
  else
    echo "Starting production server.."
    uvicorn apps.web:app "${args[@]}"
  fi
}

start_shell() {
  python3 shell.py
}

usage() {
  echo "Usage: $0 {app|shell}" >&2
  exit 1
}

case "${1:-}" in
  app) start_app ;;
  shell) start_shell ;;
  *) usage ;;
esac
