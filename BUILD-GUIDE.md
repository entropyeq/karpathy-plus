# Build Your Own Karpathy+ System

**A handoff guide for Claude to build a persistent, structured memory system for a new user, then maintain it.**

Version 3 · 2026-06-17 · Paired with the essay at [eqctrl.io/karpathy+](https://eqctrl.io/karpathy+)

---

> **Used "Use this template" to get this repo?** The `wiki/` and `runtime/` scaffolds already exist. Follow **SETUP.md** for the short install and skip Steps 2-3 below, which build the scaffold from scratch. Everything else here applies. This guide is the full reference: read it to understand every piece, or to build the system without the template.

---

## How to use this document

You are reading this because your user wants Claude to have a persistent, structured memory that sticks between chats and stays correct over time. Your job is two-fold: first build the system with them, then be its first inhabitant: its primary reader, its primary writer, and the agent that keeps it honest over time.

This guide is deliberately opinionated. Every rule below exists because something broke without it. You can adapt the specifics, but the core architecture is load-bearing. If you diverge from it, name the reason.

**The work splits in two.** Part One is the build: one focused afternoon, mostly Claude writing files while the user answers questions. Part Two is living with it: a few minutes of review a week, forever. Part Two is where a folder of markdown becomes a system that stays true. Most people underweight it. Do not.

**Fastest start:** this file is written to be executed, not just read. Hand the whole thing to Claude and say: *"Build this system for me. Walk me through it step by step, and ask me for any facts you need before you write anything."* Then answer the questions. You will have a working system before the coffee is cold.

**Even faster:** if there is a template repo for this (see the README link you came from), click **Use this template** to get a private GitHub repo with every scaffold below already in place. Then the build is just filling in blanks and answering questions, and Part Two starts immediately.

---

## A note on models

This guide is Claude-specific by design, and that is a recommendation, not just a default. The examples use Claude Code conventions (`CLAUDE.md`, slash commands, session hooks) and a current model like Opus 4.8. It is the smoothest path and it is what I run.

If you work with other models, including local ones, the clean pattern is to let **Claude be the orchestrator**: Claude reads and maintains the wiki, and dispatches to other models as workers when you want them. The system stays keyed to Claude; the other models are hands, not the brain. You lose nothing structural by running this Claude-first, and you gain a single consistent maintainer.

---

## Before you start: what you need

This guide targets macOS and Linux. On Windows, run it inside WSL. You need four things in place before the build:

1. **Claude Code.** The agent that actually creates folders and writes files on your machine; a browser chat cannot do this build. Install Node 18+ then `npm install -g @anthropic-ai/claude-code`, run `claude` in a terminal, and sign in when prompted. If `claude` starts, you are ready.
2. **git and the GitHub CLI.** Check with `git --version` and `gh --version`; install whichever is missing (on macOS, `brew install git gh`). The wiki lives as a git repo so it is backed up off your machine and readable by scheduled cloud agents later.
3. **A GitHub account.** Free, at [github.com](https://github.com). Step 2 wires it up.
4. **(Optional) Obsidian.** A free reader that makes the wiki pleasant to browse and edit by hand. Point it at your knowledge folder. Skip it if you live in the terminal.

**Glossary** (four terms this guide leans on):

- **Schema / `CLAUDE.md`:** the small rules file Claude reads at the start of every session. It holds behavior rules, not knowledge.
- **Hook:** a tiny script your runtime runs automatically at a moment you choose (here: session start and session end). It is a tripwire, not a brain.
- **Slash command:** a saved instruction you invoke by name, like `/wiki-lint`. It is a reusable prompt.
- **Frontmatter:** the `---` block at the top of a markdown file holding metadata like `last_updated`. Lint reads it.

---

## What you're building

A three-layer knowledge system:

```
Sources ──> Wiki ──> Schema ──> Session
(raw/messy)   (curated)   (~50 lines)   (context-aware Claude)
```

- **Sources** (`wiki/sources/`) are raw inputs: transcripts, bookmarks, tool feeds, exports. Messy. Claude curates them upward.
- **Wiki** (`wiki/`) is the curated layer. Target 15 to 30 pages. Claude-maintained.
- **Schema** (`CLAUDE.md`) is behavior rules plus wiki conventions. About 50 lines. No knowledge lives here; it tells Claude how to read the wiki.

Outcomes when built correctly:

- Build time: under an hour.
- Steady-state maintenance: a few minutes of human review per week.
- Failure mode closed: silent drift, where context diverges from reality without anyone noticing until something breaks.

---

## Core concepts the user should understand before you build

Walk the user through these before touching the filesystem.

**1. The boundary rule.** Knowledge goes in one place (for example, `~/knowledge/`). Runtime goes somewhere else (for example, `~/.claude/`). One rule, strictly enforced. Prevents the "same knowledge in three files, drifting independently" failure that kills most LLM memory systems.

**2. Progressive disclosure.** Claude does not load the wiki. It loads a lightweight index and reads only the two to four pages relevant to the current task. A system that requires loading everything before working is a system that gets skipped in long sessions.

**3. Three operations.** The wiki is not a static collection. It has three operations that keep it alive: ingest (write new knowledge after a change), query (read 2 to 4 pages at session start), lint (scheduled health check).

**4. Defense in depth.** No single enforcement layer is enough. Behavior rules, a session hook, scheduled lint, git history, a heartbeat timestamp, and a completion gate each catch a different class of failure. The system fails only if every layer fails at once. These split across three enforcement modes: file-state checks (does the record match reality?), tripwires (did a change happen that needs follow-through?), and output verification (did a scheduled job actually produce its expected output, on time?). One mode is blind to runtime, another is blind to staleness; together they cover the gaps.

**5. Propagation is a snapshot.** Copies detach from their source at propagation time. Auto-memory, UI instructions, and forwarded session prompts are all snapshots, not live references. Verify at consumption.

**6. Context drifts, and that is normal.** A working context is never permanently consistent. Facts change, decisions get revised, two pages will occasionally disagree. The job of the system is not to prevent that, it is to surface inconsistencies fast and make the user reconcile them on purpose, rather than letting them rot silently. Maintenance is not cleanup after a failure; it is the normal operating state of a living context. Expect to align things regularly. The hook, the lint, the heartbeat, and the "log this" habit all exist to make that alignment cheap and routine instead of a periodic crisis.

---

# PART ONE: BUILD IT

One afternoon. Mostly you writing files while the user answers questions. At the end of Part One the system works. Part Two is what keeps it true.

Work through the steps in order. Ask the user for missing facts (name, domains, project list) before drafting content. Prefer creating empty scaffolds the user fills in over inventing placeholder content that goes stale.

---

## Step 1: Decide the boundary

Ask the user:

- Where does their Claude runtime configuration live? (For Claude Code, this is `~/.claude/`.)
- Where do they want knowledge and project work to live? (Common choices: `~/knowledge/`, `~/wiki/`, or `~/notes/`.)

Pick two clean, separate directories. Never collapse them. The separation IS the rule.

For the rest of this guide, call them `KNOWLEDGE_ROOT` and `RUNTIME_ROOT`. Set them as shell variables now so every command below runs exactly as pasted:

```bash
KNOWLEDGE_ROOT="$HOME/knowledge"   # change to your choice
RUNTIME_ROOT="$HOME/.claude"
```

---

## Step 2: Set up GitHub and the wiki repo

Do this early. The wiki being a git repo from the start gives you off-machine backup, a full history (which the lint uses to age pages), and the ability for cloud-scheduled agents to read canonical state later. This is an architectural choice, not a deployment detail.

**The easy path (if you used the template repo):** you already have a private repo. Clone it into `KNOWLEDGE_ROOT` and skip to Step 3:

```bash
gh repo clone YOUR-USERNAME/wiki "$KNOWLEDGE_ROOT/wiki"
```

**From scratch (beginner walkthrough):** run these in a terminal.

```bash
# 1. Authenticate once. Opens a browser to log in.
gh auth login

# 2. Create the wiki folder and make it a git repo on a `main` branch.
mkdir -p "$KNOWLEDGE_ROOT/wiki"
cd "$KNOWLEDGE_ROOT/wiki"
git init -b main          # the -b main avoids the old master/main mismatch

# 3. First commit. We add real files in the next steps; this just seeds the branch.
git commit --allow-empty -m "Wiki system bootstrapped"

# 4. Create a PRIVATE GitHub repo, set it as origin, and push, in one command.
gh repo create wiki --private --source=. --remote=origin --push
```

If your git is older than 2.28 it has no `-b` flag: run `git init` then `git branch -M main` instead. No `gh`? Create a private repo named `wiki` in the GitHub web UI, then run the `git remote add origin ...` and `git push -u origin main` lines GitHub shows on the empty-repo page (run `git branch -M main` first if you are on `master`).

A remote is technically optional, but skipping it means no backup and no cloud agents. Do not skip it.

---

## Step 3: Create the wiki structure

Inside `$KNOWLEDGE_ROOT/wiki`, create this structure:

```
wiki/
├── INDEX.md              # Read FIRST every session. Catalog + heartbeat.
├── log.md                # Chronological: changes, decisions, judgments
├── system/               # Infrastructure knowledge (ALL-CAPS filenames)
│   └── HOW-THE-WIKI-WORKS.md
├── projects/             # One page per project
├── patterns/             # Reusable patterns, regressions, conventions
├── personal/             # Bio, career, long-form reference
├── plans/                # Forward-looking plans (see `last_reconciled:` note)
└── sources/              # Raw input before curation
```

Naming conventions:

- `system/` files are ALL-CAPS (visually distinct, these are operating-manual pages).
- Everything else uses lowercase topic names.
- No archive directory inside `wiki/`. Git history is the archive. Old pages are deleted, not moved. (To recover one later: `git log --all -- path/to/page.md` to find it, then `git show <sha>:path/to/page.md`.)

---

## Step 4: Write the schema (CLAUDE.md)

Create `CLAUDE.md` at `RUNTIME_ROOT`. Keep it under 80 lines. Below is a template. Fill in the `[bracketed]` placeholders by asking the user, and replace `KNOWLEDGE_ROOT` with the real path you chose (e.g. `~/knowledge`).

```markdown
# BOOTSTRAP: BEFORE ANY RESPONSE
A SessionStart hook injects `KNOWLEDGE_ROOT/wiki/INDEX.md` into your context (set up in Step 7). Treat that injected block as your index read. If it is not present, read `KNOWLEDGE_ROOT/wiki/INDEX.md` yourself NOW, before responding.

# Schema

You are working with [USER NAME]. [ONE-LINE USER CONTEXT: role, focus areas].

## Wiki

All knowledge lives in `KNOWLEDGE_ROOT/wiki/`. Read only the 2-4 pages you need per session. If `KNOWLEDGE_ROOT/wiki/.update-queue` exists, process it (update wiki pages for listed changed files, then clear the queue).

After any session that changes state: update the relevant wiki page(s) and append to `KNOWLEDGE_ROOT/wiki/log.md`. Include a `Judgment:` line for fixes, tradeoffs, and decisions.

`log.md` is write-only during sessions. Do not read at session start; use `git log` or read the last 10 entries on demand.

When two pages disagree, or a page disagrees with what the user just told you, surface it. Do not silently pick one. Ask which is current, fix the stale one, and log the reconciliation. Inconsistency is expected; resolving it out loud is the job.

## File Placement

No loose files at `KNOWLEDGE_ROOT/` root. Every file lives in a bucket:

| Bucket | For |
|---|---|
| `wiki/` | Curated canonical knowledge |
| `<project>/` | Active project code |
| `[YOUR CATEGORIES]` | [personal, career, outputs, etc.] |
| `inbox/` | Untriaged arrivals |
| `scratch/` | Throwaway |

Archive and backups live OUTSIDE `KNOWLEDGE_ROOT/` (for example at `~/Archive/`) to keep scoped tools (MCP servers, search indexes) clean.

## Style

[USER STYLE RULES: brevity, tone, formatting preferences.]

## Trigger Phrases

"log this" -> update relevant wiki page + log.md
"do it / defer it / kill it" -> lint triage responses
[ADD YOUR OWN]

## Forwarded Instructions

When a session starts with a forwarded or terse instruction that references a plan or prior session ("build X per plan.md"), treat it as a claim, not a direction. Re-derive scope from current wiki before executing. Propagation is a snapshot.
```

Why this works:

- The SessionStart hook puts `INDEX.md` in context every session, so Claude starts grounded instead of being trusted to remember to read it. The prose directive is the fallback for surfaces without the hook.
- File placement rules prevent stray writes to root.
- The reconcile rule turns silent disagreement into an out-loud decision.
- Trigger phrases give the user conversational control.
- Forwarded-instructions rule prevents executing against stale plans.

---

## Step 5: Create INDEX.md

This is the entry point every session reads (and the file the Step 7 hook injects). Keep it under 50 lines. Each line under 150 characters.

```markdown
---
schema_version: 1.2
last_updated: [TODAY]
---
# Wiki Index

Last updated: [TODAY] (N pages across M sections) | Last lint: [TODAY]

## Projects
- [project-a](projects/project-a.md) -- [one-line status]

## System
- [HOW-THE-WIKI-WORKS](system/HOW-THE-WIKI-WORKS.md) -- Operating manual for the system

## Patterns
- [regressions](patterns/regressions.md) -- Correction log, rules the system enforces

## Plans
- [todo.md](todo.md) -- Active task backlog
```

One line per page. Short descriptions. The index is the progressive-disclosure gate; it has to fit cheap in every session's context.

`schema_version` tracks the wiki's conventions, not its content. Bump it only when a session-visible convention changes (a bootstrap directive, the bucket taxonomy, a mandated trigger phrase). Adding a page or updating a status does not bump it. The number lets a session notice when its cached idea of "how this wiki works" is older than the wiki itself.

---

## Step 6: Create the first pages and the page template

Write three to five pages covering the user's most-repeated context. Resist writing more; the system matures through use.

**Must-haves:**

1. `wiki/system/HOW-THE-WIKI-WORKS.md`: the operating manual, a copy/adaptation of this architecture explanation.
2. `wiki/log.md`: seed with today's entry: `## [DATE] -- Wiki system bootstrapped`.

**Likely also useful:**

3. `wiki/personal/bio.md`: user identity, role, business structure, working preferences.
4. One project page in `wiki/projects/` for each active project.
5. `wiki/patterns/regressions.md`: running log of corrections and the rules they crystallized.

Ask the user for the content. Don't invent specifics.

Standardize every page on this template so lint has a contract and Claude has a predictable parse target:

```markdown
---
last_updated: YYYY-MM-DD
tags: [project, active]
---
# Page Title

## Status        (project pages only) current state, read first
## Key Facts     quick-reference table or bullets
## Details       prose, the actual knowledge
## Tasks         - [ ] tracked items, - (?) thoughts
## Links         cross-references to other pages
```

Plans get one extra frontmatter key: `last_reconciled: YYYY-MM-DD` (semantics: "all references in this plan have been re-verified against current project state as of this date"). This is distinct from `last_updated`, which bumps on any edit. Plans decay faster than the project state they depend on: when executing a plan, load the project pages it references before taking its "next steps" as scope.

---

## Step 7: Wire the bootstrap (SessionStart hook)

This is the step that makes the whole system reliable. A SessionStart hook writes `INDEX.md` to standard output, and Claude Code adds whatever the hook prints to the session's context. So the index is present every session whether or not the model remembers to go read it. The prose directive in `CLAUDE.md` becomes a fallback, not the primary mechanism.

Add this to `RUNTIME_ROOT/settings.json` (`~/.claude/settings.json`):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {"type": "command", "command": "cat ~/knowledge/wiki/INDEX.md"}
        ]
      }
    ]
  }
}
```

Adjust the path to your `KNOWLEDGE_ROOT`. **If you already have a `settings.json`, merge this in: add `SessionStart` as a sibling key inside the existing top-level `hooks` object. Do not replace the file.** The easiest safe way: in a session, tell Claude *"merge this SessionStart hook into my existing `~/.claude/settings.json` without touching my other settings,"* then confirm the file is still valid JSON.

---

## Step 8: Smoke-test the build

Do not declare this done until you have proven it works. The completion gate (Step 13) is not optional, and it applies to the build itself first.

1. Commit and push what you have: `cd "$KNOWLEDGE_ROOT/wiki" && git add -A && git commit -m "First pages" && git push`.
2. Put a unique, made-up fact in exactly one wiki page: a fake project codename, say `Project Halibut`, on its own project page. This gives you something only the wiki can know.
3. Start a brand-new Claude session and ask: *"What is Project Halibut?"*
4. If it answers with your fact, retrieval works: the index was in context and it found the page. If it has no idea, the SessionStart hook is not injecting (re-check Step 7: path correct, JSON valid). Delete the fake fact once it passes.

Testing retrieval of a fact that lives nowhere else is the only honest check. Asking the model "did you read INDEX.md?" is not verifiable from the outside, and a model can answer a normal question without it, so do not rely on that.

**You now have a working system.** Everything in Part Two makes it self-maintaining. Skip Part Two and you have a notebook: structure with no enforcement, which drifts into fiction within a month. The enforcement is the product.

---

# PART TWO: LIVE WITH IT

A few minutes a week, forever. This half is where the system earns its keep. It is also the half people skip, which is why their context systems rot. Do not treat it as optional polish.

---

## Step 9: Set up the session-end hook

A small Python script that runs at session end and records which watched project files changed, writing them to `wiki/.update-queue`. The next session or lint pass reconciles the queue.

One thing to get right: a Claude Code `SessionEnd` hook receives a **JSON event** on standard input, not the transcript itself. The event includes a `transcript_path` pointing at a JSONL file. The hook reads that file to find which paths were touched. (The template repo ships this pre-written; if you used it, just set `WIKI_DIR` and `WATCHED`.)

`RUNTIME_ROOT/hooks/wiki-session-hook.py`:

```python
#!/usr/bin/env python3
"""SessionEnd hook: record changed watched-project files for later wiki update."""
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

