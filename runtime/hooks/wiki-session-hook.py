#!/usr/bin/env python3
"""SessionEnd hook: record changed watched-project files for later wiki update.

Claude Code sends a JSON event on stdin (not the transcript). The event has a
`transcript_path` pointing at a JSONL file; we read that to find which paths
were touched, and append any that live under a watched project to the queue.
"""
import json, sys, os
from datetime import datetime
from pathlib import Path

WIKI_DIR = Path(os.path.expanduser("~/knowledge/wiki"))  # set to your KNOWLEDGE_ROOT
QUEUE = WIKI_DIR / ".update-queue"
WATCHED = ["project-a", "project-b"]                      # your project folder names


def find_paths(obj, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("file_path", "path") and isinstance(v, str):
                out.add(v)
            else:
                find_paths(v, out)
    elif isinstance(obj, list):
        for v in obj:
            find_paths(v, out)


event = json.load(sys.stdin)
session_id = str(event.get("session_id", "unknown"))[:8]
transcript_path = event.get("transcript_path")

paths = set()
if transcript_path and os.path.exists(transcript_path):
    with open(transcript_path) as f:
        for line in f:                       # the transcript file is JSONL
            line = line.strip()
            if not line:
                continue
            try:
                find_paths(json.loads(line), paths)
            except json.JSONDecodeError:
                continue

changed = set()
for p in paths:
    for proj in WATCHED:
        if f"/{proj}/" in p:
            changed.add(p.split(f"/{proj}/", 1)[1])
            break

if changed:
    try:
        QUEUE.parent.mkdir(parents=True, exist_ok=True)
        with open(QUEUE, "a") as f:
            f.write(f"\n## {datetime.now():%Y-%m-%d %H:%M} (session: {session_id})\n")
            for p in sorted(changed):
                f.write(f"- {p}\n")
    except OSError:
        pass  # a SessionEnd hook must never hard-fail the session
