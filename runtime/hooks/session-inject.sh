#!/usr/bin/env bash
# SessionStart hook: inject the wiki INDEX into Claude's context every session,
# and nudge you when the weekly lint is overdue.
#
# This is the richer alternative to a bare `cat ~/knowledge/wiki/INDEX.md`:
# same injection, plus clean bootstrap markers and an overdue-lint warning, so
# "keep it honest over time" shows up at the start of every session.
#
# Wire it in ~/.claude/settings.json (see runtime/settings.json.example):
#   "SessionStart": [{ "hooks": [
#     { "type": "command", "command": "bash ~/.claude/hooks/session-inject.sh" } ] }]
# Whatever this prints to stdout is added to the session's context.
#
# Using a knowledge folder other than ~/knowledge? Change WIKI below.
set -uo pipefail

WIKI="$HOME/knowledge/wiki"
INDEX="$WIKI/INDEX.md"

if [ ! -f "$INDEX" ]; then
  echo "[bootstrap] $INDEX not found - read your index manually, or fix the WIKI path in this hook."
  exit 0
fi

echo "=== WIKI BOOTSTRAP (injected by SessionStart hook - treat as your INDEX read) ==="

# Overdue-lint nudge: parse "Last lint: YYYY-MM-DD" from INDEX.md and warn past
# LINT_MAX_DAYS. A non-date value (e.g. "never" on a fresh install) is skipped
# silently. Portable across BSD (macOS) and GNU (Linux) date.
LINT_MAX_DAYS=8
LL=$(grep -om1 'Last lint: [0-9-]*' "$INDEX" 2>/dev/null | grep -o '[0-9-]*$' || true)
if [ -n "$LL" ]; then
  LL_S=$(date -j -f %Y-%m-%d "$LL" +%s 2>/dev/null || date -u -d "$LL" +%s 2>/dev/null || echo 0)
  if [ "$LL_S" -gt 0 ]; then
    AGE=$(( ( $(date +%s) - LL_S ) / 86400 ))
    if [ "$AGE" -gt "$LINT_MAX_DAYS" ]; then
      echo "!! Last lint ${AGE}d ago ($LL) - overdue, run /wiki-lint"
    fi
  fi
fi

echo "--- INDEX.md ---"
cat "$INDEX"
echo "=== END WIKI BOOTSTRAP ==="
exit 0
