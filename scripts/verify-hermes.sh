#!/usr/bin/env bash
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
JOBS_JSON="$HERMES_HOME/cron/jobs.json"

section() {
  printf '\n== %s ==\n' "$1"
}

section "Hermes CLI"
command -v hermes
hermes --version

section "LLM"
hermes -z '只回复 OK'

section "Gateway"
hermes gateway status --full

section "Cron Status"
hermes cron status

section "Cron Quality"
if [[ ! -f "$JOBS_JSON" ]]; then
  echo "Missing cron jobs file: $JOBS_JSON" >&2
  exit 1
fi

jq '{
  total:(.jobs|length),
  prompt_equals_name:(.jobs|map(select(.prompt == .name))|length),
  empty_prompt:(.jobs|map(select((.prompt // "") == ""))|length),
  workdir_null:(.jobs|map(select(.workdir == null))|length),
  old_openclaw_prompt_refs:(.jobs|map(select((.prompt // "") | contains(".openclaw")))|length),
  active:(.jobs|map(select(.enabled == true and .state != "paused"))|length),
  paused:(.jobs|map(select(.enabled == false or .state == "paused"))|length)
}' "$JOBS_JSON"

section "Recent Hermes Runs"
jq -r '
  .jobs
  | map(select((.last_run_at // "") >= (.created_at // "9999")))
  | sort_by(.last_run_at)[]
  | [.last_run_at, .name, .last_status, (.next_run_at // "-"), (.workdir // "-")]
  | @tsv
' "$JOBS_JSON"

section "Next Jobs"
jq -r '
  .jobs
  | sort_by(.next_run_at // "9999")[:8][]
  | [.next_run_at, .name, .last_status, ((.prompt // "") | gsub("\n"; " ") | .[0:120])]
  | @tsv
' "$JOBS_JSON"

section "Launchd"
launchctl list | rg 'ai\.(hermes|openclaw)\.gateway' || true
launchctl print-disabled "gui/$(id -u)" | rg 'ai\.openclaw\.gateway' || true

