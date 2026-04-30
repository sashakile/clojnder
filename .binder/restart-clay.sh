#!/usr/bin/env bash
set -euo pipefail

if pgrep -f 'clojnder.binder' >/dev/null 2>&1; then
  pkill -f 'clojnder.binder'
  echo 'Stopped running Clay Binder process.'
else
  echo 'No running Clay Binder process found.'
fi

echo 'Reload /clay to start a fresh Clay process.'
