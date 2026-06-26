#!/usr/bin/env python3
"""SessionEnd hook: record changed watched-project files for later wiki update.

Claude Code sends a JSON event on stdin (not the transcript). The event has a
`transcript_path` pointing at a JSONL file; we read that to find which paths
were touched, and append any that live under a watched project to the queue.

This script must never hard-fail the session: the outermost try/except ensures
that empty stdin, garbage input, or any unexpected error always exits 0.
"""
import json, sys, os
from datetime import datetime
from pathlib import Path

WIKI_DIR = Path(os.path.expanduser("~/knowledge/wiki"))  # set to your KNOWLEDGE_ROOT
QUEUE = WIKI_DIR / ".update-queue"
WATCHED = ["project-a", "project-b"]                      # your project folder names

# Pre-compute realpath roots for WATCHED names anchored under the user's home.
# Sort descending by length so a more-specific name cannot be eclipsed by a
# shorter prefix (e.g. "app" cannot false-match "app-v2").
_HOME = Path(os.path.expanduser("~")).resolve()
_WATCHED_ROOTS = sorted(
    [(_HOME / name).resolve() for name in WATCHED],
    key=lambda p: len(p.parts),
    reverse=True,
)


def _safe_realpath(raw: str):
    """Return a resolved Path for raw, or None if it is unsafe.

    Rejects:
    - any value that still contains ".." after resolution (shouldn't happen
      after realpath, but belt-and-suspenders)
    - paths that do not sit under one of the _WATCHED_ROOTS
    - anything that looks like a URL or does not start with /
    """
    if not raw or not raw.startswith("/"):
        return None
    try:
        resolved = Path(os.path.realpath(os.path.expanduser(raw)))
    except (ValueError, OSError):
        return None
    # Reject any residual ".." traversal
    if ".." in resolved.parts:
        return None
    return resolved


def _matching_root(resolved: Path):
    """Return the first WATCHED root that is a proper ancestor of resolved, or None."""
    for root in _WATCHED_ROOTS:
        # Use is_relative_to-style check compatible with Python 3.8
        try:
            resolved.relative_to(root)
            return root
        except ValueError:
            continue
    return None


def find_paths(obj, out):
    """Recursively collect only file_path / notebook_path values from obj."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("file_path", "notebook_path") and isinstance(v, str):
                out.add(v)
            else:
                find_paths(v, out)
    elif isinstance(obj, list):
        for v in obj:
            find_paths(v, out)


def main():
    event = json.load(sys.stdin)
    session_id = str(event.get("session_id", "unknown"))[:8]
    transcript_path = event.get("transcript_path")

    raw_paths = set()
    if transcript_path and os.path.exists(str(transcript_path)):
        with open(transcript_path) as f:
            for line in f:                       # the transcript file is JSONL
                line = line.strip()
                if not line:
                    continue
                try:
                    find_paths(json.loads(line), raw_paths)
                except json.JSONDecodeError:
                    continue

    changed = set()
    for raw in raw_paths:
        resolved = _safe_realpath(raw)
        if resolved is None:
            continue
        root = _matching_root(resolved)
        if root is None:
            continue
        # Store the relative portion under the watched root
        changed.add(str(resolved.relative_to(root.parent)))

    if changed:
        try:
            QUEUE.parent.mkdir(parents=True, exist_ok=True)
            with open(QUEUE, "a") as f:
                f.write(f"\n## {datetime.now():%Y-%m-%d %H:%M} (session: {session_id})\n")
                for p in sorted(changed):
                    f.write(f"- {p}\n")
        except OSError:
            pass  # a SessionEnd hook must never hard-fail the session


try:
    main()
except Exception:
    pass  # outermost guard: empty/garbage stdin or any unexpected error must never crash the session