event = json.load(sys.stdin)                       # Claude Code sends a JSON event, not the transcript
session_id = str(event.get("session_id", "unknown"))[:8]
transcript_path = event.get("transcript_path")

paths = set()
if transcript_path and os.path.exists(transcript_path):
    with open(transcript_path) as f:
        for line in f:                             # the transcript file is JSONL
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
    with open(QUEUE, "a") as f:
        f.write(f"\n## {datetime.now():%Y-%m-%d %H:%M} (session: {session_id})\n")
        for p in sorted(changed):
            f.write(f"- {p}\n")
```

Register it in `RUNTIME_ROOT/settings.json`, as a sibling of the `SessionStart` key you added in Step 7:

```json
{
  "hooks": {
    "SessionEnd": [
      {
        "matcher": "",
        "hooks": [
          {"type": "command", "command": "python3 ~/.claude/hooks/wiki-session-hook.py"}
        ]
      }
    ]
  }
}
```

**Confirm it fired:** in a session, edit a file under one of your `WATCHED` project folders, then end the session. Check that `wiki/.update-queue` now exists and lists the change. If it stays empty, either `WATCHED` does not match your real folder names or the hook is not registered. The hook is a tripwire, not a brain: it records that something changed so a future session (or `/wiki-lint`) can reason about it. Extend it to flag `LOG GAP` when a session's edits skip `log.md`.

---

## Step 10: Create the lint command

A slash command that performs a multi-step health check. Save to `RUNTIME_ROOT/commands/wiki-lint.md`; the command name comes from the filename, so this becomes `/wiki-lint`. (Newer Claude Code also supports skills at `~/.claude/skills/<name>/SKILL.md`; a plain command file is fine here.)

A 13-step pass is more than a model reliably executes in one go without cutting corners, so the command makes its own work visible: each step appends a one-line result to `wiki/.lint-run`, and the final report reads that file back verbatim. A step that got skipped is then obvious instead of silently assumed clean.

```markdown
---
description: Scan wiki for stale pages, broken links, overdue tasks, drift
---

