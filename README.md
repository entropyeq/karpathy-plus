# Karpathy+

**Give your AI a memory that sticks.** Out of the box, your AI forgets everything the moment a chat ends. Karpathy+ fixes that: it turns a folder of plain text files into a personal knowledge base your AI reads at the start of every session and keeps current as you go. Set it up once, own it forever.

### Start here: hand this repo to your agent

Open this folder in **Claude Code** and say:

> *Set this system up for me from this repo, following SETUP.md. Ask me anything you need before you start.*

That is the whole quickstart. Your agent creates the files, wires the hooks, and asks you the few things only you can answer. Everything below is for when you (or your agent) want to understand or change a piece — you do not need to read it to get running.

> **One requirement:** Karpathy+ runs on **Claude Code** (Anthropic's terminal app; it uses your paid API). It does **not** work with claude.ai in the browser. You also need `git` and the `gh` CLI installed.

---

## How it works

Three layers, borrowed from Karpathy's LLM-wiki pattern, plus an operations layer that keeps the whole thing honest:

- **Sources → Wiki → Schema.** Raw notes get distilled into a wiki of markdown pages, and a small `CLAUDE.md` tells your agent the conventions to follow. This three-layer pattern is Karpathy's ([his gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)).
- **The operations layer is mine** — the part that keeps it from rotting: a session-start hook that injects your index into every conversation, a session-end hook that records what changed, a weekly lint that catches drift, a completion gate, and one boundary rule. It does not keep itself correct; it surfaces drift fast and makes reconciling it cheap, so you keep it in sync in minutes a week. The enforcement is the product.

*Not affiliated with, sponsored by, or endorsed by Andrej Karpathy.*

## Which path are you on?

- **You clicked "Use this template" and want to set it up** → follow **[SETUP.md](SETUP.md)**. The files already exist; it is a 15-minute install. (Do not follow the build guide's from-scratch steps, you do not need them.)
- **You want to build from nothing, or understand every piece** → read **[BUILD-GUIDE.md](BUILD-GUIDE.md)**. It is written to be followed by a person or handed to Claude to execute.
- **You are publishing this template** → see **[PUBLISHING.md](PUBLISHING.md)**.

## What is in the box

- **`wiki/`** is the knowledge layer. It becomes your `~/knowledge/wiki`. Ships with an index, an operating manual, and empty buckets to fill.
- **`runtime/`** is what makes it run. These go into your Claude config (`~/.claude`):
  - `CLAUDE.md` — the ~50-line rules file Claude reads every session. Fill in the bracketed blanks.
  - `hooks/session-inject.sh` — injects your index at session start and nudges you when the weekly lint is overdue.
  - `hooks/wiki-session-hook.py` — records what changed each session.
  - `commands/wiki-lint.md` — the weekly health check, run as `/wiki-lint`.
  - `settings.json.example` — the hook wiring. Merge into your existing `~/.claude/settings.json`, do not overwrite.
- **`SETUP.md`** — the short install path for template users. **`BUILD-GUIDE.md`** — the full guide. **`PUBLISHING.md`** — maintainer publish steps. **`LICENSE`** — MIT.

> If you already use Claude Code, you have a `~/.claude/CLAUDE.md` and `~/.claude/settings.json` already. Back them up and MERGE the new pieces in, never blind-copy over them. SETUP.md shows how.

## The one rule that matters

Knowledge lives in one place (`~/knowledge`). Runtime lives somewhere else (`~/.claude`). Never collapse them. That separation is what stops the same fact living in three files and drifting apart. Everything else is detail.

## Two halves

Building it is an afternoon. Living with it is a few minutes a week, forever, and that second half is the whole point. Ask it questions, test it, correct it, reconcile it when it disagrees with itself. Skip that and you have a notebook, not a system that stays true.

## How this differs

The closest prior art is heavier by design. `claude-mem` and the "second brain" memory repos lean on SQLite and embeddings; `claude-memory-compiler` runs an Agent-SDK compile pipeline; several ship as installable plugins you bolt on; hosted context-graph products like HipAI manage the whole thing as a service. This is deliberately the opposite: markdown-only, human-in-the-loop, shipped as a "Use this template" repo you own outright, with nothing to install beyond the files themselves. The primitives here are not novel, and that is the honest concession. The value is the debugged default arrangement plus the maintenance discipline that keeps it from rotting.

---

Built by Ethan Ouimet (eqctrl). Adapt freely, credit if you fork. If you would rather have it set up around your actual work and handed back ready to run, that is what I do for individuals and teams: [eqctrl.io](https://eqctrl.io). A real human answers, and the first conversation is free.
