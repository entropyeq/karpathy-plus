# Karpathy+

A persistent, structured memory for your AI that sticks between chats and stays correct over time. A handful of plain markdown files plus a few rules that keep them honest. You build it in an afternoon and you own it forever.

This is the three-layer architecture from Andrej Karpathy's LLM Wiki pattern, plus the operations layer that keeps it honest over time: a scheduled lint, a session-start memory injection, and a completion gate, so your knowledge base does not quietly drift out of sync with reality. The enforcement is the product.

## Which path are you on?

- **You clicked "Use this template" and want to set it up** → follow **[SETUP.md](SETUP.md)**. The files already exist; it is a 15-minute install. (Do not follow the build guide's from-scratch steps, you do not need them.)
- **You want to build from nothing, or understand every piece** → read **[BUILD-GUIDE.md](BUILD-GUIDE.md)**. It is written to be followed by a person or handed to Claude to execute.
- **You are publishing this template** → see **[PUBLISHING.md](PUBLISHING.md)**.

If you would rather just hand it to Claude: open Claude Code in your copy of this repo and say *"Set this system up for me from this repo, following SETUP.md. Ask me for anything you need before writing."*

## What is in the box

- **`wiki/`** is the knowledge layer. It becomes your `~/knowledge/wiki`. Ships with an index, an operating manual, and empty buckets to fill.
- **`runtime/`** is what makes it run. These go into your Claude config (`~/.claude`):
  - `CLAUDE.md` — the ~50-line rules file Claude reads every session. Fill in the bracketed blanks.
  - `hooks/wiki-session-hook.py` — records what changed each session.
  - `commands/wiki-lint.md` — the weekly health check, run as `/wiki-lint`.
  - `settings.json.example` — the hook wiring. Merge into your existing `~/.claude/settings.json`, do not overwrite.
- **`SETUP.md`** — the short install path for template users. **`BUILD-GUIDE.md`** — the full guide. **`PUBLISHING.md`** — maintainer publish steps. **`LICENSE`** — MIT.

> If you already use Claude Code, you have a `~/.claude/CLAUDE.md` and `~/.claude/settings.json` already. Back them up and MERGE the new pieces in, never blind-copy over them. SETUP.md shows how.

## The one rule that matters

Knowledge lives in one place (`~/knowledge`). Runtime lives somewhere else (`~/.claude`). Never collapse them. That separation is what stops the same fact living in three files and drifting apart. Everything else is detail.

## Two halves

Building it is an afternoon. Living with it is a few minutes a week, forever, and that second half is the whole point. Ask it questions, test it, correct it, reconcile it when it disagrees with itself. Skip that and you have a notebook, not a system that stays true.

---

Built by Ethan Ouimet (eqctrl). Adapt freely, credit if you fork. If you would rather have it set up around your actual work and handed back ready to run, that is what I do for individuals and teams: [eqctrl.io](https://eqctrl.io). A real human answers, and the first conversation is free.
