#!/usr/bin/env bash
# Deduplicate a newline-separated list of company names.
# Reads stdin, or first arg if a file path. Writes JSON to stdout:
#   {"unique": [...], "count_in": N, "count_out": M}
# Comparison is case-insensitive on whitespace-trimmed names; first-seen casing wins.
# Exits 0 on success; non-zero with diagnostic on stderr on failure.

set -euo pipefail

main() {
  local input
  if [[ $# -gt 0 ]]; then
    if [[ ! -f "$1" ]]; then
      echo "dedup.sh: input file not found: $1" >&2
      return 2
    fi
    input="$1"
  else
    input="/dev/stdin"
  fi

  awk '
    BEGIN { count_in = 0; count_out = 0 }
    {
      gsub(/^[ \t\r]+|[ \t\r]+$/, "", $0)
      if ($0 == "") next
      count_in++
      key = tolower($0)
      if (!(key in seen)) {
        seen[key] = 1
        unique[count_out++] = $0
      }
    }
    END {
      printf "{\"unique\":["
      for (i = 0; i < count_out; i++) {
        s = unique[i]
        gsub(/\\/, "\\\\", s)
        gsub(/"/, "\\\"", s)
        if (i > 0) printf ","
        printf "\"%s\"", s
      }
      printf "],\"count_in\":%d,\"count_out\":%d}\n", count_in, count_out
    }
  ' "$input"
}

main "$@"