Run a comprehensive wiki lint pass. Follow each step in order. After each step, append one line to `wiki/.lint-run` recording what you did and what you found (e.g. `step 3 broken-links: 2 found, 2 fixed`). Start by truncating `wiki/.lint-run`.

1. **Process update queue.** Check `wiki/.update-queue`. Read each entry, determine which wiki pages need updating, update them, clear the queue.
2. **Freshness check.** Compare `last_updated` frontmatter against git activity. Flag project pages >1 week stale relative to their repo.
3. **Broken links.** Scan all pages for markdown links. Verify targets exist. Auto-fix obvious renames.
4. **Task aggregation.** Collect all `- [ ]` items across pages. Age via git blame. Write top 10 to `wiki/tasks-open.md`.
5. **Log gap check.** Flag if most recent `log.md` entry is >3 days old.
6. **Unprocessed sources.** Flag files in `wiki/sources/` without `processed: true` frontmatter, older than 5 days.
7. **Log rotation.** If `log.md` has entries older than 30 days, archive them to `wiki/sources/log-archive-YYYY-MM.md`.
8. **Root cleanliness.** List KNOWLEDGE_ROOT contents. Flag anything not in the approved bucket list. Ask triage: do it / defer it / kill it.
9. **Auto-memory drift check.** Diff key facts between runtime auto-memory and wiki. Auto-fix obvious staleness.
10. **Plan reconciliation.** For each `wiki/plans/*.md`, compare `last_reconciled` to `last_updated` of any referenced project. Flag if plan predates its dependencies.
11. **Heartbeat.** Write current timestamp to `wiki/.lint-heartbeat`. Update `INDEX.md` line 2 with lint summary.
12. **Report.** Read `wiki/.lint-run` back verbatim, then present findings: auto-fixed (just report) and needs-attention (ask triage per item).
13. **Remote sync.** `git add -A && git commit && git push` when clean.
```

Output is an auto-fix pass for mechanical issues plus a triage report for judgment calls. The user responds `do it` / `defer it` / `kill it` per item. Most steps no-op on a small new wiki; that is fine, they earn their keep as it grows. Step 10 (plan reconciliation) is the youngest and is optional; build it only when you have plans that might go stale.

---

## Step 11: Schedule the lint

A lint that depends on human memory is the first enforcement layer to lapse. Put it on a schedule so it fires whether or not anyone remembers. Three options, in increasing durability:

- **`/loop` (session-scoped).** `/loop 1w /wiki-lint` re-runs the lint weekly while a session stays open, and auto-expires after 7 days. Good for a trial, not for set-and-forget.
- **`/schedule` (cloud routine).** `/schedule "run /wiki-lint weekly"` runs on Anthropic infrastructure, durable across restarts, no machine required. This is the real set-and-forget. It clones your wiki repo fresh each run, which is exactly why Step 2 made the wiki a pushed git repo.
- **Your own scheduler (off-machine).** A weekly GitHub Action (or `cron`/`launchd` on a machine that is always on) that clones the repo and runs the lint, if you would rather own the schedule yourself.

**The verifier contract.** Lint reads files; it cannot see whether a scheduled job is actually loaded and running. An output verifier asks one dumb question: did the scheduled job produce today's expected file, on time? Any scheduled agent should declare an expected output path; that declaration is the verifier's contract. This is the enforcement mode that closes the runtime-state gap.

---

## Step 12: Operating rhythm, and how to keep it honest

Once the scaffolding is up, the system runs like this:

**Every session (automatic):**

- The SessionStart hook injects `INDEX.md`. Claude picks 2 to 4 relevant pages. Does the work.
- At session end, the hook writes changed paths to `.update-queue`.

**After any change (the user says "log this"):**

- Claude updates the affected wiki pages and appends to `log.md` with a `Judgment:` line explaining the reasoning.

**On corrections (the user says "log this"):**

- Update `patterns/regressions.md` with the new rule. Future sessions load it.

**Weekly (lint runs, scheduled or on demand):**

- 13-step pass. Auto-fix plus triage report. The user responds to each needs-attention item.

This is the part that makes it a system rather than a folder. A few habits make or break it:

- **Ask questions.** When something looks off, interrogate it. "Why does this page say X when we decided Y?" The wiki is only as good as the questions asked of it.
- **Test things.** Periodically ask Claude something you know the answer to and check that it pulls from the wiki rather than guessing. Trust is earned by spot-checks, not assumed.
- **Notice when it is wrong, and say so.** A wrong answer is signal. The fix is a "log this" away, and the correction compounds: it becomes a regression rule the system enforces forever.
- **Expect inconsistency, and reconcile on purpose.** Context changes. Two pages will disagree; a page will lag a decision. That is normal, not a defect. The discipline is to surface the conflict and resolve it deliberately rather than letting the stale copy quietly win. Alignment is routine maintenance, not a fire.

A system that is never questioned, tested, or corrected is a system slowly drifting into fiction while looking healthy. The weekly few minutes is what keeps the gap closed.

---

## Step 13: The completion gate

Install this as a non-overridable rule:

> **Nothing is "done" until all three are true:**
> 1. The change works (smoke test, verification, whatever fits).
> 2. The docs reflect the change (wiki page + `log.md`).
> 3. Any deploy or script change followed its checklist.

This is the constitutional rule. Skipping it under pressure is the exact failure that caused most past incidents. Speed without verification is not speed, it is rework.

---

## Step 14: Trigger phrases the user should learn

Conversational controls, not exact commands. Teach these; without them, corrections evaporate with the session.

| Phrase | What it triggers |
|---|---|
| `log this` | Update regressions + relevant wiki page + log.md |
| `switching to [domain]` | Scope to that domain only |
| `do it / defer it / kill it` | Lint triage responses |
| `promote to [tracker]` | Create tracker issue from a wiki checkbox |

---

## Adapt to the user's context

Keep these (universal, load-bearing):

- Three layers: sources / wiki / schema.
- Boundary rule between knowledge and runtime.
- Progressive disclosure (don't load the whole wiki).
- `INDEX.md` as entry point, injected by the SessionStart hook.
- `log.md` with `Judgment:` lines.
- Lint as scheduled enforcement.
- Defense in depth (schema + hooks + lint + git + heartbeat + completion gate).
- **Part Two itself.** This is the one people are most tempted to drop and the one that most determines the outcome. Build the structure in an afternoon, then actually live the maintenance. Skip it and you have a notebook, not a drift-closing system. The enforcement is the product.

Adapt these (context-local):

- **Page categories.** System / projects / patterns works for infrastructure-heavy work. Clients / research / processes works for research-heavy. Match the user's domains.
- **Lint schedule.** Weekly by default. Daily for high-churn teams. Manual at the start is fine, but get it scheduled within the first two weeks.
- **Trigger phrases.** Add what matches the user's vocabulary.
- **Task tracker.** Linear, Jira, GitHub, none. Doesn't matter.
- **Surface routing.** Skip if single-surface. Add if multi-surface (desktop + mobile + CLI).

When you adapt, name the reason. Cutting a load-bearing piece "to keep it simple" is how the failure mode you have not met yet comes back.

---

## Common failure modes to preempt

**Over-eagerness.** Do not write five detailed pages in the first session. The system matures through use. Start minimum viable; grow when the user notices themselves repeating context.

**Pretending to verify.** If you claim something is current, you checked it this session. Never assert based on remembered state from earlier. Re-read before reporting.

**Fighting the progressive disclosure rule.** The temptation is to read more pages "just in case." Resist it. The rule prevents context bloat; breaking it for one task is how the failure mode returns.

**Treating inconsistency as failure.** When two pages disagree, the instinct is embarrassment and a silent fix. Wrong reflex. Surface it, ask which is current, reconcile out loud, log it. A context that never disagrees with itself is a context nobody is using hard enough.

**Creating helper abstractions.** If you are tempted to add a sixth script or a new frontmatter field, ask: has this problem fired twice? If no, wait. Lint will surface it if it returns.

---

## Future extensions

Planned, not built. Each waits for its need to fire twice.

- **Richer auto-memory audit.** The current drift check compares page counts, paths, project names. A full audit would diff every factual claim in auto-memory against the wiki.
- **Local search over the wiki** (qmd or equivalent) once page count crosses ~50. Grep holds below that.

---

## Closing

The system is small on purpose. Three layers, one boundary rule, three operations, a handful of enforcement layers. Everything beyond that is earned by use, not added by default.

When your user asks "should I add X to the wiki?", the answer is usually: not yet, put it in `sources/`, let it accumulate, it will surface if it matters.

The wiki's quality is a function of what you notice and what the user corrects. Your job is to notice more than you forget, and to force the user to make decisions fast (`do it / defer it / kill it`) rather than letting issues sit.

Build it in an afternoon. Then live with it: ask it questions, test it, correct it, reconcile it when it disagrees with itself. That second half is the whole point. Do it for two weeks, then ask what needs adjustment. Not before.

---

## If you would rather not build it alone

This is genuinely a one-afternoon build, and the whole point is that you own it afterward. So try it yourself first.

But if you get stuck, or you would rather have it set up around your actual work and handed back to you ready to run, that is what I do. I am Ethan. I build custom AI systems that fit you and learn the ways you work, this one included, for individuals and teams.

If you want a hand, reach out at [eqctrl.io](https://eqctrl.io) or entropyeq@gmail.com. A real human answers, and the first conversation is free.

---

*Based on [eqctrl.io/karpathy+](https://eqctrl.io/karpathy+) · v3 · 2026-06-17. Adapt freely. Credit if you publish a fork. Built by Ethan Ouimet (eqctrl).*
