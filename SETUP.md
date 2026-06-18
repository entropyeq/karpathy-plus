# Setup (you used "Use this template")

You already have all the files. This is the short path, about 15 minutes. **Do not follow BUILD-GUIDE.md Steps 2-3** — those build the scaffold from scratch and you already have it. BUILD-GUIDE.md is here as the full reference if you want to understand each piece.

Commands are for macOS/Linux. On Windows, use WSL.

## 1. Get the files onto your machine

Clone your copy of the template somewhere neutral (not into your knowledge folder yet):

```bash
gh repo clone YOUR-USERNAME/YOUR-REPO ~/karpathy-plus-kit
cd ~/karpathy-plus-kit
```

## 2. Put the wiki where knowledge lives

```bash
mkdir -p ~/knowledge
cp -R wiki ~/knowledge/wiki
```

Your index is now at `~/knowledge/wiki/INDEX.md`. (Want knowledge somewhere other than `~/knowledge`? Use that path here, and update it in step 4.)

> Common mistake: do **not** clone the repo directly into `~/knowledge/wiki`. The repo contains a `wiki/` subfolder, so you would end up with the index one level too deep at `~/knowledge/wiki/wiki/INDEX.md` and nothing would work.

## 3. Install the runtime into ~/.claude (back up first)

If you already use Claude Code, you have files here already. Back them up, then MERGE, never blind-overwrite.

```bash
# back up anything that already exists
cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.bak 2>/dev/null
cp ~/.claude/settings.json ~/.claude/settings.json.bak 2>/dev/null

# the hook and the command are always safe to copy straight in
mkdir -p ~/.claude/hooks ~/.claude/commands
cp runtime/hooks/wiki-session-hook.py ~/.claude/hooks/
cp runtime/commands/wiki-lint.md ~/.claude/commands/
```

The two files that might already exist, do **not** just copy over:

- **`runtime/CLAUDE.md`** — if you have no `~/.claude/CLAUDE.md`, copy it in and fill the bracketed blanks. If you already have one, open both and merge the wiki rules into yours by hand (or ask Claude to merge them). Copying over the top destroys your existing global rules.
- **`runtime/settings.json.example`** — this holds the two hooks. If you have no `~/.claude/settings.json`, copy it there. If you already have one, add its `SessionStart` and `SessionEnd` keys into your existing `hooks` object. Easiest safe way: in a Claude session, say *"merge the hooks from this file into my existing ~/.claude/settings.json without touching my other settings,"* then confirm it is still valid JSON.

## 4. Point the paths at your folders

If your knowledge folder is `~/knowledge`, you are already set. If not, edit these three to match your path:

- `~/.claude/settings.json` — the SessionStart command (`cat ~/knowledge/wiki/INDEX.md`)
- `~/.claude/hooks/wiki-session-hook.py` — `WIKI_DIR`, and `WATCHED` (your real project folder names)
- `~/.claude/CLAUDE.md` — the `~/knowledge/wiki/` references

## 5. Smoke-test it

1. Put a made-up fact in one page: create `~/knowledge/wiki/projects/halibut.md` containing `Project Halibut is a test.`
2. Start a NEW Claude session and ask: *"What is Project Halibut?"*
3. If it answers with your fact, it works. Delete the fake page.

If it has no idea, debug in this order:

- Run `cat ~/knowledge/wiki/INDEX.md` in a terminal yourself. If that errors or is empty, your path is wrong (most often the `wiki/wiki` nesting from step 2). Fix the path first.
- If the index prints fine, confirm the `SessionStart` hook is in `~/.claude/settings.json` and the file is valid JSON.

That is it. Read BUILD-GUIDE.md "Part Two" for the weekly rhythm, and you are running.
