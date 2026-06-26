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

Now make the wiki its own git repo. This is **required**, not optional: the lint steps measure page freshness against git, age tasks with `git blame`, and the scheduled lint clones the repo. A plain `cp` gives you no git history, so those steps silently do nothing.

```bash
cd ~/knowledge/wiki && git init -b main && git add -A && git commit -m 'Wiki bootstrapped'
```

For the weekly cloud lint to work, this repo also needs a remote. Create a **private** GitHub repo and push to it (`gh repo create ... --private --source=. --push`, or the web-UI flow). BUILD-GUIDE.md Step 2 has the full command for both paths.

## 3. Install the runtime into ~/.claude (back up first)

If you already use Claude Code, you have files here already. Back them up, then MERGE, never blind-overwrite.

```bash
# back up anything that already exists
cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.bak 2>/dev/null
cp ~/.claude/settings.json ~/.claude/settings.json.bak 2>/dev/null

# copy in the two hooks and the lint command
mkdir -p ~/.claude/hooks ~/.claude/commands
cp runtime/hooks/session-inject.sh ~/.claude/hooks/
cp runtime/hooks/wiki-session-hook.py ~/.claude/hooks/
cp runtime/commands/wiki-lint.md ~/.claude/commands/
```

**Required: set `WATCHED` in the session-end hook.** It ships with placeholders (`WATCHED = ["project-a", "project-b"]`). Open `~/.claude/hooks/wiki-session-hook.py` and replace them with your real project folder names — the directory names directly under your home folder (`~/`) whose file changes you want recorded for the wiki. Without this the hook still runs and exits clean, but it matches nothing and records nothing forever, with no error to tell you.

```bash
${EDITOR:-nano} ~/.claude/hooks/wiki-session-hook.py
```

The two files that might already exist, do **not** just copy over:

- **`runtime/CLAUDE.md`** — if you have no `~/.claude/CLAUDE.md`, copy it in and fill the bracketed blanks. If you already have one, open both and merge the wiki rules into yours by hand (or ask Claude to merge them). Copying over the top destroys your existing global rules.

  ```bash
  cp runtime/CLAUDE.md ~/.claude/CLAUDE.md   # only if you have none already
  ```
- **`runtime/settings.json.example`** — this holds the two hooks. If you have no `~/.claude/settings.json`, copy it there. If you already have one, add its `SessionStart` and `SessionEnd` keys into your existing `hooks` object. Easiest safe way: in a Claude session, say *"merge the hooks from this file into my existing ~/.claude/settings.json without touching my other settings,"* then confirm it is still valid JSON.

  ```bash
  cp runtime/settings.json.example ~/.claude/settings.json   # only if you have none already
  ```

## 4. Point the paths at your folders

**Always required (any path):** you already set `WATCHED` in `~/.claude/hooks/wiki-session-hook.py` in step 3. That edit is mandatory regardless of where your knowledge folder lives — do not skip it.

**Only if your knowledge folder is not `~/knowledge`:** if you used `~/knowledge`, the path defaults are already correct and you can move on. Otherwise, edit the knowledge path in these to match:

- `~/.claude/hooks/session-inject.sh` — the `WIKI` variable (the SessionStart path now lives here; `settings.json` only calls `bash ~/.claude/hooks/session-inject.sh`)
- `~/.claude/hooks/wiki-session-hook.py` — `WIKI_DIR`
- `~/.claude/commands/wiki-lint.md` — the `WIKI=~/knowledge/wiki` line in step 0
- `~/.claude/CLAUDE.md` — the `~/knowledge/wiki/` references

## 5. Smoke-test it

The point of this test is to prove the chain *INDEX injected → Claude follows the link → reads the page*. A page Claude could only find by exploring the filesystem does not prove that, so you must link it from the index.

1. Create the page: `~/knowledge/wiki/projects/halibut.md` containing `Project Halibut is a test.`
2. Link it from the index. Add this line under the `## Projects` section of `~/knowledge/wiki/INDEX.md`:

   ```
   - [halibut](projects/halibut.md) -- test page for the smoke test
   ```
3. Start a NEW Claude session and ask: *"What is Project Halibut?"*
4. If it answers with your fact, the whole chain works. Delete the fake page **and** its INDEX.md line.

If it has no idea, debug in this order:

- Run `bash ~/.claude/hooks/session-inject.sh` in a terminal yourself. You should see your index printed between the bootstrap markers. A `[bootstrap] ... not found` line means the `WIKI` path in the hook is wrong (most often the `wiki/wiki` nesting from step 2) — fix that first.
- If the index prints and includes your halibut line, confirm the `SessionStart` hook is wired in `~/.claude/settings.json` (the `command` is `bash ~/.claude/hooks/session-inject.sh`) and the file is still valid JSON.

## 6. Check the session-end hook records changes

The session-start hook is only half the loop; confirm the session-end side too:

1. With `WATCHED` set to a real project folder, edit any file inside that folder during a Claude session.
2. End the session, then run `cat ~/knowledge/wiki/.update-queue`.
3. You should see the changed file listed. If it stays empty, `WATCHED` does not match your real folder names — fix it in `~/.claude/hooks/wiki-session-hook.py` (step 3).

## What you do from here

Part One is done — the system retrieves. Part Two is living with it, and it is minutes a week, not hours:

- Work normally. When a session changes something, update the relevant wiki page and add a `log.md` line. Claude does most of this when you say "log this".
- The session-end hook drops changed watched files into `~/knowledge/wiki/.update-queue`; clear that queue at the next session start.
- Run `/wiki-lint` weekly (or let the scheduled lint do it). It flags stale pages, broken links, and overdue tasks — the session-start hook nudges you when it is overdue.
- Commit and push the wiki on the same cadence, so the cloud lint always has the current state.

Read BUILD-GUIDE.md "Part Two" for the full weekly rhythm.
