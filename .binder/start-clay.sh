#!/usr/bin/env bash
set -euo pipefail

PORT="${1:?expected port}"
export CLAY_BINDER_PORT="$PORT"
export CLAY_BASE_PATH="${CLAY_BASE_PATH:-$HOME}"
export CLAY_STARTER_DOC="${CLAY_STARTER_DOC:-notebooks/index.clj}"
export CLAY_URL_PREFIX="${CLAY_URL_PREFIX:-/clay}"

exec clojure -M:clay-binder --port "$PORT"
