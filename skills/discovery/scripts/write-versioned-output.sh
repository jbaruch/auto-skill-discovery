#!/usr/bin/env bash
# Persist a discovery JSON artifact to a versioned per-run directory.
#
# Reads JSON from stdin. First positional arg is the company slug.
# Writes to: runs/<UTC-timestamp>/<slug>/discovery.json
# The timestamp is honored from the DISCOVERY_RUN_TS env var if set, so a batch
# of companies in one invocation share the same run directory and are diffable
# as a unit. If unset, the script generates a fresh timestamp.
#
# Stdout: the absolute path of the written file.
# Stderr: diagnostic on error.
# Exit codes: 0 success; 2 missing arg or stdin; 3 write failure.

set -euo pipefail

main() {
  if [[ $# -lt 1 || -z "${1:-}" ]]; then
    echo "write-versioned-output.sh: missing company slug argument" >&2
    return 2
  fi

  local slug="$1"
  # Sanitize slug — alphanumerics, dash, underscore only
  if [[ ! "$slug" =~ ^[A-Za-z0-9_-]+$ ]]; then
    echo "write-versioned-output.sh: slug must match [A-Za-z0-9_-]+; got: $slug" >&2
    return 2
  fi

  # Resolve repo root from the script's location (skills/discovery/scripts/ → repo root is 3 up)
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  local repo_root
  repo_root="$(cd "$script_dir/../../.." && pwd)"

  local ts
  ts="${DISCOVERY_RUN_TS:-$(date -u +%Y-%m-%dT%H-%M-%SZ)}"

  local target_dir="$repo_root/runs/$ts/$slug"
  local target_file="$target_dir/discovery.json"

  mkdir -p "$target_dir"

  if ! cat > "$target_file"; then
    echo "write-versioned-output.sh: failed to write $target_file" >&2
    return 3
  fi

  if [[ ! -s "$target_file" ]]; then
    echo "write-versioned-output.sh: stdin was empty; nothing written to $target_file" >&2
    rm -f "$target_file"
    return 2
  fi

  echo "$target_file"
}

main "$@"
