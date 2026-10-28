#!/bin/sh
# Layer 4, Automation: run /daily-brief without opening a session, so the brief is waiting in
# outputs/drafts/ when you sit down.
#
#   automation/morning-brief.sh claude      (default)
#   automation/morning-brief.sh opencode
#
# The guard still applies: the AI can only write into this workspace and cannot touch private/.
set -eu
cd "$(dirname "$0")/.."
harness="${1:-claude}"
bin="${AIOS_BIN:-$harness}"   # cron has a short PATH: set AIOS_BIN to the full path from `command -v claude`
case "$harness" in
  claude)
    "$bin" -p "/daily-brief" --allowedTools "Read" "Glob" "Grep" "Write(outputs/drafts/**)" "Bash(date)"
    ;;
  opencode)
    "$bin" run --command daily-brief ""
    ;;
  *)
    echo "usage: $0 claude|opencode" >&2
    exit 1
    ;;
esac
